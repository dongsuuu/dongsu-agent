# AutoBot Generator - 시스템 설계

## 개요
자연어 명령어 하나로 트레이딩 봇을 자동 생성, 백테스팅, 배포하는 시스템

## 사용자 명령어 예시

```bash
# 기본 명령어
/create-bot "BTC 5분봉 EMA 골든크로스 롱전략"

# 고급 명령어
/create-bot "ETH 1시간 RSI 과매도 반등, 손절 3%, 익절 6%, 투자금액 $1000"

# 복합 전략
/create-bot "SOL 15분봉 볼린저밴드 + MACD 확인, 트레일링스탑 2%"

# 자동 최적화
/create-bot "XRP 30분봉 추세추종, 하이퍼옵트로 파라미터 최적화"
```

## 시스템 흐름

```
┌─────────────────────────────────────────────────────────────┐
│                    AutoBot Generator                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   NLP Parser │───→│   Strategy   │───→│    Code      │  │
│  │   (자연어)   │    │   Builder    │    │   Generator  │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │          │
│         ↓                   ↓                   ↓          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Intent     │    │   Template   │    │   Python     │  │
│  │   Extractor  │    │   Selector   │    │   Code       │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Backtest    │───→│   Deploy     │───→│   Monitor    │  │
│  │   Engine     │    │   Manager    │    │   Dashboard  │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 핵심 컴포넌트

### 1. NLP Parser (자연어 분석기)

```python
class NLParser:
    """자연어 명령어를 파싱하여 구조화된 데이터로 변환"""
    
    def parse(self, command: str) -> dict:
        """
        입력: "BTC 5분봉 EMA 골든크로스 롱전략"
        출력: {
            "symbol": "BTC",
            "timeframe": "5m",
            "strategy_type": "trend_following",
            "indicators": ["ema"],
            "signal_type": "golden_cross",
            "position": "long"
        }
        """
        
        # 토큰화
        tokens = self.tokenize(command)
        
        # 엔티티 추출
        entities = {
            "symbol": self.extract_symbol(tokens),
            "timeframe": self.extract_timeframe(tokens),
            "strategy": self.extract_strategy(tokens),
            "risk_params": self.extract_risk(tokens),
            "indicators": self.extract_indicators(tokens)
        }
        
        return entities
    
    def extract_symbol(self, tokens):
        # BTC, ETH, SOL 등 식별
        symbols = ["BTC", "ETH", "SOL", "XRP", "ADA", "DOT", "LINK"]
        for token in tokens:
            if token.upper() in symbols:
                return token.upper()
        return "BTC"  # 기본값
    
    def extract_timeframe(self, tokens):
        # 1분, 5분, 1시간 등 식별
        timeframe_map = {
            "1분": "1m", "5분": "5m", "15분": "15m",
            "30분": "30m", "1시간": "1h", "4시간": "4h",
            "일봉": "1d", "주봉": "1w"
        }
        for token in tokens:
            if token in timeframe_map:
                return timeframe_map[token]
        return "5m"  # 기본값
    
    def extract_strategy(self, tokens):
        strategies = {
            "골든크로스": "golden_cross",
            "데드크로스": "dead_cross",
            "과매도": "oversold",
            "과매수": "overbought",
            "추세": "trend_following",
            "반등": "mean_reversion",
            "돌파": "breakout"
        }
        for token in tokens:
            if token in strategies:
                return strategies[token]
        return "trend_following"
```

### 2. Strategy Builder (전략 빌더)

```python
class StrategyBuilder:
    """파싱된 데이터로부터 전략 코드 생성"""
    
    TEMPLATES = {
        "golden_cross": {
            "indicators": ["ema_fast", "ema_slow"],
            "entry": "ema_fast > ema_slow and ema_fast.shift(1) <= ema_slow.shift(1)",
            "exit": "ema_fast < ema_slow"
        },
        "oversold": {
            "indicators": ["rsi", "bb_lower"],
            "entry": "rsi < 30 and close < bb_lower",
            "exit": "rsi > 70 or close > bb_middle"
        },
        "breakout": {
            "indicators": ["resistance", "volume"],
            "entry": "close > resistance and volume > volume_sma * 1.5",
            "exit": "close < support"
        }
    }
    
    def build(self, parsed_data: dict) -> dict:
        strategy_type = parsed_data["strategy"]
        template = self.TEMPLATES.get(strategy_type, self.TEMPLATES["golden_cross"])
        
        return {
            "name": f"{parsed_data['symbol']}_{strategy_type}_{parsed_data['timeframe']}",
            "symbol": parsed_data["symbol"],
            "timeframe": parsed_data["timeframe"],
            "indicators": template["indicators"],
            "entry_condition": template["entry"],
            "exit_condition": template["exit"],
            "risk_params": parsed_data.get("risk_params", {})
        }
```

### 3. Code Generator (코드 생성기)

```python
class CodeGenerator:
    """전략 사양으로부터 실행 가능한 Python 코드 생성"""
    
    def generate(self, strategy_spec: dict) -> str:
        template = '''
from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class {class_name}(IStrategy):
    """
    {description}
    Auto-generated by AutoBot Generator
    """
    
    # 전략 파라미터
    INTERFACE_VERSION = 3
    timeframe = '{timeframe}'
    stoploss = {stoploss}
    
    # ROI 설정
    minimal_roi = {minimal_roi}
    
    # 트레일링 스탑
    trailing_stop = {trailing_stop}
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        {indicators_code}
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            ({entry_condition}),
            'enter_long'
        ] = 1
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            ({exit_condition}),
            'exit_long'
        ] = 1
        return dataframe
'''
        
        return template.format(
            class_name=strategy_spec["name"],
            description=f"{strategy_spec['symbol']} {strategy_spec['timeframe']} auto strategy",
            timeframe=strategy_spec["timeframe"],
            stoploss=strategy_spec["risk_params"].get("stoploss", -0.03),
            minimal_roi=str(strategy_spec["risk_params"].get("minimal_roi", {"60": 0.01, "30": 0.02, "0": 0.04})),
            trailing_stop=strategy_spec["risk_params"].get("trailing_stop", False),
            indicators_code=self._generate_indicators(strategy_spec["indicators"]),
            entry_condition=strategy_spec["entry_condition"],
            exit_condition=strategy_spec["exit_condition"]
        )
    
    def _generate_indicators(self, indicators: list) -> str:
        code_lines = []
        for ind in indicators:
            if ind == "ema_fast":
                code_lines.append("dataframe['ema_fast'] = ta.EMA(dataframe, timeperiod=9)")
            elif ind == "ema_slow":
                code_lines.append("dataframe['ema_slow'] = ta.EMA(dataframe, timeperiod=21)")
            elif ind == "rsi":
                code_lines.append("dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)")
            elif ind == "bb_lower":
                code_lines.append("dataframe['bb_upper'], dataframe['bb_middle'], dataframe['bb_lower'] = ta.BBANDS(dataframe['close'])")
        return "\n        ".join(code_lines)
```

### 4. Auto Deployment (자동 배포)

```python
class AutoDeployer:
    """생성된 봇을 자동으로 배포하고 실행"""
    
    def deploy(self, bot_code: str, config: dict) -> str:
        # 1. 고유 ID 생성
        bot_id = f"bot_{uuid.uuid4().hex[:8]}"
        
        # 2. 파일 저장
        bot_path = f"/bots/{bot_id}/strategy.py"
        self._save_code(bot_path, bot_code)
        
        # 3. 설정 파일 생성
        config_path = f"/bots/{bot_id}/config.json"
        self._create_config(config_path, config)
        
        # 4. Docker 컨테이너 생성
        container_id = self._create_container(bot_id, bot_path, config_path)
        
        # 5. 백테스팅 실행
        backtest_result = self._run_backtest(bot_id)
        
        # 6. 실전 모드 시작 (사용자 승인 후)
        if backtest_result["profit"] > 0:
            self._start_live_trading(bot_id)
        
        return {
            "bot_id": bot_id,
            "status": "running" if backtest_result["profit"] > 0 else "backtest_failed",
            "backtest_result": backtest_result,
            "dashboard_url": f"https://dashboard.autobot.com/{bot_id}"
        }
```

## 사용자 인터페이스

### Telegram 봇 명령어

```
/createbot - 새 봇 생성
/mybots - 내 봇 목록
/stopbot [ID] - 봇 중지
/stats [ID] - 봇 성과
/backtest [ID] - 백테스팅 재실행
```

### 웹 대시보드

```
https://dashboard.autobot.com
- 실시간 P&L 차트
- 활성 포지션
- 거래 내역
- 봇 설정 수정
- 알림 설정
```

## 수익화 모델

| 플랜 | 가격 | 기능 |
|------|------|------|
| Free | $0 | 월 1개 봇, 기본 전략 |
| Pro | $29/월 | 무제한 봇, 고급 전략, 백테스팅 |
| Enterprise | $99/월 | 커스텀 개발, API 접근, 우선 지원 |

## 구현 로드맵

### Phase 1: MVP (2-4주)
- [ ] NLP 파서 구현
- [ ] 3개 기본 전략 템플릿
- [ ] 코드 생성기
- [ ] Telegram 봇 인터페이스

### Phase 2: Beta (4-8주)
- [ ] 10+ 전략 템플릿
- [ ] 백테스팅 엔진
- [ ] 웹 대시보드
- [ ] Paper trading

### Phase 3: Launch (8-12주)
- [ ] 실전 트레이딩
- [ ] 결제 시스템
- [ ] 커뮤니티 기능
- [ ] 고급 최적화 (Hyperopt)

### Phase 4: Scale (12주+)
- [ ] 머신러닝 전략 생성
- [ ] 소셜 트레이딩
- [ ] 모바일 앱
- [ ] 기관용 솔루션
