# 트레이딩 봇 마스터 가이드

## 1. 트레이딩 봇이란?

**정의:** 자동으로 암호화폐를 매매하는 소프트웨어 프로그램

**핵심 기능:**
- 실시간 시장 데이터 수집
- 기술적 분석 (TA)
- 매수/매도 신호 생성
- 자동 주문 실행
- 리스크 관리 (손절/익절)
- 백테스팅 (과거 데이터 검증)

---

## 2. 트레이딩 봇 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                      TRADING BOT                            │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Data     │  │ Strategy │  │ Risk     │  │ Execution│  │
│  │ Ingestion│→ │ Engine   │→ │ Manager  │→ │ Engine   │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│       ↑                                            ↓        │
│  ┌──────────┐                                ┌──────────┐  │
│  │ Exchange │←──────────────────────────────→│ Exchange │  │
│  │  API     │         WebSocket              │  API     │  │
│  └──────────┘                                └──────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 오픈소스 트레이딩 봇 비교

### 3.1 Freqtrade (Python)

**특징:**
- 가장 인기 있는 오픈소스 봇
- Python 3.11+ 기반
- 15+ 거래소 지원
- 백테스팅 + 하이퍼옵티마이제이션
- FreqAI (머신러닝) 지원
- Telegram/WebUI 관리

**핵심 코드 구조:**
```python
class MyStrategy(IStrategy):
    # 전략 파라미터
    timeframe = '5m'
    stoploss = -0.10
    minimal_roi = {"60": 0.01, "30": 0.02, "0": 0.04}
    
    # 지표 계산
    def populate_indicators(self, dataframe, metadata):
        dataframe['rsi'] = ta.RSI(dataframe)
        dataframe['ema9'] = ta.EMA(dataframe, timeperiod=9)
        return dataframe
    
    # 진입 신호
    def populate_entry_trend(self, dataframe, metadata):
        dataframe.loc[
            (dataframe['rsi'] < 30) &
            (dataframe['close'] > dataframe['ema9']),
            'enter_long'
        ] = 1
        return dataframe
    
    # 청산 신호
    def populate_exit_trend(self, dataframe, metadata):
        dataframe.loc[
            (dataframe['rsi'] > 70),
            'exit_long'
        ] = 1
        return dataframe
```

**장점:**
- 문서화 잘 됨
- 커뮤니티 활발
- 백테스팅 강력

**단점:**
- Python 속도 제한
- 고빈도 트레이딩 부적합

---

### 3.2 Hummingbot (Python/C++)

**특징:**
- 전문가용 마켓 메이킹 봇
- C++ 코어 + Python 전략
- 20+ 거래소/DEX 지원
- arbitrage + market making 전문

**핵심 코드 구조:**
```python
from hummingbot.strategy.market_trading_pair_tuple import MarketTradingPairTuple

class MyStrategy(StrategyBase):
    def __init__(self, market_info: MarketTradingPairTuple):
        super().__init__()
        self._market_info = market_info
        
    def tick(self, timestamp: float):
        # 가격 확인
        mid_price = self._market_info.get_mid_price()
        
        # 오더 생성
        buy_price = mid_price * 0.995
        sell_price = mid_price * 1.005
        
        # 오더 제출
        self.buy_with_specific_market(
            market_trading_pair_tuple=self._market_info,
            amount=Decimal("0.1"),
            price=buy_price
        )
```

**장점:**
- 고성능 (C++ 코어)
- 마켓 메이킹 최적화
- DEX 지원

**단점:**
- 학습 곡선 가파름
- 설정 복잡

---

### 3.3 CCXT (JavaScript/Python/PHP)

**특징:**
- 거래소 통합 라이브러리
- 100+ 거래소 지원
- 통일된 API
- 언어 선택 가능

**핵심 코드:**
```python
import ccxt

# 거래소 연결
exchange = ccxt.binance({
    'apiKey': 'YOUR_API_KEY',
    'secret': 'YOUR_SECRET',
})

# 잔고 확인
balance = exchange.fetch_balance()

# 시장가 주문
order = exchange.create_market_buy_order('BTC/USDT', 0.001)

# 지정가 주문
order = exchange.create_limit_buy_order('BTC/USDT', 0.001, 50000)
```

---

## 4. 트레이딩 봇 핵심 전략

### 4.1 추세 추종 (Trend Following)

```python
def trend_following_strategy(dataframe):
    # 이동평균 계산
    dataframe['ema_fast'] = ta.EMA(dataframe, timeperiod=9)
    dataframe['ema_slow'] = ta.EMA(dataframe, timeperiod=21)
    
    # 골든 크로스 (진입)
    dataframe['enter_long'] = (
        (dataframe['ema_fast'] > dataframe['ema_slow']) &
        (dataframe['ema_fast'].shift(1) <= dataframe['ema_slow'].shift(1))
    )
    
    # 데드 크로스 (청산)
    dataframe['exit_long'] = (
        (dataframe['ema_fast'] < dataframe['ema_slow']) &
        (dataframe['ema_fast'].shift(1) >= dataframe['ema_slow'].shift(1))
    )
    
    return dataframe
```

### 4.2 평균 회귀 (Mean Reversion)

```python
def mean_reversion_strategy(dataframe):
    # 볼린저 밴드
    dataframe['bb_upper'], dataframe['bb_middle'], dataframe['bb_lower'] = \
        ta.BBANDS(dataframe['close'])
    
    # RSI
    dataframe['rsi'] = ta.RSI(dataframe['close'])
    
    # 과매도 진입
    dataframe['enter_long'] = (
        (dataframe['close'] < dataframe['bb_lower']) &
        (dataframe['rsi'] < 30)
    )
    
    # 과매수 청산
    dataframe['exit_long'] = (
        (dataframe['close'] > dataframe['bb_upper']) |
        (dataframe['rsi'] > 70)
    )
    
    return dataframe
```

### 4.3 차익 거래 (Arbitrage)

```python
def arbitrage_strategy(exchange1, exchange2, symbol):
    # 가격 조회
    price1 = exchange1.fetch_ticker(symbol)['last']
    price2 = exchange2.fetch_ticker(symbol)['last']
    
    # 스프레드 계산
    spread = abs(price1 - price2) / min(price1, price2)
    
    # 차익 기회 확인
    if spread > 0.005:  # 0.5% 이상
        if price1 < price2:
            # exchange1에서 매수, exchange2에서 매도
            buy_order = exchange1.create_market_buy_order(symbol, amount)
            sell_order = exchange2.create_market_sell_order(symbol, amount)
        else:
            # exchange2에서 매수, exchange1에서 매도
            buy_order = exchange2.create_market_buy_order(symbol, amount)
            sell_order = exchange1.create_market_sell_order(symbol, amount)
```

### 4.4 마켓 메이킹 (Market Making)

```python
def market_making_strategy(mid_price, spread=0.002):
    # 스프레드 설정 (0.2%)
    buy_price = mid_price * (1 - spread)
    sell_price = mid_price * (1 + spread)
    
    # 양방향 오더
    buy_order = create_limit_buy_order(buy_price, amount)
    sell_order = create_limit_sell_order(sell_price, amount)
    
    # 체결 시 재주문
    if buy_order.filled:
        sell_order = create_limit_sell_order(sell_price, amount * 2)
    if sell_order.filled:
        buy_order = create_limit_buy_order(buy_price, amount * 2)
```

---

## 5. 리스크 관리 시스템

### 5.1 포지션 사이징

```python
def calculate_position_size(balance, risk_percent, stop_loss_percent):
    """
    켈리 공식 기반 포지션 크기 계산
    """
    risk_amount = balance * risk_percent
    position_size = risk_amount / stop_loss_percent
    return position_size

# 예시
balance = 10000  # $10,000
risk_percent = 0.02  # 2%
stop_loss = 0.05  # 5%

position = calculate_position_size(balance, risk_percent, stop_loss)
# position = $400 (잔고의 4%)
```

### 5.2 손절/익절

```python
# 고정 손절
stop_loss = entry_price * 0.95  # -5%

# 트레일링 스톱
trailing_stop = highest_price * 0.97  # 최고점 대비 -3%

# ATR 기반 손절
atr = ta.ATR(dataframe)
stop_loss = entry_price - (atr * 2)  # 2 ATR
```

---

## 6. 백테스팅 엔진

```python
def backtest(strategy, data, initial_balance=10000):
    balance = initial_balance
    position = 0
    trades = []
    
    for i in range(len(data)):
        # 신호 확인
        signal = strategy.generate_signal(data.iloc[:i+1])
        
        # 매수
        if signal == 'buy' and position == 0:
            position = balance / data['close'].iloc[i]
            entry_price = data['close'].iloc[i]
            trades.append({'type': 'buy', 'price': entry_price})
        
        # 매도
        elif signal == 'sell' and position > 0:
            balance = position * data['close'].iloc[i]
            exit_price = data['close'].iloc[i]
            pnl = (exit_price - entry_price) / entry_price
            trades.append({'type': 'sell', 'price': exit_price, 'pnl': pnl})
            position = 0
    
    # 최종 평가
    final_balance = balance if position == 0 else position * data['close'].iloc[-1]
    return_rate = (final_balance - initial_balance) / initial_balance
    
    return {
        'initial_balance': initial_balance,
        'final_balance': final_balance,
        'return_rate': return_rate,
        'trades': trades
    }
```

---

## 7. 실전 적용 체크리스트

### Phase 1: 준비 (1-2주)
- [ ] 거래소 API 키 발급
- [ ] 백테스팅 데이터 수집
- [ ] 전략 설계 및 코딩
- [ ] Paper trading (모의 투자)

### Phase 2: 테스트 (2-4주)
- [ ] Dry-run 모드 실행
- [ ] 소액 실전 테스트
- [ ] 성과 모니터링
- [ ] 파라미터 최적화

### Phase 3: 운영 (지속)
- [ ] 실전 투자 시작
- [ ] 24/7 모니터링
- [ ] 정기적 리밸런싱
- [ ] 로그 분석 및 개선

---

## 8. 추천 학습 경로

1. **기초:** CCXT로 간단한 봇 만들기
2. **중급:** Freqtrade로 백테스팅
3. **고급:** Hummingbot으로 마켓 메이킹
4. **전문:** 자체 엔진 개발

---

## 9. 주의사항

⚠️ **리스크 경고:**
- 절대 손실 가능한 돈으로 시작하지 마세요
- 반드시 백테스팅을 먼저 하세요
- Dry-run 모드로 충분히 테스트하세요
- API 키는 안전하게 관리하세요
- 거래소 규정을 준수하세요

---

*이 가이드는 교육 목적으로 작성되었습니다.*
*모든 투자 결정은 본인의 책임입니다.*
