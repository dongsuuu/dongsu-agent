# Multi-Agent Architecture for dongsu

## 개요
단일 Agent를 5개의 전문화된 Agent로 분할하여 각 영역의 깊이를 극대화

## Agent 구성

### 1. dongsu-trading (Trading Agent)
**역할:** 모든 트레이딩 관련 업무

**기능:**
- Freqtrade 전략 개발
- Hummingbot 마켓메이킹
- 백테스팅 엔진
- 실시간 시그널 생성
- 리스크 관리

**전문 도구:**
- TA-Lib
- CCXT
- WebSocket feeds
- Portfolio optimizers

**입력:**
```json
{
  "task": "backtest",
  "strategy": "ema_cross",
  "symbol": "BTC",
  "timeframe": "1h",
  "params": {"fast": 9, "slow": 21}
}
```

**출력:**
```json
{
  "sharpe": 1.45,
  "max_drawdown": 0.12,
  "total_return": 0.34,
  "trades": 156,
  "win_rate": 0.58
}
```

---

### 2. dongsu-acp (ACP Agent)
**역할:** Virtuals ACP 마켓플레이스 운영

**기능:**
- 10개 서비스 실행
- Agent 평가/분석
- 크레딧 시스템 관리
- 메시 라우팅
- 고객 지원

**전문 도구:**
- ACP API
- Agent registry
- Evaluation frameworks
- Credit ledger

**서비스 목록:**
1. token_quick_scan_base
2. agent_evaluation_suite
3. portfolio_health_check
4. agent_marketplace_navigator
5. agent_troubleshooter
6. agent_automation_hub
7. agent_credit_system
8. acp_mesh_router
9. grid_meta_agent
10. agent_finder

---

### 3. dongsu-web (Web Agent)
**역할:** 웹사이트 개발/운영

**기능:**
- Next.js 개발
- 차트 구현
- SEO 최적화
- 배포 관리
- 성능 모니터링

**전문 도구:**
- Next.js 14
- TradingView Charts
- Tailwind CSS
- Vercel API
- Lighthouse

**담당 페이지:**
- / (홈)
- /charts (차트)
- /evaluation (평가)
- /docs (문서)

---

### 4. dongsu-social (Social Agent)
**역할:** 소셜 미디어/커뮤니티 관리

**기능:**
- Moltbook 콘텐츠 생성
- 댓글/답글 자동화
- 팔로워 engagement
- 트렌드 분석
- 알림 관리

**전문 도구:**
- Moltbook API
- Content templates
- Engagement analytics
- Cron scheduler

**작업 주기:**
- 콘텐츠: 2시간
- 댓글 모니터: 30분
- engagement: 4시간

---

### 5. dongsu-research (Research Agent)
**역할:** 지속적 학습/리서치

**기능:**
- 시장 동향 분석
- GitHub 트렌딩
- 신규 프로토콜 리서치
- 문서화
- 지식베이스 관리

**전문 도구:**
- Web search APIs
- GitHub API
- Academic papers
- News aggregators
- Vector DB

**학습 주제:**
- DeFi protocols
- Trading strategies
- Smart contracts
- AI/ML papers
- Market microstructure

---

## Orchestrator (dongsu-orch)

**역할:** 모든 Agent 조율

**기능:**
- 요청 라우팅
- 컨텍스트 공유
- 메모리 동기화
- 충돌 해결
- 결과 통합

**라우팅 로직:**
```python
def route_request(user_input: str) -> Agent:
    if contains_trading_keywords(user_input):
        return dongsu_trading
    elif contains_acp_keywords(user_input):
        return dongsu_acp
    elif contains_web_keywords(user_input):
        return dongsu_web
    elif contains_social_keywords(user_input):
        return dongsu_social
    else:
        return dongsu_research
```

---

## 메모리 공유 시스템

```
┌─────────────────────────────────────┐
│        Shared Memory Store          │
├─────────────────────────────────────┤
│  /memory/trading/                   │
│    - strategies/                    │
│    - backtests/                     │
│    - signals/                       │
│                                     │
│  /memory/acp/                       │
│    - services/                      │
│    - evaluations/                   │
│    - credits/                       │
│                                     │
│  /memory/web/                       │
│    - components/                    │
│    - deployments/                   │
│    - analytics/                     │
│                                     │
│  /memory/social/                    │
│    - content/                       │
│    - engagement/                    │
│    - followers/                     │
│                                     │
│  /memory/research/                  │
│    - findings/                      │
│    - papers/                        │
│    - trends/                        │
└─────────────────────────────────────┘
```

---

## 통신 프로토콜

```python
class AgentMessage:
    def __init__(self):
        self.from_agent: str
        self.to_agent: str
        self.message_type: str  # request, response, broadcast
        self.payload: dict
        self.context: dict  # shared memory refs
        self.priority: int  # 1-5
        self.timestamp: datetime
```

---

## 장점 요약

| 영역 | 개선 효과 |
|------|----------|
| **전문성** | 각 Agent가 한 분야에 깊이 있게 |
| **병렬처리** | 여러 작업 동시 실행 |
| **장애 격리** | 한 Agent 문제가 다른 Agent에 영향 없음 |
| **확장성** | 새 Agent 쉽게 추가 |
| **학습** | 각자 분야에 맞는 학습 집중 |

---

## 구현 우선순위

### Phase 1: 2개 Agent 분할 (1주)
- [ ] dongsu-trading 분리
- [ ] dongsu-orch 구현
- [ ] 메모리 공유 시스템

### Phase 2: 3개 Agent (2주)
- [ ] dongsu-acp 분리
- [ ] dongsu-web 분리

### Phase 3: 5개 Agent 완성 (3주)
- [ ] dongsu-social 분리
- [ ] dongsu-research 분리
- [ ] 고급 오케스트레이션

---

## 비용 분석

| 구성 | 예상 비용/월 |
|------|------------|
| 단일 Agent | $50-100 |
| 5-Agent 시스템 | $200-400 |
| 추가 인프라 | $50-100 |
| **총계** | **$250-500** |

---

## 결론

**Multi-Agent가 더 고도화될 수 있습니다.**

이유:
1. 각 영역의 깊이 있는 전문성
2. 병렬 처리로 효율성 증가
3. 장애 격리로 안정성 향상
4. 지속적 학습의 질적 향상

단점은 복잡도와 비용 증가입니다.
