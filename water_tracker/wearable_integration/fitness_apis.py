"""
Fitness API integrations for wearable devices
"""

import requests
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class BaseFitnessAPI:
    """Base class for fitness API integrations"""
    
    def __init__(self, access_token: str, refresh_token: str = None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.base_url = ""
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    def refresh_access_token(self) -> bool:
        """Refresh the access token. Should be implemented by subclasses."""
        raise NotImplementedError
    
    def get_activity_data(self, date: datetime) -> Dict[str, Any]:
        """Get activity data for a specific date. Should be implemented by subclasses."""
        raise NotImplementedError
    
    def test_connection(self) -> bool:
        """Test if the API connection is working."""
        raise NotImplementedError

    def get_user_profile(self) -> Dict[str, Any]:
        """Get user profile information. Should be implemented by subclasses."""
        raise NotImplementedError

class GoogleFitAPI(BaseFitnessAPI):
    """Google Fit API integration"""
    
    def __init__(self, access_token: str, refresh_token: str = None):
        super().__init__(access_token, refresh_token)
        self.base_url = "https://www.googleapis.com/fitness/v1/users/me"
    
    def test_connection(self) -> bool:
        """Test Google Fit API connection"""
        try:
            # Use dataSources endpoint to test connection (this endpoint exists)
            url = f"{self.base_url}/dataSources"
            print(f"Testing Google Fit connection to: {url}")
            print(f"Access token (first 20 chars): {self.access_token[:20]}...")

            response = requests.get(url, headers=self.headers, timeout=10)
            print(f"Google Fit connection test response: {response.status_code}")

            if response.status_code != 200:
                print(f"Google Fit connection test failed with status {response.status_code}")
                print(f"Response content: {response.text[:500]}")

            return response.status_code == 200
        except Exception as e:
            print(f"Google Fit connection test failed: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return False

    def get_user_profile(self) -> Dict[str, Any]:
        """Get Google Fit user profile"""
        try:
            # Google Fit doesn't have a profile endpoint, so we'll use a simple identifier
            # based on the access token
            return {'id': f'google_user_{hash(self.access_token) % 10000}'}

        except Exception as e:
            logger.error(f"Error getting Google Fit profile: {e}")
            return {'id': f'google_user_{hash(self.access_token) % 10000}'}
    
    def get_activity_data(self, date: datetime) -> Dict[str, Any]:
        """Get activity data from Google Fit for a specific date"""
        try:
            logger.info(f"Getting Google Fit activity data for date: {date}")

            # Try aggregate API first (more reliable)
            aggregate_data = self.get_aggregate_data(date)
            if aggregate_data and aggregate_data.get('steps', 0) > 0:
                logger.info("Successfully got data from aggregate API")
                return aggregate_data

            logger.info("Aggregate API didn't return data, trying individual data sources...")

            # Convert date to milliseconds (Google Fit uses nanoseconds)
            # Ensure timezone-aware datetime
            if date.tzinfo is None:
                date = date.replace(tzinfo=timezone.utc)
            start_time = int(date.replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000)
            end_time = int(date.replace(hour=23, minute=59, second=59, microsecond=999999).timestamp() * 1000)

            logger.info(f"Time range: {start_time} to {end_time} (milliseconds)")
            
            # Data sources for different metrics - try multiple sources
            data_sources = {
                'steps': [
                    'derived:com.google.step_count.delta:com.google.android.gms:estimated_steps',
                    'derived:com.google.step_count.delta:com.google.android.gms:merge_step_deltas',
                    'raw:com.google.step_count.delta:com.google.android.gms:from_phone'
                ],
                'distance': [
                    'derived:com.google.distance.delta:com.google.android.gms:merge_distance_delta',
                    'raw:com.google.distance.delta:com.google.android.gms:from_phone'
                ],
                'calories': [
                    'derived:com.google.calories.expended:com.google.android.gms:merge_calories_expended',
                    'raw:com.google.calories.expended:com.google.android.gms:from_phone'
                ],
                'heart_rate': [
                    'derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm',
                    'raw:com.google.heart_rate.bpm:com.google.android.gms:from_phone'
                ],
                'sleep': [
                    'derived:com.google.sleep.segment:com.google.android.gms:merged',
                    'raw:com.google.sleep.segment:com.google.android.gms:from_phone'
                ]
            }
            
            activity_data = {
                'steps': 0,
                'distance_meters': 0.0,
                'calories_burned': 0,
                'active_minutes': 0,
                'heart_rate_avg': None,
                'heart_rate_max': None,
                'exercise_sessions': [],
                # Sleep data
                'sleep_duration_minutes': None,
                'sleep_efficiency': None,
                'deep_sleep_minutes': None,
                'light_sleep_minutes': None,
                'rem_sleep_minutes': None,
                'awake_minutes': None,
                'sleep_start_time': None,
                'sleep_end_time': None
            }
            
            # Get steps data - try multiple sources
            logger.info(f"Fetching steps data from multiple sources...")
            steps_data = self._get_data_from_sources(data_sources['steps'], start_time, end_time)
            if steps_data:
                activity_data['steps'] = sum(point.get('value', [{}])[0].get('intVal', 0) for point in steps_data)
                logger.info(f"Steps data found: {activity_data['steps']} steps from {len(steps_data)} data points")
            else:
                logger.warning("No steps data found from any source")
            
            # Get distance data
            distance_data = self._get_data_from_sources(data_sources['distance'], start_time, end_time)
            if distance_data:
                activity_data['distance_meters'] = sum(point.get('value', [{}])[0].get('fpVal', 0.0) for point in distance_data)

            # Get calories data
            calories_data = self._get_data_from_sources(data_sources['calories'], start_time, end_time)
            if calories_data:
                activity_data['calories_burned'] = int(sum(point.get('value', [{}])[0].get('fpVal', 0.0) for point in calories_data))

            # Get heart rate data
            heart_rate_data = self._get_data_from_sources(data_sources['heart_rate'], start_time, end_time)
            if heart_rate_data:
                heart_rates = [point.get('value', [{}])[0].get('fpVal', 0) for point in heart_rate_data if point.get('value', [{}])[0].get('fpVal', 0) > 0]
                if heart_rates:
                    activity_data['heart_rate_avg'] = int(sum(heart_rates) / len(heart_rates))
                    activity_data['heart_rate_max'] = int(max(heart_rates))

            # Get sleep data
            sleep_data = self._get_data_from_sources(data_sources['sleep'], start_time, end_time)
            if sleep_data:
                sleep_info = self._process_sleep_data(sleep_data)
                activity_data.update(sleep_info)

            # Calculate active minutes (simplified - based on steps)
            activity_data['active_minutes'] = min(activity_data['steps'] // 100, 120)  # Rough estimate
            
            logger.info(f"Final activity data: {activity_data}")
            return activity_data

        except Exception as e:
            logger.error(f"Error getting Google Fit data: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None

    def list_data_sources(self) -> List[Dict]:
        """List available data sources for debugging"""
        try:
            url = f"{self.base_url}/dataSources"
            logger.info(f"Listing data sources: {url}")

            response = requests.get(url, headers=self.headers, timeout=10)
            logger.info(f"Data sources response status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                data_sources = data.get('dataSource', [])
                logger.info(f"Found {len(data_sources)} data sources")

                for ds in data_sources[:5]:  # Log first 5 for debugging
                    logger.info(f"Data source: {ds.get('dataStreamId', 'Unknown')}")

                return data_sources
            else:
                logger.warning(f"Failed to list data sources: {response.status_code}")
                logger.warning(f"Response: {response.text[:500]}")
                return []

        except Exception as e:
            logger.error(f"Error listing data sources: {e}")
            return []
    
    def _get_data_source(self, data_source: str, start_time: int, end_time: int) -> List[Dict]:
        """Get data from a specific Google Fit data source"""
        try:
            url = f"{self.base_url}/dataSources/{data_source}/datasets/{start_time * 1000000}-{end_time * 1000000}"
            logger.info(f"Making request to Google Fit API: {url}")

            response = requests.get(url, headers=self.headers, timeout=10)
            logger.info(f"Google Fit API response status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                points = data.get('point', [])
                logger.info(f"Retrieved {len(points)} data points from {data_source}")
                if points:
                    logger.debug(f"Sample data point: {points[0] if points else 'None'}")
                return points
            else:
                logger.warning(f"Google Fit API returned status {response.status_code} for data source {data_source}")
                logger.warning(f"Response content: {response.text[:500]}")
                return []

        except Exception as e:
            logger.error(f"Error getting data from Google Fit data source {data_source}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []

    def _get_data_from_sources(self, data_sources: List[str], start_time: int, end_time: int) -> List[Dict]:
        """Try to get data from multiple data sources, return first successful result"""
        for data_source in data_sources:
            logger.info(f"Trying data source: {data_source}")
            data = self._get_data_source(data_source, start_time, end_time)
            if data:
                logger.info(f"Successfully got data from: {data_source}")
                return data

        logger.warning(f"No data found from any of the {len(data_sources)} data sources")
        return []

    def _process_sleep_data(self, sleep_data: List[Dict]) -> Dict[str, Any]:
        """Process Google Fit sleep data into structured format"""
        try:
            if not sleep_data:
                return {}

            sleep_info = {
                'sleep_duration_minutes': 0,
                'sleep_efficiency': None,
                'deep_sleep_minutes': 0,
                'light_sleep_minutes': 0,
                'rem_sleep_minutes': 0,
                'awake_minutes': 0,
                'sleep_start_time': None,
                'sleep_end_time': None
            }

            # Process sleep segments
            sleep_segments = []
            for point in sleep_data:
                if 'value' in point and point['value']:
                    value = point['value'][0]
                    sleep_type = value.get('intVal', 0)  # Sleep type: 1=awake, 2=sleep, 3=out-of-bed, 4=light, 5=deep, 6=REM

                    # Get start and end times
                    start_time_ns = int(point.get('startTimeNanos', 0))
                    end_time_ns = int(point.get('endTimeNanos', 0))
                    duration_minutes = (end_time_ns - start_time_ns) / (1000000000 * 60)  # Convert nanoseconds to minutes

                    sleep_segments.append({
                        'type': sleep_type,
                        'duration_minutes': duration_minutes,
                        'start_time': datetime.fromtimestamp(start_time_ns / 1000000000, tz=timezone.utc),
                        'end_time': datetime.fromtimestamp(end_time_ns / 1000000000, tz=timezone.utc)
                    })

            if sleep_segments:
                # Sort by start time
                sleep_segments.sort(key=lambda x: x['start_time'])

                # Calculate sleep metrics
                total_sleep_time = 0
                for segment in sleep_segments:
                    sleep_type = segment['type']
                    duration = segment['duration_minutes']

                    if sleep_type == 1:  # Awake
                        sleep_info['awake_minutes'] += duration
                    elif sleep_type == 2:  # General sleep
                        sleep_info['light_sleep_minutes'] += duration
                        total_sleep_time += duration
                    elif sleep_type == 4:  # Light sleep
                        sleep_info['light_sleep_minutes'] += duration
                        total_sleep_time += duration
                    elif sleep_type == 5:  # Deep sleep
                        sleep_info['deep_sleep_minutes'] += duration
                        total_sleep_time += duration
                    elif sleep_type == 6:  # REM sleep
                        sleep_info['rem_sleep_minutes'] += duration
                        total_sleep_time += duration

                sleep_info['sleep_duration_minutes'] = int(total_sleep_time)

                # Set sleep start and end times
                sleep_info['sleep_start_time'] = sleep_segments[0]['start_time']
                sleep_info['sleep_end_time'] = sleep_segments[-1]['end_time']

                # Calculate sleep efficiency (time asleep / time in bed)
                total_time_in_bed = sum(segment['duration_minutes'] for segment in sleep_segments)
                if total_time_in_bed > 0:
                    sleep_info['sleep_efficiency'] = round((total_sleep_time / total_time_in_bed) * 100, 1)

            return sleep_info

        except Exception as e:
            logger.error(f"Error processing sleep data: {e}")
            return {}

    def get_aggregate_data(self, date: datetime) -> Dict[str, Any]:
        """Get aggregated data using Google Fit aggregate API"""
        try:
            logger.info(f"Getting aggregate data for {date}")

            # Convert date to nanoseconds
            # Ensure timezone-aware datetime
            if date.tzinfo is None:
                date = date.replace(tzinfo=timezone.utc)
            start_time_ns = int(date.replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000000000)
            end_time_ns = int(date.replace(hour=23, minute=59, second=59, microsecond=999999).timestamp() * 1000000000)

            # Aggregate request body
            aggregate_request = {
                "aggregateBy": [
                    {"dataTypeName": "com.google.step_count.delta"},
                    {"dataTypeName": "com.google.distance.delta"},
                    {"dataTypeName": "com.google.calories.expended"},
                    {"dataTypeName": "com.google.heart_rate.bpm"}
                ],
                "bucketByTime": {"durationMillis": 86400000},  # 1 day
                "startTimeMillis": start_time_ns // 1000000,
                "endTimeMillis": end_time_ns // 1000000
            }

            url = f"{self.base_url}/dataset:aggregate"
            logger.info(f"Making aggregate request to: {url}")

            response = requests.post(url, headers=self.headers, json=aggregate_request, timeout=10)
            logger.info(f"Aggregate API response status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Aggregate response: {data}")

                activity_data = {
                    'steps': 0,
                    'distance_meters': 0.0,
                    'calories_burned': 0,
                    'active_minutes': 0,
                    'heart_rate_avg': None,
                    'heart_rate_max': None,
                    'exercise_sessions': []
                }

                # Process buckets
                for bucket in data.get('bucket', []):
                    for dataset in bucket.get('dataset', []):
                        data_type = dataset.get('dataSourceId', '')

                        for point in dataset.get('point', []):
                            values = point.get('value', [])

                            if 'step_count' in data_type and values:
                                activity_data['steps'] += values[0].get('intVal', 0)
                            elif 'distance' in data_type and values:
                                activity_data['distance_meters'] += values[0].get('fpVal', 0.0)
                            elif 'calories' in data_type and values:
                                activity_data['calories_burned'] += int(values[0].get('fpVal', 0.0))

                # Calculate active minutes based on steps
                activity_data['active_minutes'] = min(activity_data['steps'] // 100, 120)

                logger.info(f"Aggregate data result: {activity_data}")
                return activity_data
            else:
                logger.warning(f"Aggregate API failed: {response.status_code}")
                logger.warning(f"Response: {response.text[:500]}")
                return None

        except Exception as e:
            logger.error(f"Error getting aggregate data: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None

class FitbitAPI(BaseFitnessAPI):
    """Fitbit API integration"""
    
    def __init__(self, access_token: str, refresh_token: str = None):
        super().__init__(access_token, refresh_token)
        self.base_url = "https://api.fitbit.com/1/user/-"
    
    def test_connection(self) -> bool:
        """Test Fitbit API connection"""
        try:
            url = f"{self.base_url}/profile.json"
            response = requests.get(url, headers=self.headers, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Fitbit connection test failed: {e}")
            return False

    def get_user_profile(self) -> Dict[str, Any]:
        """Get Fitbit user profile"""
        try:
            url = f"{self.base_url}/profile.json"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                profile_data = response.json()
                return profile_data.get('user', {})
            else:
                logger.error(f"Failed to get Fitbit profile: {response.status_code}")
                return {'encodedId': f'fitbit_user_{hash(self.access_token) % 10000}'}

        except Exception as e:
            logger.error(f"Error getting Fitbit profile: {e}")
            return {'encodedId': f'fitbit_user_{hash(self.access_token) % 10000}'}
    
    def get_activity_data(self, date: datetime) -> Dict[str, Any]:
        """Get activity data from Fitbit for a specific date"""
        try:
            date_str = date.strftime('%Y-%m-%d')
            
            activity_data = {
                'steps': 0,
                'distance_meters': 0.0,
                'calories_burned': 0,
                'active_minutes': 0,
                'heart_rate_avg': None,
                'heart_rate_max': None,
                'exercise_sessions': [],
                # Sleep data
                'sleep_duration_minutes': None,
                'sleep_efficiency': None,
                'deep_sleep_minutes': None,
                'light_sleep_minutes': None,
                'rem_sleep_minutes': None,
                'awake_minutes': None,
                'sleep_start_time': None,
                'sleep_end_time': None
            }
            
            # Get daily activity summary
            summary_url = f"{self.base_url}/activities/date/{date_str}.json"
            summary_response = requests.get(summary_url, headers=self.headers, timeout=10)
            
            if summary_response.status_code == 200:
                summary_data = summary_response.json()
                summary = summary_data.get('summary', {})
                
                activity_data['steps'] = summary.get('steps', 0)
                activity_data['calories_burned'] = summary.get('caloriesOut', 0)
                activity_data['active_minutes'] = summary.get('veryActiveMinutes', 0) + summary.get('fairlyActiveMinutes', 0)
                
                # Convert distance from km to meters
                distances = summary.get('distances', [])
                total_distance = sum(d.get('distance', 0) for d in distances if d.get('activity') == 'total')
                activity_data['distance_meters'] = total_distance * 1000  # Convert km to meters
            
            # Get heart rate data
            heart_rate_url = f"{self.base_url}/activities/heart/date/{date_str}/1d.json"
            heart_rate_response = requests.get(heart_rate_url, headers=self.headers, timeout=10)
            
            if heart_rate_response.status_code == 200:
                heart_rate_data = heart_rate_response.json()
                activities_heart = heart_rate_data.get('activities-heart', [])
                if activities_heart:
                    heart_rate_zones = activities_heart[0].get('value', {}).get('heartRateZones', [])
                    resting_heart_rate = activities_heart[0].get('value', {}).get('restingHeartRate')
                    
                    # Calculate average heart rate from zones
                    total_minutes = sum(zone.get('minutes', 0) for zone in heart_rate_zones)
                    if total_minutes > 0:
                        weighted_hr = sum(zone.get('min', 0) * zone.get('minutes', 0) for zone in heart_rate_zones)
                        activity_data['heart_rate_avg'] = int(weighted_hr / total_minutes) if total_minutes > 0 else resting_heart_rate
                    
                    # Get max heart rate
                    max_hr = max((zone.get('max', 0) for zone in heart_rate_zones), default=None)
                    activity_data['heart_rate_max'] = max_hr if max_hr and max_hr > 0 else None

            # Get sleep data
            sleep_url = f"{self.base_url}/sleep/date/{date_str}.json"
            sleep_response = requests.get(sleep_url, headers=self.headers, timeout=10)

            if sleep_response.status_code == 200:
                sleep_data = sleep_response.json()
                sleep_info = self._process_fitbit_sleep_data(sleep_data)
                activity_data.update(sleep_info)

            return activity_data
            
        except Exception as e:
            logger.error(f"Error getting Fitbit data: {e}")
            return None

    def _process_fitbit_sleep_data(self, sleep_data: Dict) -> Dict[str, Any]:
        """Process Fitbit sleep data into structured format"""
        try:
            sleep_info = {
                'sleep_duration_minutes': None,
                'sleep_efficiency': None,
                'deep_sleep_minutes': None,
                'light_sleep_minutes': None,
                'rem_sleep_minutes': None,
                'awake_minutes': None,
                'sleep_start_time': None,
                'sleep_end_time': None
            }

            sleep_logs = sleep_data.get('sleep', [])
            if not sleep_logs:
                return sleep_info

            # Get the main sleep log (usually the longest one)
            main_sleep = max(sleep_logs, key=lambda x: x.get('duration', 0))

            # Basic sleep metrics
            sleep_info['sleep_duration_minutes'] = main_sleep.get('duration', 0) // 60000  # Convert ms to minutes
            sleep_info['sleep_efficiency'] = main_sleep.get('efficiency')

            # Sleep start and end times
            start_time_str = main_sleep.get('startTime')
            end_time_str = main_sleep.get('endTime')

            if start_time_str:
                sleep_info['sleep_start_time'] = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            if end_time_str:
                sleep_info['sleep_end_time'] = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))

            # Sleep stage data
            levels = main_sleep.get('levels', {})
            summary = levels.get('summary', {})

            if summary:
                sleep_info['deep_sleep_minutes'] = summary.get('deep', {}).get('minutes', 0)
                sleep_info['light_sleep_minutes'] = summary.get('light', {}).get('minutes', 0)
                sleep_info['rem_sleep_minutes'] = summary.get('rem', {}).get('minutes', 0)
                sleep_info['awake_minutes'] = summary.get('wake', {}).get('minutes', 0)

            return sleep_info

        except Exception as e:
            logger.error(f"Error processing Fitbit sleep data: {e}")
            return {}

class MockFitnessAPI(BaseFitnessAPI):
    """Mock fitness API for testing purposes"""
    
    def __init__(self, access_token: str = "mock_token", refresh_token: str = None):
        super().__init__(access_token, refresh_token)
    
    def test_connection(self) -> bool:
        """Always return True for mock API"""
        return True

    def get_user_profile(self) -> Dict[str, Any]:
        """Return mock user profile"""
        return {
            'id': 'mock_user_123',
            'encodedId': 'mock_user_123',
            'displayName': 'Mock User'
        }
    
    def get_activity_data(self, date: datetime) -> Dict[str, Any]:
        """Return mock activity data"""
        import random
        
        # Generate realistic mock data
        base_steps = random.randint(3000, 15000)
        
        # Generate realistic sleep data
        sleep_duration = random.randint(360, 540)  # 6-9 hours in minutes
        deep_sleep = int(sleep_duration * random.uniform(0.15, 0.25))  # 15-25% deep sleep
        rem_sleep = int(sleep_duration * random.uniform(0.20, 0.25))   # 20-25% REM sleep
        light_sleep = sleep_duration - deep_sleep - rem_sleep
        awake_time = random.randint(5, 30)  # 5-30 minutes awake

        # Generate sleep times (assuming sleep from 10 PM to 6-8 AM)
        sleep_start = date.replace(hour=22, minute=random.randint(0, 60), second=0, microsecond=0)
        sleep_end = sleep_start + timedelta(minutes=sleep_duration + awake_time)

        return {
            'steps': base_steps,
            'distance_meters': base_steps * 0.7,  # Rough conversion
            'calories_burned': random.randint(1800, 3000),
            'active_minutes': random.randint(20, 90),
            'heart_rate_avg': random.randint(65, 85),
            'heart_rate_max': random.randint(120, 180),
            'exercise_sessions': [
                {
                    'name': 'Walking',
                    'duration_minutes': random.randint(20, 60),
                    'calories': random.randint(100, 300)
                }
            ],
            # Sleep data
            'sleep_duration_minutes': sleep_duration,
            'sleep_efficiency': round(random.uniform(75, 95), 1),
            'deep_sleep_minutes': deep_sleep,
            'light_sleep_minutes': light_sleep,
            'rem_sleep_minutes': rem_sleep,
            'awake_minutes': awake_time,
            'sleep_start_time': sleep_start,
            'sleep_end_time': sleep_end
        }
