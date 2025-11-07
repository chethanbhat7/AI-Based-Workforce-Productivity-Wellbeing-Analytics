"""
M2SYS CloudABIS Biometric Authentication Integration
Handles biometric identification and attendance tracking
"""
import httpx
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
import base64
import json

from config import settings

logger = logging.getLogger(__name__)


class CloudABISAuth:
    """CloudABIS Authentication handler"""
    
    def __init__(self):
        self.app_key = settings.CLOUDABIS_APP_KEY
        self.secret_key = settings.CLOUDABIS_SECRET_KEY
        self.customer_key = settings.CLOUDABIS_CUSTOMER_KEY
        self.base_url = settings.CLOUDABIS_BASE_URL
        self.engine_name = settings.CLOUDABIS_ENGINE_NAME
    
    def get_auth_token(self) -> str:
        """
        Generate authentication token for CloudABIS API
        Format: Base64(AppKey:SecretKey)
        """
        credentials = f"{self.app_key}:{self.secret_key}"
        token = base64.b64encode(credentials.encode()).decode()
        return f"Basic {token}"


class CloudABISAPI:
    """CloudABIS API for biometric operations and attendance tracking"""
    
    def __init__(self):
        self.auth = CloudABISAuth()
        self.base_url = self.auth.base_url
        self.customer_key = self.auth.customer_key
        self.engine_name = self.auth.engine_name
        self.headers = {
            "Authorization": self.auth.get_auth_token(),
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def _make_request(
        self,
        endpoint: str,
        method: str = "POST",
        data: Optional[Dict] = None
    ) -> Dict:
        """Make authenticated request to CloudABIS API"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{self.base_url}/{endpoint}"
                
                if method == "POST":
                    response = await client.post(url, headers=self.headers, json=data)
                elif method == "GET":
                    response = await client.get(url, headers=self.headers, params=data)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response.json()
        
        except Exception as e:
            logger.error(f"Error making CloudABIS request to {endpoint}: {e}")
            raise
    
    async def register_employee(
        self,
        employee_id: str,
        biometric_data: Dict,
        registration_id: Optional[str] = None
    ) -> Dict:
        """
        Register employee biometric data
        
        Args:
            employee_id: Unique employee identifier
            biometric_data: Dictionary containing biometric samples
                {
                    "fingerprint": "base64_encoded_fingerprint",
                    "face": "base64_encoded_face_image",
                    "iris": "base64_encoded_iris_scan"
                }
            registration_id: Optional custom registration ID
        
        Returns:
            Registration response with success status
        """
        try:
            payload = {
                "CustomerKey": self.customer_key,
                "EngineName": self.engine_name,
                "RegistrationID": registration_id or employee_id,
                "Format": "ISO",
                "BiometricXml": self._build_biometric_xml(biometric_data)
            }
            
            result = await self._make_request("Register", method="POST", data=payload)
            
            return {
                "success": result.get("ResponseCode") == "1",
                "message": result.get("Message"),
                "registration_id": registration_id or employee_id,
                "employee_id": employee_id
            }
        
        except Exception as e:
            logger.error(f"Error registering employee {employee_id}: {e}")
            raise
    
    async def identify_employee(
        self,
        biometric_sample: str,
        biometric_type: str = "fingerprint"
    ) -> Dict:
        """
        Identify employee from biometric scan
        
        Args:
            biometric_sample: Base64 encoded biometric sample
            biometric_type: Type of biometric (fingerprint, face, iris)
        
        Returns:
            Identification result with employee_id and match score
        """
        try:
            payload = {
                "CustomerKey": self.customer_key,
                "EngineName": self.engine_name,
                "Format": "ISO",
                "BiometricXml": self._build_biometric_xml({biometric_type: biometric_sample})
            }
            
            result = await self._make_request("Identify", method="POST", data=payload)
            
            return {
                "success": result.get("ResponseCode") == "1",
                "employee_id": result.get("BestResult", {}).get("ID"),
                "match_score": result.get("BestResult", {}).get("Score"),
                "match_count": result.get("MatchingResults", {}).get("MatchCount", 0),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error identifying employee: {e}")
            raise
    
    async def record_punch_in(
        self,
        employee_id: str,
        biometric_sample: str,
        location: Optional[str] = None,
        device_id: Optional[str] = None
    ) -> Dict:
        """
        Record employee punch-in (clock in)
        
        Args:
            employee_id: Employee identifier
            biometric_sample: Biometric data for verification
            location: Optional location/branch
            device_id: Optional device identifier
        
        Returns:
            Punch-in record with timestamp and verification status
        """
        try:
            # First, verify identity
            identification = await self.identify_employee(biometric_sample)
            
            if not identification["success"]:
                return {
                    "success": False,
                    "message": "Biometric verification failed",
                    "error": "VERIFICATION_FAILED"
                }
            
            if identification["employee_id"] != employee_id:
                return {
                    "success": False,
                    "message": "Employee ID mismatch",
                    "error": "ID_MISMATCH"
                }
            
            punch_time = datetime.utcnow()
            
            punch_record = {
                "employee_id": employee_id,
                "punch_type": "IN",
                "punch_time": punch_time.isoformat(),
                "biometric_match_score": identification["match_score"],
                "location": location or "default",
                "device_id": device_id or "unknown",
                "verified": True
            }
            
            # In production, save to database here
            logger.info(f"Punch-in recorded for {employee_id} at {punch_time}")
            
            return {
                "success": True,
                "punch_record": punch_record,
                "message": "Punch-in successful"
            }
        
        except Exception as e:
            logger.error(f"Error recording punch-in for {employee_id}: {e}")
            raise
    
    async def record_punch_out(
        self,
        employee_id: str,
        biometric_sample: str,
        location: Optional[str] = None,
        device_id: Optional[str] = None
    ) -> Dict:
        """
        Record employee punch-out (clock out)
        
        Args:
            employee_id: Employee identifier
            biometric_sample: Biometric data for verification
            location: Optional location/branch
            device_id: Optional device identifier
        
        Returns:
            Punch-out record with timestamp, verification, and daily summary
        """
        try:
            # Verify identity
            identification = await self.identify_employee(biometric_sample)
            
            if not identification["success"]:
                return {
                    "success": False,
                    "message": "Biometric verification failed",
                    "error": "VERIFICATION_FAILED"
                }
            
            if identification["employee_id"] != employee_id:
                return {
                    "success": False,
                    "message": "Employee ID mismatch",
                    "error": "ID_MISMATCH"
                }
            
            punch_time = datetime.utcnow()
            
            punch_record = {
                "employee_id": employee_id,
                "punch_type": "OUT",
                "punch_time": punch_time.isoformat(),
                "biometric_match_score": identification["match_score"],
                "location": location or "default",
                "device_id": device_id or "unknown",
                "verified": True
            }
            
            # In production, calculate hours from punch-in time in database
            logger.info(f"Punch-out recorded for {employee_id} at {punch_time}")
            
            return {
                "success": True,
                "punch_record": punch_record,
                "message": "Punch-out successful"
            }
        
        except Exception as e:
            logger.error(f"Error recording punch-out for {employee_id}: {e}")
            raise
    
    async def get_attendance_records(
        self,
        employee_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """
        Get attendance records for an employee
        
        Args:
            employee_id: Employee identifier
            start_date: Start date for records
            end_date: End date for records
        
        Returns:
            List of attendance records
        """
        try:
            # In production, query from database
            # This is a placeholder that would fetch from your DB
            # where punch records are stored
            
            logger.info(f"Fetching attendance for {employee_id} from {start_date} to {end_date}")
            
            # Placeholder return
            return []
        
        except Exception as e:
            logger.error(f"Error getting attendance records: {e}")
            raise
    
    async def calculate_attendance_metrics(
        self,
        employee_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        Calculate attendance metrics from punch records
        
        Args:
            employee_id: Employee identifier
            start_date: Start date for calculation
            end_date: End date for calculation
        
        Returns:
            Dictionary of attendance metrics
        """
        try:
            # Get attendance records (from database in production)
            records = await self.get_attendance_records(employee_id, start_date, end_date)
            
            # Calculate metrics
            days_range = (end_date - start_date).days + 1
            work_days = days_range * 5 / 7  # Approximate weekdays
            
            # Initialize counters
            total_days_present = 0
            late_arrivals = 0
            early_departures = 0
            total_hours = 0.0
            daily_hours = []
            overtime_hours = 0.0
            
            # Group records by date
            daily_records = {}
            for record in records:
                date = datetime.fromisoformat(record["punch_time"]).date()
                if date not in daily_records:
                    daily_records[date] = {"in": None, "out": None}
                
                if record["punch_type"] == "IN":
                    daily_records[date]["in"] = datetime.fromisoformat(record["punch_time"])
                else:
                    daily_records[date]["out"] = datetime.fromisoformat(record["punch_time"])
            
            # Calculate daily metrics
            for date, punches in daily_records.items():
                if punches["in"] and punches["out"]:
                    total_days_present += 1
                    
                    # Check late arrival (after 9 AM)
                    if punches["in"].hour >= 9 and punches["in"].minute > 0:
                        late_arrivals += 1
                    
                    # Check early departure (before 5 PM)
                    if punches["out"].hour < 17:
                        early_departures += 1
                    
                    # Calculate hours worked
                    hours_worked = (punches["out"] - punches["in"]).total_seconds() / 3600
                    daily_hours.append(hours_worked)
                    total_hours += hours_worked
                    
                    # Calculate overtime (>8 hours)
                    if hours_worked > 8:
                        overtime_hours += (hours_worked - 8)
            
            # Calculate aggregates
            avg_daily_hours = total_hours / total_days_present if total_days_present > 0 else 0
            variance_hours = sum((h - avg_daily_hours) ** 2 for h in daily_hours) / len(daily_hours) if daily_hours else 0
            absenteeism_rate = (work_days - total_days_present) / work_days if work_days > 0 else 0
            punctuality_score = 1 - (late_arrivals / total_days_present) if total_days_present > 0 else 0
            
            weeks = max((end_date - start_date).days / 7, 1)
            
            return {
                "employee_id": employee_id,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "total_days_present": total_days_present,
                "total_days_expected": int(work_days),
                "late_start_count_per_week": late_arrivals / weeks,
                "early_exit_count_per_week": early_departures / weeks,
                "total_hours_per_week": total_hours / weeks,
                "variance_in_work_hours": variance_hours,
                "absenteeism_rate": round(absenteeism_rate, 3),
                "avg_daily_hours": round(avg_daily_hours, 2),
                "punctuality_score": round(punctuality_score, 2),
                "overtime_hours": round(overtime_hours, 2),
                "daily_hours_list": daily_hours
            }
        
        except Exception as e:
            logger.error(f"Error calculating attendance metrics: {e}")
            raise
    
    async def get_realtime_attendance_status(
        self,
        employee_id: str
    ) -> Dict:
        """
        Get current attendance status for employee
        
        Args:
            employee_id: Employee identifier
        
        Returns:
            Current attendance status
        """
        try:
            # In production, query most recent punch record from database
            # Check if there's an unpaired punch-in (no punch-out yet)
            
            # Placeholder
            return {
                "employee_id": employee_id,
                "status": "UNKNOWN",  # IN_OFFICE, OUT, ON_BREAK
                "last_punch_time": None,
                "last_punch_type": None,
                "hours_today": 0.0
            }
        
        except Exception as e:
            logger.error(f"Error getting realtime status: {e}")
            raise
    
    def _build_biometric_xml(self, biometric_data: Dict) -> str:
        """
        Build BiometricXml format for CloudABIS API
        
        Args:
            biometric_data: Dictionary with biometric samples
        
        Returns:
            XML string formatted for CloudABIS
        """
        # Simplified XML builder - in production use proper XML library
        xml_parts = ['<?xml version="1.0" encoding="utf-8"?>', '<BiometricData>']
        
        if "fingerprint" in biometric_data:
            xml_parts.append(f'<Fingerprint>{biometric_data["fingerprint"]}</Fingerprint>')
        
        if "face" in biometric_data:
            xml_parts.append(f'<Face>{biometric_data["face"]}</Face>')
        
        if "iris" in biometric_data:
            xml_parts.append(f'<Iris>{biometric_data["iris"]}</Iris>')
        
        xml_parts.append('</BiometricData>')
        
        return ''.join(xml_parts)
    
    async def verify_employee(
        self,
        employee_id: str,
        biometric_sample: str,
        biometric_type: str = "fingerprint"
    ) -> Dict:
        """
        Verify employee identity (1:1 verification)
        
        Args:
            employee_id: Employee to verify
            biometric_sample: Biometric sample
            biometric_type: Type of biometric
        
        Returns:
            Verification result
        """
        try:
            payload = {
                "CustomerKey": self.customer_key,
                "EngineName": self.engine_name,
                "RegistrationID": employee_id,
                "Format": "ISO",
                "BiometricXml": self._build_biometric_xml({biometric_type: biometric_sample})
            }
            
            result = await self._make_request("Verify", method="POST", data=payload)
            
            return {
                "success": result.get("ResponseCode") == "1",
                "verified": result.get("IsVerified", False),
                "match_score": result.get("MatchScore", 0),
                "employee_id": employee_id
            }
        
        except Exception as e:
            logger.error(f"Error verifying employee {employee_id}: {e}")
            raise
    
    async def remove_employee(
        self,
        employee_id: str
    ) -> Dict:
        """
        Remove employee biometric data
        
        Args:
            employee_id: Employee identifier
        
        Returns:
            Removal confirmation
        """
        try:
            payload = {
                "CustomerKey": self.customer_key,
                "EngineName": self.engine_name,
                "RegistrationID": employee_id
            }
            
            result = await self._make_request("RemoveID", method="POST", data=payload)
            
            return {
                "success": result.get("ResponseCode") == "1",
                "message": result.get("Message"),
                "employee_id": employee_id
            }
        
        except Exception as e:
            logger.error(f"Error removing employee {employee_id}: {e}")
            raise


# Singleton instance
cloudabis_api = CloudABISAPI()
