"""Health data integration service"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import httpx


class GoogleFitService:
    """Service for interacting with Google Fit API"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://www.googleapis.com/fitness/v1"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    async def get_daily_activity(
        self,
        target_date: date
    ) -> Dict[str, Any]:
        """Get daily activity summary"""
        # Convert date to milliseconds timestamp
        start_time = int(datetime.combine(target_date, datetime.min.time()).timestamp() * 1000)
        end_time = start_time + (24 * 60 * 60 * 1000)
        
        # Get steps
        steps = await self._get_aggregate_data(
            "com.google.step_count.delta",
            start_time,
            end_time
        )
        
        # Get calories
        calories = await self._get_aggregate_data(
            "com.google.calories.expended",
            start_time,
            end_time
        )
        
        # Get active minutes
        active_minutes = await self._get_aggregate_data(
            "com.google.active_minutes",
            start_time,
            end_time
        )
        
        return {
            "date": target_date.isoformat(),
            "steps": steps,
            "calories": calories,
            "active_minutes": active_minutes
        }
    
    async def _get_aggregate_data(
        self,
        data_type: str,
        start_time_millis: int,
        end_time_millis: int
    ) -> Optional[float]:
        """Get aggregated data for a specific type"""
        async with httpx.AsyncClient() as client:
            body = {
                "aggregateBy": [{
                    "dataTypeName": data_type
                }],
                "bucketByTime": {"durationMillis": end_time_millis - start_time_millis},
                "startTimeMillis": start_time_millis,
                "endTimeMillis": end_time_millis
            }
            
            response = await client.post(
                f"{self.base_url}/users/me/dataset:aggregate",
                headers=self.headers,
                json=body
            )
            
            if response.status_code == 200:
                data = response.json()
                buckets = data.get("bucket", [])
                if buckets:
                    dataset = buckets[0].get("dataset", [])
                    if dataset and dataset[0].get("point"):
                        points = dataset[0]["point"]
                        if points:
                            values = points[0].get("value", [])
                            if values:
                                return values[0].get("intVal") or values[0].get("fpVal")
            return None
    
    async def get_sleep_data(
        self,
        target_date: date
    ) -> Dict[str, Any]:
        """Get sleep data"""
        start_time = int(datetime.combine(target_date, datetime.min.time()).timestamp() * 1000)
        end_time = start_time + (24 * 60 * 60 * 1000)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/users/me/sessions",
                headers=self.headers,
                params={
                    "startTime": datetime.fromtimestamp(start_time / 1000).isoformat() + "Z",
                    "endTime": datetime.fromtimestamp(end_time / 1000).isoformat() + "Z",
                    "activityType": 72  # Sleep activity type
                }
            )
            
            if response.status_code == 200:
                sessions = response.json().get("session", [])
                if sessions:
                    sleep_session = sessions[0]
                    start = int(sleep_session["startTimeMillis"])
                    end = int(sleep_session["endTimeMillis"])
                    duration_hours = (end - start) / (1000 * 60 * 60)
                    
                    return {
                        "date": target_date.isoformat(),
                        "sleep_hours": round(duration_hours, 2),
                        "start_time": datetime.fromtimestamp(start / 1000).isoformat(),
                        "end_time": datetime.fromtimestamp(end / 1000).isoformat()
                    }
        
        return {
            "date": target_date.isoformat(),
            "sleep_hours": None
        }


class AppleHealthService:
    """Service for Apple Health data"""
    
    def __init__(self, api_key: str):
        """
        Note: Apple Health doesn't have a direct API.
        This would typically integrate with Apple HealthKit via iOS app
        or use a third-party service like Validic or Human API
        """
        self.api_key = api_key
    
    async def get_daily_activity(
        self,
        target_date: date
    ) -> Dict[str, Any]:
        """Get daily activity from Apple Health"""
        # TODO: Implement actual Apple Health integration
        # This would typically require an iOS app with HealthKit
        return {
            "date": target_date.isoformat(),
            "steps": None,
            "active_minutes": None,
            "calories": None,
            "message": "Apple Health integration requires iOS app with HealthKit"
        }
    
    async def get_sleep_data(
        self,
        target_date: date
    ) -> Dict[str, Any]:
        """Get sleep data from Apple Health"""
        # TODO: Implement actual Apple Health integration
        return {
            "date": target_date.isoformat(),
            "sleep_hours": None,
            "deep_sleep_minutes": None,
            "message": "Apple Health integration requires iOS app with HealthKit"
        }


class HealthDataAggregator:
    """Aggregator for health data from multiple sources"""
    
    def __init__(self):
        self.google_fit: Optional[GoogleFitService] = None
        self.apple_health: Optional[AppleHealthService] = None
    
    def set_google_fit(self, access_token: str):
        """Initialize Google Fit service"""
        self.google_fit = GoogleFitService(access_token)
    
    def set_apple_health(self, api_key: str):
        """Initialize Apple Health service"""
        self.apple_health = AppleHealthService(api_key)
    
    async def get_daily_summary(
        self,
        target_date: date
    ) -> Dict[str, Any]:
        """Get aggregated daily health summary from all sources"""
        summary = {
            "date": target_date.isoformat(),
            "steps": None,
            "active_minutes": None,
            "calories": None,
            "sleep_hours": None,
            "sources": []
        }
        
        # Try Google Fit first
        if self.google_fit:
            try:
                gf_data = await self.google_fit.get_daily_activity(target_date)
                summary["steps"] = gf_data.get("steps")
                summary["active_minutes"] = gf_data.get("active_minutes")
                summary["calories"] = gf_data.get("calories")
                summary["sources"].append("google_fit")
                
                sleep_data = await self.google_fit.get_sleep_data(target_date)
                summary["sleep_hours"] = sleep_data.get("sleep_hours")
            except Exception as e:
                print(f"Error fetching Google Fit data: {e}")
        
        # Fallback to Apple Health if data not available
        if self.apple_health and not summary["steps"]:
            try:
                ah_data = await self.apple_health.get_daily_activity(target_date)
                if ah_data.get("steps"):
                    summary["steps"] = ah_data["steps"]
                    summary["sources"].append("apple_health")
            except Exception as e:
                print(f"Error fetching Apple Health data: {e}")
        
        return summary

