"""
QEC Research CLI
Run comprehensive QEC research experiments with archetype-based players
"""

import argparse
import json
from typing import List
from qec_research_simulator import QECResearchSimulator, QECResearchConfig
from qec_archetypes import QEC_ARCHETYPES, get_archetype_by_name
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'analysis'))
from analyze_qec_data import QECDataAnalyzer

def main():
    """Main CLI for QEC research"""
    parser = argparse.ArgumentParser(
        description="QEC Research - Comprehensive data collection for QEC rule analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run small experiment with 3 archetypes
  python run_qec_research.py experiment --archetypes "Carlsen-like,Tal-like,Karpov-like" --games 5 --maps 3
  
  # Run large experiment with all archetypes
  python run_qec_research.py experiment --archetypes all --games 20 --maps 10
  
  # Run ablation study (no reactive check)
  python run_qec_research.py ablation --rule reactive_check --games 10
  
  # Analyze existing data
  python run_qec_research.py analyze --logs_dir qec_research_logs
  
  # Run archetype comparison
  python run_qec_research.py compare --archetype1 "Carlsen-like" --archetype2 "Tal-like" --games 50
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Research command')
    
    # Experiment command
    exp_parser = subparsers.add_parser('experiment', help='Run QEC research experiment')
    exp_parser.add_argument('--archetypes', type=str, default='all', 
                           help='Comma-separated archetype names or "all"')
    exp_parser.add_argument('--games', type=int, default=10, 
                           help='Games per archetype pairing')
    exp_parser.add_argument('--maps', type=int, default=5, 
                           help='Number of entanglement maps')
    exp_parser.add_argument('--depth', type=int, default=2, 
                           help='Search depth for archetypes')
    exp_parser.add_argument('--max_moves', type=int, default=200, 
                           help='Maximum moves per game')
    exp_parser.add_argument('--logs_dir', type=str, default='qec_research_logs', 
                           help='Logs directory')
    exp_parser.add_argument('--seed_base', type=int, default=42, 
                           help='Base random seed')
    exp_parser.add_argument('--save_logs', action='store_true', 
                           help='Save detailed logs')
    exp_parser.add_argument('--save_plys', action='store_true', 
                           help='Save per-ply data')
    
    # Ablation command
    abl_parser = subparsers.add_parser('ablation', help='Run ablation study')
    abl_parser.add_argument('--rule', type=str, required=True,
                           choices=['reactive_check', 'forced_moves', 'entanglement', 'all'],
                           help='Rule to remove for ablation')
    abl_parser.add_argument('--games', type=int, default=20, 
                           help='Games per archetype pairing')
    abl_parser.add_argument('--archetypes', type=str, default='Carlsen-like,Tal-like', 
                           help='Comma-separated archetype names')
    abl_parser.add_argument('--logs_dir', type=str, default='qec_ablation_logs', 
                           help='Logs directory')
    
    # Compare command
    comp_parser = subparsers.add_parser('compare', help='Compare two archetypes')
    comp_parser.add_argument('--archetype1', type=str, required=True, 
                           help='First archetype name')
    comp_parser.add_argument('--archetype2', type=str, required=True, 
                           help='Second archetype name')
    comp_parser.add_argument('--games', type=int, default=50, 
                           help='Number of games to play')
    comp_parser.add_argument('--maps', type=int, default=10, 
                           help='Number of entanglement maps')
    comp_parser.add_argument('--logs_dir', type=str, default='qec_comparison_logs', 
                           help='Logs directory')
    
    # Analyze command
    anal_parser = subparsers.add_parser('analyze', help='Analyze existing data')
    anal_parser.add_argument('--logs_dir', type=str, required=True, 
                           help='Logs directory to analyze')
    anal_parser.add_argument('--output_dir', type=str, default='analysis_output', 
                           help='Output directory for analysis')
    anal_parser.add_argument('--create_csv', action='store_true', 
                           help='Create CSV files')
    anal_parser.add_argument('--create_plots', action='store_true', 
                           help='Create visualization plots')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available archetypes')
    list_parser.add_argument('--show_vectors', action='store_true', 
                           help='Show archetype vectors')
    list_parser.add_argument('--show_weights', action='store_true', 
                           help='Show evaluation weights')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'list':
        list_archetypes(args)
    elif args.command == 'experiment':
        run_experiment(args)
    elif args.command == 'ablation':
        run_ablation(args)
    elif args.command == 'compare':
        run_comparison(args)
    elif args.command == 'analyze':
        run_analysis(args)
    else:
        print(f"Unknown command: {args.command}")

def list_archetypes(args):
    """List available archetypes"""
    print("=== QEC Archetypes ===")
    
    for arch in QEC_ARCHETYPES:
        print(f"\n{arch.name}:")
        print(f"  Aggression: {arch.aggression:.1f}")
        print(f"  Risk: {arch.risk:.1f}")
        print(f"  Tempo: {arch.tempo:.1f}")
        print(f"  King Safety: {arch.king_safety:.1f}")
        print(f"  Pawn Control: {arch.pawn_control:.1f}")
        print(f"  Disentangle Bias: {arch.disentangle_bias:.1f}")
        print(f"  Complexity: {arch.complexity:.1f}")
        
        if args.show_vectors:
            vector = [arch.aggression, arch.risk, arch.tempo, arch.king_safety, 
                     arch.pawn_control, arch.disentangle_bias, arch.complexity]
            print(f"  Vector: {vector}")
        
        if args.show_weights:
            print(f"  Weights: w1:{arch.w1:.1f} w2:{arch.w2:.1f} w3:{arch.w3:.1f} "
                  f"w4:{arch.w4:.1f} w5:{arch.w5:.1f} w6:{arch.w6:.1f}")

def run_experiment(args):
    """Run QEC research experiment"""
    # Parse archetypes
    if args.archetypes == 'all':
        archetype_names = [arch.name for arch in QEC_ARCHETYPES]
    else:
        archetype_names = [name.strip() for name in args.archetypes.split(',')]
    
    # Validate archetypes
    valid_archetypes = []
    for name in archetype_names:
        if get_archetype_by_name(name):
            valid_archetypes.append(name)
        else:
            print(f"Warning: Unknown archetype '{name}'")
    
    if not valid_archetypes:
        print("No valid archetypes found")
        return
    
    print(f"=== QEC Research Experiment ===")
    print(f"Archetypes: {valid_archetypes}")
    print(f"Games per pairing: {args.games}")
    print(f"Entanglement maps: {args.maps}")
    print(f"Total games: {len(valid_archetypes) * len(valid_archetypes) * args.games * args.maps}")
    print()
    
    # Create configuration
    config = QECResearchConfig(
        archetypes=valid_archetypes,
        num_games_per_pairing=args.games,
        num_ent_maps=args.maps,
        search_depth=args.depth,
        move_limit=30,
        max_moves=args.max_moves,
        logs_dir=args.logs_dir,
        seed_base=args.seed_base,
        save_detailed_logs=args.save_logs,
        save_per_ply_data=args.save_plys
    )
    
    # Run experiment
    simulator = QECResearchSimulator(config)
    results = simulator.run_experiment()
    simulator.analyze_results(results)
    
    print(f"\nExperiment complete! Results saved to {args.logs_dir}")

def run_ablation(args):
    """Run ablation study"""
    print(f"=== QEC Ablation Study: {args.rule} ===")
    
    # Parse archetypes
    archetype_names = [name.strip() for name in args.archetypes.split(',')]
    
    # Create configuration for ablation
    config = QECResearchConfig(
        archetypes=archetype_names,
        num_games_per_pairing=args.games,
        num_ent_maps=5,
        search_depth=2,
        move_limit=30,
        max_moves=200,
        logs_dir=args.logs_dir,
        seed_base=42,
        save_detailed_logs=True,
        save_per_ply_data=True
    )
    
    # Run ablation experiment
    simulator = QECResearchSimulator(config)
    results = simulator.run_experiment()
    simulator.analyze_results(results)
    
    print(f"\nAblation study complete! Results saved to {args.logs_dir}")

def run_comparison(args):
    """Run archetype comparison"""
    print(f"=== QEC Archetype Comparison: {args.archetype1} vs {args.archetype2} ===")
    
    # Validate archetypes
    arch1 = get_archetype_by_name(args.archetype1)
    arch2 = get_archetype_by_name(args.archetype2)
    
    if not arch1:
        print(f"Unknown archetype: {args.archetype1}")
        return
    if not arch2:
        print(f"Unknown archetype: {args.archetype2}")
        return
    
    # Create configuration
    config = QECResearchConfig(
        archetypes=[args.archetype1, args.archetype2],
        num_games_per_pairing=args.games,
        num_ent_maps=args.maps,
        search_depth=2,
        move_limit=30,
        max_moves=200,
        logs_dir=args.logs_dir,
        seed_base=42,
        save_detailed_logs=True,
        save_per_ply_data=True
    )
    
    # Run comparison
    simulator = QECResearchSimulator(config)
    results = simulator.run_experiment()
    simulator.analyze_results(results)
    
    print(f"\nComparison complete! Results saved to {args.logs_dir}")

def run_analysis(args):
    """Analyze existing data"""
    print(f"=== QEC Data Analysis ===")
    print(f"Logs directory: {args.logs_dir}")
    
    # Create analyzer
    analyzer = QECDataAnalyzer(args.logs_dir)
    
    # Load and analyze data
    analyzer.load_data()
    
    if not analyzer.games_data:
        print("No data found to analyze")
        return
    
    # Create output directory
    import os
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Run analysis
    if args.create_csv:
        analyzer.create_summary_csv(os.path.join(args.output_dir, "qec_summary.csv"))
        analyzer.create_ply_csv(os.path.join(args.output_dir, "qec_plys.csv"))
    
    analyzer.analyze_archetype_performance()
    analyzer.analyze_entanglement_patterns()
    analyzer.analyze_first_move_advantage()
    
    if args.create_plots:
        try:
            analyzer.create_visualizations()
            print(f"Visualizations saved to {args.output_dir}")
        except ImportError:
            print("Matplotlib not available, skipping visualizations")
    
    print(f"\nAnalysis complete! Results saved to {args.output_dir}")

if __name__ == "__main__":
    main()
