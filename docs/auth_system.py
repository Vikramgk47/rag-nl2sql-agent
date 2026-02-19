#!/usr/bin/env python3
"""
Advanced Role-Based Access Control System for Text-to-SQL Application
Supports multiple user roles with different permissions and capabilities.
"""

import sqlite3
import hashlib
import secrets
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import os

class UserRole:
    """Define user roles and their permissions"""
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"
    GUEST = "guest"

class Permission:
    """Define granular permissions"""
    # Query permissions
    READ_DATA = "read_data"
    WRITE_DATA = "write_data"
    DELETE_DATA = "delete_data"
    
    # System permissions
    MANAGE_USERS = "manage_users"
    VIEW_ANALYTICS = "view_analytics"
    EXPORT_DATA = "export_data"
    
    # Advanced features
    CREATE_DASHBOARDS = "create_dashboards"
    MANAGE_SCHEMAS = "manage_schemas"
    VIEW_QUERY_HISTORY = "view_query_history"
    SHARE_QUERIES = "share_queries"

# Role-Permission mapping
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [
        Permission.READ_DATA, Permission.WRITE_DATA, Permission.DELETE_DATA,
        Permission.MANAGE_USERS, Permission.VIEW_ANALYTICS, Permission.EXPORT_DATA,
        Permission.CREATE_DASHBOARDS, Permission.MANAGE_SCHEMAS, 
        Permission.VIEW_QUERY_HISTORY, Permission.SHARE_QUERIES
    ],
    UserRole.ANALYST: [
        Permission.READ_DATA, Permission.WRITE_DATA, Permission.VIEW_ANALYTICS,
        Permission.EXPORT_DATA, Permission.CREATE_DASHBOARDS, 
        Permission.VIEW_QUERY_HISTORY, Permission.SHARE_QUERIES
    ],
    UserRole.VIEWER: [
        Permission.READ_DATA, Permission.VIEW_ANALYTICS, Permission.EXPORT_DATA,
        Permission.VIEW_QUERY_HISTORY
    ],
    UserRole.GUEST: [
        Permission.READ_DATA
    ]
}

class AuthSystem:
    """Advanced authentication and authorization system"""
    
    def __init__(self, db_path: str = "database/auth.db"):
        self.db_path = db_path
        self.session_timeout = timedelta(hours=8)  # 8-hour sessions
        self._ensure_auth_db()
        self._create_default_admin()
    
    def _ensure_auth_db(self):
        """Create authentication database and tables"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'guest',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                failed_login_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP NULL
            )
        """)
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Query history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                natural_query TEXT NOT NULL,
                generated_sql TEXT NOT NULL,
                execution_time REAL,
                result_count INTEGER,
                status TEXT NOT NULL,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # User preferences table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id INTEGER PRIMARY KEY,
                theme TEXT DEFAULT 'light',
                default_limit INTEGER DEFAULT 100,
                favorite_queries TEXT,  -- JSON array
                dashboard_layout TEXT,  -- JSON object
                notification_settings TEXT,  -- JSON object
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _create_default_admin(self):
        """Create default admin user if no users exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            # Create default admin
            salt = secrets.token_hex(32)
            password_hash = self._hash_password("admin123", salt)
            
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, salt, role, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ("admin", "admin@texttosql.com", password_hash, salt, UserRole.ADMIN, True))
            
            user_id = cursor.lastrowid
            
            # Create default preferences
            cursor.execute("""
                INSERT INTO user_preferences (user_id, favorite_queries, dashboard_layout, notification_settings)
                VALUES (?, ?, ?, ?)
            """, (user_id, "[]", "{}", "{}"))
            
            conn.commit()
        
        conn.close()
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with salt"""
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    
    def _generate_session_token(self) -> str:
        """Generate secure session token"""
        return secrets.token_urlsafe(32)
    
    def create_user(self, username: str, email: str, password: str, role: str = UserRole.GUEST) -> bool:
        """Create new user account"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
            if cursor.fetchone():
                return False
            
            # Create user
            salt = secrets.token_hex(32)
            password_hash = self._hash_password(password, salt)
            
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, salt, role, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, email, password_hash, salt, role, True))
            
            user_id = cursor.lastrowid
            
            # Create default preferences
            cursor.execute("""
                INSERT INTO user_preferences (user_id, favorite_queries, dashboard_layout, notification_settings)
                VALUES (?, ?, ?, ?)
            """, (user_id, "[]", "{}", "{}"))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            st.error(f"Error creating user: {e}")
            return False
    
    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and create session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get user
            cursor.execute("""
                SELECT id, username, email, password_hash, salt, role, is_active, 
                       failed_login_attempts, locked_until
                FROM users WHERE username = ? OR email = ?
            """, (username, username))
            
            user_data = cursor.fetchone()
            if not user_data:
                return None
            
            user_id, username, email, stored_hash, salt, role, is_active, failed_attempts, locked_until = user_data
            
            # Check if account is locked
            if locked_until and datetime.fromisoformat(locked_until) > datetime.now():
                st.error("Account is temporarily locked due to multiple failed login attempts")
                return None
            
            # Check if account is active
            if not is_active:
                st.error("Account is deactivated")
                return None
            
            # Verify password
            password_hash = self._hash_password(password, salt)
            if password_hash != stored_hash:
                # Increment failed attempts
                failed_attempts += 1
                lock_time = None
                if failed_attempts >= 5:
                    lock_time = datetime.now() + timedelta(minutes=30)
                
                cursor.execute("""
                    UPDATE users SET failed_login_attempts = ?, locked_until = ? 
                    WHERE id = ?
                """, (failed_attempts, lock_time.isoformat() if lock_time else None, user_id))
                conn.commit()
                return None
            
            # Reset failed attempts and create session
            cursor.execute("""
                UPDATE users SET failed_login_attempts = 0, locked_until = NULL, last_login = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (user_id,))
            
            # Create session
            session_token = self._generate_session_token()
            expires_at = datetime.now() + self.session_timeout
            
            cursor.execute("""
                INSERT INTO sessions (user_id, session_token, expires_at, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, session_token, expires_at.isoformat(), "127.0.0.1", "Streamlit"))
            
            conn.commit()
            
            return {
                "user_id": user_id,
                "username": username,
                "email": email,
                "role": role,
                "session_token": session_token,
                "permissions": ROLE_PERMISSIONS.get(role, [])
            }
            
        except Exception as e:
            st.error(f"Authentication error: {e}")
            return None
        finally:
            conn.close()
    
    def validate_session(self, session_token: str) -> Optional[Dict]:
        """Validate session token and return user info"""
        if not session_token:
            return None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT s.user_id, s.expires_at, u.username, u.email, u.role, u.is_active
                FROM sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_token = ? AND s.is_active = TRUE
            """, (session_token,))
            
            session_data = cursor.fetchone()
            if not session_data:
                return None
            
            user_id, expires_at, username, email, role, is_active = session_data
            
            # Check if session expired
            if datetime.fromisoformat(expires_at) < datetime.now():
                cursor.execute("UPDATE sessions SET is_active = FALSE WHERE session_token = ?", (session_token,))
                conn.commit()
                return None
            
            # Check if user is still active
            if not is_active:
                return None
            
            return {
                "user_id": user_id,
                "username": username,
                "email": email,
                "role": role,
                "permissions": ROLE_PERMISSIONS.get(role, [])
            }
            
        except Exception as e:
            st.error(f"Session validation error: {e}")
            return None
        finally:
            conn.close()
    
    def logout(self, session_token: str):
        """Logout user by invalidating session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE sessions SET is_active = FALSE WHERE session_token = ?", (session_token,))
        conn.commit()
        conn.close()
    
    def has_permission(self, user_info: Dict, permission: str) -> bool:
        """Check if user has specific permission"""
        return permission in user_info.get("permissions", [])
    
    def get_all_users(self) -> List[Dict]:
        """Get all users (admin only)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, email, role, is_active, created_at, last_login
            FROM users ORDER BY created_at DESC
        """)
        
        users = []
        for row in cursor.fetchall():
            users.append({
                "id": row[0],
                "username": row[1],
                "email": row[2],
                "role": row[3],
                "is_active": bool(row[4]),
                "created_at": row[5],
                "last_login": row[6]
            })
        
        conn.close()
        return users
    
    def update_user_role(self, user_id: int, new_role: str) -> bool:
        """Update user role (admin only)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error updating user role: {e}")
            return False
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate user account (admin only)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("UPDATE users SET is_active = FALSE WHERE id = ?", (user_id,))
            cursor.execute("UPDATE sessions SET is_active = FALSE WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error deactivating user: {e}")
            return False
    
    def log_query(self, user_id: int, natural_query: str, generated_sql: str, 
                 execution_time: float = None, result_count: int = None, 
                 status: str = "success", error_message: str = None):
        """Log user query for audit and analytics"""
        # Skip logging for demo users
        if user_id == 999:  # Demo user ID
            return
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO query_history 
                (user_id, natural_query, generated_sql, execution_time, result_count, status, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, natural_query, generated_sql, execution_time, result_count, status, error_message))
            
            conn.commit()
            conn.close()
        except Exception as e:
            # Don't show error to user, just log it
            print(f"Error logging query: {e}")
    
    def get_user_query_history(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get user's query history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT natural_query, generated_sql, execution_time, result_count, 
                   status, error_message, created_at
            FROM query_history 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (user_id, limit))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                "natural_query": row[0],
                "generated_sql": row[1],
                "execution_time": row[2],
                "result_count": row[3],
                "status": row[4],
                "error_message": row[5],
                "created_at": row[6]
            })
        
        conn.close()
        return history

# Streamlit session state helpers
def init_auth_session():
    """Initialize authentication session state"""
    if 'auth_system' not in st.session_state:
        st.session_state.auth_system = AuthSystem()
    
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    
    if 'session_token' not in st.session_state:
        st.session_state.session_token = None

def require_login():
    """Decorator-like function to require login"""
    init_auth_session()
    
    # Check for demo mode first
    if st.session_state.get('is_demo_mode', False) and st.session_state.get('user_info'):
        return True
    
    # Check if user is logged in
    if st.session_state.session_token:
        user_info = st.session_state.auth_system.validate_session(st.session_state.session_token)
        if user_info:
            st.session_state.user_info = user_info
            return True
        else:
            # Session expired
            st.session_state.user_info = None
            st.session_state.session_token = None
    
    return False

def require_permission(permission: str) -> bool:
    """Check if current user has required permission"""
    if not st.session_state.user_info:
        return False
    
    return st.session_state.auth_system.has_permission(st.session_state.user_info, permission)

def get_current_user() -> Optional[Dict]:
    """Get current logged-in user info"""
    return st.session_state.user_info
