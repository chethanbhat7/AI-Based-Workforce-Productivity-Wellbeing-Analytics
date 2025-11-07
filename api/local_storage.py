"""
Local JSON storage fallback for OAuth tokens
Works without Firebase/Firestore
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

TOKEN_FILE = Path(__file__).parent / "local_tokens.json"


def _load_tokens() -> Dict:
    """Load tokens from local JSON file"""
    if not TOKEN_FILE.exists():
        return {"tokens": []}
    
    try:
        with open(TOKEN_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading tokens: {e}")
        return {"tokens": []}


def _save_tokens(data: Dict):
    """Save tokens to local JSON file"""
    try:
        with open(TOKEN_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Tokens saved to {TOKEN_FILE}")
    except Exception as e:
        logger.error(f"Error saving tokens: {e}")


class LocalTokenStorage:
    """Local JSON-based token storage"""
    
    def collection(self, name: str):
        """Mock Firestore collection interface"""
        return LocalCollection(name)


class LocalCollection:
    """Mock Firestore collection"""
    
    def __init__(self, name: str):
        self.name = name
    
    def add(self, data: Dict) -> Dict:
        """Add a document (token) to the collection"""
        tokens_data = _load_tokens()
        
        # Add ID and timestamp
        token_id = f"{data.get('userId')}_{data.get('provider')}_{datetime.utcnow().timestamp()}"
        doc = {
            "id": token_id,
            "collection": self.name,
            **data
        }
        
        tokens_data["tokens"].append(doc)
        _save_tokens(tokens_data)
        
        logger.info(f"✅ Token saved locally: {data.get('provider')} for user {data.get('userId')}")
        return {"id": token_id}
    
    def where(self, field: str, op: str, value: str):
        """Query documents by field"""
        return LocalQuery(self.name, field, op, value)
    
    def stream(self):
        """Stream all documents in collection"""
        tokens_data = _load_tokens()
        collection_docs = [
            LocalDocument(doc) 
            for doc in tokens_data.get("tokens", []) 
            if doc.get("collection") == self.name
        ]
        return collection_docs


class LocalQuery:
    """Mock Firestore query"""
    
    def __init__(self, collection: str, field: str, op: str, value: str):
        self.collection = collection
        self.field = field
        self.op = op
        self.value = value
        self.filters = [(field, op, value)]
    
    def where(self, field: str, op: str, value: str):
        """Add another filter"""
        self.filters.append((field, op, value))
        return self
    
    def stream(self):
        """Execute query and return matching documents"""
        tokens_data = _load_tokens()
        results = []
        
        for doc in tokens_data.get("tokens", []):
            if doc.get("collection") != self.collection:
                continue
            
            # Check all filters
            match = True
            for field, op, value in self.filters:
                doc_value = doc.get(field)
                
                if op == "==":
                    if doc_value != value:
                        match = False
                        break
                elif op == "!=":
                    if doc_value == value:
                        match = False
                        break
            
            if match:
                results.append(LocalDocument(doc))
        
        return results
    
    def limit(self, count: int):
        """Limit results (returns self for chaining)"""
        # For simplicity, just return self
        return self


class LocalDocument:
    """Mock Firestore document"""
    
    def __init__(self, data: Dict):
        self._data = data
        self.id = data.get("id", "")
    
    def to_dict(self) -> Dict:
        """Convert document to dictionary"""
        return self._data.copy()
    
    def delete(self):
        """Delete this document"""
        tokens_data = _load_tokens()
        tokens_data["tokens"] = [
            t for t in tokens_data.get("tokens", []) 
            if t.get("id") != self.id
        ]
        _save_tokens(tokens_data)
        logger.info(f"Deleted token: {self.id}")


def get_local_storage():
    """Get local storage instance"""
    return LocalTokenStorage()
