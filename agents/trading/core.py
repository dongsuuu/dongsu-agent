"""
dongsu-trading-agent
비트코인/이더리움 자동 트레이딩 분석 엔진
"""

import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import os

class SignalType(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"

class TimeFrame(Enum):
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"

@dataclass
class Candle:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume
        }

@dataclass
class Signal:
    symbol: str
    timeframe: str
    signal_type: SignalType
    price: float
    target_price: float
    stop_loss: float
    confidence: float
    indicators: Dict
    timestamp: int
    reason: str

@dataclass
class Position:
    symbol: str
    direction: str  # "long" or "short"
    entry_price: float
    entry_time: int
    target_price: float
    stop_loss: float
    size: float
    status: str  # "open", "closed"
    exit_price: Optional[float] = None
    exit_time: Optional[int] = None
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None

class DataFetcher:
    """Binance API로 차트 데이터 수집"""
    
    BASE_URL = "https://api.binance.com"
    
    def __init__(self):
        self.session = requests.Session()
    
    def fetch_candles(self, symbol: str, interval: str, limit: int = 100) -> List[Candle]:
        """
        Binance API로 캔들 데이터 수집
        interval: 1m, 5m, 15m, 30m, 1h, 4h, 1d
        """
        symbol = f"{symbol}USDT"
        url = f"{self.BASE_URL}/api/v3/klines"
        
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Binance returns: [timestamp, open, high, low, close, volume, ...]
            candles = []
            for item in data:
                candles.append(Candle(
                    timestamp=item[0],  # already in milliseconds
                    open=float(item[1]),
                    high=float(item[2]),
                    low=float(item[3]),
                    close=float(item[4]),
                    volume=float(item[5])
                ))
            
            return candles
            
        except Exception as e:
            print(f"Error fetching candles: {e}")
            return []
    
    def fetch_all_timeframes(self, symbol: str) -> Dict[str, List[Candle]]:
        """모든 시간대 데이터 수집"""
        timeframes = {
            "1m": ("1m", 100),
            "5m": ("5m", 100),
            "15m": ("15m", 100),
            "1h": ("1h", 100),
            "4h": ("4h", 100),
            "1d": ("1d", 100)
        }
        
        result = {}
        for tf, (interval, limit) in timeframes.items():
            candles = self.fetch_candles(symbol, interval, limit)
            result[tf] = candles
            
        return result

class TechnicalAnalysis:
    """기술적 분석 엔진"""
    
    @staticmethod
    def ema(data: List[float], period: int) -> List[float]:
        """지수이동평균 계산"""
        if len(data) < period:
            return data
        
        multiplier = 2 / (period + 1)
        ema_values = [sum(data[:period]) / period]
        
        for price in data[period:]:
            ema_values.append((price - ema_values[-1]) * multiplier + ema_values[-1])
        
        # Pad with None for the first 'period-1' values
        return [None] * (period - 1) + ema_values
    
    @staticmethod
    def rsi(data: List[float], period: int = 14) -> List[float]:
        """RSI 계산"""
        if len(data) < period + 1:
            return [50] * len(data)
        
        deltas = [data[i] - data[i-1] for i in range(1, len(data))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gains = []
        avg_losses = []
        
        # First average
        avg_gains.append(sum(gains[:period]) / period)
        avg_losses.append(sum(losses[:period]) / period)
        
        # Subsequent averages
        for i in range(period, len(gains)):
            avg_gains.append((avg_gains[-1] * (period - 1) + gains[i]) / period)
            avg_losses.append((avg_losses[-1] * (period - 1) + losses[i]) / period)
        
        rsi_values = []
        for i in range(len(avg_gains)):
            if avg_losses[i] == 0:
                rsi_values.append(100)
            else:
                rs = avg_gains[i] / avg_losses[i]
                rsi_values.append(100 - (100 / (1 + rs)))
        
        # Pad with None
        return [None] * (period) + rsi_values
    
    @staticmethod
    def macd(data: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """MACD 계산"""
        ema_fast = TechnicalAnalysis.ema(data, fast)
        ema_slow = TechnicalAnalysis.ema(data, slow)
        
        # Remove None values for calculation
        valid_fast = [x for x in ema_fast if x is not None]
        valid_slow = [x for x in ema_slow if x is not None]
        
        if len(valid_fast) != len(valid_slow):
            min_len = min(len(valid_fast), len(valid_slow))
            valid_fast = valid_fast[-min_len:]
            valid_slow = valid_slow[-min_len:]
        
        macd_line = [f - s for f, s in zip(valid_fast, valid_slow)]
        signal_line = TechnicalAnalysis.ema(macd_line, signal)
        
        # Histogram
        valid_signal = [x for x in signal_line if x is not None]
        min_len = min(len(macd_line), len(valid_signal))
        histogram = [macd_line[-(i+1)] - valid_signal[-(i+1)] for i in range(min_len)]
        histogram.reverse()
        
        return {
            "macd": [None] * (len(data) - len(macd_line)) + macd_line,
            "signal": [None] * (len(data) - len(valid_signal)) + valid_signal,
            "histogram": [None] * (len(data) - len(histogram)) + histogram
        }
    
    @staticmethod
    def bollinger_bands(data: List[float], period: int = 20, std_dev: float = 2.0) -> Dict:
        """볼린저 밴드 계산"""
        if len(data) < period:
            return {"upper": data, "middle": data, "lower": data}
        
        upper = []
        middle = []
        lower = []
        
        for i in range(len(data)):
            if i < period - 1:
                upper.append(None)
                middle.append(None)
                lower.append(None)
            else:
                slice_data = data[i-period+1:i+1]
                avg = sum(slice_data) / period
                variance = sum((x - avg) ** 2 for x in slice_data) / period
                std = variance ** 0.5
                
                middle.append(avg)
                upper.append(avg + std_dev * std)
                lower.append(avg - std_dev * std)
        
        return {"upper": upper, "middle": middle, "lower": lower}
    
    @staticmethod
    def support_resistance(data: List[Candle], lookback: int = 20) -> Dict:
        """지지/저항선 계산"""
        if len(data) < lookback:
            return {"support": data[-1].low if data else 0, "resistance": data[-1].high if data else 0}
        
        recent = data[-lookback:]
        highs = [c.high for c in recent]
        lows = [c.low for c in recent]
        
        # Simple pivot detection
        resistance = max(highs)
        support = min(lows)
        
        return {"support": support, "resistance": resistance}

class SignalGenerator:
    """매매 시그널 생성기"""
    
    def __init__(self):
        self.ta = TechnicalAnalysis()
    
    def generate_signals(self, symbol: str, candles: List[Candle], timeframe: str) -> List[Signal]:
        """모든 전략으로 시그널 생성"""
        signals = []
        
        closes = [c.close for c in candles]
        if len(closes) < 50:
            return signals
        
        # EMA Cross 전략
        ema_signal = self._ema_cross_strategy(symbol, candles, timeframe, closes)
        if ema_signal:
            signals.append(ema_signal)
        
        # RSI 반전 전략
        rsi_signal = self._rsi_reversal_strategy(symbol, candles, timeframe, closes)
        if rsi_signal:
            signals.append(rsi_signal)
        
        # Bollinger Breakout 전략
        bb_signal = self._bollinger_breakout_strategy(symbol, candles, timeframe, closes)
        if bb_signal:
            signals.append(bb_signal)
        
        return signals
    
    def _ema_cross_strategy(self, symbol: str, candles: List[Candle], timeframe: str, closes: List[float]) -> Optional[Signal]:
        """EMA 골든/데드 크로스 전략"""
        ema9 = self.ta.ema(closes, 9)
        ema21 = self.ta.ema(closes, 21)
        
        # Remove None values
        valid_ema9 = [x for x in ema9 if x is not None]
        valid_ema21 = [x for x in ema21 if x is not None]
        
        if len(valid_ema9) < 2 or len(valid_ema21) < 2:
            return None
        
        # Check for cross
        prev_ema9, curr_ema9 = valid_ema9[-2], valid_ema9[-1]
        prev_ema21, curr_ema21 = valid_ema21[-2], valid_ema21[-1]
        
        current_price = closes[-1]
        
        # 수수료 고려 (Binance 기준: 진입 0.05% + 청산 0.05% = 0.1%)
        FEE_RATE = 0.001  # 0.1%
        MIN_PROFIT = 0.005  # 최소 0.5% 수익 (수수료 커버 + 실익)
        
        # Golden Cross (Bullish)
        if prev_ema9 <= prev_ema21 and curr_ema9 > curr_ema21:
            target = current_price * (1 + MIN_PROFIT + 0.01)  # 0.6% 이상
            stop = current_price * 0.97
            
            return Signal(
                symbol=symbol,
                timeframe=timeframe,
                signal_type=SignalType.BUY,
                price=current_price,
                target_price=target,
                stop_loss=stop,
                confidence=0.75,
                indicators={"ema9": curr_ema9, "ema21": curr_ema21, "fee_rate": FEE_RATE},
                timestamp=candles[-1].timestamp,
                reason=f"EMA Golden Cross (Fee adjusted: {FEE_RATE*100}%)"
            )
        
        # Dead Cross (Bearish)
        elif prev_ema9 >= prev_ema21 and curr_ema9 < curr_ema21:
            target = current_price * 0.95  # 5% down target
            stop = current_price * 1.03    # 3% stop
            
            return Signal(
                symbol=symbol,
                timeframe=timeframe,
                signal_type=SignalType.SELL,
                price=current_price,
                target_price=target,
                stop_loss=stop,
                confidence=0.70,
                indicators={"ema9": curr_ema9, "ema21": curr_ema21},
                timestamp=candles[-1].timestamp,
                reason=f"EMA Dead Cross: EMA9({curr_ema9:.2f}) < EMA21({curr_ema21:.2f})"
            )
        
        return None
    
    def _rsi_reversal_strategy(self, symbol: str, candles: List[Candle], timeframe: str, closes: List[float]) -> Optional[Signal]:
        """RSI 과매수/과매도 반전 전략"""
        rsi_values = self.ta.rsi(closes, 14)
        valid_rsi = [x for x in rsi_values if x is not None]
        
        if len(valid_rsi) < 2:
            return None
        
        current_rsi = valid_rsi[-1]
        prev_rsi = valid_rsi[-2]
        current_price = closes[-1]
        
        # Oversold bounce (RSI < 30 and rising)
        if prev_rsi < 30 and current_rsi > prev_rsi:
            target = current_price * 1.04
            stop = current_price * 0.98
            
            return Signal(
                symbol=symbol,
                timeframe=timeframe,
                signal_type=SignalType.BUY,
                price=current_price,
                target_price=target,
                stop_loss=stop,
                confidence=0.65,
                indicators={"rsi": current_rsi},
                timestamp=candles[-1].timestamp,
                reason=f"RSI Oversold Bounce: {current_rsi:.1f} (was {prev_rsi:.1f})"
            )
        
        # Overbought pullback (RSI > 70 and falling)
        elif prev_rsi > 70 and current_rsi < prev_rsi:
            target = current_price * 0.96
            stop = current_price * 1.02
            
            return Signal(
                symbol=symbol,
                timeframe=timeframe,
                signal_type=SignalType.SELL,
                price=current_price,
                target_price=target,
                stop_loss=stop,
                confidence=0.60,
                indicators={"rsi": current_rsi},
                timestamp=candles[-1].timestamp,
                reason=f"RSI Overbought Pullback: {current_rsi:.1f} (was {prev_rsi:.1f})"
            )
        
        return None
    
    def _bollinger_breakout_strategy(self, symbol: str, candles: List[Candle], timeframe: str, closes: List[float]) -> Optional[Signal]:
        """볼린저 밴드 돌파 전략"""
        bb = self.ta.bollinger_bands(closes, 20, 2.0)
        
        if bb["lower"][-1] is None:
            return None
        
        current_price = closes[-1]
        lower = bb["lower"][-1]
        upper = bb["upper"][-1]
        middle = bb["middle"][-1]
        
        # Price below lower band (bounce opportunity)
        if current_price < lower:
            target = middle
            stop = current_price * 0.97
            
            return Signal(
                symbol=symbol,
                timeframe=timeframe,
                signal_type=SignalType.BUY,
                price=current_price,
                target_price=target,
                stop_loss=stop,
                confidence=0.70,
                indicators={"bb_lower": lower, "bb_middle": middle, "bb_upper": upper},
                timestamp=candles[-1].timestamp,
                reason=f"BB Lower Band Bounce: Price({current_price:.2f}) < Lower({lower:.2f})"
            )
        
        # Price above upper band (pullback opportunity)
        elif current_price > upper:
            target = middle
            stop = current_price * 1.03
            
            return Signal(
                symbol=symbol,
                timeframe=timeframe,
                signal_type=SignalType.SELL,
                price=current_price,
                target_price=target,
                stop_loss=stop,
                confidence=0.65,
                indicators={"bb_lower": lower, "bb_middle": middle, "bb_upper": upper},
                timestamp=candles[-1].timestamp,
                reason=f"BB Upper Band Pullback: Price({current_price:.2f}) > Upper({upper:.2f})"
            )
        
        return None

class TradingJournal:
    """매매일지 관리"""
    
    def __init__(self, base_path: str = "/root/.openclaw/workspace/archive/trading"):
        self.base_path = base_path
        self.journals_path = os.path.join(base_path, "journals")
        os.makedirs(self.journals_path, exist_ok=True)
    
    def create_entry(self, symbol: str, signals: List[Signal], positions: List[Position], current_price: float = 0) -> str:
        """새 매매일지 작성 - 심볼별 분리, 시간순 누적"""
        now = datetime.now()
        # 심볼별 파일: BTC_2026-02-25.md, ETH_2026-02-25.md
        filename = f"{symbol}_{now.strftime('%Y-%m-%d')}.md"
        filepath = os.path.join(self.journals_path, filename)
        
        # 기존 파일 있으면 끝에 추가, 없으면 새로 생성
        if os.path.exists(filepath):
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(self._format_entry(symbol, signals, positions, now, current_price))
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self._format_journal_header(symbol, now))
                f.write(self._format_entry(symbol, signals, positions, now, current_price))
        
        return filepath
    
    def _format_journal_header(self, symbol: str, dt: datetime) -> str:
        """일지 헤더 (처음 생성시만)"""
        return f"""# {symbol} Trading Journal - {dt.strftime('%Y-%m-%d')}

> 자동 생성된 매매일지 | dongsu-trading-agent
> 실시간 가격: Binance API

---

"""
    
    def _format_entry(self, symbol: str, signals: List[Signal], positions: List[Position], dt: datetime, current_price: float) -> str:
        """개별 분석 항목"""
        entry = f"""## 📊 Analysis - {dt.strftime('%H:%M')} KST

| 지표 | 값 |
|------|-----|
| 시간 | {dt.strftime('%H:%M')} |
| 현재가 | ${current_price:.2f} |

"""
        
        if signals:
            for i, signal in enumerate(signals, 1):
                emoji = "🟢 BUY" if signal.signal_type == SignalType.BUY else "🔴 SELL" if signal.signal_type == SignalType.SELL else "⚪ HOLD"
                entry += f"""### {emoji} | {signal.timeframe}

| 항목 | 값 |
|------|-----|
| 진입가 | ${signal.price:.2f} |
| 목표가 | ${signal.target_price:.2f} |
| 손절가 | ${signal.stop_loss:.2f} |
| 기대 수익률 | {((signal.target_price - signal.price) / signal.price * 100):.2f}% |
| 리스크 | {abs((signal.stop_loss - signal.price) / signal.price * 100):.2f}% |
| 승률 | {signal.confidence * 100:.0f}% |
| 근거 | {signal.reason} |

"""
        else:
            entry += "**시그널 없음** - 현재 조건 미충족\n\n"
        
        entry += "---\n\n"
        return entry
    
    def _format_journal(self, symbol: str, signals: List[Signal], positions: List[Position], dt: datetime, current_price: float = 0) -> str:
        """매매일지 마크다운 포맷"""
        
        
        journal = f"""# Trading Journal - {symbol} | {dt.strftime('%Y-%m-%d %H:%M')} KST

## 📊 시장 상황

| 지표 | 값 |
|------|-----|
| 분석 시간 | {dt.strftime('%Y-%m-%d %H:%M')} |
| 심볼 | {symbol} |
| 현재가 | ${current_price:.2f} |

## 🎯 생성된 시그널

"""
        
        for i, signal in enumerate(signals, 1):
            emoji = "🟢" if signal.signal_type == SignalType.BUY else "🔴" if signal.signal_type == SignalType.SELL else "⚪"
            journal += f"""### {i}. {emoji} {signal.signal_type.value.upper()} | {signal.timeframe}

| 항목 | 값 |
|------|-----|
| 진입가 | ${signal.price:.2f} |
| 목표가 | ${signal.target_price:.2f} |
| 손절가 | ${signal.stop_loss:.2f} |
| 기대 수익률 | {((signal.target_price - signal.price) / signal.price * 100):.2f}% |
| 리스크 | {abs((signal.stop_loss - signal.price) / signal.price * 100):.2f}% |
| 승률 | {signal.confidence * 100:.0f}% |
| 근거 | {signal.reason} |

**지표:**
```json
{json.dumps(signal.indicators, indent=2)}
```

---

"""
        
        journal += f"""## 💼 포지션 현황

| 심볼 | 방향 | 진입가 | 현재가 | 손절가 | 목표가 | 상태 |
|------|------|--------|--------|--------|--------|------|
"""
        
        for pos in positions:
            current = signals[0].price if signals else pos.entry_price
            journal += f"| {pos.symbol} | {pos.direction} | ${pos.entry_price:.2f} | ${current:.2f} | ${pos.stop_loss:.2f} | ${pos.target_price:.2f} | {pos.status} |\n"
        
        journal += f"""
## 📝 회고

### 잘한 점
- 

### 개선할 점
- 

### 다음 전략 조정
- 

---
*자동 생성된 매매일지 | dongsu-trading-agent*
"""
        
        return journal

class TradingAgent:
    """메인 트레이딩 에이전트"""
    
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.signal_generator = SignalGenerator()
        self.journal = TradingJournal()
        self.positions: List[Position] = []
    
    def analyze(self, symbol: str = "BTC") -> Dict:
        """전체 분석 실행"""
        print(f"🔍 {symbol} 분석 시작...")
        
        # 1. 데이터 수집
        print("  → 데이터 수집 중...")
        all_data = self.data_fetcher.fetch_all_timeframes(symbol)
        
        # 2. 시그널 생성 (각 시간대별)
        print("  → 시그널 생성 중...")
        all_signals = []
        for timeframe, candles in all_data.items():
            if len(candles) >= 50:
                signals = self.signal_generator.generate_signals(symbol, candles, timeframe)
                all_signals.extend(signals)
        
        # 3. 매매일지 작성
        print("  → 매매일지 작성 중...")
        current_price = all_data.get("1h", [{}])[-1].close if all_data.get("1h") else 0
        journal_path = self.journal.create_entry(symbol, all_signals, self.positions, current_price)
        
        # Get current price from most recent candle
        current_price = all_data.get("1h", [{}])[-1].close if all_data.get("1h") else 0
        
        result = {
            "symbol": symbol,
            "timestamp": int(datetime.now().timestamp() * 1000),
            "current_price": current_price,
            "signals": all_signals,
            "journal_path": journal_path,
            "data_summary": {tf: len(candles) for tf, candles in all_data.items()}
        }
        
        print(f"✅ 분석 완료! 일지: {journal_path}")
        return result
    
    def simulate_position(self, signal: Signal, capital: float = 10000) -> Position:
        """가상 포지션 생성"""
        position_size = capital / signal.price * 0.1  # 10% of capital
        
        position = Position(
            symbol=signal.symbol,
            direction="long" if signal.signal_type == SignalType.BUY else "short",
            entry_price=signal.price,
            entry_time=signal.timestamp,
            target_price=signal.target_price,
            stop_loss=signal.stop_loss,
            size=position_size,
            status="open"
        )
        
        self.positions.append(position)
        return position

# 실행
if __name__ == "__main__":
    agent = TradingAgent()
    
    # BTC 분석
    result_btc = agent.analyze("BTC")
    
    # ETH 분석
    result_eth = agent.analyze("ETH")
    
    print("\n📊 분석 결과 요약:")
    print(f"BTC 시그널: {len(result_btc['signals'])}개")
    print(f"ETH 시그널: {len(result_eth['signals'])}개")
