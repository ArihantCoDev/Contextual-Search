"""
Service for async processing of user behavior events.
"""
import asyncio
from typing import Dict, Any
from app.data.event_repository import get_event_repository
from app.utils.logger import logger

class EventService:
    """
    Service to handle event ingestion asynchronously.
    
    Uses an internal queue to buffer events and a background worker
    to persist them to storage without blocking the API response.
    """
    
    def __init__(self):
        """Initialize event service with repository and queue."""
        self.repository = get_event_repository()
        # ARCHITECTURE NOTE: Async queue prevents event processing from blocking search API
        # - Events are added to queue without waiting
        # - Background worker processes events asynchronously
        # - If queue fills, events are dropped (logged) rather than blocking search
        self.queue = asyncio.Queue()
        self.is_running = False
        self.worker_task = None
        # Metrics: Track total events processed (in-memory counter)
        self.total_events_processed = 0
        
    async def start_worker(self):
        """Start the background event processing worker."""
        if self.is_running:
            return
            
        self.is_running = True
        self.worker_task = asyncio.create_task(self._worker())
        logger.info("Event processing worker started")

    async def stop_worker(self):
        """Stop the background worker gracefully."""
        self.is_running = False
        if self.worker_task:
            # Wait for queue to empty or timeout? 
            # For simplicity, we just join queue if needed, or cancel task.
            # Ideally we want to process remaining items.
            if not self.queue.empty():
                logger.info(f"Processing remaining {self.queue.qsize()} events...")
                await self.queue.join()
            
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
            logger.info("Event processing worker stopped")

    async def track_event(self, event_type: str, session_id: str, payload: Dict[str, Any]):
        """
        Add an event to the processing queue.
        
        Args:
            event_type: Name of the event
            session_id: User identifier
            payload: Arbitrary event data
        """
        event_data = {
            "event_type": event_type,
            "session_id": session_id,
            "payload": payload
        }
        # Log event ingestion
        logger.info(f"Event ingested: type={event_type}, session={session_id}")
        
        # Put into queue without blocking
        try:
            self.queue.put_nowait(event_data)
        except asyncio.QueueFull:
            logger.error(f"Event queue is full, dropping event: type={event_type}, session={session_id}")
            
    async def _worker(self):
        """Background loop to process events from the queue."""
        while self.is_running:
            try:
                # Wait for next event
                event_data = await self.queue.get()
                
                # Process event (IO bound operation)
                await self._process_event(event_data)
                
                # Mark as done
                self.queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in event worker: {e}")

    async def _process_event(self, event_data: Dict[str, Any]):
        """
        Persist event to database.
        
        In a real system, this might batch writes or send to a message broker (Kafka/SQS).
        For now, we write directly to SQLite.
        """
        try:
            # Running synchronous DB call in thread pool to avoid blocking async loop
            await asyncio.to_thread(
                self.repository.save_event,
                event_type=event_data["event_type"],
                session_id=event_data["session_id"],
                payload=event_data["payload"]
            )
            # Increment counter and log metrics periodically
            self.total_events_processed += 1
            if self.total_events_processed % 100 == 0:  # Log every 100 events
                logger.info(f"Total events processed: {self.total_events_processed}")
        except Exception as e:
            logger.error(f"Failed to save event type={event_data.get('event_type')}: {e}")


# Singleton instance
_event_service_instance = None


def get_event_service() -> EventService:
    """Get singleton event service instance."""
    global _event_service_instance
    if _event_service_instance is None:
        _event_service_instance = EventService()
    return _event_service_instance
