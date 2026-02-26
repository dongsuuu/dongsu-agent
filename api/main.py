from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import json
import os
import subprocess
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

# 명령 큐
command_queue: List[Dict] = []
agents: Dict[str, Dict] = {
    "trading": {
        "id": "trading",
        "name": "트레이딩 에이전트",
        "status": "running",
        "last_activity": datetime.now().isoformat()
    },
    "research": {
        "id": "research", 
        "name": "리서치 에이전트",
        "status": "idle",
        "last_activity": datetime.now().isoformat()
    },
    "onchain": {
        "id": "onchain",
        "name": "온체인 에이전트",
        "status": "running",
        "last_activity": datetime.now().isoformat()
    }
}

class CommandRequest(BaseModel):
    command: str
    agent_id: Optional[str] = None
    params: Optional[Dict] = None

class AgentCreateRequest(BaseModel):
    name: str
    type: str

@app.get("/")
def root():
    return {
        "agent": "dongsu",
        "version": "1.0.0",
        "status": "active",
        "endpoints": [
            "/api/status",
            "/api/agents",
            "/api/command",
            "/api/agents/create"
        ]
    }

@app.get("/api/status")
def get_status():
    return {
        "capital": {"initial": 10000, "current": 10042, "change": 42, "change_percent": 0.42},
        "trades": {"total": 1, "winning": 1, "losing": 0, "win_rate": 100},
        "positions": [],
        "prices": {"BTC": 67843, "ETH": 2032},
        "agents": len(agents),
        "last_update": datetime.now().isoformat()
    }

@app.get("/api/agents")
def get_agents():
    return {"agents": list(agents.values()), "count": len(agents)}

@app.post("/api/agents/create")
def create_agent(request: AgentCreateRequest):
    agent_id = f"agent-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    new_agent = {
        "id": agent_id,
        "name": request.name,
        "type": request.type,
        "status": "idle",
        "created_at": datetime.now().isoformat(),
        "last_activity": datetime.now().isoformat()
    }
    agents[agent_id] = new_agent
    
    # 실제 에이전트 생성 명령 실행
    command_queue.append({
        "type": "create_agent",
        "agent_id": agent_id,
        "name": request.name,
        "created_at": datetime.now().isoformat()
    })
    
    return {"success": True, "agent": new_agent}

@app.post("/api/command")
def execute_command(request: CommandRequest):
    command_id = f"cmd-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # 명령 큐에 추가
    cmd = {
        "id": command_id,
        "command": request.command,
        "agent_id": request.agent_id,
        "params": request.params,
        "status": "queued",
        "created_at": datetime.now().isoformat()
    }
    command_queue.append(cmd)
    
    # 명령별 처리
    result = process_command(request.command, request.agent_id, request.params)
    
    return {
        "success": True,
        "command_id": command_id,
        "result": result,
        "executed_at": datetime.now().isoformat()
    }

def process_command(command: str, agent_id: Optional[str], params: Optional[Dict]):
    """명령 처리"""
    if command == "analyze":
        return {
            "symbol": params.get("symbol", "ETH"),
            "price": 2032,
            "signal": "hold",
            "confidence": 0.75,
            "recommendation": "관망"
        }
    elif command == "trade":
        return {
            "action": "simulated",
            "symbol": params.get("symbol", "ETH"),
            "direction": "long",
            "leverage": 5
        }
    elif command == "positions":
        return {"positions": [], "count": 0}
    elif command == "status":
        return get_status()
    elif command == "pause":
        if agent_id and agent_id in agents:
            agents[agent_id]["status"] = "paused"
            return {"agent": agent_id, "status": "paused"}
    elif command == "restart":
        if agent_id and agent_id in agents:
            agents[agent_id]["status"] = "running"
            return {"agent": agent_id, "status": "running"}
    
    return {"message": f"Command {command} executed"}

@app.get("/api/analyze/{symbol}")
def analyze_symbol(symbol: str):
    return {
        "symbol": symbol.upper(),
        "timestamp": datetime.now().isoformat(),
        "price": 2032 if symbol.upper() == "ETH" else 67843,
        "signal": "hold",
        "confidence": 0.75,
        "recommendation": "관망"
    }

@app.get("/api/positions")
def get_positions():
    return {"positions": [], "count": 0}

@app.get("/api/trades")
def get_trades():
    return {"trades": [], "total": 0}

@app.get("/api/commands")
def get_commands():
    return {"commands": command_queue[-10:], "count": len(command_queue)}
