#!/usr/bin/env python3
import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import os
import google.generativeai as genai
from dotenv import load_dotenv
import time

# Import authentication system
from auth_system import (
    AuthSystem, UserRole, Permission, 
    init_auth_session, require_login, require_permission, get_current_user
)
from auth_ui import (
    show_login_page, show_user_profile, show_admin_panel, show_role_info,
    create_auth_sidebar, permission_required
)

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="🤖 Text-to-SQL GenAI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with Enhanced Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Enhanced Header */
    .main-header {
        font-size: 3.5rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
        animation: fadeInUp 1s ease-out;
        text-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    /* Enhanced Sidebar */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 15px;
        padding: 1rem;
        animation: slideInLeft 0.8s ease-out;
    }
    
    /* Modern Cards */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(135deg, #667eea, #764ba2);
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
        animation: pulse 1s infinite;
    }
    
    /* Enhanced Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border: none;
        border-radius: 12px;
        color: white;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        font-family: 'Inter', sans-serif;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
        background: linear-gradient(135deg, #5a6fd8, #6a5acd);
    }
    
    .stButton > button:active {
        transform: translateY(0px);
    }
    
    /* Glass Morphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.25);
        border-radius: 20px;
        padding: 1.5rem;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }
    
    /* Enhanced Database Stats */
    .database-stat {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .database-stat::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        transform: rotate(45deg);
        transition: all 0.6s;
    }
    
    .database-stat:hover::before {
        animation: shine 0.6s ease;
    }
    
    @keyframes shine {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    /* Enhanced Agent Cards */
    .agent-planner {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 0.8rem 0;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
        position: relative;
    }
    
    .agent-validator {
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 0.8rem 0;
        box-shadow: 0 6px 20px rgba(40, 167, 69, 0.4);
        transition: all 0.3s ease;
        position: relative;
    }
    
    .agent-optimizer {
        background: linear-gradient(135deg, #ffc107, #fd7e14);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 0.8rem 0;
        box-shadow: 0 6px 20px rgba(255, 193, 7, 0.4);
        transition: all 0.3s ease;
        position: relative;
    }
    
    .agent-planner:hover, .agent-validator:hover, .agent-optimizer:hover {
        transform: translateY(-3px) scale(1.02);
    }
    
    /* Enhanced Form Elements */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.9);
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.9);
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Enhanced Selectbox */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.9);
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #667eea;
    }
    
    /* Enhanced Metrics */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 15px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    /* Enhanced Code Blocks */
    .stCodeBlock {
        background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
        border-radius: 12px;
        border: 1px solid #404040;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Enhanced Expanders */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
        transform: translateY(-1px);
    }
    
    /* Enhanced Dataframes */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a6fd8, #6a5acd);
    }
    
    /* Status Indicators */
    .status-success {
        background: linear-gradient(135deg, #d4edda, #c3e6cb);
        color: #155724;
        padding: 1rem;
        border-radius: 12px;
        border-left: 4px solid #28a745;
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.2);
    }
    
    .status-warning {
        background: linear-gradient(135deg, #fff3cd, #ffeaa7);
        color: #856404;
        padding: 1rem;
        border-radius: 12px;
        border-left: 4px solid #ffc107;
        box-shadow: 0 4px 15px rgba(255, 193, 7, 0.2);
    }
    
    .status-error {
        background: linear-gradient(135deg, #f8d7da, #f5c6cb);
        color: #721c24;
        padding: 1rem;
        border-radius: 12px;
        border-left: 4px solid #dc3545;
        box-shadow: 0 4px 15px rgba(220, 53, 69, 0.2);
    }
    
    /* Loading Animation */
    .loading-spinner {
        border: 3px solid #f3f3f3;
        border-top: 3px solid #667eea;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        animation: spin 1s linear infinite;
        margin: 0 auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Confidence Indicators */
    .confidence-high { 
        color: #28a745; 
        font-weight: 600;
        text-shadow: 0 2px 4px rgba(40, 167, 69, 0.2);
    }
    .confidence-medium { 
        color: #ffc107; 
        font-weight: 600;
        text-shadow: 0 2px 4px rgba(255, 193, 7, 0.2);
    }
    .confidence-low { 
        color: #dc3545; 
        font-weight: 600;
        text-shadow: 0 2px 4px rgba(220, 53, 69, 0.2);
    }
    
    /* Reasoning Section */
    .reasoning-section {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .reasoning-section:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    /* Welcome Message */
    .welcome-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    /* Footer Enhancement */
    .footer-tech {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-top: 3rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Check database exists
def check_database():
    db_path = "database/sample.db"
    if not os.path.exists(db_path):
        st.error(f"❌ Database not found at {db_path}")
        st.info("Please run: `python scripts/create_sample_db.py` to create the database")
        st.stop()
    return db_path

# Get database schema
def get_schema():
    db_path = check_database()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    schema = {}
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            schema[table] = {
                'columns': [(col[1], col[2]) for col in columns],
                'primary_keys': [col[1] for col in columns if col[5] == 1]
            }
    except Exception as e:
        st.error(f"Error reading schema: {e}")
    finally:
        conn.close()
    
    return schema

# Configure Gemini
def setup_gemini():
    # Try to get API key from environment variables or Streamlit secrets
    api_key = os.getenv('GEMINI_API_KEY')
    
    # If not found in env vars, try Streamlit secrets
    if not api_key:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
        except (KeyError, FileNotFoundError):
            pass
    
    if not api_key:
        st.error("🚨 GEMINI_API_KEY not found!")
        st.info("For local development: Add your API key to .env file: `GEMINI_API_KEY=your_key_here`")
        st.info("For Streamlit Cloud: Add GEMINI_API_KEY to your app's Secrets in the Streamlit dashboard")
        return None
    
    try:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-2.5-flash')
    except Exception as e:
        st.error(f"Gemini setup error: {e}")
        return None

# Chain-of-Thought SQL generation with AI reasoning
@permission_required(Permission.READ_DATA)
def generate_sql_with_reasoning(user_query, schema):
    # Store the natural query for logging
    st.session_state.last_natural_query = user_query
    
    model = setup_gemini()
    if not model:
        return None, None
    
    user = get_current_user()
    
    # Get role-based AI persona
    def get_ai_persona(role):
        if role == UserRole.GUEST:
            return "helpful SQL assistant who explains queries clearly for beginners"
        elif role == UserRole.VIEWER:
            return "data exploration expert who creates insightful analytical queries"
        elif role == UserRole.ANALYST:
            return "advanced data analyst who builds sophisticated business intelligence queries"
        else:  # ADMIN
            return "database expert with full technical capabilities and optimization skills"
    
    # Get role-based example
    def get_example(role):
        if role == UserRole.GUEST:
            return """
Example: "Show me 5 customers"
UNDERSTANDING: User wants a simple list of customers
TABLES: customers table
LOGIC: Select basic customer info, limit to 5 rows for readability
CONFIDENCE: 9/10 - Simple query
SQL: SELECT customer_id, first_name, last_name FROM customers LIMIT 5;
"""
        elif role == UserRole.VIEWER:
            return """
Example: "Top customers by orders"
UNDERSTANDING: User wants to identify most active customers
TABLES: customers, orders (need to join)
LOGIC: Join customers with orders, count orders per customer, sort by count descending
CONFIDENCE: 8/10 - Standard analytical query
SQL: SELECT c.first_name, c.last_name, COUNT(o.order_id) as order_count 
     FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id 
     GROUP BY c.customer_id ORDER BY order_count DESC LIMIT 10;
"""
        else:  # ANALYST or ADMIN
            return """
Example: "Customer lifetime value analysis"
UNDERSTANDING: User wants comprehensive customer value metrics
TABLES: customers, orders (join required)
LOGIC: Calculate total spending, order frequency, average order value per customer
CONFIDENCE: 9/10 - Complex analytical query
SQL: SELECT c.customer_id, c.first_name, c.last_name,
     COUNT(o.order_id) as total_orders,
     SUM(o.total_amount) as lifetime_value,
     AVG(o.total_amount) as avg_order_value
     FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id
     GROUP BY c.customer_id ORDER BY lifetime_value DESC;
"""
    
    persona = get_ai_persona(user['role'])
    example = get_example(user['role'])
    
    # Create schema context
    schema_context = "Database Schema:\n"
    for table, info in schema.items():
        schema_context += f"\nTable: {table}\n"
        for col_name, col_type in info['columns']:
            pk_indicator = " (PRIMARY KEY)" if col_name in info['primary_keys'] else ""
            schema_context += f"  - {col_name}: {col_type}{pk_indicator}\n"
    
    # Role-based restrictions
    restrictions = ""
    if user['role'] == UserRole.GUEST:
        restrictions = "Only SELECT queries allowed, max 50 rows"
    elif user['role'] == UserRole.VIEWER:
        restrictions = "Only SELECT queries allowed, max 100 rows"
    elif user['role'] == UserRole.ANALYST:
        restrictions = "SELECT, INSERT, UPDATE allowed, max 500 rows"
    else:
        restrictions = "Full database access"
    
    # Chain-of-thought prompt
    prompt = f"""You are a {persona}.

{schema_context}

User Role Restrictions: {restrictions}

Here's how I think step by step:
{example}

Now analyze this query step by step:

UNDERSTANDING: [What does the user want?]
TABLES: [Which tables do I need?]
LOGIC: [My step-by-step approach]
CONFIDENCE: [Rate my confidence 1-10]
SQL: [The final query - NO COMMENTS, clean executable SQL only]

IMPORTANT: In the SQL section, provide ONLY executable SQL code without any comments or explanations.

User Query: "{user_query}"

Think through this carefully:"""
    
    try:
        response = model.generate_content(prompt)
        reasoning_text = response.text.strip()
        
        # Parse the structured response
        understanding = extract_section(reasoning_text, "UNDERSTANDING:", "TABLES:")
        tables = extract_section(reasoning_text, "TABLES:", "LOGIC:")
        logic = extract_section(reasoning_text, "LOGIC:", "CONFIDENCE:")
        confidence = extract_section(reasoning_text, "CONFIDENCE:", "SQL:")
        sql = extract_section(reasoning_text, "SQL:", None)
        
        # Clean SQL
        sql = clean_sql(sql)
        
        reasoning = {
            "understanding": understanding,
            "tables": tables,
            "logic": logic,
            "confidence": confidence,
            "raw_response": reasoning_text
        }
        
        return sql, reasoning
        
    except Exception as e:
        st.error(f"SQL generation error: {e}")
        return None, None

def extract_section(text, start_marker, end_marker):
    """Extract text between markers"""
    start_idx = text.find(start_marker)
    if start_idx == -1:
        return ""
    
    start_idx += len(start_marker)
    
    if end_marker:
        end_idx = text.find(end_marker, start_idx)
        if end_idx == -1:
            return text[start_idx:].strip()
        return text[start_idx:end_idx].strip()
    else:
        return text[start_idx:].strip()

def clean_sql(sql):
    """Clean SQL query by removing markdown, comments, and formatting properly"""
    if not sql:
        return ""
    
    import re
    
    # Remove markdown
    sql = re.sub(r'```sql\n?', '', sql)
    sql = re.sub(r'```\n?', '', sql)
    
    # Remove SQL comments (both -- and /* */ style)
    # Remove single-line comments (-- comment)
    sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
    
    # Remove multi-line comments (/* comment */)
    sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
    
    # Remove extra whitespace and newlines
    sql = ' '.join(sql.split())
    
    # Clean and format
    sql = sql.strip()
    
    # Ensure it ends with semicolon for proper execution
    if sql and not sql.endswith(';'):
        sql += ';'
    
    return sql

# AI Agents System
@permission_required(Permission.READ_DATA)
def query_planner_agent(user_query, schema):
    """Breaks complex queries into manageable steps"""
    model = setup_gemini()
    if not model:
        return None
    
    user = get_current_user()
    
    prompt = f"""You are a Query Planner Agent. Provide a brief analysis.

User Query: "{user_query}"

Respond in exactly this format:
📋 PLAN: [One sentence summary]
⚡ COMPLEXITY: [Simple/Medium/Complex]
🎯 FOCUS: [Main tables/operations needed]"""
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Planning error: {e}"

@permission_required(Permission.READ_DATA)
def validator_agent(sql, results, user_query, execution_time):
    """Validates if results make business sense"""
    try:
        model = setup_gemini()
        if not model:
            return "❌ Gemini model not available"
        
        if results is None or results.empty:
            result_summary = "No results returned"
            row_count = 0
            columns = []
        else:
            result_summary = f"{len(results)} rows returned"
            row_count = len(results)
            columns = list(results.columns)
        
        prompt = f"""You are a Validator Agent. Quick validation check.

Query: "{user_query}"
Results: {result_summary} in {execution_time:.2f}s

Respond in exactly this format:
✅ STATUS: [GOOD/NEEDS_REVIEW/ERROR]
📊 ACCURACY: [Results look correct/suspicious]
💡 NOTE: [Brief observation if any]"""
        
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        return f"❌ Validation error: {e}"

@permission_required(Permission.READ_DATA)
def optimizer_agent(sql, execution_time, row_count):
    """Suggests query performance improvements"""
    try:
        model = setup_gemini()
        if not model:
            return "❌ Gemini model not available"
        
        prompt = f"""You are an Optimizer Agent. Quick performance tips.

Execution: {execution_time:.2f}s, {row_count} rows

Respond in exactly this format:
⚡ PERFORMANCE: [Fast/Good/Slow]
🔧 TIP: [One quick optimization suggestion]
📈 IMPACT: [Low/Medium/High improvement potential]"""
        
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        return f"❌ Optimization error: {e}"

def display_reasoning(reasoning):
    """Display AI reasoning in an attractive format"""
    if not reasoning:
        return
        
    with st.expander("🧠 See How AI Thought Through This", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            if reasoning.get("understanding"):
                st.markdown("**💭 Understanding**")
                st.info(reasoning['understanding'])
            
            if reasoning.get("tables"):
                st.markdown("**📋 Tables Needed**")
                st.success(reasoning['tables'])
        
        with col2:
            if reasoning.get("logic"):
                st.markdown("**⚙️ My Approach**")
                st.warning(reasoning['logic'])
            
            if reasoning.get("confidence"):
                st.markdown("**🎯 AI Confidence**")
                confidence_text = reasoning['confidence']
                
                # Extract confidence score
                import re
                confidence_match = re.search(r'(\d+)', confidence_text)
                if confidence_match:
                    score = int(confidence_match.group(1))
                    if score >= 8:
                        st.success(f"High confidence: {confidence_text}")
                    elif score >= 6:
                        st.warning(f"Medium confidence: {confidence_text}")
                    else:
                        st.error(f"Low confidence: {confidence_text}")
                else:
                    st.info(confidence_text)

def display_agents_analysis(agents_data):
    """Display all AI agents analysis in compact format"""
    if not agents_data:
        return
    
    # Debug: Show which agents have data
    available_agents = list(agents_data.keys())
    st.caption(f"Available agents: {', '.join(available_agents)}")
        
    with st.expander("🤖 AI Agents Analysis", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        # Query Planner
        if agents_data.get('planning'):
            with col1:
                st.markdown("**📋 Planner**")
                st.info(agents_data['planning'])
        
        # Validator
        if agents_data.get('validation'):
            with col2:
                st.markdown("**✅ Validator**")
                validation_text = agents_data['validation']
                
                # Color code based on validation results
                if "GOOD" in validation_text or "correct" in validation_text.lower():
                    st.success(validation_text)
                elif "NEEDS_REVIEW" in validation_text or "suspicious" in validation_text.lower():
                    st.warning(validation_text)
                else:
                    st.error(validation_text)
        
        # Optimizer
        if agents_data.get('optimization'):
            with col3:
                st.markdown("**⚡ Optimizer**")
                st.warning(agents_data['optimization'])

# Main application

# Generate SQL with authentication (legacy function for compatibility)
@permission_required(Permission.READ_DATA)
def generate_sql(user_query, schema):
    sql, _ = generate_sql_with_reasoning(user_query, schema)
    return sql

# Execute SQL with security and logging
@permission_required(Permission.READ_DATA)
def execute_sql(sql):
    db_path = check_database()
    start_time = time.time()
    
    try:
        # Basic SQL validation
        sql = sql.strip()
        if not sql:
            st.error("Empty SQL query")
            return None
        
        # Check if it starts with a valid SQL keyword
        valid_starts = ['SELECT', 'WITH', 'EXPLAIN']
        if not any(sql.upper().startswith(keyword) for keyword in valid_starts):
            st.error(f"Invalid SQL query. Must start with: {', '.join(valid_starts)}")
            return None
        
        # Additional security check for role-based restrictions
        user = get_current_user()
        if user['role'] == UserRole.GUEST:
            # Guests can only do simple SELECT queries
            if 'UPDATE' in sql.upper() or 'DELETE' in sql.upper() or 'INSERT' in sql.upper() or 'DROP' in sql.upper():
                st.error("🚫 Guest users can only perform SELECT queries")
                return None
        
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(sql, conn)
        conn.close()
        
        execution_time = time.time() - start_time
        st.session_state.execution_time = execution_time
        
        # Log successful query
        if user:
            st.session_state.auth_system.log_query(
                user['user_id'], 
                st.session_state.get('last_natural_query', ''),
                sql,
                execution_time,
                len(df),
                'success'
            )
        
        # Run AI Agents if enabled
        if st.session_state.get('enable_agents', True):
            run_ai_agents_after_execution(sql, df, execution_time)
        
        return df
        
    except Exception as e:
        execution_time = time.time() - start_time
        st.session_state.execution_time = execution_time
        
        # Log failed query
        user = get_current_user()
        if user:
            st.session_state.auth_system.log_query(
                user['user_id'],
                st.session_state.get('last_natural_query', ''),
                sql,
                execution_time,
                0,
                'error',
                str(e)
            )
        
        st.error(f"SQL execution error: {e}")
        st.code(sql, language='sql')  # Show the problematic SQL
        return None

def run_ai_agents_after_execution(sql, results, execution_time):
    """Run AI agents after query execution"""
    user_query = st.session_state.get('last_natural_query', '')
    row_count = len(results) if results is not None and not results.empty else 0
    
    with st.spinner("🤖 AI Agents are analyzing..."):
        # Run Validator Agent
        validation = validator_agent(sql, results, user_query, execution_time)
        
        # Run Optimizer Agent  
        optimization = optimizer_agent(sql, execution_time, row_count)
        
        # Update agent results (preserve existing data like planning)
        if 'agents_data' not in st.session_state:
            st.session_state.agents_data = {}
        
        # Only update if the agents returned valid results
        if validation:
            st.session_state.agents_data['validation'] = validation
        if optimization:
            st.session_state.agents_data['optimization'] = optimization

# Initialize authentication
init_auth_session()

# Check if user is logged in
if not require_login():
    show_login_page()
    st.stop()

# Create authentication sidebar
create_auth_sidebar()

# Main app with authentication
# Simplified Main Header
st.markdown('''
<div style="text-align: center; margin: 2rem 0;">
    <h1 style="font-size: 3rem; font-weight: 700; color: #667eea; margin-bottom: 0.5rem;">
        🤖 Text-to-SQL GenAI
    </h1>
    <p style="font-size: 1.1rem; color: #8b949e; margin: 0;">
        Convert natural language to SQL queries with AI
    </p>
</div>
''', unsafe_allow_html=True)

# Simplified User Welcome
user = get_current_user()
if user:
    role_emoji = {"guest": "👋", "viewer": "👀", "analyst": "📊", "admin": "⚡"}.get(user['role'].lower(), "👤")
    
    if st.session_state.get('is_demo_mode', False):
        st.info(f"{role_emoji} **Demo Mode** - {user['role'].title()} Access Level")
    else:
        st.success(f"{role_emoji} Welcome **{user['username']}**! ({user['role'].title()})") 

# Show different panels based on session state
if st.session_state.get('show_profile', False):
    show_user_profile()
    if st.button("🔙 Back to Main App"):
        st.session_state.show_profile = False
        st.rerun()
    st.stop()

if st.session_state.get('show_admin', False):
    show_admin_panel()
    if st.button("🔙 Back to Main App"):
        st.session_state.show_admin = False
        st.rerun()
    st.stop()

if st.session_state.get('show_roles', False):
    show_role_info()
    if st.button("🔙 Back to Main App"):
        st.session_state.show_roles = False
        st.rerun()
    st.stop()

# Initialize session state
if 'generated_sql' not in st.session_state:
    st.session_state.generated_sql = ""
if 'results' not in st.session_state:
    st.session_state.results = None
if 'reasoning' not in st.session_state:
    st.session_state.reasoning = None
if 'agents_data' not in st.session_state:
    st.session_state.agents_data = {}
if 'execution_time' not in st.session_state:
    st.session_state.execution_time = 0
if 'selected_query' not in st.session_state:
    st.session_state.selected_query = ""
if 'force_query_update' not in st.session_state:
    st.session_state.force_query_update = False

# Simplified AI Settings
with st.expander("🧠 AI Configuration", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        show_reasoning = st.checkbox("💭 Show AI reasoning", value=True)
        st.session_state.show_reasoning = show_reasoning
        
    with col2:
        enable_agents = st.checkbox("🤖 Enable AI Agents", value=True)
        st.session_state.enable_agents = enable_agents

# Simplified Sidebar
with st.sidebar:
    st.markdown("### 📝 Sample Queries")
    
    samples = [
        "Show top 10 customers by total orders",
        "What are the most popular product categories?", 
        "List all customers from USA with their email",
        "Show total revenue by month",
        "Calculate total profit from all sales",
        "Which products have the highest profit margins?",
        "Top 5 highest rated products",
        "Show profit analysis by product category",
        "Payment method distribution across orders",
        "Customers who spent more than $1000",
        "Most recent 20 orders with customer names"
    ]
    
    selected = st.selectbox(
        "Choose a sample:",
        ["Select a sample query..."] + samples,
        key="sample_query_selector"
    )
    
    # Store selected query in session state
    if selected and not selected.startswith("Select"):
        st.session_state.selected_query = selected
    else:
        st.session_state.selected_query = ""
    
    # Quick copy button
    if selected and not selected.startswith("Select"):
        if st.button("📋 Use This Query", use_container_width=True, type="primary"):
            st.session_state.selected_query = selected
            st.session_state.force_query_update = True
            st.success("✅ Query copied!")
    
    # Clear button
    if st.button("🔄 Clear All", use_container_width=True):
        st.session_state.selected_query = ""
        st.session_state.generated_sql = ""
        st.session_state.results = None
        st.session_state.reasoning = None
        st.session_state.agents_data = {}
        st.session_state.force_query_update = True
        st.rerun()
    
    st.markdown("---")
    
    # Database info
    st.markdown("### 📊 Database")
    schema = get_schema()
    st.metric("Tables", len(schema))
    st.caption("E-commerce database with 1,693+ records")

# Main interface
col1, col2 = st.columns([1, 1])

with col1:
    # Simplified Query Interface
    st.subheader("💬 Ask Your Question")
    st.caption("Type your question in plain English")
    
    # Handle sample selection from sidebar
    query_text = ""
    if 'selected_query' in st.session_state and st.session_state.selected_query:
        query_text = st.session_state.selected_query
    
    # Dynamic key to force refresh when needed
    text_area_key = "query_input"
    if st.session_state.get('force_query_update', False):
        text_area_key = f"query_input_{time.time()}"
        st.session_state.force_query_update = False
    
    user_query = st.text_area(
        "Query Input",  # Proper label for accessibility
        value=query_text,
        height=120,
        placeholder="Example: 'Show me the top 5 customers by revenue' or 'What products are trending?'",
        help="Ask anything about the database in plain English",
        key=text_area_key,
        label_visibility="hidden"  # Hide the label since we have styled header
    )
    
    # Simplified buttons
    col_gen, col_clear = st.columns([3, 1])
    with col_gen:
        generate_button = st.button("🧠 Generate SQL", type="primary", use_container_width=True)
    with col_clear:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.generated_sql = ""
            st.session_state.results = None
            st.session_state.reasoning = None
            st.session_state.agents_data = {}
            st.session_state.selected_query = ""
            st.session_state.force_query_update = True
            st.rerun()
    
    if generate_button and user_query:
        with st.spinner("🤖 AI is thinking step by step..."):
            # Use Chain-of-Thought with optional agents
            
            # Run Query Planner Agent first if enabled
            if st.session_state.get('enable_agents', True):
                # Ensure agents_data exists
                if 'agents_data' not in st.session_state:
                    st.session_state.agents_data = {}
                
                planning = query_planner_agent(user_query, schema)
                st.session_state.agents_data['planning'] = planning
            
            # Generate SQL with reasoning
            sql, reasoning = generate_sql_with_reasoning(user_query, schema)
            if sql:
                st.session_state.generated_sql = sql
                st.session_state.reasoning = reasoning
                st.success("✅ SQL generated with AI reasoning!")
                
                # Show reasoning if enabled
                if st.session_state.get('show_reasoning', True):
                    display_reasoning(reasoning)
                
                # Show agents analysis if enabled and planning was done
                if st.session_state.get('enable_agents', True) and st.session_state.agents_data.get('planning'):
                    display_agents_analysis(st.session_state.agents_data)

with col2:
    st.subheader("🔧 Generated SQL")
    
    if st.session_state.generated_sql:
        st.code(st.session_state.generated_sql, language='sql')
        
        if st.button("▶️ Execute Query", use_container_width=True):
            with st.spinner("🔄 Executing..."):
                results = execute_sql(st.session_state.generated_sql)
                st.session_state.results = results
                
                # Show agents analysis after execution if enabled
                if st.session_state.get('enable_agents', True) and st.session_state.agents_data:
                    display_agents_analysis(st.session_state.agents_data)

# Simplified Results Section
if st.session_state.results is not None:
    st.markdown("---")
    st.subheader("📊 Query Results")
    
    df = st.session_state.results
    
    if not df.empty:
        # Simple metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📄 Rows", len(df))
        with col2:
            st.metric("📊 Columns", len(df.columns))
        with col3:
            st.metric("💾 Size", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
        with col4:
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Download CSV",
                csv,
                "query_results.csv",
                "text/csv",
                use_container_width=True
            )
        
        # Simple data display
        st.dataframe(df, use_container_width=True, height=400)
        
        # Enhanced auto-charts
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0 and len(df) <= 50:
            cat_cols = df.select_dtypes(include=['object']).columns
            if len(cat_cols) > 0:
                st.markdown("#### 📈 Data Visualization")
                
                chart_col1, chart_col2 = st.columns(2)
                with chart_col1:
                    # Bar chart
                    fig_bar = px.bar(
                        df.head(20), 
                        x=cat_cols[0], 
                        y=numeric_cols[0],
                        title=f"{numeric_cols[0]} by {cat_cols[0]}",
                        color=numeric_cols[0],
                        color_continuous_scale="viridis"
                    )
                    fig_bar.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                with chart_col2:
                    # Pie chart if suitable
                    if len(df) <= 10:
                        fig_pie = px.pie(
                            df, 
                            names=cat_cols[0], 
                            values=numeric_cols[0],
                            title=f"Distribution of {numeric_cols[0]}"
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)
                    else:
                        # Summary statistics
                        st.markdown("##### 📈 Summary Statistics")
                        st.dataframe(df[numeric_cols].describe(), use_container_width=True)
        
        # Success message
        st.success(f"✅ Query executed successfully! Found {len(df)} records.")
        
    else:
        st.warning("⚠️ Query executed successfully but returned no results.")
        st.info("Try modifying your query or check if the data exists in the database.")

# Simplified Footer
st.markdown("---")
with st.expander("ℹ️ About This Application", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🤖 AI Technology**
        - Google Gemini 2.5 Flash
        - Chain-of-Thought Reasoning
        - Multi-Agent System
        - Natural Language Processing
        """)
        
    with col2:
        st.markdown("""
        **📊 Database**
        - 1,693+ Records
        - 11 Interconnected Tables
        - E-commerce Domain Data
        - Real-time Visualization
        """)
    
    st.caption("� Built with Python, Streamlit, and Google Generative AI")
