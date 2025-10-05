"""
QEC (Quantum Entanglement Chess) Core Package
"""

__version__ = "0.1.0"
__author__ = "QEC Research Team"
__email__ = "research@qec.dev"

# Core game components
from .main import Game, Board, Piece, Square, Color

# Performance optimizations
from .move_generation_cache import get_move_cache, get_slider_rays, get_cache_stats, clear_cache
from .fast_evaluation import get_fast_evaluator, evaluate_fast, get_evaluation_stats, reset_evaluation_stats
from .performance_optimizations import get_performance_cache, clear_performance_cache, get_cache_stats as get_perf_cache_stats

# Schema and validation
from .result_schema import QECResultSchemaV1, QECResultValidator, create_result_v1, validate_result_file

# Public API
def simulate_match(white_policy: str = "minimax", black_policy: str = "minimax", 
                  seed: int = 42, max_plies: int = 200) -> dict:
    """
    Simulate a single QEC match between two players.
    
    Args:
        white_policy: AI policy for white player
        black_policy: AI policy for black player  
        seed: Random seed for reproducibility
        max_plies: Maximum number of plies before timeout
        
    Returns:
        Dictionary with game result and statistics
    """
    game = Game(seed=seed)
    result = game.run(max_plies=max_plies)
    
    return {
        'result': result,
        'total_plies': len(game.move_log),
        'forced_moves': sum(1 for log in game.move_log if 'FORCED' in log),
        'reactive_moves': sum(1 for log in game.move_log if 'REACT' in log),
        'captures': sum(1 for log in game.move_log if ' x ' in log),
        'final_fen': game.board.to_fen(),
        'seed': seed
    }

def run_sweep(num_archetypes: int = 10, num_entropy_configs: int = 5, 
             num_games_per_config: int = 3, seed_base: int = 42,
             output_file: str = "sweep_results.csv") -> str:
    """
    Run a parameter sweep experiment.
    
    Args:
        num_archetypes: Number of archetype vectors to test
        num_entropy_configs: Number of entropy configurations to test
        num_games_per_config: Games per configuration
        seed_base: Base seed for reproducibility
        output_file: Output CSV file path
        
    Returns:
        Path to output CSV file
    """
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'research'))
    
    from parameter_sweep_runner import QECParameterSweep
    
    runner = QECParameterSweep(output_file)
    runner.run_parameter_sweep(
        num_archetypes=num_archetypes,
        num_entropy_configs=num_entropy_configs, 
        num_games_per_config=num_games_per_config,
        seed_base=seed_base
    )
    runner.save_results()
    
    return output_file

# Version info
__all__ = [
    'Game', 'Board', 'Piece', 'Square', 'Color',
    'simulate_match', 'run_sweep',
    'get_move_cache', 'get_slider_rays', 'get_cache_stats', 'clear_cache',
    'get_fast_evaluator', 'evaluate_fast', 'get_evaluation_stats', 'reset_evaluation_stats',
    'get_performance_cache', 'clear_performance_cache', 'get_perf_cache_stats',
    'QECResultSchemaV1', 'QECResultValidator', 'create_result_v1', 'validate_result_file',
    '__version__', '__author__', '__email__'
]
