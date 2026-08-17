import sys
import os
import asyncio
from quart import Quart
from quart_cors import cors
from websockets.server import serve
import websockets
import json
from dotenv import load_dotenv

load_dotenv()

# Add backend to path to import models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
from models import Order # type: ignore
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

app = Quart(__name__)

FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5000')
app = cors(app, allow_origin=[FRONTEND_URL])

DB_URL = os.environ.get('MONGODB_URL', 'mongodb://localhost:27017')

async def fetch_metrics():
    try:
        total_orders = await Order.find_all().count()
        
        revenue_agg = await Order.aggregate([{"$group": {"_id": None, "revenue": {"$sum": "$total"}}}]).to_list()
        total_revenue = revenue_agg[0]["revenue"] if revenue_agg else 0
        
        sales_agg = await Order.aggregate([
            {"$addFields": {"date": {"$substr": ["$created_at", 0, 10]}}},
            {"$group": {"_id": "$date", "revenue": {"$sum": "$total"}}},
            {"$sort": {"_id": -1}},
            {"$limit": 7}
        ]).to_list()
        
        dates = [row["_id"] for row in sales_agg][::-1]
        revenues = [row["revenue"] for row in sales_agg][::-1]

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

connected_clients = set()
MAX_CONNECTIONS = 100

async def ws_handler(websocket, path=None):
    if len(connected_clients) >= MAX_CONNECTIONS:
        await websocket.close(code=1008, reason="Too many connections")
        return

    connected_clients.add(websocket)
    try:
        metrics = await fetch_metrics()
        if metrics:
            await websocket.send(json.dumps({'event': 'metrics_update', 'data': metrics}))
            
        async for message in websocket:
            pass
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        connected_clients.remove(websocket)

async def background_task():
    while True:
        await asyncio.sleep(5)
        if not connected_clients:
            continue
            
        metrics = await fetch_metrics()
        if metrics:
            message = json.dumps({'event': 'metrics_update', 'data': metrics})
            websockets.broadcast(connected_clients, message)

@app.before_serving
async def startup():
    client = AsyncIOMotorClient(DB_URL)
    await init_beanie(database=client.boojee, document_models=[Order])
    
    app.add_background_task(background_task)
    ws_server = await serve(ws_handler, "0.0.0.0", 5001)
    app.ws_server = ws_server

@app.after_serving
async def shutdown():
    if hasattr(app, 'ws_server'):
        app.ws_server.close()
        await app.ws_server.wait_closed()

if __name__ == '__main__':
    import hypercorn.asyncio
    import hypercorn.config
    
    config = hypercorn.config.Config()
    config.bind = ["0.0.0.0:5002"]
    asyncio.run(hypercorn.asyncio.serve(app, config))
