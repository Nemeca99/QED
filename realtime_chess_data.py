"""
Real-time Chess Data Collection
Collect real-time chess data using working APIs
"""

import asyncio
import aiohttp
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

class RealTimeChessDataCollector:
    """Collect real-time chess data from working APIs"""
    
    def __init__(self, data_dir: str = "data/realtime_chess"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Working API endpoints
        self.chesscom_api = "https://api.chess.com"
        self.lichess_puzzles_api = "https://lichess.org/api/puzzle"
        self.lichess_tournaments_api = "https://lichess.org/api/tournament"
        
    async def collect_chesscom_games(self, username: str, max_games: int = 20) -> dict:
        """Collect games from Chess.com"""
        print(f"Collecting {max_games} games for {username} from Chess.com...")
        
        games_data = {
            'username': username,
            'games': [],
            'total_games': 0,
            'collection_time': datetime.now().isoformat()
        }
        
        try:
            # Get archives
            archives_url = f"{self.chesscom_api}/pub/player/{username}/games/archives"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(archives_url) as response:
                    if response.status == 200:
                        archives_data = await response.json()
                        archives = archives_data.get('archives', [])
                        
                        # Get games from recent archives
                        recent_archives = archives[-3:] if len(archives) > 3 else archives
                        
                        for archive_url in recent_archives:
                            try:
                                async with session.get(archive_url) as archive_response:
                                    if archive_response.status == 200:
                                        archive_data = await archive_response.json()
                                        games = archive_data.get('games', [])
                                        
                                        for game in games:
                                            if len(games_data['games']) >= max_games:
                                                break
                                            
                                            # Process game for QEC analysis
                                            processed_game = self._process_chesscom_game(game)
                                            games_data['games'].append(processed_game)
                                        
                                        if len(games_data['games']) >= max_games:
                                            break
                                            
                                # Rate limiting
                                await asyncio.sleep(0.5)
                                
                            except Exception as e:
                                print(f"Error fetching archive {archive_url}: {e}")
                                continue
                        
                        games_data['total_games'] = len(games_data['games'])
                        print(f"✅ Collected {games_data['total_games']} games from Chess.com")
                        
                    else:
                        print(f"❌ Error fetching archives: {response.status}")
                        
        except Exception as e:
            print(f"❌ Error collecting Chess.com games: {e}")
        
        return games_data
    
    def _process_chesscom_game(self, game: dict) -> dict:
        """Process Chess.com game for QEC analysis"""
        # Extract basic game info
        processed_game = {
            'id': game.get('url', '').split('/')[-1] if game.get('url') else '',
            'url': game.get('url', ''),
            'white': game.get('white', {}),
            'black': game.get('black', {}),
            'result': game.get('result', ''),
            'time_control': game.get('time_control', ''),
            'time_class': game.get('time_class', ''),
            'rated': game.get('rated', False),
            'rules': game.get('rules', ''),
            'fen': game.get('fen', ''),
            'pgn': game.get('pgn', ''),
            'end_time': game.get('end_time', 0),
            'qec_analysis': self._analyze_game_for_qec(game)
        }
        
        return processed_game
    
    def _analyze_game_for_qec(self, game: dict) -> dict:
        """Analyze game for QEC patterns"""
        analysis = {
            'entanglement_opportunities': [],
            'forced_move_patterns': [],
            'reactive_escape_patterns': [],
            'tactical_combinations': [],
            'positional_themes': [],
            'time_pressure': self._analyze_time_pressure(game),
            'performance_metrics': self._analyze_performance_metrics(game)
        }
        
        # Analyze PGN for patterns
        pgn = game.get('pgn', '')
        if pgn:
            moves = self._extract_moves_from_pgn(pgn)
            analysis.update(self._analyze_moves_for_qec(moves))
        
        return analysis
    
    def _extract_moves_from_pgn(self, pgn: str) -> list:
        """Extract moves from PGN"""
        moves = []
        lines = pgn.split('\n')
        
        for line in lines:
            if line.strip() and not line.startswith('['):
                # Split by spaces and filter out move numbers
                move_parts = line.strip().split()
                for part in move_parts:
                    if '.' not in part and part not in ['1-0', '0-1', '1/2-1/2']:
                        moves.append(part)
        
        return moves
    
    def _analyze_moves_for_qec(self, moves: list) -> dict:
        """Analyze moves for QEC patterns"""
        analysis = {
            'entanglement_opportunities': [],
            'forced_move_patterns': [],
            'reactive_escape_patterns': [],
            'tactical_combinations': [],
            'positional_themes': []
        }
        
        for i, move in enumerate(moves):
            # Look for captures (entanglement opportunities)
            if 'x' in move:
                analysis['entanglement_opportunities'].append({
                    'move_number': i + 1,
                    'move': move,
                    'type': 'capture_entanglement',
                    'description': 'Capture move that could create entanglement'
                })
            
            # Look for checks (forced responses)
            if '+' in move or '#' in move:
                analysis['forced_move_patterns'].append({
                    'move_number': i + 1,
                    'move': move,
                    'type': 'check_forced',
                    'description': 'Check that forces response'
                })
            
            # Look for king moves (reactive escapes)
            if 'K' in move:
                analysis['reactive_escape_patterns'].append({
                    'move_number': i + 1,
                    'move': move,
                    'type': 'king_escape',
                    'description': 'King move that could be an escape'
                })
            
            # Look for tactical sequences
            if i < len(moves) - 1 and 'x' in move and 'x' in moves[i + 1]:
                analysis['tactical_combinations'].append({
                    'move_number': i + 1,
                    'move': move,
                    'type': 'tactical_sequence',
                    'description': 'Tactical sequence detected'
                })
        
        # Identify positional themes
        if len(moves) <= 20:
            analysis['positional_themes'].append('opening_phase')
        elif len(moves) <= 40:
            analysis['positional_themes'].append('middlegame_phase')
        else:
            analysis['positional_themes'].append('endgame_phase')
        
        return analysis
    
    def _analyze_time_pressure(self, game: dict) -> dict:
        """Analyze time pressure from game data"""
        time_control = game.get('time_control', '')
        time_class = game.get('time_class', '')
        
        return {
            'time_control': time_control,
            'time_class': time_class,
            'time_pressure_level': 'high' if 'blitz' in time_class else 'medium' if 'rapid' in time_class else 'low'
        }
    
    def _analyze_performance_metrics(self, game: dict) -> dict:
        """Analyze performance metrics"""
        return {
            'time_class': game.get('time_class', ''),
            'rated': game.get('rated', False),
            'rules': game.get('rules', ''),
            'result': game.get('result', '')
        }
    
    async def collect_lichess_puzzles(self, max_puzzles: int = 10) -> dict:
        """Collect puzzles from Lichess"""
        print(f"Collecting {max_puzzles} puzzles from Lichess...")
        
        puzzles_data = {
            'puzzles': [],
            'total_puzzles': 0,
            'collection_time': datetime.now().isoformat()
        }
        
        try:
            # Get daily puzzle
            daily_url = f"{self.lichess_puzzles_api}/daily"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(daily_url) as response:
                    if response.status == 200:
                        puzzle_data = await response.json()
                        
                        # Process daily puzzle
                        processed_puzzle = self._process_lichess_puzzle(puzzle_data)
                        puzzles_data['puzzles'].append(processed_puzzle)
                        
                        # Get more puzzles from the database
                        for i in range(max_puzzles - 1):
                            try:
                                puzzle_id = f"puzzle_{i + 1}"
                                puzzle_url = f"{self.lichess_puzzles_api}/{puzzle_id}"
                                
                                async with session.get(puzzle_url) as puzzle_response:
                                    if puzzle_response.status == 200:
                                        puzzle = await puzzle_response.json()
                                        processed_puzzle = self._process_lichess_puzzle(puzzle)
                                        puzzles_data['puzzles'].append(processed_puzzle)
                                    
                                # Rate limiting
                                await asyncio.sleep(0.5)
                                
                            except Exception as e:
                                print(f"Error fetching puzzle {i + 1}: {e}")
                                continue
                        
                        puzzles_data['total_puzzles'] = len(puzzles_data['puzzles'])
                        print(f"✅ Collected {puzzles_data['total_puzzles']} puzzles from Lichess")
                        
                    else:
                        print(f"❌ Error fetching daily puzzle: {response.status}")
                        
        except Exception as e:
            print(f"❌ Error collecting Lichess puzzles: {e}")
        
        return puzzles_data
    
    def _process_lichess_puzzle(self, puzzle_data: dict) -> dict:
        """Process Lichess puzzle for QEC analysis"""
        puzzle = puzzle_data.get('puzzle', {})
        
        return {
            'id': puzzle.get('id', ''),
            'rating': puzzle.get('rating', 0),
            'themes': puzzle.get('themes', []),
            'fen': puzzle.get('fen', ''),
            'moves': puzzle.get('moves', []),
            'qec_analysis': self._analyze_puzzle_for_qec(puzzle)
        }
    
    def _analyze_puzzle_for_qec(self, puzzle: dict) -> dict:
        """Analyze puzzle for QEC patterns"""
        return {
            'entanglement_opportunities': [],
            'forced_move_patterns': [],
            'tactical_combinations': [],
            'difficulty_level': 'easy' if puzzle.get('rating', 0) < 1500 else 'medium' if puzzle.get('rating', 0) < 2000 else 'hard',
            'themes': puzzle.get('themes', [])
        }
    
    async def collect_lichess_tournaments(self) -> dict:
        """Collect tournament data from Lichess"""
        print("Collecting tournament data from Lichess...")
        
        tournaments_data = {
            'tournaments': [],
            'total_tournaments': 0,
            'collection_time': datetime.now().isoformat()
        }
        
        try:
            url = f"{self.lichess_tournaments_api}"
            params = {'nb': 10}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        tournaments = data.get('featured', [])
                        
                        for tournament in tournaments:
                            processed_tournament = self._process_lichess_tournament(tournament)
                            tournaments_data['tournaments'].append(processed_tournament)
                        
                        tournaments_data['total_tournaments'] = len(tournaments_data['tournaments'])
                        print(f"✅ Collected {tournaments_data['total_tournaments']} tournaments from Lichess")
                        
                    else:
                        print(f"❌ Error fetching tournaments: {response.status}")
                        
        except Exception as e:
            print(f"❌ Error collecting Lichess tournaments: {e}")
        
        return tournaments_data
    
    def _process_lichess_tournament(self, tournament: dict) -> dict:
        """Process Lichess tournament for QEC analysis"""
        return {
            'id': tournament.get('id', ''),
            'name': tournament.get('fullName', ''),
            'status': tournament.get('status', ''),
            'players': tournament.get('nbPlayers', 0),
            'clock': tournament.get('clock', {}),
            'rated': tournament.get('rated', False),
            'variant': tournament.get('variant', {}),
            'qec_analysis': {
                'time_pressure': 'high' if tournament.get('clock', {}).get('initial', 0) < 300 else 'medium',
                'player_count': tournament.get('nbPlayers', 0),
                'tournament_type': tournament.get('variant', {}).get('name', '')
            }
        }
    
    async def collect_all_data(self, usernames: list = None, max_games_per_user: int = 10) -> dict:
        """Collect all available chess data"""
        if usernames is None:
            usernames = ["MagnusCarlsen", "Hikaru", "FabianoCaruana"]
        
        print("🚀 Starting real-time chess data collection...")
        print("=" * 60)
        
        all_data = {
            'chesscom_games': [],
            'lichess_puzzles': [],
            'lichess_tournaments': [],
            'metadata': {
                'collection_time': datetime.now().isoformat(),
                'total_sources': 3,
                'usernames': usernames
            }
        }
        
        # Collect Chess.com games
        for username in usernames:
            print(f"\n📊 Collecting Chess.com data for {username}...")
            games_data = await self.collect_chesscom_games(username, max_games_per_user)
            all_data['chesscom_games'].append(games_data)
            
            # Rate limiting between users
            await asyncio.sleep(1)
        
        # Collect Lichess puzzles
        print(f"\n🧩 Collecting Lichess puzzles...")
        puzzles_data = await self.collect_lichess_puzzles(10)
        all_data['lichess_puzzles'] = puzzles_data
        
        # Collect Lichess tournaments
        print(f"\n🏆 Collecting Lichess tournaments...")
        tournaments_data = await self.collect_lichess_tournaments()
        all_data['lichess_tournaments'] = tournaments_data
        
        # Save all data
        output_file = self.data_dir / "realtime_chess_data.json"
        with open(output_file, 'w') as f:
            json.dump(all_data, f, indent=2)
        
        print(f"\n💾 Data saved to: {output_file}")
        
        # Print summary
        total_games = sum(len(user_data['games']) for user_data in all_data['chesscom_games'])
        total_puzzles = all_data['lichess_puzzles']['total_puzzles']
        total_tournaments = all_data['lichess_tournaments']['total_tournaments']
        
        print(f"\n📈 Collection Summary:")
        print(f"  Chess.com games: {total_games}")
        print(f"  Lichess puzzles: {total_puzzles}")
        print(f"  Lichess tournaments: {total_tournaments}")
        print(f"  Total data points: {total_games + total_puzzles + total_tournaments}")
        
        return all_data

async def main():
    """Main real-time data collection"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Real-time Chess Data Collection')
    parser.add_argument('--usernames', nargs='+', default=['MagnusCarlsen', 'Hikaru'], help='Usernames to collect data for')
    parser.add_argument('--max-games', type=int, default=10, help='Maximum games per user')
    parser.add_argument('--output', type=str, default='realtime_chess_data.json', help='Output file')
    
    args = parser.parse_args()
    
    # Initialize collector
    collector = RealTimeChessDataCollector()
    
    try:
        # Collect all data
        data = await collector.collect_all_data(args.usernames, args.max_games)
        
        print("\n🎉 Real-time chess data collection completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during data collection: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
