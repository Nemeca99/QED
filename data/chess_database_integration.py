"""
Chess Database Integration for QEC
Download and parse Lumbra's Gigabase for QEC research
"""

import os
import sys
import requests
import zipfile
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import chess
import chess.pgn
from datetime import datetime

class ChessDatabaseIntegrator:
    """Integrate Lumbra's Gigabase with QEC system"""
    
    def __init__(self, data_dir: str = "data/chess_database"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = "https://lumbrasgigabase.com/en/"
        self.games_parsed = 0
        self.games_processed = 0
        
    def download_database(self, database_type: str = "OTB") -> str:
        """Download Lumbra's Gigabase database"""
        print(f"Downloading {database_type} database from Lumbra's Gigabase...")
        
        # Database URLs (these would need to be updated with actual download links)
        urls = {
            "OTB": "https://lumbrasgigabase.com/download/otb_database.zip",
            "Online": "https://lumbrasgigabase.com/download/online_database.zip"
        }
        
        if database_type not in urls:
            raise ValueError(f"Unknown database type: {database_type}")
        
        # Download the database
        response = requests.get(urls[database_type], stream=True)
        response.raise_for_status()
        
        # Save to file
        zip_path = self.data_dir / f"{database_type.lower()}_database.zip"
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Downloaded {database_type} database to {zip_path}")
        return str(zip_path)
    
    def extract_database(self, zip_path: str) -> str:
        """Extract the database archive"""
        print(f"Extracting database from {zip_path}...")
        
        extract_dir = self.data_dir / "extracted"
        extract_dir.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Find the main PGN file
        pgn_files = list(extract_dir.rglob("*.pgn"))
        if not pgn_files:
            raise FileNotFoundError("No PGN files found in extracted archive")
        
        main_pgn = pgn_files[0]  # Take the first (largest) PGN file
        print(f"Found main PGN file: {main_pgn}")
        return str(main_pgn)
    
    def parse_games(self, pgn_path: str, max_games: int = 10000) -> List[Dict[str, Any]]:
        """Parse games from PGN file"""
        print(f"Parsing games from {pgn_path} (max: {max_games})...")
        
        games = []
        with open(pgn_path, 'r', encoding='utf-8', errors='ignore') as pgn_file:
            while len(games) < max_games:
                try:
                    game = chess.pgn.read_game(pgn_file)
                    if game is None:
                        break
                    
                    # Extract game information
                    game_data = self._extract_game_data(game)
                    if game_data:
                        games.append(game_data)
                        self.games_parsed += 1
                        
                        if self.games_parsed % 1000 == 0:
                            print(f"Parsed {self.games_parsed} games...")
                            
                except Exception as e:
                    print(f"Error parsing game: {e}")
                    continue
        
        print(f"Successfully parsed {len(games)} games")
        return games
    
    def _extract_game_data(self, game: chess.pgn.Game) -> Optional[Dict[str, Any]]:
        """Extract relevant data from a chess game"""
        try:
            # Get game headers
            headers = game.headers
            
            # Filter for high-quality games
            white_elo = headers.get('WhiteElo', '0')
            black_elo = headers.get('BlackElo', '0')
            
            # Skip games with low ELO ratings
            if white_elo.isdigit() and black_elo.isdigit():
                if int(white_elo) < 1800 or int(black_elo) < 1800:
                    return None
            
            # Skip very short games
            if len(list(game.mainline())) < 10:
                return None
            
            # Extract moves
            moves = []
            board = game.board()
            
            for move in game.mainline():
                moves.append({
                    'move': str(move),
                    'san': board.san(move),
                    'fen': board.fen(),
                    'turn': 'white' if board.turn else 'black'
                })
                board.push(move)
            
            return {
                'white': headers.get('White', 'Unknown'),
                'black': headers.get('Black', 'Unknown'),
                'white_elo': white_elo,
                'black_elo': black_elo,
                'result': headers.get('Result', '*'),
                'date': headers.get('Date', '????.??.??'),
                'event': headers.get('Event', 'Unknown'),
                'site': headers.get('Site', 'Unknown'),
                'round': headers.get('Round', '?'),
                'eco': headers.get('ECO', ''),
                'opening': headers.get('Opening', ''),
                'moves': moves,
                'total_moves': len(moves),
                'final_fen': board.fen(),
                'source': headers.get('Source', 'LumbraGigabase')
            }
            
        except Exception as e:
            print(f"Error extracting game data: {e}")
            return None
    
    def create_qec_training_set(self, games: List[Dict[str, Any]], output_file: str = "qec_training_set.json") -> str:
        """Create QEC training set from chess games"""
        print(f"Creating QEC training set from {len(games)} games...")
        
        training_data = []
        
        for i, game in enumerate(games):
            if i % 1000 == 0:
                print(f"Processing game {i}/{len(games)}...")
            
            # Convert to QEC format
            qec_game = self._convert_to_qec_format(game)
            if qec_game:
                training_data.append(qec_game)
                self.games_processed += 1
        
        # Save training set
        output_path = self.data_dir / output_file
        with open(output_path, 'w') as f:
            json.dump(training_data, f, indent=2)
        
        print(f"Created QEC training set with {len(training_data)} games")
        print(f"Saved to {output_path}")
        return str(output_path)
    
    def _convert_to_qec_format(self, game: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Convert chess game to QEC format"""
        try:
            # Create QEC game structure
            qec_game = {
                'original_game': {
                    'white': game['white'],
                    'black': game['black'],
                    'white_elo': game['white_elo'],
                    'black_elo': game['black_elo'],
                    'result': game['result'],
                    'date': game['date'],
                    'event': game['event'],
                    'eco': game['eco'],
                    'opening': game['opening']
                },
                'qec_analysis': {
                    'entanglement_opportunities': self._find_entanglement_opportunities(game['moves']),
                    'forced_move_patterns': self._find_forced_move_patterns(game['moves']),
                    'reactive_escape_patterns': self._find_reactive_escape_patterns(game['moves']),
                    'opening_phase': self._analyze_opening_phase(game['moves']),
                    'middlegame_phase': self._analyze_middlegame_phase(game['moves']),
                    'endgame_phase': self._analyze_endgame_phase(game['moves'])
                },
                'moves': game['moves'],
                'total_moves': game['total_moves'],
                'final_fen': game['final_fen']
            }
            
            return qec_game
            
        except Exception as e:
            print(f"Error converting game to QEC format: {e}")
            return None
    
    def _find_entanglement_opportunities(self, moves: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find potential entanglement opportunities in the game"""
        opportunities = []
        
        for i, move in enumerate(moves):
            # Look for piece interactions that could become entangled
            if 'x' in move['san']:  # Capture moves
                opportunities.append({
                    'move_number': i + 1,
                    'move': move['san'],
                    'type': 'capture_entanglement',
                    'fen': move['fen']
                })
            
            # Look for piece coordination
            if i > 0:
                prev_move = moves[i-1]
                if self._pieces_coordinated(prev_move, move):
                    opportunities.append({
                        'move_number': i + 1,
                        'move': move['san'],
                        'type': 'coordination_entanglement',
                        'fen': move['fen']
                    })
        
        return opportunities
    
    def _find_forced_move_patterns(self, moves: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find forced move patterns in the game"""
        forced_patterns = []
        
        for i, move in enumerate(moves):
            # Check for checks (forced responses)
            if '+' in move['san'] or '#' in move['san']:
                forced_patterns.append({
                    'move_number': i + 1,
                    'move': move['san'],
                    'type': 'check_forced',
                    'fen': move['fen']
                })
            
            # Check for tactical sequences
            if i < len(moves) - 1:
                next_move = moves[i + 1]
                if self._is_tactical_sequence(move, next_move):
                    forced_patterns.append({
                        'move_number': i + 1,
                        'move': move['san'],
                        'type': 'tactical_forced',
                        'fen': move['fen']
                    })
        
        return forced_patterns
    
    def _find_reactive_escape_patterns(self, moves: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find reactive escape patterns in the game"""
        escape_patterns = []
        
        for i, move in enumerate(moves):
            # Look for king escape patterns
            if 'K' in move['san'] and ('+' in move['san'] or '#' in move['san']):
                escape_patterns.append({
                    'move_number': i + 1,
                    'move': move['san'],
                    'type': 'king_escape',
                    'fen': move['fen']
                })
            
            # Look for piece retreats
            if i > 0 and self._is_retreat_move(moves[i-1], move):
                escape_patterns.append({
                    'move_number': i + 1,
                    'move': move['san'],
                    'type': 'piece_retreat',
                    'fen': move['fen']
                })
        
        return escape_patterns
    
    def _analyze_opening_phase(self, moves: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze opening phase of the game"""
        opening_moves = moves[:20] if len(moves) >= 20 else moves
        
        return {
            'moves': len(opening_moves),
            'eco_codes': self._extract_eco_codes(opening_moves),
            'opening_patterns': self._identify_opening_patterns(opening_moves),
            'development': self._analyze_development(opening_moves)
        }
    
    def _analyze_middlegame_phase(self, moves: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze middlegame phase of the game"""
        if len(moves) < 20:
            return {'moves': 0, 'tactical_patterns': [], 'strategic_themes': []}
        
        middlegame_moves = moves[20:len(moves)-20] if len(moves) > 40 else moves[20:]
        
        return {
            'moves': len(middlegame_moves),
            'tactical_patterns': self._identify_tactical_patterns(middlegame_moves),
            'strategic_themes': self._identify_strategic_themes(middlegame_moves)
        }
    
    def _analyze_endgame_phase(self, moves: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze endgame phase of the game"""
        if len(moves) < 40:
            return {'moves': 0, 'endgame_patterns': [], 'material_balance': {}}
        
        endgame_moves = moves[-20:]
        
        return {
            'moves': len(endgame_moves),
            'endgame_patterns': self._identify_endgame_patterns(endgame_moves),
            'material_balance': self._analyze_material_balance(endgame_moves)
        }
    
    def _pieces_coordinated(self, prev_move: Dict, curr_move: Dict) -> bool:
        """Check if pieces are coordinated between moves"""
        # Simplified coordination check
        return prev_move['turn'] != curr_move['turn']
    
    def _is_tactical_sequence(self, move1: Dict, move2: Dict) -> bool:
        """Check if two moves form a tactical sequence"""
        # Simplified tactical sequence detection
        return 'x' in move1['san'] and 'x' in move2['san']
    
    def _is_retreat_move(self, prev_move: Dict, curr_move: Dict) -> bool:
        """Check if current move is a retreat"""
        # Simplified retreat detection
        return prev_move['turn'] == curr_move['turn']
    
    def _extract_eco_codes(self, moves: List[Dict[str, Any]]) -> List[str]:
        """Extract ECO codes from opening moves"""
        # This would implement actual ECO code extraction
        return []
    
    def _identify_opening_patterns(self, moves: List[Dict[str, Any]]) -> List[str]:
        """Identify opening patterns"""
        # This would implement opening pattern recognition
        return []
    
    def _analyze_development(self, moves: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze piece development in opening"""
        return {
            'knights_developed': 0,
            'bishops_developed': 0,
            'castling': False,
            'queen_development': False
        }
    
    def _identify_tactical_patterns(self, moves: List[Dict[str, Any]]) -> List[str]:
        """Identify tactical patterns in middlegame"""
        return []
    
    def _identify_strategic_themes(self, moves: List[Dict[str, Any]]) -> List[str]:
        """Identify strategic themes in middlegame"""
        return []
    
    def _identify_endgame_patterns(self, moves: List[Dict[str, Any]]) -> List[str]:
        """Identify endgame patterns"""
        return []
    
    def _analyze_material_balance(self, moves: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze material balance in endgame"""
        return {
            'white_material': 0,
            'black_material': 0,
            'material_difference': 0
        }

def main():
    """Main integration script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Chess Database Integration for QEC')
    parser.add_argument('--database', type=str, choices=['OTB', 'Online'], default='OTB', help='Database type to download')
    parser.add_argument('--max-games', type=int, default=10000, help='Maximum games to process')
    parser.add_argument('--output', type=str, default='qec_training_set.json', help='Output file name')
    parser.add_argument('--download-only', action='store_true', help='Only download, do not process')
    
    args = parser.parse_args()
    
    # Initialize integrator
    integrator = ChessDatabaseIntegrator()
    
    try:
        # Download database
        zip_path = integrator.download_database(args.database)
        
        if args.download_only:
            print("Download completed. Use --no-download-only to process games.")
            return 0
        
        # Extract database
        pgn_path = integrator.extract_database(zip_path)
        
        # Parse games
        games = integrator.parse_games(pgn_path, args.max_games)
        
        # Create QEC training set
        training_set_path = integrator.create_qec_training_set(games, args.output)
        
        print(f"Integration completed successfully!")
        print(f"Training set saved to: {training_set_path}")
        
    except Exception as e:
        print(f"Error during integration: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
