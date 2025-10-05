"""
Tournament System for QEC Human Simulation
Implements various tournament formats with realistic chess tournament structures
"""

import random
import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

from player_database import ChessPlayer, get_tournament_pools
from human_simulation import HumanQECSimulation, GameResult

class TournamentFormat(Enum):
    ROUND_ROBIN = "round_robin"
    SWISS = "swiss"
    KNOCKOUT = "knockout"
    DOUBLE_ELIMINATION = "double_elimination"
    MATCH_PLAY = "match_play"

@dataclass
class TournamentRound:
    round_number: int
    games: List[Tuple[str, str]]  # (white_player, black_player)
    results: List[GameResult]
    completed: bool = False

@dataclass
class TournamentStandings:
    player: str
    games_played: int
    wins: int
    losses: int
    draws: int
    points: float
    tiebreak_score: float
    rating_change: int

@dataclass
class Tournament:
    name: str
    format: TournamentFormat
    players: List[ChessPlayer]
    rounds: List[TournamentRound]
    standings: List[TournamentStandings]
    completed: bool = False
    winner: Optional[str] = None

class TournamentSystem:
    """Tournament management system for QEC human simulation"""
    
    def __init__(self, logs_dir: str = "tournament_logs"):
        self.logs_dir = logs_dir
        self.simulation = HumanQECSimulation(logs_dir)
        self.tournaments = []
        
    def create_round_robin_tournament(self, name: str, players: List[ChessPlayer]) -> Tournament:
        """Create a round robin tournament"""
        if len(players) < 2:
            raise ValueError("Need at least 2 players for tournament")
        
        # Calculate number of rounds
        n = len(players)
        if n % 2 == 0:
            rounds = n - 1
        else:
            rounds = n
        
        tournament = Tournament(
            name=name,
            format=TournamentFormat.ROUND_ROBIN,
            players=players,
            rounds=[],
            standings=[TournamentStandings(p.name, 0, 0, 0, 0, 0.0, 0.0, 0) for p in players]
        )
        
        # Generate round pairings
        for round_num in range(rounds):
            round_games = self._generate_round_robin_pairings(players, round_num)
            tournament.rounds.append(TournamentRound(round_num + 1, round_games, []))
        
        return tournament
    
    def create_swiss_tournament(self, name: str, players: List[ChessPlayer], 
                                rounds: int = None) -> Tournament:
        """Create a Swiss tournament"""
        if len(players) < 4:
            raise ValueError("Need at least 4 players for Swiss tournament")
        
        if rounds is None:
            rounds = math.ceil(math.log2(len(players)))
        
        tournament = Tournament(
            name=name,
            format=TournamentFormat.SWISS,
            players=players,
            rounds=[],
            standings=[TournamentStandings(p.name, 0, 0, 0, 0, 0.0, 0.0, 0) for p in players]
        )
        
        # Generate Swiss pairings for each round
        for round_num in range(rounds):
            round_games = self._generate_swiss_pairings(tournament.standings, round_num)
            tournament.rounds.append(TournamentRound(round_num + 1, round_games, []))
        
        return tournament
    
    def create_knockout_tournament(self, name: str, players: List[ChessPlayer]) -> Tournament:
        """Create a knockout tournament"""
        if len(players) < 2:
            raise ValueError("Need at least 2 players for tournament")
        
        # Ensure number of players is power of 2
        n = len(players)
        if not (n & (n - 1) == 0):
            # Add byes to make it power of 2
            byes_needed = 2 ** math.ceil(math.log2(n)) - n
            for i in range(byes_needed):
                players.append(ChessPlayer(
                    name=f"Bye_{i+1}",
                    rating=0,
                    style=None,
                    strengths=[],
                    weaknesses=[],
                    opening_preferences=[],
                    time_control_preference="classical",
                    aggression_level=0.0,
                    calculation_depth=0,
                    blunder_rate=1.0,
                    tactical_vision=0.0,
                    endgame_strength=0.0,
                    opening_knowledge=0.0
                ))
        
        tournament = Tournament(
            name=name,
            format=TournamentFormat.KNOCKOUT,
            players=players,
            rounds=[],
            standings=[TournamentStandings(p.name, 0, 0, 0, 0, 0.0, 0.0, 0) for p in players]
        )
        
        # Generate knockout brackets
        self._generate_knockout_brackets(tournament)
        
        return tournament
    
    def _generate_round_robin_pairings(self, players: List[ChessPlayer], round_num: int) -> List[Tuple[str, str]]:
        """Generate round robin pairings for a specific round"""
        n = len(players)
        pairings = []
        
        # Rotate players for round robin
        rotated_players = players[round_num:] + players[:round_num]
        
        for i in range(n // 2):
            white = rotated_players[i]
            black = rotated_players[n - 1 - i]
            pairings.append((white.name, black.name))
        
        return pairings
    
    def _generate_swiss_pairings(self, standings: List[TournamentStandings], round_num: int) -> List[Tuple[str, str]]:
        """Generate Swiss pairings for a specific round"""
        # Sort by points, then by tiebreak
        sorted_standings = sorted(standings, key=lambda x: (-x.points, -x.tiebreak_score))
        
        pairings = []
        used_players = set()
        
        for i, player1 in enumerate(sorted_standings):
            if player1.player in used_players:
                continue
            
            # Find best available opponent
            for j, player2 in enumerate(sorted_standings[i+1:], i+1):
                if player2.player in used_players:
                    continue
                
                # Check if they haven't played before (simplified)
                if round_num == 0 or random.random() < 0.8:  # 80% chance of valid pairing
                    pairings.append((player1.player, player2.player))
                    used_players.add(player1.player)
                    used_players.add(player2.player)
                    break
        
        return pairings
    
    def _generate_knockout_brackets(self, tournament: Tournament):
        """Generate knockout tournament brackets"""
        players = tournament.players
        n = len(players)
        rounds_needed = int(math.log2(n))
        
        for round_num in range(rounds_needed):
            games_in_round = n // (2 ** (round_num + 1))
            round_games = []
            
            for game_num in range(games_in_round):
                # Simplified pairing - in real implementation, would track winners
                white_idx = game_num * 2
                black_idx = game_num * 2 + 1
                
                if white_idx < len(players) and black_idx < len(players):
                    round_games.append((players[white_idx].name, players[black_idx].name))
            
            tournament.rounds.append(TournamentRound(round_num + 1, round_games, []))
    
    def run_tournament(self, tournament: Tournament, live: bool = False) -> Tournament:
        """Run a complete tournament"""
        print(f"=== {tournament.name} ===")
        print(f"Format: {tournament.format.value}")
        print(f"Players: {len(tournament.players)}")
        print(f"Rounds: {len(tournament.rounds)}")
        print()
        
        for round_obj in tournament.rounds:
            print(f"Round {round_obj.round_number}:")
            
            for white_name, black_name in round_obj.games:
                if live:
                    print(f"  {white_name} vs {black_name}")
                
                # Get player objects
                white_player = next(p for p in tournament.players if p.name == white_name)
                black_player = next(p for p in tournament.players if p.name == black_name)
                
                # Skip bye games
                if white_player.rating == 0 or black_player.rating == 0:
                    continue
                
                # Play game
                result = self.simulation._simulate_human_game(white_player, black_player)
                round_obj.results.append(result)
                
                if live:
                    print(f"    Result: {result.result}")
                    print(f"    Moves: {result.moves}")
                
                # Update standings
                self._update_standings(tournament, result)
            
            round_obj.completed = True
            
            if live:
                print(f"Round {round_obj.round_number} completed")
                print()
        
        # Determine winner
        tournament.completed = True
        if tournament.standings:
            winner = max(tournament.standings, key=lambda x: (x.points, x.tiebreak_score))
            tournament.winner = winner.player
        
        return tournament
    
    def _update_standings(self, tournament: Tournament, result: GameResult):
        """Update tournament standings after a game"""
        # Find standings entries
        white_standing = next(s for s in tournament.standings if s.player == result.white_player)
        black_standing = next(s for s in tournament.standings if s.player == result.black_player)
        
        # Update games played
        white_standing.games_played += 1
        black_standing.games_played += 1
        
        # Update results and points
        if result.result == "W wins":
            white_standing.wins += 1
            white_standing.points += 1.0
            black_standing.losses += 1
        elif result.result == "B wins":
            black_standing.wins += 1
            black_standing.points += 1.0
            white_standing.losses += 1
        else:  # Draw
            white_standing.draws += 1
            white_standing.points += 0.5
            black_standing.draws += 1
            black_standing.points += 0.5
        
        # Update tiebreak score (simplified)
        white_standing.tiebreak_score += result.moves / 100.0
        black_standing.tiebreak_score += result.moves / 100.0
    
    def print_standings(self, tournament: Tournament):
        """Print tournament standings"""
        if not tournament.standings:
            print("No standings available")
            return
        
        # Sort by points, then by tiebreak
        sorted_standings = sorted(tournament.standings, 
                                key=lambda x: (-x.points, -x.tiebreak_score))
        
        print(f"=== {tournament.name} Standings ===")
        print(f"{'Rank':<4} {'Player':<20} {'Games':<5} {'W':<3} {'L':<3} {'D':<3} {'Points':<6} {'Tiebreak':<8}")
        print("-" * 70)
        
        for i, standing in enumerate(sorted_standings, 1):
            print(f"{i:<4} {standing.player:<20} {standing.games_played:<5} "
                  f"{standing.wins:<3} {standing.losses:<3} {standing.draws:<3} "
                  f"{standing.points:<6.1f} {standing.tiebreak_score:<8.2f}")
        
        if tournament.winner:
            print(f"\nWinner: {tournament.winner}")
    
    def run_world_championship(self, candidates: List[ChessPlayer], 
                             match_length: int = 12) -> Tournament:
        """Run a world championship match"""
        if len(candidates) != 2:
            raise ValueError("World championship needs exactly 2 candidates")
        
        white_player, black_player = candidates
        
        print(f"=== World Championship Match ===")
        print(f"White: {white_player.name} (Rating: {white_player.rating})")
        print(f"Black: {white_player.name} (Rating: {black_player.rating})")
        print(f"Match length: {match_length} games")
        print()
        
        # Create match tournament
        tournament = Tournament(
            name="World Championship Match",
            format=TournamentFormat.MATCH_PLAY,
            players=candidates,
            rounds=[],
            standings=[TournamentStandings(p.name, 0, 0, 0, 0, 0.0, 0.0, 0) for p in candidates]
        )
        
        # Play match games
        for game_num in range(match_length):
            # Alternate colors
            if game_num % 2 == 0:
                white, black = white_player, black_player
            else:
                white, black = black_player, white_player
            
            print(f"Game {game_num + 1}: {white.name} vs {black.name}")
            
            result = self.simulation._simulate_human_game(white, black)
            tournament.standings[0].games_played += 1
            tournament.standings[1].games_played += 1
            
            if result.result == "W wins":
                if white.name == white_player.name:
                    tournament.standings[0].wins += 1
                    tournament.standings[0].points += 1.0
                    tournament.standings[1].losses += 1
                else:
                    tournament.standings[1].wins += 1
                    tournament.standings[1].points += 1.0
                    tournament.standings[0].losses += 1
            elif result.result == "B wins":
                if black.name == white_player.name:
                    tournament.standings[0].wins += 1
                    tournament.standings[0].points += 1.0
                    tournament.standings[1].losses += 1
                else:
                    tournament.standings[1].wins += 1
                    tournament.standings[1].points += 1.0
                    tournament.standings[0].losses += 1
            else:  # Draw
                tournament.standings[0].draws += 1
                tournament.standings[0].points += 0.5
                tournament.standings[1].draws += 1
                tournament.standings[1].points += 0.5
            
            print(f"  Result: {result.result}")
            print(f"  Moves: {result.moves}")
            print()
        
        # Determine winner
        if tournament.standings[0].points > tournament.standings[1].points:
            tournament.winner = white_player.name
        elif tournament.standings[1].points > tournament.standings[0].points:
            tournament.winner = black_player.name
        else:
            tournament.winner = "Tie"
        
        tournament.completed = True
        return tournament
    
    def run_candidates_tournament(self, players: List[ChessPlayer]) -> Tournament:
        """Run a candidates tournament to determine world championship challenger"""
        if len(players) < 4:
            raise ValueError("Candidates tournament needs at least 4 players")
        
        # Create double round robin
        tournament = self.create_round_robin_tournament("Candidates Tournament", players)
        
        # Double the rounds for double round robin
        original_rounds = tournament.rounds.copy()
        for round_obj in original_rounds:
            new_round = TournamentRound(
                round_obj.round_number + len(original_rounds),
                round_obj.games,
                []
            )
            tournament.rounds.append(new_round)
        
        return tournament

if __name__ == "__main__":
    # Test the tournament system
    from player_database import get_tournament_pools
    
    print("=== QEC Tournament System ===")
    
    # Get player pools
    pools = get_tournament_pools()
    
    # Test round robin tournament
    print("Testing Round Robin Tournament...")
    system = TournamentSystem()
    
    # Use a small pool for testing
    test_players = pools["mixed"][:4]  # Take first 4 players
    
    tournament = system.create_round_robin_tournament("Test Tournament", test_players)
    tournament = system.run_tournament(tournament, live=True)
    system.print_standings(tournament)
    
    print("\n" + "="*50)
    
    # Test world championship match
    print("Testing World Championship Match...")
    candidates = [pools["super_gm"][0], pools["super_gm"][1]]  # Top 2 super GMs
    match = system.run_world_championship(candidates, match_length=4)
    system.print_standings(match)
