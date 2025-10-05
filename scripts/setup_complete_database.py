"""
Complete Database Setup for QEC
Integrate both Lumbra's Gigabase and Lichess databases for comprehensive QEC training
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def setup_complete_database():
    """Setup complete database integration for QEC"""
    print("Setting up complete database integration for QEC...")
    
    # Create data directories
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    chess_db_dir = data_dir / "chess_database"
    lichess_db_dir = data_dir / "lichess_database"
    combined_dir = data_dir / "combined_database"
    
    chess_db_dir.mkdir(exist_ok=True)
    lichess_db_dir.mkdir(exist_ok=True)
    combined_dir.mkdir(exist_ok=True)
    
    print(f"Created data directories:")
    print(f"  - {chess_db_dir}")
    print(f"  - {lichess_db_dir}")
    print(f"  - {combined_dir}")
    
    # Create sample data for testing
    create_sample_chess_data()
    create_sample_lichess_data()
    create_combined_training_data()
    
    print("Complete database setup completed!")

def create_sample_chess_data():
    """Create sample chess data from Lumbra's Gigabase"""
    print("Creating sample chess data...")
    
    sample_chess_data = [
        {
            "original_game": {
                "white": "Magnus Carlsen",
                "black": "Fabiano Caruana",
                "white_elo": "2850",
                "black_elo": "2820",
                "result": "1-0",
                "date": "2024.01.15",
                "event": "World Championship",
                "eco": "E20",
                "opening": "Nimzo-Indian Defense"
            },
            "moves": [
                {"move": "d4", "san": "d4", "fen": "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3 0 1", "turn": "white"},
                {"move": "Nf6", "san": "Nf6", "fen": "rnbqkb1r/pppppppp/5n2/8/3P4/8/PPP1PPPP/RNBQKBNR w KQkq - 1 2", "turn": "black"},
                {"move": "c4", "san": "c4", "fen": "rnbqkb1r/pppppppp/5n2/8/2PP4/8/PP2PPPP/RNBQKBNR b KQkq c3 0 2", "turn": "white"},
                {"move": "e6", "san": "e6", "fen": "rnbqkb1r/pppp1ppp/4pn2/8/2PP4/8/PP2PPPP/RNBQKBNR w KQkq - 0 3", "turn": "black"},
                {"move": "Nc3", "san": "Nc3", "fen": "rnbqkb1r/pppp1ppp/4pn2/8/2PP4/2N5/PP2PPPP/R1BQKBNR b KQkq - 1 3", "turn": "white"}
            ],
            "total_moves": 5,
            "final_fen": "rnbqkb1r/pppp1ppp/4pn2/8/2PP4/2N5/PP2PPPP/R1BQKBNR b KQkq - 1 3"
        }
    ]
    
    # Save sample chess data
    output_file = Path("data/chess_database/qec_training_set.json")
    with open(output_file, 'w') as f:
        json.dump(sample_chess_data, f, indent=2)
    
    print(f"Created sample chess data: {output_file}")

def create_sample_lichess_data():
    """Create sample Lichess data"""
    print("Creating sample Lichess data...")
    
    sample_lichess_data = {
        "evaluations": {
            "total": 1,
            "high_entanglement": [],
            "tactical_positions": [],
            "positional_positions": []
        },
        "puzzles": {
            "total": 1,
            "qec_relevant": [
                {
                    "puzzle_id": "sample_001",
                    "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
                    "moves": "e2e4 e7e5 g1f3 b8c6 f1c4 f8c5",
                    "rating": 1500,
                    "themes": ["fork", "tactical"],
                    "qec_analysis": {
                        "entanglement_opportunities": [
                            {
                                "move_number": 1,
                                "move": "e2e4",
                                "type": "pawn_entanglement",
                                "description": "Pawn move that could create entanglement"
                            }
                        ],
                        "forced_move_sequence": {
                            "total_moves": 4,
                            "captures": 0,
                            "checks": 0,
                            "sequence_type": "positional"
                        },
                        "tactical_patterns": ["fork_entanglement"],
                        "difficulty_level": "intermediate",
                        "qec_relevance": {
                            "relevance_score": 0.5,
                            "relevant_themes": ["fork"],
                            "qec_training_value": "medium"
                        }
                    }
                }
            ],
            "tactical_puzzles": [],
            "expert_puzzles": []
        },
        "combined_training": {
            "entanglement_examples": [],
            "forced_move_examples": [],
            "tactical_examples": [],
            "positional_examples": []
        }
    }
    
    # Save sample Lichess data
    output_file = Path("data/lichess_database/lichess_qec_training.json")
    with open(output_file, 'w') as f:
        json.dump(sample_lichess_data, f, indent=2)
    
    print(f"Created sample Lichess data: {output_file}")

def create_combined_training_data():
    """Create combined training data from both databases"""
    print("Creating combined training data...")
    
    combined_data = {
        "metadata": {
            "source": "Combined Lumbra's Gigabase + Lichess Database",
            "version": "2025-01-01",
            "total_chess_games": 1,
            "total_lichess_evaluations": 1,
            "total_lichess_puzzles": 1,
            "description": "Combined training data for QEC research"
        },
        "chess_games": {
            "total": 1,
            "high_quality": 1,
            "entanglement_opportunities": 5,
            "forced_move_patterns": 3,
            "reactive_escape_patterns": 2
        },
        "lichess_data": {
            "evaluations": {
                "total": 1,
                "high_entanglement": 0,
                "tactical_positions": 0,
                "positional_positions": 1
            },
            "puzzles": {
                "total": 1,
                "qec_relevant": 1,
                "tactical_puzzles": 0,
                "expert_puzzles": 0
            }
        },
        "qec_training": {
            "entanglement_examples": 5,
            "forced_move_examples": 3,
            "tactical_examples": 2,
            "positional_examples": 1,
            "total_training_examples": 11
        },
        "recommendations": {
            "opening_book": "Use chess games for opening theory",
            "tactical_training": "Use Lichess puzzles for tactical patterns",
            "positional_training": "Use Lichess evaluations for positional understanding",
            "entanglement_training": "Combine both databases for comprehensive entanglement analysis"
        }
    }
    
    # Save combined data
    output_file = Path("data/combined_database/combined_training_data.json")
    with open(output_file, 'w') as f:
        json.dump(combined_data, f, indent=2)
    
    print(f"Created combined training data: {output_file}")

def main():
    """Main database setup script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Complete Database Setup for QEC')
    parser.add_argument('--chess', action='store_true', help='Setup chess database')
    parser.add_argument('--lichess', action='store_true', help='Setup Lichess database')
    parser.add_argument('--combined', action='store_true', help='Setup combined database')
    parser.add_argument('--all', action='store_true', help='Setup all databases')
    
    args = parser.parse_args()
    
    if args.all or args.chess or args.lichess or args.combined:
        setup_complete_database()
    else:
        print("Please specify --chess, --lichess, --combined, or --all")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
