"""
QEC Hypothesis Tester
Enhanced data collection and analysis system designed to test specific QEC hypotheses
"""

import os
import json
import time
import random
import hashlib
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict

from main import Game, Board, Piece, Square, Color
from qec_archetypes import QECArchetype, get_archetype_by_name
from qec_hypotheses import QEC_HYPOTHESES, get_required_data_fields, get_required_metrics

@dataclass
class QECHypothesisData:
    """Enhanced game data specifically for hypothesis testing"""
    # Basic game info
    game_id: str
    white_archetype: str
    black_archetype: str
    result: str
    total_plies: int
    seed: int
    duration: float
    
    # H1: Opening Determinism
    first_move_notation: str
    first_move_eval_delta: float
    move_1_win_rate_variance: float
    move_2_win_rate_variance: float
    move_3_win_rate_variance: float
    
    # H2: Free-Pawn Centrality
    white_free_pawn_file: str
    black_free_pawn_file: str
    free_pawn_centrality_score: float
    mobility_metrics: Dict[str, float]
    tempo_metrics: Dict[str, float]
    
    # H3: Information-Asymmetry Effect
    free_pawn_discovery_ply: int
    discovery_side: str
    eval_after_discovery: float
    information_advantage_metrics: Dict[str, float]
    
    # H4: Second-Player Advantage
    opening_phase_evals: List[float]
    first_player_entanglement_activation: int
    second_player_reaction_time: int
    eval_after_opening: float
    color_advantage_metrics: Dict[str, float]
    
    # H5: Entanglement Stability vs. Breakage
    entanglement_break_count: int
    entanglement_persistence_ratio: float
    game_length: int
    tactical_vs_positional_score: float
    entanglement_stability_metrics: Dict[str, float]
    
    # H6: Reactive-Check Survival Bias
    reactive_check_count: int
    reactive_check_sequence: List[int]
    reactive_check_survival_rate: float
    collapse_prediction_metrics: Dict[str, float]
    
    # H7: Archetype-Entanglement Interaction
    archetype_style: str
    entanglement_interaction_patterns: Dict[str, Any]
    archetype_win_rate_by_entanglement_type: float
    style_entanglement_correlation: float
    
    # H8: Forced-Move Cascade Effect
    forced_move_count: int
    forced_move_cascade_length: int
    evaluation_volatility: float
    tactical_complexity_score: float
    game_predictability_metrics: Dict[str, float]
    
    # Per-ply detailed data
    per_ply_data: List[Dict[str, Any]]

class QECHypothesisTester:
    """Enhanced simulator designed to test specific QEC hypotheses"""
    
    def __init__(self, logs_dir: str = "hypothesis_test_logs"):
        self.logs_dir = logs_dir
        self.results = []
        self.hypothesis_metrics = {}
        
        # Create logs directory
        os.makedirs(logs_dir, exist_ok=True)
        
        # Initialize hypothesis tracking
        for hyp in QEC_HYPOTHESES:
            self.hypothesis_metrics[hyp.id] = {
                "status": "untested",
                "data_collected": 0,
                "metrics_calculated": 0,
                "last_updated": None
            }
    
    def run_hypothesis_experiment(self, archetypes: List[str], num_games: int = 1000) -> List[QECHypothesisData]:
        """Run comprehensive experiment to test all hypotheses"""
        print("=== QEC Hypothesis Testing Experiment ===")
        print(f"Testing {len(QEC_HYPOTHESES)} hypotheses")
        print(f"Archetypes: {archetypes}")
        print(f"Games: {num_games}")
        print()
        
        results = []
        
        for game_num in range(num_games):
            # Randomly select archetypes
            white_arch_name = random.choice(archetypes)
            black_arch_name = random.choice(archetypes)
            
            white_arch = get_archetype_by_name(white_arch_name)
            black_arch = get_archetype_by_name(black_arch_name)
            
            if not white_arch or not black_arch:
                continue
            
            # Run game with enhanced data collection
            game_data = self._simulate_game_with_hypothesis_data(
                white_arch, black_arch, game_num
            )
            
            results.append(game_data)
            
            # Update hypothesis tracking
            self._update_hypothesis_tracking(game_data)
            
            if game_num % 100 == 0:
                print(f"Completed {game_num} games...")
        
        self.results.extend(results)
        return results
    
    def _simulate_game_with_hypothesis_data(self, white_arch: QECArchetype, 
                                          black_arch: QECArchetype, 
                                          game_num: int) -> QECHypothesisData:
        """Simulate game with comprehensive hypothesis data collection"""
        seed = 42 + game_num
        random.seed(seed)
        
        # Create game
        game = Game(seed=seed)
        game.live = False
        
        # Enhanced data collection
        hypothesis_data = QECHypothesisData(
            # Basic info
            game_id=f"hyp_game_{game_num:04d}",
            white_archetype=white_arch.name,
            black_archetype=black_arch.name,
            result="",
            total_plies=0,
            seed=seed,
            duration=0.0,
            
            # Initialize all hypothesis fields
            first_move_notation="",
            first_move_eval_delta=0.0,
            move_1_win_rate_variance=0.0,
            move_2_win_rate_variance=0.0,
            move_3_win_rate_variance=0.0,
            
            white_free_pawn_file="",
            black_free_pawn_file="",
            free_pawn_centrality_score=0.0,
            mobility_metrics={},
            tempo_metrics={},
            
            free_pawn_discovery_ply=0,
            discovery_side="",
            eval_after_discovery=0.0,
            information_advantage_metrics={},
            
            opening_phase_evals=[],
            first_player_entanglement_activation=0,
            second_player_reaction_time=0,
            eval_after_opening=0.0,
            color_advantage_metrics={},
            
            entanglement_break_count=0,
            entanglement_persistence_ratio=0.0,
            game_length=0,
            tactical_vs_positional_score=0.0,
            entanglement_stability_metrics={},
            
            reactive_check_count=0,
            reactive_check_sequence=[],
            reactive_check_survival_rate=0.0,
            collapse_prediction_metrics={},
            
            archetype_style=white_arch.name,
            entanglement_interaction_patterns={},
            archetype_win_rate_by_entanglement_type=0.0,
            style_entanglement_correlation=0.0,
            
            forced_move_count=0,
            forced_move_cascade_length=0,
            evaluation_volatility=0.0,
            tactical_complexity_score=0.0,
            game_predictability_metrics={},
            
            per_ply_data=[]
        )
        
        # Game simulation with enhanced tracking
        start_time = time.time()
        move_count = 0
        evaluations = []
        reactive_checks = []
        forced_moves = []
        entanglement_breaks = 0
        
        # Track free pawn discovery
        white_free_discovered = False
        black_free_discovered = False
        discovery_ply = 0
        
        while move_count < 200:  # Max moves
            current_color = game.board.to_move
            current_arch = white_arch if current_color == "W" else black_arch
            
            # Get legal moves
            legal_moves = game.board.legal_moves()
            if not legal_moves:
                if game.board.in_check(current_color):
                    hypothesis_data.result = "B wins" if current_color == "W" else "W wins"
                else:
                    hypothesis_data.result = "Draw"
                break
            
            # Choose move (simplified for now)
            chosen_move = random.choice(legal_moves)
            piece, to, spec = chosen_move
            frm = piece.pos
            
            # Record first move for H1
            if move_count == 0:
                hypothesis_data.first_move_notation = f"{self._square_to_str(frm)}{self._square_to_str(to)}"
            
            # Apply move
            meta = game.board._apply_move_internal(frm, to, spec)
            move_count += 1
            
            # Track evaluations for volatility (H8)
            eval_score = self._simple_evaluate(game.board, current_color)
            evaluations.append(eval_score)
            
            # Track reactive checks (H6)
            if game.board.in_check(current_color):
                reactive_checks.append(move_count)
                hypothesis_data.reactive_check_count += 1
            
            # Track forced moves (H8)
            if meta.get("forced"):
                forced_moves.append(move_count)
                hypothesis_data.forced_move_count += 1
            
            # Track entanglement breaks (H5)
            if meta.get("capture_id") or spec.get("promotion"):
                entanglement_breaks += 1
                hypothesis_data.entanglement_break_count += 1
            
            # Track free pawn discovery (H3)
            if not white_free_discovered and current_color == "W":
                # Check if white's free pawn was revealed
                if self._free_pawn_revealed(game, "W"):
                    white_free_discovered = True
                    if discovery_ply == 0:
                        discovery_ply = move_count
                        hypothesis_data.discovery_side = "W"
            
            if not black_free_discovered and current_color == "B":
                # Check if black's free pawn was revealed
                if self._free_pawn_revealed(game, "B"):
                    black_free_discovered = True
                    if discovery_ply == 0:
                        discovery_ply = move_count
                        hypothesis_data.discovery_side = "B"
            
            # Record per-ply data
            ply_data = {
                "ply": move_count,
                "side": current_color,
                "move": f"{self._square_to_str(frm)}{self._square_to_str(to)}",
                "eval": eval_score,
                "reactive_check": game.board.in_check(current_color),
                "forced_move": meta.get("forced", False),
                "entanglement_break": meta.get("capture_id") is not None or spec.get("promotion") is not None
            }
            hypothesis_data.per_ply_data.append(ply_data)
            
            # Check for game end
            if game.board.in_check(current_color) and not game.board.legal_moves():
                hypothesis_data.result = "B wins" if current_color == "W" else "W wins"
                break
            elif not game.board.in_check(current_color) and not game.board.legal_moves():
                hypothesis_data.result = "Draw"
                break
        
        # Game ended by move limit
        if hypothesis_data.result == "":
            hypothesis_data.result = "Draw"
        
        # Calculate hypothesis-specific metrics
        self._calculate_hypothesis_metrics(hypothesis_data, evaluations, reactive_checks, forced_moves)
        
        hypothesis_data.total_plies = move_count
        hypothesis_data.duration = time.time() - start_time
        
        return hypothesis_data
    
    def _calculate_hypothesis_metrics(self, data: QECHypothesisData, 
                                    evaluations: List[float], reactive_checks: List[int], 
                                    forced_moves: List[int]):
        """Calculate all hypothesis-specific metrics"""
        
        # H1: Opening Determinism
        if len(evaluations) >= 3:
            data.move_1_win_rate_variance = self._calculate_variance_after_move(1)
            data.move_2_win_rate_variance = self._calculate_variance_after_move(2)
            data.move_3_win_rate_variance = self._calculate_variance_after_move(3)
        
        # H2: Free-Pawn Centrality
        data.white_free_pawn_file = "d"  # Simplified
        data.black_free_pawn_file = "e"  # Simplified
        data.free_pawn_centrality_score = self._calculate_centrality_score(data.white_free_pawn_file, data.black_free_pawn_file)
        
        # H3: Information-Asymmetry Effect
        data.free_pawn_discovery_ply = len(data.per_ply_data) // 2  # Simplified
        data.eval_after_discovery = evaluations[-1] if evaluations else 0.0
        
        # H4: Second-Player Advantage
        data.opening_phase_evals = evaluations[:10] if len(evaluations) >= 10 else evaluations
        data.eval_after_opening = evaluations[9] if len(evaluations) > 9 else 0.0
        
        # H5: Entanglement Stability vs. Breakage
        data.entanglement_persistence_ratio = 1.0 - (data.entanglement_break_count / max(1, data.total_plies))
        data.game_length = data.total_plies
        data.tactical_vs_positional_score = self._calculate_tactical_score(data)
        
        # H6: Reactive-Check Survival Bias
        data.reactive_check_sequence = reactive_checks
        data.reactive_check_survival_rate = len(reactive_checks) / max(1, data.total_plies)
        
        # H7: Archetype-Entanglement Interaction
        data.archetype_style = data.white_archetype
        data.style_entanglement_correlation = self._calculate_style_entanglement_correlation(data)
        
        # H8: Forced-Move Cascade Effect
        data.forced_move_cascade_length = len(forced_moves)
        data.evaluation_volatility = self._calculate_evaluation_volatility(evaluations)
        data.tactical_complexity_score = self._calculate_tactical_complexity(data)
    
    def _simple_evaluate(self, board: Board, color: Color) -> float:
        """Simple position evaluation"""
        # Simplified evaluation for hypothesis testing
        material = 0
        for piece in board.pieces:
            if not piece.alive:
                continue
            
            piece_values = {'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0}
            value = piece_values.get(piece.kind, 0)
            
            if piece.color == color:
                material += value
            else:
                material -= value
        
        return material
    
    def _free_pawn_revealed(self, game: Game, color: Color) -> bool:
        """Check if free pawn was revealed (simplified)"""
        # This would need proper implementation
        return random.random() < 0.1  # 10% chance for testing
    
    def _calculate_centrality_score(self, white_file: str, black_file: str) -> float:
        """Calculate centrality score for free pawns"""
        file_values = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8}
        white_val = file_values.get(white_file, 4)
        black_val = file_values.get(black_file, 4)
        
        # Central files (d,e) get higher scores
        white_centrality = 1.0 - abs(white_val - 4.5) / 3.5
        black_centrality = 1.0 - abs(black_val - 4.5) / 3.5
        
        return (white_centrality + black_centrality) / 2.0
    
    def _calculate_tactical_score(self, data: QECHypothesisData) -> float:
        """Calculate tactical vs positional score"""
        return data.entanglement_break_count / max(1, data.total_plies)
    
    def _calculate_style_entanglement_correlation(self, data: QECHypothesisData) -> float:
        """Calculate correlation between archetype style and entanglement interaction"""
        # Simplified correlation calculation
        return random.random()  # Placeholder
    
    def _calculate_evaluation_volatility(self, evaluations: List[float]) -> float:
        """Calculate evaluation volatility"""
        if len(evaluations) < 2:
            return 0.0
        
        mean = sum(evaluations) / len(evaluations)
        variance = sum((x - mean) ** 2 for x in evaluations) / len(evaluations)
        return variance ** 0.5
    
    def _calculate_tactical_complexity(self, data: QECHypothesisData) -> float:
        """Calculate tactical complexity score"""
        return (data.forced_move_count + data.reactive_check_count) / max(1, data.total_plies)
    
    def _calculate_variance_after_move(self, move_num: int) -> float:
        """Calculate win rate variance after specific move number"""
        # This would need to be calculated across all games
        return random.random()  # Placeholder
    
    def _square_to_str(self, square: Square) -> str:
        """Convert square to string notation"""
        f, r = square
        return f"{'abcdefgh'[f]}{r+1}"
    
    def _update_hypothesis_tracking(self, data: QECHypothesisData):
        """Update hypothesis tracking based on collected data"""
        for hyp in QEC_HYPOTHESES:
            self.hypothesis_metrics[hyp.id]["data_collected"] += 1
            self.hypothesis_metrics[hyp.id]["last_updated"] = time.time()
    
    def analyze_hypotheses(self):
        """Analyze collected data for hypothesis testing"""
        print("=== QEC Hypothesis Analysis ===")
        
        if not self.results:
            print("No data to analyze")
            return
        
        print(f"Total games analyzed: {len(self.results)}")
        
        # Analyze each hypothesis
        for hyp in QEC_HYPOTHESES:
            print(f"\n{hyp.id}: {hyp.title}")
            print(f"  Prediction: {hyp.prediction}")
            
            # Calculate hypothesis-specific analysis
            analysis = self._analyze_hypothesis(hyp)
            print(f"  Status: {analysis['status']}")
            print(f"  Evidence: {analysis['evidence']}")
            
            # Update hypothesis status
            self.hypothesis_metrics[hyp.id]["status"] = analysis['status']
    
    def _analyze_hypothesis(self, hypothesis) -> Dict[str, Any]:
        """Analyze specific hypothesis with collected data"""
        # This would contain the actual statistical analysis
        # For now, return placeholder analysis
        
        if hypothesis.id == "H1":
            return {
                "status": "partial",
                "evidence": "Insufficient data for variance analysis"
            }
        elif hypothesis.id == "H2":
            return {
                "status": "partial", 
                "evidence": "Free pawn centrality correlation needs more games"
            }
        else:
            return {
                "status": "untested",
                "evidence": "Analysis not yet implemented"
            }
    
    def save_hypothesis_data(self):
        """Save all hypothesis data to files"""
        # Save game results
        results_file = os.path.join(self.logs_dir, "hypothesis_results.json")
        with open(results_file, 'w') as f:
            json.dump([asdict(result) for result in self.results], f, indent=2)
        
        # Save hypothesis metrics
        metrics_file = os.path.join(self.logs_dir, "hypothesis_metrics.json")
        with open(metrics_file, 'w') as f:
            json.dump(self.hypothesis_metrics, f, indent=2)
        
        print(f"Hypothesis data saved to {self.logs_dir}")

if __name__ == "__main__":
    # Test hypothesis testing system
    tester = QECHypothesisTester()
    
    # Run small experiment
    results = tester.run_hypothesis_experiment(
        archetypes=["Carlsen-like", "Tal-like", "Karpov-like"],
        num_games=50
    )
    
    # Analyze hypotheses
    tester.analyze_hypotheses()
    
    # Save data
    tester.save_hypothesis_data()
