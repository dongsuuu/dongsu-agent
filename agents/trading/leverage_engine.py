"""
dongsu-leverage-trading-engine
레버리지 선물 트레이딩 + 동적 배율 판단 시스템
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import os

class LeverageLevel(Enum):
    """레버리지 레벨"""
    NONE = 1      # 확신 없음 - 진입 안함
    LOW = 5       # 애매함 - 5배
    HIGH = 10     # 확신 - 10배

@dataclass
class LeverageTrade:
    """레버리지 거래 기록"""
    id: str
    symbol: str
    direction: str  # "long" or "short"
    leverage: int   # 5 or 10
    entry_price: float
    entry_time: datetime
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    target_price: float = 0
    stop_loss: float = 0
    size: float = 0
    margin: float = 0  # 증거금
    status: str = "open"  # "open", "closed", "liquidated"
    pnl: float = 0
    pnl_percent: float = 0
    roe: float = 0  # Return on Equity (배율 적용 수익률)
    exit_reason: str = ""
    confidence: float = 0
    market_condition: str = ""

class LeverageTradingEngine:
    """레버리지 트레이딩 엔진 - 동적 배율 판단"""
    
    def __init__(self, initial_capital: float = 10000):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions: List[LeverageTrade] = []
        self.closed_trades: List[LeverageTrade] = []
        
        # 수수료 설정 (Binance Futures 기준)
        self.maker_fee = 0.0002  # 0.02%
        self.taker_fee = 0.0005  # 0.05%
        
        # 학습 데이터
        self.leverage_performance = {
            5: {"trades": 0, "wins": 0, "total_pnl": 0},
            10: {"trades": 0, "wins": 0, "total_pnl": 0}
        }
        
        # 시장 상황별 성과
        self.condition_performance = {}
    
    def calculate_leverage(self, confidence: float, risk_score: float,
                          market_volatility: float, trend_strength: float) -> Tuple[int, str]:
        """
        스스로 레버리지 배율 판단
        
        판단 기준:
        - confidence (신뢰도): 0.0 ~ 1.0
        - risk_score (리스크 점수): 0 ~ 10 (낮을수록 좋음)
        - market_volatility (변동성): 0.0 ~ 1.0 (낮을수록 좋음)
        - trend_strength (추세 강도): 0.0 ~ 1.0 (높을수록 좋음)
        """
        
        # 점수 계산 (0 ~ 100)
        score = 0
        reasons = []
        
        # 1. 신뢰도 (40% 가중치)
        if confidence >= 0.85:
            score += 40
            reasons.append(f"신뢰도 매우 높음 ({confidence*100:.0f}%)")
        elif confidence >= 0.70:
            score += 30
            reasons.append(f"신뢰도 높음 ({confidence*100:.0f}%)")
        elif confidence >= 0.60:
            score += 20
            reasons.append(f"신뢰도 보통 ({confidence*100:.0f}%)")
        else:
            score += 10
            reasons.append(f"신뢰도 낮음 ({confidence*100:.0f}%)")
        
        # 2. 리스크 점수 (30% 가중치)
        if risk_score <= 2:
            score += 30
            reasons.append(f"리스크 매우 낮음 ({risk_score}/10)")
        elif risk_score <= 4:
            score += 25
            reasons.append(f"리스크 낮음 ({risk_score}/10)")
        elif risk_score <= 6:
            score += 15
            reasons.append(f"리스크 보통 ({risk_score}/10)")
        else:
            score += 5
            reasons.append(f"리스크 높음 ({risk_score}/10)")
        
        # 3. 변동성 (15% 가중치)
        if market_volatility <= 0.3:
            score += 15
            reasons.append(f"변동성 낮음 ({market_volatility*100:.0f}%)")
        elif market_volatility <= 0.6:
            score += 10
            reasons.append(f"변동성 보통 ({market_volatility*100:.0f}%)")
        else:
            score += 5
            reasons.append(f"변동성 높음 ({market_volatility*100:.0f}%)")
        
        # 4. 추세 강도 (15% 가중치)
        if trend_strength >= 0.8:
            score += 15
            reasons.append(f"추세 매우 강함 ({trend_strength*100:.0f}%)")
        elif trend_strength >= 0.6:
            score += 10
            reasons.append(f"추세 강함 ({trend_strength*100:.0f}%)")
        else:
            score += 5
            reasons.append(f"추세 약함 ({trend_strength*100:.0f}%)")
        
        # 레버리지 결정
        if score >= 75:
            leverage = 10
            decision = f"🎯 10배 레버리지 결정 (점수: {score}/100)\n   " + "\n   ".join(reasons)
        elif score >= 50:
            leverage = 5
            decision = f"📊 5배 레버리지 결정 (점수: {score}/100)\n   " + "\n   ".join(reasons)
        else:
            leverage = 0
            decision = f"❌ 진입 보류 (점수: {score}/100)\n   " + "\n   ".join(reasons)
        
        return leverage, decision
    
    def open_position(self, symbol: str, direction: str, entry_price: float,
                     target_price: float, stop_loss: float,
                     confidence: float, market_condition: str,
                     risk_score: float = 5, volatility: float = 0.5,
                     trend_strength: float = 0.5) -> Optional[LeverageTrade]:
        """레버리지 포지션 진입"""
        
        # 레버리지 결정
        leverage, decision = self.calculate_leverage(
            confidence, risk_score, volatility, trend_strength
        )
        
        if leverage == 0:
            print(f"\n{decision}")
            return None
        
        print(f"\n{decision}")
        
        # 증거금 계산 (자본의 10%)
        margin = self.current_capital * 0.1
        
        # 포지션 크기 (레버리지 적용)
        position_value = margin * leverage
        size = position_value / entry_price
        
        # 수수료 계산
        entry_fee = position_value * self.taker_fee
        
        trade = LeverageTrade(
            id=f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            symbol=symbol,
            direction=direction,
            leverage=leverage,
            entry_price=entry_price,
            entry_time=datetime.now(),
            target_price=target_price,
            stop_loss=stop_loss,
            size=size,
            margin=margin,
            confidence=confidence,
            market_condition=market_condition
        )
        
        self.positions.append(trade)
        
        # 매매일지 작성
        self._write_journal_entry(trade)
        
        print(f"\n🚀 포지션 진입!")
        print(f"   심볼: {trade.symbol}")
        print(f"   방향: {trade.direction.upper()}")
        print(f"   레버리지: {trade.leverage}x")
        print(f"   진입가: ${trade.entry_price:.2f}")
        print(f"   목표가: ${trade.target_price:.2f}")
        print(f"   손절가: ${trade.stop_loss:.2f}")
        print(f"   증거금: ${trade.margin:.2f}")
        print(f"   포지션 크기: ${trade.margin * trade.leverage:.2f}")
        print(f"   수수료: ${entry_fee:.2f}")
        
        return trade
    
    def close_position(self, trade_id: str, exit_price: float,
                      reason: str = "signal") -> Optional[LeverageTrade]:
        """포지션 청산"""
        trade = next((p for p in self.positions if p.id == trade_id), None)
        if not trade:
            return None
        
        trade.exit_price = exit_price
        trade.exit_time = datetime.now()
        trade.status = "closed"
        trade.exit_reason = reason
        
        # PnL 계산 (레버리지 적용)
        if trade.direction == "long":
            price_change = (exit_price - trade.entry_price) / trade.entry_price
        else:
            price_change = (trade.entry_price - exit_price) / trade.entry_price
        
        # 레버리지 적용 수익률
        trade.roe = price_change * trade.leverage * 100
        
        # 실제 PnL (증거금 기준)
        trade.pnl = trade.margin * price_change * trade.leverage
        trade.pnl_percent = trade.roe
        
        # 수수료 차감 (진입 + 청산)
        position_value = trade.margin * trade.leverage
        total_fee = position_value * (self.taker_fee * 2)
        trade.pnl -= total_fee
        
        # 자본 업데이트
        self.current_capital += trade.pnl
        
        # 청산 체크
        if trade.roe <= -90:  # 90% 손실 = 청산
            trade.status = "liquidated"
            trade.pnl = -trade.margin  # 증거금 전액 손실
            self.current_capital += trade.pnl
        
        # 리스트 이동
        self.positions.remove(trade)
        self.closed_trades.append(trade)
        
        # 학습 데이터 업데이트
        self._update_learning(trade)
        
        # 매매일지 작성
        self._write_journal_close(trade)
        
        return trade
    
    def _update_learning(self, trade: LeverageTrade):
        """학습 데이터 업데이트"""
        # 레버리지별 성과
        self.leverage_performance[trade.leverage]["trades"] += 1
        self.leverage_performance[trade.leverage]["total_pnl"] += trade.pnl
        if trade.pnl > 0:
            self.leverage_performance[trade.leverage]["wins"] += 1
        
        # 시장 상황별 성과
        condition = trade.market_condition
        if condition not in self.condition_performance:
            self.condition_performance[condition] = {
                "trades": 0, "wins": 0, "total_pnl": 0
            }
        self.condition_performance[condition]["trades"] += 1
        self.condition_performance[condition]["total_pnl"] += trade.pnl
        if trade.pnl > 0:
            self.condition_performance[condition]["wins"] += 1
    
    def _write_journal_entry(self, trade: LeverageTrade):
        """매매일지 - 진입 기록"""
        try:
            journal_entry = f"""
## 🟢 포지션 진입 - {trade.entry_time.strftime('%H:%M:%S')}

| 항목 | 값 |
|------|-----|
| 심볼 | {trade.symbol} |
| 방향 | {trade.direction.upper()} |
| 레버리지 | **{trade.leverage}x** |
| 진입가 | ${trade.entry_price:.2f} |
| 목표가 | ${trade.target_price:.2f} |
| 손절가 | ${trade.stop_loss:.2f} |
| 증거금 | ${trade.margin:.2f} |
| 포지션 크기 | ${trade.margin * trade.leverage:.2f} |
| 신뢰도 | {trade.confidence*100:.0f}% |
| 시장 상황 | {trade.market_condition} |

---
"""
            journal_path = f"/root/.openclaw/workspace/archive/trading/journals/{trade.symbol}_{trade.entry_time.strftime('%Y-%m-%d')}.md"
            os.makedirs(os.path.dirname(journal_path), exist_ok=True)
            
            with open(journal_path, 'a', encoding='utf-8') as f:
                f.write(journal_entry)
                
        except Exception as e:
            print(f"   ⚠️ 매매일지 오류: {e}")
    
    def _write_journal_close(self, trade: LeverageTrade):
        """매매일지 - 청산 기록"""
        try:
            emoji = "🎉" if trade.pnl > 0 else "😢"
            result = "익절" if trade.pnl > 0 else "손절"
            status = "청산" if trade.status == "liquidated" else "청산"
            
            journal_entry = f"""
## {emoji} 포지션 {status} - {trade.exit_time.strftime('%H:%M:%S')}

| 항목 | 값 |
|------|-----|
| 심볼 | {trade.symbol} |
| 방향 | {trade.direction.upper()} |
| 레버리지 | {trade.leverage}x |
| 진입가 | ${trade.entry_price:.2f} |
| 청산가 | ${trade.exit_price:.2f} |
| 청산 사유 | {trade.exit_reason} |
| 보유 시간 | {(trade.exit_time - trade.entry_time).total_seconds() / 60:.1f}분 |
| ROE | {trade.roe:+.2f}% |
| PnL | ${trade.pnl:+.2f} |
| 결과 | **{result}** |

---
"""
            journal_path = f"/root/.openclaw/workspace/archive/trading/journals/{trade.symbol}_{trade.exit_time.strftime('%Y-%m-%d')}.md"
            
            with open(journal_path, 'a', encoding='utf-8') as f:
                f.write(journal_entry)
                
        except Exception as e:
            print(f"   ⚠️ 매매일지 오류: {e}")
    
    def generate_report(self) -> dict:
        """성과 리포트"""
        total_trades = len(self.closed_trades)
        winning_trades = len([t for t in self.closed_trades if t.pnl > 0])
        
        return {
            "timestamp": datetime.now().isoformat(),
            "capital": {
                "initial": self.initial_capital,
                "current": self.current_capital,
                "change": self.current_capital - self.initial_capital,
                "change_percent": ((self.current_capital - self.initial_capital) / self.initial_capital) * 100
            },
            "trades": {
                "total": total_trades,
                "winning": winning_trades,
                "losing": total_trades - winning_trades,
                "win_rate": (winning_trades / total_trades * 100) if total_trades > 0 else 0,
                "open_positions": len(self.positions)
            },
            "leverage_performance": self.leverage_performance,
            "condition_performance": self.condition_performance
        }

# 실행
if __name__ == "__main__":
    engine = LeverageTradingEngine(initial_capital=10000)
    
    # 테스트: 높은 신뢰도 = 10배
    trade1 = engine.open_position(
        symbol="ETH",
        direction="long",
        entry_price=2000,
        target_price=2200,
        stop_loss=1900,
        confidence=0.90,
        market_condition="bullish_trend",
        risk_score=2,
        volatility=0.2,
        trend_strength=0.85
    )
    
    if trade1:
        print(f"\n✅ 결정된 레버리지: {trade1.leverage}x")
