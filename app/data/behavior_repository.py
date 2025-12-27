"""
Repository for aggregating user behavior data from events.
"""
import sqlite3
import json
from typing import Dict, List, Any
from collections import defaultdict

from app.utils.logger import logger


class BehaviorRepository:
    """
    Repository for querying and aggregating user behavior signals.
    
    Provides metrics like click counts and simple engagement stats
    derived from the raw event stream.
    """
    
    def __init__(self, db_path: str = "data/events.db"):
        """Initialize with path to existing events database."""
        self.db_path = db_path

    def get_product_metrics(self, product_ids: List[str]) -> Dict[str, Dict[str, int]]:
        """
        Get behavior metrics for a list of products.
        
        Args:
            product_ids: List of product IDs to fetch metrics for
            
        Returns:
            Dictionary mapping product_id to metrics dict (clicks, etc.)
        """
        if not product_ids:
            return {}
            
        metrics = defaultdict(lambda: {"clicks": 0, "impressions": 0})
        
        # We'll use a relatively simple query pattern here.
        # In a high-scale production system, this would hit a pre-aggregated table (OLAP).
        # For this setup, we scan the events table.
        
        with sqlite3.connect(self.db_path) as conn:
            # Fetch click events
            # Note: We are parsing JSON in Python because SQLite's JSON support 
            # might depend on the specific build/extension availability.
            # This is safer for a portable starter kit.
            cursor = conn.execute(
                "SELECT payload FROM events WHERE event_type = 'click'"
            )
            
            for (payload_json,) in cursor:
                try:
                    payload = json.loads(payload_json)
                    pid = payload.get("product_id")
                    if pid and pid in product_ids:
                        metrics[pid]["clicks"] += 1
                except (json.JSONDecodeError, AttributeError):
                    continue
                    
        # Convert defaultdict to regular dict
        return dict(metrics)


# Singleton instance
_behavior_repository_instance = None


def get_behavior_repository() -> BehaviorRepository:
    """Get singleton behavior repository instance."""
    global _behavior_repository_instance
    if _behavior_repository_instance is None:
        _behavior_repository_instance = BehaviorRepository()
    return _behavior_repository_instance
