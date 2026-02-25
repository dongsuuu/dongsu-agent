"""
dongsu-research-agent-v2
Dune Analytics + DeFiLlama + 다중 소스 연동 리서치 에이전트
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ProjectDiscovery:
    """발굴한 프로젝트 정보"""
    name: str
    category: str
    chain: str
    tge_status: str  # "upcoming", "live", "completed"
    airdrop_potential: bool
    metrics: Dict
    sources: List[str]
    discovered_at: datetime
    confidence: float

class DuneAnalyticsClient:
    """Dune Analytics API 클라이언트"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.dune.com/api/v1"
        self.session = requests.Session()
    
    def get_popular_queries(self) -> List[Dict]:
        """인기 쿼리 조회"""
        try:
            # Dune API는 인증 필요
            # 묣 티어: 10 API calls/month
            if not self.api_key:
                return []
            
            headers = {"X-Dune-API-Key": self.api_key}
            response = self.session.get(
                f"{self.base_url}/queries",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json().get("queries", [])
            
        except Exception as e:
            print(f"Dune API 오류: {e}")
            return []
    
    def execute_query(self, query_id: int) -> Optional[Dict]:
        """쿼리 실행"""
        try:
            if not self.api_key:
                return None
            
            headers = {"X-Dune-API-Key": self.api_key}
            
            # 쿼리 실행
            response = self.session.post(
                f"{self.base_url}/query/{query_id}/execute",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            execution_id = response.json().get("execution_id")
            
            # 결과 대기
            import time
            time.sleep(2)
            
            result = self.session.get(
                f"{self.base_url}/execution/{execution_id}/results",
                headers=headers,
                timeout=10
            )
            result.raise_for_status()
            return result.json()
            
        except Exception as e:
            print(f"쿼리 실행 오류: {e}")
            return None

class DeFiLlamaClient:
    """DeFiLlama API 클라이언트 (묣)"""
    
    def __init__(self):
        self.base_url = "https://api.llama.fi"
        self.session = requests.Session()
    
    def get_protocols(self) -> List[Dict]:
        """모든 프로토콜 정보"""
        try:
            response = self.session.get(
                f"{self.base_url}/protocols",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"DeFiLlama 오류: {e}")
            return []
    
    def get_tvl(self, protocol: str) -> Optional[float]:
        """특정 프로토콜 TVL"""
        try:
            response = self.session.get(
                f"{self.base_url}/tvl/{protocol}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"TVL 조회 오류: {e}")
            return None
    
    def get_new_protocols(self, days: int = 30) -> List[Dict]:
        """신규 프로토콜 발굴 - TVL 성장률 기반"""
        protocols = self.get_protocols()
        
        # TVL 상승세 있는 프로토콜 필터링
        rising_protocols = []
        
        for protocol in protocols:
            tvl = protocol.get("tvl", 0)
            change_7d = protocol.get("change_7d", 0)
            change_1d = protocol.get("change_1d", 0)
            
            # TVL $100K 이상, 7일 상승세 또는 1일 급등
            tvl = tvl or 0
            change_7d = change_7d or 0
            change_1d = change_1d or 0
            
            if tvl > 100_000 and (change_7d > 5 or change_1d > 10):
                rising_protocols.append({
                    "name": protocol.get("name"),
                    "category": protocol.get("category"),
                    "chain": protocol.get("chain"),
                    "tvl": tvl,
                    "change_1d": change_1d,
                    "change_7d": change_7d,
                    "url": protocol.get("url"),
                    "twitter": protocol.get("twitter"),
                    "description": protocol.get("description", "")[:100]
                })
        
        # TVL 높은 순 정렬
        rising_protocols.sort(key=lambda x: x.get("tvl", 0), reverse=True)
        return rising_protocols[:20]  # 상위 20개만

class CoinGeckoClient:
    """CoinGecko API 클라이언트 (묣)"""
    
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.session = requests.Session()
    
    def get_new_listings(self) -> List[Dict]:
        """신규 상장 코인"""
        try:
            response = self.session.get(
                f"{self.base_url}/coins/markets",
                params={
                    "vs_currency": "usd",
                    "order": "market_cap_desc",
                    "per_page": 100,
                    "page": 1
                },
                timeout=10
            )
            response.raise_for_status()
            
            coins = response.json()
            # 최근 상장된 코인 필터링 (ath_date 기준)
            new_coins = []
            for coin in coins:
                ath_date = coin.get("ath_date")
                if ath_date:
                    try:
                        ath = datetime.fromisoformat(ath_date.replace("Z", "+00:00"))
                        if (datetime.now(ath.tzinfo) - ath).days < 30:
                            new_coins.append(coin)
                    except:
                        continue
            
            return new_coins[:10]
            
        except Exception as e:
            print(f"CoinGecko 오류: {e}")
            return []

class ResearchAgent:
    """통합 리서치 에이전트"""
    
    def __init__(self, dune_api_key: Optional[str] = None):
        self.dune = DuneAnalyticsClient(dune_api_key)
        self.defillama = DeFiLlamaClient()
        self.coingecko = CoinGeckoClient()
        
        self.discovered_projects: List[ProjectDiscovery] = []
        self.reports: List[Dict] = []
    
    def discover_new_projects(self) -> List[ProjectDiscovery]:
        """신규 프로젝트 발굴"""
        print("🔍 신규 프로젝트 발굴 중...")
        
        discoveries = []
        
        # 1. DeFiLlama에서 신규 프로토콜
        new_protocols = self.defillama.get_new_protocols(days=30)
        for protocol in new_protocols:
            discovery = ProjectDiscovery(
                name=protocol.get("name", "Unknown"),
                category=protocol.get("category", "Unknown"),
                chain=protocol.get("chain", "Unknown"),
                tge_status="live" if protocol.get("tvl", 0) > 0 else "upcoming",
                airdrop_potential=self._assess_airdrop_potential(protocol),
                metrics={
                    "tvl": protocol.get("tvl"),
                    "change_1d": protocol.get("change_1d"),
                    "change_7d": protocol.get("change_7d")
                },
                sources=["defillama"],
                discovered_at=datetime.now(),
                confidence=0.7
            )
            discoveries.append(discovery)
        
        print(f"   ✅ {len(discoveries)}개 프로젝트 발굴")
        self.discovered_projects.extend(discoveries)
        return discoveries
    
    def _assess_airdrop_potential(self, protocol: Dict) -> bool:
        """에어드랍 가능성 평가"""
        # 휴리스틱: TVL 상승세 + 신규 프로토콜 = 에어드랍 가능성
        tvl = protocol.get("tvl", 0)
        change_7d = protocol.get("change_7d", 0)
        
        # TVL $1M 이상, 7일 상승세면 에어드랍 가능성 있음
        return tvl > 1_000_000 and change_7d > 0
    
    def generate_daily_report(self) -> Dict:
        """일일 리서치 리포트 생성"""
        print("📊 일일 리서치 리포트 생성 중...")
        
        # 새로운 프로젝트 발굴
        new_projects = self.discover_new_projects()
        
        # 에어드랍 가능 프로젝트 필터링
        airdrop_projects = [p for p in new_projects if p.airdrop_potential]
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_discovered": len(new_projects),
                "airdrop_potential": len(airdrop_projects),
                "high_confidence": len([p for p in new_projects if p.confidence >= 0.8])
            },
            "new_projects": [
                {
                    "name": p.name,
                    "category": p.category,
                    "chain": p.chain,
                    "tvl": p.metrics.get("tvl"),
                    "airdrop_potential": p.airdrop_potential,
                    "confidence": p.confidence
                }
                for p in new_projects[:10]  # 상위 10개만
            ],
            "airdrop_candidates": [
                {
                    "name": p.name,
                    "reason": f"TVL ${p.metrics.get('tvl', 0):,.0f}, 7일 변화 {p.metrics.get('change_7d', 0):+.2f}%"
                }
                for p in airdrop_projects[:5]
            ]
        }
        
        self.reports.append(report)
        
        # 리포트 저장
        self._save_report(report)
        
        return report
    
    def _save_report(self, report: Dict):
        """리포트 저장"""
        import os
        
        filename = f"/root/.openclaw/workspace/archive/research/report_{datetime.now().strftime('%Y-%m-%d')}.json"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"   💾 리포트 저장: {filename}")

# 실행
if __name__ == "__main__":
    agent = ResearchAgent()
    
    # 일일 리포트 생성
    report = agent.generate_daily_report()
    
    print("\n" + "="*60)
    print("📋 리서치 리포트 요약")
    print("="*60)
    print(f"발굴 프로젝트: {report['summary']['total_discovered']}개")
    print(f"에어드랍 후보: {report['summary']['airdrop_potential']}개")
    print(f"높은 신뢰도: {report['summary']['high_confidence']}개")
    
    if report['airdrop_candidates']:
        print("\n🎯 에어드랍 후보:")
        for candidate in report['airdrop_candidates']:
            print(f"   • {candidate['name']}: {candidate['reason']}")
