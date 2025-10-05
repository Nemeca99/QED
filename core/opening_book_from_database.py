"""
QEC Opening Book from Real Chess Games
Create opening book from Lumbra's Gigabase for QEC training
"""

import sys
import os
import json
import chess
import chess.pgn
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict, Counter
import pickle

class QECOpeningBook:
    """Opening book created from real chess games for QEC training"""
    
    def __init__(self, database_path: str = "data/chess_database/qec_training_set.json"):
        self.database_path = Path(database_path)
        self.opening_book = {}
        self.position_stats = defaultdict(lambda: {'games': 0, 'wins': 0, 'draws': 0, 'losses': 0})
        self.move_frequencies = defaultdict(Counter)
        self.eco_codes = {}
        
    def load_database(self) -> List[Dict[str, Any]]:
        """Load chess database for opening book creation"""
        print(f"Loading chess database from {self.database_path}...")
        
        if not self.database_path.exists():
            raise FileNotFoundError(f"Database not found: {self.database_path}")
        
        with open(self.database_path, 'r') as f:
            games = json.load(f)
        
        print(f"Loaded {len(games)} games from database")
        return games
    
    def create_opening_book(self, max_depth: int = 15) -> Dict[str, Any]:
        """Create opening book from chess games"""
        print(f"Creating opening book with max depth {max_depth}...")
        
        games = self.load_database()
        
        for i, game in enumerate(games):
            if i % 1000 == 0:
                print(f"Processing game {i}/{len(games)}...")
            
            self._process_game_for_opening_book(game, max_depth)
        
        # Convert to final opening book format
        opening_book = self._finalize_opening_book()
        
        print(f"Created opening book with {len(opening_book)} positions")
        return opening_book
    
    def _process_game_for_opening_book(self, game: Dict[str, Any], max_depth: int):
        """Process a single game for opening book creation"""
        try:
            moves = game.get('moves', [])
            result = game.get('original_game', {}).get('result', '*')
            
            # Convert result to numeric
            result_value = self._convert_result_to_numeric(result)
            
            # Process opening moves
            for i, move in enumerate(moves[:max_depth]):
                fen = move.get('fen', '')
                if not fen:
                    continue
                
                # Update position statistics
                self.position_stats[fen]['games'] += 1
                self.position_stats[fen]['wins'] += result_value
                self.position_stats[fen]['draws'] += 1 if result_value == 0 else 0
                self.position_stats[fen]['losses'] += -result_value if result_value < 0 else 0
                
                # Update move frequencies
                if i < len(moves) - 1:
                    next_move = moves[i + 1]
                    move_san = next_move.get('san', '')
                    if move_san:
                        self.move_frequencies[fen][move_san] += 1
                
                # Extract ECO code if available
                if i == 0:  # First move
                    eco = game.get('original_game', {}).get('eco', '')
                    if eco:
                        self.eco_codes[fen] = eco
                        
        except Exception as e:
            print(f"Error processing game for opening book: {e}")
    
    def _convert_result_to_numeric(self, result: str) -> int:
        """Convert game result to numeric value"""
        if result == '1-0':
            return 1  # White wins
        elif result == '0-1':
            return -1  # Black wins
        elif result == '1/2-1/2':
            return 0  # Draw
        else:
            return 0  # Unknown result
    
    def _finalize_opening_book(self) -> Dict[str, Any]:
        """Finalize opening book with statistics and recommendations"""
        opening_book = {}
        
        for fen, stats in self.position_stats.items():
            if stats['games'] < 3:  # Skip positions with too few games
                continue
            
            # Calculate win rates
            total_games = stats['games']
            white_wins = stats['wins']
            black_wins = stats['losses']
            draws = stats['draws']
            
            white_win_rate = white_wins / total_games if total_games > 0 else 0
            black_win_rate = black_wins / total_games if total_games > 0 else 0
            draw_rate = draws / total_games if total_games > 0 else 0
            
            # Get move recommendations
            move_recommendations = self._get_move_recommendations(fen)
            
            # Get ECO code
            eco_code = self.eco_codes.get(fen, '')
            
            opening_book[fen] = {
                'games': total_games,
                'white_wins': white_wins,
                'black_wins': black_wins,
                'draws': draws,
                'white_win_rate': white_win_rate,
                'black_win_rate': black_win_rate,
                'draw_rate': draw_rate,
                'eco_code': eco_code,
                'recommended_moves': move_recommendations,
                'entanglement_opportunities': self._find_entanglement_opportunities(fen)
            }
        
        return opening_book
    
    def _get_move_recommendations(self, fen: str) -> List[Dict[str, Any]]:
        """Get move recommendations for a position"""
        if fen not in self.move_frequencies:
            return []
        
        move_freq = self.move_frequencies[fen]
        total_moves = sum(move_freq.values())
        
        recommendations = []
        for move, frequency in move_freq.most_common(5):  # Top 5 moves
            recommendations.append({
                'move': move,
                'frequency': frequency,
                'percentage': frequency / total_moves if total_moves > 0 else 0
            })
        
        return recommendations
    
    def _find_entanglement_opportunities(self, fen: str) -> List[Dict[str, Any]]:
        """Find entanglement opportunities in a position"""
        try:
            board = chess.Board(fen)
            opportunities = []
            
            # Look for piece interactions that could become entangled
            for square in chess.SQUARES:
                piece = board.piece_at(square)
                if piece is None:
                    continue
                
                # Check for piece coordination opportunities
                if piece.piece_type == chess.PAWN:
                    # Pawn entanglement opportunities
                    opportunities.append({
                        'type': 'pawn_entanglement',
                        'square': chess.square_name(square),
                        'piece': piece.symbol(),
                        'color': 'white' if piece.color else 'black'
                    })
                
                elif piece.piece_type in [chess.ROOK, chess.BISHOP, chess.QUEEN]:
                    # Sliding piece entanglement opportunities
                    opportunities.append({
                        'type': 'sliding_entanglement',
                        'square': chess.square_name(square),
                        'piece': piece.symbol(),
                        'color': 'white' if piece.color else 'black'
                    })
            
            return opportunities
            
        except Exception as e:
            print(f"Error finding entanglement opportunities: {e}")
            return []
    
    def save_opening_book(self, output_path: str = "data/opening_book.json"):
        """Save opening book to file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(self.opening_book, f, indent=2)
        
        print(f"Opening book saved to {output_file}")
        return str(output_file)
    
    def load_opening_book(self, book_path: str) -> Dict[str, Any]:
        """Load opening book from file"""
        with open(book_path, 'r') as f:
            self.opening_book = json.load(f)
        
        print(f"Loaded opening book with {len(self.opening_book)} positions")
        return self.opening_book
    
    def get_best_move(self, fen: str) -> Optional[str]:
        """Get best move recommendation for a position"""
        if fen not in self.opening_book:
            return None
        
        position = self.opening_book[fen]
        recommended_moves = position.get('recommended_moves', [])
        
        if not recommended_moves:
            return None
        
        # Return the most frequent move
        return recommended_moves[0]['move']
    
    def get_position_stats(self, fen: str) -> Optional[Dict[str, Any]]:
        """Get position statistics"""
        if fen not in self.opening_book:
            return None
        
        return self.opening_book[fen]
    
    def analyze_opening_performance(self) -> Dict[str, Any]:
        """Analyze opening performance across the book"""
        total_positions = len(self.opening_book)
        total_games = sum(pos['games'] for pos in self.opening_book.values())
        
        # Calculate average win rates
        avg_white_win_rate = sum(pos['white_win_rate'] for pos in self.opening_book.values()) / total_positions
        avg_black_win_rate = sum(pos['black_win_rate'] for pos in self.opening_book.values()) / total_positions
        avg_draw_rate = sum(pos['draw_rate'] for pos in self.opening_book.values()) / total_positions
        
        # Find most popular positions
        most_popular = sorted(
            self.opening_book.items(),
            key=lambda x: x[1]['games'],
            reverse=True
        )[:10]
        
        # Find positions with highest white/black win rates
        best_white_positions = sorted(
            self.opening_book.items(),
            key=lambda x: x[1]['white_win_rate'],
            reverse=True
        )[:10]
        
        best_black_positions = sorted(
            self.opening_book.items(),
            key=lambda x: x[1]['black_win_rate'],
            reverse=True
        )[:10]
        
        return {
            'total_positions': total_positions,
            'total_games': total_games,
            'average_white_win_rate': avg_white_win_rate,
            'average_black_win_rate': avg_black_win_rate,
            'average_draw_rate': avg_draw_rate,
            'most_popular_positions': most_popular,
            'best_white_positions': best_white_positions,
            'best_black_positions': best_black_positions
        }

def main():
    """Main opening book creation script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='QEC Opening Book Creation')
    parser.add_argument('--database', type=str, default='data/chess_database/qec_training_set.json', help='Database path')
    parser.add_argument('--output', type=str, default='data/opening_book.json', help='Output file')
    parser.add_argument('--max-depth', type=int, default=15, help='Maximum opening depth')
    parser.add_argument('--analyze', action='store_true', help='Analyze opening performance')
    
    args = parser.parse_args()
    
    # Create opening book
    book_creator = QECOpeningBook(args.database)
    
    try:
        # Create opening book
        opening_book = book_creator.create_opening_book(args.max_depth)
        book_creator.opening_book = opening_book
        
        # Save opening book
        output_path = book_creator.save_opening_book(args.output)
        
        # Analyze performance if requested
        if args.analyze:
            analysis = book_creator.analyze_opening_performance()
            print("\nOpening Book Analysis:")
            print(f"Total positions: {analysis['total_positions']}")
            print(f"Total games: {analysis['total_games']}")
            print(f"Average white win rate: {analysis['average_white_win_rate']:.3f}")
            print(f"Average black win rate: {analysis['average_black_win_rate']:.3f}")
            print(f"Average draw rate: {analysis['average_draw_rate']:.3f}")
        
        print(f"Opening book creation completed successfully!")
        print(f"Book saved to: {output_path}")
        
    except Exception as e:
        print(f"Error creating opening book: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
