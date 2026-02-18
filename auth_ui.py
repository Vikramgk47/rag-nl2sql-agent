#!/usr/bin/env python3
"""
Authentication UI Components for Text-to-SQL Application
Provides login, registration, and user management interfaces.
"""

import streamlit as st
from auth_system import (
    AuthSystem, UserRole, Permission, ROLE_PERMISSIONS,
    init_auth_session, require_login, require_permission, get_current_user
)
from datetime import datetime
import pandas as pd

def show_login_page():
    """Display simplified login interface"""
    init_auth_session()
    
    # Centered container with simple styling
    st.markdown("""
    <div style="max-width: 600px; margin: 0 auto; padding: 2rem;">
        <h1 style="text-align: center; color: #667eea; margin-bottom: 2rem;">
            🤖 Text-to-SQL GenAI
        </h1>
        <p style="text-align: center; color: #666; margin-bottom: 3rem;">
            Convert natural language to SQL queries with AI
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Simple tab interface
    tab1, tab2 = st.tabs(["🚀 Try Demo", "🔑 Login"])
    
    with tab1:
        show_simple_demo()
    
    with tab2:
        show_simple_login()

def show_simple_demo():
    """Simplified demo mode with quick access"""
    st.markdown("### 🚀 Quick Demo Access")
    st.info("👋 **Try the app instantly with pre-configured accounts**")
    
    # Simple role selection
    demo_roles = {
        "🎯 Admin Demo": {"user": "demo_admin", "pass": "admin123", "desc": "Full access"},
        "📊 Analyst Demo": {"user": "demo_analyst", "pass": "analyst123", "desc": "Advanced queries"},
        "👁️ Viewer Demo": {"user": "demo_viewer", "pass": "viewer123", "desc": "Read-only access"},
        "👤 Guest Demo": {"user": "demo_guest", "pass": "guest123", "desc": "Basic queries"}
    }
    
    selected = st.selectbox("Choose your demo role:", list(demo_roles.keys()))
    role_info = demo_roles[selected]
    
    # Show credentials in a clean box
    st.markdown(f"""
    <div style="background: #f0f8ff; padding: 1.5rem; border-radius: 10px; margin: 1rem 0;">
        <h4 style="margin: 0; color: #667eea;">🔑 {selected}</h4>
        <p style="margin: 0.5rem 0; color: #666;">{role_info['desc']}</p>
        <div style="background: white; padding: 1rem; border-radius: 5px; margin-top: 1rem;">
            <strong>Username:</strong> <code>{role_info['user']}</code><br>
            <strong>Password:</strong> <code>{role_info['pass']}</code>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Single login button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎯 Login to Demo", type="primary", use_container_width=True, key="simple_demo_login"):
            with st.spinner("Logging in..."):
                user_info = st.session_state.auth_system.authenticate(role_info['user'], role_info['pass'])
                
            if user_info:
                st.session_state.user_info = user_info
                st.session_state.session_token = user_info["session_token"]
                st.session_state.is_demo_mode = True
                st.success(f"✅ Welcome to {selected}!")
                st.rerun()
            else:
                st.error("❌ Demo login failed. Please try again.")

def show_simple_login():
    """Simplified login form"""
    st.markdown("### 🔑 Sign In")
    st.markdown("Enter your credentials to access the application")
    
    with st.form("simple_login"):
        username = st.text_input("👤 Username", placeholder="Enter username")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter password")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            login_clicked = st.form_submit_button("🚀 Sign In", use_container_width=True)
        
        if login_clicked and username and password:
            with st.spinner("Signing in..."):
                user_info = st.session_state.auth_system.authenticate(username, password)
            
            if user_info:
                st.session_state.user_info = user_info
                st.session_state.session_token = user_info["session_token"]
                st.success(f"✅ Welcome back, {user_info['username']}!")
                st.rerun()
            else:
                st.error("❌ Invalid credentials")
        elif login_clicked:
            st.warning("⚠️ Please enter both username and password")
    
    # Help section - simplified
    with st.expander("ℹ️ Need Help?"):
        st.markdown("""
        **Demo Accounts:** Use the "Try Demo" tab for instant access
        
        **Default Admin:** username: `admin`, password: `admin123`
        
        **Register:** Contact your admin to create a new account
        """)

def show_demo_mode():
    """Legacy demo mode - kept for compatibility"""
    st.markdown("### 🚀 Demo Accounts")
    st.info("💡 **Try different roles with demo credentials - password required for all roles!**")
    
    # Role selection with descriptions and credentials
    role_options = {
        "👑 Admin Demo": {
            "role": UserRole.ADMIN,
            "username": "demo_admin",
            "password": "admin123",
            "description": "Full system access + user management + all features"
        },
        "📊 Analyst Demo": {
            "role": UserRole.ANALYST,
            "username": "demo_analyst",
            "password": "analyst123",
            "description": "Advanced queries + data modification + analytics"
        },
        "👁️ Viewer Demo": {
            "role": UserRole.VIEWER,
            "username": "demo_viewer",
            "password": "viewer123",
            "description": "Read-only access + visualizations + exports"
        },
        "👤 Guest Demo": {
            "role": UserRole.GUEST,
            "username": "demo_guest",
            "password": "guest123",
            "description": "Basic read-only queries (50 row limit)"
        }
    }
    
    selected_role = st.selectbox(
        "Choose a demo account:",
        list(role_options.keys()),
        help="Select a role to see the credentials and login"
    )
    
    # Show role description and credentials
    role_info = role_options[selected_role]
    st.markdown(f"""
    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #667eea;">
        <strong>🎭 {selected_role}</strong><br>
        <em>{role_info['description']}</em><br><br>
        <strong>🔐 Demo Credentials:</strong><br>
        <code>Username: {role_info['username']}</code><br>
        <code>Password: {role_info['password']}</code>
    </div>
    """, unsafe_allow_html=True)
    
    # Demo permissions preview
    with st.expander("🔍 See what you can do with this role"):
        permissions = ROLE_PERMISSIONS.get(role_info['role'], [])
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**✅ Allowed:**")
            for perm in permissions:
                perm_label = perm.replace('_', ' ').title()
                st.markdown(f"• {perm_label}")
        
        with col2:
            st.markdown("**❌ Restricted:**")
            all_perms = [Permission.READ_DATA, Permission.WRITE_DATA, Permission.DELETE_DATA,
                        Permission.MANAGE_USERS, Permission.VIEW_ANALYTICS, Permission.EXPORT_DATA,
                        Permission.CREATE_DASHBOARDS, Permission.MANAGE_SCHEMAS, 
                        Permission.VIEW_QUERY_HISTORY, Permission.SHARE_QUERIES]
            
            restricted = [p for p in all_perms if p not in permissions]
            for perm in restricted[:6]:  # Show first 6 restrictions
                perm_label = perm.replace('_', ' ').title()
                st.markdown(f"• {perm_label}")
    
    # Demo login form
    st.markdown("### 🔑 Login with Demo Credentials")
    with st.form("demo_login_form"):
        demo_username = st.text_input("Username", value=role_info['username'], help="Copy from credentials above")
        demo_password = st.text_input("Password", type="password", help="Copy from credentials above")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            demo_login_button = st.form_submit_button("🎯 Login to Demo", use_container_width=True)
        
        if demo_login_button:
            if demo_username and demo_password:
                with st.spinner(f"🔐 Authenticating {demo_username}..."):
                    # Authenticate through the normal login system
                    user_info = st.session_state.auth_system.authenticate(demo_username, demo_password)
                    
                if user_info:
                    st.session_state.user_info = user_info
                    st.session_state.session_token = user_info["session_token"]
                    st.session_state.is_demo_mode = True
                    st.success(f"🎉 Welcome {user_info['username']} ({user_info['role']})!")
                    st.rerun()
                else:
                    st.error("❌ Invalid demo credentials. Please copy the exact username and password from above.")
            else:
                st.warning("⚠️ Please enter both username and password.")
    
    # Info about demo mode
    st.markdown("---")
    st.markdown("### ℹ️ About Demo Accounts")
    st.markdown("""
    - **Password authentication** required for all roles
    - **Secure demo accounts** with different permission levels
    - **Full functionality** with sample data
    - **Safe environment** for testing
    - **Query logging enabled** for demo accounts
    
    ⚠️ **Security:** All demo accounts require password authentication - no bypass allowed!
    
    💡 **Tip:** Copy the credentials exactly as shown above, then use the Login tab for regular accounts.
    """)

def show_login_form():
    """Login form"""
    st.markdown("### Sign In to Your Account")
    
    with st.form("login_form"):
        username = st.text_input("Username or Email", placeholder="Enter your username or email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            login_button = st.form_submit_button("🚀 Sign In", use_container_width=True)
        
        if login_button:
            if username and password:
                with st.spinner("Authenticating..."):
                    user_info = st.session_state.auth_system.authenticate(username, password)
                    
                if user_info:
                    st.session_state.user_info = user_info
                    st.session_state.session_token = user_info["session_token"]
                    st.success(f"Welcome back, {user_info['username']}! 🎉")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Please try again.")
            else:
                st.warning("⚠️ Please enter both username and password.")
    
    # Default admin credentials info
    with st.expander("ℹ️ Default Admin Access"):
        st.info("""
        **Default Admin Credentials:**
        - Username: `admin`
        - Password: `admin123`
        
        ⚠️ **Important:** Change the default password after first login!
        """)

def show_registration_form():
    """Registration form"""
    st.markdown("### Create New Account")
    
    with st.form("register_form"):
        username = st.text_input("Username", placeholder="Choose a unique username")
        email = st.text_input("Email", placeholder="Enter your email address")
        password = st.text_input("Password", type="password", placeholder="Create a strong password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        
        # Role selection (admin only can assign roles other than guest)
        if get_current_user() and require_permission(Permission.MANAGE_USERS):
            role = st.selectbox("Role", [UserRole.GUEST, UserRole.VIEWER, UserRole.ANALYST, UserRole.ADMIN])
        else:
            role = UserRole.GUEST
            st.info("New accounts are created with Guest role. Contact admin for role upgrade.")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            register_button = st.form_submit_button("📝 Create Account", use_container_width=True)
        
        if register_button:
            if username and email and password and confirm_password:
                if password != confirm_password:
                    st.error("❌ Passwords do not match.")
                elif len(password) < 6:
                    st.error("❌ Password must be at least 6 characters long.")
                else:
                    with st.spinner("Creating account..."):
                        success = st.session_state.auth_system.create_user(username, email, password, role)
                    
                    if success:
                        st.success("✅ Account created successfully! Please login.")
                    else:
                        st.error("❌ Username or email already exists.")
            else:
                st.warning("⚠️ Please fill in all fields.")

def show_user_profile():
    """Display user profile and settings"""
    user = get_current_user()
    if not user:
        return
    
    st.markdown("### 👤 User Profile")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # User info card
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea, #764ba2); 
                    color: white; padding: 1.5rem; border-radius: 10px; text-align: center;">
            <h3>👤 {user['username']}</h3>
            <p><strong>Role:</strong> {user['role'].title()}</p>
            <p><strong>Email:</strong> {user['email']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True, key="profile_logout"):
            st.session_state.auth_system.logout(st.session_state.session_token)
            st.session_state.user_info = None
            st.session_state.session_token = None
            st.success("👋 Logged out successfully!")
            st.rerun()
    
    with col2:
        # Permissions
        st.markdown("### 🔒 Your Permissions")
        permissions = user.get('permissions', [])
        
        if permissions:
            for permission in permissions:
                permission_label = permission.replace('_', ' ').title()
                st.markdown(f"✅ {permission_label}")
        else:
            st.info("No specific permissions assigned.")
        
        # Query history
        if require_permission(Permission.VIEW_QUERY_HISTORY):
            st.markdown("### 📊 Recent Query History")
            history = st.session_state.auth_system.get_user_query_history(user['user_id'], 10)
            
            if history:
                history_df = pd.DataFrame(history)
                history_df['created_at'] = pd.to_datetime(history_df['created_at'])
                history_df = history_df.sort_values('created_at', ascending=False)
                
                for idx, row in history_df.head(5).iterrows():
                    with st.expander(f"🔍 {row['natural_query'][:50]}... - {row['created_at'].strftime('%Y-%m-%d %H:%M')}"):
                        st.code(row['generated_sql'], language='sql')
                        if row['status'] == 'success':
                            st.success(f"✅ Success - {row['result_count']} rows returned")
                        else:
                            st.error(f"❌ Error: {row['error_message']}")
            else:
                st.info("No query history found.")

def show_admin_panel():
    """Display admin panel for user management"""
    user = get_current_user()
    if not user or not require_permission(Permission.MANAGE_USERS):
        st.error("🚫 Access denied. Admin privileges required.")
        return
    
    st.markdown("### 👑 Admin Panel - User Management")
    
    # Get all users
    users = st.session_state.auth_system.get_all_users()
    
    if users:
        users_df = pd.DataFrame(users)
        users_df['created_at'] = pd.to_datetime(users_df['created_at'])
        users_df['last_login'] = pd.to_datetime(users_df['last_login'])
        
        # User statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("👥 Total Users", len(users))
        with col2:
            active_users = sum(1 for u in users if u['is_active'])
            st.metric("✅ Active Users", active_users)
        with col3:
            admin_count = sum(1 for u in users if u['role'] == UserRole.ADMIN)
            st.metric("👑 Admins", admin_count)
        with col4:
            recent_logins = sum(1 for u in users if u['last_login'] and 
                              (datetime.now() - pd.to_datetime(u['last_login'])).days <= 7)
            st.metric("🔄 Recent Logins", recent_logins)
        
        st.markdown("---")
        
        # User management table
        st.markdown("#### 📋 User Management")
        
        for idx, user_data in enumerate(users):
            with st.expander(f"👤 {user_data['username']} ({user_data['role']})"):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**Email:** {user_data['email']}")
                    st.write(f"**Created:** {user_data['created_at']}")
                    st.write(f"**Last Login:** {user_data['last_login'] or 'Never'}")
                    st.write(f"**Status:** {'🟢 Active' if user_data['is_active'] else '🔴 Inactive'}")
                
                with col2:
                    # Role change
                    new_role = st.selectbox(
                        "Role", 
                        [UserRole.GUEST, UserRole.VIEWER, UserRole.ANALYST, UserRole.ADMIN],
                        index=[UserRole.GUEST, UserRole.VIEWER, UserRole.ANALYST, UserRole.ADMIN].index(user_data['role']),
                        key=f"role_{user_data['id']}"
                    )
                    
                    if st.button("💾 Update Role", key=f"update_{user_data['id']}"):
                        if st.session_state.auth_system.update_user_role(user_data['id'], new_role):
                            st.success("✅ Role updated!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to update role")
                
                with col3:
                    # Account actions
                    if user_data['is_active']:
                        if st.button("🚫 Deactivate", key=f"deactivate_{user_data['id']}"):
                            if st.session_state.auth_system.deactivate_user(user_data['id']):
                                st.success("✅ User deactivated!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to deactivate user")
                    
                    # Show permissions
                    permissions = ROLE_PERMISSIONS.get(user_data['role'], [])
                    st.write(f"**Permissions:** {len(permissions)}")
                    for perm in permissions[:3]:  # Show first 3
                        st.write(f"• {perm.replace('_', ' ').title()}")
                    if len(permissions) > 3:
                        st.write(f"• ... and {len(permissions) - 3} more")
    else:
        st.info("No users found.")

def show_role_info():
    """Display role information and permissions"""
    st.markdown("### 🎭 Role-Based Access Control")
    
    st.markdown("""
    Our application uses a comprehensive role-based access control system to ensure security and proper data governance.
    """)
    
    # Role descriptions
    role_descriptions = {
        UserRole.ADMIN: {
            "icon": "👑",
            "description": "Full system access with user management capabilities",
            "color": "#dc3545"
        },
        UserRole.ANALYST: {
            "icon": "📊", 
            "description": "Advanced data analysis with write permissions",
            "color": "#28a745"
        },
        UserRole.VIEWER: {
            "icon": "👁️",
            "description": "Read-only access with basic analytics",
            "color": "#17a2b8"
        },
        UserRole.GUEST: {
            "icon": "👤",
            "description": "Limited read-only access for basic queries",
            "color": "#6c757d"
        }
    }
    
    for role, info in role_descriptions.items():
        with st.expander(f"{info['icon']} {role.title()} Role"):
            st.markdown(f"**Description:** {info['description']}")
            
            permissions = ROLE_PERMISSIONS.get(role, [])
            st.markdown("**Permissions:**")
            
            for permission in permissions:
                permission_label = permission.replace('_', ' ').title()
                st.markdown(f"✅ {permission_label}")
            
            if not permissions:
                st.markdown("❌ No specific permissions")

def create_auth_sidebar():
    """Create authentication-aware sidebar"""
    user = get_current_user()
    
    if user:
        # Demo mode indicator
        demo_badge = ""
        if st.session_state.get('is_demo_mode', False):
            demo_badge = '<span style="background: #ff6b6b; color: white; padding: 0.2rem 0.5rem; border-radius: 10px; font-size: 0.7rem; margin-left: 0.5rem;">DEMO</span>'
        
        # User info in sidebar
        st.sidebar.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea, #764ba2); 
                    color: white; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
            <h4>👤 {user['username']}{demo_badge}</h4>
            <p style="margin: 0;"><strong>Role:</strong> {user['role'].title()}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Demo mode controls
        if st.session_state.get('is_demo_mode', False):
            st.sidebar.markdown("### 🎯 Demo Controls")
            
            if st.sidebar.button("🔄 Switch Role", use_container_width=True, key="sidebar_switch_role"):
                st.session_state.is_demo_mode = False
                st.session_state.user_info = None
                st.session_state.session_token = None
                st.rerun()
            
            st.sidebar.markdown("---")
        
        # Quick actions
        st.sidebar.markdown("### ⚡ Quick Actions")
        
        if st.sidebar.button("👤 Profile", use_container_width=True, key="sidebar_profile"):
            st.session_state.show_profile = True
        
        if require_permission(Permission.MANAGE_USERS):
            if st.sidebar.button("👑 Admin Panel", use_container_width=True, key="sidebar_admin"):
                st.session_state.show_admin = True
        
        if st.sidebar.button("🎭 Role Info", use_container_width=True, key="sidebar_role_info"):
            st.session_state.show_roles = True
        
        st.sidebar.markdown("---")
        
        # Logout/Exit button
        logout_text = "🚪 Exit Demo" if st.session_state.get('is_demo_mode', False) else "🚪 Logout"
        if st.sidebar.button(logout_text, use_container_width=True, key="sidebar_logout"):
            if st.session_state.get('is_demo_mode', False):
                st.session_state.is_demo_mode = False
            else:
                st.session_state.auth_system.logout(st.session_state.session_token)
            
            st.session_state.user_info = None
            st.session_state.session_token = None
            st.rerun()
    
    else:
        st.sidebar.error("🔒 Please login to access the application")

def permission_required(permission: str):
    """Decorator function to check permissions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not require_permission(permission):
                st.error(f"🚫 Access denied. Required permission: {permission.replace('_', ' ').title()}")
                return None
            return func(*args, **kwargs)
        return wrapper
    return decorator
