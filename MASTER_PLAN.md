# dongsu Ultimate Vision - Master Plan

## 최종 목표
**완전 자동화된 크립토 수익 플랫폼 구축**

---

## Phase 1: Trading Agent 훈련 (1-3개월)

### 1.1 매일 수행할 작업

```
⏰ 00:00 KST - 일일 차트 분석
⏰ 06:00 KST - 아시아 장 분석  
⏰ 12:00 KST - 유럽 장 분석
⏰ 20:00 KST - 미국 장 분석
⏰ 매 4시간 - 포지션 점검
```

### 1.2 매매일지 템플릿

```markdown
# Trading Journal - YYYY-MM-DD HH:MM

## 시장 상황
- BTC: $XX,XXX (X.XX%)
- ETH: $X,XXX (X.XX%)
- 공포/탐욕 지수: XX
- 주요 뉴스: 

## 진입 포지션
| 심볼 | 방향 | 진입가 | 목표가 | 손절가 | 근거 |
|------|------|--------|--------|--------|------|
| BTC | Long | $XX,XXX | $XX,XXX | $XX,XXX | EMA 크로스 + RSI |

## 시뮬레이션 결과
- 예상 수익률: X.XX%
- 리스크/리워드: 1:X
- 승률: XX%

## 회고
- 잘한 점:
- 개선할 점:
- 다음 전략 조정:
```

### 1.3 훈련 목표

| 단계 | 목표 | 기간 | 성과 기준 |
|------|------|------|----------|
| 1 | 전략 백테스팅 | 2주 | 100+ 시뮬레이션 |
| 2 | Paper Trading | 4주 | 승률 60%+ |
| 3 | 소액 실전 | 4주 | 승률 70%+ 수익률 + |
| 4 | 고도화 | 4주 | 승률 80%+ |

### 1.4 사용 전략 풀

```python
STRATEGIES = {
    "scalping": {
        "timeframe": "1m, 5m",
        "indicators": ["EMA9", "RSI", "Volume"],
        "target": "0.5-1%",
        "stop": "0.3%"
    },
    "day_trading": {
        "timeframe": "15m, 1h",
        "indicators": ["EMA9/21", "MACD", "Bollinger"],
        "target": "2-3%",
        "stop": "1%"
    },
    "swing": {
        "timeframe": "4h, 1d",
        "indicators": ["EMA50/200", "RSI", "Support/Resistance"],
        "target": "5-10%",
        "stop": "3%"
    }
}
```

---

## Phase 2: Research Agent (지속)

### 2.1 정보 수집 소스

| 카테고리 | 소스 | API | 비용 |
|----------|------|-----|------|
| **새 프로젝트** | Twitter, Discord, Telegram | Nitter, custom scraper | 묶 |
| **에어드랍** | Airdrops.io, Earndrop.io | Web scraping | 묶 |
| **TGE 일정** | CoinMarketCap, CoinGecko | CMC API, CG API | 묶/유료 |
| **온체인 데이터** | Dune Analytics, DeFiLlama | Dune API, LL API | 묶/유료 |
| **뉴스** | CoinDesk, TheBlock | RSS, API | 묶 |
| **GitHub** | Crypto repos | GitHub API | 묶 |
| **VC 투자** | Crunchbase, Dove Metrics | API | 유료 |

### 2.2 Dune Analytics 쿼리

```sql
-- 신규 토큰 발행 추적
SELECT 
    token_address,
    symbol,
    name,
    block_time as created_at,
    creator_address
FROM tokens_ethereum.erc20_tokens
WHERE block_time >= NOW() - INTERVAL '7' DAY
ORDER BY block_time DESC
```

### 2.3 일일 리포트 템플릿

```markdown
# Daily Alpha Report - YYYY-MM-DD

## 🆕 New Projects (24h)
| 프로젝트 | 체인 | TGE | VC | 특징 | 근거 |
|---------|------|-----|----|------|------|
| XXX | Solana | Q2 2025 | a16z | DePIN | GitHub 활발, 팀 검증 |

## 🎁 Airdrop Opportunities
| 프로젝트 | 예상 시기 | 조건 | 확률 | 근거 |
|---------|----------|------|------|------|
| YYY | 3월 | 테스트넷 참여 | 높음 | 공식 언급 |

## 📈 Trending (7d)
1. AI + Crypto
2. DePIN
3. RWA
4. L2 Scaling

## 🔍 On-Chain Signals
- ETH 유출량: XXX
- 신규 지갑: XXX
- 대형 거래: XXX
```

---

## Phase 3: On-Chain Analysis Agent

### 3.1 데이터 소스

```python
DATA_SOURCES = {
    "etherscan": {
        "api": "https://api.etherscan.io/api",
        "free_tier": "5 calls/sec",
        "paid_tier": "Starting $199/month"
    },
    "dune": {
        "api": "https://api.dune.com/api/v1",
        "free_tier": "4,000 credits/month",
        "paid_tier": "Starting $300/month"
    },
    "defillama": {
        "api": "https://api.llama.fi",
        "free": "Unlimited"
    },
    "thegraph": {
        "api": "Subgraph queries",
        "free": "100,000 queries/month"
    },
    "nansen": {
        "api": "Premium only",
        "cost": "$1,500+/month"
    }
}
```

### 3.2 분석 지표

| 지표 | 설명 | 데이터 소스 |
|------|------|------------|
| **Exchange Inflow/Outflow** | 거래소 입출금 | Glassnode, CryptoQuant |
| **Active Addresses** | 활성 지갑 수 | Dune, Etherscan |
| **Network Value to Transactions** | NVT Ratio | On-chain data |
| **MVRV Ratio** | 시가총액/실현가치 | Glassnode |
| **Funding Rate** | 선물 펀딩비율 | Binance, Bybit API |
| **Open Interest** | 미결제약정 | Coinglass |

---

## Phase 4: Platform & Monetization

### 4.1 서비스 구조

```
┌─────────────────────────────────────────────┐
│           dongsu Platform                   │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Trading    │  │    Simulation       │  │
│  │  Bot Store  │  │    Playground       │  │
│  │             │  │                     │  │
│  │ • Buy bots  │  │ • Backtest          │  │
│  │ • Rent bots │  │ • Paper trade       │  │
│  │ • Custom    │  │ • Optimize          │  │
│  └─────────────┘  └─────────────────────┘  │
│                                             │
│  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Alpha      │  │    Custom Bot       │  │
│  │  Terminal   │  │    Builder          │  │
│  │             │  │                     │  │
│  │ • New coins │  │ • Strategy config   │  │
│  │ • Airdrops  │  │ • Risk settings     │  │
│  │ • Trends    │  │ • Deploy            │  │
│  └─────────────┘  └─────────────────────┘  │
│                                             │
└─────────────────────────────────────────────┘
```

### 4.2 수익 모델

| 서비스 | 가격 | 타겟 |
|--------|------|------|
| **Trading Bot 구독** | $29-99/월 | 개인 트레이더 |
| **Alpha Report** | $19/월 | 투자자 |
| **Custom Bot 개발** | $500-2000 | 고급 사용자 |
| **Simulation API** | $0.01/콜 | 개발자 |
| **Bot Marketplace 수수료** | 10% | 플랫폼 |

---

## Multi-Agent Architecture

### 최종 구성

```
┌─────────────────────────────────────────────────────────┐
│              dongsu-orch (Orchestrator)                 │
│              Web Dashboard / Admin Panel                │
└─────────────────────────────────────────────────────────┘
                            │
        ┌──────────┬────────┼────────┬──────────┐
        ↓          ↓        ↓        ↓          ↓
   ┌────────┐ ┌────────┐ ┌──────┐ ┌──────┐ ┌──────────┐
   │Trading │ │Research│ │On-   │ │Social│ │Platform  │
   │  Agent │ │  Agent │ │Chain │ │ Agent│ │  Agent   │
   │        │ │        │ │Agent │ │      │ │          │
   │•Chart  │ │•New    │ │•Dune │ │•Molt │ │•Web      │
   │•Signal │ │  coins │ │•Scan │ │•Content│ │  dev    │
   │•Execute│ │•Airdrop│ │•News │ │•Engage│ │•Deploy   │
   │•Journal│ │•Trends │ │•Alert│ │      │ │•Monitor  │
   └────────┘ └────────┘ └──────┘ └──────┘ └──────────┘
```

### Agent별 상세

#### Trading Agent
```yaml
name: dongsu-trading
schedule:
  - "0 */4 * * *"  # 4시간마다 시그널 생성
  - "0 0 * * *"    # 일일 리포트
  - "0 * * * *"    # 포지션 모니터링
memory:
  - /memory/trading/journal/
  - /memory/trading/strategies/
  - /memory/trading/performance/
```

#### Research Agent
```yaml
name: dongsu-research
schedule:
  - "0 */6 * * *"  # 6시간마다 새 프로젝트 스캔
  - "0 9 * * *"    # 일일 알파 리포트
sources:
  - twitter
  - discord
  - github
  - defillama
  - dune
```

#### On-Chain Agent
```yaml
name: dongsu-onchain
schedule:
  - "*/15 * * * *" # 15분마다 온체인 데이터
  - "0 * * * *"    # 시간별 리포트
alerts:
  - whale_transactions
  - exchange_inflows
  - funding_rates
```

---

## 학습 로드맵 (지속)

### 매일 학습 주제 (자동 순환)

```python
LEARNING_TOPICS = [
    # Trading
    "Technical analysis patterns",
    "Risk management strategies",
    "Position sizing methods",
    "Market microstructure",
    "Order flow analysis",
    
    # DeFi/Crypto
    "New protocol mechanisms",
    "Tokenomics design",
    "Smart contract security",
    "MEV strategies",
    "Cross-chain bridges",
    
    # Data
    "On-chain metrics",
    "Dune query optimization",
    "API integration patterns",
    "Data visualization",
    
    # Platform
    "Next.js advanced patterns",
    "Database optimization",
    "API design",
    "Security best practices"
]
```

---

## Archive 구조

```
/root/.openclaw/workspace/
├── archive/
│   ├── trading/
│   │   ├── strategies/          # 백테스팅된 전략
│   │   ├── journals/            # 매매일지
│   │   ├── signals/             # 생성된 시그널
│   │   └── performance/         # 성과 분석
│   │
│   ├── research/
│   │   ├── projects/            # 프로젝트 리서치
│   │   ├── airdrops/            # 에어드랍 정보
│   │   ├── trends/              # 트렌드 분석
│   │   └── reports/             # 일일 리포트
│   │
│   ├── onchain/
│   │   ├── queries/             # Dune 쿼리
│   │   ├── alerts/              # 알림 기록
│   │   └── analysis/            # 분석 결과
│   │
│   └── learning/
│       ├── papers/              # 학습 자료
│       ├── code/                # 코드 스니펫
│       └── notes/               # 노트
│
├── agents/                      # Multi-agent 코드
│   ├── trading/
│   ├── research/
│   ├── onchain/
│   ├── social/
│   └── platform/
│
└── dashboard/                   # 관리 대시보드
    ├── web/
    └── api/
```

---

## 첫 7일 실행 계획

| 일차 | 작업 | 산출물 |
|------|------|--------|
| 1 | Trading Agent 구조 설정 | /agents/trading/ |
| 2 | 백테스팅 엔진 구현 | simulation engine |
| 3 | 매매일지 시스템 | journal template |
| 4 | 첫 시뮬레이션 10회 | 10 journal entries |
| 5 | Research Agent 설정 | /agents/research/ |
| 6 | 정보 소스 연결 | data pipeline |
| 7 | 통합 테스트 | end-to-end test |

---

## 승인 요청 사항

1. **Trading Agent 구현 승인?**
2. **Research Agent 정보 소스 설정 승인?**
3. **Multi-Agent 아키텍처 전환 승인?**
4. **Dashboard 개발 승인?**

---

*이 계획은 2026-02-25에 작성되었습니다.*
*매일 업데이트되며 학습 내용이 추가됩니다.*
