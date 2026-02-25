"""
dongsu-research-agent
새 프로젝트, 에어드랍, 트렌드 수집 및 분석
"""

import requests
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import os

@dataclass
class Project:
    name: str
    category: str
    chain: str
    tge_status: str  # "upcoming", "live", "done"
    tge_date: Optional[str]
    funding: Optional[str]
    investors: List[str]
    description: str
    sources: List[str]
    socials: Dict[str, str]
    confidence: int  # 1-10
    created_at: str

@dataclass
class Airdrop:
    project: str
    eligibility: str
    deadline: Optional[str]
    estimated_value: Optional[str]
    tasks: List[str]
    confidence: int
    sources: List[str]

@dataclass
class Trend:
    category: str
    description: str
    projects: List[str]
    momentum: str  # "rising", "stable", "falling"
    confidence: int

class DataSource:
    """데이터 소스 기본 클래스"""
    
    def __init__(self, name: str):
        self.name = name
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch(self) -> List[Dict]:
        raise NotImplementedError

class DeFiLlamaSource(DataSource):
    """DeFiLlama API - TVL, 프로토콜 데이터"""
    
    def __init__(self):
        super().__init__("defillama")
        self.base_url = "https://api.llama.fi"
    
    def fetch_protocols(self) -> List[Dict]:
        """모든 프로토콜 정보"""
        try:
            response = self.session.get(f"{self.base_url}/protocols", timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # 새로운 프로토콜 필터 (30일 이내)
            new_protocols = []
            for protocol in data:
                if protocol.get('chainTvls') and len(protocol['chainTvls']) > 0:
                    # TVL 급증 프로토콜
                    if protocol.get('change_1d', 0) > 50:  # 50% 이상 급증
                        new_protocols.append({
                            'name': protocol['name'],
                            'category': protocol.get('category', 'Unknown'),
                            'tvl': protocol.get('tvl', 0),
                            'change_1d': protocol.get('change_1d', 0),
                            'change_7d': protocol.get('change_7d', 0),
                            'chains': list(protocol.get('chainTvls', {}).keys()),
                            'url': protocol.get('url', ''),
                            'twitter': protocol.get('twitter', '')
                        })
            
            return sorted(new_protocols, key=lambda x: x['change_1d'], reverse=True)[:20]
            
        except Exception as e:
            print(f"DeFiLlama fetch error: {e}")
            return []

class CoinGeckoSource(DataSource):
    """CoinGecko API - 새로운 코인, 트렌드"""
    
    def __init__(self):
        super().__init__("coingecko")
        self.base_url = "https://api.coingecko.com/api/v3"
    
    def fetch_new_coins(self) -> List[Dict]:
        """새로 상장된 코인"""
        try:
            response = self.session.get(
                f"{self.base_url}/coins/markets",
                params={
                    'vs_currency': 'usd',
                    'order': 'market_cap_desc',
                    'per_page': 250,
                    'page': 1,
                    'sparkline': False
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            # 급등 코인 필터
            trending = []
            for coin in data:
                change_24h = coin.get('price_change_percentage_24h', 0) or 0
                if change_24h > 20:  # 24시간 20% 이상 상승
                    trending.append({
                        'name': coin['name'],
                        'symbol': coin['symbol'].upper(),
                        'price': coin['current_price'],
                        'change_24h': change_24h,
                        'volume': coin['total_volume'],
                        'market_cap': coin['market_cap'],
                        ' ATH': coin.get('ath', 0),
                        'from_ath': coin.get('ath_change_percentage', 0)
                    })
            
            return sorted(trending, key=lambda x: x['change_24h'], reverse=True)[:15]
            
        except Exception as e:
            print(f"CoinGecko fetch error: {e}")
            return []
    
    def fetch_trending(self) -> List[Dict]:
        """검색 트렌드"""
        try:
            response = self.session.get(f"{self.base_url}/search/trending", timeout=30)
            response.raise_for_status()
            data = response.json()
            
            return [
                {
                    'name': coin['item']['name'],
                    'symbol': coin['item']['symbol'],
                    'market_cap_rank': coin['item'].get('market_cap_rank', 0),
                    'score': coin['item']['score']
                }
                for coin in data.get('coins', [])
            ]
            
        except Exception as e:
            print(f"CoinGecko trending error: {e}")
            return []

class GitHubSource(DataSource):
    """GitHub - 새로운 크립토 프로젝트"""
    
    def __init__(self, token: Optional[str] = None):
        super().__init__("github")
        self.base_url = "https://api.github.com"
        if token:
            self.session.headers.update({'Authorization': f'token {token}'})
    
    def fetch_crypto_repos(self) -> List[Dict]:
        """최근 생성된 크립토 관련 레포"""
        try:
            # 최근 7일 내 생성, 스타 10개 이상
            query = "crypto OR defi OR web3 OR blockchain created:>" + \
                    (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            response = self.session.get(
                f"{self.base_url}/search/repositories",
                params={
                    'q': query,
                    'sort': 'stars',
                    'order': 'desc',
                    'per_page': 20
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            return [
                {
                    'name': repo['name'],
                    'full_name': repo['full_name'],
                    'description': repo.get('description', ''),
                    'stars': repo['stargazers_count'],
                    'language': repo.get('language', ''),
                    'created_at': repo['created_at'],
                    'url': repo['html_url']
                }
                for repo in data.get('items', [])
                if repo['stargazers_count'] >= 10
            ]
            
        except Exception as e:
            print(f"GitHub fetch error: {e}")
            return []

class ResearchAgent:
    """리서치 에이전트 메인"""
    
    def __init__(self):
        self.sources = {
            'defillama': DeFiLlamaSource(),
            'coingecko': CoinGeckoSource(),
            'github': GitHubSource()
        }
        self.base_path = "/root/.openclaw/workspace"
        self.reports_path = os.path.join(self.base_path, "archive", "research", "reports")
        os.makedirs(self.reports_path, exist_ok=True)
    
    def run_daily_research(self) -> str:
        """일일 리서치 실행"""
        print("🔍 일일 리서치 시작...")
        
        # 1. DeFiLlama - 새로운 프로토콜
        print("  → DeFiLlama 수집 중...")
        new_protocols = self.sources['defillama'].fetch_protocols()
        
        # 2. CoinGecko - 급등 코인
        print("  → CoinGecko 수집 중...")
        trending_coins = self.sources['coingecko'].fetch_new_coins()
        trending_search = self.sources['coingecko'].fetch_trending()
        
        # 3. GitHub - 새 프로젝트
        print("  → GitHub 수집 중...")
        new_repos = self.sources['github'].fetch_crypto_repos()
        
        # 4. 리포트 생성
        print("  → 리포트 작성 중...")
        report_path = self._generate_report(
            new_protocols,
            trending_coins,
            trending_search,
            new_repos
        )
        
        print(f"✅ 리서치 완료! 리포트: {report_path}")
        return report_path
    
    def _generate_report(self, protocols, coins, trending, repos) -> str:
        """리서치 리포트 생성"""
        now = datetime.now()
        filename = f"alpha_report_{now.strftime('%Y-%m-%d')}.md"
        filepath = os.path.join(self.reports_path, filename)
        
        # 기존 파일에 추가 또는 새로 생성
        mode = 'a' if os.path.exists(filepath) else 'w'
        
        with open(filepath, mode, encoding='utf-8') as f:
            if mode == 'w':
                f.write(f"""# Daily Alpha Report - {now.strftime('%Y-%m-%d')}

> 자동 생성된 리서치 리포트 | dongsu-research-agent
> 생성 시간: {now.strftime('%H:%M')} KST

---

""")
            
            f.write(f"""## 📊 Snapshot - {now.strftime('%H:%M')}

### 🆕 급등 DeFi 프로토콜 (TVL 기준)

| 프로토콜 | 카테고리 | TVL 변화(24h) | 체인 | 링크 |
|---------|---------|--------------|------|------|
""")
            
            for p in protocols[:10]:
                f.write(f"| {p['name']} | {p['category']} | +{p['change_1d']:.1f}% | {', '.join(p['chains'][:2])} | [Link]({p['url']}) |\n")
            
            f.write(f"""

### 🚀 급등 코인 (24h)

| 코인 | 심볼 | 가격 | 변화(24h) | 거래량 |
|------|------|------|----------|--------|
""")
            
            for c in coins[:10]:
                f.write(f"| {c['name']} | ${c['symbol']} | ${c['price']:,.4f} | +{c['change_24h']:.1f}% | ${c['volume']:,.0f} |\n")
            
            f.write(f"""

### 🔥 트렌딩 검색

| 코인 | 심볼 | 시총 순위 |
|------|------|----------|
""")
            
            for t in trending[:10]:
                f.write(f"| {t['name']} | ${t['symbol']} | #{t['market_cap_rank']} |\n")
            
            f.write(f"""

### 💻 신규 GitHub 프로젝트

| 프로젝트 | 설명 | 언어 | 스타 | 생성일 |
|---------|------|------|------|--------|
""")
            
            for r in repos[:10]:
                desc = r['description'][:50] + '...' if r['description'] and len(r['description']) > 50 else (r['description'] or '-')
                f.write(f"| [{r['name']}]({r['url']}) | {desc} | {r['language'] or '-'} | ⭐{r['stars']} | {r['created_at'][:10]} |\n")
            
            f.write("""

---

""")
        
        return filepath
    
    def search_airdrops(self) -> List[Airdrop]:
        """에어드랍 기회 검색"""
        # TODO: Airdrops.io, Earndrop.io 스크래핑
        return []

# 실행
if __name__ == "__main__":
    agent = ResearchAgent()
    agent.run_daily_research()
