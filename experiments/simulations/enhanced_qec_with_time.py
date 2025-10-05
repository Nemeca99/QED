"""
Enhanced QEC with Time Management
Integrates 3-minute turn timer with strategic implications
"""

import os
import json
import time
import random
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from collections import defaultdict

from main import Game, Board, Piece, Square, Color
from qec_time_manager import QECTimeManager, TimePressure

@dataclass
class TimeAwareGameResult:
    """Game result with time management data"""
    # Basic game info
    game_id: str
    result: str
    total_plies: int
    duration: float
    seed: int
    
    # Time management data
    white_time_remaining: float
    black_time_remaining: float
    white_time_pressure_events: int
    black_time_pressure_events: int
    time_advantage_swings: int
    
    # Strategic time effects
    first_move_time: float
    time_given_to_opponent: float
    critical_time_decisions: int
    
    # Entanglement + time
    forced_moves_under_pressure: int
    reactive_moves_under_pressure: int
    time_pressure_mistakes: int

class EnhancedQECWithTime:
    """Enhanced QEC simulator with comprehensive time management"""
    
    def __init__(self, logs_dir: str = "enhanced_qec_time_logs"):
        self.logs_dir = logs_dir
        self.game_count = 0
        
        # Create logs directory
        os.makedirs(logs_dir, exist_ok=True)
    
    def simulate_time_aware_game(self, seed: int = 42) -> TimeAwareGameResult:
        """Simulate game with full time management"""
        random.seed(seed)
        game = Game(seed=seed)
        game.live = False
        
        # Initialize time manager
        time_manager = QECTimeManager()
        
        # Game tracking
        move_count = 0
        start_time = time.time()
        
        # Time tracking
        white_time_events = 0
        black_time_events = 0
        time_advantage_swings = 0
        first_move_time = 0.0
        time_given_to_opponent = 0.0
        critical_decisions = 0
        forced_under_pressure = 0
        reactive_under_pressure = 0
        time_pressure_mistakes = 0
        
        # Track time advantage changes
        last_white_advantage = 0.0
        last_black_advantage = 0.0
        
        while move_count < 200:  # Max moves
            current_color = game.board.to_move
            
            # Get legal moves
            legal_moves = game.board.legal_moves()
            if not legal_moves:
                break
            
            # Start turn with time management
            decision_quality = time_manager.start_turn(current_color)
            time_status = time_manager.get_time_status(current_color)
            
            # Track first move time
            if move_count == 0:
                first_move_time = time_status['time_remaining']
            
            # Calculate move complexity
            move_complexity = len(legal_moves) / 50.0
            position_complexity = self._calculate_position_complexity(game.board)
            
            # Get optimal thinking time
            optimal_thinking = time_manager.get_optimal_thinking_time(
                current_color, move_complexity, position_complexity
            )
            
            # Simulate thinking time (scaled for testing)
            thinking_time = optimal_thinking * random.uniform(0.8, 1.2)  # Add some variance
            thinking_time = min(thinking_time, time_status['time_remaining'])
            
            # Track time given to opponent
            if current_color == "W":
                time_given_to_opponent += thinking_time
            else:
                time_given_to_opponent += thinking_time
            
            # Choose move with time pressure effects
            chosen_move = self._choose_move_with_time_pressure(
                game, legal_moves, decision_quality, move_complexity, time_status
            )
            
            if chosen_move is None:
                break
            
            piece, to, spec = chosen_move
            frm = piece.pos
            
            # Track time pressure events
            if time_status['time_pressure'] in ['high', 'critical']:
                if current_color == "W":
                    white_time_events += 1
                else:
                    black_time_events += 1
                
                if time_status['time_pressure'] == 'critical':
                    critical_decisions += 1
            
            # Track time advantage swings
            current_advantage = time_status['time_advantage']
            if current_color == "W":
                if abs(current_advantage - last_white_advantage) > 10.0:
                    time_advantage_swings += 1
                last_white_advantage = current_advantage
            else:
                if abs(current_advantage - last_black_advantage) > 10.0:
                    time_advantage_swings += 1
                last_black_advantage = current_advantage
            
            # Apply move
            meta = game.board._apply_move_internal(frm, to, spec)
            move_count += 1
            
            # End turn
            time_manager.end_turn(current_color, thinking_time)
            
            # Handle entanglement side effects
            if meta.get("capture_id"):
                game.ent.break_link_if_member(meta["capture_id"])
            if spec.get("promotion"):
                game.ent.break_link_if_member(piece.id)
            
            # Forced counterpart move (with time pressure)
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
            
            # Track forced moves under pressure
            if forced_happened and time_status['time_pressure'] in ['high', 'critical']:
                forced_under_pressure += 1
            
            # Reactive king escape (with time pressure)
            defender = game.board.to_move
            reactive_happened = False
            if game.board.in_check(defender):
                reactive_happened = game._do_reactive_king_escape(defender, record=False)
                
                # Track reactive moves under pressure
                if reactive_happened and time_status['time_pressure'] in ['high', 'critical']:
                    reactive_under_pressure += 1
            else:
                # No legal king escape = reactive mate
                if game.board.in_check(defender):
                    break
        
        # Determine result
        if game.board.in_check(game.board.to_move):
            result = "B wins" if game.board.to_move == "W" else "W wins"
        else:
            result = "Draw"
        
        # Create result
        game_result = TimeAwareGameResult(
            game_id=f"time_aware_game_{seed:04d}",
            result=result,
            total_plies=move_count,
            duration=time.time() - start_time,
            seed=seed,
            white_time_remaining=time_manager.white_time.time_remaining,
            black_time_remaining=time_manager.black_time.time_remaining,
            white_time_pressure_events=white_time_events,
            black_time_pressure_events=black_time_events,
            time_advantage_swings=time_advantage_swings,
            first_move_time=first_move_time,
            time_given_to_opponent=time_given_to_opponent,
            critical_time_decisions=critical_decisions,
            forced_moves_under_pressure=forced_under_pressure,
            reactive_moves_under_pressure=reactive_under_pressure,
            time_pressure_mistakes=time_pressure_mistakes
        )
        
        return game_result
    
    def _calculate_position_complexity(self, board) -> float:
        """Calculate position complexity"""
        piece_count = len([p for p in board.pieces if p.alive])
        legal_moves = len(board.legal_moves())
        
        # Simple complexity metric
        complexity = (piece_count / 32.0) + (legal_moves / 50.0)
        return min(1.0, complexity)
    
    def _choose_move_with_time_pressure(self, game, legal_moves, decision_quality, 
                                      move_complexity, time_status):
        """Choose move considering time pressure"""
        # Time pressure affects move selection quality
        if decision_quality < 0.8:  # High time pressure
            # Choose from top moves only
            top_moves = legal_moves[:max(1, len(legal_moves) // 3)]
            return random.choice(top_moves)
        else:
            # Normal move selection
            return random.choice(legal_moves)
    
    def run_time_aware_experiment(self, num_games: int = 100):
        """Run experiment with time management"""
        print(f"=== Enhanced QEC with Time Management ===")
        print(f"Games: {num_games}")
        print(f"Logs directory: {self.logs_dir}")
        print()
        
        results = []
        
        for game_num in range(num_games):
            seed = 42 + game_num
            result = self.simulate_time_aware_game(seed)
            results.append(result)
            
            if game_num % 20 == 0:
                print(f"Completed {game_num} games...")
        
        # Analyze results
        self._analyze_time_results(results)
        
        # Save results
        self._save_time_results(results)
        
        return results
    
    def _analyze_time_results(self, results: List[TimeAwareGameResult]):
        """Analyze time management results"""
        print(f"\\n=== Time Management Analysis ===")
        print(f"Total games: {len(results)}")
        
        # Result distribution
        result_counts = defaultdict(int)
        for result in results:
            result_counts[result.result] += 1
        
        print(f"Results: {dict(result_counts)}")
        
        # Time pressure analysis
        total_white_pressure = sum(r.white_time_pressure_events for r in results)
        total_black_pressure = sum(r.black_time_pressure_events for r in results)
        total_critical = sum(r.critical_time_decisions for r in results)
        
        print(f"\\nTime Pressure Statistics:")
        print(f"  White time pressure events: {total_white_pressure}")
        print(f"  Black time pressure events: {total_black_pressure}")
        print(f"  Critical time decisions: {total_critical}")
        print(f"  Avg pressure events per game: {(total_white_pressure + total_black_pressure) / len(results):.1f}")
        
        # Strategic time effects
        avg_first_move_time = sum(r.first_move_time for r in results) / len(results)
        avg_time_given = sum(r.time_given_to_opponent for r in results) / len(results)
        avg_advantage_swings = sum(r.time_advantage_swings for r in results) / len(results)
        
        print(f"\\nStrategic Time Effects:")
        print(f"  Average first move time: {avg_first_move_time:.1f}s")
        print(f"  Average time given to opponent: {avg_time_given:.1f}s")
        print(f"  Average time advantage swings: {avg_advantage_swings:.1f}")
        
        # Entanglement + time pressure
        total_forced_pressure = sum(r.forced_moves_under_pressure for r in results)
        total_reactive_pressure = sum(r.reactive_moves_under_pressure for r in results)
        total_pressure_mistakes = sum(r.time_pressure_mistakes for r in results)
        
        print(f"\\nEntanglement + Time Pressure:")
        print(f"  Forced moves under pressure: {total_forced_pressure}")
        print(f"  Reactive moves under pressure: {total_reactive_pressure}")
        print(f"  Time pressure mistakes: {total_pressure_mistakes}")
        
        # Time advantage analysis
        white_advantages = [r.white_time_remaining - r.black_time_remaining for r in results]
        if white_advantages:
            print(f"\\nTime Advantage Analysis:")
            print(f"  White advantage range: {min(white_advantages):.1f}s to {max(white_advantages):.1f}s")
            print(f"  Average white advantage: {sum(white_advantages) / len(white_advantages):.1f}s")
    
    def _save_time_results(self, results: List[TimeAwareGameResult]):
        """Save time management results"""
        # Save detailed results
        results_file = os.path.join(self.logs_dir, "time_aware_results.json")
        with open(results_file, 'w') as f:
            json.dump([{
                "game_id": r.game_id,
                "result": r.result,
                "total_plies": r.total_plies,
                "duration": r.duration,
                "seed": r.seed,
                "white_time_remaining": r.white_time_remaining,
                "black_time_remaining": r.black_time_remaining,
                "white_time_pressure_events": r.white_time_pressure_events,
                "black_time_pressure_events": r.black_time_pressure_events,
                "time_advantage_swings": r.time_advantage_swings,
                "first_move_time": r.first_move_time,
                "time_given_to_opponent": r.time_given_to_opponent,
                "critical_time_decisions": r.critical_time_decisions,
                "forced_moves_under_pressure": r.forced_moves_under_pressure,
                "reactive_moves_under_pressure": r.reactive_moves_under_pressure,
                "time_pressure_mistakes": r.time_pressure_mistakes
            } for r in results], f, indent=2)
        
        # Save summary CSV
        summary_file = os.path.join(self.logs_dir, "time_aware_summary.csv")
        with open(summary_file, 'w') as f:
            f.write("game_id,result,total_plies,duration,white_time_remaining,black_time_remaining,white_time_pressure_events,black_time_pressure_events,time_advantage_swings,first_move_time,time_given_to_opponent,critical_time_decisions,forced_moves_under_pressure,reactive_moves_under_pressure,time_pressure_mistakes\\n")
            
            for result in results:
                f.write(f"{result.game_id},{result.result},{result.total_plies},{result.duration:.2f},{result.white_time_remaining:.1f},{result.black_time_remaining:.1f},{result.white_time_pressure_events},{result.black_time_pressure_events},{result.time_advantage_swings},{result.first_move_time:.1f},{result.time_given_to_opponent:.1f},{result.critical_time_decisions},{result.forced_moves_under_pressure},{result.reactive_moves_under_pressure},{result.time_pressure_mistakes}\\n")
        
        print(f"Results saved to {self.logs_dir}")

if __name__ == "__main__":
    # Run enhanced QEC with time management
    simulator = EnhancedQECWithTime()
    results = simulator.run_time_aware_experiment(num_games=50)
