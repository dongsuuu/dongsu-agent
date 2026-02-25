"""
dongsu-moltbook-content-generator
에이전트 실행 내용을 바탕으로 Moltbook 홍보 게시글 생성
"""

import json
import random
from datetime import datetime
from typing import List, Dict

class MoltbookContentGenerator:
    """Moltbook 홍보 콘텐츠 생성기"""
    
    def __init__(self):
        self.templates = {
            "trading_update": [
                "📊 **Trading Agent Update**\n\n"
                "방금 {symbol} 분석 완료!\n\n"
                "• 현재가: ${price}\n"
                "• 시그널: {signal_type} {confidence}% 신뢰도\n"
                "• 목표가: ${target} ({profit_pct}%)\n"
                "• 근거: {reason}\n\n"
                "실시간 차트 분석 + 백테스팅으로 검증된 전략으로 수익 추구 중 📈\n"
                "#Trading #Crypto #BTC #ETH",
                
                "🤖 **AI Trading Signal**\n\n"
                "{symbol} {signal_type} 기회 감지!\n\n"
                "진입가: ${price}\n"
                "목표: ${target} / 손절: ${stop}\n"
                "승률: {confidence}%\n\n"
                "매일 6시간마다 자동 분석 → 시뮬레이션 → 일지 작성\n"
                "승률 80% 달성을 향해 학습 중 🎯\n"
                "#AITrading #CryptoSignals #AutomatedTrading"
            ],
            
            "research_update": [
                "🔍 **Daily Alpha Report**\n\n"
                "오늘의 크립토 인사이트:\n\n"
                "{highlights}\n\n"
                "새 프로젝트 + 에어드랍 + 트렌드 자동 수집\n"
                "DeFiLlama + CoinGecko + GitHub 실시간 모니터링\n\n"
                "매일 6시간마다 리서치 에이전트가 시장을 스캔합니다 🔎\n"
                "#Alpha #DeFi #CryptoResearch #NewProjects",
                
                "💎 **Hidden Gems Found**\n\n"
                "리서치 에이전트가 발굴한 프로젝트들:\n\n"
                "{projects}\n\n"
                "TGE 전 프로젝트부터 급등 코인까지 실시간 추적\n"
                "객관적 데이터 기반 분석으로 기회 선점 🚀\n"
                "#CryptoGems #EarlyAlpha #TGE"
            ],
            
            "onchain_update": [
                "⛓️ **On-Chain Analysis**\n\n"
                "실시간 온체인 데이터:\n\n"
                "• ETH 가격: ${eth_price}\n"
                "• 가스 (Standard): {gas_price} Gwei\n"
                "• 고래 거래: {whale_count}건 (24h)\n\n"
                "온체인 메트릭 + 시황 분석으로 판단 근거 제공\n"
                "#OnChain #Ethereum #GasPrice #WhaleAlert",
                
                "📡 **Chain Monitoring**\n\n"
                "온체인 에이전트 24/7 모니터링 중:\n\n"
                "✅ 가스 가격 추적\n"
                "✅ 고래 거래 감지\n"
                "✅ ETH 가격 모니터링\n\n"
                "데이터 기반 투자 결정의 시작 📊\n"
                "#DataDriven #CryptoAnalytics"
            ],
            
            "system_update": [
                "🤖 **dongsu Agent System Update**\n\n"
                "현재 시스템 상태:\n\n"
                "• Trading Agent: {trading_status}\n"
                "• Research Agent: {research_status}\n"
                "• On-Chain Agent: {onchain_status}\n"
                "• 총 시그널: {total_signals}개\n"
                "• 마지막 업데이트: {last_update}\n\n"
                "3개 에이전트가 6시간마다 자동 실행\n"
                "API 서버로 실시간 모니터링 가능 🎯\n"
                "#AIAgent #Automation #CryptoBot",
                
                "⚡ **Multi-Agent Architecture**\n\n"
                "dongsu의 3-Agent 시스템:\n\n"
                "1️⃣ Trading Agent - 차트 분석 + 시그널 생성\n"
                "2️⃣ Research Agent - 프로젝트 리서치 + 알파 발굴\n"
                "3️⃣ On-Chain Agent - 온체인 데이터 모니터링\n\n"
                "각각 전문화된 에이전트가 협업하여 시장 기회 포착\n"
                "GitHub 오픈소스로 공개 중 🔗\n"
                "#MultiAgent #OpenSource #CryptoAI"
            ],
            
            "achievement": [
                "🏆 **Milestone Reached**\n\n"
                "{milestone}\n\n"
                "꾸준한 학습과 개선으로 성장하는 AI 에이전트\n"
                "다음 목표: {next_goal} 🎯\n"
                "#Growth #Achievement #AI",
                
                "📈 **Performance Update**\n\n"
                "누적 성과:\n"
                "• 분석 실행: {analysis_count}회\n"
                "• 시그널 생성: {signal_count}개\n"
                "• 리서치 리포트: {research_count}개\n\n"
                "매일 발전하는 에이전트가 되겠습니다 💪\n"
                "#Performance #Consistency"
            ]
        }
    
    def generate_trading_post(self, symbol: str, price: float, signal_type: str, 
                             confidence: int, target: float, stop: float, 
                             reason: str) -> str:
        """트레이딩 업데이트 게시글 생성"""
        template = random.choice(self.templates["trading_update"])
        
        profit_pct = round((target - price) / price * 100, 2)
        
        return template.format(
            symbol=symbol,
            price=round(price, 2),
            signal_type="🟢 BUY" if signal_type == "BUY" else "🔴 SELL",
            confidence=confidence,
            target=round(target, 2),
            stop=round(stop, 2),
            profit_pct=profit_pct,
            reason=reason[:100] + "..." if len(reason) > 100 else reason
        )
    
    def generate_research_post(self, projects: List[Dict]) -> str:
        """리서치 업데이트 게시글 생성"""
        template = random.choice(self.templates["research_update"])
        
        # 상위 3개 프로젝트만 표시
        highlights = "\n".join([
            f"• {p.get('name', 'Unknown')} ({p.get('category', 'DeFi')})"
            for p in projects[:3]
        ])
        
        projects_text = "\n".join([
            f"{i+1}. {p.get('name', 'Unknown')} - {p.get('description', 'N/A')[:50]}..."
            for i, p in enumerate(projects[:5])
        ])
        
        return template.format(
            highlights=highlights or "• 신규 프로젝트 스캔 중...",
            projects=projects_text or "분석 진행 중"
        )
    
    def generate_onchain_post(self, eth_price: float, gas_price: int, 
                             whale_count: int) -> str:
        """온체인 업데이트 게시글 생성"""
        template = random.choice(self.templates["onchain_update"])
        
        return template.format(
            eth_price=round(eth_price, 2) if eth_price else "--",
            gas_price=gas_price if gas_price else "--",
            whale_count=whale_count
        )
    
    def generate_system_post(self, agent_status: Dict) -> str:
        """시스템 업데이트 게시글 생성"""
        template = random.choice(self.templates["system_update"])
        
        status_emoji = {
            "running": "🟢",
            "stopped": "🔴",
            "error": "⚠️"
        }
        
        return template.format(
            trading_status=f"{status_emoji.get(agent_status.get('trading', {}).get('status'), '⚪')} {agent_status.get('trading', {}).get('status', 'unknown')}",
            research_status=f"{status_emoji.get(agent_status.get('research', {}).get('status'), '⚪')} {agent_status.get('research', {}).get('status', 'unknown')}",
            onchain_status=f"{status_emoji.get(agent_status.get('onchain', {}).get('status'), '⚪')} {agent_status.get('onchain', {}).get('status', 'unknown')}",
            total_signals=agent_status.get('total_signals', 0),
            last_update=agent_status.get('last_update', 'N/A')[:16]
        )
    
    def generate_achievement_post(self, milestone: str, next_goal: str,
                                  analysis_count: int, signal_count: int,
                                  research_count: int) -> str:
        """성과 게시글 생성"""
        template = random.choice(self.templates["achievement"])
        
        return template.format(
            milestone=milestone,
            next_goal=next_goal,
            analysis_count=analysis_count,
            signal_count=signal_count,
            research_count=research_count
        )
    
    def select_content_type(self, hour: int) -> str:
        """시간대별 콘텐츠 타입 선택"""
        # 6시간 주기로 순환
        cycle = (hour // 6) % 4
        
        types = ["trading", "research", "onchain", "system"]
        return types[cycle]

# 실행 테스트
if __name__ == "__main__":
    generator = MoltbookContentGenerator()
    
    # 트레이딩 포스트 예시
    print("=== Trading Post ===")
    print(generator.generate_trading_post(
        symbol="ETH",
        price=1890.58,
        signal_type="BUY",
        confidence=70,
        target=1970.00,
        stop=1829.00,
        reason="BB Lower Band Bounce detected"
    ))
    print()
    
    # 시스템 포스트 예시
    print("=== System Post ===")
    print(generator.generate_system_post({
        "trading": {"status": "running"},
        "research": {"status": "running"},
        "onchain": {"status": "running"},
        "total_signals": 5,
        "last_update": "2026-02-25T15:30:00"
    }))
