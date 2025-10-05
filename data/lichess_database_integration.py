"""
Lichess Database Integration for QEC
Download and integrate Lichess database with 302M evaluated positions and 5.4M puzzles
"""

import os
import sys
import requests
import json
import csv
import zstandard as zstd
from pathlib import Path
from typing import Dict, List, Any, Optional, Iterator
import chess
import chess.pgn
from datetime import datetime
import io

class LichessDatabaseIntegrator:
    """Integrate Lichess database with QEC system"""
    
    def __init__(self, data_dir: str = "data/lichess_database"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = "https://database.lichess.org"
        self.evaluations_processed = 0
        self.puzzles_processed = 0
        
    def download_evaluations(self) -> str:
        """Download Lichess evaluations database (302M positions)"""
        print("Downloading Lichess evaluations database (302M positions)...")
        
        url = f"{self.base_url}/lichess_db_eval.jsonl.zst"
        output_file = self.data_dir / "lichess_db_eval.jsonl.zst"
        
        # Download with streaming
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Downloaded evaluations to {output_file}")
        return str(output_file)
    
    def download_puzzles(self) -> str:
        """Download Lichess puzzles database (5.4M puzzles)"""
        print("Downloading Lichess puzzles database (5.4M puzzles)...")
        
        url = f"{self.base_url}/lichess_db_puzzle.csv.zst"
        output_file = self.data_dir / "lichess_db_puzzle.csv.zst"
        
        # Download with streaming
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Downloaded puzzles to {output_file}")
        return str(output_file)
    
    def process_evaluations(self, eval_file: str, max_evaluations: int = 100000) -> List[Dict[str, Any]]:
        """Process Lichess evaluations for QEC training"""
        print(f"Processing Lichess evaluations (max: {max_evaluations})...")
        
        evaluations = []
        
        with open(eval_file, 'rb') as f:
            dctx = zstd.ZstdDecompressor()
            with dctx.stream_reader(f) as reader:
                for line_num, line in enumerate(reader):
                    if line_num >= max_evaluations:
                        break
                    
                    try:
                        line_str = line.decode('utf-8').strip()
                        if not line_str:
                            continue
                        
                        eval_data = json.loads(line_str)
                        qec_eval = self._convert_evaluation_to_qec(eval_data)
                        if qec_eval:
                            evaluations.append(qec_eval)
                            self.evaluations_processed += 1
                            
                            if self.evaluations_processed % 10000 == 0:
                                print(f"Processed {self.evaluations_processed} evaluations...")
                                
                    except Exception as e:
                        print(f"Error processing evaluation {line_num}: {e}")
                        continue
        
        print(f"Successfully processed {len(evaluations)} evaluations")
        return evaluations
    
    def _convert_evaluation_to_qec(self, eval_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Convert Lichess evaluation to QEC format"""
        try:
            fen = eval_data.get('fen', '')
            if not fen:
                return None
            
            # Parse FEN to board
            board = chess.Board(fen)
            
            # Extract best evaluation
            evals = eval_data.get('evals', [])
            if not evals:
                return None
            
            # Get evaluation with highest depth
            best_eval = max(evals, key=lambda x: x.get('depth', 0))
            pvs = best_eval.get('pvs', [])
            if not pvs:
                return None
            
            best_pv = pvs[0]
            
            # Convert to QEC format
            qec_eval = {
                'fen': fen,
                'evaluation': {
                    'cp': best_pv.get('cp', 0),
                    'mate': best_pv.get('mate'),
                    'line': best_pv.get('line', ''),
                    'depth': best_eval.get('depth', 0),
                    'knodes': best_eval.get('knodes', 0)
                },
                'qec_analysis': {
                    'entanglement_opportunities': self._find_entanglement_opportunities(board, best_pv),
                    'forced_move_potential': self._analyze_forced_move_potential(board, best_pv),
                    'tactical_complexity': self._analyze_tactical_complexity(board, best_pv),
                    'positional_themes': self._identify_positional_themes(board),
                    'material_balance': self._analyze_material_balance(board)
                }
            }
            
            return qec_eval
            
        except Exception as e:
            print(f"Error converting evaluation: {e}")
            return None
    
    def _find_entanglement_opportunities(self, board: chess.Board, pv: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find entanglement opportunities in position"""
        opportunities = []
        
        # Look for piece interactions that could become entangled
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is None:
                continue
            
            # Check for piece coordination opportunities
            if piece.piece_type == chess.PAWN:
                opportunities.append({
                    'type': 'pawn_entanglement',
                    'square': chess.square_name(square),
                    'piece': piece.symbol(),
                    'color': 'white' if piece.color else 'black'
                })
            
            elif piece.piece_type in [chess.ROOK, chess.BISHOP, chess.QUEEN]:
                opportunities.append({
                    'type': 'sliding_entanglement',
                    'square': chess.square_name(square),
                    'piece': piece.symbol(),
                    'color': 'white' if piece.color else 'black'
                })
        
        return opportunities
    
    def _analyze_forced_move_potential(self, board: chess.Board, pv: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze forced move potential in position"""
        # Check for checks
        is_check = board.is_check()
        
        # Check for tactical sequences
        line = pv.get('line', '')
        tactical_moves = line.count('x') if line else 0
        
        return {
            'is_check': is_check,
            'tactical_moves': tactical_moves,
            'forced_potential': 'high' if is_check or tactical_moves > 2 else 'medium' if tactical_moves > 0 else 'low'
        }
    
    def _analyze_tactical_complexity(self, board: chess.Board, pv: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze tactical complexity of position"""
        line = pv.get('line', '')
        captures = line.count('x') if line else 0
        checks = line.count('+') if line else 0
        
        return {
            'captures': captures,
            'checks': checks,
            'complexity': 'high' if captures > 3 or checks > 2 else 'medium' if captures > 1 or checks > 0 else 'low'
        }
    
    def _identify_positional_themes(self, board: chess.Board) -> List[str]:
        """Identify positional themes in position"""
        themes = []
        
        # Check for central control
        center_squares = [chess.E4, chess.E5, chess.D4, chess.D5]
        center_control = sum(1 for sq in center_squares if board.piece_at(sq) is not None)
        if center_control > 2:
            themes.append('central_control')
        
        # Check for piece development
        developed_pieces = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.piece_type in [chess.KNIGHT, chess.BISHOP]:
                if piece.color and square > 15:  # White pieces out of back rank
                    developed_pieces += 1
                elif not piece.color and square < 48:  # Black pieces out of back rank
                    developed_pieces += 1
        
        if developed_pieces > 4:
            themes.append('piece_development')
        
        # Check for king safety
        white_king_square = board.king(chess.WHITE)
        black_king_square = board.king(chess.BLACK)
        
        if white_king_square is not None and white_king_square > 15:
            themes.append('white_king_safety')
        if black_king_square is not None and black_king_square < 48:
            themes.append('black_king_safety')
        
        return themes
    
    def _analyze_material_balance(self, board: chess.Board) -> Dict[str, int]:
        """Analyze material balance in position"""
        piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9
        }
        
        white_material = 0
        black_material = 0
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                value = piece_values.get(piece.piece_type, 0)
                if piece.color:
                    white_material += value
                else:
                    black_material += value
        
        return {
            'white_material': white_material,
            'black_material': black_material,
            'material_difference': white_material - black_material
        }
    
    def process_puzzles(self, puzzle_file: str, max_puzzles: int = 50000) -> List[Dict[str, Any]]:
        """Process Lichess puzzles for QEC training"""
        print(f"Processing Lichess puzzles (max: {max_puzzles})...")
        
        puzzles = []
        
        with open(puzzle_file, 'rb') as f:
            dctx = zstd.ZstdDecompressor()
            with dctx.stream_reader(f) as reader:
                csv_reader = csv.DictReader(io.TextIOWrapper(reader, encoding='utf-8'))
                
                for row_num, row in enumerate(csv_reader):
                    if row_num >= max_puzzles:
                        break
                    
                    try:
                        qec_puzzle = self._convert_puzzle_to_qec(row)
                        if qec_puzzle:
                            puzzles.append(qec_puzzle)
                            self.puzzles_processed += 1
                            
                            if self.puzzles_processed % 5000 == 0:
                                print(f"Processed {self.puzzles_processed} puzzles...")
                                
                    except Exception as e:
                        print(f"Error processing puzzle {row_num}: {e}")
                        continue
        
        print(f"Successfully processed {len(puzzles)} puzzles")
        return puzzles
    
    def _convert_puzzle_to_qec(self, puzzle_row: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Convert Lichess puzzle to QEC format"""
        try:
            fen = puzzle_row.get('FEN', '')
            if not fen:
                return None
            
            # Parse puzzle data
            puzzle_id = puzzle_row.get('PuzzleId', '')
            moves = puzzle_row.get('Moves', '')
            rating = int(puzzle_row.get('Rating', 0))
            themes = puzzle_row.get('Themes', '').split()
            
            # Convert to QEC format
            qec_puzzle = {
                'puzzle_id': puzzle_id,
                'fen': fen,
                'moves': moves,
                'rating': rating,
                'themes': themes,
                'qec_analysis': {
                    'entanglement_opportunities': self._analyze_puzzle_entanglement(fen, moves),
                    'forced_move_sequence': self._analyze_forced_sequence(moves),
                    'tactical_patterns': self._identify_tactical_patterns(themes),
                    'difficulty_level': self._assess_difficulty(rating),
                    'qec_relevance': self._assess_qec_relevance(themes)
                }
            }
            
            return qec_puzzle
            
        except Exception as e:
            print(f"Error converting puzzle: {e}")
            return None
    
    def _analyze_puzzle_entanglement(self, fen: str, moves: str) -> List[Dict[str, Any]]:
        """Analyze entanglement opportunities in puzzle"""
        opportunities = []
        
        try:
            board = chess.Board(fen)
            
            # Look for piece interactions in the puzzle
            move_list = moves.split()
            for i, move in enumerate(move_list):
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
        
        except Exception as e:
            print(f"Error analyzing puzzle entanglement: {e}")
        
        return opportunities
    
    def _analyze_forced_sequence(self, moves: str) -> Dict[str, Any]:
        """Analyze forced move sequence in puzzle"""
        move_list = moves.split()
        
        return {
            'total_moves': len(move_list),
            'captures': sum(1 for move in move_list if 'x' in move),
            'checks': sum(1 for move in move_list if '+' in move),
            'sequence_type': 'tactical' if any('x' in move for move in move_list) else 'positional'
        }
    
    def _identify_tactical_patterns(self, themes: List[str]) -> List[str]:
        """Identify tactical patterns from puzzle themes"""
        qec_patterns = []
        
        theme_mapping = {
            'fork': 'fork_entanglement',
            'pin': 'pin_entanglement',
            'skewer': 'skewer_entanglement',
            'discoveredAttack': 'discovered_entanglement',
            'sacrifice': 'sacrifice_entanglement',
            'mate': 'mate_entanglement'
        }
        
        for theme in themes:
            if theme in theme_mapping:
                qec_patterns.append(theme_mapping[theme])
        
        return qec_patterns
    
    def _assess_difficulty(self, rating: int) -> str:
        """Assess puzzle difficulty level"""
        if rating >= 2000:
            return 'expert'
        elif rating >= 1500:
            return 'advanced'
        elif rating >= 1000:
            return 'intermediate'
        else:
            return 'beginner'
    
    def _assess_qec_relevance(self, themes: List[str]) -> Dict[str, Any]:
        """Assess relevance to QEC training"""
        relevant_themes = ['fork', 'pin', 'skewer', 'discoveredAttack', 'sacrifice', 'mate']
        qec_relevant = sum(1 for theme in themes if theme in relevant_themes)
        
        return {
            'relevance_score': qec_relevant / len(themes) if themes else 0,
            'relevant_themes': [theme for theme in themes if theme in relevant_themes],
            'qec_training_value': 'high' if qec_relevant >= 3 else 'medium' if qec_relevant >= 1 else 'low'
        }
    
    def create_qec_training_dataset(self, evaluations: List[Dict[str, Any]], puzzles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create comprehensive QEC training dataset"""
        print("Creating QEC training dataset from Lichess data...")
        
        training_dataset = {
            'evaluations': {
                'total': len(evaluations),
                'high_entanglement': [e for e in evaluations if len(e['qec_analysis']['entanglement_opportunities']) > 2],
                'tactical_positions': [e for e in evaluations if e['qec_analysis']['tactical_complexity']['complexity'] == 'high'],
                'positional_positions': [e for e in evaluations if len(e['qec_analysis']['positional_themes']) > 2]
            },
            'puzzles': {
                'total': len(puzzles),
                'qec_relevant': [p for p in puzzles if p['qec_analysis']['qec_relevance']['qec_training_value'] == 'high'],
                'tactical_puzzles': [p for p in puzzles if 'tactical' in p['qec_analysis']['forced_move_sequence']['sequence_type']],
                'expert_puzzles': [p for p in puzzles if p['qec_analysis']['difficulty_level'] == 'expert']
            },
            'combined_training': {
                'entanglement_examples': self._extract_entanglement_examples(evaluations, puzzles),
                'forced_move_examples': self._extract_forced_move_examples(evaluations, puzzles),
                'tactical_examples': self._extract_tactical_examples(evaluations, puzzles),
                'positional_examples': self._extract_positional_examples(evaluations, puzzles)
            }
        }
        
        print(f"Created training dataset with {len(evaluations)} evaluations and {len(puzzles)} puzzles")
        return training_dataset
    
    def _extract_entanglement_examples(self, evaluations: List[Dict[str, Any]], puzzles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract entanglement examples for training"""
        examples = []
        
        # From evaluations
        for eval_data in evaluations:
            if len(eval_data['qec_analysis']['entanglement_opportunities']) > 0:
                examples.append({
                    'type': 'evaluation',
                    'fen': eval_data['fen'],
                    'opportunities': eval_data['qec_analysis']['entanglement_opportunities'],
                    'evaluation': eval_data['evaluation']
                })
        
        # From puzzles
        for puzzle in puzzles:
            if len(puzzle['qec_analysis']['entanglement_opportunities']) > 0:
                examples.append({
                    'type': 'puzzle',
                    'fen': puzzle['fen'],
                    'opportunities': puzzle['qec_analysis']['entanglement_opportunities'],
                    'rating': puzzle['rating']
                })
        
        return examples
    
    def _extract_forced_move_examples(self, evaluations: List[Dict[str, Any]], puzzles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract forced move examples for training"""
        examples = []
        
        # From evaluations
        for eval_data in evaluations:
            if eval_data['qec_analysis']['forced_move_potential']['forced_potential'] == 'high':
                examples.append({
                    'type': 'evaluation',
                    'fen': eval_data['fen'],
                    'forced_potential': eval_data['qec_analysis']['forced_move_potential'],
                    'evaluation': eval_data['evaluation']
                })
        
        # From puzzles
        for puzzle in puzzles:
            if puzzle['qec_analysis']['forced_move_sequence']['total_moves'] > 2:
                examples.append({
                    'type': 'puzzle',
                    'fen': puzzle['fen'],
                    'sequence': puzzle['qec_analysis']['forced_move_sequence'],
                    'rating': puzzle['rating']
                })
        
        return examples
    
    def _extract_tactical_examples(self, evaluations: List[Dict[str, Any]], puzzles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract tactical examples for training"""
        examples = []
        
        # From evaluations
        for eval_data in evaluations:
            if eval_data['qec_analysis']['tactical_complexity']['complexity'] == 'high':
                examples.append({
                    'type': 'evaluation',
                    'fen': eval_data['fen'],
                    'complexity': eval_data['qec_analysis']['tactical_complexity'],
                    'evaluation': eval_data['evaluation']
                })
        
        # From puzzles
        for puzzle in puzzles:
            if len(puzzle['qec_analysis']['tactical_patterns']) > 0:
                examples.append({
                    'type': 'puzzle',
                    'fen': puzzle['fen'],
                    'patterns': puzzle['qec_analysis']['tactical_patterns'],
                    'rating': puzzle['rating']
                })
        
        return examples
    
    def _extract_positional_examples(self, evaluations: List[Dict[str, Any]], puzzles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract positional examples for training"""
        examples = []
        
        # From evaluations
        for eval_data in evaluations:
            if len(eval_data['qec_analysis']['positional_themes']) > 0:
                examples.append({
                    'type': 'evaluation',
                    'fen': eval_data['fen'],
                    'themes': eval_data['qec_analysis']['positional_themes'],
                    'evaluation': eval_data['evaluation']
                })
        
        return examples
    
    def save_training_dataset(self, dataset: Dict[str, Any], output_path: str = "data/lichess_qec_training.json"):
        """Save training dataset to file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(dataset, f, indent=2)
        
        print(f"Training dataset saved to {output_file}")
        return str(output_file)

def main():
    """Main Lichess integration script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Lichess Database Integration for QEC')
    parser.add_argument('--download-evals', action='store_true', help='Download evaluations database')
    parser.add_argument('--download-puzzles', action='store_true', help='Download puzzles database')
    parser.add_argument('--process-evals', type=int, default=100000, help='Number of evaluations to process')
    parser.add_argument('--process-puzzles', type=int, default=50000, help='Number of puzzles to process')
    parser.add_argument('--output', type=str, default='data/lichess_qec_training.json', help='Output file')
    parser.add_argument('--all', action='store_true', help='Download and process all data')
    
    args = parser.parse_args()
    
    # Initialize integrator
    integrator = LichessDatabaseIntegrator()
    
    try:
        evaluations = []
        puzzles = []
        
        if args.all or args.download_evals:
            # Download evaluations
            eval_file = integrator.download_evaluations()
            evaluations = integrator.process_evaluations(eval_file, args.process_evals)
        
        if args.all or args.download_puzzles:
            # Download puzzles
            puzzle_file = integrator.download_puzzles()
            puzzles = integrator.process_puzzles(puzzle_file, args.process_puzzles)
        
        if evaluations or puzzles:
            # Create training dataset
            dataset = integrator.create_qec_training_dataset(evaluations, puzzles)
            
            # Save dataset
            output_path = integrator.save_training_dataset(dataset, args.output)
            
            print(f"Lichess integration completed successfully!")
            print(f"Dataset saved to: {output_path}")
        
    except Exception as e:
        print(f"Error during Lichess integration: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
