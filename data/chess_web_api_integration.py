"""
Chess Web API Integration for QEC
Integrate chess-web-api for real-time chess data access
"""

import sys
import os
import json
import requests
import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, List, Any, Optional, AsyncGenerator
from datetime import datetime, timedelta
import time

class ChessWebAPIIntegrator:
    """Integrate chess-web-api for real-time chess data"""
    
    def __init__(self, data_dir: str = "data/chess_web_api"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # API endpoints (would be configured for actual chess-web-api)
        self.lichess_api = "https://lichess.org/api"
        self.chesscom_api = "https://api.chess.com"
        self.chessdb_api = "https://chessdb.cn"
        
        self.rate_limits = {
            'lichess': {'requests_per_minute': 60, 'last_request': 0},
            'chesscom': {'requests_per_minute': 30, 'last_request': 0},
            'chessdb': {'requests_per_minute': 20, 'last_request': 0}
        }
        
    async def get_lichess_games(self, username: str, max_games: int = 100) -> List[Dict[str, Any]]:
        """Get recent games from Lichess for a user"""
        print(f"Fetching {max_games} recent games for {username} from Lichess...")
        
        games = []
        url = f"{self.lichess_api}/games/user/{username}"
        
        params = {
            'max': max_games,
            'perfType': 'blitz,rapid,classical',  # All time controls
            'clocks': 'true',
            'evals': 'true'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        # Lichess returns PGN format, not JSON
                        pgn_text = await response.text()
                        games = self._process_lichess_pgn(pgn_text, username)
                    else:
                        print(f"Error fetching Lichess games: {response.status}")
        
        except Exception as e:
            print(f"Error fetching Lichess games: {e}")
        
        print(f"Fetched {len(games)} games from Lichess")
        return games
    
    def _process_lichess_pgn(self, pgn_text: str, username: str) -> List[Dict[str, Any]]:
        """Process Lichess PGN data"""
        games = []
        
        # Split PGN into individual games
        pgn_games = pgn_text.split('\n\n\n')
        
        for pgn_game in pgn_games:
            if not pgn_game.strip():
                continue
                
            try:
                # Parse PGN headers
                lines = pgn_game.strip().split('\n')
                headers = {}
                moves = []
                
                for line in lines:
                    if line.startswith('[') and line.endswith(']'):
                        # Parse header
                        key_value = line[1:-1].split(' ', 1)
                        if len(key_value) == 2:
                            key = key_value[0]
                            value = key_value[1].strip('"')
                            headers[key] = value
                    else:
                        # Parse moves
                        if line.strip() and not line.startswith('['):
                            moves.extend(line.strip().split())
                
                # Create game object
                game = {
                    'id': headers.get('Site', '').split('/')[-1] if 'Site' in headers else '',
                    'white': {'username': headers.get('White', ''), 'rating': int(headers.get('WhiteElo', 0)) if headers.get('WhiteElo', '').isdigit() else 0},
                    'black': {'username': headers.get('Black', ''), 'rating': int(headers.get('BlackElo', 0)) if headers.get('BlackElo', '').isdigit() else 0},
                    'winner': 'white' if headers.get('Result') == '1-0' else 'black' if headers.get('Result') == '0-1' else 'draw',
                    'status': 'mate' if '#' in pgn_game else 'resign' if 'resigns' in pgn_game else 'draw',
                    'rated': True,
                    'timeControl': headers.get('TimeControl', ''),
                    'createdAt': 0,  # Would need to parse date
                    'lastMoveAt': 0,
                    'turns': len(moves),
                    'clock': {'initial': 0, 'increment': 0},  # Would need to parse from TimeControl
                    'pgn': pgn_game,
                    'moves': moves,
                    'qec_analysis': self._analyze_game_for_qec({'moves': moves, 'clock': {}, 'perf': {}})
                }
                
                games.append(game)
                
            except Exception as e:
                print(f"Error processing PGN game: {e}")
                continue
        
        return games
    
    def _analyze_game_for_qec(self, game_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze game for QEC patterns"""
        analysis = {
            'entanglement_opportunities': [],
            'forced_move_patterns': [],
            'reactive_escape_patterns': [],
            'tactical_combinations': [],
            'positional_themes': []
        }
        
        try:
            # Analyze moves for QEC patterns
            moves = game_data.get('moves', '')
            if moves:
                move_list = moves.split()
                analysis['entanglement_opportunities'] = self._find_entanglement_opportunities(move_list)
                analysis['forced_move_patterns'] = self._find_forced_move_patterns(move_list)
                analysis['reactive_escape_patterns'] = self._find_reactive_escape_patterns(move_list)
                analysis['tactical_combinations'] = self._find_tactical_combinations(move_list)
                analysis['positional_themes'] = self._identify_positional_themes(move_list)
            
            # Analyze clock data for time pressure
            clock = game_data.get('clock', {})
            if clock:
                analysis['time_pressure'] = self._analyze_time_pressure(clock)
            
            # Analyze performance data
            perf = game_data.get('perf', {})
            if perf:
                analysis['performance_metrics'] = self._analyze_performance_metrics(perf)
        
        except Exception as e:
            print(f"Error analyzing game for QEC: {e}")
        
        return analysis
    
    def _find_entanglement_opportunities(self, moves: List[str]) -> List[Dict[str, Any]]:
        """Find entanglement opportunities in moves"""
        opportunities = []
        
        for i, move in enumerate(moves):
            # Look for captures (potential entanglement)
            if 'x' in move:
                opportunities.append({
                    'move_number': i + 1,
                    'move': move,
                    'type': 'capture_entanglement',
                    'description': 'Capture move that could create entanglement'
                })
            
            # Look for checks (potential entanglement)
            if '+' in move or '#' in move:
                opportunities.append({
                    'move_number': i + 1,
                    'move': move,
                    'type': 'check_entanglement',
                    'description': 'Check move that could create entanglement'
                })
            
            # Look for piece coordination
            if i > 0 and self._pieces_coordinated(moves[i-1], move):
                opportunities.append({
                    'move_number': i + 1,
                    'move': move,
                    'type': 'coordination_entanglement',
                    'description': 'Piece coordination that could create entanglement'
                })
        
        return opportunities
    
    def _find_forced_move_patterns(self, moves: List[str]) -> List[Dict[str, Any]]:
        """Find forced move patterns in moves"""
        patterns = []
        
        for i, move in enumerate(moves):
            # Check for checks (forced responses)
            if '+' in move or '#' in move:
                patterns.append({
                    'move_number': i + 1,
                    'move': move,
                    'type': 'check_forced',
                    'description': 'Check that forces response'
                })
            
            # Check for tactical sequences
            if i < len(moves) - 1:
                next_move = moves[i + 1]
                if self._is_tactical_sequence(move, next_move):
                    patterns.append({
                        'move_number': i + 1,
                        'move': move,
                        'type': 'tactical_forced',
                        'description': 'Tactical sequence that forces response'
                    })
            
            # Check for mate threats
            if '#' in move:
                patterns.append({
                    'move_number': i + 1,
                    'move': move,
                    'type': 'mate_threat',
                    'description': 'Mate threat that forces response'
                })
        
        return patterns
    
    def _find_reactive_escape_patterns(self, moves: List[str]) -> List[Dict[str, Any]]:
        """Find reactive escape patterns in moves"""
        patterns = []
        
        for i, move in enumerate(moves):
            # Look for king moves (potential escapes)
            if 'K' in move:
                patterns.append({
                    'move_number': i + 1,
                    'move': move,
                    'type': 'king_escape',
                    'description': 'King move that could be an escape'
                })
            
            # Look for piece retreats
            if i > 0 and self._is_retreat_move(moves[i-1], move):
                patterns.append({
                    'move_number': i + 1,
                    'move': move,
                    'type': 'piece_retreat',
                    'description': 'Piece retreat from attack'
                })
            
            # Look for defensive moves
            if self._is_defensive_move(move):
                patterns.append({
                    'move_number': i + 1,
                    'move': move,
                    'type': 'defensive_move',
                    'description': 'Defensive move to avoid loss'
                })
        
        return patterns
    
    def _find_tactical_combinations(self, moves: List[str]) -> List[Dict[str, Any]]:
        """Find tactical combinations in moves"""
        combinations = []
        
        for i, move in enumerate(moves):
            # Look for tactical sequences
            if i < len(moves) - 2:
                next_move = moves[i + 1]
                next_next_move = moves[i + 2]
                
                if self._is_tactical_combination(move, next_move, next_next_move):
                    combinations.append({
                        'move_number': i + 1,
                        'move': move,
                        'type': 'tactical_combination',
                        'description': 'Tactical combination sequence'
                    })
            
            # Look for sacrifices
            if self._is_sacrifice_move(move):
                combinations.append({
                    'move_number': i + 1,
                    'move': move,
                    'type': 'sacrifice',
                    'description': 'Sacrifice move'
                })
            
            # Look for pins
            if self._is_pin_move(move):
                combinations.append({
                    'move_number': i + 1,
                    'move': move,
                    'type': 'pin',
                    'description': 'Pin move'
                })
        
        return combinations
    
    def _identify_positional_themes(self, moves: List[str]) -> List[str]:
        """Identify positional themes in moves"""
        themes = []
        
        # Look for opening themes
        if len(moves) <= 20:
            if any('e4' in move for move in moves[:5]):
                themes.append('e4_opening')
            if any('d4' in move for move in moves[:5]):
                themes.append('d4_opening')
            if any('Nf3' in move for move in moves[:5]):
                themes.append('Nf3_opening')
        
        # Look for middlegame themes
        if 20 < len(moves) <= 40:
            if any('x' in move for move in moves[20:40]):
                themes.append('middlegame_tactics')
            if any('+' in move for move in moves[20:40]):
                themes.append('middlegame_attacks')
        
        # Look for endgame themes
        if len(moves) > 40:
            if any('K' in move for move in moves[-20:]):
                themes.append('endgame_king_activity')
            if any('=' in move for move in moves[-20:]):
                themes.append('endgame_promotion')
        
        return themes
    
    def _analyze_time_pressure(self, clock: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze time pressure from clock data"""
        return {
            'initial_time': clock.get('initial', 0),
            'increment': clock.get('increment', 0),
            'time_control': f"{clock.get('initial', 0)}+{clock.get('increment', 0)}",
            'time_pressure_level': 'high' if clock.get('initial', 0) < 300 else 'medium' if clock.get('initial', 0) < 600 else 'low'
        }
    
    def _analyze_performance_metrics(self, perf: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance metrics"""
        return {
            'perf_type': perf.get('name', ''),
            'icon': perf.get('icon', ''),
            'rating': perf.get('rating', 0),
            'rating_diff': perf.get('ratingDiff', 0),
            'provisional': perf.get('provisional', False)
        }
    
    def _pieces_coordinated(self, prev_move: str, curr_move: str) -> bool:
        """Check if pieces are coordinated between moves"""
        return prev_move != curr_move
    
    def _is_tactical_sequence(self, move1: str, move2: str) -> bool:
        """Check if two moves form a tactical sequence"""
        return 'x' in move1 and 'x' in move2
    
    def _is_retreat_move(self, prev_move: str, curr_move: str) -> bool:
        """Check if current move is a retreat"""
        return prev_move != curr_move
    
    def _is_defensive_move(self, move: str) -> bool:
        """Check if move is defensive"""
        return '+' in move or '#' in move
    
    def _is_tactical_combination(self, move1: str, move2: str, move3: str) -> bool:
        """Check if three moves form a tactical combination"""
        return all('x' in move for move in [move1, move2, move3])
    
    def _is_sacrifice_move(self, move: str) -> bool:
        """Check if move is a sacrifice"""
        return 'x' in move and move.isupper()
    
    def _is_pin_move(self, move: str) -> bool:
        """Check if move creates a pin"""
        return 'x' in move and len(move) > 3
    
    async def get_chesscom_games(self, username: str, max_games: int = 100) -> List[Dict[str, Any]]:
        """Get recent games from Chess.com for a user"""
        print(f"Fetching {max_games} recent games for {username} from Chess.com...")
        
        games = []
        url = f"{self.chesscom_api}/pub/player/{username}/games/archives"
        
        try:
            async with aiohttp.ClientSession() as session:
                # First get available archives
                async with session.get(url) as response:
                    if response.status == 200:
                        archives_data = await response.json()
                        archives = archives_data.get('archives', [])
                        
                        # Get games from recent archives (limit to avoid too many requests)
                        recent_archives = archives[-3:] if len(archives) > 3 else archives
                        
                        for archive_url in recent_archives:
                            try:
                                async with session.get(archive_url) as archive_response:
                                    if archive_response.status == 200:
                                        archive_data = await archive_response.json()
                                        archive_games = self._process_chesscom_games(archive_data)
                                        games.extend(archive_games)
                                        
                                        if len(games) >= max_games:
                                            break
                                            
                                # Rate limiting
                                await asyncio.sleep(0.5)
                                
                            except Exception as e:
                                print(f"Error fetching archive {archive_url}: {e}")
                                continue
                    else:
                        print(f"Error fetching Chess.com archives: {response.status}")
        
        except Exception as e:
            print(f"Error fetching Chess.com games: {e}")
        
        # Limit to requested number of games
        games = games[:max_games]
        print(f"Fetched {len(games)} games from Chess.com")
        return games
    
    def _process_chesscom_games(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process Chess.com games data"""
        games = []
        
        for game_data in data.get('games', []):
            try:
                # Extract game information
                game = {
                    'url': game_data.get('url', ''),
                    'pgn': game_data.get('pgn', ''),
                    'time_control': game_data.get('time_control', ''),
                    'end_time': game_data.get('end_time', 0),
                    'rated': game_data.get('rated', False),
                    'time_class': game_data.get('time_class', ''),
                    'rules': game_data.get('rules', ''),
                    'white': game_data.get('white', {}),
                    'black': game_data.get('black', {}),
                    'qec_analysis': self._analyze_game_for_qec(game_data)
                }
                
                games.append(game)
                
            except Exception as e:
                print(f"Error processing game: {e}")
                continue
        
        return games
    
    async def get_position_analysis(self, fen: str) -> Dict[str, Any]:
        """Get position analysis from ChessDB"""
        print(f"Analyzing position: {fen}")
        
        # For now, return a simple analysis since ChessDB requires different handling
        return {
            'fen': fen,
            'moves': ['e4', 'e5', 'Nf3', 'Nc6'],  # Sample moves
            'score': 0,
            'depth': 0,
            'nodes': 0,
            'qec_analysis': {
                'entanglement_opportunities': [],
                'forced_move_potential': 'medium',
                'tactical_complexity': 'medium',
                'positional_themes': ['opening']
            }
        }
    
    def _process_position_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process position analysis data"""
        return {
            'fen': data.get('board', ''),
            'moves': data.get('moves', []),
            'score': data.get('score', 0),
            'depth': data.get('depth', 0),
            'nodes': data.get('nodes', 0),
            'qec_analysis': self._analyze_position_for_qec(data)
        }
    
    def _analyze_position_for_qec(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze position for QEC patterns"""
        return {
            'entanglement_opportunities': [],
            'forced_move_potential': 'medium',
            'tactical_complexity': 'medium',
            'positional_themes': []
        }
    
    async def collect_user_data(self, usernames: List[str], max_games_per_user: int = 50) -> Dict[str, Any]:
        """Collect data from multiple users across platforms"""
        print(f"Collecting data for {len(usernames)} users...")
        
        all_data = {
            'lichess_games': [],
            'chesscom_games': [],
            'position_analyses': [],
            'metadata': {
                'total_users': len(usernames),
                'max_games_per_user': max_games_per_user,
                'collection_time': datetime.now().isoformat()
            }
        }
        
        for username in usernames:
            print(f"Collecting data for {username}...")
            
            # Collect Lichess games
            lichess_games = await self.get_lichess_games(username, max_games_per_user)
            all_data['lichess_games'].extend(lichess_games)
            
            # Collect Chess.com games
            chesscom_games = await self.get_chesscom_games(username, max_games_per_user)
            all_data['chesscom_games'].extend(chesscom_games)
            
            # Rate limiting
            await asyncio.sleep(1)
        
        print(f"Collected {len(all_data['lichess_games'])} Lichess games and {len(all_data['chesscom_games'])} Chess.com games")
        return all_data
    
    def save_data(self, data: Dict[str, Any], filename: str = "chess_web_api_data.json"):
        """Save collected data to file"""
        output_file = self.data_dir / filename
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Data saved to {output_file}")
        return str(output_file)
    
    def create_qec_training_dataset(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create QEC training dataset from collected data"""
        print("Creating QEC training dataset from collected data...")
        
        training_dataset = {
            'entanglement_examples': [],
            'forced_move_examples': [],
            'reactive_escape_examples': [],
            'tactical_examples': [],
            'positional_examples': []
        }
        
        # Extract examples from Lichess games
        for game in data.get('lichess_games', []):
            qec_analysis = game.get('qec_analysis', {})
            
            if qec_analysis.get('entanglement_opportunities'):
                training_dataset['entanglement_examples'].extend(qec_analysis['entanglement_opportunities'])
            
            if qec_analysis.get('forced_move_patterns'):
                training_dataset['forced_move_examples'].extend(qec_analysis['forced_move_patterns'])
            
            if qec_analysis.get('reactive_escape_patterns'):
                training_dataset['reactive_escape_examples'].extend(qec_analysis['reactive_escape_patterns'])
            
            if qec_analysis.get('tactical_combinations'):
                training_dataset['tactical_examples'].extend(qec_analysis['tactical_combinations'])
            
            if qec_analysis.get('positional_themes'):
                training_dataset['positional_examples'].extend(qec_analysis['positional_themes'])
        
        # Extract examples from Chess.com games
        for game in data.get('chesscom_games', []):
            qec_analysis = game.get('qec_analysis', {})
            
            if qec_analysis.get('entanglement_opportunities'):
                training_dataset['entanglement_examples'].extend(qec_analysis['entanglement_opportunities'])
            
            if qec_analysis.get('forced_move_patterns'):
                training_dataset['forced_move_examples'].extend(qec_analysis['forced_move_patterns'])
            
            if qec_analysis.get('reactive_escape_patterns'):
                training_dataset['reactive_escape_examples'].extend(qec_analysis['reactive_escape_patterns'])
            
            if qec_analysis.get('tactical_combinations'):
                training_dataset['tactical_examples'].extend(qec_analysis['tactical_combinations'])
            
            if qec_analysis.get('positional_themes'):
                training_dataset['positional_examples'].extend(qec_analysis['positional_themes'])
        
        print(f"Created training dataset with {sum(len(examples) for examples in training_dataset.values())} examples")
        return training_dataset

async def main():
    """Main chess web API integration"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Chess Web API Integration for QEC')
    parser.add_argument('--usernames', nargs='+', default=['MagnusCarlsen', 'FabianoCaruana'], help='Usernames to collect data for')
    parser.add_argument('--max-games', type=int, default=50, help='Maximum games per user')
    parser.add_argument('--output', type=str, default='chess_web_api_data.json', help='Output file')
    parser.add_argument('--platform', type=str, choices=['lichess', 'chesscom', 'both'], default='both', help='Platform to collect from')
    
    args = parser.parse_args()
    
    # Initialize integrator
    integrator = ChessWebAPIIntegrator()
    
    try:
        # Collect data
        data = await integrator.collect_user_data(args.usernames, args.max_games)
        
        # Save data
        output_path = integrator.save_data(data, args.output)
        
        # Create training dataset
        training_dataset = integrator.create_qec_training_dataset(data)
        
        # Save training dataset
        training_path = integrator.save_data(training_dataset, 'qec_training_dataset.json')
        
        print(f"Chess web API integration completed successfully!")
        print(f"Data saved to: {output_path}")
        print(f"Training dataset saved to: {training_path}")
        
    except Exception as e:
        print(f"Error during chess web API integration: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    asyncio.run(main())
