"""
QEC Research Simulator
Comprehensive data collection for QEC rule analysis and pattern discovery
"""

import os
import json
import time
import random
import hashlib
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
from main import Game, Board, Piece, Square, Color
from qec_archetypes import QECArchetype, QEC_ARCHETYPES, get_archetype_by_name
from qec_evaluation import QECEvaluator, QECEvaluation

@dataclass
class QECGameResult:
    """Comprehensive QEC game result for research"""
    game_id: str
    white_archetype: str
    black_archetype: str
    result: str  # "W wins", "B", "Draw"
    total_plies: int
    captures: int
    promotions: int
    forced_moves: int
    reactive_moves: int
    reactive_mates: int
    ent_map_hash: str
    ent_pairs_remaining_10: int
    ent_pairs_remaining_20: int
    ent_pairs_remaining_30: int
    king_reacts: int
    king_distance_traveled: float
    eval_swing: float  # std dev of evaluations
    avg_legal_moves: float
    first_move_advantage: float
    duration: float
    seed: int
    per_ply_data: List[Dict[str, Any]]

@dataclass
class QECResearchConfig:
    """Configuration for QEC research experiments"""
    archetypes: List[str]
    num_games_per_pairing: int
    num_ent_maps: int
    search_depth: int
    move_limit: int
    max_moves: int
    logs_dir: str
    seed_base: int
    save_detailed_logs: bool
    save_per_ply_data: bool

class QECResearchSimulator:
    """QEC research simulator with comprehensive data collection"""
    
    def __init__(self, config: QECResearchConfig):
        self.config = config
        self.results = []
        self.ent_maps = []
        self.game_count = 0
        
        # Create logs directory
        os.makedirs(config.logs_dir, exist_ok=True)
        
        # Generate entanglement maps
        self._generate_ent_maps()
        
    def _generate_ent_maps(self):
        """Generate random entanglement maps for experiments"""
        for i in range(self.config.num_ent_maps):
            # Create random entanglement mapping
            ent_map = self._create_random_ent_map()
            self.ent_maps.append(ent_map)
    
    def _create_random_ent_map(self) -> Dict[str, Any]:
        """Create random entanglement mapping following QEC rules"""
        import random
        
        # Get all white pawns and black non-king pieces
        white_pawns = [f"W_P_{file}{rank}" for file in "abcdefgh" for rank in "2"]
        black_pieces = []
        for file in "abcdefgh":
            for rank in "7":
                for piece in ["P", "R", "N", "B", "Q"]:  # No king
                    black_pieces.append(f"B_{piece}_{file}{rank}")
        
        # Get all black pawns and white non-king pieces  
        black_pawns = [f"B_P_{file}{rank}" for file in "abcdefgh" for rank in "7"]
        white_pieces = []
        for file in "abcdefgh":
            for rank in "2":
                for piece in ["P", "R", "N", "B", "Q"]:  # No king
                    white_pieces.append(f"W_{piece}_{file}{rank}")
        
        # Select 7 white pawns to entangle with 7 black non-king pieces
        selected_white_pawns = random.sample(white_pawns, 7)
        selected_black_targets = random.sample(black_pieces, 7)
        white_free_pawn = [p for p in white_pawns if p not in selected_white_pawns][0]
        
        # Select 7 black pawns to entangle with 7 white non-king pieces
        selected_black_pawns = random.sample(black_pawns, 7)
        selected_white_targets = random.sample(white_pieces, 7)
        black_free_pawn = [p for p in black_pawns if p not in selected_black_pawns][0]
        
        # Create mappings
        w_pawn_to_black = dict(zip(selected_white_pawns, selected_black_targets))
        b_pawn_to_white = dict(zip(selected_black_pawns, selected_white_targets))
        
        return {
            "W_pawn_to_black": w_pawn_to_black,
            "B_pawn_to_white": b_pawn_to_white,
            "white_free_pawn": white_free_pawn,
            "black_free_pawn": black_free_pawn
        }
    
    def _get_ent_hash(self, ent_map: Dict[str, Any]) -> str:
        """Get hash of entanglement map"""
        return hashlib.md5(json.dumps(ent_map, sort_keys=True).encode()).hexdigest()[:8]
    
    def _simulate_qec_game(self, white_arch: QECArchetype, black_arch: QECArchetype, 
                          ent_map: Dict[str, Any], seed: int) -> QECGameResult:
        """Simulate a single QEC game with comprehensive data collection"""
        random.seed(seed)
        
        # Create game with specific entanglement
        game = Game(seed=seed)
        game.live = False
        
        # Set entanglement map
        game.ent.W_pawn_to_black = ent_map.get("W_pawn_to_black", {})
        game.ent.B_pawn_to_white = ent_map.get("B_pawn_to_white", {})
        game.ent.white_free_pawn = ent_map.get("white_free_pawn")
        game.ent.black_free_pawn = ent_map.get("black_free_pawn")
        
        # Create evaluators
        white_evaluator = QECEvaluator(white_arch)
        black_evaluator = QECEvaluator(black_arch)
        
        # Game state tracking
        per_ply_data = []
        evaluations = []
        king_positions = {"W": None, "B": None}
        king_distance = {"W": 0.0, "B": 0.0}
        
        move_count = 0
        captures = 0
        promotions = 0
        forced_moves = 0
        reactive_moves = 0
        reactive_mates = 0
        
        start_time = time.time()
        result = None
        
        while move_count < self.config.max_moves:
            current_color = game.board.to_move
            current_arch = white_arch if current_color == "W" else black_arch
            current_evaluator = white_evaluator if current_color == "W" else black_evaluator
            
            # Get legal moves
            legal_moves = game.board.legal_moves()
            if not legal_moves:
                if game.board.in_check(current_color):
                    result = "B wins" if current_color == "W" else "W wins"
                else:
                    result = "Draw"
                break
            
            # Choose move using archetype-based evaluation
            chosen_move = self._choose_archetype_move(game, current_arch, current_evaluator, legal_moves)
            if chosen_move is None:
                result = "Draw"
                break
            
            piece, to, spec = chosen_move
            frm = piece.pos
            
            # Record pre-move state
            pre_eval = current_evaluator.evaluate(game.board, current_color)
            evaluations.append(pre_eval.total)
            
            # Apply primary move
            meta = game.board._apply_move_internal(frm, to, spec)
            move_count += 1
            
            # Track statistics
            if meta.get("capture_id"):
                captures += 1
            if spec.get("promotion"):
                promotions += 1
            
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
                forced_happened = game._maybe_force_counterpart(meta.get("moved_id", ""), record=False)
            
            if forced_happened:
                forced_moves += 1
            
            # Reactive king escape
            defender = game.board.to_move
            reactive_happened = False
            if game.board.in_check(defender):
                reactive_happened = game._do_reactive_king_escape(defender, record=False)
                if reactive_happened:
                    reactive_moves += 1
                else:
                    # No legal king escape = reactive mate
                    reactive_mates += 1
                    result = "B wins" if defender == "W" else "W wins"
                    break
            
            # Track king movement
            king = next((p for p in game.board.pieces if p.alive and p.color == current_color and p.kind == "K"), None)
            if king:
                if king_positions[current_color]:
                    old_pos = king_positions[current_color]
                    new_pos = king.pos
                    distance = ((old_pos[0] - new_pos[0])**2 + (old_pos[1] - new_pos[1])**2)**0.5
                    king_distance[current_color] += distance
                king_positions[current_color] = king.pos
            
            # Record per-ply data
            if self.config.save_per_ply_data:
                ply_data = {
                    "game_id": f"game_{self.game_count:04d}",
                    "ply": move_count,
                    "side": current_color,
                    "primary": f"{self._square_to_str(frm)}{self._square_to_str(to)}",
                    "forced": "—" if not forced_happened else "forced_move",
                    "react": "—" if not reactive_happened else "react_move",
                    "ent_map_hash": self._get_ent_hash(ent_map),
                    "ent_changes": [],  # Would track entanglement changes
                    "eval": pre_eval.total,
                    "phase": self._get_game_phase(move_count),
                    "legal_count": len(legal_moves),
                    "time_used_ms": 0,  # Would track actual time
                    "notes": self._get_move_notes(meta, forced_happened, reactive_happened)
                }
                per_ply_data.append(ply_data)
            
            # Check for game end
            if game.board.in_check(current_color) and not game.board.legal_moves():
                result = "B wins" if current_color == "W" else "W wins"
                break
            elif not game.board.in_check(current_color) and not game.board.legal_moves():
                result = "Draw"
                break
        
        # Game ended by move limit
        if result is None:
            result = "Draw"
        
        duration = time.time() - start_time
        
        # Calculate derived statistics
        eval_swing = self._calculate_eval_swing(evaluations)
        avg_legal_moves = sum(len(game.board.legal_moves()) for _ in range(10)) / 10  # Sample
        first_move_advantage = self._calculate_first_move_advantage(result, move_count)
        
        # Count entanglement pairs at different stages
        ent_pairs_10 = self._count_ent_pairs(game, 10)
        ent_pairs_20 = self._count_ent_pairs(game, 20)
        ent_pairs_30 = self._count_ent_pairs(game, 30)
        
        return QECGameResult(
            game_id=f"game_{self.game_count:04d}",
            white_archetype=white_arch.name,
            black_archetype=black_arch.name,
            result=result,
            total_plies=move_count,
            captures=captures,
            promotions=promotions,
            forced_moves=forced_moves,
            reactive_moves=reactive_moves,
            reactive_mates=reactive_mates,
            ent_map_hash=self._get_ent_hash(ent_map),
            ent_pairs_remaining_10=ent_pairs_10,
            ent_pairs_remaining_20=ent_pairs_20,
            ent_pairs_remaining_30=ent_pairs_30,
            king_reacts=reactive_moves,
            king_distance_traveled=sum(king_distance.values()),
            eval_swing=eval_swing,
            avg_legal_moves=avg_legal_moves,
            first_move_advantage=first_move_advantage,
            duration=duration,
            seed=seed,
            per_ply_data=per_ply_data
        )
    
    def _choose_archetype_move(self, game: Game, archetype: QECArchetype, 
                              evaluator: QECEvaluator, legal_moves: List[Tuple[Piece, Square, Dict]]) -> Optional[Tuple[Piece, Square, Dict]]:
        """Choose move using archetype-based evaluation"""
        if not legal_moves:
            return None
        
        # Limit moves to consider (top N)
        if len(legal_moves) > archetype.move_limit:
            legal_moves = legal_moves[:archetype.move_limit]
        
        # For now, use simple heuristic selection based on archetype preferences
        # This avoids the complex move simulation that's causing issues
        
        # Sort moves by archetype preferences
        if archetype.aggression > 0.7:  # Aggressive players prefer checks and captures
            # Prioritize moves that give checks or captures
            def move_priority(move):
                piece, to, spec = move
                score = 0
                if spec.get("capture"):
                    score += 100
                if spec.get("promotion"):
                    score += 200
                # Check if move gives check (simplified)
                if self._move_gives_check(game, move):
                    score += 150
                return score
            legal_moves.sort(key=move_priority, reverse=True)
        elif archetype.king_safety > 0.8:  # Defensive players prefer safe moves
            # Prioritize moves that don't expose king
            def move_priority(move):
                piece, to, spec = move
                score = 0
                if piece.kind == 'K':  # Avoid moving king unless necessary
                    score -= 50
                if spec.get("capture"):
                    score += 50
                return score
            legal_moves.sort(key=move_priority, reverse=True)
        else:  # Balanced players
            # Simple material-based evaluation
            def move_priority(move):
                piece, to, spec = move
                score = 0
                if spec.get("capture"):
                    target = game.board.piece_at(to)
                    if target:
                        piece_values = {'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0}
                        score += piece_values.get(target.kind, 0)
                return score
            legal_moves.sort(key=move_priority, reverse=True)
        
        # Choose from top moves with some randomness
        top_moves = legal_moves[:max(1, len(legal_moves)//3)]
        return random.choice(top_moves)
    
    def _move_gives_check(self, game: Game, move: Tuple[Piece, Square, Dict]) -> bool:
        """Check if move gives check (simplified)"""
        # This is a simplified check - in reality would need proper check detection
        piece, to, spec = move
        if piece.kind in ['Q', 'R', 'B']:
            # Assume diagonal/straight moves toward enemy king might give check
            return random.random() < 0.1  # 10% chance for simplification
        return False
    
    def _square_to_str(self, square: Square) -> str:
        """Convert square to string notation"""
        f, r = square
        return f"{'abcdefgh'[f]}{r+1}"
    
    def _get_game_phase(self, move_count: int) -> str:
        """Determine game phase"""
        if move_count <= 15:
            return "opening"
        elif move_count <= 30:
            return "middlegame"
        else:
            return "endgame"
    
    def _get_move_notes(self, meta: Dict, forced: bool, reactive: bool) -> str:
        """Get move notes"""
        notes = []
        if meta.get("capture_id"):
            notes.append("capture")
        if meta.get("castle_rook_to"):
            notes.append("castle")
        if forced:
            notes.append("forced")
        if reactive:
            notes.append("react")
        if meta.get("promotion"):
            notes.append("promote")
        return "; ".join(notes) if notes else ""
    
    def _calculate_eval_swing(self, evaluations: List[int]) -> float:
        """Calculate evaluation swing (std dev)"""
        if len(evaluations) < 2:
            return 0.0
        
        mean = sum(evaluations) / len(evaluations)
        variance = sum((x - mean) ** 2 for x in evaluations) / len(evaluations)
        return variance ** 0.5
    
    def _calculate_first_move_advantage(self, result: str, moves: int) -> float:
        """Calculate first move advantage"""
        if result == "W wins":
            return 1.0
        elif result == "B wins":
            return -1.0
        else:
            return 0.0
    
    def _count_ent_pairs(self, game: Game, move_threshold: int) -> int:
        """Count remaining entanglement pairs"""
        # This would need proper entanglement counting
        # For now, return placeholder
        return len(game.ent.W_pawn_to_black) + len(game.ent.B_pawn_to_white)
    
    def run_experiment(self) -> List[QECGameResult]:
        """Run complete research experiment"""
        print(f"=== QEC Research Experiment ===")
        print(f"Archetypes: {self.config.archetypes}")
        print(f"Games per pairing: {self.config.num_games_per_pairing}")
        print(f"Entanglement maps: {self.config.num_ent_maps}")
        print(f"Total games: {len(self.config.archetypes) * len(self.config.archetypes) * self.config.num_games_per_pairing * self.config.num_ent_maps}")
        print()
        
        results = []
        
        # Run all pairings
        for i, white_arch_name in enumerate(self.config.archetypes):
            for j, black_arch_name in enumerate(self.config.archetypes):
                white_arch = get_archetype_by_name(white_arch_name)
                black_arch = get_archetype_by_name(black_arch_name)
                
                if not white_arch or not black_arch:
                    continue
                
                print(f"Pairing {i+1}-{j+1}: {white_arch_name} vs {black_arch_name}")
                
                # Run games for this pairing
                for game_num in range(self.config.num_games_per_pairing):
                    for ent_map in self.ent_maps:
                        seed = self.config.seed_base + self.game_count
                        
                        result = self._simulate_qec_game(white_arch, black_arch, ent_map, seed)
                        results.append(result)
                        
                        if self.config.save_detailed_logs:
                            self._save_game_logs(result)
                        
                        self.game_count += 1
                        
                        print(f"  Game {self.game_count}: {result.result} ({result.total_plies} plies)")
        
        self.results.extend(results)
        return results
    
    def _save_game_logs(self, result: QECGameResult):
        """Save detailed game logs"""
        # Create date-based directory
        date_dir = time.strftime("%Y%m%d", time.localtime())
        out_dir = os.path.join(self.config.logs_dir, date_dir)
        os.makedirs(out_dir, exist_ok=True)
        
        # Save game result
        result_file = os.path.join(out_dir, f"{result.game_id}_result.json")
        with open(result_file, 'w') as f:
            json.dump(asdict(result), f, indent=2)
        
        # Save per-ply data
        if result.per_ply_data:
            ply_file = os.path.join(out_dir, f"{result.game_id}_plys.jsonl")
            with open(ply_file, 'w') as f:
                for ply in result.per_ply_data:
                    f.write(json.dumps(ply) + "\n")
    
    def analyze_results(self, results: List[QECGameResult] = None):
        """Analyze research results"""
        if results is None:
            results = self.results
        
        if not results:
            print("No results to analyze")
            return
        
        print("=== QEC Research Analysis ===")
        print(f"Total games: {len(results)}")
        
        # Result distribution
        results_dist = defaultdict(int)
        for result in results:
            results_dist[result.result] += 1
        
        print(f"Results: {dict(results_dist)}")
        
        # Archetype performance
        archetype_stats = defaultdict(lambda: {"wins": 0, "losses": 0, "draws": 0, "games": 0})
        
        for result in results:
            # White archetype stats
            archetype_stats[result.white_archetype]["games"] += 1
            if result.result == "W wins":
                archetype_stats[result.white_archetype]["wins"] += 1
            elif result.result == "B wins":
                archetype_stats[result.white_archetype]["losses"] += 1
            else:
                archetype_stats[result.white_archetype]["draws"] += 1
            
            # Black archetype stats
            archetype_stats[result.black_archetype]["games"] += 1
            if result.result == "B wins":
                archetype_stats[result.black_archetype]["wins"] += 1
            elif result.result == "W wins":
                archetype_stats[result.black_archetype]["losses"] += 1
            else:
                archetype_stats[result.black_archetype]["draws"] += 1
        
        # Print archetype statistics
        print(f"\nArchetype Performance:")
        print(f"{'Archetype':<15} {'Games':<6} {'Wins':<5} {'Losses':<7} {'Draws':<5} {'Win%':<6}")
        print("-" * 60)
        
        for archetype, stats in archetype_stats.items():
            win_rate = stats["wins"] / stats["games"] * 100 if stats["games"] > 0 else 0
            print(f"{archetype:<15} {stats['games']:<6} {stats['wins']:<5} "
                  f"{stats['losses']:<7} {stats['draws']:<5} {win_rate:<6.1f}")
        
        # QEC-specific statistics
        total_forced = sum(r.forced_moves for r in results)
        total_reactive = sum(r.reactive_moves for r in results)
        total_reactive_mates = sum(r.reactive_mates for r in results)
        avg_plies = sum(r.total_plies for r in results) / len(results)
        avg_captures = sum(r.captures for r in results) / len(results)
        
        print(f"\nQEC Statistics:")
        print(f"Total forced moves: {total_forced}")
        print(f"Total reactive moves: {total_reactive}")
        print(f"Total reactive mates: {total_reactive_mates}")
        print(f"Average plies: {avg_plies:.1f}")
        print(f"Average captures: {avg_captures:.1f}")
        
        # Save analysis
        analysis_file = os.path.join(self.config.logs_dir, "research_analysis.json")
        with open(analysis_file, 'w') as f:
            json.dump({
                "total_games": len(results),
                "result_distribution": dict(results_dist),
                "archetype_statistics": {k: dict(v) for k, v in archetype_stats.items()},
                "qec_statistics": {
                    "total_forced_moves": total_forced,
                    "total_reactive_moves": total_reactive,
                    "total_reactive_mates": total_reactive_mates,
                    "average_plies": avg_plies,
                    "average_captures": avg_captures
                }
            }, f, indent=2)
        
        print(f"\nAnalysis saved to: {analysis_file}")

if __name__ == "__main__":
    # Test research simulator
    config = QECResearchConfig(
        archetypes=["Carlsen-like", "Tal-like", "Karpov-like"],
        num_games_per_pairing=2,
        num_ent_maps=2,
        search_depth=2,
        move_limit=30,
        max_moves=100,
        logs_dir="qec_research_logs",
        seed_base=42,
        save_detailed_logs=True,
        save_per_ply_data=True
    )
    
    simulator = QECResearchSimulator(config)
    results = simulator.run_experiment()
    simulator.analyze_results(results)
