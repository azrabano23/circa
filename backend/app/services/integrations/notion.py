"""Notion integration service"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import httpx


class NotionService:
    """Service for interacting with Notion API"""
    
    def __init__(self, api_key: str, version: str = "2022-06-28"):
        self.api_key = api_key
        self.version = version
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Notion-Version": version,
            "Content-Type": "application/json"
        }
    
    async def search(self, query: str = "", filter_type: Optional[str] = None) -> List[dict]:
        """Search for pages and databases"""
        async with httpx.AsyncClient() as client:
            body = {}
            if query:
                body["query"] = query
            if filter_type:
                body["filter"] = {"property": "object", "value": filter_type}
            
            response = await client.post(
                f"{self.base_url}/search",
                headers=self.headers,
                json=body
            )
            
            if response.status_code == 200:
                return response.json().get("results", [])
            return []
    
    async def get_database(self, database_id: str) -> Optional[dict]:
        """Get a database by ID"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/databases/{database_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            return None
    
    async def query_database(
        self,
        database_id: str,
        filter_params: Optional[Dict[str, Any]] = None,
        sorts: Optional[List[Dict[str, str]]] = None
    ) -> List[dict]:
        """Query a database with optional filters and sorts"""
        async with httpx.AsyncClient() as client:
            body = {}
            if filter_params:
                body["filter"] = filter_params
            if sorts:
                body["sorts"] = sorts
            
            response = await client.post(
                f"{self.base_url}/databases/{database_id}/query",
                headers=self.headers,
                json=body
            )
            
            if response.status_code == 200:
                return response.json().get("results", [])
            return []
    
    async def get_page(self, page_id: str) -> Optional[dict]:
        """Get a page by ID"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/pages/{page_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            return None
    
    async def create_page(
        self,
        parent: Dict[str, str],
        properties: Dict[str, Any],
        children: Optional[List[dict]] = None
    ) -> Optional[dict]:
        """Create a new page"""
        async with httpx.AsyncClient() as client:
            body = {
                "parent": parent,
                "properties": properties
            }
            if children:
                body["children"] = children
            
            response = await client.post(
                f"{self.base_url}/pages",
                headers=self.headers,
                json=body
            )
            
            if response.status_code == 200:
                return response.json()
            return None
    
    async def update_page(
        self,
        page_id: str,
        properties: Dict[str, Any]
    ) -> Optional[dict]:
        """Update a page"""
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/pages/{page_id}",
                headers=self.headers,
                json={"properties": properties}
            )
            
            if response.status_code == 200:
                return response.json()
            return None
    
    async def get_tasks_from_database(
        self,
        database_id: str,
        status_property: str = "Status",
        due_date_property: str = "Due Date"
    ) -> List[dict]:
        """Get tasks from a task database"""
        # Filter for incomplete tasks
        filter_params = {
            "property": status_property,
            "status": {
                "does_not_equal": "Done"
            }
        }
        
        # Sort by due date
        sorts = [{
            "property": due_date_property,
            "direction": "ascending"
        }]
        
        pages = await self.query_database(database_id, filter_params, sorts)
        
        tasks = []
        for page in pages:
            tasks.append(self._parse_task_page(page))
        
        return tasks
    
    def _parse_task_page(self, page: dict) -> dict:
        """Parse a Notion page into a task format"""
        properties = page.get("properties", {})
        
        # Extract common properties
        title = ""
        if "Name" in properties or "Title" in properties:
            title_prop = properties.get("Name") or properties.get("Title")
            if title_prop and "title" in title_prop:
                title = "".join([t["plain_text"] for t in title_prop["title"]])
        
        due_date = None
        if "Due Date" in properties:
            date_prop = properties["Due Date"]
            if date_prop and "date" in date_prop and date_prop["date"]:
                due_date = date_prop["date"].get("start")
        
        status = ""
        if "Status" in properties:
            status_prop = properties["Status"]
            if status_prop and "status" in status_prop:
                status = status_prop["status"].get("name", "")
        
        return {
            "id": page["id"],
            "title": title,
            "due_date": due_date,
            "status": status,
            "url": page.get("url"),
            "created_time": page.get("created_time"),
            "last_edited_time": page.get("last_edited_time")
        }

