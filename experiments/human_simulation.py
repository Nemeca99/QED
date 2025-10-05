"""
Human-like QEC Simulation Engine
Mimics real chess players with authentic skill profiles, playing styles, and error patterns
"""

import os
import json
import time
import random
import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from collections import defaultdict

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import main
from player_database import ChessPlayer, PlayerStyle, get_player_by_name, get_tournament_pools

@dataclass
class GameResult:
    white_player: str
    black_player: str
    result: str  # "W wins", "B wins", "Draw", "Timeout"
    moves: int
    forced_moves: int
    reactive_moves: int
    captures: int
    entanglement_breaks: int
    final_board: str
    game_log: str
    pgn: str
    jsonl: str
    duration: float
    seed: int
    white_rating: int
    black_rating: int
    white_style: str
    black_style: str

class HumanQECSimulation:
    """Human-like QEC simulation with real player profiles"""
    
    def __init__(self, logs_dir: str = "human_logs", max_moves: int = 200):
        self.logs_dir = logs_dir
        self.max_moves = max_moves
        self.game_count = 0
        self.results = []
        
        # Create logs directory
        os.makedirs(logs_dir, exist_ok=True)
        
        # Initialize player pools
        self.tournament_pools = get_tournament_pools()
        
        # Game phase detection
        self.opening_moves = 15
        self.endgame_threshold = 20  # pieces remaining
        
    def _get_game_phase(self, move_number: int, pieces_remaining: int) -> str:
        """Determine current game phase"""
        if move_number <= self.opening_moves:
            return "opening"
        elif pieces_remaining <= self.endgame_threshold:
            return "endgame"
        else:
            return "middlegame"
    
    def _calculate_human_skill(self, player: ChessPlayer, game_phase: str, 
                             time_pressure: float = 0.0) -> float:
        """Calculate human skill level based on player profile and game state"""
        base_skill = player.rating / 2850.0  # Normalize to 0-1 scale
        
        # Time control adjustment
        time_control = "blitz" if time_pressure > 0.7 else "classical"
        time_adjustment = 1.0
        if player.time_control_preference != time_control:
            time_adjustment = 0.9 if time_control == "blitz" else 0.95
        
        # Style bonus for game phase
        style_bonus = 1.0
        if game_phase == "opening" and player.style in [PlayerStyle.OPENING, PlayerStyle.TACTICAL]:
            style_bonus = 1.1
        elif game_phase == "middlegame" and player.style in [PlayerStyle.TACTICAL, PlayerStyle.POSITIONAL]:
            style_bonus = 1.05
        elif game_phase == "endgame" and player.style in [PlayerStyle.ENDGAME, PlayerStyle.POSITIONAL]:
            style_bonus = 1.1
        
        # Time pressure effect
        time_pressure_penalty = 1.0 - (time_pressure * 0.3)
        
        # Calculate final skill
        final_skill = base_skill * time_adjustment * style_bonus * time_pressure_penalty
        return max(0.1, min(1.0, final_skill))
    
    def _get_human_move_quality(self, player: ChessPlayer, game_phase: str, 
                               time_pressure: float = 0.0) -> float:
        """Get move quality based on human skill and game state"""
        skill = self._calculate_human_skill(player, game_phase, time_pressure)
        
        # Add some randomness to simulate human inconsistency
        consistency = 0.8 + (player.rating - 2200) / 650.0 * 0.2  # Better players more consistent
        consistency = max(0.5, min(1.0, consistency))
        
        # Random variation around skill level
        variation = random.gauss(0, 0.1 * (1 - consistency))
        quality = skill + variation
        
        return max(0.1, min(1.0, quality))
    
    def _should_blunder(self, player: ChessPlayer, game_phase: str, 
                       time_pressure: float = 0.0) -> bool:
        """Determine if player should blunder based on profile and game state"""
        base_blunder_rate = player.blunder_rate
        
        # Time pressure increases blunder rate
        time_pressure_multiplier = 1.0 + (time_pressure * 2.0)
        
        # Game phase affects blunder rate
        phase_multiplier = 1.0
        if game_phase == "opening" and player.style == PlayerStyle.OPENING:
            phase_multiplier = 0.8
        elif game_phase == "endgame" and player.style == PlayerStyle.ENDGAME:
            phase_multiplier = 0.7
        
        # Calculate final blunder probability
        final_blunder_rate = base_blunder_rate * time_pressure_multiplier * phase_multiplier
        return random.random() < final_blunder_rate
    
    def _choose_human_move(self, game, player: ChessPlayer, 
                          game_phase: str, time_pressure: float = 0.0):
        """Choose a move using human-like decision making"""
        legal_moves = game.board.legal_moves()
        if not legal_moves:
            return None
        
        # Get move quality threshold
        move_quality = self._get_human_move_quality(player, game_phase, time_pressure)
        
        # Check for blunder
        if self._should_blunder(player, game_phase, time_pressure):
            # Choose a suboptimal move
            bad_moves = legal_moves[:len(legal_moves)//3]  # Take worst third
            if bad_moves:
                return random.choice(bad_moves)
        
        # Filter moves based on quality
        if move_quality > 0.8:
            # High quality - choose from best moves
            best_moves = legal_moves[-len(legal_moves)//3:]
            return random.choice(best_moves)
        elif move_quality > 0.6:
            # Medium quality - choose from middle moves
            mid_start = len(legal_moves)//3
            mid_end = 2 * len(legal_moves)//3
            mid_moves = legal_moves[mid_start:mid_end]
            return random.choice(mid_moves) if mid_moves else random.choice(legal_moves)
        else:
            # Low quality - choose from worst moves
            worst_moves = legal_moves[:len(legal_moves)//3]
            return random.choice(worst_moves) if worst_moves else random.choice(legal_moves)
    
    def _simulate_human_game(self, white_player: ChessPlayer, black_player: ChessPlayer, 
                           seed: int = None) -> GameResult:
        """Simulate a game between two human players"""
        if seed is None:
            seed = random.randint(1, 1000000)
        
        random.seed(seed)
        
        # Create game with random entanglement
        game = main.Game(seed=seed)
        game.live = False  # Disable live printing for simulation
        
        # Game state tracking
        move_count = 0
        forced_moves = 0
        reactive_moves = 0
        captures = 0
        entanglement_breaks = 0
        per_move_records: List[Dict[str, Any]] = []
        
        # Time pressure simulation (increases as game progresses)
        time_pressure = 0.0
        
        # Game log
        game_log = f"=== QEC Human Simulation ===\n"
        game_log += f"White: {white_player.name} (Rating: {white_player.rating}, Style: {white_player.style.value})\n"
        game_log += f"Black: {black_player.name} (Rating: {black_player.rating}, Style: {black_player.style.value})\n"
        game_log += f"Seed: {seed}\n\n"
        
        # Announce free pawns (as in real QEC)
        white_free = game.ent.W_pawn_to_black.get("free", "unknown")
        black_free = game.ent.B_pawn_to_white.get("free", "unknown")
        game_log += f"White's free pawn: {white_free}\n"
        game_log += f"Black's free pawn: {black_free}\n\n"
        
        # Game loop
        start_time = time.time()
        result = None
        
        while move_count < self.max_moves:
            current_player = white_player if game.board.to_move == "W" else black_player
            game_phase = self._get_game_phase(move_count, len([p for p in game.board.pieces if p.alive]))
            
            # Increase time pressure as game progresses
            time_pressure = min(0.8, move_count / self.max_moves * 0.8)
            
            # Choose move using human-like decision making
            move = self._choose_human_move(game, current_player, game_phase, time_pressure)
            
            if move is None:
                # No legal moves - checkmate or stalemate
                if game.board.in_check(game.board.to_move):
                    result = "B wins" if game.board.to_move == "W" else "W wins"
                else:
                    result = "Draw"
                break
            
            # Extract move components
            piece, to, spec = move
            frm = piece.pos
            
            # Apply primary move
            meta = game.board._apply_move_internal(frm, to, spec)
            move_count += 1
            
            # Track statistics
            if meta.get("capture_id"):
                captures += 1
            # If primary move caused capture or promotion, break entanglement accordingly
            if meta.get("capture_id"):
                game.ent.break_link_if_member(meta["capture_id"])  # type: ignore[attr-defined]
            if spec.get("promotion"):
                game.ent.break_link_if_member(piece.id)  # type: ignore[attr-defined]
            
            # Forced counterpart (castling rook prioritized)
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
            
            # Reactive check
            defender = game.board.to_move
            reactive_happened = False
            if game.board.in_check(defender):
                reactive_happened = game._do_reactive_king_escape(defender, record=False)
            if reactive_happened:
                reactive_moves += 1
            
            # Entanglement changes tracking (hash compare not available here; approximate by counts)
            # We track a simple counter when capture/promotion occurred above
            
            # Record per-move details after side-effects
            per_move_records.append({
                "move": move_count,
                "player": current_player.name,
                "from": frm,
                "to": to,
                "spec": spec,
                "capture_id": meta.get("capture_id"),
                "forced": forced_happened,
                "reactive": reactive_happened,
                "fen": game.board.to_fen(),
                "check_W": int(game.board.in_check("W")),
                "check_B": int(game.board.in_check("B"))
            })
            
            # Log move
            game_log += f"Move {move_count}: {current_player.name} plays {meta.get('move_notation', 'unknown')}\n"
            
            # Check for game end
            if game.board.in_check(game.board.to_move) and not game.board.legal_moves():
                result = "B wins" if game.board.to_move == "W" else "W wins"
                break
            elif not game.board.in_check(game.board.to_move) and not game.board.legal_moves():
                result = "Draw"
                break
        
        # Game ended by move limit
        if result is None:
            result = "Draw"
        
        duration = time.time() - start_time
        
        # Create result object
        game_result = GameResult(
            white_player=white_player.name,
            black_player=black_player.name,
            result=result,
            moves=move_count,
            forced_moves=forced_moves,
            reactive_moves=reactive_moves,
            captures=captures,
            entanglement_breaks=entanglement_breaks,
            final_board=str(game.board),
            game_log=game_log,
            pgn="",  # PGN not generated in human sim
            jsonl="",  # Will be set in _save_game_logs
            duration=duration,
            seed=seed,
            white_rating=white_player.rating,
            black_rating=black_player.rating,
            white_style=white_player.style.value,
            black_style=black_player.style.value
        )
        
        # Attach per-move records for saving
        game_result._records = per_move_records  # type: ignore[attr-defined]
        return game_result
    
    def _save_game_logs(self, result: GameResult):
        """Save game logs to files in date-based subfolders and JSONL per-move"""
        ts_struct = time.localtime()
        date_dir = time.strftime("%Y%m%d", ts_struct)
        time_stamp = time.strftime("%H%M%S", ts_struct)
        out_dir = os.path.join(self.logs_dir, date_dir)
        os.makedirs(out_dir, exist_ok=True)
        filename_base = f"game_{self.game_count:04d}_{time_stamp}"
        
        # Save game log
        log_file = os.path.join(out_dir, f"{filename_base}.log")
        with open(log_file, 'w') as f:
            f.write(result.game_log)
        
        # Save result summary
        summary_file = os.path.join(out_dir, f"{filename_base}_summary.json")
        summary = {
            "white_player": result.white_player,
            "black_player": result.black_player,
            "result": result.result,
            "moves": result.moves,
            "forced_moves": result.forced_moves,
            "reactive_moves": result.reactive_moves,
            "captures": result.captures,
            "entanglement_breaks": result.entanglement_breaks,
            "duration": result.duration,
            "seed": result.seed,
            "white_rating": result.white_rating,
            "black_rating": result.black_rating,
            "white_style": result.white_style,
            "black_style": result.black_style
        }
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Save per-move JSONL
        jsonl_file = os.path.join(out_dir, f"{filename_base}.jsonl")
        records = getattr(result, "_records", [])  # type: ignore[attr-defined]
        with open(jsonl_file, 'w') as f:
            for rec in records:
                f.write(json.dumps(rec) + "\n")
        
        # Expose paths in result for external tooling
        result.jsonl = jsonl_file
        result.game_log = log_file
    
    def run_tournament(self, pool_name: str, num_games: int = 100, 
                     round_robin: bool = True) -> List[GameResult]:
        """Run a tournament with specified player pool"""
        if pool_name not in self.tournament_pools:
            raise ValueError(f"Unknown pool: {pool_name}")
        
        players = self.tournament_pools[pool_name]
        if len(players) < 2:
            raise ValueError(f"Pool {pool_name} has less than 2 players")
        
        print(f"=== QEC Human Tournament ===")
        print(f"Pool: {pool_name} ({len(players)} players)")
        print(f"Games: {num_games}")
        print(f"Round robin: {round_robin}")
        print()
        
        results = []
        
        if round_robin:
            # Round robin tournament
            for i in range(len(players)):
                for j in range(i + 1, len(players)):
                    white = players[i]
                    black = players[j]
                    
                    print(f"Playing: {white.name} vs {black.name}")
                    result = self._simulate_human_game(white, black)
                    self._save_game_logs(result)
                    results.append(result)
                    
                    # Also play reverse colors
                    print(f"Playing: {black.name} vs {white.name}")
                    result = self._simulate_human_game(black, white)
                    self._save_game_logs(result)
                    results.append(result)
        else:
            # Random pairings
            for game_num in range(num_games):
                white, black = random.sample(players, 2)
                
                print(f"Game {game_num + 1}: {white.name} vs {black.name}")
                result = self._simulate_human_game(white, black)
                self._save_game_logs(result)
                results.append(result)
        
        self.results.extend(results)
        return results
    
    def run_single_match(self, white_name: str, black_name: str, seed: int = None) -> GameResult:
        """Run a single match between two specific players"""
        white_player = get_player_by_name(white_name)
        black_player = get_player_by_name(black_name)
        
        if not white_player:
            raise ValueError(f"Player not found: {white_name}")
        if not black_player:
            raise ValueError(f"Player not found: {black_name}")
        
        print(f"=== QEC Single Match ===")
        print(f"White: {white_player.name} (Rating: {white_player.rating})")
        print(f"Black: {black_player.name} (Rating: {black_player.rating})")
        print()
        
        result = self._simulate_human_game(white_player, black_player, seed)
        self._save_game_logs(result)
        self.results.append(result)
        
        return result
    
    def analyze_results(self, results: List[GameResult] = None):
        """Analyze tournament results"""
        if results is None:
            results = self.results
        
        if not results:
            print("No results to analyze")
            return
        
        print("=== Tournament Analysis ===")
        print(f"Total games: {len(results)}")
        
        # Result distribution
        results_dist = defaultdict(int)
        for result in results:
            results_dist[result.result] += 1
        
        print(f"Results: {dict(results_dist)}")
        
        # Player statistics
        player_stats = defaultdict(lambda: {"wins": 0, "losses": 0, "draws": 0, "games": 0})
        
        for result in results:
            # White player stats
            player_stats[result.white_player]["games"] += 1
            if result.result == "W wins":
                player_stats[result.white_player]["wins"] += 1
            elif result.result == "B wins":
                player_stats[result.white_player]["losses"] += 1
            else:
                player_stats[result.white_player]["draws"] += 1
            
            # Black player stats
            player_stats[result.black_player]["games"] += 1
            if result.result == "B wins":
                player_stats[result.black_player]["wins"] += 1
            elif result.result == "W wins":
                player_stats[result.black_player]["losses"] += 1
            else:
                player_stats[result.black_player]["draws"] += 1
        
        # Print player statistics
        print("\nPlayer Statistics:")
        for player, stats in player_stats.items():
            win_rate = stats["wins"] / stats["games"] * 100 if stats["games"] > 0 else 0
            print(f"{player:20} | {stats['wins']:3}W {stats['losses']:3}L {stats['draws']:3}D | {win_rate:5.1f}% win rate")
        
        # Game statistics
        avg_moves = sum(r.moves for r in results) / len(results)
        avg_forced = sum(r.forced_moves for r in results) / len(results)
        avg_reactive = sum(r.reactive_moves for r in results) / len(results)
        avg_captures = sum(r.captures for r in results) / len(results)
        
        print(f"\nGame Statistics:")
        print(f"Average moves: {avg_moves:.1f}")
        print(f"Average forced moves: {avg_forced:.1f}")
        print(f"Average reactive moves: {avg_reactive:.1f}")
        print(f"Average captures: {avg_captures:.1f}")

if __name__ == "__main__":
    # Test the human simulation
    sim = HumanQECSimulation()
    
    # Run a small test
    print("Testing human simulation...")
    result = sim.run_single_match("Magnus Carlsen", "Fabiano Caruana", seed=42)
    
    print(f"\nResult: {result.result}")
    print(f"Moves: {result.moves}")
    print(f"Duration: {result.duration:.2f}s")
    
    # Analyze results
    sim.analyze_results()
