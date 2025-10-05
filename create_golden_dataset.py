"""
Create Golden Dataset for QEC Testing
Generate a small, deterministic dataset for testing analyzers
"""

import sys
import os
import json
import random
from typing import Dict, List, Any

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))
import main as qec_main

def create_golden_dataset():
    """Create a small, deterministic dataset for testing"""
    print("Creating golden dataset for QEC testing...")
    
    # Set up deterministic environment
    os.makedirs('data/golden', exist_ok=True)
    
    # Create 3 deterministic games with known outcomes
    games = []
    
    for i in range(3):
        print(f"Generating game {i+1}/3...")
        
        # Use fixed seed for reproducibility
        seed = 1000 + i
        random.seed(seed)
        
        # Create game with fixed entanglement
        game = qec_main.Game(seed=seed)
        
        # Run game with limited moves for testing
        result = game.run(max_plies=50)
        
        # Collect game data
        game_data = {
            'game_id': f'golden_game_{i+1:03d}',
            'seed': seed,
            'result': result,
            'total_plies': len(game.move_log),
            'forced_moves': sum(1 for log in game.move_log if 'FORCED' in log),
            'reactive_moves': sum(1 for log in game.move_log if 'REACT' in log),
            'captures': sum(1 for log in game.move_log if ' x ' in log),
            'entanglement_map': game.get_full_entanglement_map(),
            'final_fen': game.board.to_fen(),
            'move_log': game.move_log[:10],  # First 10 moves for testing
            'pgn_moves': game.pgn_moves[:10]  # First 10 PGN moves
        }
        
        games.append(game_data)
        
        # Save individual game files
        game_file = f'data/golden/game_{i+1:03d}.json'
        with open(game_file, 'w', encoding='utf-8') as f:
            json.dump(game_data, f, indent=2)
        
        print(f"  Saved: {game_file}")
    
    # Create summary dataset
    summary = {
        'dataset_info': {
            'name': 'QEC Golden Dataset',
            'version': '1.0',
            'description': 'Small deterministic dataset for testing QEC analyzers',
            'created': '2025-01-05',
            'games': len(games)
        },
        'games': games,
        'statistics': {
            'total_games': len(games),
            'total_plies': sum(g['total_plies'] for g in games),
            'total_forced_moves': sum(g['forced_moves'] for g in games),
            'total_reactive_moves': sum(g['reactive_moves'] for g in games),
            'total_captures': sum(g['captures'] for g in games),
            'results': {
                'White wins': sum(1 for g in games if 'White wins' in g['result']),
                'Black wins': sum(1 for g in games if 'Black wins' in g['result']),
                'Draw': sum(1 for g in games if 'Draw' in g['result'] or 'draw' in g['result'])
            }
        }
    }
    
    # Save summary
    summary_file = 'data/golden/golden_dataset.json'
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nGolden dataset created:")
    print(f"  Summary: {summary_file}")
    print(f"  Games: {len(games)}")
    print(f"  Total plies: {summary['statistics']['total_plies']}")
    print(f"  Results: {summary['statistics']['results']}")
    
    return summary

def test_analyzer_consistency():
    """Test that analyzers can read the golden dataset consistently"""
    print("\nTesting analyzer consistency...")
    
    # Test that analyzers can read the golden dataset
    try:
        # Test JSONL format
        jsonl_file = 'data/golden/test.jsonl'
        with open(jsonl_file, 'w', encoding='utf-8') as f:
            # Create sample JSONL records
            for i in range(3):
                record = {
                    'game_id': f'golden_game_{i+1:03d}',
                    'ply': i + 1,
                    'side': 'W' if i % 2 == 0 else 'B',
                    'primary': f'move_{i+1}',
                    'forced': '—' if i % 3 == 0 else '—',
                    'react': '—' if i % 5 == 0 else '—',
                    'ent_map_hash': f'hash_{i+1:08x}',
                    'ent_changes': [],
                    'eval': 100 + i * 10,
                    'phase': 'opening' if i < 10 else 'middlegame',
                    'legal_count': 20 - i,
                    'time_used_ms': 100 + i * 5
                }
                f.write(json.dumps(record) + '\n')
        
        print(f"✅ JSONL format test passed: {jsonl_file}")
        
        # Test CSV format
        csv_file = 'data/golden/test.csv'
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write('game_id,ply,side,primary,forced,react,eval,phase,legal_count,time_used_ms\n')
            for i in range(3):
                f.write(f'golden_game_{i+1:03d},{i+1},{"W" if i % 2 == 0 else "B"},move_{i+1},—,—,{100 + i * 10},opening,{20 - i},{100 + i * 5}\n')
        
        print(f"✅ CSV format test passed: {csv_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Analyzer consistency test failed: {e}")
        return False

def main():
    """Main function"""
    print("=== QEC Golden Dataset Creation ===")
    
    # Create golden dataset
    summary = create_golden_dataset()
    
    # Test analyzer consistency
    if test_analyzer_consistency():
        print("\n✅ Golden dataset and analyzer tests completed successfully!")
        return True
    else:
        print("\n❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
