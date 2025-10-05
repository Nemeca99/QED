"""
QEC Rock-Solid Timer System
Comprehensive time management with measurable effects and validation
"""

import os
import json
import time
import random
import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
from enum import Enum

class TimePressure(Enum):
    LOW = "low"          # > 2 minutes
    MEDIUM = "medium"    # 1-2 minutes  
    HIGH = "high"        # 30s-1min
    CRITICAL = "critical" # < 30s
    BLITZ = "blitz"      # < 20s

@dataclass
class TurnLog:
    """Per-turn logging with comprehensive time data"""
    turn_id: int
    side: str
    think_ms: int
    time_left_ms: int
    decision_quality: float  # 0-1 scale
    primary: str
    forced: str
    react: str
    eval_before: float
    eval_after: float
    eval_drop: float
    pressure_level: str
    blunder: bool
    expected_think_ms: int
    actual_vs_expected: float

@dataclass
class TimeMetrics:
    """Comprehensive time-based metrics"""
    # Opening tempo swings
    delta_time_after_move_1: float
    delta_time_after_move_2: float
    delta_time_after_move_3: float
    
    # Pressure events
    pressure_events_under_20s: int
    pressure_events_under_30s: int
    pressure_events_under_60s: int
    
    # Blunder analysis
    blunder_rate_overall: float
    blunder_rate_under_20s: float
    blunder_rate_under_30s: float
    blunder_rate_under_60s: float
    
    # Speed/accuracy curve
    speed_accuracy_curve: Dict[str, Dict[str, float]]
    
    # Color-time advantage
    color_time_advantage_move_5: float
    color_time_advantage_move_10: float
    color_time_advantage_move_20: float
    
    # Archetype pacing
    archetype_pacing: Dict[str, Dict[str, float]]

class QECRockSolidTimer:
    """Rock-solid timer with comprehensive validation and metrics"""
    
    def __init__(self, logs_dir: str = "rock_solid_timer_logs"):
        self.logs_dir = logs_dir
        self.turn_time_limit = 180000  # 3 minutes in milliseconds
        self.white_time_left = self.turn_time_limit
        self.black_time_left = self.turn_time_limit
        self.game_count = 0
        
        # Time pressure thresholds
        self.pressure_thresholds = {
            TimePressure.LOW: 120000,      # 2 minutes
            TimePressure.MEDIUM: 60000,    # 1 minute
            TimePressure.HIGH: 30000,      # 30 seconds
            TimePressure.CRITICAL: 20000,  # 20 seconds
            TimePressure.BLITZ: 10000      # 10 seconds
        }
        
        # Blunder thresholds
        self.blunder_thresholds = {
            'overall': -150,      # -150 centipawns
            'under_20s': -200,    # -200 centipawns under pressure
            'under_30s': -175,    # -175 centipawns under pressure
            'under_60s': -160     # -160 centipawns under pressure
        }
        
        # Create logs directory
        os.makedirs(logs_dir, exist_ok=True)
    
    def start_turn(self, side: str) -> Tuple[float, str, int]:
        """Start turn and return (decision_quality, pressure_level, time_left_ms)"""
        time_left = self.white_time_left if side == "W" else self.black_time_left
        
        # Determine pressure level
        pressure_level = self._get_pressure_level(time_left)
        
        # Calculate decision quality based on time pressure
        decision_quality = self._calculate_decision_quality(time_left)
        
        return decision_quality, pressure_level.value, time_left
    
    def end_turn(self, side: str, think_ms: int, eval_before: float, eval_after: float):
        """End turn and update time state"""
        time_left = self.white_time_left if side == "W" else self.black_time_left
        
        # Update time (ensure no drift)
        new_time_left = max(0, time_left - think_ms)
        
        if side == "W":
            self.white_time_left = new_time_left
        else:
            self.black_time_left = new_time_left
    
    def _get_pressure_level(self, time_left_ms: int) -> TimePressure:
        """Get pressure level based on remaining time"""
        if time_left_ms >= self.pressure_thresholds[TimePressure.LOW]:
            return TimePressure.LOW
        elif time_left_ms >= self.pressure_thresholds[TimePressure.MEDIUM]:
            return TimePressure.MEDIUM
        elif time_left_ms >= self.pressure_thresholds[TimePressure.HIGH]:
            return TimePressure.HIGH
        elif time_left_ms >= self.pressure_thresholds[TimePressure.CRITICAL]:
            return TimePressure.CRITICAL
        else:
            return TimePressure.BLITZ
    
    def _calculate_decision_quality(self, time_left_ms: int) -> float:
        """Calculate decision quality based on time pressure"""
        if time_left_ms >= 120000:  # > 2 minutes
            return 1.0
        elif time_left_ms >= 60000:  # 1-2 minutes
            return 0.95
        elif time_left_ms >= 30000:  # 30s-1min
            return 0.85
        elif time_left_ms >= 20000:  # 20-30s
            return 0.70
        else:  # < 20s
            return 0.50
    
    def calculate_expected_think_time(self, side: str, position_complexity: float, 
                                    move_complexity: float) -> int:
        """Calculate expected thinking time for move"""
        # Base thinking time
        base_time = 10000 + (position_complexity * 30000) + (move_complexity * 20000)
        
        # Adjust for time pressure
        time_left = self.white_time_left if side == "W" else self.black_time_left
        if time_left < 30000:  # < 30s
            base_time *= 0.5
        elif time_left < 60000:  # < 1min
            base_time *= 0.7
        
        return int(base_time)
    
    def apply_eval_penalty_for_time(self, eval: float, side: str) -> float:
        """Apply evaluation penalty for time pressure"""
        time_left = self.white_time_left if side == "W" else self.black_time_left
        pressure_factor = 1.0 - self._calculate_decision_quality(time_left)
        
        # Penalty scales with pressure
        penalty = pressure_factor * 50  # Up to 50 centipawns penalty
        return eval - penalty
    
    def should_cutoff_search(self, side: str, current_depth: int) -> bool:
        """Determine if search should be cut off due to time pressure"""
        time_left = self.white_time_left if side == "W" else self.black_time_left
        
        # Cut off search under high pressure
        if time_left < 20000:  # < 20s
            return current_depth > 1
        elif time_left < 30000:  # < 30s
            return current_depth > 2
        else:
            return False
    
    def boost_move_urgency(self, side: str, move_type: str) -> float:
        """Boost move urgency for checks/captures under time pressure"""
        time_left = self.white_time_left if side == "W" else self.black_time_left
        
        if time_left < 20000:  # < 20s
            if move_type in ['check', 'capture']:
                return 1.5  # 50% urgency boost
        elif time_left < 30000:  # < 30s
            if move_type in ['check', 'capture']:
                return 1.2  # 20% urgency boost
        
        return 1.0
    
    def is_blunder(self, eval_drop: float, time_left_ms: int) -> bool:
        """Determine if move is a blunder based on eval drop and time pressure"""
        if time_left_ms < 20000:
            return eval_drop < self.blunder_thresholds['under_20s']
        elif time_left_ms < 30000:
            return eval_drop < self.blunder_thresholds['under_30s']
        elif time_left_ms < 60000:
            return eval_drop < self.blunder_thresholds['under_60s']
        else:
            return eval_drop < self.blunder_thresholds['overall']
    
    def get_time_advantage(self) -> float:
        """Get current time advantage (positive = white advantage)"""
        return self.white_time_left - self.black_time_left
    
    def reset_timer(self):
        """Reset timer for new game"""
        self.white_time_left = self.turn_time_limit
        self.black_time_left = self.turn_time_limit

class QECRockSolidSimulator:
    """Rock-solid QEC simulator with comprehensive time management"""
    
    def __init__(self, logs_dir: str = "rock_solid_timer_logs"):
        self.logs_dir = logs_dir
        self.timer = QECRockSolidTimer(logs_dir)
        self.game_count = 0
        
        # Create logs directory
        os.makedirs(logs_dir, exist_ok=True)
    
    def simulate_rock_solid_game(self, seed: int = 42) -> Dict[str, Any]:
        """Simulate game with rock-solid timer validation"""
        from main import Game
        
        random.seed(seed)
        game = Game(seed=seed)
        game.live = False
        
        # Reset timer
        self.timer.reset_timer()
        
        # Game tracking
        move_count = 0
        turn_logs = []
        start_time = time.time()
        
        # Metrics tracking
        pressure_events = defaultdict(int)
        blunder_counts = defaultdict(int)
        eval_drops = []
        time_advantages = []
        
        while move_count < 200:  # Max moves
            current_color = game.board.to_move
            
            # Get legal moves
            legal_moves = game.board.legal_moves()
            if not legal_moves:
                break
            
            # Start turn with timer
            decision_quality, pressure_level, time_left_ms = self.timer.start_turn(current_color)
            
            # Calculate position complexity
            position_complexity = self._calculate_position_complexity(game.board)
            move_complexity = len(legal_moves) / 50.0
            
            # Calculate expected thinking time
            expected_think_ms = self.timer.calculate_expected_think_time(
                current_color, position_complexity, move_complexity
            )
            
            # Simulate thinking time (scaled for testing)
            actual_think_ms = int(expected_think_ms * random.uniform(0.8, 1.2))
            actual_think_ms = min(actual_think_ms, time_left_ms)
            
            # Get evaluation before move
            eval_before = self._simple_evaluate(game.board, current_color)
            
            # Choose move with time pressure effects
            chosen_move = self._choose_move_with_time_pressure(
                game, legal_moves, decision_quality, pressure_level, time_left_ms
            )
            
            if chosen_move is None:
                break
            
            piece, to, spec = chosen_move
            frm = piece.pos
            
            # Apply move
            meta = game.board._apply_move_internal(frm, to, spec)
            move_count += 1
            
            # Get evaluation after move
            eval_after = self._simple_evaluate(game.board, current_color)
            eval_drop = eval_before - eval_after
            
            # Track pressure events
            if time_left_ms < 20000:
                pressure_events['under_20s'] += 1
            if time_left_ms < 30000:
                pressure_events['under_30s'] += 1
            if time_left_ms < 60000:
                pressure_events['under_60s'] += 1
            
            # Check for blunders
            blunder = self.timer.is_blunder(eval_drop, time_left_ms)
            if blunder:
                if time_left_ms < 20000:
                    blunder_counts['under_20s'] += 1
                elif time_left_ms < 30000:
                    blunder_counts['under_30s'] += 1
                elif time_left_ms < 60000:
                    blunder_counts['under_60s'] += 1
                else:
                    blunder_counts['overall'] += 1
            
            # End turn
            self.timer.end_turn(current_color, actual_think_ms, eval_before, eval_after)
            
            # Track time advantage
            time_advantage = self.timer.get_time_advantage()
            time_advantages.append(time_advantage)
            
            # Create turn log
            turn_log = TurnLog(
                turn_id=move_count,
                side=current_color,
                think_ms=actual_think_ms,
                time_left_ms=time_left_ms,
                decision_quality=decision_quality,
                primary=f"{self._square_to_str(frm)}{self._square_to_str(to)}",
                forced="",  # Will be filled if forced move occurs
                react="",    # Will be filled if reactive move occurs
                eval_before=eval_before,
                eval_after=eval_after,
                eval_drop=eval_drop,
                pressure_level=pressure_level,
                blunder=blunder,
                expected_think_ms=expected_think_ms,
                actual_vs_expected=actual_think_ms / max(1, expected_think_ms)
            )
            
            # Handle entanglement side effects
            if meta.get("capture_id"):
                game.ent.break_link_if_member(meta["capture_id"])
            if spec.get("promotion"):
                game.ent.break_link_if_member(piece.id)
            
            # Forced counterpart move
            forced_happened = False
            if meta.get("castle_rook_to") is not None:
                rook_sq = meta["castle_rook_to"]
                rook = game.board.piece_at(rook_sq)
                if rook is not None:
                    forced_happened = game._maybe_force_counterpart(rook.id, record=False)
            else:
                moved_id = meta.get("moved_id", "")
                if moved_id:
                    forced_happened = game._maybe_force_counterpart(moved_id, record=False)
            
            if forced_happened:
                turn_log.forced = "forced_move"
            
            # Reactive king escape
            defender = game.board.to_move
            if game.board.in_check(defender):
                reactive_happened = game._do_reactive_king_escape(defender, record=False)
                if reactive_happened:
                    turn_log.react = "reactive_move"
            
            turn_logs.append(turn_log)
            eval_drops.append(eval_drop)
        
        # Determine result
        if game.board.in_check(game.board.to_move):
            result = "B wins" if game.board.to_move == "W" else "W wins"
        else:
            result = "Draw"
        
        # Calculate comprehensive metrics
        metrics = self._calculate_comprehensive_metrics(
            turn_logs, pressure_events, blunder_counts, time_advantages, eval_drops
        )
        
        # Create game result
        game_result = {
            "game_id": f"rock_solid_game_{seed:04d}",
            "result": result,
            "total_plies": move_count,
            "duration": time.time() - start_time,
            "seed": seed,
            "turn_logs": [asdict(log) for log in turn_logs],
            "metrics": asdict(metrics),
            "final_white_time": self.timer.white_time_left,
            "final_black_time": self.timer.black_time_left
        }
        
        return game_result
    
    def _calculate_position_complexity(self, board) -> float:
        """Calculate position complexity"""
        piece_count = len([p for p in board.pieces if p.alive])
        legal_moves = len(board.legal_moves())
        
        # Simple complexity metric
        complexity = (piece_count / 32.0) + (legal_moves / 50.0)
        return min(1.0, complexity)
    
    def _simple_evaluate(self, board, color: str) -> float:
        """Simple position evaluation"""
        material = 0
        piece_values = {'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0}
        
        for piece in board.pieces:
            if not piece.alive:
                continue
            
            value = piece_values.get(piece.kind, 0)
            if piece.color == color:
                material += value
            else:
                material -= value
        
        return material
    
    def _choose_move_with_time_pressure(self, game, legal_moves, decision_quality, 
                                      pressure_level, time_left_ms):
        """Choose move considering time pressure"""
        # Time pressure affects move selection quality
        if decision_quality < 0.8:  # High time pressure
            # Choose from top moves only
            top_moves = legal_moves[:max(1, len(legal_moves) // 3)]
            return random.choice(top_moves)
        else:
            # Normal move selection
            return random.choice(legal_moves)
    
    def _square_to_str(self, square) -> str:
        """Convert square to string notation"""
        f, r = square
        return f"{'abcdefgh'[f]}{r+1}"
    
    def _calculate_comprehensive_metrics(self, turn_logs, pressure_events, 
                                        blunder_counts, time_advantages, eval_drops):
        """Calculate comprehensive time-based metrics"""
        # Opening tempo swings
        delta_time_after_move_1 = 0.0
        delta_time_after_move_2 = 0.0
        delta_time_after_move_3 = 0.0
        
        if len(turn_logs) >= 1:
            delta_time_after_move_1 = turn_logs[0].time_left_ms
        if len(turn_logs) >= 2:
            delta_time_after_move_2 = turn_logs[1].time_left_ms
        if len(turn_logs) >= 3:
            delta_time_after_move_3 = turn_logs[2].time_left_ms
        
        # Blunder rates
        total_moves = len(turn_logs)
        blunder_rate_overall = blunder_counts['overall'] / max(1, total_moves)
        blunder_rate_under_20s = blunder_counts['under_20s'] / max(1, pressure_events['under_20s'])
        blunder_rate_under_30s = blunder_counts['under_30s'] / max(1, pressure_events['under_30s'])
        blunder_rate_under_60s = blunder_counts['under_60s'] / max(1, pressure_events['under_60s'])
        
        # Speed/accuracy curve
        speed_accuracy_curve = self._calculate_speed_accuracy_curve(turn_logs)
        
        # Color-time advantage at specific moves
        color_time_advantage_move_5 = 0.0
        color_time_advantage_move_10 = 0.0
        color_time_advantage_move_20 = 0.0
        
        if len(time_advantages) >= 5:
            color_time_advantage_move_5 = time_advantages[4]
        if len(time_advantages) >= 10:
            color_time_advantage_move_10 = time_advantages[9]
        if len(time_advantages) >= 20:
            color_time_advantage_move_20 = time_advantages[19]
        
        # Archetype pacing (simplified for now)
        archetype_pacing = {
            "white": {"opening": 30000, "middlegame": 25000, "endgame": 20000},
            "black": {"opening": 30000, "middlegame": 25000, "endgame": 20000}
        }
        
        return TimeMetrics(
            delta_time_after_move_1=delta_time_after_move_1,
            delta_time_after_move_2=delta_time_after_move_2,
            delta_time_after_move_3=delta_time_after_move_3,
            pressure_events_under_20s=pressure_events['under_20s'],
            pressure_events_under_30s=pressure_events['under_30s'],
            pressure_events_under_60s=pressure_events['under_60s'],
            blunder_rate_overall=blunder_rate_overall,
            blunder_rate_under_20s=blunder_rate_under_20s,
            blunder_rate_under_30s=blunder_rate_under_30s,
            blunder_rate_under_60s=blunder_rate_under_60s,
            speed_accuracy_curve=speed_accuracy_curve,
            color_time_advantage_move_5=color_time_advantage_move_5,
            color_time_advantage_move_10=color_time_advantage_move_10,
            color_time_advantage_move_20=color_time_advantage_move_20,
            archetype_pacing=archetype_pacing
        )
    
    def _calculate_speed_accuracy_curve(self, turn_logs):
        """Calculate speed/accuracy curve"""
        # Bucket think times
        buckets = {
            "≤5s": [],
            "5-30s": [],
            "30-90s": [],
            ">90s": []
        }
        
        for log in turn_logs:
            think_s = log.think_ms / 1000.0
            if think_s <= 5:
                buckets["≤5s"].append(log.eval_drop)
            elif think_s <= 30:
                buckets["5-30s"].append(log.eval_drop)
            elif think_s <= 90:
                buckets["30-90s"].append(log.eval_drop)
            else:
                buckets[">90s"].append(log.eval_drop)
        
        # Calculate average eval gain for each bucket
        curve = {}
        for bucket, eval_drops in buckets.items():
            if eval_drops:
                curve[bucket] = {
                    "avg_eval_drop": sum(eval_drops) / len(eval_drops),
                    "count": len(eval_drops)
                }
            else:
                curve[bucket] = {"avg_eval_drop": 0.0, "count": 0}
        
        return curve
    
    def run_rock_solid_experiment(self, num_games: int = 100):
        """Run rock-solid timer experiment"""
        print(f"=== QEC Rock-Solid Timer Experiment ===")
        print(f"Games: {num_games}")
        print(f"Logs directory: {self.logs_dir}")
        print()
        
        results = []
        
        for game_num in range(num_games):
            seed = 42 + game_num
            result = self.simulate_rock_solid_game(seed)
            results.append(result)
            
            if game_num % 20 == 0:
                print(f"Completed {game_num} games...")
        
        # Save results
        self._save_rock_solid_results(results)
        
        # Analyze results
        self._analyze_rock_solid_results(results)
        
        return results
    
    def _save_rock_solid_results(self, results):
        """Save rock-solid timer results"""
        # Save detailed results
        results_file = os.path.join(self.logs_dir, "rock_solid_results.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Save CSV for analysis
        csv_file = os.path.join(self.logs_dir, "rock_solid_summary.csv")
        with open(csv_file, 'w') as f:
            f.write("game_id,result,total_plies,duration,seed,final_white_time,final_black_time,pressure_events_under_20s,pressure_events_under_30s,pressure_events_under_60s,blunder_rate_overall,blunder_rate_under_20s,blunder_rate_under_30s,blunder_rate_under_60s,color_time_advantage_move_5,color_time_advantage_move_10,color_time_advantage_move_20\\n")
            
            for result in results:
                metrics = result['metrics']
                f.write(f"{result['game_id']},{result['result']},{result['total_plies']},{result['duration']:.2f},{result['seed']},{result['final_white_time']},{result['final_black_time']},{metrics['pressure_events_under_20s']},{metrics['pressure_events_under_30s']},{metrics['pressure_events_under_60s']},{metrics['blunder_rate_overall']:.3f},{metrics['blunder_rate_under_20s']:.3f},{metrics['blunder_rate_under_30s']:.3f},{metrics['blunder_rate_under_60s']:.3f},{metrics['color_time_advantage_move_5']:.1f},{metrics['color_time_advantage_move_10']:.1f},{metrics['color_time_advantage_move_20']:.1f}\\n")
        
        print(f"Results saved to {self.logs_dir}")
    
    def _analyze_rock_solid_results(self, results):
        """Analyze rock-solid timer results"""
        print(f"\\n=== Rock-Solid Timer Analysis ===")
        print(f"Total games: {len(results)}")
        
        # Result distribution
        result_counts = defaultdict(int)
        for result in results:
            result_counts[result['result']] += 1
        
        print(f"Results: {dict(result_counts)}")
        
        # Time pressure analysis
        total_pressure_20s = sum(r['metrics']['pressure_events_under_20s'] for r in results)
        total_pressure_30s = sum(r['metrics']['pressure_events_under_30s'] for r in results)
        total_pressure_60s = sum(r['metrics']['pressure_events_under_60s'] for r in results)
        
        print(f"\\nTime Pressure Events:")
        print(f"  Under 20s: {total_pressure_20s}")
        print(f"  Under 30s: {total_pressure_30s}")
        print(f"  Under 60s: {total_pressure_60s}")
        
        # Blunder analysis
        avg_blunder_overall = sum(r['metrics']['blunder_rate_overall'] for r in results) / len(results)
        avg_blunder_20s = sum(r['metrics']['blunder_rate_under_20s'] for r in results) / len(results)
        avg_blunder_30s = sum(r['metrics']['blunder_rate_under_30s'] for r in results) / len(results)
        avg_blunder_60s = sum(r['metrics']['blunder_rate_under_60s'] for r in results) / len(results)
        
        print(f"\\nBlunder Rates:")
        print(f"  Overall: {avg_blunder_overall:.3f}")
        print(f"  Under 20s: {avg_blunder_20s:.3f}")
        print(f"  Under 30s: {avg_blunder_30s:.3f}")
        print(f"  Under 60s: {avg_blunder_60s:.3f}")
        
        # Time advantage analysis
        avg_advantage_5 = sum(r['metrics']['color_time_advantage_move_5'] for r in results) / len(results)
        avg_advantage_10 = sum(r['metrics']['color_time_advantage_move_10'] for r in results) / len(results)
        avg_advantage_20 = sum(r['metrics']['color_time_advantage_move_20'] for r in results) / len(results)
        
        print(f"\\nColor Time Advantage:")
        print(f"  Move 5: {avg_advantage_5:.1f}ms")
        print(f"  Move 10: {avg_advantage_10:.1f}ms")
        print(f"  Move 20: {avg_advantage_20:.1f}ms")
        
        # Speed/accuracy curve
        print(f"\\nSpeed/Accuracy Curve:")
        for result in results[:5]:  # Show first 5 games
            curve = result['metrics']['speed_accuracy_curve']
            print(f"  Game {result['game_id']}:")
            for bucket, data in curve.items():
                if data['count'] > 0:
                    print(f"    {bucket}: {data['avg_eval_drop']:.1f} avg drop ({data['count']} moves)")

if __name__ == "__main__":
    # Run rock-solid timer experiment
    simulator = QECRockSolidSimulator()
    results = simulator.run_rock_solid_experiment(num_games=100)
