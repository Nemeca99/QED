"""
QEC Data Analyzer
Comprehensive analysis of QEC simulation results with hypothesis testing
"""

import os
import json
import csv
import glob
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns

class QECAnalyzer:
    """Comprehensive QEC data analyzer with hypothesis testing"""
    
    def __init__(self, logs_dir: str):
        self.logs_dir = logs_dir
        self.games_data = []
        self.ply_data = []
        self.hypothesis_results = {}
        
    def load_all_data(self):
        """Load all QEC simulation data"""
        print("Loading QEC simulation data...")
        
        # Load game results
        result_files = glob.glob(os.path.join(self.logs_dir, "**", "*_result.json"), recursive=True)
        result_files.extend(glob.glob(os.path.join(self.logs_dir, "**", "*_summary.json"), recursive=True))
        
        print(f"Found {len(result_files)} result files")
        
        for file_path in result_files:
            try:
                with open(file_path, 'r') as f:
                    game_data = json.load(f)
                    self.games_data.append(game_data)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        # Load per-ply data
        ply_files = glob.glob(os.path.join(self.logs_dir, "**", "*_plys.jsonl"), recursive=True)
        ply_files.extend(glob.glob(os.path.join(self.logs_dir, "**", "*.jsonl"), recursive=True))
        
        print(f"Found {len(ply_files)} ply files")
        
        for file_path in ply_files:
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        if line.strip():
                            ply_data = json.loads(line.strip())
                            self.ply_data.append(ply_data)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        print(f"Loaded {len(self.games_data)} games and {len(self.ply_data)} ply records")
    
    def analyze_basic_patterns(self):
        """Analyze basic QEC patterns"""
        if not self.games_data:
            print("No game data loaded")
            return
        
        print("\n=== Basic QEC Pattern Analysis ===")
        
        # Result distribution
        results = [g.get('result', 'Unknown') for g in self.games_data]
        result_counts = pd.Series(results).value_counts()
        
        print(f"Total games: {len(self.games_data)}")
        print(f"Results: {dict(result_counts)}")
        
        # Calculate percentages
        total = len(self.games_data)
        for result, count in result_counts.items():
            percentage = count / total * 100
            print(f"  {result}: {count} ({percentage:.1f}%)")
        
        # Game length analysis
        plies = [g.get('total_plies', 0) for g in self.games_data]
        if plies:
            print(f"\nGame Length Analysis:")
            print(f"  Average plies: {np.mean(plies):.1f}")
            print(f"  Median plies: {np.median(plies):.1f}")
            print(f"  Min plies: {np.min(plies)}")
            print(f"  Max plies: {np.max(plies)}")
            
            # Length by result
            print(f"\nGame Length by Result:")
            for result in result_counts.index:
                result_plies = [g.get('total_plies', 0) for g in self.games_data if g.get('result') == result]
                if result_plies:
                    print(f"  {result}: {np.mean(result_plies):.1f} avg plies")
        
        # Color advantage analysis
        white_wins = sum(1 for g in self.games_data if g.get('result') == 'W wins')
        black_wins = sum(1 for g in self.games_data if g.get('result') == 'B wins')
        draws = sum(1 for g in self.games_data if g.get('result') == 'Draw')
        
        print(f"\nColor Advantage Analysis:")
        print(f"  White wins: {white_wins} ({white_wins/total*100:.1f}%)")
        print(f"  Black wins: {black_wins} ({black_wins/total*100:.1f}%)")
        print(f"  Draws: {draws} ({draws/total*100:.1f}%)")
        
        if white_wins + black_wins > 0:
            decisive_rate = (white_wins + black_wins) / total * 100
            white_advantage = white_wins / (white_wins + black_wins) * 100
            print(f"  Decisive rate: {decisive_rate:.1f}%")
            print(f"  White advantage in decisive games: {white_advantage:.1f}%")
    
    def analyze_archetype_performance(self):
        """Analyze archetype performance patterns"""
        if not self.games_data:
            print("No game data loaded")
            return
        
        print("\n=== Archetype Performance Analysis ===")
        
        # Group by archetype
        archetype_stats = defaultdict(lambda: {
            "wins": 0, "losses": 0, "draws": 0, "games": 0,
            "avg_plies": 0, "avg_captures": 0, "avg_forced": 0, "avg_reactive": 0
        })
        
        for game in self.games_data:
            white_arch = game.get('white_archetype', 'Unknown')
            black_arch = game.get('black_archetype', 'Unknown')
            result = game.get('result', 'Unknown')
            
            # White archetype stats
            archetype_stats[white_arch]["games"] += 1
            archetype_stats[white_arch]["avg_plies"] += game.get('total_plies', 0)
            archetype_stats[white_arch]["avg_captures"] += game.get('captures', 0)
            archetype_stats[white_arch]["avg_forced"] += game.get('forced_moves', 0)
            archetype_stats[white_arch]["avg_reactive"] += game.get('reactive_moves', 0)
            
            if result == 'W wins':
                archetype_stats[white_arch]["wins"] += 1
            elif result == 'B wins':
                archetype_stats[white_arch]["losses"] += 1
            else:
                archetype_stats[white_arch]["draws"] += 1
            
            # Black archetype stats
            archetype_stats[black_arch]["games"] += 1
            archetype_stats[black_arch]["avg_plies"] += game.get('total_plies', 0)
            archetype_stats[black_arch]["avg_captures"] += game.get('captures', 0)
            archetype_stats[black_arch]["avg_forced"] += game.get('forced_moves', 0)
            archetype_stats[black_arch]["avg_reactive"] += game.get('reactive_moves', 0)
            
            if result == 'B wins':
                archetype_stats[black_arch]["wins"] += 1
            elif result == 'W wins':
                archetype_stats[black_arch]["losses"] += 1
            else:
                archetype_stats[black_arch]["draws"] += 1
        
        # Calculate averages and win rates
        for arch, stats in archetype_stats.items():
            if stats["games"] > 0:
                stats["win_rate"] = stats["wins"] / stats["games"] * 100
                stats["avg_plies"] = stats["avg_plies"] / stats["games"]
                stats["avg_captures"] = stats["avg_captures"] / stats["games"]
                stats["avg_forced"] = stats["avg_forced"] / stats["games"]
                stats["avg_reactive"] = stats["avg_reactive"] / stats["games"]
        
        # Print results
        print(f"{'Archetype':<15} {'Games':<6} {'Wins':<5} {'Losses':<7} {'Draws':<5} {'Win%':<6} {'Avg Plies':<10} {'Avg Reactive':<12}")
        print("-" * 90)
        
        sorted_archetypes = sorted(archetype_stats.items(), key=lambda x: x[1]["win_rate"], reverse=True)
        for arch, stats in sorted_archetypes:
            print(f"{arch:<15} {stats['games']:<6} {stats['wins']:<5} "
                  f"{stats['losses']:<7} {stats['draws']:<5} {stats['win_rate']:<6.1f} "
                  f"{stats['avg_plies']:<10.1f} {stats['avg_reactive']:<12.1f}")
        
        return archetype_stats
    
    def analyze_entanglement_patterns(self):
        """Analyze entanglement-related patterns"""
        if not self.games_data:
            print("No game data loaded")
            return
        
        print("\n=== Entanglement Pattern Analysis ===")
        
        # Entanglement statistics
        forced_moves = [g.get('forced_moves', 0) for g in self.games_data]
        reactive_moves = [g.get('reactive_moves', 0) for g in self.games_data]
        reactive_mates = [g.get('reactive_mates', 0) for g in self.games_data]
        captures = [g.get('captures', 0) for g in self.games_data]
        
        print(f"Entanglement Statistics:")
        print(f"  Total forced moves: {sum(forced_moves)}")
        print(f"  Total reactive moves: {sum(reactive_moves)}")
        print(f"  Total reactive mates: {sum(reactive_mates)}")
        print(f"  Total captures: {sum(captures)}")
        
        print(f"\nPer-Game Averages:")
        print(f"  Average forced moves: {np.mean(forced_moves):.1f}")
        print(f"  Average reactive moves: {np.mean(reactive_moves):.1f}")
        print(f"  Average reactive mates: {np.mean(reactive_mates):.1f}")
        print(f"  Average captures: {np.mean(captures):.1f}")
        
        # Correlation analysis
        plies = [g.get('total_plies', 0) for g in self.games_data]
        
        if len(plies) > 1:
            print(f"\nCorrelation Analysis:")
            print(f"  Forced moves vs game length: {np.corrcoef(forced_moves, plies)[0,1]:.3f}")
            print(f"  Reactive moves vs game length: {np.corrcoef(reactive_moves, plies)[0,1]:.3f}")
            print(f"  Captures vs game length: {np.corrcoef(captures, plies)[0,1]:.3f}")
        
        # Entanglement stability analysis
        stable_games = [g for g in self.games_data if g.get('forced_moves', 0) == 0 and g.get('reactive_moves', 0) < 10]
        volatile_games = [g for g in self.games_data if g.get('reactive_moves', 0) > 20]
        
        print(f"\nEntanglement Stability:")
        print(f"  Stable games (low entanglement activity): {len(stable_games)}")
        print(f"  Volatile games (high entanglement activity): {len(volatile_games)}")
        
        if stable_games:
            stable_plies = [g.get('total_plies', 0) for g in stable_games]
            print(f"  Stable games avg length: {np.mean(stable_plies):.1f} plies")
        
        if volatile_games:
            volatile_plies = [g.get('total_plies', 0) for g in volatile_games]
            print(f"  Volatile games avg length: {np.mean(volatile_plies):.1f} plies")
    
    def test_hypotheses(self):
        """Test QEC hypotheses with collected data"""
        print("\n=== QEC Hypothesis Testing ===")
        
        if not self.games_data:
            print("No data available for hypothesis testing")
            return
        
        # H1: Opening Determinism
        print("\nH1: Opening Determinism")
        first_move_impact = self._test_opening_determinism()
        print(f"  First move impact score: {first_move_impact:.3f}")
        
        # H2: Free-Pawn Centrality
        print("\nH2: Free-Pawn Centrality")
        centrality_correlation = self._test_free_pawn_centrality()
        print(f"  Centrality correlation: {centrality_correlation:.3f}")
        
        # H4: Second-Player Advantage
        print("\nH4: Second-Player Advantage")
        second_player_advantage = self._test_second_player_advantage()
        print(f"  Second player advantage: {second_player_advantage:.3f}")
        
        # H5: Entanglement Stability vs Breakage
        print("\nH5: Entanglement Stability vs Breakage")
        stability_correlation = self._test_entanglement_stability()
        print(f"  Stability correlation: {stability_correlation:.3f}")
        
        # H6: Reactive-Check Survival Bias
        print("\nH6: Reactive-Check Survival Bias")
        reactive_survival = self._test_reactive_check_survival()
        print(f"  Reactive survival correlation: {reactive_survival:.3f}")
    
    def _test_opening_determinism(self) -> float:
        """Test H1: Opening Determinism"""
        # Simplified test - would need more sophisticated analysis
        plies = [g.get('total_plies', 0) for g in self.games_data]
        if len(plies) > 1:
            return np.std(plies) / np.mean(plies)  # Coefficient of variation
        return 0.0
    
    def _test_free_pawn_centrality(self) -> float:
        """Test H2: Free-Pawn Centrality"""
        # Simplified test - would need actual free pawn file data
        return 0.0  # Placeholder
    
    def _test_second_player_advantage(self) -> float:
        """Test H4: Second-Player Advantage"""
        white_wins = sum(1 for g in self.games_data if g.get('result') == 'W wins')
        black_wins = sum(1 for g in self.games_data if g.get('result') == 'B wins')
        total_decisive = white_wins + black_wins
        
        if total_decisive > 0:
            return (white_wins - black_wins) / total_decisive
        return 0.0
    
    def _test_entanglement_stability(self) -> float:
        """Test H5: Entanglement Stability vs Breakage"""
        reactive_moves = [g.get('reactive_moves', 0) for g in self.games_data]
        plies = [g.get('total_plies', 0) for g in self.games_data]
        
        if len(reactive_moves) > 1 and len(plies) > 1:
            return np.corrcoef(reactive_moves, plies)[0,1]
        return 0.0
    
    def _test_reactive_check_survival(self) -> float:
        """Test H6: Reactive-Check Survival Bias"""
        reactive_moves = [g.get('reactive_moves', 0) for g in self.games_data]
        plies = [g.get('total_plies', 0) for g in self.games_data]
        
        if len(reactive_moves) > 1 and len(plies) > 1:
            return np.corrcoef(reactive_moves, plies)[0,1]
        return 0.0
    
    def create_visualizations(self):
        """Create comprehensive visualizations"""
        if not self.games_data:
            print("No data available for visualization")
            return
        
        print("\nCreating visualizations...")
        
        # Set up plotting
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        # 1. Result distribution
        results = [g.get('result', 'Unknown') for g in self.games_data]
        result_counts = pd.Series(results).value_counts()
        axes[0, 0].pie(result_counts.values, labels=result_counts.index, autopct='%1.1f%%')
        axes[0, 0].set_title('Game Results Distribution')
        
        # 2. Game length distribution
        plies = [g.get('total_plies', 0) for g in self.games_data]
        axes[0, 1].hist(plies, bins=20, alpha=0.7, color='skyblue')
        axes[0, 1].set_title('Game Length Distribution')
        axes[0, 1].set_xlabel('Number of Plies')
        axes[0, 1].set_ylabel('Frequency')
        
        # 3. Reactive moves vs game length
        reactive_moves = [g.get('reactive_moves', 0) for g in self.games_data]
        axes[0, 2].scatter(reactive_moves, plies, alpha=0.6, color='red')
        axes[0, 2].set_title('Reactive Moves vs Game Length')
        axes[0, 2].set_xlabel('Reactive Moves')
        axes[0, 2].set_ylabel('Game Length (plies)')
        
        # 4. Archetype performance
        archetype_stats = self.analyze_archetype_performance()
        if archetype_stats:
            archetypes = list(archetype_stats.keys())
            win_rates = [archetype_stats[arch]["win_rate"] for arch in archetypes]
            axes[1, 0].bar(archetypes, win_rates, color='lightgreen')
            axes[1, 0].set_title('Archetype Win Rates')
            axes[1, 0].set_ylabel('Win Rate (%)')
            axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 5. Captures vs game length
        captures = [g.get('captures', 0) for g in self.games_data]
        axes[1, 1].scatter(captures, plies, alpha=0.6, color='purple')
        axes[1, 1].set_title('Captures vs Game Length')
        axes[1, 1].set_xlabel('Captures')
        axes[1, 1].set_ylabel('Game Length (plies)')
        
        # 6. Entanglement activity heatmap
        if len(self.games_data) > 10:
            # Create a simple heatmap of entanglement activity
            forced_data = [g.get('forced_moves', 0) for g in self.games_data]
            reactive_data = [g.get('reactive_moves', 0) for g in self.games_data]
            
            # Create 2D histogram
            axes[1, 2].hist2d(forced_data, reactive_data, bins=10, cmap='Blues')
            axes[1, 2].set_title('Forced vs Reactive Moves')
            axes[1, 2].set_xlabel('Forced Moves')
            axes[1, 2].set_ylabel('Reactive Moves')
        
        plt.tight_layout()
        plt.savefig('qec_comprehensive_analysis.png', dpi=300, bbox_inches='tight')
        print("Visualization saved as qec_comprehensive_analysis.png")
    
    def create_summary_report(self):
        """Create comprehensive summary report"""
        if not self.games_data:
            print("No data available for summary report")
            return
        
        print("\n=== QEC Comprehensive Analysis Report ===")
        
        # Basic statistics
        total_games = len(self.games_data)
        results = [g.get('result', 'Unknown') for g in self.games_data]
        result_counts = pd.Series(results).value_counts()
        
        print(f"Dataset Summary:")
        print(f"  Total games: {total_games}")
        print(f"  Results: {dict(result_counts)}")
        
        # Key findings
        white_wins = sum(1 for g in self.games_data if g.get('result') == 'W wins')
        black_wins = sum(1 for g in self.games_data if g.get('result') == 'B wins')
        draws = sum(1 for g in self.games_data if g.get('result') == 'Draw')
        
        print(f"\nKey Findings:")
        print(f"  Draw rate: {draws/total_games*100:.1f}%")
        print(f"  Decisive rate: {(white_wins + black_wins)/total_games*100:.1f}%")
        print(f"  White advantage: {white_wins/(white_wins + black_wins)*100:.1f}% of decisive games")
        
        # Entanglement patterns
        total_reactive = sum(g.get('reactive_moves', 0) for g in self.games_data)
        total_forced = sum(g.get('forced_moves', 0) for g in self.games_data)
        
        print(f"\nEntanglement Patterns:")
        print(f"  Total reactive moves: {total_reactive}")
        print(f"  Total forced moves: {total_forced}")
        print(f"  Reactive/forced ratio: {total_reactive/max(1, total_forced):.1f}")
        
        # Game length patterns
        plies = [g.get('total_plies', 0) for g in self.games_data]
        print(f"\nGame Length Patterns:")
        print(f"  Average length: {np.mean(plies):.1f} plies")
        print(f"  Length range: {np.min(plies)} - {np.max(plies)} plies")
        
        # Save report
        report = {
            "total_games": total_games,
            "results": dict(result_counts),
            "draw_rate": draws/total_games*100,
            "decisive_rate": (white_wins + black_wins)/total_games*100,
            "white_advantage": white_wins/(white_wins + black_wins)*100 if (white_wins + black_wins) > 0 else 0,
            "total_reactive_moves": total_reactive,
            "total_forced_moves": total_forced,
            "reactive_forced_ratio": total_reactive/max(1, total_forced),
            "average_game_length": np.mean(plies),
            "game_length_range": [np.min(plies), np.max(plies)]
        }
        
        with open('qec_analysis_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nReport saved to qec_analysis_report.json")
    
    def run_full_analysis(self):
        """Run complete analysis pipeline"""
        print("=== QEC Comprehensive Analysis ===")
        
        # Load data
        self.load_all_data()
        
        if not self.games_data:
            print("No data found to analyze")
            return
        
        # Run analyses
        self.analyze_basic_patterns()
        self.analyze_archetype_performance()
        self.analyze_entanglement_patterns()
        self.test_hypotheses()
        
        # Create visualizations
        try:
            self.create_visualizations()
        except ImportError:
            print("Matplotlib not available, skipping visualizations")
        
        # Create summary report
        self.create_summary_report()
        
        print("\nAnalysis complete!")

if __name__ == "__main__":
    # Run analysis on QEC logs
    analyzer = QECAnalyzer("qec_research_logs")
    analyzer.run_full_analysis()
