"""
dongsu-monitoring-agent
오류 감지, 로깅, 자동 개선 시스템
"""

import os
import sys
import json
import traceback
from datetime import datetime
from typing import Dict, List, Optional

class ErrorMonitor:
    """오류 모니터링 및 개선 추적"""
    
    def __init__(self, base_path: str = "/root/.openclaw/workspace"):
        self.base_path = base_path
        self.log_path = os.path.join(base_path, "archive", "monitoring")
        os.makedirs(self.log_path, exist_ok=True)
        
        self.error_history = []
        self.improvement_log = []
    
    def log_error(self, component: str, error: Exception, context: Dict = None):
        """오류 기록"""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {}
        }
        
        self.error_history.append(error_entry)
        
        # 파일에 저장
        log_file = os.path.join(self.log_path, f"errors_{datetime.now().strftime('%Y-%m')}.json")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(error_entry, ensure_ascii=False) + "\n")
        
        # 심각한 오류는 즉시 알림
        if self._is_critical_error(error):
            self._alert_critical(error_entry)
        
        return error_entry
    
    def log_improvement(self, component: str, description: str, before: str, after: str):
        """개선 사항 기록"""
        improvement = {
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "description": description,
            "before": before,
            "after": after
        }
        
        self.improvement_log.append(improvement)
        
        # 파일에 저장
        log_file = os.path.join(self.log_path, f"improvements_{datetime.now().strftime('%Y-%m')}.json")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(improvement, ensure_ascii=False) + "\n")
        
        return improvement
    
    def _is_critical_error(self, error: Exception) -> bool:
        """심각한 오류 판단"""
        critical_types = [
            "ConnectionError",
            "TimeoutError",
            "MemoryError",
            "KeyError",
            "IndexError"
        ]
        return type(error).__name__ in critical_types
    
    def _alert_critical(self, error_entry: Dict):
        """심각한 오류 알림"""
        print(f"""
🚨 CRITICAL ERROR DETECTED 🚨

Component: {error_entry['component']}
Error: {error_entry['error_type']}
Message: {error_entry['error_message']}
Time: {error_entry['timestamp']}

Immediate action required!
""")
    
    def generate_report(self) -> str:
        """모니터링 리포트 생성"""
        now = datetime.now()
        
        # 최근 24시간 오류
        recent_errors = [
            e for e in self.error_history
            if (now - datetime.fromisoformat(e['timestamp'])).days < 1
        ]
        
        # 최근 개선
        recent_improvements = [
            i for i in self.improvement_log
            if (now - datetime.fromisoformat(i['timestamp'])).days < 1
        ]
        
        report = f"""# Monitoring Report - {now.strftime('%Y-%m-%d %H:%M')}

## 📊 오류 현황 (24h)
- 총 오류: {len(recent_errors)}건
- 심각 오류: {len([e for e in recent_errors if self._is_critical_error(Exception(e['error_message']))])}건

### 오류 유형 분포
"""
        
        error_types = {}
        for e in recent_errors:
            et = e['error_type']
            error_types[et] = error_types.get(et, 0) + 1
        
        for et, count in sorted(error_types.items(), key=lambda x: -x[1]):
            report += f"- {et}: {count}건\n"
        
        report += f"""

## 🔧 개선 사항 (24h)
- 총 개선: {len(recent_improvements)}건

"""
        
        for imp in recent_improvements[-5:]:  # 최근 5개
            report += f"- [{imp['component']}] {imp['description']}\n"
        
        report += """

## 📈 시스템 상태
"""
        
        if len(recent_errors) == 0:
            report += "✅ 정상 작동 중\n"
        elif len(recent_errors) < 5:
            report += "⚠️ 경미한 오류 발생\n"
        else:
            report += "🔴 주의 필요 - 오류 다발\n"
        
        return report

class SimulationValidator:
    """시뮬레이션 검증 및 피드백"""
    
    def __init__(self):
        self.simulation_results = []
        self.validation_rules = [
            self._check_price_realistic,
            self._check_signal_logic,
            self._check_risk_reward_ratio,
            self._check_position_size
        ]
    
    def validate_simulation(self, result: Dict) -> List[str]:
        """시뮬레이션 결과 검증"""
        issues = []
        
        for rule in self.validation_rules:
            issue = rule(result)
            if issue:
                issues.append(issue)
        
        return issues
    
    def _check_price_realistic(self, result: Dict) -> Optional[str]:
        """가격 현실성 검증"""
        price = result.get('current_price', 0)
        symbol = result.get('symbol', '')
        
        # BTC: $10,000 ~ $200,000
        # ETH: $500 ~ $10,000
        if symbol == 'BTC' and not (10000 <= price <= 200000):
            return f"BTC 가격 비정상: ${price}"
        elif symbol == 'ETH' and not (500 <= price <= 10000):
            return f"ETH 가격 비정상: ${price}"
        
        return None
    
    def _check_signal_logic(self, result: Dict) -> Optional[str]:
        """시그널 로직 검증"""
        signals = result.get('signals', [])
        
        for signal in signals:
            # 진입가 < 목표가 (BUY) 또는 진입가 > 목표가 (SELL)
            if signal.signal_type.value == 'buy':
                if signal.price >= signal.target_price:
                    return f"BUY 시그널: 진입가({signal.price}) >= 목표가({signal.target_price})"
            elif signal.signal_type.value == 'sell':
                if signal.price <= signal.target_price:
                    return f"SELL 시그널: 진입가({signal.price}) <= 목표가({signal.target_price})"
        
        return None
    
    def _check_risk_reward_ratio(self, result: Dict) -> Optional[str]:
        """리스크/리워드 비율 검증"""
        signals = result.get('signals', [])
        
        for signal in signals:
            risk = abs(signal.stop_loss - signal.price)
            reward = abs(signal.target_price - signal.price)
            
            if risk == 0:
                return "손절가 = 진입가 (리스크 0)"
            
            ratio = reward / risk
            if ratio < 1:
                return f"R/R 비율 낮음: {ratio:.2f} (권장: 1.5 이상)"
        
        return None
    
    def _check_position_size(self, result: Dict) -> Optional[str]:
        """포지션 크기 검증"""
        # TODO: 포지션 사이징 로직 추가
        return None

# 전역 모니터 인스턴스
monitor = ErrorMonitor()
validator = SimulationValidator()

def track_execution(component: str):
    """함수 실행 추적 데코레이터"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                
                # 시뮬레이션 결과 검증
                if isinstance(result, dict) and 'signals' in result:
                    issues = validator.validate_simulation(result)
                    if issues:
                        for issue in issues:
                            monitor.log_error(component, Exception(issue), {"type": "validation"})
                
                return result
                
            except Exception as e:
                monitor.log_error(component, e, {
                    "args": str(args),
                    "kwargs": str(kwargs)
                })
                raise
        
        return wrapper
    return decorator

if __name__ == "__main__":
    # 테스트
    print(monitor.generate_report())
