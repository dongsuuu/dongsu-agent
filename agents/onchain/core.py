"""
dongsu-onchain-agent
온체인 데이터 분석, 알림, 시황 분석
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import os

@dataclass
class WhaleAlert:
    symbol: str
    amount: float
    from_address: str
    to_address: str
    tx_hash: str
    timestamp: int
    alert_type: str  # "exchange_inflow", "exchange_outflow", "large_transfer"

@dataclass
class OnChainMetric:
    name: str
    value: float
    change_24h: float
    trend: str  # "up", "down", "stable"
    timestamp: int

class DuneAnalytics:
    """Dune Analytics API (Free tier)"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.dune.com/api/v1"
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({'X-Dune-API-Key': api_key})
    
    def execute_query(self, query_id: int) -> Optional[Dict]:
        """쿼리 실행"""
        if not self.api_key:
            print("Dune API key not provided")
            return None
        
        try:
            # 쿼리 실행
            response = self.session.post(
                f"{self.base_url}/query/{query_id}/execute",
                timeout=30
            )
            response.raise_for_status()
            execution = response.json()
            
            # 결과 대기 및 조회
            execution_id = execution['execution_id']
            # TODO: 결과 polling
            
            return execution
            
        except Exception as e:
            print(f"Dune query error: {e}")
            return None

class EtherscanAPI:
    """Etherscan API - 온체인 데이터"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.etherscan.io/api"
        self.session = requests.Session()
    
    def get_gas_price(self) -> Optional[Dict]:
        """가스 가격 조회"""
        try:
            params = {
                'module': 'gastracker',
                'action': 'gasoracle',
                'apikey': self.api_key
            }
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == '1':
                return {
                    'safe_low': int(data['result']['SafeGasPrice']),
                    'standard': int(data['result']['ProposeGasPrice']),
                    'fast': int(data['result']['FastGasPrice']),
                    'timestamp': int(datetime.now().timestamp())
                }
            return None
            
        except Exception as e:
            print(f"Etherscan gas error: {e}")
            return None
    
    def get_eth_price(self) -> Optional[float]:
        """ETH 가격 조회 - Binance 사용"""
        try:
            response = self.session.get(
                "https://api.binance.com/api/v3/ticker/price",
                params={'symbol': 'ETHUSDT'},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return float(data['price'])
        except Exception as e:
            print(f"ETH price error: {e}")
            return None

class GlassnodeAPI:
    """Glassnode API - 고급 온체인 메트릭"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.glassnode.com/v1"
        self.session = requests.Session()
    
    def get_metric(self, metric: str, asset: str = "BTC") -> Optional[List]:
        """온체인 메트릭 조회"""
        if not self.api_key:
            return None
        
        try:
            response = self.session.get(
                f"{self.base_url}/metrics/{metric}",
                params={
                    'a': asset,
                    'api_key': self.api_key
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"Glassnode error: {e}")
            return None

class WhaleWatcher:
    """고래 거래 모니터링"""
    
    def __init__(self):
        self.session = requests.Session()
        self.thresholds = {
            'BTC': 100,      # 100 BTC 이상
            'ETH': 1000,     # 1000 ETH 이상
            'USDT': 1000000  # 100만 USDT 이상
        }
    
    def check_whale_alerts(self) -> List[WhaleAlert]:
        """고래 알림 체크 (Public API 활용)"""
        # TODO: Whale Alert API 또는 블록 익스플로러 활용
        return []

class OnChainAgent:
    """온체인 에이전트 메인"""
    
    def __init__(self):
        self.etherscan = EtherscanAPI()
        self.glassnode = GlassnodeAPI()
        self.dune = DuneAnalytics()
        self.whale = WhaleWatcher()
        
        self.base_path = "/root/.openclaw/workspace"
        self.reports_path = os.path.join(self.base_path, "archive", "onchain", "reports")
        os.makedirs(self.reports_path, exist_ok=True)
    
    def run_analysis(self) -> str:
        """온체인 분석 실행"""
        print("⛓️ 온체인 분석 시작...")
        
        # 1. 가스 가격
        print("  → 가스 가격 조회...")
        gas = self.etherscan.get_gas_price()
        
        # 2. ETH 가격
        print("  → ETH 가격 조회...")
        eth_price = self.etherscan.get_eth_price()
        
        # 3. 고래 알림
        print("  → 고래 거래 모니터링...")
        whale_alerts = self.whale.check_whale_alerts()
        
        # 4. 리포트 생성
        print("  → 리포트 작성...")
        report_path = self._generate_report(gas, eth_price, whale_alerts)
        
        print(f"✅ 온체인 분석 완료! 리포트: {report_path}")
        return report_path
    
    def _generate_report(self, gas: Optional[Dict], eth_price: Optional[float], whales: List) -> str:
        """온체인 리포트 생성"""
        now = datetime.now()
        filename = f"onchain_report_{now.strftime('%Y-%m-%d')}.md"
        filepath = os.path.join(self.reports_path, filename)
        
        mode = 'a' if os.path.exists(filepath) else 'w'
        
        with open(filepath, mode, encoding='utf-8') as f:
            if mode == 'w':
                f.write(f"""# On-Chain Analysis Report - {now.strftime('%Y-%m-%d')}

> 자동 생성된 온체인 리포트 | dongsu-onchain-agent

---

""")
            
            f.write(f"""## ⛓️ Snapshot - {now.strftime('%H:%M')} KST

### ⛽ 가스 가격 (Ethereum)

""")
            
            if gas:
                f.write(f"""| 타입 | 가격 (Gwei) |
|------|------------|
| Safe Low | {gas['safe_low']} |
| Standard | {gas['standard']} |
| Fast | {gas['fast']} |

""")
            else:
                f.write("*가스 가격 조회 실패*\n\n")
            
            f.write(f"""### 💰 ETH 가격

""")
            
            if eth_price:
                f.write(f"**현재가:** ${eth_price:,.2f}\n\n")
            else:
                f.write("*ETH 가격 조회 실패*\n\n")
            
            f.write(f"""### 🐋 고래 거래 알림

| 심볼 | 수량 | 타입 | 시간 |
|------|------|------|------|
""")
            
            if whales:
                for w in whales[:10]:
                    f.write(f"| {w.symbol} | {w.amount:,.2f} | {w.alert_type} | {datetime.fromtimestamp(w.timestamp).strftime('%H:%M')} |\n")
            else:
                f.write("| - | - | - | - |\n")
            
            f.write("""

---

""")
        
        return filepath
    
    def get_quick_metrics(self) -> Dict:
        """빠른 메트릭 조회"""
        return {
            'gas': self.etherscan.get_gas_price(),
            'eth_price': self.etherscan.get_eth_price(),
            'timestamp': int(datetime.now().timestamp())
        }

# 실행
if __name__ == "__main__":
    agent = OnChainAgent()
    agent.run_analysis()
    
    # 빠른 메트릭
    metrics = agent.get_quick_metrics()
    print(f"\n📊 Quick Metrics:")
    print(f"  ETH: ${metrics['eth_price']:.2f}" if metrics['eth_price'] else "  ETH: N/A")
    if metrics['gas']:
        print(f"  Gas: {metrics['gas']['standard']} Gwei")
