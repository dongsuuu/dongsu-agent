# DEV_RADAR_NOTES - 2026-02-25

## Trending Repos Analysis

### 1. Agent-X (crypto-trading-agent)

**URL:** https://github.com/topics/crypto-trading-agent

**What it does:**
- Self-evolving autonomous crypto trading bot
- LSTM price predictor + technical analysis hybrid
- 자기 진화하는 트레이딩 에이전트

**Why trending:**
- AI + 트레이딩 결합
- 자동 학습/적응 기능

**How to use:**
- 백테스팅 엔진 연결
- 실시간 데이터 파이프라인 구축
- 리스크 관리 모듈 추가

---

### 2. Kalshi Trading Bot

**URL:** https://github.com/topics/bot-trading

**What it does:**
- Kalshi 예측 마켓 자동화
- Copy trading + arbitrage strategies
- 오픈소스, 물리 인터페이스

**Why trending:**
- 예측 마켓(Polymarket 유사) 자동화
- 물리 사용 가능

**How to use:**
- Polymarket/Kalshi API 연결
- 시그널 소스 다변화
- 자동 배팅/헤징 로직

---

### 3. AI Trading Bot (Multi-exchange)

**URL:** https://github.com/topics/ai-trading

**What it does:**
- Binance, Hyperliquid 등 15+ 거래소 지원
- AI, Grid, DCA, TradingView 전략
- 물리 오픈소스

**Why trending:**
- 다중 거래소 지원
- 다양한 전략 템플릿

**How to use:**
- dongsu-website에 차트 연동
- WebSocket 실시간 데이터
- 자동 주문 실행 모듈

---

### 4. Market Making Bot

**URL:** https://github.com/topics/crypto-bot

**What it does:**
- Self-hosted market-making
- Volume, spread, liquidity 관리
- Dynamic order books

**Why trending:**
- 토큰 발행자/프로젝트 운영자용
- 유동성 공급 자동화

**How to use:**
- ACP 서비스에 유동성 관리 추가
- 수수료 수익 모델

---

### 5. Telegram Copy Trading Bot

**URL:** https://github.com/topics/copy-trade

**What it does:**
- Telegram 기반 copy trading
- Multi-exchange support
- GPT signal analysis
- Automated execution

**Why trending:**
- 소셜 트레이딩 + AI 분석
- Telegram 인터페이스

**How to use:**
- @virtualdongsubot에 연동
- Moltbook 에이전트 시그널 공유
- 자동 복제 트레이딩

---

## Key Insights

| Trend | Description | Opportunity |
|-------|-------------|-------------|
| AI + Trading | LSTM, GPT 기반 예측 | 차트 예측 모듈 추가 |
| Multi-exchange | 15+ 거래소 지원 | arbitrage 기회 포착 |
| Social Trading | Copy trading, Telegram | Moltbook 연동 |
| Market Making | 유동성 공급 자동화 | ACP 서비스 확장 |
| Prediction Markets | Kalshi, Polymarket | 새로운 데이터 소스 |

---

## Experiment Ideas

### EXP-001: AI Signal Integration
- **Goal:** GPT/LSTM 기반 시그널 생성
- **Prep:** OpenAI API, historical data
- **Steps:**
  1. 과거 데이터 학습
  2. 실시간 예측 모델 구축
  3. 차트에 예측선 표시
- **Success Metric:** 예측 정확도 > 60%
- **Risk:** Overfitting, API 비용

### EXP-002: Multi-Exchange Arbitrage
- **Goal:** 거래소 간 가격 차이 포착
- **Prep:** Binance, Coinbase API keys
- **Steps:**
  1. 실시간 가격 모니터링
  2. 차익 기회 알림
  3. 자동 실행 (선택)
- **Success Metric:** 월 수익률 > 2%
- **Risk:** 거래소 지연, 수수료

### EXP-003: Telegram Signal Bot
- **Goal:** Moltbook 시그널 자동 공유
- **Prep:** @virtualdongsubot 연동
- **Steps:**
  1. 시그널 생성 로직
  2. Telegram 메시지 포맷
  3. 구독자 관리
- **Success Metric:** 구독자 10명+
- **Risk:** 스팸, 정확도
