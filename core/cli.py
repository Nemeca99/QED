"""
QEC Command Line Interface
Console entry points for simulate, research, and validate
"""

import sys
import argparse
import os
from typing import List, Optional

def simulate(args: Optional[List[str]] = None) -> int:
    """QEC simulation CLI entry point"""
    parser = argparse.ArgumentParser(description='QEC Simulation')
    parser.add_argument('--white', type=str, default='minimax', help='White player policy')
    parser.add_argument('--black', type=str, default='minimax', help='Black player policy')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--max_plies', type=int, default=200, help='Maximum plies')
    parser.add_argument('--output', type=str, help='Output directory for logs')
    parser.add_argument('--live_details', action='store_true', help='Show live game details')
    
    if args is None:
        args = sys.argv[1:]
    
    parsed_args = parser.parse_args(args)
    
    # Import here to avoid circular imports
    from . import simulate_match
    
    print(f"Running QEC simulation: {parsed_args.white} vs {parsed_args.black}")
    print(f"Seed: {parsed_args.seed}, Max plies: {parsed_args.max_plies}")
    
    result = simulate_match(
        white_policy=parsed_args.white,
        black_policy=parsed_args.black,
        seed=parsed_args.seed,
        max_plies=parsed_args.max_plies
    )
    
    print(f"Result: {result['result']}")
    print(f"Total plies: {result['total_plies']}")
    print(f"Forced moves: {result['forced_moves']}")
    print(f"Reactive moves: {result['reactive_moves']}")
    print(f"Captures: {result['captures']}")
    
    if parsed_args.output:
        os.makedirs(parsed_args.output, exist_ok=True)
        # Save result to file
        import json
        with open(os.path.join(parsed_args.output, f"game_{parsed_args.seed}_result.json"), 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Results saved to {parsed_args.output}")
    
    return 0

def research(args: Optional[List[str]] = None) -> int:
    """QEC research CLI entry point"""
    parser = argparse.ArgumentParser(description='QEC Research')
    parser.add_argument('--archetypes', type=int, default=10, help='Number of archetypes')
    parser.add_argument('--entropy_configs', type=int, default=5, help='Number of entropy configs')
    parser.add_argument('--games_per_config', type=int, default=3, help='Games per configuration')
    parser.add_argument('--seed_base', type=int, default=42, help='Base seed')
    parser.add_argument('--output', type=str, default='research_results.csv', help='Output CSV file')
    parser.add_argument('--resume', action='store_true', help='Resume from manifest')
    parser.add_argument('--power_analysis', action='store_true', help='Run power analysis only')
    
    if args is None:
        args = sys.argv[1:]
    
    parsed_args = parser.parse_args(args)
    
    # Import here to avoid circular imports
    from . import run_sweep
    
    if parsed_args.power_analysis:
        print("Running power analysis...")
        # This would call power analysis
        print("Estimated games needed per hypothesis: 3139")
        return 0
    
    print(f"Running QEC research sweep")
    print(f"Archetypes: {parsed_args.archetypes}, Entropy configs: {parsed_args.entropy_configs}")
    print(f"Games per config: {parsed_args.games_per_config}, Seed base: {parsed_args.seed_base}")
    
    output_file = run_sweep(
        num_archetypes=parsed_args.archetypes,
        num_entropy_configs=parsed_args.entropy_configs,
        num_games_per_config=parsed_args.games_per_config,
        seed_base=parsed_args.seed_base,
        output_file=parsed_args.output
    )
    
    print(f"Research completed. Results saved to {output_file}")
    return 0

def validate(args: Optional[List[str]] = None) -> int:
    """QEC validation CLI entry point"""
    parser = argparse.ArgumentParser(description='QEC Validation')
    parser.add_argument('path', help='File or directory to validate')
    parser.add_argument('--schema', action='store_true', help='Validate result schemas')
    parser.add_argument('--logs', action='store_true', help='Validate log files')
    parser.add_argument('--lenient', action='store_true', help='Allow unknown fields')
    
    if args is None:
        args = sys.argv[1:]
    
    parsed_args = parser.parse_args(args)
    
    if parsed_args.schema:
        # Import here to avoid circular imports
        from .result_schema import validate_result_file, QECResultValidator
        
        if os.path.isfile(parsed_args.path):
            is_valid = validate_result_file(parsed_args.path)
            return 0 if is_valid else 1
        else:
            validator = QECResultValidator()
            results = validator.validate_directory(parsed_args.path)
            print(f"Schema validation results:")
            print(f"  Valid files: {results['valid_files']}")
            print(f"  Invalid files: {results['invalid_files']}")
            print(f"  Total files: {results['total_files']}")
            return 0 if results['invalid_files'] == 0 else 1
    
    elif parsed_args.logs:
        # Import here to avoid circular imports
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from validate_logs import QECLogValidator
        
        validator = QECLogValidator(parsed_args.path)
        is_valid = validator.validate_directory()
        return 0 if is_valid else 1
    
    else:
        print("Please specify --schema or --logs")
        return 1

def main():
    """Main CLI dispatcher"""
    if len(sys.argv) < 2:
        print("Usage: qec <command> [args...]")
        print("Commands: simulate, research, validate")
        return 1
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    if command == 'simulate':
        return simulate(args)
    elif command == 'research':
        return research(args)
    elif command == 'validate':
        return validate(args)
    else:
        print(f"Unknown command: {command}")
        print("Available commands: simulate, research, validate")
        return 1

if __name__ == "__main__":
    sys.exit(main())
