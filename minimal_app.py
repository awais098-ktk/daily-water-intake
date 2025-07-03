#!/usr/bin/env python3
"""
Minimal Flask app to test basic functionality
"""

from flask import Flask, render_template_string

app = Flask(__name__)
app.secret_key = 'test-secret-key'

@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Water Intake Tracker - Test</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-body text-center">
                            <h1 class="card-title text-primary">🚰 Water Intake Tracker</h1>
                            <p class="card-text">Application is running successfully!</p>
                            <div class="alert alert-success">
                                <strong>✅ Status:</strong> All systems operational
                            </div>
                            <a href="/test" class="btn btn-primary">Test Features</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    ''')

@app.route('/test')
def test():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-body">
                            <h2 class="card-title">🧪 Test Results</h2>
                            <div class="list-group">
                                <div class="list-group-item">
                                    <strong>✅ Flask Application:</strong> Running
                                </div>
                                <div class="list-group-item">
                                    <strong>✅ Templates:</strong> Rendering
                                </div>
                                <div class="list-group-item">
                                    <strong>✅ Bootstrap CSS:</strong> Loading
                                </div>
                                <div class="list-group-item">
                                    <strong>✅ Routes:</strong> Working
                                </div>
                            </div>
                            <div class="mt-3">
                                <a href="/" class="btn btn-secondary">← Back to Home</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    ''')

if __name__ == '__main__':
    print("Starting minimal Flask app for testing...")
    print("Open http://127.0.0.1:5000 in your browser")
    app.run(debug=True, host='127.0.0.1', port=5000)
