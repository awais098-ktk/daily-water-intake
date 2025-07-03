"""
Sarcastic Chatbot Routes

This module contains Flask routes for the sarcastic chatbot interface
and API endpoints for chat functionality.
"""

from flask import Blueprint, render_template, request, jsonify, session, current_app
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
import logging
import json

from .chatbot import SarcasticChatbot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

# Initialize chatbot instance
chatbot = SarcasticChatbot()

def init_chatbot_routes(app):
    """Initialize chatbot routes with the Flask app."""
    app.register_blueprint(chatbot_bp)
    logger.info("Sarcastic chatbot routes initialized")

@chatbot_bp.route('/')
@login_required
def chatbot_interface():
    """Main chatbot interface page."""
    return render_template('chatbot/interface.html')

@chatbot_bp.route('/api/chat', methods=['POST'])
@login_required
def chat_api():
    """
    API endpoint for chatbot conversations.
    
    Expected JSON payload:
    {
        "message": "user message text"
    }
    
    Returns:
    {
        "success": true,
        "response": "chatbot response",
        "action": "action_type",
        "data": {...}
    }
    """
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Request must be JSON'
            }), 400
        
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'No message provided'
            }), 400
        
        # Get current user's water intake for today
        current_intake, daily_goal = get_user_daily_intake(current_user.id)
        
        # Process the message with the chatbot
        result = chatbot.process_user_input(user_message, current_intake, daily_goal)
        
        # Handle different actions
        response_data = {
            'success': True,
            'response': result['response'],
            'action': result['action'],
            'current_intake': current_intake,
            'daily_goal': daily_goal,
            'timestamp': datetime.now().isoformat()
        }
        
        # If user reported water intake, log it
        if result['action'] == 'log_intake' and result['extracted_intake']:
            success = log_water_intake(
                current_user.id, 
                result['extracted_intake'],
                'chatbot'
            )
            
            if success:
                # Update current intake for response
                new_intake = current_intake + result['extracted_intake']
                response_data.update({
                    'intake_logged': True,
                    'added_amount': result['extracted_intake'],
                    'new_total': new_intake,
                    'remaining': max(0, daily_goal - new_intake)
                })
            else:
                response_data.update({
                    'intake_logged': False,
                    'error': 'Failed to log water intake'
                })
        
        # Store conversation in session for context
        store_conversation(user_message, result['response'])
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in chat API: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'response': "Something went wrong. Are you sure you're not too dehydrated to use technology?"
        }), 500

@chatbot_bp.route('/api/reminder', methods=['GET'])
@login_required
def get_reminder():
    """
    API endpoint to get a sarcastic reminder message.
    
    Returns:
    {
        "success": true,
        "reminder": "sarcastic reminder message",
        "current_intake": 1500,
        "daily_goal": 2000
    }
    """
    try:
        current_intake, daily_goal = get_user_daily_intake(current_user.id)
        reminder = chatbot.generate_reminder(current_intake, daily_goal)
        
        return jsonify({
            'success': True,
            'reminder': reminder,
            'current_intake': current_intake,
            'daily_goal': daily_goal,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating reminder: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate reminder'
        }), 500

@chatbot_bp.route('/api/send_reminder', methods=['POST'])
@login_required
def send_reminder():
    """
    API endpoint to manually trigger a reminder for the current user.

    Returns:
    {
        "success": true,
        "reminder_sent": true,
        "reminder": "sarcastic reminder message"
    }
    """
    try:
        current_intake, daily_goal = get_user_daily_intake(current_user.id)
        reminder = chatbot.generate_reminder(current_intake, daily_goal)

        # Store the reminder in session for the user to see
        store_conversation("System Reminder", reminder)

        return jsonify({
            'success': True,
            'reminder_sent': True,
            'reminder': reminder,
            'current_intake': current_intake,
            'daily_goal': daily_goal,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error sending reminder: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to send reminder'
        }), 500

@chatbot_bp.route('/api/status', methods=['GET'])
@login_required
def get_status():
    """
    API endpoint to get current hydration status with sarcastic commentary.
    
    Returns:
    {
        "success": true,
        "status_message": "sarcastic status message",
        "current_intake": 1500,
        "daily_goal": 2000,
        "progress_percentage": 75
    }
    """
    try:
        current_intake, daily_goal = get_user_daily_intake(current_user.id)
        
        # Generate status message
        category = chatbot.get_intake_category(current_intake, daily_goal)
        remaining = max(0, daily_goal - current_intake)
        excess = max(0, current_intake - daily_goal)
        
        status_message = chatbot.generate_response(
            category,
            intake=current_intake,
            remaining=remaining,
            excess=excess
        )
        
        progress_percentage = (current_intake / daily_goal * 100) if daily_goal > 0 else 0
        
        return jsonify({
            'success': True,
            'status_message': status_message,
            'current_intake': current_intake,
            'daily_goal': daily_goal,
            'progress_percentage': round(progress_percentage, 1),
            'remaining': remaining,
            'category': category,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get status'
        }), 500

def get_user_daily_intake(user_id: int) -> tuple:
    """
    Get user's current daily water intake and goal.
    
    Args:
        user_id: User ID
        
    Returns:
        Tuple of (current_intake_ml, daily_goal_ml)
    """
    try:
        # Import here to avoid circular imports
        from flask import current_app
        
        # Get database models from the main app
        with current_app.app_context():
            # Get models from the main app
            import sys
            main_module = None
            for module_name, module in sys.modules.items():
                if hasattr(module, 'WaterLog') and hasattr(module, 'User') and hasattr(module, 'db'):
                    main_module = module
                    break
            
            if not main_module:
                logger.error("Could not find main app module with database models")
                return 0, 2000
            
            WaterLog = main_module.WaterLog
            User = main_module.User
            db = main_module.db
            
            # Get user's daily goal
            user = User.query.get(user_id)
            daily_goal = user.daily_goal if user else 2000
            
            # Get today's intake
            today = date.today()
            today_entries = WaterLog.query.filter(
                WaterLog.user_id == user_id,
                db.func.date(WaterLog.timestamp) == today
            ).all()
            
            current_intake = sum(entry.amount for entry in today_entries)
            
            return current_intake, daily_goal
            
    except Exception as e:
        logger.error(f"Error getting user daily intake: {e}")
        return 0, 2000

def log_water_intake(user_id: int, amount_ml: int, input_method: str = 'chatbot') -> bool:
    """
    Log water intake to the database.
    
    Args:
        user_id: User ID
        amount_ml: Amount in milliliters
        input_method: How the intake was logged
        
    Returns:
        True if successful, False otherwise
    """
    try:
        from flask import current_app
        
        with current_app.app_context():
            # Get models from the main app
            import sys
            main_module = None
            for module_name, module in sys.modules.items():
                if hasattr(module, 'WaterLog') and hasattr(module, 'db'):
                    main_module = module
                    break
            
            if not main_module:
                logger.error("Could not find main app module with database models")
                return False
            
            WaterLog = main_module.WaterLog
            db = main_module.db
            
            # Create new water log entry
            water_log = WaterLog(
                amount=amount_ml,
                user_id=user_id,
                input_method=input_method,
                timestamp=datetime.now()
            )
            
            db.session.add(water_log)
            db.session.commit()
            
            logger.info(f"Logged {amount_ml}ml for user {user_id} via {input_method}")
            return True
            
    except Exception as e:
        logger.error(f"Error logging water intake: {e}")
        import traceback
        traceback.print_exc()
        return False

def store_conversation(user_message: str, bot_response: str):
    """
    Store conversation in session for context.
    
    Args:
        user_message: User's message
        bot_response: Bot's response
    """
    try:
        if 'chatbot_history' not in session:
            session['chatbot_history'] = []
        
        # Keep only last 10 conversations
        if len(session['chatbot_history']) >= 10:
            session['chatbot_history'] = session['chatbot_history'][-9:]
        
        session['chatbot_history'].append({
            'user': user_message,
            'bot': bot_response,
            'timestamp': datetime.now().isoformat()
        })
        
        session.modified = True
        
    except Exception as e:
        logger.error(f"Error storing conversation: {e}")
