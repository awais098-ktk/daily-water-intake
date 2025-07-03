from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///water_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    daily_goal = db.Column(db.Integer, default=2000)  # ml
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    water_logs = db.relationship('WaterLog', backref='user', lazy=True)

class WaterLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # ml
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.String(200))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return render_template('register.html')
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    today = datetime.now().date()
    today_logs = WaterLog.query.filter(
        WaterLog.user_id == current_user.id,
        db.func.date(WaterLog.timestamp) == today
    ).all()
    
    total_today = sum(log.amount for log in today_logs)
    progress_percentage = min((total_today / current_user.daily_goal) * 100, 100)
    
    return render_template('dashboard.html', 
                         total_today=total_today,
                         daily_goal=current_user.daily_goal,
                         progress_percentage=progress_percentage,
                         logs=today_logs)

@app.route('/log_water', methods=['POST'])
@login_required
def log_water():
    amount = int(request.form['amount'])
    notes = request.form.get('notes', '')
    
    water_log = WaterLog(
        user_id=current_user.id,
        amount=amount,
        notes=notes
    )
    db.session.add(water_log)
    db.session.commit()
    
    flash(f'Logged {amount}ml of water!')
    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/api/water_data')
@login_required
def water_data():
    # Get last 7 days of data
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=6)
    
    data = []
    for i in range(7):
        date = start_date + timedelta(days=i)
        logs = WaterLog.query.filter(
            WaterLog.user_id == current_user.id,
            db.func.date(WaterLog.timestamp) == date
        ).all()
        total = sum(log.amount for log in logs)
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'amount': total
        })
    
    return jsonify(data)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
