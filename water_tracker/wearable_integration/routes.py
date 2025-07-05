"""
Flask routes for wearable integration
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app, session
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta, timezone
import logging

from .fitness_apis import GoogleFitAPI, FitbitAPI, MockFitnessAPI
from .activity_calculator import ActivityHydrationCalculator
from .oauth_manager import OAuthManager

logger = logging.getLogger(__name__)

# Create blueprint
wearable_bp = Blueprint('wearable', __name__, template_folder='templates')

# Initialize OAuth manager
oauth_manager = None

def init_oauth_manager(app_config):
    """Initialize OAuth manager with app configuration"""
    global oauth_manager
    oauth_manager = OAuthManager(app_config)

def get_wearable_models():
    """Get the wearable models from the main app"""
    from flask import current_app

    # Get the database instance from the current app
    db = current_app.extensions['sqlalchemy']

    # Get all registered models from SQLAlchemy
    models = db.Model.registry._class_registry

    WearableConnection = models.get('WearableConnection')
    ActivityData = models.get('ActivityData')
    HydrationRecommendation = models.get('HydrationRecommendation')

    # If not found, they might be registered with different names
    if not WearableConnection:
        for name, model in models.items():
            if hasattr(model, '__tablename__'):
                if model.__tablename__ == 'wearable_connections':
                    WearableConnection = model
                elif model.__tablename__ == 'activity_data':
                    ActivityData = model
                elif model.__tablename__ == 'hydration_recommendations':
                    HydrationRecommendation = model

    return WearableConnection, ActivityData, HydrationRecommendation, db

@wearable_bp.route('/')
@login_required
def index():
    """Wearable integration dashboard"""
    WearableConnection, ActivityData, HydrationRecommendation, db = get_wearable_models()

    connections = WearableConnection.query.filter_by(user_id=current_user.id, is_active=True).all()

    # Get recent activity data
    recent_activity = ActivityData.query.filter_by(user_id=current_user.id)\
        .order_by(ActivityData.date.desc())\
        .limit(7)\
        .all()

    # Get latest hydration recommendation
    latest_recommendation = HydrationRecommendation.query.filter_by(user_id=current_user.id)\
        .order_by(HydrationRecommendation.date.desc())\
        .first()

    return render_template('wearable/dashboard.html',
                         connections=connections,
                         recent_activity=recent_activity,
                         latest_recommendation=latest_recommendation)

@wearable_bp.route('/connect')
@login_required
def connect():
    """Show available wearable connections"""
    from flask import current_app
    import logging

    logger = logging.getLogger(__name__)

    # Check if OAuth is configured for each platform
    google_fit_client_id = current_app.config.get('GOOGLE_FIT_CLIENT_ID')
    google_fit_client_secret = current_app.config.get('GOOGLE_FIT_CLIENT_SECRET')

    google_fit_configured = bool(google_fit_client_id and google_fit_client_secret)

    fitbit_configured = bool(
        current_app.config.get('FITBIT_CLIENT_ID') and
        current_app.config.get('FITBIT_CLIENT_SECRET')
    )

    oauth_configured = {
        'google_fit': google_fit_configured,
        'fitbit': fitbit_configured
    }

    # Debug logging
    logger.info(f"OAuth Configuration - Google Fit: {google_fit_configured}, Fitbit: {fitbit_configured}")
    logger.info(f"Google Fit Client ID: {google_fit_client_id[:20] if google_fit_client_id else 'None'}...")

    return render_template('wearable/connect.html', oauth_configured=oauth_configured)

@wearable_bp.route('/connect/<platform>')
@login_required
def connect_platform(platform):
    """Initiate connection to a specific platform"""
    if platform not in ['google_fit', 'fitbit', 'mock']:
        flash('Unsupported platform', 'error')
        return redirect(url_for('wearable.connect'))

    if platform == 'mock':
        WearableConnection, ActivityData, HydrationRecommendation, db = get_wearable_models()

        # Create a mock connection for testing
        existing_connection = WearableConnection.query.filter_by(
            user_id=current_user.id,
            platform='mock',
            is_active=True
        ).first()

        if existing_connection:
            flash('Mock connection already exists', 'info')
        else:
            mock_connection = WearableConnection(
                user_id=current_user.id,
                platform='mock',
                platform_user_id='mock_user_123',
                access_token='mock_access_token',
                is_active=True
            )
            db.session.add(mock_connection)
            db.session.commit()
            flash('Mock wearable connected successfully!', 'success')

        return redirect(url_for('wearable.index'))

    # For real platforms, initiate OAuth flow
    if not oauth_manager:
        flash('OAuth not configured. Please check API credentials.', 'error')
        return redirect(url_for('wearable.connect'))

    try:
        # Check if already connected
        WearableConnection, ActivityData, HydrationRecommendation, db = get_wearable_models()
        existing_connection = WearableConnection.query.filter_by(
            user_id=current_user.id,
            platform=platform,
            is_active=True
        ).first()

        if existing_connection:
            flash(f'{platform.title()} is already connected', 'info')
            return redirect(url_for('wearable.index'))

        # Generate OAuth authorization URL
        auth_url, state = oauth_manager.get_authorization_url(platform, current_user.id)

        # Store state in session for security
        session[f'oauth_state_{platform}'] = state

        # Redirect to OAuth provider
        return redirect(auth_url)

    except Exception as e:
        logger.error(f"Error initiating OAuth for {platform}: {e}")
        flash(f'Failed to connect to {platform.title()}. Please try again.', 'error')
        return redirect(url_for('wearable.connect'))

@wearable_bp.route('/oauth/<platform>/callback')
@login_required
def oauth_callback(platform):
    """Handle OAuth callback from fitness platforms"""
    if platform not in ['google_fit', 'fitbit']:
        flash('Invalid OAuth platform', 'error')
        return redirect(url_for('wearable.connect'))

    if not oauth_manager:
        flash('OAuth not configured', 'error')
        return redirect(url_for('wearable.connect'))

    # Get authorization code and state from callback
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')

    # Check for OAuth errors
    if error:
        logger.error(f"OAuth error for {platform}: {error}")
        flash(f'Authorization failed: {error}', 'error')
        return redirect(url_for('wearable.connect'))

    if not code or not state:
        flash('Invalid OAuth callback parameters', 'error')
        return redirect(url_for('wearable.connect'))

    # Validate state parameter
    session_state = session.get(f'oauth_state_{platform}')
    if not session_state or session_state != state:
        flash('Invalid OAuth state. Please try again.', 'error')
        return redirect(url_for('wearable.connect'))

    try:
        # Exchange code for tokens
        token_info = oauth_manager.exchange_code_for_tokens(platform, code, state)

        # Get user profile to get platform user ID
        if platform == 'google_fit':
            api = GoogleFitAPI(token_info['access_token'], token_info.get('refresh_token'))
            profile_data = api.get_user_profile()
            platform_user_id = profile_data.get('id', f"google_user_{current_user.id}")
        elif platform == 'fitbit':
            api = FitbitAPI(token_info['access_token'], token_info.get('refresh_token'))
            profile_data = api.get_user_profile()
            platform_user_id = profile_data.get('encodedId', f"fitbit_user_{current_user.id}")

        # Store connection in database
        WearableConnection, ActivityData, HydrationRecommendation, db = get_wearable_models()

        # Check if connection already exists
        existing_connection = WearableConnection.query.filter_by(
            user_id=current_user.id,
            platform=platform,
            platform_user_id=platform_user_id
        ).first()

        if existing_connection:
            # Update existing connection
            existing_connection.access_token = token_info['access_token']
            existing_connection.refresh_token = token_info.get('refresh_token')
            existing_connection.token_expires_at = token_info.get('expires_at')
            existing_connection.is_active = True
            existing_connection.connected_at = datetime.now(timezone.utc)
        else:
            # Create new connection
            new_connection = WearableConnection(
                user_id=current_user.id,
                platform=platform,
                platform_user_id=platform_user_id,
                access_token=token_info['access_token'],
                refresh_token=token_info.get('refresh_token'),
                token_expires_at=token_info.get('expires_at'),
                is_active=True,
                connected_at=datetime.now(timezone.utc)
            )
            db.session.add(new_connection)

        db.session.commit()

        # Clean up session state
        session.pop(f'oauth_state_{platform}', None)

        flash(f'{platform.title()} connected successfully!', 'success')
        return redirect(url_for('wearable.index'))

    except Exception as e:
        logger.error(f"Error processing OAuth callback for {platform}: {e}")
        flash(f'Failed to connect {platform.title()}. Please try again.', 'error')
        return redirect(url_for('wearable.connect'))

@wearable_bp.route('/disconnect/<int:connection_id>')
@login_required
def disconnect(connection_id):
    """Disconnect a wearable device"""
    WearableConnection, ActivityData, HydrationRecommendation, db = get_wearable_models()

    connection = WearableConnection.query.filter_by(
        id=connection_id,
        user_id=current_user.id
    ).first()

    if not connection:
        flash('Connection not found', 'error')
        return redirect(url_for('wearable.index'))

    connection.is_active = False
    db.session.commit()

    flash(f'{connection.platform.title()} disconnected successfully', 'success')
    return redirect(url_for('wearable.index'))

@wearable_bp.route('/debug')
@login_required
def debug_connections():
    """Debug wearable connections and data"""
    WearableConnection, ActivityData, HydrationRecommendation, db = get_wearable_models()

    connections = WearableConnection.query.filter_by(user_id=current_user.id, is_active=True).all()
    debug_info = []

    for connection in connections:
        info = {
            'platform': connection.platform,
            'platform_user_id': connection.platform_user_id,
            'connected_at': connection.connected_at,
            'connection_test': False,
            'data_sources': [],
            'sample_data': None,
            'error': None
        }

        try:
            # Create API instance
            if connection.platform == 'google_fit':
                from .fitness_apis import GoogleFitAPI
                api = GoogleFitAPI(connection.access_token, connection.refresh_token)
            elif connection.platform == 'fitbit':
                from .fitness_apis import FitbitAPI
                api = FitbitAPI(connection.access_token, connection.refresh_token)
            elif connection.platform == 'mock':
                from .fitness_apis import MockFitnessAPI
                api = MockFitnessAPI(connection.access_token)
            else:
                info['error'] = f'Unsupported platform: {connection.platform}'
                debug_info.append(info)
                continue

            # Test connection
            connection_result = api.test_connection()
            info['connection_test'] = connection_result

            # Get data sources (Google Fit only)
            if connection.platform == 'google_fit' and hasattr(api, 'list_data_sources'):
                data_sources = api.list_data_sources()
                info['data_sources'] = [ds.get('dataStreamId', 'Unknown') for ds in data_sources[:10]]

            # Get sample data for today
            sample_data = api.get_activity_data(datetime.now())
            info['sample_data'] = sample_data

        except Exception as e:
            info['error'] = str(e)

        debug_info.append(info)

    return render_template('wearable/debug.html', debug_info=debug_info)

@wearable_bp.route('/test_sync')
@login_required
def test_sync():
    """Test sync with detailed output"""
    WearableConnection, ActivityData, HydrationRecommendation, db = get_wearable_models()

    connections = WearableConnection.query.filter_by(user_id=current_user.id, is_active=True).all()

    if not connections:
        return jsonify({'error': 'No wearable devices connected'})

    results = []

    for connection in connections:
        result = {
            'platform': connection.platform,
            'platform_user_id': connection.platform_user_id,
            'steps': []
        }

        try:
            # Create API instance
            if connection.platform == 'google_fit':
                from .fitness_apis import GoogleFitAPI
                api = GoogleFitAPI(connection.access_token, connection.refresh_token)
            elif connection.platform == 'fitbit':
                from .fitness_apis import FitbitAPI
                api = FitbitAPI(connection.access_token, connection.refresh_token)
            elif connection.platform == 'mock':
                from .fitness_apis import MockFitnessAPI
                api = MockFitnessAPI(connection.access_token)
            else:
                result['error'] = f'Unsupported platform: {connection.platform}'
                results.append(result)
                continue

            # Test connection
            connection_test = api.test_connection()
            result['connection_test'] = connection_test

            if not connection_test:
                result['error'] = 'Connection test failed'
                results.append(result)
                continue

            # Test data for today
            today_data = api.get_activity_data(datetime.now())
            result['today_data'] = today_data

            # Test aggregate data if Google Fit
            if connection.platform == 'google_fit' and hasattr(api, 'get_aggregate_data'):
                aggregate_data = api.get_aggregate_data(datetime.now())
                result['aggregate_data'] = aggregate_data

        except Exception as e:
            result['error'] = str(e)
            import traceback
            result['traceback'] = traceback.format_exc()

        results.append(result)

    return jsonify(results)

@wearable_bp.route('/sync')
@login_required
def sync_all():
    """Sync data from all connected wearables"""
    WearableConnection, ActivityData, HydrationRecommendation, db = get_wearable_models()

    connections = WearableConnection.query.filter_by(user_id=current_user.id, is_active=True).all()

    if not connections:
        flash('No wearable devices connected', 'warning')
        return redirect(url_for('wearable.index'))

    sync_results = []
    for connection in connections:
        try:
            # Add timeout protection to prevent hanging
            result = sync_connection(connection)
            sync_results.append(result)
        except Exception as e:
            sync_results.append({
                'success': False,
                'error': f'Sync timeout or error: {str(e)}',
                'platform': connection.platform
            })

    successful_syncs = sum(1 for result in sync_results if result['success'])

    # Show detailed results
    for result in sync_results:
        platform = result.get('platform', 'Unknown')
        if result['success']:
            count = result.get('sync_count', 0)
            flash(f'{platform}: Successfully synced {count} days of data', 'success')
        else:
            error = result.get('error', 'Unknown error')
            flash(f'{platform}: {error}', 'danger')



    return redirect(url_for('wearable.index'))

@wearable_bp.route('/api/sync/<int:connection_id>')
@login_required
def api_sync_connection(connection_id):
    """API endpoint to sync a specific connection"""
    WearableConnection, ActivityData, HydrationRecommendation, db = get_wearable_models()

    connection = WearableConnection.query.filter_by(
        id=connection_id,
        user_id=current_user.id,
        is_active=True
    ).first()

    if not connection:
        return jsonify({'error': 'Connection not found'}), 404

    result = sync_connection(connection)
    return jsonify(result)

@wearable_bp.route('/api/activity-data')
@login_required
def api_activity_data():
    """API endpoint to get activity data"""
    WearableConnection, ActivityData, HydrationRecommendation, db = get_wearable_models()

    days = request.args.get('days', 7, type=int)
    end_date = date.today()
    start_date = end_date - timedelta(days=days-1)

    activity_data = ActivityData.query.filter_by(user_id=current_user.id)\
        .filter(ActivityData.date >= start_date)\
        .filter(ActivityData.date <= end_date)\
        .order_by(ActivityData.date.desc())\
        .all()

    return jsonify({
        'success': True,
        'data': [data.to_dict() for data in activity_data]
    })

@wearable_bp.route('/api/hydration-recommendation')
@login_required
def api_hydration_recommendation():
    """API endpoint to get current hydration recommendation"""
    WearableConnection, ActivityData, HydrationRecommendation, db = get_wearable_models()

    target_date = request.args.get('date')
    if target_date:
        try:
            target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
    else:
        target_date = date.today()

    # Get activity data for the date
    activity_data = ActivityData.query.filter_by(
        user_id=current_user.id,
        date=target_date
    ).first()

    if not activity_data:
        return jsonify({
            'success': False,
            'message': 'No activity data available for this date'
        })

    # Calculate hydration recommendation
    calculator = ActivityHydrationCalculator(user_weight_kg=getattr(current_user, 'weight_kg', None))
    recommendation = calculator.calculate_total_recommendation(activity_data.to_dict())

    # Get hydration tips
    tips = calculator.get_hydration_tips(activity_data.to_dict())

    return jsonify({
        'success': True,
        'recommendation': recommendation,
        'tips': tips,
        'activity_data': activity_data.to_dict()
    })

def sync_connection(connection) -> dict:
    """Sync data from a specific wearable connection"""
    try:
        print(f"🔄 Starting sync for {connection.platform} (ID: {connection.id})")

        # Get models
        WearableConnection, ActivityData, HydrationRecommendation, db = get_wearable_models()

        # Check if token needs refresh
        if connection.token_expires_at and connection.refresh_token and oauth_manager:
            # Ensure both datetimes have the same timezone for comparison
            token_expires = connection.token_expires_at
            if token_expires.tzinfo is None:
                token_expires = token_expires.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) >= token_expires:
                try:
                    # Refresh the token
                    new_token_info = oauth_manager.refresh_access_token(connection.platform, connection.refresh_token)

                    # Update connection with new token
                    connection.access_token = new_token_info['access_token']
                    if 'refresh_token' in new_token_info:
                        connection.refresh_token = new_token_info['refresh_token']
                    if 'expires_at' in new_token_info:
                        connection.token_expires_at = new_token_info['expires_at']

                    # Save updated token to database
                    db.session.commit()

                except Exception as refresh_error:
                    return {'success': False, 'error': f'Token refresh failed: {str(refresh_error)}', 'platform': connection.platform}

        # Create API instance based on platform
        if connection.platform == 'google_fit':
            api = GoogleFitAPI(connection.access_token, connection.refresh_token)
        elif connection.platform == 'fitbit':
            api = FitbitAPI(connection.access_token, connection.refresh_token)
        elif connection.platform == 'mock':
            api = MockFitnessAPI(connection.access_token)
        else:
            return {'success': False, 'error': f'Unsupported platform: {connection.platform}', 'platform': connection.platform}

        # Test connection
        connection_test = api.test_connection()

        if not connection_test:
            # If connection fails and we have a refresh token, try refreshing once more
            if connection.refresh_token and connection.platform != 'mock' and oauth_manager:
                try:
                    new_token_info = oauth_manager.refresh_access_token(connection.platform, connection.refresh_token)

                    # Update connection with new token
                    connection.access_token = new_token_info['access_token']
                    if 'refresh_token' in new_token_info:
                        connection.refresh_token = new_token_info['refresh_token']
                    if 'expires_at' in new_token_info:
                        connection.token_expires_at = new_token_info['expires_at']

                    # Save updated token and retry
                    db.session.commit()

                    # Create new API instance with refreshed token
                    if connection.platform == 'google_fit':
                        api = GoogleFitAPI(connection.access_token, connection.refresh_token)
                    elif connection.platform == 'fitbit':
                        api = FitbitAPI(connection.access_token, connection.refresh_token)

                    # Test connection again
                    connection_test = api.test_connection()

                except Exception as refresh_error:
                    pass

            if not connection_test:
                return {'success': False, 'error': 'Failed to connect to API after token refresh attempt', 'platform': connection.platform}

        # Sync last 7 days of data
        sync_count = 0
        today = date.today()

        for i in range(7):
            sync_date = today - timedelta(days=i)

            try:
                # Get activity data from API
                sync_datetime = datetime.combine(sync_date, datetime.min.time()).replace(tzinfo=timezone.utc)
                activity_data = api.get_activity_data(sync_datetime)

                if activity_data:
                    # Update or create activity record
                    existing_record = ActivityData.query.filter_by(
                        user_id=current_user.id,
                        date=sync_date
                    ).first()

                    if existing_record:
                        # Update existing record - only set valid attributes
                        for key, value in activity_data.items():
                            if hasattr(existing_record, key):
                                setattr(existing_record, key, value)
                        existing_record.updated_at = datetime.now(timezone.utc)
                    else:
                        # Create new record - only include valid fields
                        valid_fields = {}
                        for key, value in activity_data.items():
                            if hasattr(ActivityData, key):
                                valid_fields[key] = value

                        new_record = ActivityData(
                            user_id=current_user.id,
                            connection_id=connection.id,
                            date=sync_date,
                            **valid_fields
                        )
                        db.session.add(new_record)

                    sync_count += 1

            except Exception as day_error:
                # Continue with other days even if one fails
                continue

        # Update last sync time and commit all changes
        try:
            connection.last_sync = datetime.now(timezone.utc)
            db.session.commit()
        except Exception as commit_error:
            db.session.rollback()
            return {'success': False, 'error': f'Database commit failed: {str(commit_error)}', 'platform': connection.platform}

        return {
            'success': True,
            'sync_count': sync_count,
            'platform': connection.platform
        }

    except Exception as e:
        # Rollback any pending transaction
        try:
            db.session.rollback()
        except:
            pass

        return {'success': False, 'error': str(e), 'platform': getattr(connection, 'platform', 'unknown')}
