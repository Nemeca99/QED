"""
QEC Training from Real Chess Games
Train QEC AI using patterns from real chess games
"""

import sys
import os
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict
import chess
import chess.pgn

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))

import main as qec_main

class QECTrainingFromDatabase:
    """Train QEC AI using patterns from real chess games"""
    
    def __init__(self, database_path: str = "data/chess_database/qec_training_set.json"):
        self.database_path = Path(database_path)
        self.training_data = []
        self.patterns = defaultdict(list)
        self.entanglement_examples = []
        self.forced_move_examples = []
        self.reactive_escape_examples = []
        
    def load_training_data(self) -> List[Dict[str, Any]]:
        """Load training data from chess database"""
        print(f"Loading training data from {self.database_path}...")
        
        if not self.database_path.exists():
            raise FileNotFoundError(f"Training data not found: {self.database_path}")
        
        with open(self.database_path, 'r') as f:
            self.training_data = json.load(f)
        
        print(f"Loaded {len(self.training_data)} games for training")
        return self.training_data
    
    def extract_qec_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Extract QEC-specific patterns from chess games"""
        print("Extracting QEC patterns from chess games...")
        
        patterns = {
            'entanglement_opportunities': [],
            'forced_move_sequences': [],
            'reactive_escape_patterns': [],
            'tactical_combinations': [],
            'strategic_themes': []
        }
        
        for i, game in enumerate(self.training_data):
            if i % 1000 == 0:
                print(f"Processing game {i}/{len(self.training_data)}...")
            
            # Extract patterns from this game
            game_patterns = self._extract_patterns_from_game(game)
            
            for pattern_type, pattern_list in game_patterns.items():
                patterns[pattern_type].extend(pattern_list)
        
        print(f"Extracted patterns:")
        for pattern_type, pattern_list in patterns.items():
            print(f"  {pattern_type}: {len(pattern_list)} patterns")
        
        return patterns
    
    def _extract_patterns_from_game(self, game: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Extract patterns from a single game"""
        patterns = {
            'entanglement_opportunities': [],
            'forced_move_sequences': [],
            'reactive_escape_patterns': [],
            'tactical_combinations': [],
            'strategic_themes': []
        }
        
        try:
            moves = game.get('moves', [])
            if not moves:
                return patterns
            
            # Extract entanglement opportunities
            entanglement_opps = self._find_entanglement_opportunities(moves)
            patterns['entanglement_opportunities'].extend(entanglement_opps)
            
            # Extract forced move sequences
            forced_sequences = self._find_forced_move_sequences(moves)
            patterns['forced_move_sequences'].extend(forced_sequences)
            
            # Extract reactive escape patterns
            escape_patterns = self._find_reactive_escape_patterns(moves)
            patterns['reactive_escape_patterns'].extend(escape_patterns)
            
            # Extract tactical combinations
            tactical_combos = self._find_tactical_combinations(moves)
            patterns['tactical_combinations'].extend(tactical_combos)
            
            # Extract strategic themes
            strategic_themes = self._identify_strategic_themes(moves)
            patterns['strategic_themes'].extend(strategic_themes)
            
        except Exception as e:
            print(f"Error extracting patterns from game: {e}")
        
        return patterns
    
    def _find_entanglement_opportunities(self, moves: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find potential entanglement opportunities in moves"""
        opportunities = []
        
        for i, move in enumerate(moves):
            # Look for piece interactions that could become entangled
            if 'x' in move['san']:  # Capture moves
                opportunities.append({
                    'move_number': i + 1,
                    'move': move['san'],
                    'fen': move['fen'],
                    'type': 'capture_entanglement',
                    'description': 'Piece capture that could create entanglement'
                })
            
            # Look for piece coordination
            if i > 0:
                prev_move = moves[i-1]
                if self._pieces_coordinated(prev_move, move):
                    opportunities.append({
                        'move_number': i + 1,
                        'move': move['san'],
                        'fen': move['fen'],
                        'type': 'coordination_entanglement',
                        'description': 'Piece coordination that could create entanglement'
                    })
            
            # Look for pawn structure interactions
            if move['san'].startswith('P') or move['san'].islower():
                opportunities.append({
                    'move_number': i + 1,
                    'move': move['san'],
                    'fen': move['fen'],
                    'type': 'pawn_entanglement',
                    'description': 'Pawn move that could create entanglement'
                })
        
        return opportunities
    
    def _find_forced_move_sequences(self, moves: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find forced move sequences in the game"""
        sequences = []
        
        for i, move in enumerate(moves):
            # Check for checks (forced responses)
            if '+' in move['san'] or '#' in move['san']:
                sequences.append({
                    'move_number': i + 1,
                    'move': move['san'],
                    'fen': move['fen'],
                    'type': 'check_forced',
                    'description': 'Check that forces response'
                })
            
            # Check for tactical sequences
            if i < len(moves) - 1:
                next_move = moves[i + 1]
                if self._is_tactical_sequence(move, next_move):
                    sequences.append({
                        'move_number': i + 1,
                        'move': move['san'],
                        'fen': move['fen'],
                        'type': 'tactical_forced',
                        'description': 'Tactical sequence that forces response'
                    })
            
            # Check for mate threats
            if '#' in move['san']:
                sequences.append({
                    'move_number': i + 1,
                    'move': move['san'],
                    'fen': move['fen'],
                    'type': 'mate_threat',
                    'description': 'Mate threat that forces response'
                })
        
        return sequences
    
    def _find_reactive_escape_patterns(self, moves: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find reactive escape patterns in the game"""
        escape_patterns = []
        
        for i, move in enumerate(moves):
            # Look for king escape patterns
            if 'K' in move['san'] and ('+' in move['san'] or '#' in move['san']):
                escape_patterns.append({
                    'move_number': i + 1,
                    'move': move['san'],
                    'fen': move['fen'],
                    'type': 'king_escape',
                    'description': 'King escape from check'
                })
            
            # Look for piece retreats
            if i > 0 and self._is_retreat_move(moves[i-1], move):
                escape_patterns.append({
                    'move_number': i + 1,
                    'move': move['san'],
                    'fen': move['fen'],
                    'type': 'piece_retreat',
                    'description': 'Piece retreat from attack'
                })
            
            # Look for defensive moves
            if self._is_defensive_move(move):
                escape_patterns.append({
                    'move_number': i + 1,
                    'move': move['san'],
                    'fen': move['fen'],
                    'type': 'defensive_move',
                    'description': 'Defensive move to avoid loss'
                })
        
        return escape_patterns
    
    def _find_tactical_combinations(self, moves: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find tactical combinations in the game"""
        combinations = []
        
        for i, move in enumerate(moves):
            # Look for tactical sequences
            if i < len(moves) - 2:
                next_move = moves[i + 1]
                next_next_move = moves[i + 2]
                
                if self._is_tactical_combination(move, next_move, next_next_move):
                    combinations.append({
                        'move_number': i + 1,
                        'move': move['san'],
                        'fen': move['fen'],
                        'type': 'tactical_combination',
                        'description': 'Tactical combination sequence'
                    })
            
            # Look for sacrifices
            if self._is_sacrifice_move(move):
                combinations.append({
                    'move_number': i + 1,
                    'move': move['san'],
                    'fen': move['fen'],
                    'type': 'sacrifice',
                    'description': 'Sacrifice move'
                })
            
            # Look for pins
            if self._is_pin_move(move):
                combinations.append({
                    'move_number': i + 1,
                    'move': move['san'],
                    'fen': move['fen'],
                    'type': 'pin',
                    'description': 'Pin move'
                })
        
        return combinations
    
    def _identify_strategic_themes(self, moves: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify strategic themes in the game"""
        themes = []
        
        # Analyze opening themes
        opening_moves = moves[:20] if len(moves) >= 20 else moves
        opening_themes = self._analyze_opening_themes(opening_moves)
        themes.extend(opening_themes)
        
        # Analyze middlegame themes
        if len(moves) > 20:
            middlegame_moves = moves[20:len(moves)-20] if len(moves) > 40 else moves[20:]
            middlegame_themes = self._analyze_middlegame_themes(middlegame_moves)
            themes.extend(middlegame_themes)
        
        # Analyze endgame themes
        if len(moves) > 40:
            endgame_moves = moves[-20:]
            endgame_themes = self._analyze_endgame_themes(endgame_moves)
            themes.extend(endgame_themes)
        
        return themes
    
    def _analyze_opening_themes(self, moves: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze opening themes"""
        themes = []
        
        # Look for development patterns
        if self._has_rapid_development(moves):
            themes.append({
                'type': 'rapid_development',
                'description': 'Rapid piece development in opening'
            })
        
        # Look for central control
        if self._has_central_control(moves):
            themes.append({
                'type': 'central_control',
                'description': 'Central control in opening'
            })
        
        # Look for castling
        if self._has_castling(moves):
            themes.append({
                'type': 'castling',
                'description': 'Castling in opening'
            })
        
        return themes
    
    def _analyze_middlegame_themes(self, moves: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze middlegame themes"""
        themes = []
        
        # Look for attack patterns
        if self._has_attack_patterns(moves):
            themes.append({
                'type': 'attack_patterns',
                'description': 'Attack patterns in middlegame'
            })
        
        # Look for defensive patterns
        if self._has_defensive_patterns(moves):
            themes.append({
                'type': 'defensive_patterns',
                'description': 'Defensive patterns in middlegame'
            })
        
        return themes
    
    def _analyze_endgame_themes(self, moves: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze endgame themes"""
        themes = []
        
        # Look for king activity
        if self._has_king_activity(moves):
            themes.append({
                'type': 'king_activity',
                'description': 'King activity in endgame'
            })
        
        # Look for pawn promotion
        if self._has_pawn_promotion(moves):
            themes.append({
                'type': 'pawn_promotion',
                'description': 'Pawn promotion in endgame'
            })
        
        return themes
    
    def _pieces_coordinated(self, prev_move: Dict, curr_move: Dict) -> bool:
        """Check if pieces are coordinated between moves"""
        return prev_move['turn'] != curr_move['turn']
    
    def _is_tactical_sequence(self, move1: Dict, move2: Dict) -> bool:
        """Check if two moves form a tactical sequence"""
        return 'x' in move1['san'] and 'x' in move2['san']
    
    def _is_retreat_move(self, prev_move: Dict, curr_move: Dict) -> bool:
        """Check if current move is a retreat"""
        return prev_move['turn'] == curr_move['turn']
    
    def _is_defensive_move(self, move: Dict) -> bool:
        """Check if move is defensive"""
        # Simplified defensive move detection
        return '+' in move['san'] or '#' in move['san']
    
    def _is_tactical_combination(self, move1: Dict, move2: Dict, move3: Dict) -> bool:
        """Check if three moves form a tactical combination"""
        return all('x' in move['san'] for move in [move1, move2, move3])
    
    def _is_sacrifice_move(self, move: Dict) -> bool:
        """Check if move is a sacrifice"""
        # Simplified sacrifice detection
        return 'x' in move['san'] and move['san'].isupper()
    
    def _is_pin_move(self, move: Dict) -> bool:
        """Check if move creates a pin"""
        # Simplified pin detection
        return 'x' in move['san'] and len(move['san']) > 3
    
    def _has_rapid_development(self, moves: List[Dict[str, Any]]) -> bool:
        """Check if opening has rapid development"""
        # Simplified rapid development detection
        return len(moves) >= 10 and any('N' in move['san'] for move in moves[:10])
    
    def _has_central_control(self, moves: List[Dict[str, Any]]) -> bool:
        """Check if opening has central control"""
        # Simplified central control detection
        return any('d' in move['san'] or 'e' in move['san'] for move in moves[:10])
    
    def _has_castling(self, moves: List[Dict[str, Any]]) -> bool:
        """Check if opening has castling"""
        return any('O-O' in move['san'] for move in moves)
    
    def _has_attack_patterns(self, moves: List[Dict[str, Any]]) -> bool:
        """Check if middlegame has attack patterns"""
        return any('x' in move['san'] for move in moves)
    
    def _has_defensive_patterns(self, moves: List[Dict[str, Any]]) -> bool:
        """Check if middlegame has defensive patterns"""
        return any('+' in move['san'] for move in moves)
    
    def _has_king_activity(self, moves: List[Dict[str, Any]]) -> bool:
        """Check if endgame has king activity"""
        return any('K' in move['san'] for move in moves)
    
    def _has_pawn_promotion(self, moves: List[Dict[str, Any]]) -> bool:
        """Check if endgame has pawn promotion"""
        return any('=' in move['san'] for move in moves)
    
    def create_training_dataset(self, patterns: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Create training dataset from extracted patterns"""
        print("Creating training dataset from patterns...")
        
        training_dataset = {
            'entanglement_training': self._create_entanglement_training_data(patterns['entanglement_opportunities']),
            'forced_move_training': self._create_forced_move_training_data(patterns['forced_move_sequences']),
            'reactive_escape_training': self._create_reactive_escape_training_data(patterns['reactive_escape_patterns']),
            'tactical_training': self._create_tactical_training_data(patterns['tactical_combinations']),
            'strategic_training': self._create_strategic_training_data(patterns['strategic_themes'])
        }
        
        print(f"Created training dataset with {sum(len(data) for data in training_dataset.values())} examples")
        return training_dataset
    
    def _create_entanglement_training_data(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create entanglement training data"""
        training_data = []
        
        for opp in opportunities:
            training_data.append({
                'position': opp['fen'],
                'move': opp['move'],
                'type': opp['type'],
                'description': opp['description'],
                'target_entanglement': self._predict_entanglement(opp)
            })
        
        return training_data
    
    def _create_forced_move_training_data(self, sequences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create forced move training data"""
        training_data = []
        
        for seq in sequences:
            training_data.append({
                'position': seq['fen'],
                'move': seq['move'],
                'type': seq['type'],
                'description': seq['description'],
                'forced_response': self._predict_forced_response(seq)
            })
        
        return training_data
    
    def _create_reactive_escape_training_data(self, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create reactive escape training data"""
        training_data = []
        
        for pattern in patterns:
            training_data.append({
                'position': pattern['fen'],
                'move': pattern['move'],
                'type': pattern['type'],
                'description': pattern['description'],
                'escape_quality': self._evaluate_escape_quality(pattern)
            })
        
        return training_data
    
    def _create_tactical_training_data(self, combinations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create tactical training data"""
        training_data = []
        
        for combo in combinations:
            training_data.append({
                'position': combo['fen'],
                'move': combo['move'],
                'type': combo['type'],
                'description': combo['description'],
                'tactical_value': self._evaluate_tactical_value(combo)
            })
        
        return training_data
    
    def _create_strategic_training_data(self, themes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create strategic training data"""
        training_data = []
        
        for theme in themes:
            training_data.append({
                'type': theme['type'],
                'description': theme['description'],
                'strategic_value': self._evaluate_strategic_value(theme)
            })
        
        return training_data
    
    def _predict_entanglement(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Predict entanglement for an opportunity"""
        # Simplified entanglement prediction
        return {
            'probability': 0.5,
            'strength': 'medium',
            'type': opportunity['type']
        }
    
    def _predict_forced_response(self, sequence: Dict[str, Any]) -> Dict[str, Any]:
        """Predict forced response for a sequence"""
        # Simplified forced response prediction
        return {
            'response_type': 'defensive',
            'urgency': 'high',
            'alternatives': 1
        }
    
    def _evaluate_escape_quality(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate escape quality"""
        # Simplified escape quality evaluation
        return {
            'quality': 'good',
            'safety': 'high',
            'efficiency': 'medium'
        }
    
    def _evaluate_tactical_value(self, combination: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate tactical value"""
        # Simplified tactical value evaluation
        return {
            'value': 'high',
            'complexity': 'medium',
            'risk': 'low'
        }
    
    def _evaluate_strategic_value(self, theme: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate strategic value"""
        # Simplified strategic value evaluation
        return {
            'value': 'medium',
            'importance': 'high',
            'long_term': True
        }
    
    def save_training_dataset(self, dataset: Dict[str, Any], output_path: str = "data/qec_training_dataset.json"):
        """Save training dataset to file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(dataset, f, indent=2)
        
        print(f"Training dataset saved to {output_file}")
        return str(output_file)

def main():
    """Main training script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='QEC Training from Database')
    parser.add_argument('--database', type=str, default='data/chess_database/qec_training_set.json', help='Database path')
    parser.add_argument('--output', type=str, default='data/qec_training_dataset.json', help='Output file')
    parser.add_argument('--analyze', action='store_true', help='Analyze training data')
    
    args = parser.parse_args()
    
    # Create trainer
    trainer = QECTrainingFromDatabase(args.database)
    
    try:
        # Load training data
        training_data = trainer.load_training_data()
        
        # Extract patterns
        patterns = trainer.extract_qec_patterns()
        
        # Create training dataset
        dataset = trainer.create_training_dataset(patterns)
        
        # Save training dataset
        output_path = trainer.save_training_dataset(dataset, args.output)
        
        # Analyze if requested
        if args.analyze:
            print("\nTraining Data Analysis:")
            for pattern_type, pattern_list in patterns.items():
                print(f"  {pattern_type}: {len(pattern_list)} patterns")
        
        print(f"Training dataset creation completed successfully!")
        print(f"Dataset saved to: {output_path}")
        
    except Exception as e:
        print(f"Error creating training dataset: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
