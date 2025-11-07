"""
Attendance Tracking API Routes
Handles biometric punch in/out and attendance reporting
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
import logging

from integrations.cloudabis import cloudabis_api
from database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/attendance", tags=["Attendance"])


# Request/Response Models
class BiometricSample(BaseModel):
    """Biometric sample for authentication"""
    sample_data: str = Field(..., description="Base64 encoded biometric sample")
    biometric_type: str = Field(default="fingerprint", description="Type: fingerprint, face, iris")


class PunchInRequest(BaseModel):
    """Request model for punch-in"""
    employee_id: str = Field(..., description="Employee identifier")
    biometric_sample: BiometricSample
    location: Optional[str] = Field(None, description="Punch location/branch")
    device_id: Optional[str] = Field(None, description="Biometric device ID")


class PunchOutRequest(BaseModel):
    """Request model for punch-out"""
    employee_id: str = Field(..., description="Employee identifier")
    biometric_sample: BiometricSample
    location: Optional[str] = Field(None, description="Punch location/branch")
    device_id: Optional[str] = Field(None, description="Biometric device ID")


class EmployeeRegistration(BaseModel):
    """Request model for employee biometric registration"""
    employee_id: str = Field(..., description="Employee identifier")
    fingerprint: Optional[str] = Field(None, description="Base64 encoded fingerprint")
    face: Optional[str] = Field(None, description="Base64 encoded face image")
    iris: Optional[str] = Field(None, description="Base64 encoded iris scan")
    registration_id: Optional[str] = Field(None, description="Custom registration ID")


class AttendanceMetricsRequest(BaseModel):
    """Request model for attendance metrics"""
    employee_id: str
    start_date: datetime
    end_date: datetime


class PunchRecord(BaseModel):
    """Punch record response model"""
    employee_id: str
    punch_type: str
    punch_time: datetime
    biometric_match_score: float
    location: str
    device_id: str
    verified: bool


class AttendanceStatusResponse(BaseModel):
    """Current attendance status"""
    employee_id: str
    status: str  # IN_OFFICE, OUT, ON_BREAK
    last_punch_time: Optional[datetime]
    last_punch_type: Optional[str]
    hours_today: float


# Routes
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_employee_biometric(
    registration: EmployeeRegistration
):
    """
    Register employee biometric data
    
    This endpoint enrolls an employee's biometric data (fingerprint, face, or iris)
    into the CloudABIS system for future identification.
    """
    try:
        # Build biometric data dictionary
        biometric_data = {}
        if registration.fingerprint:
            biometric_data["fingerprint"] = registration.fingerprint
        if registration.face:
            biometric_data["face"] = registration.face
        if registration.iris:
            biometric_data["iris"] = registration.iris
        
        if not biometric_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one biometric sample is required"
            )
        
        # Register with CloudABIS
        result = await cloudabis_api.register_employee(
            employee_id=registration.employee_id,
            biometric_data=biometric_data,
            registration_id=registration.registration_id
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message", "Registration failed")
            )
        
        logger.info(f"Employee {registration.employee_id} registered successfully")
        
        return {
            "message": "Employee biometric registered successfully",
            "employee_id": registration.employee_id,
            "registration_id": result["registration_id"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering employee: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/punch-in", response_model=dict)
async def punch_in(request: PunchInRequest):
    """
    Record employee punch-in (clock in)
    
    Verifies employee identity using biometric authentication and records
    the punch-in time. Triggers data collection from other APIs.
    """
    try:
        # Record punch-in with biometric verification
        result = await cloudabis_api.record_punch_in(
            employee_id=request.employee_id,
            biometric_sample=request.biometric_sample.sample_data,
            location=request.location,
            device_id=request.device_id
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result.get("message", "Punch-in verification failed")
            )
        
        punch_record = result["punch_record"]
        
        # TODO: Store punch record in Google Sheets
        # TODO: Trigger background data collection from APIs
        
        logger.info(f"Punch-in successful for {request.employee_id}")
        
        return {
            "success": True,
            "message": "Punch-in successful",
            "employee_id": punch_record["employee_id"],
            "punch_time": punch_record["punch_time"],
            "match_score": punch_record["biometric_match_score"],
            "location": punch_record["location"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during punch-in: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Punch-in failed: {str(e)}"
        )


@router.post("/punch-out", response_model=dict)
async def punch_out(request: PunchOutRequest):
    """
    Record employee punch-out (clock out)
    
    Verifies employee identity using biometric authentication and records
    the punch-out time. Calculates daily hours and updates metrics.
    """
    try:
        # Record punch-out with biometric verification
        result = await cloudabis_api.record_punch_out(
            employee_id=request.employee_id,
            biometric_sample=request.biometric_sample.sample_data,
            location=request.location,
            device_id=request.device_id
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result.get("message", "Punch-out verification failed")
            )
        
        punch_record = result["punch_record"]
        
        # TODO: Store punch record in Google Sheets
        # TODO: Calculate daily hours from punch-in to punch-out
        # TODO: Update attendance metrics
        
        logger.info(f"Punch-out successful for {request.employee_id}")
        
        return {
            "success": True,
            "message": "Punch-out successful",
            "employee_id": punch_record["employee_id"],
            "punch_time": punch_record["punch_time"],
            "match_score": punch_record["biometric_match_score"],
            "location": punch_record["location"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during punch-out: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Punch-out failed: {str(e)}"
        )


@router.get("/status/{employee_id}", response_model=AttendanceStatusResponse)
async def get_attendance_status(employee_id: str):
    """
    Get current attendance status for an employee
    
    Returns whether the employee is currently in office, their last punch time,
    and hours worked today.
    """
    try:
        status_result = await cloudabis_api.get_realtime_attendance_status(
            employee_id=employee_id
        )
        
        return AttendanceStatusResponse(**status_result)
    
    except Exception as e:
        logger.error(f"Error getting attendance status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get attendance status: {str(e)}"
        )


@router.post("/metrics", response_model=dict)
async def get_attendance_metrics(request: AttendanceMetricsRequest):
    """
    Calculate attendance metrics for an employee
    
    Returns comprehensive attendance statistics including:
    - Days present/absent
    - Late arrivals and early departures
    - Total hours worked
    - Punctuality score
    - Overtime hours
    """
    try:
        metrics = await cloudabis_api.calculate_attendance_metrics(
            employee_id=request.employee_id,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        return {
            "success": True,
            "metrics": metrics
        }
    
    except Exception as e:
        logger.error(f"Error calculating metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate metrics: {str(e)}"
        )


@router.get("/records/{employee_id}")
async def get_attendance_records(
    employee_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """
    Get punch records for an employee
    
    Returns all punch-in/out records for the specified date range.
    If no dates provided, returns last 7 days.
    """
    try:
        # Default to last 7 days if not specified
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=7)
        
        records = await cloudabis_api.get_attendance_records(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "success": True,
            "employee_id": employee_id,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_records": len(records),
            "records": records
        }
    
    except Exception as e:
        logger.error(f"Error getting attendance records: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get records: {str(e)}"
        )


@router.delete("/employee/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_employee_biometric(employee_id: str):
    """
    Remove employee biometric data
    
    Deletes all biometric data for the employee from CloudABIS.
    Use this when an employee leaves the organization.
    """
    try:
        result = await cloudabis_api.remove_employee(employee_id=employee_id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message", "Failed to remove employee")
            )
        
        logger.info(f"Employee {employee_id} biometric data removed")
        
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing employee: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove employee: {str(e)}"
        )


@router.post("/verify")
async def verify_employee(
    employee_id: str,
    biometric_sample: BiometricSample
):
    """
    Verify employee identity (1:1 verification)
    
    Checks if the provided biometric sample matches the registered
    employee without searching the entire database.
    """
    try:
        result = await cloudabis_api.verify_employee(
            employee_id=employee_id,
            biometric_sample=biometric_sample.sample_data,
            biometric_type=biometric_sample.biometric_type
        )
        
        return {
            "success": result["success"],
            "verified": result.get("verified", False),
            "match_score": result.get("match_score", 0),
            "employee_id": employee_id
        }
    
    except Exception as e:
        logger.error(f"Error verifying employee: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}"
        )
