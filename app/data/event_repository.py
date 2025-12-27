"""
Repository for storing user behavior events in SQLite.
"""
import sqlite3
import json
from typing import Dict, Any, List
from pathlib import Path

from app.utils.logger import logger


class EventRepository:
    """
    Repository for persisting user events.
    
    Stores events like search, click, add_to_cart, purchase for future analysis.
    """
    
    def __init__(self, db_path: str = "data/events.db"):
        """
        Initialize the event repository.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        
        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database schema
        self._init_database()
        logger.info(f"Event repository initialized at {db_path}")

    def _init_database(self):
        """Create the events table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    session_id TEXT,
                    payload TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Index for querying by session or type
            conn.execute("CREATE INDEX IF NOT EXISTS idx_event_type ON events(event_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON events(session_id)")
            conn.commit()

    def save_event(self, event_type: str, session_id: str, payload: Dict[str, Any]):
        """
        Save a single event to the database.
        
        Args:
            event_type: Type of event (search, click, etc.)
            session_id: User session identifier
            payload: Event details as dictionary
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO events (event_type, session_id, payload)
                VALUES (?, ?, ?)
            """, (event_type, session_id, json.dumps(payload)))
            conn.commit()

    def get_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve recent events (for debugging/monitoring).
        
        Args:
            limit: Max number of events to return
            
        Returns:
            List of event dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM events ORDER BY created_at DESC LIMIT ?", 
                (limit,)
            )
            rows = cursor.fetchall()
            
            events = []
            for row in rows:
                event = dict(row)
                try:
                    event['payload'] = json.loads(event['payload'])
                except json.JSONDecodeError:
                    event['payload'] = {}
                events.append(event)
            return events

    def get_event_count(self) -> int:
        """Get total number of recorded events."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM events")
            return cursor.fetchone()[0]


# Singleton instance
_event_repository_instance = None


def get_event_repository() -> EventRepository:
    """Get singleton event repository instance."""
    global _event_repository_instance
    if _event_repository_instance is None:
        _event_repository_instance = EventRepository()
    return _event_repository_instance
