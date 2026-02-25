"""
dongsu-paper-trading-engine
가상 트레이딩 + 자동 학습 시스템
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import os

class PositionStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"

@dataclass
class PaperTrade:
    """가상 거래 기록"""
    id: str
    symbol: str
    direction: str  # "long" or "short"
    entry_price: float
    entry_time: datetime
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    target_price: float = 0
    stop_loss: float = 0
    size: float = 0
    status: PositionStatus = PositionStatus.OPEN
    pnl: float = 0
    pnl_percent: float = 0
    exit_reason: str = ""  # "target", "stop", "signal", "timeout"

@dataclass
class TradingPerformance:
    """트레이딩 성과"""
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_pnl: float = 0
    total_pnl_percent: float = 0
    win_rate: float = 0
    avg_win: float = 0
    avg_loss: float = 0
    profit_factor: float = 0
    max_drawdown: float = 0
    sharpe_ratio: float = 0
    equity_curve: List[Tuple[datetime, float]] = field(default_factory=list)

class PaperTradingEngine:
    """가상 트레이딩 엔진"""
    
    def __init__(self, initial_capital: float = 10000):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions: List[PaperTrade] = []
        self.closed_trades: List[PaperTrade] = []
        self.performance = TradingPerformance()
        self.equity_history: List[Tuple[datetime, float]] = [
            (datetime.now(), initial_capital)
        ]
        
        # TradingJournal 통합
        from core import TradingJournal
        self.journal = TradingJournal()
        
        # 학습 데이터
        self.learning_data = {
            "strategy_performance": {},
            "market_conditions": {},
            "mistakes": [],
            "improvements": []
        }
    
    def open_position(self, symbol: str, direction: str, entry_price: float,
                     target_price: float, stop_loss: float, 
                     confidence: float = 0.5) -> PaperTrade:
        """포지션 진입 + 매매일지 작성"""
        # 자본의 10% 투자 (리스크 관리)
        position_size = (self.current_capital * 0.1) / entry_price
        
        trade = PaperTrade(
            id=f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            symbol=symbol,
            direction=direction,
            entry_price=entry_price,
            entry_time=datetime.now(),
            target_price=target_price,
            stop_loss=stop_loss,
            size=position_size,
            status=PositionStatus.OPEN
        )
        
        self.positions.append(trade)
        
        # ✅ 매매일지 작성 - 진입 기록
        self._write_journal_entry(trade, "OPEN", confidence)
        
        # 학습 데이터 기록
        self._record_open(trade, confidence)
        
        return trade
    
    def close_position(self, trade_id: str, exit_price: float, 
                      reason: str = "signal") -> Optional[PaperTrade]:
        """포지션 청산 + 매매일지 작성"""
        trade = next((p for p in self.positions if p.id == trade_id), None)
        if not trade:
            return None
        
        trade.exit_price = exit_price
        trade.exit_time = datetime.now()
        trade.status = PositionStatus.CLOSED
        trade.exit_reason = reason
        
        # PnL 계산
        if trade.direction == "long":
            trade.pnl = (exit_price - trade.entry_price) * trade.size
            trade.pnl_percent = ((exit_price - trade.entry_price) / trade.entry_price) * 100
        else:  # short
            trade.pnl = (trade.entry_price - exit_price) * trade.size
            trade.pnl_percent = ((trade.entry_price - exit_price) / trade.entry_price) * 100
        
        # 자본 업데이트
        self.current_capital += trade.pnl
        
        # 리스트 이동
        self.positions.remove(trade)
        self.closed_trades.append(trade)
        
        # 성과 업데이트
        self._update_performance(trade)
        
        # ✅ 매매일지 작성 - 청산 기록
        self._write_journal_close(trade)
        
        # 학습 데이터 기록
        self._record_close(trade)
        
        return trade
    
    def _write_journal_entry(self, trade: PaperTrade, action: str, confidence: float):
        """매매일지에 진입 기록 작성"""
        try:
            journal_entry = f"""
## 🟢 포지션 진입 - {trade.entry_time.strftime('%H:%M:%S')}

| 항목 | 값 |
|------|-----|
| 심볼 | {trade.symbol} |
| 방향 | {trade.direction.upper()} |
| 진입가 | ${trade.entry_price:.2f} |
| 목표가 | ${trade.target_price:.2f} |
| 손절가 | ${trade.stop_loss:.2f} |
| 수량 | {trade.size:.6f} |
| 신뢰도 | {confidence*100:.0f}% |
| 예상 R/R | {abs(trade.target_price - trade.entry_price) / abs(trade.stop_loss - trade.entry_price):.2f} |

---
"""
            # 파일에 추가
            journal_path = f"/root/.openclaw/workspace/archive/trading/journals/{trade.symbol}_{trade.entry_time.strftime('%Y-%m-%d')}.md"
            os.makedirs(os.path.dirname(journal_path), exist_ok=True)
            
            with open(journal_path, 'a', encoding='utf-8') as f:
                f.write(journal_entry)
                
            print(f"   📝 매매일지 기록: {journal_path}")
            
        except Exception as e:
            print(f"   ⚠️ 매매일지 작성 오류: {e}")
    
    def _write_journal_close(self, trade: PaperTrade):
        """매매일지에 청산 기록 작성"""
        try:
            emoji = "🎉" if trade.pnl > 0 else "😢"
            result = "익절" if trade.pnl > 0 else "손절"
            
            journal_entry = f"""
## {emoji} 포지션 청산 - {trade.exit_time.strftime('%H:%m:%S')}

| 항목 | 값 |
|------|-----|
| 심볼 | {trade.symbol} |
| 방향 | {trade.direction.upper()} |
| 진입가 | ${trade.entry_price:.2f} |
| 청산가 | ${trade.exit_price:.2f} |
| 청산 사유 | {trade.exit_reason} |
| 보유 시간 | {(trade.exit_time - trade.entry_time).total_seconds() / 60:.1f}분 |
| PnL | ${trade.pnl:+.2f} ({trade.pnl_percent:+.2f}%) |
| 결과 | **{result}** |

---
"""
            # 파일에 추가
            journal_path = f"/root/.openclaw/workspace/archive/trading/journals/{trade.symbol}_{trade.exit_time.strftime('%Y-%m-%d')}.md"
            
            with open(journal_path, 'a', encoding='utf-8') as f:
                f.write(journal_entry)
                
            print(f"   📝 매매일지 기록: {journal_path}")
            
        except Exception as e:
            print(f"   ⚠️ 매매일지 작성 오류: {e}")
    
    def check_positions(self, current_prices: Dict[str, float]):
        """포지션 청산 조건 체크"""
        for trade in self.positions[:]:
            current_price = current_prices.get(trade.symbol)
            if not current_price:
                continue
            
            # 롱 포지션
            if trade.direction == "long":
                # 목표가 도달
                if current_price >= trade.target_price:
                    self.close_position(trade.id, trade.target_price, "target")
                # 손절가 도달
                elif current_price <= trade.stop_loss:
                    self.close_position(trade.id, trade.stop_loss, "stop")
            
            # 숏 포지션
            else:
                # 목표가 도달
                if current_price <= trade.target_price:
                    self.close_position(trade.id, trade.target_price, "target")
                # 손절가 도달
                elif current_price >= trade.stop_loss:
                    self.close_position(trade.id, trade.stop_loss, "stop")
    
    def _update_performance(self, trade: PaperTrade):
        """성과 지표 업데이트"""
        self.performance.total_trades += 1
        
        if trade.pnl > 0:
            self.performance.winning_trades += 1
        else:
            self.performance.losing_trades += 1
        
        self.performance.total_pnl += trade.pnl
        self.performance.total_pnl_percent += trade.pnl_percent
        
        # 승률
        self.performance.win_rate = (
            self.performance.winning_trades / self.performance.total_trades * 100
        )
        
        # 평균 수익/손실
        wins = [t.pnl for t in self.closed_trades if t.pnl > 0]
        losses = [t.pnl for t in self.closed_trades if t.pnl <= 0]
        
        self.performance.avg_win = sum(wins) / len(wins) if wins else 0
        self.performance.avg_loss = sum(losses) / len(losses) if losses else 0
        
        # 수익 팩터
        total_wins = sum(wins)
        total_losses = abs(sum(losses))
        self.performance.profit_factor = (
            total_wins / total_losses if total_losses > 0 else float('inf')
        )
        
        # 자본 곡선
        self.equity_history.append((datetime.now(), self.current_capital))
        self.performance.equity_curve = self.equity_history
    
    def _record_open(self, trade: PaperTrade, confidence: float):
        """진입 기록 (학습용)"""
        record = {
            "time": trade.entry_time.isoformat(),
            "symbol": trade.symbol,
            "direction": trade.direction,
            "entry_price": trade.entry_price,
            "target": trade.target_price,
            "stop": trade.stop_loss,
            "confidence": confidence,
            "market_condition": self._analyze_market_condition()
        }
        
        # 파일에 저장
        self._save_learning_data("opens", record)
    
    def _record_close(self, trade: PaperTrade):
        """청산 기록 (학습용)"""
        record = {
            "time": trade.exit_time.isoformat(),
            "symbol": trade.symbol,
            "pnl": trade.pnl,
            "pnl_percent": trade.pnl_percent,
            "exit_reason": trade.exit_reason,
            "duration_minutes": (trade.exit_time - trade.entry_time).total_seconds() / 60,
            "lesson": self._extract_lesson(trade)
        }
        
        self._save_learning_data("closes", record)
        
        # 실수 기록
        if trade.pnl < 0:
            self.learning_data["mistakes"].append(record)
    
    def _analyze_market_condition(self) -> str:
        """시장 상황 분석"""
        # 간단한 시장 상황 분류
        conditions = ["bullish", "bearish", "sideways", "volatile"]
        return random.choice(conditions)  # 실제로는 기술적 분석 기반
    
    def _extract_lesson(self, trade: PaperTrade) -> str:
        """거래에서 교훈 추출"""
        if trade.pnl > 0:
            if trade.exit_reason == "target":
                return "목표가 설정이 적절했음"
            else:
                return "조기 청산했으나 수익"
        else:
            if trade.exit_reason == "stop":
                return "손절가가 너무 좁았을 수 있음"
            else:
                return "진입 타이밍 개선 필요"
    
    def _save_learning_data(self, category: str, data: dict):
        """학습 데이터 저장"""
        path = f"/root/.openclaw/workspace/archive/trading/learning/{category}.jsonl"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, 'a') as f:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
    
    def generate_report(self) -> dict:
        """성과 리포트 생성"""
        return {
            "timestamp": datetime.now().isoformat(),
            "capital": {
                "initial": self.initial_capital,
                "current": self.current_capital,
                "change": self.current_capital - self.initial_capital,
                "change_percent": (
                    (self.current_capital - self.initial_capital) / self.initial_capital * 100
                )
            },
            "trades": {
                "total": self.performance.total_trades,
                "winning": self.performance.winning_trades,
                "losing": self.performance.losing_trades,
                "win_rate": round(self.performance.win_rate, 2),
                "open_positions": len(self.positions)
            },
            "performance": {
                "total_pnl": round(self.performance.total_pnl, 2),
                "total_pnl_percent": round(self.performance.total_pnl_percent, 2),
                "avg_win": round(self.performance.avg_win, 2),
                "avg_loss": round(self.performance.avg_loss, 2),
                "profit_factor": round(self.performance.profit_factor, 2)
            },
            "learning": {
                "mistakes_count": len(self.learning_data["mistakes"]),
                "recent_lessons": [
                    m.get("lesson", "") 
                    for m in self.learning_data["mistakes"][-5:]
                ]
            }
        }

# 실행
if __name__ == "__main__":
    engine = PaperTradingEngine(initial_capital=10000)
    
    # 테스트 거래
    trade1 = engine.open_position(
        symbol="ETH",
        direction="long",
        entry_price=1890,
        target_price=1970,
        stop_loss=1820,
        confidence=0.7
    )
    
    # 가격 변동 시뮬레이션
    engine.check_positions({"ETH": 1980})  # 목표가 도달
    
    # 리포트 출력
    report = engine.generate_report()
    print(json.dumps(report, indent=2, ensure_ascii=False))
