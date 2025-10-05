"""
QEC Time Management System
Implements 3-minute turn timer with strategic time pressure effects
"""

import time
import random
import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

class TimePressure(Enum):
    LOW = "low"      # > 2 minutes remaining
    MEDIUM = "medium" # 1-2 minutes remaining  
    HIGH = "high"     # 30 seconds - 1 minute
    CRITICAL = "critical" # < 30 seconds

@dataclass
class TimeState:
    """Time state for a player"""
    time_remaining: float  # seconds
    time_used: float       # seconds used this turn
    total_time_used: float # total time used in game
    time_pressure: TimePressure
    thinking_time_given: float  # time opponent spent thinking (advantage)
    time_advantage: float  # net time advantage

class QECTimeManager:
    """Manages 3-minute turn timer with strategic implications"""
    
    def __init__(self):
        self.turn_time_limit = 180.0  # 3 minutes in seconds
        self.white_time = TimeState(
            time_remaining=180.0,
            time_used=0.0,
            total_time_used=0.0,
            time_pressure=TimePressure.LOW,
            thinking_time_given=0.0,
            time_advantage=0.0
        )
        self.black_time = TimeState(
            time_remaining=180.0,
            time_used=0.0,
            total_time_used=0.0,
            time_pressure=TimePressure.LOW,
            thinking_time_given=0.0,
            time_advantage=0.0
        )
        
        # Time pressure effects on decision quality
        self.time_pressure_effects = {
            TimePressure.LOW: 1.0,      # No penalty
            TimePressure.MEDIUM: 0.95,   # 5% decision quality reduction
            TimePressure.HIGH: 0.85,     # 15% decision quality reduction
            TimePressure.CRITICAL: 0.70  # 30% decision quality reduction
        }
    
    def start_turn(self, color: str) -> float:
        """Start a new turn and return time pressure factor"""
        current_time = self.white_time if color == "W" else self.black_time
        opponent_time = self.black_time if color == "W" else self.white_time
        
        # Calculate time advantage from opponent's thinking time
        current_time.thinking_time_given = opponent_time.time_used
        current_time.time_advantage = current_time.time_remaining - opponent_time.time_remaining
        
        # Update time pressure
        self._update_time_pressure(current_time)
        
        # Return decision quality factor
        return self.time_pressure_effects[current_time.time_pressure]
    
    def end_turn(self, color: str, time_used: float):
        """End turn and update time state"""
        current_time = self.white_time if color == "W" else self.black_time
        
        # Update time tracking
        current_time.time_used = time_used
        current_time.total_time_used += time_used
        current_time.time_remaining = max(0.0, current_time.time_remaining - time_used)
        
        # Check for time forfeit
        if current_time.time_remaining <= 0:
            current_time.time_remaining = 0.0
            current_time.time_pressure = TimePressure.CRITICAL
    
    def _update_time_pressure(self, time_state: TimeState):
        """Update time pressure based on remaining time"""
        if time_state.time_remaining > 120.0:
            time_state.time_pressure = TimePressure.LOW
        elif time_state.time_remaining > 60.0:
            time_state.time_pressure = TimePressure.MEDIUM
        elif time_state.time_remaining > 30.0:
            time_state.time_pressure = TimePressure.HIGH
        else:
            time_state.time_pressure = TimePressure.CRITICAL
    
    def get_time_pressure_factor(self, color: str) -> float:
        """Get decision quality factor based on time pressure"""
        current_time = self.white_time if color == "W" else self.black_time
        return self.time_pressure_effects[current_time.time_pressure]
    
    def get_time_advantage(self, color: str) -> float:
        """Get time advantage (positive = more time than opponent)"""
        current_time = self.white_time if color == "W" else self.black_time
        return current_time.time_advantage
    
    def get_thinking_time_given(self, color: str) -> float:
        """Get how much thinking time was given to opponent"""
        current_time = self.white_time if color == "W" else self.black_time
        return current_time.thinking_time_given
    
    def should_rush_move(self, color: str, move_complexity: float) -> bool:
        """Determine if player should rush move based on time pressure and complexity"""
        current_time = self.white_time if color == "W" else self.black_time
        
        # Rush if time is critical
        if current_time.time_pressure == TimePressure.CRITICAL:
            return True
        
        # Rush if high pressure and complex move
        if current_time.time_pressure == TimePressure.HIGH and move_complexity > 0.7:
            return True
        
        # Rush if giving opponent too much thinking time
        if current_time.thinking_time_given > 60.0:  # More than 1 minute
            return True
        
        return False
    
    def get_optimal_thinking_time(self, color: str, move_complexity: float, 
                                position_complexity: float) -> float:
        """Calculate optimal thinking time based on position and time state"""
        current_time = self.white_time if color == "W" else self.black_time
        
        # Base thinking time based on complexity
        base_time = 10.0 + (move_complexity * 30.0) + (position_complexity * 20.0)
        
        # Adjust for time pressure
        if current_time.time_pressure == TimePressure.LOW:
            # Can think longer, but don't give opponent too much time
            max_time = min(60.0, current_time.time_remaining * 0.3)
            return min(base_time, max_time)
        
        elif current_time.time_pressure == TimePressure.MEDIUM:
            # Moderate thinking time
            max_time = min(45.0, current_time.time_remaining * 0.4)
            return min(base_time * 0.8, max_time)
        
        elif current_time.time_pressure == TimePressure.HIGH:
            # Quick thinking
            max_time = min(30.0, current_time.time_remaining * 0.5)
            return min(base_time * 0.6, max_time)
        
        else:  # CRITICAL
            # Very quick thinking
            max_time = min(15.0, current_time.time_remaining * 0.8)
            return min(base_time * 0.4, max_time)
    
    def get_time_status(self, color: str) -> Dict[str, Any]:
        """Get comprehensive time status for a player"""
        current_time = self.white_time if color == "W" else self.black_time
        
        return {
            "time_remaining": current_time.time_remaining,
            "time_used_this_turn": current_time.time_used,
            "total_time_used": current_time.total_time_used,
            "time_pressure": current_time.time_pressure.value,
            "thinking_time_given": current_time.thinking_time_given,
            "time_advantage": current_time.time_advantage,
            "decision_quality_factor": self.time_pressure_effects[current_time.time_pressure]
        }
    
    def get_game_time_summary(self) -> Dict[str, Any]:
        """Get overall game time summary"""
        return {
            "white_time_remaining": self.white_time.time_remaining,
            "black_time_remaining": self.black_time.time_remaining,
            "white_total_time_used": self.white_time.total_time_used,
            "black_total_time_used": self.black_time.total_time_used,
            "white_time_pressure": self.white_time.time_pressure.value,
            "black_time_pressure": self.black_time.time_pressure.value,
            "time_advantage": self.white_time.time_remaining - self.black_time.time_remaining
        }

class QECTimeAwareSimulator:
    """QEC simulator with time management integration"""
    
    def __init__(self, logs_dir: str = "time_aware_logs"):
        self.logs_dir = logs_dir
        self.time_manager = QECTimeManager()
        self.game_count = 0
        
        # Create logs directory
        import os
        os.makedirs(logs_dir, exist_ok=True)
    
    def simulate_time_aware_game(self, white_arch, black_arch, seed: int = 42):
        """Simulate game with time management"""
        import random
        from main import Game
        
        random.seed(seed)
        game = Game(seed=seed)
        game.live = False
        
        # Game tracking
        move_count = 0
        time_pressure_events = []
        time_advantage_changes = []
        
        while move_count < 200:  # Max moves
            current_color = game.board.to_move
            current_arch = white_arch if current_color == "W" else black_arch
            
            # Get legal moves
            legal_moves = game.board.legal_moves()
            if not legal_moves:
                break
            
            # Start turn with time management
            decision_quality = self.time_manager.start_turn(current_color)
            
            # Calculate move complexity (simplified)
            move_complexity = len(legal_moves) / 50.0  # Normalize to 0-1
            position_complexity = self._calculate_position_complexity(game.board)
            
            # Get optimal thinking time
            thinking_time = self.time_manager.get_optimal_thinking_time(
                current_color, move_complexity, position_complexity
            )
            
            # Simulate thinking time
            time.sleep(thinking_time / 100.0)  # Scale down for simulation
            
            # Choose move with time pressure effects
            chosen_move = self._choose_move_with_time_pressure(
                game, legal_moves, decision_quality, move_complexity
            )
            
            if chosen_move is None:
                break
            
            piece, to, spec = chosen_move
            frm = piece.pos
            
            # Apply move
            meta = game.board._apply_move_internal(frm, to, spec)
            move_count += 1
            
            # End turn
            self.time_manager.end_turn(current_color, thinking_time)
            
            # Track time events
            time_status = self.time_manager.get_time_status(current_color)
            time_pressure_events.append({
                "move": move_count,
                "color": current_color,
                "time_pressure": time_status["time_pressure"],
                "decision_quality": time_status["decision_quality_factor"],
                "thinking_time": thinking_time,
                "time_advantage": time_status["time_advantage"]
            })
            
            # Handle entanglement side effects
            if meta.get("capture_id"):
                game.ent.break_link_if_member(meta["capture_id"])
            if spec.get("promotion"):
                game.ent.break_link_if_member(piece.id)
            
            # Forced counterpart move
            if meta.get("castle_rook_to") is not None:
                rook_sq = meta["castle_rook_to"]
                rook = game.board.piece_at(rook_sq)
                if rook is not None:
                    game._maybe_force_counterpart(rook.id, record=False)
            else:
                moved_id = meta.get("moved_id", "")
                if moved_id:
                    game._maybe_force_counterpart(moved_id, record=False)
            
            # Reactive king escape
            defender = game.board.to_move
            if game.board.in_check(defender):
                game._do_reactive_king_escape(defender, record=False)
        
        # Save time analysis
        self._save_time_analysis(time_pressure_events, seed)
        
        return {
            "moves": move_count,
            "time_summary": self.time_manager.get_game_time_summary(),
            "time_pressure_events": time_pressure_events
        }
    
    def _calculate_position_complexity(self, board) -> float:
        """Calculate position complexity (simplified)"""
        # Count pieces, legal moves, and tactical elements
        piece_count = len([p for p in board.pieces if p.alive])
        legal_moves = len(board.legal_moves())
        
        # Simple complexity metric
        complexity = (piece_count / 32.0) + (legal_moves / 50.0)
        return min(1.0, complexity)
    
    def _choose_move_with_time_pressure(self, game, legal_moves, decision_quality, 
                                      move_complexity):
        """Choose move considering time pressure"""
        # Time pressure affects move selection quality
        if decision_quality < 0.8:  # High time pressure
            # Choose from top moves only
            top_moves = legal_moves[:max(1, len(legal_moves) // 3)]
            return random.choice(top_moves)
        else:
            # Normal move selection
            return random.choice(legal_moves)
    
    def _save_time_analysis(self, time_pressure_events, seed):
        """Save time analysis to file"""
        import json
        import os
        
        analysis = {
            "seed": seed,
            "total_events": len(time_pressure_events),
            "time_pressure_events": time_pressure_events,
            "final_time_summary": self.time_manager.get_game_time_summary()
        }
        
        filename = os.path.join(self.logs_dir, f"time_analysis_{seed}.json")
        with open(filename, 'w') as f:
            json.dump(analysis, f, indent=2)

if __name__ == "__main__":
    # Test time management system
    simulator = QECTimeAwareSimulator()
    
    # Simulate a game with time management
    result = simulator.simulate_time_aware_game(
        white_arch="Carlsen-like",
        black_arch="Tal-like", 
        seed=42
    )
    
    print("Time-aware simulation complete!")
    print(f"Moves: {result['moves']}")
    print(f"Time summary: {result['time_summary']}")
