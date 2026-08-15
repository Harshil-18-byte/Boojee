import os
import time
from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)
# Enable CORS for the Socket.IO server
socketio = SocketIO(app, cors_allowed_origins="*")

if os.environ.get('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    # Use the shared SQLite DB for local dev
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

db = SQLAlchemy(app)

def fetch_metrics():
    with app.app_context():
        try:
            # Query the orders table
            total_orders = db.session.execute(text('SELECT COUNT(*) FROM orders')).scalar()
            total_revenue = db.session.execute(text('SELECT SUM(total) FROM orders')).scalar() or 0
            
            # Simple aggregation by date
            sales_by_date = db.session.execute(text('''
                SELECT DATE(created_at) as date, SUM(total) as revenue 
                FROM orders 
                GROUP BY DATE(created_at) 
                ORDER BY date DESC LIMIT 7
            ''')).fetchall()
            
            dates = [row[0] for row in sales_by_date][::-1]
            revenues = [row[1] for row in sales_by_date][::-1]

            return {
                'total_orders': total_orders,
                'total_revenue': total_revenue,
                'chart_data': {
                    'labels': dates,
                    'datasets': [{
                        'label': 'Revenue (INR)',
                        'data': revenues,
                        'borderColor': '#1E1E1E',
                        'backgroundColor': 'rgba(30,30,30,0.1)',
                        'borderWidth': 2,
                        'tension': 0.4,
                        'fill': True
                    }]
                }
            }
        except Exception as e:
            print("DB Error:", e)
            return None

def background_thread():
    while True:
        socketio.sleep(5)
        metrics = fetch_metrics()
        if metrics:
            socketio.emit('metrics_update', metrics)

@socketio.on('connect')
def test_connect():
    metrics = fetch_metrics()
    if metrics:
        socketio.emit('metrics_update', metrics)
    print('Client connected')

if __name__ == '__main__':
    socketio.start_background_task(background_thread)
    socketio.run(app, host='0.0.0.0', port=5001, allow_unsafe_werkzeug=True)
