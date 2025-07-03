"""
Data Export Module for Water Intake Tracker
Provides functionality to export water intake data in various formats
"""

import json
import io
import os
from datetime import datetime, timedelta
from flask import current_app
from io import BytesIO
import base64

# Try to import optional dependencies
try:
    import pandas as pd
    pandas_available = True
except ImportError:
    pandas_available = False

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    reportlab_available = True
except ImportError:
    reportlab_available = False

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    matplotlib_available = True
except ImportError:
    matplotlib_available = False


class DataExporter:
    """Main class for exporting water intake data"""

    def __init__(self, user_id):
        self.user_id = user_id

    def get_water_logs(self, start_date=None, end_date=None, drink_types=None):
        """Get water logs for the specified date range and drink types"""
        # Import models only when needed and ensure we're in app context
        from flask import has_app_context, current_app

        if not has_app_context():
            raise RuntimeError("This method must be called within a Flask application context")

        # Import the models directly from the main app module
        # This ensures we get the models that are properly bound to the Flask app
        import sys

        # Try to get the models from the main module
        main_module = None
        for module_name, module in sys.modules.items():
            if hasattr(module, 'WaterLog') and hasattr(module, 'DrinkType') and hasattr(module, 'db'):
                main_module = module
                break

        if main_module:
            WaterLog = main_module.WaterLog
            DrinkType = main_module.DrinkType
            db = main_module.db
        else:
            # Fallback to the registry approach
            db = current_app.extensions['sqlalchemy']
            models = db.Model.registry._class_registry
            WaterLog = models.get('WaterLog')
            DrinkType = models.get('DrinkType')

            # If not found, try to find by table name
            if not WaterLog or not DrinkType:
                for name, model in models.items():
                    if hasattr(model, '__tablename__'):
                        if model.__tablename__ == 'water_logs':
                            WaterLog = model
                        elif model.__tablename__ == 'drink_types':
                            DrinkType = model

        # Use the model's query method which should be properly bound
        query = WaterLog.query.filter_by(user_id=self.user_id)

        if start_date:
            query = query.filter(WaterLog.timestamp >= start_date)
        if end_date:
            query = query.filter(WaterLog.timestamp <= end_date)
        if drink_types:
            query = query.filter(WaterLog.drink_type_id.in_(drink_types))

        logs = query.order_by(WaterLog.timestamp.desc()).all()

        # Convert to list of dictionaries
        data = []
        for log in logs:
            drink_type_name = "Unknown"
            if log.drink_type:
                drink_type_name = log.drink_type.name

            data.append({
                'id': log.id,
                'amount': log.amount,
                'timestamp': log.timestamp,
                'drink_type': drink_type_name,
                'input_method': log.input_method,
                'notes': log.notes or ''
            })

        return data

    def get_meal_logs(self, start_date=None, end_date=None, meal_types=None, food_categories=None):
        """Get meal logs for the user with optional filtering"""
        from flask import has_app_context, current_app

        if not has_app_context():
            raise RuntimeError("This method must be called within a Flask application context")

        try:
            # Try to import meal models
            import sys
            main_module = None

            # Try to get the main app module
            for module_name, module in sys.modules.items():
                if hasattr(module, 'MealLog') and hasattr(module, 'FoodItem') and hasattr(module, 'FoodCategory'):
                    main_module = module
                    break

            if main_module:
                MealLog = main_module.MealLog
                FoodItem = main_module.FoodItem
                FoodCategory = main_module.FoodCategory
            else:
                # Fallback to registry approach
                db = current_app.extensions['sqlalchemy']
                models = db.Model.registry._class_registry
                MealLog = models.get('MealLog')
                FoodItem = models.get('FoodItem')
                FoodCategory = models.get('FoodCategory')

                if not MealLog:
                    # If meal models don't exist, return empty list
                    return []

            # Use the model's query method
            query = MealLog.query.filter_by(user_id=self.user_id)

            if start_date:
                query = query.filter(MealLog.timestamp >= start_date)
            if end_date:
                query = query.filter(MealLog.timestamp <= end_date)
            if meal_types:
                query = query.filter(MealLog.meal_type.in_(meal_types))

            logs = query.order_by(MealLog.timestamp.desc()).all()

            # Convert to list of dictionaries
            data = []
            for log in logs:
                food_category = "Unknown"
                if log.food_item and log.food_item.category:
                    food_category = log.food_item.category.name

                data.append({
                    'id': log.id,
                    'food_name': log.food_name,
                    'quantity_g': log.quantity_g,
                    'calories': log.calories,
                    'carbs': log.carbs,
                    'fats': log.fats,
                    'proteins': log.proteins,
                    'fiber': log.fiber,
                    'sugar': log.sugar,
                    'sodium': log.sodium,
                    'meal_type': log.meal_type,
                    'food_category': food_category,
                    'timestamp': log.timestamp,
                    'input_method': log.input_method,
                    'notes': log.notes or ''
                })

            return data

        except Exception as e:
            # If there's any error with meal models, return empty list
            print(f"Error getting meal logs: {e}")
            return []

    def get_combined_data(self, start_date=None, end_date=None, include_water=True, include_food=True):
        """Get combined water and food data"""
        combined_data = {
            'water_logs': [],
            'meal_logs': [],
            'summary': {}
        }

        if include_water:
            combined_data['water_logs'] = self.get_water_logs(start_date, end_date)

        if include_food:
            combined_data['meal_logs'] = self.get_meal_logs(start_date, end_date)

        # Calculate summary statistics
        combined_data['summary'] = self.get_combined_summary_stats(start_date, end_date)

        return combined_data

    def get_combined_summary_stats(self, start_date=None, end_date=None):
        """Get combined summary statistics for water and food data"""
        water_data = self.get_water_logs(start_date, end_date)
        meal_data = self.get_meal_logs(start_date, end_date)

        # Water statistics
        total_water_ml = sum(item['amount'] for item in water_data)
        water_entries = len(water_data)

        # Food statistics
        total_calories = sum(item['calories'] for item in meal_data)
        total_carbs = sum(item['carbs'] for item in meal_data)
        total_fats = sum(item['fats'] for item in meal_data)
        total_proteins = sum(item['proteins'] for item in meal_data)
        meal_entries = len(meal_data)

        # Calculate date range
        all_dates = []
        for item in water_data + meal_data:
            timestamp = item['timestamp']
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            all_dates.append(timestamp.date())

        unique_dates = len(set(all_dates)) if all_dates else 0

        return {
            'water': {
                'total_volume_ml': total_water_ml,
                'total_entries': water_entries,
                'avg_daily_ml': total_water_ml / unique_dates if unique_dates > 0 else 0
            },
            'nutrition': {
                'total_calories': total_calories,
                'total_carbs_g': total_carbs,
                'total_fats_g': total_fats,
                'total_proteins_g': total_proteins,
                'total_entries': meal_entries,
                'avg_daily_calories': total_calories / unique_dates if unique_dates > 0 else 0
            },
            'general': {
                'date_range_days': unique_dates,
                'total_entries': water_entries + meal_entries
            }
        }

    def export_csv(self, start_date=None, end_date=None, drink_types=None, include_food=False):
        """Export data as CSV"""
        data = self.get_water_logs(start_date, end_date, drink_types)

        if not data:
            return None

        if pandas_available:
            # Use pandas if available
            df = pd.DataFrame(data)

            # Format timestamp for better readability
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')

            # Reorder columns
            df = df[['timestamp', 'amount', 'drink_type', 'input_method', 'notes']]

            # Create CSV string
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)

            return csv_buffer.getvalue()
        else:
            # Manual CSV creation without pandas
            csv_buffer = io.StringIO()

            # Write header
            csv_buffer.write('timestamp,amount,drink_type,input_method,notes\n')

            # Write data rows
            for item in data:
                timestamp = item['timestamp']
                if isinstance(timestamp, datetime):
                    timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    timestamp_str = str(timestamp)

                # Escape commas and quotes in notes
                notes = str(item['notes'] or '').replace('"', '""')
                if ',' in notes or '"' in notes:
                    notes = f'"{notes}"'

                csv_buffer.write(f'{timestamp_str},{item["amount"]},{item["drink_type"]},{item["input_method"]},{notes}\n')

            return csv_buffer.getvalue()

    def export_combined_csv(self, start_date=None, end_date=None, drink_types=None):
        """Export combined water and food data as CSV"""
        combined_data = self.get_combined_data(start_date, end_date, True, True)

        if not combined_data['water_logs'] and not combined_data['meal_logs']:
            return None

        csv_buffer = io.StringIO()

        # Write water logs section
        if combined_data['water_logs']:
            csv_buffer.write('WATER INTAKE LOGS\n')
            csv_buffer.write('timestamp,amount_ml,drink_type,input_method,notes\n')

            for item in combined_data['water_logs']:
                timestamp = item['timestamp']
                if isinstance(timestamp, datetime):
                    timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    timestamp_str = str(timestamp)

                notes = str(item['notes'] or '').replace('"', '""')
                if ',' in notes or '"' in notes:
                    notes = f'"{notes}"'

                csv_buffer.write(f'{timestamp_str},{item["amount"]},{item["drink_type"]},{item["input_method"]},{notes}\n')

            csv_buffer.write('\n')

        # Write meal logs section
        if combined_data['meal_logs']:
            csv_buffer.write('MEAL LOGS\n')
            csv_buffer.write('timestamp,food_name,quantity_g,calories,carbs_g,fats_g,proteins_g,fiber_g,sugar_g,sodium_mg,meal_type,food_category,input_method,notes\n')

            for item in combined_data['meal_logs']:
                timestamp = item['timestamp']
                if isinstance(timestamp, datetime):
                    timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    timestamp_str = str(timestamp)

                # Escape text fields
                food_name = str(item['food_name']).replace('"', '""')
                meal_type = str(item['meal_type']).replace('"', '""')
                food_category = str(item['food_category']).replace('"', '""')
                input_method = str(item['input_method']).replace('"', '""')
                notes = str(item['notes'] or '').replace('"', '""')

                # Add quotes if needed
                if ',' in food_name or '"' in food_name:
                    food_name = f'"{food_name}"'
                if ',' in meal_type or '"' in meal_type:
                    meal_type = f'"{meal_type}"'
                if ',' in food_category or '"' in food_category:
                    food_category = f'"{food_category}"'
                if ',' in input_method or '"' in input_method:
                    input_method = f'"{input_method}"'
                if ',' in notes or '"' in notes:
                    notes = f'"{notes}"'

                csv_buffer.write(f'{timestamp_str},{food_name},{item["quantity_g"]},{item["calories"]},{item["carbs"]},{item["fats"]},{item["proteins"]},{item["fiber"]},{item["sugar"]},{item["sodium"]},{meal_type},{food_category},{input_method},{notes}\n')

            csv_buffer.write('\n')

        # Write summary section
        summary = combined_data['summary']
        csv_buffer.write('SUMMARY\n')
        csv_buffer.write('metric,value\n')
        csv_buffer.write(f'Total Water (ml),{summary["water"]["total_volume_ml"]}\n')
        csv_buffer.write(f'Total Calories,{summary["nutrition"]["total_calories"]}\n')
        csv_buffer.write(f'Total Carbs (g),{summary["nutrition"]["total_carbs_g"]}\n')
        csv_buffer.write(f'Total Fats (g),{summary["nutrition"]["total_fats_g"]}\n')
        csv_buffer.write(f'Total Proteins (g),{summary["nutrition"]["total_proteins_g"]}\n')
        csv_buffer.write(f'Days Tracked,{summary["general"]["date_range_days"]}\n')
        csv_buffer.write(f'Total Entries,{summary["general"]["total_entries"]}\n')

        return csv_buffer.getvalue()

    def export_json(self, start_date=None, end_date=None, drink_types=None, include_food=False):
        """Export data as JSON"""
        if include_food:
            # Export combined data
            combined_data = self.get_combined_data(start_date, end_date, True, True)

            if not combined_data['water_logs'] and not combined_data['meal_logs']:
                return None

            # Convert datetime objects to strings for JSON serialization
            for item in combined_data['water_logs']:
                if isinstance(item['timestamp'], datetime):
                    item['timestamp'] = item['timestamp'].isoformat()

            for item in combined_data['meal_logs']:
                if isinstance(item['timestamp'], datetime):
                    item['timestamp'] = item['timestamp'].isoformat()

            export_data = {
                'export_date': datetime.now().isoformat(),
                'user_id': self.user_id,
                'date_range': {
                    'start': start_date.isoformat() if start_date else None,
                    'end': end_date.isoformat() if end_date else None
                },
                'water_logs': {
                    'total_records': len(combined_data['water_logs']),
                    'data': combined_data['water_logs']
                },
                'meal_logs': {
                    'total_records': len(combined_data['meal_logs']),
                    'data': combined_data['meal_logs']
                },
                'summary': combined_data['summary']
            }
        else:
            # Export only water data (existing functionality)
            data = self.get_water_logs(start_date, end_date, drink_types)

            if not data:
                return None

            # Convert datetime objects to strings for JSON serialization
            for item in data:
                if isinstance(item['timestamp'], datetime):
                    item['timestamp'] = item['timestamp'].isoformat()

            export_data = {
                'export_date': datetime.now().isoformat(),
                'user_id': self.user_id,
                'date_range': {
                    'start': start_date.isoformat() if start_date else None,
                    'end': end_date.isoformat() if end_date else None
                },
                'total_records': len(data),
                'data': data
            }

        return json.dumps(export_data, indent=2)

    def create_chart(self, data, chart_type='daily'):
        """Create a chart from the data"""
        if not data or not matplotlib_available:
            return None

        if pandas_available:
            # Use pandas for data processing
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date

            # Group by date and sum amounts
            daily_data = df.groupby('date')['amount'].sum().reset_index()
            dates = daily_data['date']
            amounts = daily_data['amount']
        else:
            # Manual data processing without pandas
            daily_totals = {}
            for item in data:
                timestamp = item['timestamp']
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                date = timestamp.date()

                if date not in daily_totals:
                    daily_totals[date] = 0
                daily_totals[date] += item['amount']

            dates = sorted(daily_totals.keys())
            amounts = [daily_totals[date] for date in dates]

        # Create matplotlib chart
        plt.figure(figsize=(10, 6))
        plt.plot(dates, amounts, marker='o', linewidth=2, markersize=6)
        plt.title('Daily Water Intake', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Amount (ml)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save to bytes
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()

        return img_buffer

    def export_pdf(self, start_date=None, end_date=None, drink_types=None, include_charts=True):
        """Export data as PDF report"""
        if not reportlab_available:
            # Return a simple text-based report if ReportLab is not available
            return self._create_text_report(start_date, end_date, drink_types)

        data = self.get_water_logs(start_date, end_date, drink_types)

        if not data:
            return None

        # Create PDF buffer
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)

        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )

        # Build PDF content
        story = []

        # Title
        title = Paragraph("Water Intake Report", title_style)
        story.append(title)
        story.append(Spacer(1, 20))

        # Report info
        report_info = f"""
        <b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        <b>Date Range:</b> {start_date.strftime('%Y-%m-%d') if start_date else 'All time'} to {end_date.strftime('%Y-%m-%d') if end_date else 'Present'}<br/>
        <b>Total Records:</b> {len(data)}<br/>
        <b>Total Volume:</b> {sum(item['amount'] for item in data)} ml
        """
        story.append(Paragraph(report_info, styles['Normal']))
        story.append(Spacer(1, 20))

        # Add chart if requested
        if include_charts and data:
            chart_buffer = self.create_chart(data)
            if chart_buffer:
                # Save chart as temporary file
                chart_path = os.path.join(current_app.static_folder, 'temp_chart.png')
                with open(chart_path, 'wb') as f:
                    f.write(chart_buffer.getvalue())

                # Add chart to PDF
                chart_img = Image(chart_path, width=6*inch, height=3.6*inch)
                story.append(chart_img)
                story.append(Spacer(1, 20))

                # Clean up temporary file
                try:
                    os.remove(chart_path)
                except:
                    pass

        # Create data table
        if data:
            # Prepare table data
            table_data = [['Date', 'Time', 'Amount (ml)', 'Drink Type', 'Method']]

            for item in data:
                timestamp = item['timestamp']
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

                table_data.append([
                    timestamp.strftime('%Y-%m-%d'),
                    timestamp.strftime('%H:%M:%S'),
                    str(item['amount']),
                    item['drink_type'],
                    item['input_method']
                ])

            # Create table
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            story.append(table)

        # Build PDF
        doc.build(story)
        pdf_buffer.seek(0)

        return pdf_buffer.getvalue()

    def _create_text_report(self, start_date=None, end_date=None, drink_types=None):
        """Create a simple text-based report when PDF libraries are not available"""
        data = self.get_water_logs(start_date, end_date, drink_types)

        if not data:
            return None

        # Create text report
        report_lines = []
        report_lines.append("WATER INTAKE REPORT")
        report_lines.append("=" * 50)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        if start_date:
            report_lines.append(f"Start Date: {start_date.strftime('%Y-%m-%d')}")
        if end_date:
            report_lines.append(f"End Date: {end_date.strftime('%Y-%m-%d')}")

        report_lines.append(f"Total Records: {len(data)}")
        report_lines.append(f"Total Volume: {sum(item['amount'] for item in data)} ml")
        report_lines.append("")

        # Add data table
        report_lines.append("DETAILED DATA:")
        report_lines.append("-" * 50)
        report_lines.append("Date\t\tTime\t\tAmount\tDrink Type\tMethod")
        report_lines.append("-" * 50)

        for item in data:
            timestamp = item['timestamp']
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

            date_str = timestamp.strftime('%Y-%m-%d')
            time_str = timestamp.strftime('%H:%M:%S')

            report_lines.append(f"{date_str}\t{time_str}\t{item['amount']} ml\t{item['drink_type']}\t{item['input_method']}")

        report_text = '\n'.join(report_lines)
        return report_text.encode('utf-8')

    def get_summary_stats(self, start_date=None, end_date=None):
        """Get summary statistics for the data"""
        data = self.get_water_logs(start_date, end_date)

        if not data:
            return {}

        if pandas_available:
            # Use pandas for calculations
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date

            # Calculate statistics
            total_volume = df['amount'].sum()
            daily_avg = df.groupby('date')['amount'].sum().mean()
            max_daily = df.groupby('date')['amount'].sum().max()
            min_daily = df.groupby('date')['amount'].sum().min()

            # Drink type breakdown
            drink_breakdown = df.groupby('drink_type')['amount'].sum().to_dict()

            # Input method breakdown
            method_breakdown = df.groupby('input_method')['amount'].sum().to_dict()

            total_days = len(df['date'].unique())
        else:
            # Manual calculations without pandas
            total_volume = sum(item['amount'] for item in data)

            # Group by date
            daily_totals = {}
            drink_breakdown = {}
            method_breakdown = {}

            for item in data:
                timestamp = item['timestamp']
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                date = timestamp.date()

                # Daily totals
                if date not in daily_totals:
                    daily_totals[date] = 0
                daily_totals[date] += item['amount']

                # Drink type breakdown
                drink_type = item['drink_type']
                if drink_type not in drink_breakdown:
                    drink_breakdown[drink_type] = 0
                drink_breakdown[drink_type] += item['amount']

                # Method breakdown
                method = item['input_method']
                if method not in method_breakdown:
                    method_breakdown[method] = 0
                method_breakdown[method] += item['amount']

            daily_amounts = list(daily_totals.values())
            daily_avg = sum(daily_amounts) / len(daily_amounts) if daily_amounts else 0
            max_daily = max(daily_amounts) if daily_amounts else 0
            min_daily = min(daily_amounts) if daily_amounts else 0
            total_days = len(daily_totals)

        # Convert to native Python types to avoid JSON serialization issues
        def to_python_type(value):
            """Convert pandas/numpy types to native Python types"""
            if hasattr(value, 'item'):  # numpy scalar
                return value.item()
            elif hasattr(value, 'tolist'):  # numpy array
                return value.tolist()
            else:
                return value

        return {
            'total_volume': float(round(to_python_type(total_volume), 2)),
            'daily_average': float(round(to_python_type(daily_avg), 2)),
            'max_daily': float(round(to_python_type(max_daily), 2)),
            'min_daily': float(round(to_python_type(min_daily), 2)),
            'total_days': int(to_python_type(total_days)),
            'total_logs': int(len(data)),
            'drink_breakdown': {k: float(to_python_type(v)) for k, v in drink_breakdown.items()},
            'method_breakdown': {k: float(to_python_type(v)) for k, v in method_breakdown.items()}
        }
