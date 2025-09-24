import sqlite3
import aiosqlite
import json
from datetime import datetime
from typing import Dict, Any, Optional
import logging
import os

logger = logging.getLogger(__name__)

class ConversationLogger:
    def __init__(self, db_path: str = "conversations.db"):
        self.db_path = db_path
        self.initialized = False
    
    async def initialize(self):
        """Initialize the database and create tables"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        conversation_id TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        sentiment_score REAL,
                        sentiment_label TEXT,
                        sentiment_confidence REAL,
                        crisis_detected BOOLEAN DEFAULT FALSE,
                        severity TEXT DEFAULT 'low',
                        response_time_ms INTEGER,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_conversation_id 
                    ON conversations(conversation_id)
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_timestamp 
                    ON conversations(timestamp)
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_crisis 
                    ON conversations(crisis_detected)
                """)
                
                await db.commit()
            
            self.initialized = True
            logger.info(f"Database initialized at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            self.initialized = False
    
    async def log_conversation(
        self,
        conversation_id: str,
        sentiment: Dict[str, Any],
        crisis_detected: bool = False,
        severity: str = "low",
        response_time_ms: Optional[int] = None
    ):
        """Log conversation metadata (anonymized)"""
        if not self.initialized:
            await self.initialize()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO conversations (
                        conversation_id, timestamp, sentiment_score, 
                        sentiment_label, sentiment_confidence, crisis_detected, 
                        severity, response_time_ms
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    conversation_id,
                    datetime.now().isoformat(),
                    sentiment.get("score", 0.0),
                    sentiment.get("label", "neutral"),
                    sentiment.get("confidence", 0.0),
                    crisis_detected,
                    severity,
                    response_time_ms
                ))
                
                await db.commit()
            
        except Exception as e:
            logger.error(f"Failed to log conversation: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get anonymized conversation statistics"""
        if not self.initialized:
            return {"error": "Database not initialized"}
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Total conversations
                cursor = await db.execute("SELECT COUNT(*) FROM conversations")
                total_conversations = (await cursor.fetchone())[0]
                
                # Crisis events
                cursor = await db.execute(
                    "SELECT COUNT(*) FROM conversations WHERE crisis_detected = TRUE"
                )
                crisis_count = (await cursor.fetchone())[0]
                
                # Sentiment distribution
                cursor = await db.execute("""
                    SELECT sentiment_label, COUNT(*) as count 
                    FROM conversations 
                    GROUP BY sentiment_label
                """)
                sentiment_dist = dict(await cursor.fetchall())
                
                # Average response time
                cursor = await db.execute("""
                    SELECT AVG(response_time_ms) 
                    FROM conversations 
                    WHERE response_time_ms IS NOT NULL
                """)
                avg_response_time = (await cursor.fetchone())[0]
                
                # Recent activity (last 24 hours)
                cursor = await db.execute("""
                    SELECT COUNT(*) FROM conversations 
                    WHERE datetime(timestamp) > datetime('now', '-1 day')
                """)
                recent_activity = (await cursor.fetchone())[0]
                
                return {
                    "total_conversations": total_conversations,
                    "crisis_events": crisis_count,
                    "crisis_rate": crisis_count / max(total_conversations, 1) * 100,
                    "sentiment_distribution": sentiment_dist,
                    "avg_response_time_ms": avg_response_time,
                    "recent_activity_24h": recent_activity,
                    "last_updated": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}
    
    async def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old conversation logs for privacy"""
        if not self.initialized:
            return
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    DELETE FROM conversations 
                    WHERE datetime(timestamp) < datetime('now', '-{} days')
                """.format(days_to_keep))
                
                await db.commit()
                logger.info(f"Cleaned up conversations older than {days_to_keep} days")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")