"""
QEC Human Simulation Runner
Easy-to-use CLI for running various types of QEC simulations with real chess players
"""

import argparse
import sys
from comprehensive_simulator import ComprehensiveSimulator, SimulationConfig

def main():
    """Main CLI for QEC human simulation"""
    parser = argparse.ArgumentParser(
        description="QEC Human Simulation - Real chess players in Quantum Entanglement Chess",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single match between two players
  python run_simulation.py match --white "Magnus Carlsen" --black "Fabiano Caruana"
  
  # Multiple games between same players
  python run_simulation.py multiple --white "Magnus Carlsen" --black "Fabiano Caruana" --games 10
  
  # Round robin tournament
  python run_simulation.py tournament --format round_robin --pool super_gm --games 1
  
  # Swiss tournament
  python run_simulation.py tournament --format swiss --pool mixed --games 1
  
  # World championship match
  python run_simulation.py world_championship --games 12
  
  # Infinite simulation with random pairings
  python run_simulation.py infinite --pool mixed
  
  # Show available players
  python run_simulation.py list_players
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Simulation type')
    
    # Single match
    match_parser = subparsers.add_parser('match', help='Single match between two players')
    match_parser.add_argument('--white', type=str, default='Magnus Carlsen', help='White player name')
    match_parser.add_argument('--black', type=str, default='Fabiano Caruana', help='Black player name')
    match_parser.add_argument('--seed', type=int, default=42, help='Random seed')
    match_parser.add_argument('--save_logs', action='store_true', help='Save game logs')
    match_parser.add_argument('--live_details', action='store_true', help='Show live move details')
    
    # Multiple games
    multiple_parser = subparsers.add_parser('multiple', help='Multiple games between same players')
    multiple_parser.add_argument('--white', type=str, default='Magnus Carlsen', help='White player name')
    multiple_parser.add_argument('--black', type=str, default='Fabiano Caruana', help='Black player name')
    multiple_parser.add_argument('--games', type=int, default=10, help='Number of games')
    multiple_parser.add_argument('--seed_base', type=int, default=42, help='Base random seed')
    multiple_parser.add_argument('--save_logs', action='store_true', help='Save game logs')
    multiple_parser.add_argument('--live_details', action='store_true', help='Show live move details')
    
    # Tournament
    tournament_parser = subparsers.add_parser('tournament', help='Tournament with multiple players')
    tournament_parser.add_argument('--format', type=str, default='round_robin', 
                                 choices=['round_robin', 'swiss', 'knockout'], help='Tournament format')
    tournament_parser.add_argument('--pool', type=str, default='mixed', 
                                 help='Player pool (super_gm, top_gm, strong_gm, im, master, mixed, tactical, positional, blitz)')
    tournament_parser.add_argument('--games', type=int, default=1, help='Number of games per pairing')
    tournament_parser.add_argument('--save_logs', action='store_true', help='Save game logs')
    tournament_parser.add_argument('--live_details', action='store_true', help='Show live move details')
    
    # World championship
    world_parser = subparsers.add_parser('world_championship', help='World championship match')
    world_parser.add_argument('--games', type=int, default=12, help='Number of games in match')
    world_parser.add_argument('--save_logs', action='store_true', help='Save game logs')
    world_parser.add_argument('--live_details', action='store_true', help='Show live move details')
    
    # Infinite simulation
    infinite_parser = subparsers.add_parser('infinite', help='Infinite simulation with random pairings')
    infinite_parser.add_argument('--pool', type=str, default='mixed', 
                               help='Player pool (super_gm, top_gm, strong_gm, im, master, mixed, tactical, positional, blitz)')
    infinite_parser.add_argument('--seed_base', type=int, default=42, help='Base random seed')
    infinite_parser.add_argument('--save_logs', action='store_true', help='Save game logs')
    infinite_parser.add_argument('--live_details', action='store_true', help='Show live move details')
    
    # List players
    list_parser = subparsers.add_parser('list_players', help='List available players')
    list_parser.add_argument('--pool', type=str, help='Filter by player pool')
    list_parser.add_argument('--style', type=str, help='Filter by playing style')
    list_parser.add_argument('--rating_min', type=int, help='Minimum rating')
    list_parser.add_argument('--rating_max', type=int, help='Maximum rating')
    
    # Common options
    parser.add_argument('--logs_dir', type=str, default='simulation_logs', help='Logs directory')
    parser.add_argument('--max_moves', type=int, default=200, help='Maximum moves per game')
    
    args = parser.parse_args()
    
    if args.command == 'list_players':
        list_players(args)
        return
    
    if not args.command:
        parser.print_help()
        return
    
    # Create configuration
    config = SimulationConfig(
        white_player=getattr(args, 'white', 'Magnus Carlsen'),
        black_player=getattr(args, 'black', 'Fabiano Caruana'),
        num_games=getattr(args, 'games', 1),
        tournament_format=getattr(args, 'format', 'round_robin'),
        player_pool=getattr(args, 'pool', 'mixed'),
        logs_dir=args.logs_dir,
        seed_base=getattr(args, 'seed_base', getattr(args, 'seed', 42)),
        max_moves=args.max_moves,
        live_details=getattr(args, 'live_details', False),
        infinite=(args.command == 'infinite'),
        save_logs=getattr(args, 'save_logs', False)
    )
    
    # Create simulator
    simulator = ComprehensiveSimulator(config)
    
    # Run simulation based on command
    if args.command == 'match':
        result = simulator.run_single_match()
        print(f"\nResult: {result.result}")
        print(f"Moves: {result.moves}")
        print(f"Duration: {result.duration:.2f}s")
        
    elif args.command == 'multiple':
        results = simulator.run_multiple_games()
        simulator.analyze_results(results)
        
    elif args.command == 'tournament':
        results = simulator.run_tournament()
        simulator.analyze_results(results)
        
    elif args.command == 'world_championship':
        results = simulator.run_world_championship()
        simulator.analyze_results(results)
        
    elif args.command == 'infinite':
        simulator.run_infinite_simulation()
    
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)

def list_players(args):
    """List available players with optional filtering"""
    from player_database import CHESS_PLAYERS, get_tournament_pools, get_players_by_style, get_players_by_rating_range
    
    players = CHESS_PLAYERS
    
    # Apply filters
    if args.pool:
        pools = get_tournament_pools()
        if args.pool in pools:
            players = pools[args.pool]
        else:
            print(f"Unknown pool: {args.pool}")
            return
    
    if args.style:
        players = [p for p in players if p.style.value == args.style]
    
    if args.rating_min:
        players = [p for p in players if p.rating >= args.rating_min]
    
    if args.rating_max:
        players = [p for p in players if p.rating <= args.rating_max]
    
    # Display players
    print(f"Available Players ({len(players)}):")
    print(f"{'Name':<20} {'Rating':<6} {'Style':<12} {'Strengths':<30}")
    print("-" * 80)
    
    for player in sorted(players, key=lambda x: x.rating, reverse=True):
        strengths = ", ".join(player.strengths[:2])  # Show first 2 strengths
        print(f"{player.name:<20} {player.rating:<6} {player.style.value:<12} {strengths:<30}")
    
    print(f"\nPlayer Pools:")
    pools = get_tournament_pools()
    for pool_name, pool_players in pools.items():
        print(f"  {pool_name}: {len(pool_players)} players")

if __name__ == "__main__":
    main()
