"""
Comprehensive QEC Human Simulation System
Complete simulation framework with real player profiles, tournaments, and statistics
"""

import os
import json
import time
import random
import argparse
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict

from player_database import ChessPlayer, get_tournament_pools, get_player_by_name
from human_simulation import HumanQECSimulation, GameResult
from tournament_system import TournamentSystem, TournamentFormat
from opening_book import get_opening_by_style, get_opening_by_rating

@dataclass
class SimulationConfig:
    """Configuration for comprehensive simulation"""
    white_player: str
    black_player: str
    num_games: int
    tournament_format: str
    player_pool: str
    logs_dir: str
    seed_base: int
    max_moves: int
    live_details: bool
    infinite: bool
    save_logs: bool

class ComprehensiveSimulator:
    """Complete QEC simulation system with human-like players"""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.simulation = HumanQECSimulation(config.logs_dir, config.max_moves)
        self.tournament_system = TournamentSystem(config.logs_dir)
        self.results = []
        self.statistics = {}
        
        # Create logs directory
        os.makedirs(config.logs_dir, exist_ok=True)
        
    def run_single_match(self) -> GameResult:
        """Run a single match between two players"""
        white_player = get_player_by_name(self.config.white_player)
        black_player = get_player_by_name(self.config.black_player)
        
        if not white_player:
            raise ValueError(f"Player not found: {self.config.white_player}")
        if not black_player:
            raise ValueError(f"Player not found: {self.config.black_player}")
        
        print(f"=== QEC Single Match ===")
        print(f"White: {white_player.name} (Rating: {white_player.rating}, Style: {white_player.style.value})")
        print(f"Black: {black_player.name} (Rating: {black_player.rating}, Style: {black_player.style.value})")
        print(f"Seed: {self.config.seed_base}")
        print()
        
        result = self.simulation._simulate_human_game(white_player, black_player, self.config.seed_base)
        self.results.append(result)
        
        if self.config.save_logs:
            self.simulation._save_game_logs(result)
        
        return result
    
    def run_multiple_games(self) -> List[GameResult]:
        """Run multiple games between the same two players"""
        white_player = get_player_by_name(self.config.white_player)
        black_player = get_player_by_name(self.config.black_player)
        
        if not white_player:
            raise ValueError(f"Player not found: {self.config.white_player}")
        if not black_player:
            raise ValueError(f"Player not found: {self.config.black_player}")
        
        print(f"=== QEC Multiple Games ===")
        print(f"White: {white_player.name} (Rating: {white_player.rating})")
        print(f"Black: {black_player.name} (Rating: {black_player.rating})")
        print(f"Games: {self.config.num_games}")
        print()
        
        results = []
        
        for game_num in range(self.config.num_games):
            seed = self.config.seed_base + game_num
            print(f"Game {game_num + 1}/{self.config.num_games} (Seed: {seed})")
            
            result = self.simulation._simulate_human_game(white_player, black_player, seed)
            results.append(result)
            
            if self.config.save_logs:
                self.simulation.game_count = game_num
                self.simulation._save_game_logs(result)
            
            print(f"  Result: {result.result}")
            print(f"  Moves: {result.moves}")
            print(f"  Duration: {result.duration:.2f}s")
            print()
        
        self.results.extend(results)
        return results
    
    def run_tournament(self) -> List[GameResult]:
        """Run a tournament with specified format and player pool"""
        if self.config.player_pool not in get_tournament_pools():
            raise ValueError(f"Unknown player pool: {self.config.player_pool}")
        
        players = get_tournament_pools()[self.config.player_pool]
        
        print(f"=== QEC Tournament ===")
        print(f"Format: {self.config.tournament_format}")
        print(f"Pool: {self.config.player_pool} ({len(players)} players)")
        print()
        
        # Create tournament based on format
        if self.config.tournament_format == "round_robin":
            tournament = self.tournament_system.create_round_robin_tournament(
                f"{self.config.player_pool} Tournament", players
            )
        elif self.config.tournament_format == "swiss":
            tournament = self.tournament_system.create_swiss_tournament(
                f"{self.config.player_pool} Swiss", players
            )
        elif self.config.tournament_format == "knockout":
            tournament = self.tournament_system.create_knockout_tournament(
                f"{self.config.player_pool} Knockout", players
            )
        else:
            raise ValueError(f"Unknown tournament format: {self.config.tournament_format}")
        
        # Run tournament
        tournament = self.tournament_system.run_tournament(tournament, live=True)
        
        # Print standings
        self.tournament_system.print_standings(tournament)
        
        # Collect results
        results = []
        for round_obj in tournament.rounds:
            results.extend(round_obj.results)
        
        self.results.extend(results)
        return results
    
    def run_world_championship(self) -> List[GameResult]:
        """Run a world championship match"""
        # Get top 2 players from super GM pool
        super_gms = get_tournament_pools()["super_gm"]
        if len(super_gms) < 2:
            raise ValueError("Need at least 2 super GMs for world championship")
        
        candidates = super_gms[:2]
        
        print(f"=== QEC World Championship ===")
        print(f"Challenger: {candidates[0].name} (Rating: {candidates[0].rating})")
        print(f"Champion: {candidates[1].name} (Rating: {candidates[1].rating})")
        print(f"Match length: {self.config.num_games} games")
        print()
        
        # Run world championship match
        tournament = self.tournament_system.run_world_championship(candidates, self.config.num_games)
        
        # Print standings
        self.tournament_system.print_standings(tournament)
        
        # Collect results
        results = []
        for round_obj in tournament.rounds:
            results.extend(round_obj.results)
        
        self.results.extend(results)
        return results
    
    def run_infinite_simulation(self):
        """Run infinite simulation with random player pairings"""
        pools = get_tournament_pools()
        all_players = []
        for pool_players in pools.values():
            all_players.extend(pool_players)
        
        print(f"=== QEC Infinite Simulation ===")
        print(f"Total players: {len(all_players)}")
        print(f"Logs directory: {self.config.logs_dir}")
        print()
        
        game_count = 0
        
        try:
            while True:
                # Randomly select two players
                white_player, black_player = random.sample(all_players, 2)
                seed = self.config.seed_base + game_count
                
                print(f"Game {game_count + 1}: {white_player.name} vs {black_player.name}")
                
                result = self.simulation._simulate_human_game(white_player, black_player, seed)
                self.results.append(result)
                
                if self.config.save_logs:
                    # Increment internal counter for unique names
                    self.simulation.game_count = game_count
                    self.simulation._save_game_logs(result)
                
                print(f"  Result: {result.result}")
                print(f"  Moves: {result.moves}")
                print(f"  Duration: {result.duration:.2f}s")
                print()
                
                game_count += 1
                
        except KeyboardInterrupt:
            print(f"\nSimulation stopped after {game_count} games")
            print(f"Results saved to {self.config.logs_dir}")
    
    def analyze_results(self, results: List[GameResult] = None):
        """Analyze simulation results"""
        if results is None:
            results = self.results
        
        if not results:
            print("No results to analyze")
            return
        
        print("=== Comprehensive Analysis ===")
        print(f"Total games: {len(results)}")
        
        # Basic statistics
        total_moves = sum(r.moves for r in results)
        total_forced = sum(r.forced_moves for r in results)
        total_reactive = sum(r.reactive_moves for r in results)
        total_captures = sum(r.captures for r in results)
        total_entanglement_breaks = sum(r.entanglement_breaks for r in results)
        
        print(f"Total moves: {total_moves}")
        print(f"Total forced moves: {total_forced}")
        print(f"Total reactive moves: {total_reactive}")
        print(f"Total captures: {total_captures}")
        print(f"Total entanglement breaks: {total_entanglement_breaks}")
        
        # Result distribution
        results_dist = defaultdict(int)
        for result in results:
            results_dist[result.result] += 1
        
        print(f"\nResult distribution:")
        for result, count in results_dist.items():
            percentage = count / len(results) * 100
            print(f"  {result}: {count} ({percentage:.1f}%)")
        
        # Player statistics
        player_stats = defaultdict(lambda: {
            "wins": 0, "losses": 0, "draws": 0, "games": 0,
            "total_moves": 0, "avg_moves": 0.0, "win_rate": 0.0
        })
        
        for result in results:
            # White player stats
            player_stats[result.white_player]["games"] += 1
            player_stats[result.white_player]["total_moves"] += result.moves
            if result.result == "W wins":
                player_stats[result.white_player]["wins"] += 1
            elif result.result == "B wins":
                player_stats[result.white_player]["losses"] += 1
            else:
                player_stats[result.white_player]["draws"] += 1
            
            # Black player stats
            player_stats[result.black_player]["games"] += 1
            player_stats[result.black_player]["total_moves"] += result.moves
            if result.result == "B wins":
                player_stats[result.black_player]["wins"] += 1
            elif result.result == "W wins":
                player_stats[result.black_player]["losses"] += 1
            else:
                player_stats[result.black_player]["draws"] += 1
        
        # Calculate averages and win rates
        for player, stats in player_stats.items():
            if stats["games"] > 0:
                stats["avg_moves"] = stats["total_moves"] / stats["games"]
                stats["win_rate"] = stats["wins"] / stats["games"] * 100
        
        # Print player statistics
        print(f"\nPlayer Statistics:")
        print(f"{'Player':<20} {'Games':<5} {'Wins':<5} {'Losses':<5} {'Draws':<5} {'Win%':<6} {'Avg Moves':<8}")
        print("-" * 80)
        
        sorted_players = sorted(player_stats.items(), key=lambda x: x[1]["win_rate"], reverse=True)
        for player, stats in sorted_players:
            print(f"{player:<20} {stats['games']:<5} {stats['wins']:<5} "
                  f"{stats['losses']:<5} {stats['draws']:<5} {stats['win_rate']:<6.1f} "
                  f"{stats['avg_moves']:<8.1f}")
        
        # Style analysis
        style_stats = defaultdict(lambda: {"wins": 0, "losses": 0, "draws": 0, "games": 0})
        
        for result in results:
            # Get player styles
            white_player = get_player_by_name(result.white_player)
            black_player = get_player_by_name(result.black_player)
            
            if white_player and black_player:
                # White player style
                style_stats[white_player.style.value]["games"] += 1
                if result.result == "W wins":
                    style_stats[white_player.style.value]["wins"] += 1
                elif result.result == "B wins":
                    style_stats[white_player.style.value]["losses"] += 1
                else:
                    style_stats[white_player.style.value]["draws"] += 1
                
                # Black player style
                style_stats[black_player.style.value]["games"] += 1
                if result.result == "B wins":
                    style_stats[black_player.style.value]["wins"] += 1
                elif result.result == "W wins":
                    style_stats[black_player.style.value]["losses"] += 1
                else:
                    style_stats[black_player.style.value]["draws"] += 1
        
        # Print style statistics
        print(f"\nStyle Statistics:")
        print(f"{'Style':<15} {'Games':<5} {'Wins':<5} {'Losses':<5} {'Draws':<5} {'Win%':<6}")
        print("-" * 60)
        
        for style, stats in style_stats.items():
            if stats["games"] > 0:
                win_rate = stats["wins"] / stats["games"] * 100
                print(f"{style:<15} {stats['games']:<5} {stats['wins']:<5} "
                      f"{stats['losses']:<5} {stats['draws']:<5} {win_rate:<6.1f}")
        
        # Save statistics to file
        stats_file = os.path.join(self.config.logs_dir, "simulation_statistics.json")
        with open(stats_file, 'w') as f:
            json.dump({
                "total_games": len(results),
                "result_distribution": dict(results_dist),
                "player_statistics": {k: dict(v) for k, v in player_stats.items()},
                "style_statistics": {k: dict(v) for k, v in style_stats.items()}
            }, f, indent=2)
        
        print(f"\nStatistics saved to: {stats_file}")

def main():
    """Main function for comprehensive simulation"""
    parser = argparse.ArgumentParser(description="QEC Comprehensive Human Simulation")
    
    # Player selection
    parser.add_argument("--white", type=str, default="Magnus Carlsen", help="White player name")
    parser.add_argument("--black", type=str, default="Fabiano Caruana", help="Black player name")
    
    # Simulation type
    parser.add_argument("--type", type=str, default="single", 
                       choices=["single", "multiple", "tournament", "world_championship", "infinite"],
                       help="Simulation type")
    
    # Tournament options
    parser.add_argument("--tournament_format", type=str, default="round_robin",
                       choices=["round_robin", "swiss", "knockout"],
                       help="Tournament format")
    parser.add_argument("--player_pool", type=str, default="mixed",
                       help="Player pool for tournaments")
    
    # Game options
    parser.add_argument("--games", type=int, default=1, help="Number of games to play")
    parser.add_argument("--max_moves", type=int, default=200, help="Maximum moves per game")
    parser.add_argument("--seed_base", type=int, default=42, help="Base seed for games")
    
    # Output options
    parser.add_argument("--logs_dir", type=str, default="comprehensive_logs", help="Logs directory")
    parser.add_argument("--live_details", action="store_true", help="Show live move details")
    parser.add_argument("--save_logs", action="store_true", help="Save game logs to files")
    
    args = parser.parse_args()
    
    # Create configuration
    config = SimulationConfig(
        white_player=args.white,
        black_player=args.black,
        num_games=args.games,
        tournament_format=args.tournament_format,
        player_pool=args.player_pool,
        logs_dir=args.logs_dir,
        seed_base=args.seed_base,
        max_moves=args.max_moves,
        live_details=args.live_details,
        infinite=False,
        save_logs=args.save_logs
    )
    
    # Create simulator
    simulator = ComprehensiveSimulator(config)
    
    # Run simulation based on type
    if args.type == "single":
        result = simulator.run_single_match()
        print(f"\nResult: {result.result}")
        print(f"Moves: {result.moves}")
        print(f"Duration: {result.duration:.2f}s")
        
    elif args.type == "multiple":
        results = simulator.run_multiple_games()
        simulator.analyze_results(results)
        
    elif args.type == "tournament":
        results = simulator.run_tournament()
        simulator.analyze_results(results)
        
    elif args.type == "world_championship":
        results = simulator.run_world_championship()
        simulator.analyze_results(results)
        
    elif args.type == "infinite":
        config.infinite = True
        simulator.run_infinite_simulation()
    
    else:
        print(f"Unknown simulation type: {args.type}")

if __name__ == "__main__":
    main()
