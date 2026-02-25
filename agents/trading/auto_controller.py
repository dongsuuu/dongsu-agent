"""
dongsu-auto-trading-controller
수시 자동 트레이딩 컨트롤러 - 스스로 판단하여 실행
"""

import time
import random
from datetime import datetime, timedelta
from typing import Optional
import json
import os

class AutoTradingController:
    """자동 트레이딩 컨트롤러 - 스스로 매매 타이밍 판단"""
    
    def __init__(self):
        self.last_check = None
        self.positions = []
        self.trade_count = 0
        self.running = True
        
        # Paper Trading 엔진 로드
        from paper_trading import PaperTradingEngine
        self.engine = PaperTradingEngine(initial_capital=10000)
        
        # Trading Agent 로드
        from core import TradingAgent
        self.agent = TradingAgent()
        
        # 학습 데이터
        self.learning = {
            "best_times": [],  # 수익 낸 시간대
            "worst_times": [],  # 손실 낸 시간대
            "successful_patterns": [],  # 성공한 패턴
            "failed_patterns": []  # 실패한 패턴
        }
    
    def should_trade_now(self, analysis_result: dict) -> tuple[bool, str]:
        """지금 매매해야 하는지 스스로 판단"""
        
        signals = analysis_result.get("signals", [])
        security = analysis_result.get("security_report", {})
        current_price = analysis_result.get("current_price", 0)
        
        # 1. 시그널이 없으면 매매하지 않음
        if not signals:
            return False, "시그널 없음 - 관망"
        
        # 2. 보안 리스크가 높으면 매매하지 않음
        risk_score = security.get("risk_score", 10)
        if risk_score >= 7:
            return False, f"보안 리스크 높음 ({risk_score}/10) - 관망"
        
        # 3. 승률이 높은 시그널만 선택
        best_signal = max(signals, key=lambda s: s.confidence)
        
        if best_signal.confidence < 0.65:
            return False, f"신뢰도 낮음 ({best_signal.confidence*100:.0f}%) - 관망"
        
        # 4. 리스크/리워드 비율 체크
        risk = abs(best_signal.stop_loss - best_signal.price)
        reward = abs(best_signal.target_price - best_signal.price)
        
        if risk == 0:
            return False, "리스크 계산 불가 - 관망"
        
        rr_ratio = reward / risk
        
        if rr_ratio < 1.5:
            return False, f"R/R 비율 낮음 ({rr_ratio:.2f}) - 관망"
        
        # 5. 모든 조건 충족 - 매매 실행
        return True, f"✅ 매매 조건 충족: 신뢰도 {best_signal.confidence*100:.0f}%, R/R {rr_ratio:.2f}"
    
    def check_and_trade(self, symbol: str = "ETH"):
        """분석 후 조건에 따라 매매"""
        now = datetime.now()
        
        print(f"\n{'='*60}")
        print(f"🔍 {now.strftime('%Y-%m-%d %H:%M:%S')} - {symbol} 분석 시작")
        print(f"{'='*60}")
        
        # 1. 시장 분석
        result = self.agent.analyze(symbol)
        
        # 2. 매매 판단
        should_trade, reason = self.should_trade_now(result)
        
        print(f"\n📊 판단: {reason}")
        
        if should_trade:
            # 매매 실행
            signals = result.get("signals", [])
            best_signal = max(signals, key=lambda s: s.confidence)
            
            # Paper Trading으로 포지션 진입
            trade = self.engine.open_position(
                symbol=symbol,
                direction="long" if best_signal.signal_type.value == "buy" else "short",
                entry_price=best_signal.price,
                target_price=best_signal.target_price,
                stop_loss=best_signal.stop_loss,
                confidence=best_signal.confidence
            )
            
            print(f"\n🎯 포지션 진입!")
            print(f"   심볼: {trade.symbol}")
            print(f"   방향: {trade.direction}")
            print(f"   진입가: ${trade.entry_price:.2f}")
            print(f"   목표가: ${trade.target_price:.2f}")
            print(f"   손절가: ${trade.stop_loss:.2f}")
            print(f"   수량: {trade.size:.4f}")
            
            self.trade_count += 1
            
            # 학습 데이터 기록
            self.learning["best_times"].append({
                "time": now.isoformat(),
                "symbol": symbol,
                "confidence": best_signal.confidence,
                "reason": reason
            })
        
        else:
            # 관망 - 학습 데이터 기록
            self.learning["failed_patterns"].append({
                "time": now.isoformat(),
                "symbol": symbol,
                "reason": reason
            })
        
        # 3. 기존 포지션 체크
        self.check_existing_positions(symbol, result.get("current_price", 0))
        
        # 4. 성과 리포트 출력
        report = self.engine.generate_report()
        print(f"\n📈 현재 성과:")
        print(f"   자본: ${report['capital']['current']:.2f} ({report['capital']['change_percent']:+.2f}%)")
        print(f"   승률: {report['trades']['win_rate']:.1f}%")
        print(f"   총 거래: {report['trades']['total']}회")
        print(f"   보유 포지션: {report['trades']['open_positions']}개")
        
        self.last_check = now
    
    def check_existing_positions(self, symbol: str, current_price: float):
        """기존 포지션 청산 체크"""
        for trade in self.engine.positions[:]:
            if trade.symbol != symbol:
                continue
            
            exit_price = None
            reason = None
            
            if trade.direction == "long":
                # 목표가 도달
                if current_price >= trade.target_price:
                    exit_price = trade.target_price
                    reason = "목표가 도달"
                # 손절가 도달
                elif current_price <= trade.stop_loss:
                    exit_price = trade.stop_loss
                    reason = "손절가 도달"
            else:  # short
                if current_price <= trade.target_price:
                    exit_price = trade.target_price
                    reason = "목표가 도달"
                elif current_price >= trade.stop_loss:
                    exit_price = trade.stop_loss
                    reason = "손절가 도달"
            
            if exit_price:
                closed = self.engine.close_position(trade.id, exit_price, reason)
                if closed:
                    print(f"\n🔴 포지션 청산: {reason}")
                    print(f"   PnL: ${closed.pnl:+.2f} ({closed.pnl_percent:+.2f}%)")
    
    def run_continuous(self, check_interval_minutes: int = 30):
        """지속적 실행 - 스스로 판단하여 매매"""
        print(f"🚀 자동 트레이딩 시작 (체크 주기: {check_interval_minutes}분)")
        print(f"   초기 자본: $10,000")
        print(f"   목표: 승률 80%+, 수익률 양수\n")
        
        while self.running:
            try:
                # ETH 분석 및 매매
                self.check_and_trade("ETH")
                
                # BTC도 분석
                self.check_and_trade("BTC")
                
                # 다음 체크까지 대기
                print(f"\n⏳ 다음 체크: {check_interval_minutes}분 후...")
                time.sleep(check_interval_minutes * 60)
                
            except KeyboardInterrupt:
                print("\n\n🛑 사용자 중단")
                self.running = False
                break
            except Exception as e:
                print(f"\n❌ 오류 발생: {e}")
                time.sleep(60)  # 오류 시 1분 후 재시도
        
        # 종료 리포트
        self.print_final_report()
    
    def print_final_report(self):
        """최종 리포트 출력"""
        report = self.engine.generate_report()
        
        print(f"\n{'='*60}")
        print(f"📊 최종 성과 리포트")
        print(f"{'='*60}")
        print(f"총 거래: {report['trades']['total']}회")
        print(f"승률: {report['trades']['win_rate']:.1f}%")
        print(f"최종 자본: ${report['capital']['current']:.2f}")
        print(f"총 수익: ${report['capital']['change']:+.2f} ({report['capital']['change_percent']:+.2f}%)")
        print(f"수익 팩터: {report['performance']['profit_factor']:.2f}")
        print(f"{'='*60}\n")

# 실행
if __name__ == "__main__":
    controller = AutoTradingController()
    
    # 30분마다 체크하며 스스로 매매 판단
    controller.run_continuous(check_interval_minutes=30)
