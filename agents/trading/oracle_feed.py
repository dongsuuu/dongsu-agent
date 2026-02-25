"""
dongsu-oracle-price-feed
Chainlink + Pyth 오라클 통합 가격 피드
"""

import requests
import json
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PriceData:
    symbol: str
    price: float
    timestamp: int
    source: str
    confidence: Optional[float] = None
    sources_count: Optional[int] = None

class ChainlinkOracle:
    """Chainlink Price Feed"""
    
    # Chainlink Price Feed 컨트랙트 주소 (Ethereum Mainnet)
    PRICE_FEEDS = {
        "ETH-USD": "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419",
        "BTC-USD": "0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c",
        "LINK-USD": "0x2c1d072e956AFFC0D435Cb7AC38EF18d24d9127c",
        "DAI-USD": "0xAed0c38402a5d19df6E4c03F4E2DceD6e29c1ee9",
        "USDC-USD": "0x8fFfFfd4AfB6115b954Bd326cbe7B4BA576818f6",
        "USDT-USD": "0x3E7d1eAB13ad0104d2750B8863b489D65364e32D",
    }
    
    def __init__(self):
        self.session = requests.Session()
        # Chainlink Market API
        self.base_url = "https://api.chain.link/v1"
    
    def get_price(self, pair: str = "ETH-USD") -> Optional[PriceData]:
        """Chainlink에서 가격 조회"""
        try:
            # Chainlink Market 페이지 스크래핑 또는 API 사용
            # 공식 API가 없으므로 대체 방법 사용
            
            # 방법 1: Chainlink Data Streams API (유료)
            # 방법 2: The Graph로 컨트랙트 직접 쿼리
            # 방법 3: Etherscan API로 컨트랙트 읽기
            
            # 여기서는 Etherscan API 예시
            contract = self.PRICE_FEEDS.get(pair)
            if not contract:
                return None
            
            # Etherscan API로 latestRoundData 호출
            # 실제 구현 시 API 키 필요
            
            # 임시: 다른 오라클 사용
            return None
            
        except Exception as e:
            print(f"Chainlink error: {e}")
            return None

class PythOracle:
    """Pyth Network Price Feed"""
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://hermes.pyth.network"
    
    def get_price(self, symbol: str = "Crypto.ETH/USD") -> Optional[PriceData]:
        """Pyth에서 가격 조회 - v2 API 사용"""
        try:
            # Pyth v2 API - price IDs 사용
            # 주요 심볼의 price ID 매핑
            PRICE_IDS = {
                "Crypto.ETH/USD": "0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace",
                "Crypto.BTC/USD": "0xe62df6c8b4a85fe1f67dab53838813a513f50e13e5af36e3a6ac4e82c9e1b7b5",
                "Crypto.SOL/USD": "0xef0d8b6fda2ceba41da15d4095d1da392a0d2f8ed0c6c7bc0f4cf2b1e6e5e5a5",
            }
            
            price_id = PRICE_IDS.get(symbol)
            if not price_id:
                return None
            
            url = f"{self.base_url}/v2/updates/price/latest"
            params = {"ids[]": price_id}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # 파싱
            parsed = data.get("parsed", [])
            if not parsed:
                return None
            
            price_data = parsed[0].get("price", {})
            raw_price = int(price_data.get("price", 0))
            exponent = int(price_data.get("expo", -8))
            price = raw_price * (10 ** exponent)
            
            return PriceData(
                symbol=symbol,
                price=price,
                timestamp=price_data.get("publish_time", 0) * 1000,
                source="Pyth",
                confidence=int(price_data.get("conf", 0)) * (10 ** exponent),
                sources_count=None
            )
            
        except Exception as e:
            print(f"Pyth error: {e}")
            return None
    
    def get_multiple_prices(self, symbols: List[str]) -> Dict[str, PriceData]:
        """여러 심볼의 가격 조회"""
        results = {}
        for symbol in symbols:
            price = self.get_price(symbol)
            if price:
                results[symbol] = price
        return results

class CoinGeckoOracle:
    """CoinGecko API (묣 오라클 대안)"""
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://api.coingecko.com/api/v3"
    
    def get_price(self, ids: List[str], vs_currencies: List[str] = ["usd"]) -> Optional[Dict]:
        """CoinGecko에서 가격 조회"""
        try:
            url = f"{self.base_url}/simple/price"
            params = {
                "ids": ",".join(ids),
                "vs_currencies": ",".join(vs_currencies),
                "include_24hr_change": "true",
                "include_market_cap": "true",
                "include_24hr_vol": "true"
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"CoinGecko error: {e}")
            return None

class MultiOracleAggregator:
    """다중 오라클 집계기"""
    
    def __init__(self):
        self.pyth = PythOracle()
        self.coingecko = CoinGeckoOracle()
        # self.chainlink = ChainlinkOracle()  # API 키 필요
    
    def get_aggregated_price(self, symbol: str) -> Optional[PriceData]:
        """여러 오라클에서 가격을 가져와 중간값 사용"""
        prices = []
        
        # 1. Pyth 시도
        pyth_price = self.pyth.get_price(f"Crypto.{symbol}/USD")
        if pyth_price:
            prices.append(pyth_price)
        
        # 2. CoinGecko 시도
        coin_id = self._symbol_to_coingecko_id(symbol)
        cg_data = self.coingecko.get_price([coin_id])
        if cg_data and coin_id in cg_data:
            prices.append(PriceData(
                symbol=symbol,
                price=cg_data[coin_id]["usd"],
                timestamp=int(datetime.now().timestamp() * 1000),
                source="CoinGecko",
                confidence=None,
                sources_count=None
            ))
        
        # 중간값 계산
        if len(prices) == 0:
            return None
        elif len(prices) == 1:
            return prices[0]
        else:
            # 여러 소스에서 가격 집계
            avg_price = sum(p.price for p in prices) / len(prices)
            return PriceData(
                symbol=symbol,
                price=avg_price,
                timestamp=int(datetime.now().timestamp() * 1000),
                source=f"Aggregated({len(prices)})",
                confidence=min(p.confidence or 0 for p in prices) if any(p.confidence for p in prices) else None,
                sources_count=len(prices)
            )
    
    def _symbol_to_coingecko_id(self, symbol: str) -> str:
        """심볼을 CoinGecko ID로 변환"""
        mapping = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "SOL": "solana",
            "LINK": "chainlink",
            "DAI": "dai",
            "USDC": "usd-coin",
            "USDT": "tether",
        }
        return mapping.get(symbol.upper(), symbol.lower())
    
    def compare_oracles(self, symbol: str) -> Dict:
        """여러 오라클의 가격 비교"""
        results = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "sources": {}
        }
        
        # Pyth
        pyth = self.pyth.get_price(f"Crypto.{symbol}/USD")
        if pyth:
            results["sources"]["Pyth"] = {
                "price": pyth.price,
                "confidence": pyth.confidence,
                "timestamp": pyth.timestamp
            }
        
        # CoinGecko
        coin_id = self._symbol_to_coingecko_id(symbol)
        cg = self.coingecko.get_price([coin_id])
        if cg and coin_id in cg:
            results["sources"]["CoinGecko"] = {
                "price": cg[coin_id]["usd"],
                "change_24h": cg[coin_id].get("usd_24h_change")
            }
        
        # 편차 계산
        if len(results["sources"]) >= 2:
            prices = [s["price"] for s in results["sources"].values()]
            max_price = max(prices)
            min_price = min(prices)
            deviation = ((max_price - min_price) / min_price) * 100
            results["deviation_percent"] = round(deviation, 4)
        
        return results

# 사용 예시
if __name__ == "__main__":
    aggregator = MultiOracleAggregator()
    
    print("=== Pyth Oracle ===")
    pyth = PythOracle()
    eth_price = pyth.get_price("Crypto.ETH/USD")
    if eth_price:
        print(f"ETH: ${eth_price.price:.2f} (confidence: {eth_price.confidence})")
    
    print("\n=== Aggregated Price ===")
    agg = aggregator.get_aggregated_price("ETH")
    if agg:
        print(f"ETH: ${agg.price:.2f} (sources: {agg.source})")
    
    print("\n=== Oracle Comparison ===")
    comparison = aggregator.compare_oracles("ETH")
    print(json.dumps(comparison, indent=2))
