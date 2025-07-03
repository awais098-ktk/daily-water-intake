"""
Database Admin Routes for Water Intake Tracker
Add these routes to your Flask app for web-based database viewing
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
import sqlite3
import os
import json
from datetime import datetime

# Create blueprint
db_admin_bp = Blueprint('db_admin', __name__, url_prefix='/admin/db')

def get_db_connection():
    """Get database connection"""
    db_path = os.path.join('instance', 'water_tracker.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@db_admin_bp.route('/')
@login_required
def index():
    """Database admin dashboard"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get table statistics
        tables = []
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        table_names = cursor.fetchall()
        
        for table in table_names:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            tables.append({'name': table_name, 'count': count})
        
        conn.close()
        
        return render_template('admin/db_dashboard.html', tables=tables)
    
    except Exception as e:
        return f"Error: {str(e)}"

@db_admin_bp.route('/table/<table_name>')
@login_required
def view_table(table_name):
    """View table data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get table schema
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        # Get table data (limit to 100 rows)
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit} OFFSET {offset}")
        rows = cursor.fetchall()
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_count = cursor.fetchone()[0]
        
        conn.close()
        
        # Convert rows to list of dicts for easier template handling
        data = []
        for row in rows:
            row_dict = {}
            for col in columns:
                col_name = col[1]
                value = row[col_name]
                
                # Format JSON fields
                if col_name in ['exercise_sessions', 'features'] and value:
                    try:
                        value = json.dumps(json.loads(value), indent=2)
                    except:
                        pass
                
                row_dict[col_name] = value
            data.append(row_dict)
        
        return render_template('admin/table_view.html', 
                             table_name=table_name,
                             columns=columns,
                             data=data,
                             total_count=total_count,
                             limit=limit,
                             offset=offset)
    
    except Exception as e:
        return f"Error: {str(e)}"

@db_admin_bp.route('/query', methods=['GET', 'POST'])
@login_required
def custom_query():
    """Execute custom SQL queries"""
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        
        if not query:
            return render_template('admin/query.html', error="Please enter a query")
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Only allow SELECT queries for safety
            if not query.upper().startswith('SELECT'):
                return render_template('admin/query.html', 
                                     error="Only SELECT queries are allowed",
                                     query=query)
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            # Get column names
            columns = [description[0] for description in cursor.description] if cursor.description else []
            
            conn.close()
            
            return render_template('admin/query.html',
                                 query=query,
                                 columns=columns,
                                 results=results,
                                 count=len(results))
        
        except Exception as e:
            return render_template('admin/query.html',
                                 error=f"Query error: {str(e)}",
                                 query=query)
    
    return render_template('admin/query.html')

@db_admin_bp.route('/api/table/<table_name>')
@login_required
def api_table_data(table_name):
    """API endpoint for table data (for AJAX)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit} OFFSET {offset}")
        rows = cursor.fetchall()
        
        # Convert to list of dicts
        data = [dict(row) for row in rows]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

# Template files would need to be created in templates/admin/
# For now, let's create simple HTML responses

@db_admin_bp.route('/simple')
@login_required
def simple_view():
    """Simple HTML view of database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Database Admin</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                table { border-collapse: collapse; width: 100%; margin: 20px 0; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .table-section { margin: 30px 0; }
                .table-title { color: #333; border-bottom: 2px solid #333; }
            </style>
        </head>
        <body>
            <h1>Water Tracker Database Admin</h1>
        """
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            html += f'<div class="table-section">'
            html += f'<h2 class="table-title">{table_name.replace("_", " ").title()}</h2>'
            
            # Get recent data (limit 5 rows)
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            rows = cursor.fetchall()
            
            if rows:
                html += '<table>'
                # Headers
                html += '<tr>'
                for col in rows[0].keys():
                    html += f'<th>{col}</th>'
                html += '</tr>'
                
                # Data
                for row in rows:
                    html += '<tr>'
                    for value in row:
                        # Truncate long values
                        str_value = str(value) if value is not None else ''
                        if len(str_value) > 50:
                            str_value = str_value[:50] + '...'
                        html += f'<td>{str_value}</td>'
                    html += '</tr>'
                html += '</table>'
            else:
                html += '<p>No data in this table.</p>'
            
            html += '</div>'
        
        html += '</body></html>'
        conn.close()
        
        return html
    
    except Exception as e:
        return f"Error: {str(e)}"
