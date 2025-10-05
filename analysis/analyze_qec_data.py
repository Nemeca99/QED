"""
QEC Data Analyzer
Aggregates and analyzes QEC simulation data for pattern discovery
"""

import os
import json
import csv
import glob
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns

class QECDataAnalyzer:
    """Analyze QEC simulation data for patterns and insights"""
    
    def __init__(self, logs_dir: str):
        self.logs_dir = logs_dir
        self.games_data = []
        self.ply_data = []
        
    def load_data(self):
        """Load all QEC simulation data"""
        print("Loading QEC simulation data...")
        
        # Find all result files
        result_files = glob.glob(os.path.join(self.logs_dir, "**", "*_result.json"), recursive=True)
        print(f"Found {len(result_files)} result files")
        
        # Load game results
        for file_path in result_files:
            try:
                with open(file_path, 'r') as f:
                    game_data = json.load(f)
                    self.games_data.append(game_data)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        # Find all ply files
        ply_files = glob.glob(os.path.join(self.logs_dir, "**", "*_plys.jsonl"), recursive=True)
        print(f"Found {len(ply_files)} ply files")
        
        # Load per-ply data
        for file_path in ply_files:
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        ply_data = json.loads(line.strip())
                        self.ply_data.append(ply_data)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        print(f"Loaded {len(self.games_data)} games and {len(self.ply_data)} ply records")
    
    def create_summary_csv(self, output_file: str = "qec_summary.csv"):
        """Create comprehensive CSV summary of all games"""
        if not self.games_data:
            print("No game data loaded")
            return
        
        print(f"Creating summary CSV: {output_file}")
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'game_id', 'white_archetype', 'black_archetype', 'result',
                'total_plies', 'captures', 'promotions', 'forced_moves',
                'reactive_moves', 'reactive_mates', 'ent_map_hash',
                'ent_pairs_10', 'ent_pairs_20', 'ent_pairs_30',
                'king_reacts', 'king_distance', 'eval_swing',
                'avg_legal_moves', 'first_move_advantage', 'duration'
            ])
            
            # Write data
            for game in self.games_data:
                writer.writerow([
                    game.get('game_id', ''),
                    game.get('white_archetype', ''),
                    game.get('black_archetype', ''),
                    game.get('result', ''),
                    game.get('total_plies', 0),
                    game.get('captures', 0),
                    game.get('promotions', 0),
                    game.get('forced_moves', 0),
                    game.get('reactive_moves', 0),
                    game.get('reactive_mates', 0),
                    game.get('ent_map_hash', ''),
                    game.get('ent_pairs_remaining_10', 0),
                    game.get('ent_pairs_remaining_20', 0),
                    game.get('ent_pairs_remaining_30', 0),
                    game.get('king_reacts', 0),
                    game.get('king_distance_traveled', 0.0),
                    game.get('eval_swing', 0.0),
                    game.get('avg_legal_moves', 0.0),
                    game.get('first_move_advantage', 0.0),
                    game.get('duration', 0.0)
                ])
        
        print(f"Summary CSV created: {output_file}")
    
    def create_ply_csv(self, output_file: str = "qec_plys.csv"):
        """Create CSV of per-ply data"""
        if not self.ply_data:
            print("No ply data loaded")
            return
        
        print(f"Creating ply CSV: {output_file}")
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'game_id', 'ply', 'side', 'primary', 'forced', 'react',
                'ent_map_hash', 'eval', 'phase', 'legal_count', 'notes'
            ])
            
            # Write data
            for ply in self.ply_data:
                writer.writerow([
                    ply.get('game_id', ''),
                    ply.get('ply', 0),
                    ply.get('side', ''),
                    ply.get('primary', ''),
                    ply.get('forced', ''),
                    ply.get('react', ''),
                    ply.get('ent_map_hash', ''),
                    ply.get('eval', 0),
                    ply.get('phase', ''),
                    ply.get('legal_count', 0),
                    ply.get('notes', '')
                ])
        
        print(f"Ply CSV created: {output_file}")
    
    def analyze_archetype_performance(self):
        """Analyze archetype performance patterns"""
        if not self.games_data:
            print("No game data loaded")
            return
        
        print("\n=== Archetype Performance Analysis ===")
        
        # Group by archetype
        archetype_stats = defaultdict(lambda: {
            "wins": 0, "losses": 0, "draws": 0, "games": 0,
            "avg_plies": 0, "avg_captures": 0, "avg_forced": 0,
            "avg_reactive": 0, "reactive_mate_rate": 0
        })
        
        for game in self.games_data:
            # White archetype
            white_arch = game.get('white_archetype', '')
            archetype_stats[white_arch]["games"] += 1
            if game.get('result') == 'W wins':
                archetype_stats[white_arch]["wins"] += 1
            elif game.get('result') == 'B wins':
                archetype_stats[white_arch]["losses"] += 1
            else:
                archetype_stats[white_arch]["draws"] += 1
            
            # Black archetype
            black_arch = game.get('black_archetype', '')
            archetype_stats[black_arch]["games"] += 1
            if game.get('result') == 'B wins':
                archetype_stats[black_arch]["wins"] += 1
            elif game.get('result') == 'W wins':
                archetype_stats[black_arch]["losses"] += 1
            else:
                archetype_stats[black_arch]["draws"] += 1
        
        # Calculate averages
        for arch, stats in archetype_stats.items():
            if stats["games"] > 0:
                stats["win_rate"] = stats["wins"] / stats["games"] * 100
                stats["avg_plies"] = sum(g.get('total_plies', 0) for g in self.games_data 
                                       if g.get('white_archetype') == arch or g.get('black_archetype') == arch) / stats["games"]
                stats["avg_captures"] = sum(g.get('captures', 0) for g in self.games_data 
                                          if g.get('white_archetype') == arch or g.get('black_archetype') == arch) / stats["games"]
                stats["avg_forced"] = sum(g.get('forced_moves', 0) for g in self.games_data 
                                        if g.get('white_archetype') == arch or g.get('black_archetype') == arch) / stats["games"]
                stats["avg_reactive"] = sum(g.get('reactive_moves', 0) for g in self.games_data 
                                          if g.get('white_archetype') == arch or g.get('black_archetype') == arch) / stats["games"]
                stats["reactive_mate_rate"] = sum(g.get('reactive_mates', 0) for g in self.games_data 
                                                if g.get('white_archetype') == arch or g.get('black_archetype') == arch) / stats["games"]
        
        # Print results
        print(f"{'Archetype':<15} {'Games':<6} {'Win%':<6} {'Avg Plies':<10} {'Avg Captures':<12} {'Avg Forced':<10} {'Reactive Mate%':<12}")
        print("-" * 90)
        
        for arch, stats in archetype_stats.items():
            print(f"{arch:<15} {stats['games']:<6} {stats['win_rate']:<6.1f} "
                  f"{stats['avg_plies']:<10.1f} {stats['avg_captures']:<12.1f} "
                  f"{stats['avg_forced']:<10.1f} {stats['reactive_mate_rate']:<12.1f}")
    
    def analyze_entanglement_patterns(self):
        """Analyze entanglement-related patterns"""
        if not self.games_data:
            print("No game data loaded")
            return
        
        print("\n=== Entanglement Pattern Analysis ===")
        
        # Entanglement persistence
        ent_pairs_10 = [g.get('ent_pairs_remaining_10', 0) for g in self.games_data]
        ent_pairs_20 = [g.get('ent_pairs_remaining_20', 0) for g in self.games_data]
        ent_pairs_30 = [g.get('ent_pairs_remaining_30', 0) for g in self.games_data]
        
        print(f"Average entanglement pairs at move 10: {np.mean(ent_pairs_10):.1f}")
        print(f"Average entanglement pairs at move 20: {np.mean(ent_pairs_20):.1f}")
        print(f"Average entanglement pairs at move 30: {np.mean(ent_pairs_30):.1f}")
        
        # Forced move patterns
        forced_moves = [g.get('forced_moves', 0) for g in self.games_data]
        reactive_moves = [g.get('reactive_moves', 0) for g in self.games_data]
        reactive_mates = [g.get('reactive_mates', 0) for g in self.games_data]
        
        print(f"Average forced moves per game: {np.mean(forced_moves):.1f}")
        print(f"Average reactive moves per game: {np.mean(reactive_moves):.1f}")
        print(f"Reactive mate rate: {np.mean(reactive_mates):.1f}")
        
        # Correlation analysis
        print(f"\nCorrelation between forced moves and game length: {np.corrcoef(forced_moves, [g.get('total_plies', 0) for g in self.games_data])[0,1]:.3f}")
        print(f"Correlation between reactive moves and game length: {np.corrcoef(reactive_moves, [g.get('total_plies', 0) for g in self.games_data])[0,1]:.3f}")
    
    def analyze_first_move_advantage(self):
        """Analyze first move advantage in QEC"""
        if not self.games_data:
            print("No game data loaded")
            return
        
        print("\n=== First Move Advantage Analysis ===")
        
        white_wins = sum(1 for g in self.games_data if g.get('result') == 'W wins')
        black_wins = sum(1 for g in self.games_data if g.get('result') == 'B wins')
        draws = sum(1 for g in self.games_data if g.get('result') == 'Draw')
        total = len(self.games_data)
        
        print(f"White wins: {white_wins} ({white_wins/total*100:.1f}%)")
        print(f"Black wins: {black_wins} ({black_wins/total*100:.1f}%)")
        print(f"Draws: {draws} ({draws/total*100:.1f}%)")
        
        # First move advantage by archetype
        archetype_advantage = defaultdict(lambda: {"white_wins": 0, "black_wins": 0, "total": 0})
        
        for game in self.games_data:
            white_arch = game.get('white_archetype', '')
            black_arch = game.get('black_archetype', '')
            result = game.get('result', '')
            
            archetype_advantage[white_arch]["total"] += 1
            if result == 'W wins':
                archetype_advantage[white_arch]["white_wins"] += 1
            elif result == 'B wins':
                archetype_advantage[white_arch]["black_wins"] += 1
        
        print(f"\nFirst move advantage by archetype:")
        for arch, stats in archetype_advantage.items():
            if stats["total"] > 0:
                white_rate = stats["white_wins"] / stats["total"] * 100
                print(f"{arch:<15}: {white_rate:.1f}% white win rate")
    
    def create_visualizations(self):
        """Create visualization plots"""
        if not self.games_data:
            print("No game data loaded")
            return
        
        print("\nCreating visualizations...")
        
        # Set up plotting
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Result distribution
        results = [g.get('result', '') for g in self.games_data]
        result_counts = pd.Series(results).value_counts()
        axes[0, 0].pie(result_counts.values, labels=result_counts.index, autopct='%1.1f%%')
        axes[0, 0].set_title('Game Results Distribution')
        
        # 2. Game length distribution
        plies = [g.get('total_plies', 0) for g in self.games_data]
        axes[0, 1].hist(plies, bins=20, alpha=0.7)
        axes[0, 1].set_title('Game Length Distribution')
        axes[0, 1].set_xlabel('Number of Plies')
        axes[0, 1].set_ylabel('Frequency')
        
        # 3. Forced moves vs game length
        forced_moves = [g.get('forced_moves', 0) for g in self.games_data]
        axes[1, 0].scatter(forced_moves, plies, alpha=0.6)
        axes[1, 0].set_title('Forced Moves vs Game Length')
        axes[1, 0].set_xlabel('Forced Moves')
        axes[1, 0].set_ylabel('Game Length (plies)')
        
        # 4. Archetype performance
        archetype_wins = defaultdict(int)
        archetype_games = defaultdict(int)
        
        for game in self.games_data:
            white_arch = game.get('white_archetype', '')
            black_arch = game.get('black_archetype', '')
            result = game.get('result', '')
            
            archetype_games[white_arch] += 1
            archetype_games[black_arch] += 1
            
            if result == 'W wins':
                archetype_wins[white_arch] += 1
            elif result == 'B wins':
                archetype_wins[black_arch] += 1
        
        archetypes = list(archetype_games.keys())
        win_rates = [archetype_wins[arch] / archetype_games[arch] * 100 for arch in archetypes]
        
        axes[1, 1].bar(archetypes, win_rates)
        axes[1, 1].set_title('Archetype Win Rates')
        axes[1, 1].set_ylabel('Win Rate (%)')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig('qec_analysis.png', dpi=300, bbox_inches='tight')
        print("Visualization saved as qec_analysis.png")
    
    def run_full_analysis(self):
        """Run complete analysis pipeline"""
        print("=== QEC Data Analysis Pipeline ===")
        
        # Load data
        self.load_data()
        
        if not self.games_data:
            print("No data found to analyze")
            return
        
        # Create CSV files
        self.create_summary_csv()
        self.create_ply_csv()
        
        # Run analyses
        self.analyze_archetype_performance()
        self.analyze_entanglement_patterns()
        self.analyze_first_move_advantage()
        
        # Create visualizations
        try:
            self.create_visualizations()
        except ImportError:
            print("Matplotlib not available, skipping visualizations")
        
        print("\nAnalysis complete!")

if __name__ == "__main__":
    # Run analysis on QEC research logs
    analyzer = QECDataAnalyzer("qec_research_logs")
    analyzer.run_full_analysis()
