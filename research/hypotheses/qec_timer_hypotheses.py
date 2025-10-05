"""
QEC Timer Hypotheses Testing (H9-H11)
Test tempo tax, pressure blunders, and reactive cushion hypotheses
"""

import os
import json
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class HypothesisResult:
    """Result of hypothesis testing"""
    hypothesis_id: str
    hypothesis_name: str
    prediction: str
    data_needed: str
    metric: str
    result: str
    confidence: float
    evidence: Dict[str, Any]

class QECTimerHypothesisTester:
    """Test timer-based hypotheses H9-H11"""
    
    def __init__(self, logs_dir: str = "timer_hypotheses_logs"):
        self.logs_dir = logs_dir
        self.hypotheses = self._define_timer_hypotheses()
        
        # Create logs directory
        os.makedirs(logs_dir, exist_ok=True)
    
    def _define_timer_hypotheses(self) -> Dict[str, Dict[str, str]]:
        """Define timer-based hypotheses H9-H11"""
        return {
            "H9": {
                "name": "Tempo Tax Hypothesis",
                "prediction": "Longer White move 1 → larger Black eval after move 2",
                "data_needed": "Move 1 thinking time, Black eval after move 2",
                "metric": "Correlation between White move 1 time and Black eval gain"
            },
            "H10": {
                "name": "Pressure Blunders Hypothesis", 
                "prediction": "Sub-20s turns have ≥2× blunder odds",
                "data_needed": "Blunder rates under different time pressures",
                "metric": "Blunder rate ratio: <20s vs >20s"
            },
            "H11": {
                "name": "Reactive Cushion Hypothesis",
                "prediction": "Positions with many legal forced replies reduce pressure blunders",
                "data_needed": "Legal forced replies count, blunder rates under pressure",
                "metric": "Correlation between forced replies and pressure blunder reduction"
            }
        }
    
    def test_hypothesis_h9_tempo_tax(self, results: List[Dict]) -> HypothesisResult:
        """Test H9: Tempo Tax Hypothesis"""
        print("Testing H9: Tempo Tax Hypothesis")
        
        # Extract data
        white_move_1_times = []
        black_evals_after_move_2 = []
        
        for result in results:
            turn_logs = result.get('turn_logs', [])
            if len(turn_logs) >= 2:
                # White move 1 thinking time
                white_move_1 = turn_logs[0]
                if white_move_1['side'] == 'W':
                    white_move_1_times.append(white_move_1['think_ms'])
                    
                    # Black eval after move 2
                    black_move_2 = turn_logs[1]
                    if black_move_2['side'] == 'B':
                        black_evals_after_move_2.append(black_move_2['eval_after'])
        
        # Calculate correlation
        if len(white_move_1_times) > 1 and len(black_evals_after_move_2) > 1:
            correlation = np.corrcoef(white_move_1_times, black_evals_after_move_2)[0, 1]
            
            # Test significance (simplified)
            if abs(correlation) > 0.3:
                result_status = "CONFIRMED"
                confidence = min(0.95, abs(correlation) * 1.5)
            elif abs(correlation) > 0.1:
                result_status = "PARTIAL"
                confidence = abs(correlation) * 1.2
            else:
                result_status = "REJECTED"
                confidence = 0.1
        else:
            correlation = 0.0
            result_status = "INSUFFICIENT_DATA"
            confidence = 0.0
        
        evidence = {
            "correlation": correlation,
            "sample_size": len(white_move_1_times),
            "white_move_1_avg_time": np.mean(white_move_1_times) if white_move_1_times else 0,
            "black_eval_avg": np.mean(black_evals_after_move_2) if black_evals_after_move_2 else 0
        }
        
        return HypothesisResult(
            hypothesis_id="H9",
            hypothesis_name=self.hypotheses["H9"]["name"],
            prediction=self.hypotheses["H9"]["prediction"],
            data_needed=self.hypotheses["H9"]["data_needed"],
            metric=self.hypotheses["H9"]["metric"],
            result=result_status,
            confidence=confidence,
            evidence=evidence
        )
    
    def test_hypothesis_h10_pressure_blunders(self, results: List[Dict]) -> HypothesisResult:
        """Test H10: Pressure Blunders Hypothesis"""
        print("Testing H10: Pressure Blunders Hypothesis")
        
        # Extract blunder data
        blunders_under_20s = 0
        moves_under_20s = 0
        blunders_over_20s = 0
        moves_over_20s = 0
        
        for result in results:
            turn_logs = result.get('turn_logs', [])
            for log in turn_logs:
                if log['time_left_ms'] < 20000:  # Under 20s
                    moves_under_20s += 1
                    if log['blunder']:
                        blunders_under_20s += 1
                else:  # Over 20s
                    moves_over_20s += 1
                    if log['blunder']:
                        blunders_over_20s += 1
        
        # Calculate blunder rates
        blunder_rate_under_20s = blunders_under_20s / max(1, moves_under_20s)
        blunder_rate_over_20s = blunders_over_20s / max(1, moves_over_20s)
        
        # Calculate ratio
        if blunder_rate_over_20s > 0:
            blunder_ratio = blunder_rate_under_20s / blunder_rate_over_20s
        else:
            blunder_ratio = 0.0
        
        # Test hypothesis (≥2× blunder odds)
        if blunder_ratio >= 2.0:
            result_status = "CONFIRMED"
            confidence = min(0.95, blunder_ratio / 3.0)
        elif blunder_ratio >= 1.5:
            result_status = "PARTIAL"
            confidence = blunder_ratio / 2.0
        else:
            result_status = "REJECTED"
            confidence = 0.1
        
        evidence = {
            "blunder_rate_under_20s": blunder_rate_under_20s,
            "blunder_rate_over_20s": blunder_rate_over_20s,
            "blunder_ratio": blunder_ratio,
            "moves_under_20s": moves_under_20s,
            "moves_over_20s": moves_over_20s,
            "blunders_under_20s": blunders_under_20s,
            "blunders_over_20s": blunders_over_20s
        }
        
        return HypothesisResult(
            hypothesis_id="H10",
            hypothesis_name=self.hypotheses["H10"]["name"],
            prediction=self.hypotheses["H10"]["prediction"],
            data_needed=self.hypotheses["H10"]["data_needed"],
            metric=self.hypotheses["H10"]["metric"],
            result=result_status,
            confidence=confidence,
            evidence=evidence
        )
    
    def test_hypothesis_h11_reactive_cushion(self, results: List[Dict]) -> HypothesisResult:
        """Test H11: Reactive Cushion Hypothesis"""
        print("Testing H11: Reactive Cushion Hypothesis")
        
        # Extract data
        forced_replies_data = []
        blunder_rates = []
        
        for result in results:
            turn_logs = result.get('turn_logs', [])
            for log in turn_logs:
                if log['time_left_ms'] < 30000:  # Under pressure
                    # Count legal forced replies (simplified)
                    forced_replies = 1 if log['forced'] else 0
                    blunder = 1 if log['blunder'] else 0
                    
                    forced_replies_data.append(forced_replies)
                    blunder_rates.append(blunder)
        
        # Calculate correlation
        if len(forced_replies_data) > 1 and len(blunder_rates) > 1:
            correlation = np.corrcoef(forced_replies_data, blunder_rates)[0, 1]
            
            # Test significance
            if correlation < -0.2:  # Negative correlation expected
                result_status = "CONFIRMED"
                confidence = min(0.95, abs(correlation) * 2.0)
            elif correlation < -0.1:
                result_status = "PARTIAL"
                confidence = abs(correlation) * 1.5
            else:
                result_status = "REJECTED"
                confidence = 0.1
        else:
            correlation = 0.0
            result_status = "INSUFFICIENT_DATA"
            confidence = 0.0
        
        evidence = {
            "correlation": correlation,
            "sample_size": len(forced_replies_data),
            "avg_forced_replies": np.mean(forced_replies_data) if forced_replies_data else 0,
            "avg_blunder_rate": np.mean(blunder_rates) if blunder_rates else 0
        }
        
        return HypothesisResult(
            hypothesis_id="H11",
            hypothesis_name=self.hypotheses["H11"]["name"],
            prediction=self.hypotheses["H11"]["prediction"],
            data_needed=self.hypotheses["H11"]["data_needed"],
            metric=self.hypotheses["H11"]["metric"],
            result=result_status,
            confidence=confidence,
            evidence=evidence
        )
    
    def test_all_timer_hypotheses(self, results: List[Dict]) -> List[HypothesisResult]:
        """Test all timer-based hypotheses"""
        print("=== Testing Timer-Based Hypotheses (H9-H11) ===")
        
        hypothesis_results = []
        
        # Test H9: Tempo Tax
        h9_result = self.test_hypothesis_h9_tempo_tax(results)
        hypothesis_results.append(h9_result)
        
        # Test H10: Pressure Blunders
        h10_result = self.test_hypothesis_h10_pressure_blunders(results)
        hypothesis_results.append(h10_result)
        
        # Test H11: Reactive Cushion
        h11_result = self.test_hypothesis_h11_reactive_cushion(results)
        hypothesis_results.append(h11_result)
        
        # Save results
        self._save_hypothesis_results(hypothesis_results)
        
        # Print summary
        self._print_hypothesis_summary(hypothesis_results)
        
        return hypothesis_results
    
    def _save_hypothesis_results(self, results: List[HypothesisResult]):
        """Save hypothesis testing results"""
        results_file = os.path.join(self.logs_dir, "timer_hypotheses_results.json")
        with open(results_file, 'w') as f:
            json.dump([{
                "hypothesis_id": r.hypothesis_id,
                "hypothesis_name": r.hypothesis_name,
                "prediction": r.prediction,
                "data_needed": r.data_needed,
                "metric": r.metric,
                "result": r.result,
                "confidence": r.confidence,
                "evidence": r.evidence
            } for r in results], f, indent=2)
        
        print(f"Hypothesis results saved to {self.logs_dir}")
    
    def _print_hypothesis_summary(self, results: List[HypothesisResult]):
        """Print hypothesis testing summary"""
        print(f"\\n=== Timer Hypotheses Summary ===")
        
        for result in results:
            print(f"\\n{result.hypothesis_id}: {result.hypothesis_name}")
            print(f"  Prediction: {result.prediction}")
            print(f"  Result: {result.result}")
            print(f"  Confidence: {result.confidence:.2f}")
            print(f"  Evidence: {result.evidence}")
        
        # Overall summary
        confirmed = sum(1 for r in results if r.result == "CONFIRMED")
        partial = sum(1 for r in results if r.result == "PARTIAL")
        rejected = sum(1 for r in results if r.result == "REJECTED")
        
        print(f"\\nOverall Summary:")
        print(f"  Confirmed: {confirmed}")
        print(f"  Partial: {partial}")
        print(f"  Rejected: {rejected}")

if __name__ == "__main__":
    # Test timer hypotheses
    tester = QECTimerHypothesisTester()
    
    # Load results from rock-solid timer experiment
    results_file = "rock_solid_timer_logs/rock_solid_results.json"
    if os.path.exists(results_file):
        with open(results_file, 'r') as f:
            results = json.load(f)
        
        # Test hypotheses
        hypothesis_results = tester.test_all_timer_hypotheses(results)
    else:
        print("No results file found. Run rock-solid timer experiment first.")
