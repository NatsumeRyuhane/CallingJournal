# dao/user_dao.py
from typing import Optional
from datetime import time
from db.connection import DatabaseConnection, get_db_connection
from models.entities import User


class UserDAO:
    """Data Access Object for User entity."""
    
    def __init__(self, db: Optional[DatabaseConnection] = None):
        self.db = db or get_db_connection()
    
    # ==================== CREATE ====================
    
    def create(self, user: User) -> User:
        """Create a new user and return with generated ID."""
        query = """
            INSERT INTO users (phone_number, timezone, preferred_call_time, is_active)
            VALUES (%s, %s, %s, %s)
            RETURNING id, phone_number, timezone, preferred_call_time, is_active, created_at, updated_at
        """
        result = self.db.execute_returning(query, (
            user.phone_number,
            user.timezone,
            user.preferred_call_time,
            user.is_active
        ))
        return self._map_to_user(result)
    
    # ==================== READ ====================
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        query = "SELECT * FROM users WHERE id = %s"
        result = self.db.execute_one(query, (user_id,))
        return self._map_to_user(result) if result else None
    
    def get_by_phone(self, phone_number: str) -> Optional[User]:
        """Get user by phone number."""
        query = "SELECT * FROM users WHERE phone_number = %s"
        result = self.db.execute_one(query, (phone_number,))
        return self._map_to_user(result) if result else None
    
    def get_all(self, active_only: bool = False) -> list[User]:
        """Get all users, optionally filtering by active status."""
        if active_only:
            query = "SELECT * FROM users WHERE is_active = TRUE ORDER BY created_at DESC"
        else:
            query = "SELECT * FROM users ORDER BY created_at DESC"
        results = self.db.execute(query)
        return [self._map_to_user(row) for row in results]
    
    def get_users_for_scheduled_call(self, call_time: time) -> list[User]:
        """Get active users scheduled for calls at specific time."""
        query = """
            SELECT * FROM users 
            WHERE is_active = TRUE 
            AND preferred_call_time = %s
            ORDER BY timezone
        """
        results = self.db.execute(query, (call_time,))
        return [self._map_to_user(row) for row in results]
    
    # ==================== UPDATE ====================
    
    def update(self, user: User) -> Optional[User]:
        """Update user details."""
        query = """
            UPDATE users 
            SET phone_number = %s, timezone = %s, preferred_call_time = %s, 
                is_active = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING *
        """
        result = self.db.execute_returning(query, (
            user.phone_number,
            user.timezone,
            user.preferred_call_time,
            user.is_active,
            user.id
        ))
        return self._map_to_user(result) if result else None
    
    def deactivate(self, user_id: int) -> bool:
        """Deactivate a user (soft delete)."""
        query = """
            UPDATE users SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING id
        """
        result = self.db.execute_returning(query, (user_id,))
        return result is not None
    
    def activate(self, user_id: int) -> bool:
        """Activate a user."""
        query = """
            UPDATE users SET is_active = TRUE, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING id
        """
        result = self.db.execute_returning(query, (user_id,))
        return result is not None
    
    # ==================== DELETE ====================
    
    def delete(self, user_id: int) -> bool:
        """Permanently delete a user (cascades to conversations and journals)."""
        query = "DELETE FROM users WHERE id = %s RETURNING id"
        result = self.db.execute_returning(query, (user_id,))
        return result is not None
    
    # ==================== HELPER ====================
    
    def _map_to_user(self, row: dict) -> User:
        """Map database row to User entity."""
        return User(
            id=row["id"],
            phone_number=row["phone_number"],
            timezone=row["timezone"],
            preferred_call_time=row["preferred_call_time"],
            is_active=row["is_active"],
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )
