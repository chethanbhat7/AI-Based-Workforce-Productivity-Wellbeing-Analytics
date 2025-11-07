"""
Google Sheets Integration for Attendance Tracking
Stores weekly punch records for all employees
"""
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import json

import httpx
from config import settings

logger = logging.getLogger(__name__)


class GoogleSheetsOAuth:
    """Google OAuth2 authentication handler"""
    
    AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    
    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.get_redirect_uri("google")
        self.scopes = settings.GOOGLE_SCOPES
    
    def get_authorization_url(self, state: str = None) -> str:
        """
        Generate Google OAuth authorization URL
        
        Scopes requested:
        - https://www.googleapis.com/auth/spreadsheets: Read and write access to sheets
        - https://www.googleapis.com/auth/drive.file: Access to created/opened files
        """
        from urllib.parse import urlencode
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "access_type": "offline",  # Get refresh token
            "prompt": "consent"  # Force consent screen to get refresh token
        }
        
        if state:
            params["state"] = state
        
        query_string = urlencode(params)
        return f"{self.AUTHORIZATION_URL}?{query_string}"
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        
        Returns:
            {
                "access_token": "...",
                "refresh_token": "...",
                "expires_in": 3600,
                "token_type": "Bearer"
            }
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "code": code,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uri": self.redirect_uri,
                    "grant_type": "authorization_code"
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh expired access token"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token"
                }
            )
            response.raise_for_status()
            return response.json()


class GoogleSheetsAPI:
    """Google Sheets API wrapper for attendance tracking"""
    
    BASE_URL = "https://sheets.googleapis.com/v4/spreadsheets"
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    async def create_attendance_spreadsheet(self, title: str = "Employee Attendance Records") -> Dict[str, Any]:
        """
        Create a new spreadsheet for attendance tracking
        
        Creates a master spreadsheet with an index sheet.
        Individual employee-week sheets will be created dynamically as needed.
        """
        spreadsheet_data = {
            "properties": {
                "title": title
            },
            "sheets": [
                {
                    "properties": {
                        "title": "Index",
                        "gridProperties": {
                            "rowCount": 1000,
                            "columnCount": 6,
                            "frozenRowCount": 1
                        }
                    }
                }
            ]
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.BASE_URL,
                headers=self.headers,
                json=spreadsheet_data
            )
            response.raise_for_status()
            result = response.json()
            
            spreadsheet_id = result["spreadsheetId"]
            
            # Initialize index sheet headers
            await self._initialize_index_headers(spreadsheet_id)
            
            logger.info(f"Created attendance spreadsheet: {spreadsheet_id}")
            return result
    
    async def _initialize_index_headers(self, spreadsheet_id: str):
        """Initialize headers for Index sheet"""
        headers = [
            "Employee ID",
            "Employee Name",
            "Week Start Date",
            "Week End Date",
            "Sheet Name",
            "Last Updated"
        ]
        
        await self.append_rows(
            spreadsheet_id=spreadsheet_id,
            sheet_name="Index",
            values=[headers]
        )
    
    async def create_employee_week_sheet(
        self,
        spreadsheet_id: str,
        employee_id: str,
        employee_name: str,
        week_start: datetime
    ) -> str:
        """
        Create a new sheet for a specific employee's week
        
        Sheet name format: "EMP001_2025-W45" (Employee ID + Year + Week Number)
        
        Returns:
            Sheet name
        """
        # Generate sheet name
        week_number = week_start.isocalendar()[1]
        year = week_start.year
        sheet_name = f"{employee_id}_{year}-W{week_number:02d}"
        
        # Check if sheet already exists
        spreadsheet_info = await self.get_spreadsheet_info(spreadsheet_id)
        existing_sheets = [sheet["properties"]["title"] for sheet in spreadsheet_info.get("sheets", [])]
        
        if sheet_name in existing_sheets:
            logger.info(f"Sheet {sheet_name} already exists")
            return sheet_name
        
        # Create new sheet
        request_body = {
            "requests": [
                {
                    "addSheet": {
                        "properties": {
                            "title": sheet_name,
                            "gridProperties": {
                                "rowCount": 100,
                                "columnCount": 12,
                                "frozenRowCount": 1
                            }
                        }
                    }
                }
            ]
        }
        
        url = f"{self.BASE_URL}/{spreadsheet_id}:batchUpdate"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                headers=self.headers,
                json=request_body
            )
            response.raise_for_status()
        
        # Initialize headers for the new sheet
        await self._initialize_employee_week_headers(spreadsheet_id, sheet_name, employee_id, employee_name, week_start)
        
        # Add entry to index
        await self._add_to_index(spreadsheet_id, employee_id, employee_name, week_start, sheet_name)
        
        logger.info(f"Created sheet {sheet_name} for employee {employee_id}")
        return sheet_name
    
    async def _initialize_employee_week_headers(
        self,
        spreadsheet_id: str,
        sheet_name: str,
        employee_id: str,
        employee_name: str,
        week_start: datetime
    ):
        """Initialize headers and metadata for employee week sheet"""
        week_end = week_start + timedelta(days=6)
        
        # Header rows
        header_rows = [
            # Row 1: Employee info
            [f"Employee: {employee_name} ({employee_id})", "", "", "", "", "", "", "", "", "", "", ""],
            # Row 2: Week range
            [f"Week: {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}", "", "", "", "", "", "", "", "", "", "", ""],
            # Row 3: Empty
            ["", "", "", "", "", "", "", "", "", "", "", ""],
            # Row 4: Column headers
            [
                "Date",
                "Day",
                "Punch In Time",
                "Punch Out Time",
                "Total Hours",
                "Break Duration (min)",
                "Biometric Score (In)",
                "Biometric Score (Out)",
                "Location",
                "Status",
                "Overtime",
                "Notes"
            ]
        ]
        
        await self.append_rows(
            spreadsheet_id=spreadsheet_id,
            sheet_name=sheet_name,
            values=header_rows
        )
    
    async def _add_to_index(
        self,
        spreadsheet_id: str,
        employee_id: str,
        employee_name: str,
        week_start: datetime,
        sheet_name: str
    ):
        """Add entry to index sheet"""
        week_end = week_start + timedelta(days=6)
        
        index_row = [
            employee_id,
            employee_name,
            week_start.strftime("%Y-%m-%d"),
            week_end.strftime("%Y-%m-%d"),
            sheet_name,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]
        
        await self.append_rows(
            spreadsheet_id=spreadsheet_id,
            sheet_name="Index",
            values=[index_row]
        )
    
    async def append_daily_record(
        self,
        spreadsheet_id: str,
        employee_id: str,
        employee_name: str,
        date: datetime,
        punch_in_time: Optional[datetime] = None,
        punch_out_time: Optional[datetime] = None,
        biometric_score_in: Optional[float] = None,
        biometric_score_out: Optional[float] = None,
        location: str = "",
        status: str = "Present",
        notes: str = ""
    ):
        """
        Append or update a daily record in the employee's week sheet
        
        Args:
            spreadsheet_id: The Google Sheets ID
            employee_id: Employee identifier
            employee_name: Employee full name
            date: Date of attendance
            punch_in_time: Time employee punched in
            punch_out_time: Time employee punched out
            biometric_score_in: Match score for punch in
            biometric_score_out: Match score for punch out
            location: Office location
            status: Present, Absent, Late, etc.
            notes: Additional notes
        """
        # Calculate week start (Monday)
        week_start = date - timedelta(days=date.weekday())
        
        # Create or get employee week sheet
        sheet_name = await self.create_employee_week_sheet(
            spreadsheet_id=spreadsheet_id,
            employee_id=employee_id,
            employee_name=employee_name,
            week_start=week_start
        )
        
        # Calculate total hours and break duration
        total_hours = 0.0
        break_duration = 0
        overtime = 0.0
        
        if punch_in_time and punch_out_time:
            time_diff = punch_out_time - punch_in_time
            total_hours = time_diff.total_seconds() / 3600
            
            # Standard work day is 8 hours
            if total_hours > 8:
                overtime = total_hours - 8
            
            # Estimate break (if worked more than 6 hours, assume 1 hour break)
            if total_hours > 6:
                break_duration = 60
                total_hours -= 1  # Subtract break from total
        
        # Format row data
        row_data = [
            date.strftime("%Y-%m-%d"),
            date.strftime("%A"),  # Day name (Monday, Tuesday, etc.)
            punch_in_time.strftime("%H:%M:%S") if punch_in_time else "",
            punch_out_time.strftime("%H:%M:%S") if punch_out_time else "",
            f"{total_hours:.2f}" if total_hours > 0 else "",
            str(break_duration) if break_duration > 0 else "",
            f"{biometric_score_in:.1f}" if biometric_score_in else "",
            f"{biometric_score_out:.1f}" if biometric_score_out else "",
            location,
            status,
            f"{overtime:.2f}" if overtime > 0 else "",
            notes
        ]
        
        await self.append_rows(
            spreadsheet_id=spreadsheet_id,
            sheet_name=sheet_name,
            values=[row_data]
        )
        
        logger.info(f"Added daily record for {employee_id} on {date.strftime('%Y-%m-%d')}")
    
    async def append_weekly_summary(
        self,
        spreadsheet_id: str,
        employee_id: str,
        employee_name: str,
        week_start: datetime,
        summary_data: Dict[str, Any]
    ):
        """
        Append weekly summary to the employee's week sheet
        
        This adds a summary row at the bottom of the employee's week sheet
        showing total hours, days present, punctuality, etc.
        """
        # Get sheet name
        week_number = week_start.isocalendar()[1]
        year = week_start.year
        sheet_name = f"{employee_id}_{year}-W{week_number:02d}"
        
        # Add empty row for spacing
        await self.append_rows(
            spreadsheet_id=spreadsheet_id,
            sheet_name=sheet_name,
            values=[[""]]
        )
        
        # Add summary section
        summary_rows = [
            ["WEEKLY SUMMARY", "", "", "", "", "", "", "", "", "", "", ""],
            ["Total Days Present:", str(summary_data.get("days_present", 0)), "", "", "", "", "", "", "", "", "", ""],
            ["Total Hours Worked:", f"{summary_data.get('total_hours', 0):.2f}", "", "", "", "", "", "", "", "", "", ""],
            ["Average Daily Hours:", f"{summary_data.get('avg_daily_hours', 0):.2f}", "", "", "", "", "", "", "", "", "", ""],
            ["Late Arrivals:", str(summary_data.get("late_arrivals", 0)), "", "", "", "", "", "", "", "", "", ""],
            ["Early Departures:", str(summary_data.get("early_departures", 0)), "", "", "", "", "", "", "", "", "", ""],
            ["Overtime Hours:", f"{summary_data.get('overtime_hours', 0):.2f}", "", "", "", "", "", "", "", "", "", ""],
            ["Punctuality Score:", f"{summary_data.get('punctuality_score', 0):.1f}%", "", "", "", "", "", "", "", "", "", ""],
            ["Attendance Rate:", f"{summary_data.get('attendance_rate', 0):.1f}%", "", "", "", "", "", "", "", "", "", ""],
        ]
        
        await self.append_rows(
            spreadsheet_id=spreadsheet_id,
            sheet_name=sheet_name,
            values=summary_rows
        )
        
        logger.info(f"Added weekly summary for {employee_id}, week {week_start}")
    
    async def get_employee_week_data(
        self,
        spreadsheet_id: str,
        employee_id: str,
        week_start: datetime
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all daily records for an employee's specific week
        
        Returns:
            List of daily attendance records
        """
        week_number = week_start.isocalendar()[1]
        year = week_start.year
        sheet_name = f"{employee_id}_{year}-W{week_number:02d}"
        
        range_name = f"{sheet_name}!A5:L"  # Start from row 5 (after headers)
        url = f"{self.BASE_URL}/{spreadsheet_id}/values/{range_name}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
            
            if "values" not in data or len(data["values"]) == 0:
                return []
            
            # Parse rows
            records = []
            for row in data["values"]:
                # Skip empty rows or summary rows
                if not row or len(row) == 0 or row[0] == "WEEKLY SUMMARY":
                    break
                
                # Pad row if needed
                row = row + [""] * (12 - len(row))
                
                record = {
                    "date": row[0],
                    "day": row[1],
                    "punch_in_time": row[2],
                    "punch_out_time": row[3],
                    "total_hours": row[4],
                    "break_duration": row[5],
                    "biometric_score_in": row[6],
                    "biometric_score_out": row[7],
                    "location": row[8],
                    "status": row[9],
                    "overtime": row[10],
                    "notes": row[11]
                }
                
                records.append(record)
            
            return records
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                # Sheet doesn't exist
                logger.warning(f"Sheet {sheet_name} not found")
                return []
            raise
    
    async def append_punch_record(
        self,
        spreadsheet_id: str,
        employee_id: str,
        punch_type: str,
        punch_time: datetime,
        biometric_match_score: float,
        location: str,
        device_id: str,
        verified: bool,
        employee_name: str = "Unknown Employee"
    ):
        """
        Append a single punch record to the employee's week sheet
        
        This is a compatibility wrapper that converts punch in/out events
        to daily records in the employee's dedicated week sheet.
        
        Args:
            spreadsheet_id: The Google Sheets ID
            employee_id: Employee identifier
            punch_type: "IN" or "OUT"
            punch_time: Timestamp of punch
            biometric_match_score: Match confidence (0-100)
            location: Punch location/branch
            device_id: Biometric device identifier
            verified: Whether biometric verification passed
            employee_name: Employee full name
        """
        # Store punch data temporarily (in production, use a cache/database)
        # For now, we'll append daily records when we have both IN and OUT
        
        if punch_type == "IN":
            # Record punch-in
            await self.append_daily_record(
                spreadsheet_id=spreadsheet_id,
                employee_id=employee_id,
                employee_name=employee_name,
                date=punch_time.date() if hasattr(punch_time, 'date') else punch_time,
                punch_in_time=punch_time,
                biometric_score_in=biometric_match_score,
                location=location,
                status="Present" if verified else "Unverified"
            )
        else:
            # For punch-out, we need to update the existing row
            # In a real implementation, you'd fetch the row and update it
            # For now, we'll just log it
            logger.info(f"Punch-out recorded for {employee_id} at {punch_time}")
            # TODO: Implement row update logic to add punch-out time to existing daily record
        
        logger.info(f"Recorded {punch_type} for {employee_id} at {punch_time}")
    
    async def append_weekly_summary(
        self,
        spreadsheet_id: str,
        employee_id: str,
        week_start: datetime,
        week_end: datetime,
        summary_data: Dict[str, Any]
    ):
        """
        Append weekly attendance summary
        
        Args:
            spreadsheet_id: The Google Sheets ID
            employee_id: Employee identifier
            week_start: Start date of week
            week_end: End date of week
            summary_data: Dictionary with metrics:
                - days_present
                - total_hours
                - late_arrivals
                - early_departures
                - overtime_hours
                - avg_daily_hours
                - punctuality_score
                - total_punches
                - break_duration_minutes
                - avg_break_duration
                - attendance_rate
        """
        row_data = [
            employee_id,
            week_start.strftime("%Y-%m-%d"),
            week_end.strftime("%Y-%m-%d"),
            str(summary_data.get("days_present", 0)),
            f"{summary_data.get('total_hours', 0):.2f}",
            str(summary_data.get("late_arrivals", 0)),
            str(summary_data.get("early_departures", 0)),
            f"{summary_data.get('overtime_hours', 0):.2f}",
            f"{summary_data.get('avg_daily_hours', 0):.2f}",
            f"{summary_data.get('punctuality_score', 0):.1f}",
            str(summary_data.get("total_punches", 0)),
            str(summary_data.get("break_duration_minutes", 0)),
            f"{summary_data.get('avg_break_duration', 0):.1f}",
            f"{summary_data.get('attendance_rate', 0):.1f}",
            summary_data.get("notes", "")
        ]
        
        await self.append_rows(
            spreadsheet_id=spreadsheet_id,
            sheet_name="Weekly Summary",
            values=[row_data]
        )
        
        logger.info(f"Appended weekly summary for {employee_id}: Week {week_start} to {week_end}")
    
    async def append_rows(
        self,
        spreadsheet_id: str,
        sheet_name: str,
        values: List[List[str]]
    ):
        """Append rows to a sheet"""
        range_name = f"{sheet_name}!A:Z"
        url = f"{self.BASE_URL}/{spreadsheet_id}/values/{range_name}:append"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                headers=self.headers,
                params={"valueInputOption": "RAW"},
                json={"values": values}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_punch_records(
        self,
        spreadsheet_id: str,
        employee_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve punch records from the spreadsheet
        
        Args:
            spreadsheet_id: The Google Sheets ID
            employee_id: Filter by employee (optional)
            start_date: Filter by start date (optional)
            end_date: Filter by end date (optional)
        
        Returns:
            List of punch records as dictionaries
        """
        range_name = "Punch Records!A:L"
        url = f"{self.BASE_URL}/{spreadsheet_id}/values/{range_name}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
        
        if "values" not in data or len(data["values"]) < 2:
            return []
        
        # Parse rows (skip header)
        headers = data["values"][0]
        records = []
        
        for row in data["values"][1:]:
            # Pad row if needed
            row = row + [""] * (len(headers) - len(row))
            
            record = dict(zip(headers, row))
            
            # Apply filters
            if employee_id and record.get("Employee ID") != employee_id:
                continue
            
            if start_date or end_date:
                try:
                    punch_date = datetime.fromisoformat(record.get("Punch Time", ""))
                    if start_date and punch_date < start_date:
                        continue
                    if end_date and punch_date > end_date:
                        continue
                except (ValueError, TypeError):
                    continue
            
            records.append(record)
        
        return records
    
    async def get_weekly_summary(
        self,
        spreadsheet_id: str,
        employee_id: Optional[str] = None,
        week_start: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve weekly summaries from the spreadsheet
        
        Args:
            spreadsheet_id: The Google Sheets ID
            employee_id: Filter by employee (optional)
            week_start: Filter by week start date (optional)
        
        Returns:
            List of weekly summaries as dictionaries
        """
        range_name = "Weekly Summary!A:O"
        url = f"{self.BASE_URL}/{spreadsheet_id}/values/{range_name}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
        
        if "values" not in data or len(data["values"]) < 2:
            return []
        
        # Parse rows (skip header)
        headers = data["values"][0]
        summaries = []
        
        for row in data["values"][1:]:
            # Pad row if needed
            row = row + [""] * (len(headers) - len(row))
            
            summary = dict(zip(headers, row))
            
            # Apply filters
            if employee_id and summary.get("Employee ID") != employee_id:
                continue
            
            if week_start:
                try:
                    summary_week_start = datetime.strptime(
                        summary.get("Week Start Date", ""),
                        "%Y-%m-%d"
                    )
                    if summary_week_start != week_start:
                        continue
                except (ValueError, TypeError):
                    continue
            
            summaries.append(summary)
        
        return summaries
    
    async def update_weekly_summary(
        self,
        spreadsheet_id: str,
        employee_id: str,
        week_start: datetime,
        summary_data: Dict[str, Any]
    ):
        """
        Update an existing weekly summary or create if it doesn't exist
        
        This method searches for an existing weekly summary for the employee
        and updates it, or creates a new one if not found.
        """
        # Get existing summaries
        existing = await self.get_weekly_summary(
            spreadsheet_id=spreadsheet_id,
            employee_id=employee_id,
            week_start=week_start
        )
        
        week_end = week_start + timedelta(days=6)
        
        if existing:
            # TODO: Implement update logic using spreadsheets.values.update API
            logger.info(f"Weekly summary exists for {employee_id}, week {week_start}")
        else:
            # Create new summary
            await self.append_weekly_summary(
                spreadsheet_id=spreadsheet_id,
                employee_id=employee_id,
                week_start=week_start,
                week_end=week_end,
                summary_data=summary_data
            )
    
    async def get_spreadsheet_info(self, spreadsheet_id: str) -> Dict[str, Any]:
        """Get spreadsheet metadata"""
        url = f"{self.BASE_URL}/{spreadsheet_id}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()


# Global instance (will be initialized with access token at runtime)
google_sheets_oauth = GoogleSheetsOAuth()


async def get_google_sheets_api(access_token: str) -> GoogleSheetsAPI:
    """Factory function to create GoogleSheetsAPI instance"""
    return GoogleSheetsAPI(access_token=access_token)
