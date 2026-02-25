from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import json
import os
from datetime import datetime

app = FastAPI(title="dongsu AI Agent API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 상태 저장
STATUS_FILE = "/tmp/trading_status.json"

def load_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    return {
        "capital": {"initial": 10000, "current": 10000, "change": 0, "change_percent": 0},
        "trades": {"total": 0, "winning": 0, "losing": 0, "win_rate": 0, "open_positions": 0},
        "positions": [],
        "prices": {"BTC": 67843, "ETH": 2032},
        "last_update": datetime.now().isoformat()
    }

@app.get("/")
def root():
    return {
        "agent": "dongsu",
        "version": "1.0.0",
        "status": "active",
        "endpoints": [
            "/api/status",
            "/api/analyze/{symbol}",
            "/api/positions",
            "/api/trades"
        ]
    }

@app.get("/api/status")
def get_status():
    return load_status()

@app.get("/api/analyze/{symbol}")
def analyze_symbol(symbol: str):
    return {
        "symbol": symbol,
        "timestamp": datetime.now().isoformat(),
        "price": 2032 if symbol == "ETH" else 67843,
        "signal": "hold",
        "confidence": 0.75
    }

@app.get("/api/positions")
def get_positions():
    return {"positions": [], "count": 0}

@app.get("/api/trades")
def get_trades():
    return {"trades": [], "total": 0}
