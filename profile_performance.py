"""
QEC Performance Profiler
Profile key functions for optimization opportunities
"""

import sys
import os
import time
import cProfile
import pstats
from typing import List, Tuple, Dict, Any

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))
import main as qec_main

class QECPerformanceProfiler:
    """Profile QEC performance bottlenecks"""
    
    def __init__(self):
        self.results = {}
    
    def profile_legal_moves(self, num_games: int = 10):
        """Profile legal move generation"""
        print(f"Profiling legal move generation for {num_games} games...")
        
        def run_games():
            for i in range(num_games):
                game = qec_main.Game(seed=42 + i)
                for _ in range(10):  # 10 moves per game
                    legal_moves = game.board.legal_moves()
                    if not legal_moves:
                        break
                    # Make a random move
                    import random
                    move = random.choice(legal_moves)
                    game.board._apply_move_internal(move[0].pos, move[1], move[2])
        
        # Profile the function
        profiler = cProfile.Profile()
        profiler.enable()
        start_time = time.time()
        run_games()
        end_time = time.time()
        profiler.disable()
        
        # Get stats
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        
        print(f"Legal moves profiling completed in {end_time - start_time:.2f}s")
        print("Top 10 functions by cumulative time:")
        stats.print_stats(10)
        
        self.results['legal_moves'] = {
            'time': end_time - start_time,
            'games': num_games
        }
    
    def profile_piece_moves(self, num_pieces: int = 1000):
        """Profile piece move generation"""
        print(f"Profiling piece move generation for {num_pieces} pieces...")
        
        def run_piece_moves():
            game = qec_main.Game(seed=42)
            for piece in game.board.pieces:
                if piece.alive:
                    for _ in range(num_pieces // len(game.board.pieces)):
                        moves = game.board._gen_piece_moves(piece, attacks_only=False)
                        if not moves:
                            break
        
        profiler = cProfile.Profile()
        profiler.enable()
        start_time = time.time()
        run_piece_moves()
        end_time = time.time()
        profiler.disable()
        
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        
        print(f"Piece moves profiling completed in {end_time - start_time:.2f}s")
        print("Top 10 functions by cumulative time:")
        stats.print_stats(10)
        
        self.results['piece_moves'] = {
            'time': end_time - start_time,
            'pieces': num_pieces
        }
    
    def profile_evaluation(self, num_evaluations: int = 1000):
        """Profile position evaluation"""
        print(f"Profiling position evaluation for {num_evaluations} positions...")
        
        def run_evaluations():
            game = qec_main.Game(seed=42)
            for _ in range(num_evaluations):
                eval_score = game._evaluate('W')
                eval_score = game._evaluate('B')
        
        profiler = cProfile.Profile()
        profiler.enable()
        start_time = time.time()
        run_evaluations()
        end_time = time.time()
        profiler.disable()
        
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        
        print(f"Evaluation profiling completed in {end_time - start_time:.2f}s")
        print("Top 10 functions by cumulative time:")
        stats.print_stats(10)
        
        self.results['evaluation'] = {
            'time': end_time - start_time,
            'evaluations': num_evaluations
        }
    
    def profile_entanglement_operations(self, num_operations: int = 1000):
        """Profile entanglement operations"""
        print(f"Profiling entanglement operations for {num_operations} operations...")
        
        def run_entanglement_ops():
            game = qec_main.Game(seed=42)
            for _ in range(num_operations):
                # Test entanglement hash
                hash_val = game.get_entanglement_hash()
                # Test counterpart lookup
                for pawn_id in list(game.ent.W_pawn_to_black.keys())[:5]:
                    counterpart = game.ent.linked_counterpart_id(pawn_id)
                # Test entanglement map
                ent_map = game.get_full_entanglement_map()
        
        profiler = cProfile.Profile()
        profiler.enable()
        start_time = time.time()
        run_entanglement_ops()
        end_time = time.time()
        profiler.disable()
        
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        
        print(f"Entanglement operations profiling completed in {end_time - start_time:.2f}s")
        print("Top 10 functions by cumulative time:")
        stats.print_stats(10)
        
        self.results['entanglement'] = {
            'time': end_time - start_time,
            'operations': num_operations
        }
    
    def profile_full_game(self, num_games: int = 5):
        """Profile complete game execution"""
        print(f"Profiling full game execution for {num_games} games...")
        
        def run_full_games():
            for i in range(num_games):
                game = qec_main.Game(seed=42 + i)
                result = game.run(max_plies=100)  # Limit to 100 moves for profiling
        
        profiler = cProfile.Profile()
        profiler.enable()
        start_time = time.time()
        run_full_games()
        end_time = time.time()
        profiler.disable()
        
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        
        print(f"Full game profiling completed in {end_time - start_time:.2f}s")
        print("Top 15 functions by cumulative time:")
        stats.print_stats(15)
        
        self.results['full_game'] = {
            'time': end_time - start_time,
            'games': num_games
        }
    
    def run_all_profiles(self):
        """Run all performance profiles"""
        print("=== QEC Performance Profiling ===")
        
        # Profile individual components
        self.profile_legal_moves(5)
        print("\n" + "="*50 + "\n")
        
        self.profile_piece_moves(500)
        print("\n" + "="*50 + "\n")
        
        self.profile_evaluation(500)
        print("\n" + "="*50 + "\n")
        
        self.profile_entanglement_operations(500)
        print("\n" + "="*50 + "\n")
        
        self.profile_full_game(3)
        print("\n" + "="*50 + "\n")
        
        # Print summary
        print("=== Performance Summary ===")
        for component, data in self.results.items():
            print(f"{component}: {data['time']:.3f}s")
        
        # Identify bottlenecks
        print("\n=== Optimization Recommendations ===")
        if 'legal_moves' in self.results and self.results['legal_moves']['time'] > 1.0:
            print("⚠️  Legal move generation is slow - consider caching or optimization")
        
        if 'piece_moves' in self.results and self.results['piece_moves']['time'] > 0.5:
            print("⚠️  Piece move generation is slow - consider precomputing rays for sliders")
        
        if 'evaluation' in self.results and self.results['evaluation']['time'] > 0.5:
            print("⚠️  Position evaluation is slow - consider caching or simplification")
        
        if 'entanglement' in self.results and self.results['entanglement']['time'] > 0.2:
            print("⚠️  Entanglement operations are slow - consider optimization")
        
        print("✅ Performance profiling completed!")

def main():
    """Main profiling function"""
    profiler = QECPerformanceProfiler()
    profiler.run_all_profiles()

if __name__ == "__main__":
    main()
