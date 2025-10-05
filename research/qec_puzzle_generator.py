"""
QEC Puzzle Generator from Lichess Database
Generate QEC-specific puzzles from Lichess puzzle database
"""

import sys
import os
import json
import chess
import chess.pgn
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import random

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))

import main as qec_main

@dataclass
class QECPuzzle:
    """QEC puzzle structure"""
    puzzle_id: str
    fen: str
    solution: List[str]
    difficulty: str
    themes: List[str]
    entanglement_opportunities: List[Dict[str, Any]]
    forced_moves: List[Dict[str, Any]]
    reactive_escapes: List[Dict[str, Any]]
    qec_complexity: str
    training_value: str

class QECPuzzleGenerator:
    """Generate QEC puzzles from Lichess database"""
    
    def __init__(self, lichess_data_path: str = "data/lichess_qec_training.json"):
        self.data_path = Path(lichess_data_path)
        self.puzzles = []
        self.generated_puzzles = []
        
    def load_lichess_data(self) -> Dict[str, Any]:
        """Load Lichess training data"""
        print(f"Loading Lichess data from {self.data_path}...")
        
        if not self.data_path.exists():
            raise FileNotFoundError(f"Lichess data not found: {self.data_path}")
        
        with open(self.data_path, 'r') as f:
            data = json.load(f)
        
        print(f"Loaded Lichess data with {data['evaluations']['total']} evaluations and {data['puzzles']['total']} puzzles")
        return data
    
    def generate_qec_puzzles(self, num_puzzles: int = 1000) -> List[QECPuzzle]:
        """Generate QEC puzzles from Lichess data"""
        print(f"Generating {num_puzzles} QEC puzzles...")
        
        data = self.load_lichess_data()
        
        # Extract puzzle data
        lichess_puzzles = data.get('puzzles', {}).get('qec_relevant', [])
        if not lichess_puzzles:
            lichess_puzzles = data.get('puzzles', {}).get('total', [])
        
        # Generate QEC puzzles
        for i in range(min(num_puzzles, len(lichess_puzzles))):
            if i % 100 == 0:
                print(f"Generated {i} QEC puzzles...")
            
            lichess_puzzle = lichess_puzzles[i]
            qec_puzzle = self._convert_to_qec_puzzle(lichess_puzzle, i)
            if qec_puzzle:
                self.generated_puzzles.append(qec_puzzle)
        
        print(f"Successfully generated {len(self.generated_puzzles)} QEC puzzles")
        return self.generated_puzzles
    
    def _convert_to_qec_puzzle(self, lichess_puzzle: Dict[str, Any], puzzle_num: int) -> Optional[QECPuzzle]:
        """Convert Lichess puzzle to QEC puzzle"""
        try:
            fen = lichess_puzzle.get('fen', '')
            if not fen:
                return None
            
            # Parse puzzle data
            puzzle_id = f"qec_{puzzle_num:06d}"
            moves = lichess_puzzle.get('moves', '')
            rating = lichess_puzzle.get('rating', 1500)
            themes = lichess_puzzle.get('themes', [])
            
            # Convert moves to solution
            solution = moves.split() if moves else []
            
            # Analyze QEC aspects
            entanglement_opps = self._analyze_entanglement_opportunities(fen, solution)
            forced_moves = self._analyze_forced_moves(fen, solution)
            reactive_escapes = self._analyze_reactive_escapes(fen, solution)
            
            # Determine QEC complexity
            qec_complexity = self._assess_qec_complexity(entanglement_opps, forced_moves, reactive_escapes)
            
            # Determine training value
            training_value = self._assess_training_value(entanglement_opps, forced_moves, themes)
            
            # Determine difficulty
            difficulty = self._assess_difficulty(rating, qec_complexity)
            
            return QECPuzzle(
                puzzle_id=puzzle_id,
                fen=fen,
                solution=solution,
                difficulty=difficulty,
                themes=themes,
                entanglement_opportunities=entanglement_opps,
                forced_moves=forced_moves,
                reactive_escapes=reactive_escapes,
                qec_complexity=qec_complexity,
                training_value=training_value
            )
            
        except Exception as e:
            print(f"Error converting puzzle {puzzle_num}: {e}")
            return None
    
    def _analyze_entanglement_opportunities(self, fen: str, solution: List[str]) -> List[Dict[str, Any]]:
        """Analyze entanglement opportunities in puzzle"""
        opportunities = []
        
        try:
            board = chess.Board(fen)
            
            # Look for piece interactions that could become entangled
            for i, move in enumerate(solution):
                if 'x' in move:  # Capture move
                    opportunities.append({
                        'move_number': i + 1,
                        'move': move,
                        'type': 'capture_entanglement',
                        'description': 'Capture move that could create entanglement'
                    })
                
                if '+' in move:  # Check move
                    opportunities.append({
                        'move_number': i + 1,
                        'move': move,
                        'type': 'check_entanglement',
                        'description': 'Check move that could create entanglement'
                    })
                
                # Look for piece coordination
                if i > 0:
                    prev_move = solution[i-1]
                    if self._pieces_coordinated(prev_move, move):
                        opportunities.append({
                            'move_number': i + 1,
                            'move': move,
                            'type': 'coordination_entanglement',
                            'description': 'Piece coordination that could create entanglement'
                        })
        
        except Exception as e:
            print(f"Error analyzing entanglement opportunities: {e}")
        
        return opportunities
    
    def _analyze_forced_moves(self, fen: str, solution: List[str]) -> List[Dict[str, Any]]:
        """Analyze forced moves in puzzle"""
        forced_moves = []
        
        try:
            board = chess.Board(fen)
            
            for i, move in enumerate(solution):
                # Check for checks (forced responses)
                if '+' in move or '#' in move:
                    forced_moves.append({
                        'move_number': i + 1,
                        'move': move,
                        'type': 'check_forced',
                        'description': 'Check that forces response'
                    })
                
                # Check for tactical sequences
                if i < len(solution) - 1:
                    next_move = solution[i + 1]
                    if self._is_tactical_sequence(move, next_move):
                        forced_moves.append({
                            'move_number': i + 1,
                            'move': move,
                            'type': 'tactical_forced',
                            'description': 'Tactical sequence that forces response'
                        })
                
                # Check for mate threats
                if '#' in move:
                    forced_moves.append({
                        'move_number': i + 1,
                        'move': move,
                        'type': 'mate_threat',
                        'description': 'Mate threat that forces response'
                    })
        
        except Exception as e:
            print(f"Error analyzing forced moves: {e}")
        
        return forced_moves
    
    def _analyze_reactive_escapes(self, fen: str, solution: List[str]) -> List[Dict[str, Any]]:
        """Analyze reactive escape patterns in puzzle"""
        escape_patterns = []
        
        try:
            board = chess.Board(fen)
            
            for i, move in enumerate(solution):
                # Look for king escape patterns
                if 'K' in move and ('+' in move or '#' in move):
                    escape_patterns.append({
                        'move_number': i + 1,
                        'move': move,
                        'type': 'king_escape',
                        'description': 'King escape from check'
                    })
                
                # Look for piece retreats
                if i > 0 and self._is_retreat_move(solution[i-1], move):
                    escape_patterns.append({
                        'move_number': i + 1,
                        'move': move,
                        'type': 'piece_retreat',
                        'description': 'Piece retreat from attack'
                    })
                
                # Look for defensive moves
                if self._is_defensive_move(move):
                    escape_patterns.append({
                        'move_number': i + 1,
                        'move': move,
                        'type': 'defensive_move',
                        'description': 'Defensive move to avoid loss'
                    })
        
        except Exception as e:
            print(f"Error analyzing reactive escapes: {e}")
        
        return escape_patterns
    
    def _pieces_coordinated(self, prev_move: str, curr_move: str) -> bool:
        """Check if pieces are coordinated between moves"""
        # Simplified coordination check
        return prev_move != curr_move
    
    def _is_tactical_sequence(self, move1: str, move2: str) -> bool:
        """Check if two moves form a tactical sequence"""
        return 'x' in move1 and 'x' in move2
    
    def _is_retreat_move(self, prev_move: str, curr_move: str) -> bool:
        """Check if current move is a retreat"""
        # Simplified retreat detection
        return prev_move != curr_move
    
    def _is_defensive_move(self, move: str) -> bool:
        """Check if move is defensive"""
        return '+' in move or '#' in move
    
    def _assess_qec_complexity(self, entanglement_opps: List[Dict], forced_moves: List[Dict], reactive_escapes: List[Dict]) -> str:
        """Assess QEC complexity of puzzle"""
        total_complexity = len(entanglement_opps) + len(forced_moves) + len(reactive_escapes)
        
        if total_complexity >= 6:
            return 'expert'
        elif total_complexity >= 4:
            return 'advanced'
        elif total_complexity >= 2:
            return 'intermediate'
        else:
            return 'beginner'
    
    def _assess_training_value(self, entanglement_opps: List[Dict], forced_moves: List[Dict], themes: List[str]) -> str:
        """Assess training value for QEC"""
        qec_relevant_themes = ['fork', 'pin', 'skewer', 'discoveredAttack', 'sacrifice', 'mate']
        relevant_themes = sum(1 for theme in themes if theme in qec_relevant_themes)
        
        total_qec_elements = len(entanglement_opps) + len(forced_moves) + relevant_themes
        
        if total_qec_elements >= 5:
            return 'high'
        elif total_qec_elements >= 3:
            return 'medium'
        else:
            return 'low'
    
    def _assess_difficulty(self, rating: int, qec_complexity: str) -> str:
        """Assess overall difficulty"""
        if rating >= 2000 and qec_complexity == 'expert':
            return 'expert'
        elif rating >= 1500 and qec_complexity in ['advanced', 'expert']:
            return 'advanced'
        elif rating >= 1000 and qec_complexity in ['intermediate', 'advanced']:
            return 'intermediate'
        else:
            return 'beginner'
    
    def create_puzzle_categories(self) -> Dict[str, List[QECPuzzle]]:
        """Create puzzle categories for training"""
        categories = {
            'entanglement_puzzles': [],
            'forced_move_puzzles': [],
            'reactive_escape_puzzles': [],
            'tactical_puzzles': [],
            'positional_puzzles': []
        }
        
        for puzzle in self.generated_puzzles:
            # Categorize by primary QEC aspect
            if len(puzzle.entanglement_opportunities) > len(puzzle.forced_moves) and len(puzzle.entanglement_opportunities) > len(puzzle.reactive_escapes):
                categories['entanglement_puzzles'].append(puzzle)
            elif len(puzzle.forced_moves) > len(puzzle.entanglement_opportunities) and len(puzzle.forced_moves) > len(puzzle.reactive_escapes):
                categories['forced_move_puzzles'].append(puzzle)
            elif len(puzzle.reactive_escapes) > len(puzzle.entanglement_opportunities) and len(puzzle.reactive_escapes) > len(puzzle.forced_moves):
                categories['reactive_escape_puzzles'].append(puzzle)
            elif 'tactical' in puzzle.themes or 'sacrifice' in puzzle.themes:
                categories['tactical_puzzles'].append(puzzle)
            else:
                categories['positional_puzzles'].append(puzzle)
        
        return categories
    
    def generate_training_curriculum(self) -> Dict[str, Any]:
        """Generate training curriculum from puzzles"""
        categories = self.create_puzzle_categories()
        
        curriculum = {
            'beginner': {
                'entanglement': [p for p in categories['entanglement_puzzles'] if p.difficulty == 'beginner'][:50],
                'forced_moves': [p for p in categories['forced_move_puzzles'] if p.difficulty == 'beginner'][:50],
                'reactive_escapes': [p for p in categories['reactive_escape_puzzles'] if p.difficulty == 'beginner'][:50]
            },
            'intermediate': {
                'entanglement': [p for p in categories['entanglement_puzzles'] if p.difficulty == 'intermediate'][:100],
                'forced_moves': [p for p in categories['forced_move_puzzles'] if p.difficulty == 'intermediate'][:100],
                'reactive_escapes': [p for p in categories['reactive_escape_puzzles'] if p.difficulty == 'intermediate'][:100]
            },
            'advanced': {
                'entanglement': [p for p in categories['entanglement_puzzles'] if p.difficulty == 'advanced'][:150],
                'forced_moves': [p for p in categories['forced_move_puzzles'] if p.difficulty == 'advanced'][:150],
                'reactive_escapes': [p for p in categories['reactive_escape_puzzles'] if p.difficulty == 'advanced'][:150]
            },
            'expert': {
                'entanglement': [p for p in categories['entanglement_puzzles'] if p.difficulty == 'expert'][:200],
                'forced_moves': [p for p in categories['forced_move_puzzles'] if p.difficulty == 'expert'][:200],
                'reactive_escapes': [p for p in categories['reactive_escape_puzzles'] if p.difficulty == 'expert'][:200]
            }
        }
        
        return curriculum
    
    def save_puzzles(self, output_path: str = "data/qec_puzzles.json"):
        """Save QEC puzzles to file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert puzzles to serializable format
        puzzles_data = []
        for puzzle in self.generated_puzzles:
            puzzles_data.append({
                'puzzle_id': puzzle.puzzle_id,
                'fen': puzzle.fen,
                'solution': puzzle.solution,
                'difficulty': puzzle.difficulty,
                'themes': puzzle.themes,
                'entanglement_opportunities': puzzle.entanglement_opportunities,
                'forced_moves': puzzle.forced_moves,
                'reactive_escapes': puzzle.reactive_escapes,
                'qec_complexity': puzzle.qec_complexity,
                'training_value': puzzle.training_value
            })
        
        with open(output_file, 'w') as f:
            json.dump(puzzles_data, f, indent=2)
        
        print(f"QEC puzzles saved to {output_file}")
        return str(output_file)
    
    def save_training_curriculum(self, curriculum: Dict[str, Any], output_path: str = "data/qec_training_curriculum.json"):
        """Save training curriculum to file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert curriculum to serializable format
        curriculum_data = {}
        for level, categories in curriculum.items():
            curriculum_data[level] = {}
            for category, puzzles in categories.items():
                curriculum_data[level][category] = [
                    {
                        'puzzle_id': p.puzzle_id,
                        'fen': p.fen,
                        'solution': p.solution,
                        'difficulty': p.difficulty,
                        'themes': p.themes,
                        'entanglement_opportunities': p.entanglement_opportunities,
                        'forced_moves': p.forced_moves,
                        'reactive_escapes': p.reactive_escapes,
                        'qec_complexity': p.qec_complexity,
                        'training_value': p.training_value
                    }
                    for p in puzzles
                ]
        
        with open(output_file, 'w') as f:
            json.dump(curriculum_data, f, indent=2)
        
        print(f"Training curriculum saved to {output_file}")
        return str(output_file)

def main():
    """Main QEC puzzle generator"""
    import argparse
    
    parser = argparse.ArgumentParser(description='QEC Puzzle Generator from Lichess Database')
    parser.add_argument('--lichess-data', type=str, default='data/lichess_qec_training.json', help='Lichess data file')
    parser.add_argument('--num-puzzles', type=int, default=1000, help='Number of puzzles to generate')
    parser.add_argument('--output-puzzles', type=str, default='data/qec_puzzles.json', help='Puzzles output file')
    parser.add_argument('--output-curriculum', type=str, default='data/qec_training_curriculum.json', help='Curriculum output file')
    parser.add_argument('--generate-curriculum', action='store_true', help='Generate training curriculum')
    
    args = parser.parse_args()
    
    # Create puzzle generator
    generator = QECPuzzleGenerator(args.lichess_data)
    
    try:
        # Generate QEC puzzles
        puzzles = generator.generate_qec_puzzles(args.num_puzzles)
        
        # Save puzzles
        puzzles_path = generator.save_puzzles(args.output_puzzles)
        
        # Generate curriculum if requested
        if args.generate_curriculum:
            curriculum = generator.generate_training_curriculum()
            curriculum_path = generator.save_training_curriculum(curriculum, args.output_curriculum)
            print(f"Training curriculum saved to {curriculum_path}")
        
        print(f"QEC puzzle generation completed successfully!")
        print(f"Generated {len(puzzles)} puzzles")
        print(f"Puzzles saved to {puzzles_path}")
        
    except Exception as e:
        print(f"Error generating QEC puzzles: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
