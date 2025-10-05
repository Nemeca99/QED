"""
QEC Results Analyzer
Focused analysis of QEC simulation results based on ChatGPT's insights
"""

import os
import json
import glob
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict

class QECResultsAnalyzer:
    """Focused analyzer for QEC simulation results"""
    
    def __init__(self, logs_dir: str = "qec_research_logs"):
        self.logs_dir = logs_dir
        self.games_data = []
        self.analysis_results = {}
        
    def load_data(self):
        """Load all QEC simulation data"""
        print("Loading QEC simulation data...")
        
        # Find all result files
        result_files = []
        for pattern in ["**/*_result.json", "**/*_summary.json", "**/summary.csv"]:
            result_files.extend(glob.glob(os.path.join(self.logs_dir, pattern), recursive=True))
        
        print(f"Found {len(result_files)} result files")
        
        for file_path in result_files:
            try:
                if file_path.endswith('.csv'):
                    # Load CSV data
                    df = pd.read_csv(file_path)
                    for _, row in df.iterrows():
                        game_data = {
                            'game_id': row.get('game_id', 'unknown'),
                            'result': row.get('result', 'Unknown'),
                            'total_plies': row.get('total_plies', 0),
                            'white_archetype': row.get('white_archetype', 'Unknown'),
                            'black_archetype': row.get('black_archetype', 'Unknown'),
                            'forced_moves': row.get('forced_moves', 0),
                            'reactive_moves': row.get('reactive_moves', 0),
                            'reactive_mates': row.get('reactive_mates', 0),
                            'captures': row.get('captures', 0),
                            'entanglement_breaks': row.get('entanglement_breaks', 0)
                        }
                        self.games_data.append(game_data)
                else:
                    # Load JSON data
                    with open(file_path, 'r') as f:
                        if file_path.endswith('.json'):
                            data = json.load(f)
                            if isinstance(data, list):
                                self.games_data.extend(data)
                            else:
                                self.games_data.append(data)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        print(f"Loaded {len(self.games_data)} games")
    
    def analyze_chatgpt_patterns(self):
        """Analyze the specific patterns identified by ChatGPT"""
        if not self.games_data:
            print("No data loaded")
            return
        
        print("\n=== ChatGPT Pattern Analysis ===")
        
        # Basic statistics
        total_games = len(self.games_data)
        results = [g.get('result', 'Unknown') for g in self.games_data]
        result_counts = pd.Series(results).value_counts()
        
        print(f"Total games: {total_games}")
        print(f"Results: {dict(result_counts)}")
        
        # Calculate percentages
        draws = result_counts.get('Draw', 0)
        white_wins = result_counts.get('W wins', 0)
        black_wins = result_counts.get('B wins', 0)
        
        print(f"\nResult Distribution:")
        print(f"  Draws: {draws} ({draws/total_games*100:.1f}%)")
        print(f"  White wins: {white_wins} ({white_wins/total_games*100:.1f}%)")
        print(f"  Black wins: {black_wins} ({black_wins/total_games*100:.1f}%)")
        
        # Game length analysis
        plies = [g.get('total_plies', 0) for g in self.games_data]
        print(f"\nGame Length Analysis:")
        print(f"  Average plies: {np.mean(plies):.1f}")
        print(f"  Median plies: {np.median(plies):.1f}")
        print(f"  Range: {np.min(plies)} - {np.max(plies)} plies")
        
        # Entanglement analysis
        forced_moves = [g.get('forced_moves', 0) for g in self.games_data]
        reactive_moves = [g.get('reactive_moves', 0) for g in self.games_data]
        reactive_mates = [g.get('reactive_mates', 0) for g in self.games_data]
        captures = [g.get('captures', 0) for g in self.games_data]
        
        print(f"\nEntanglement Analysis:")
        print(f"  Total forced moves: {sum(forced_moves)}")
        print(f"  Total reactive moves: {sum(reactive_moves)}")
        print(f"  Total reactive mates: {sum(reactive_mates)}")
        print(f"  Total captures: {sum(captures)}")
        
        print(f"\nPer-Game Averages:")
        print(f"  Average forced moves: {np.mean(forced_moves):.1f}")
        print(f"  Average reactive moves: {np.mean(reactive_moves):.1f}")
        print(f"  Average reactive mates: {np.mean(reactive_mates):.1f}")
        print(f"  Average captures: {np.mean(captures):.1f}")
        
        # Color advantage analysis
        decisive_games = white_wins + black_wins
        if decisive_games > 0:
            white_advantage = white_wins / decisive_games * 100
            print(f"\nColor Advantage Analysis:")
            print(f"  Decisive rate: {decisive_games/total_games*100:.1f}%")
            print(f"  White advantage in decisive games: {white_advantage:.1f}%")
        
        # Archetype performance
        self._analyze_archetype_performance()
        
        # Entanglement stability analysis
        self._analyze_entanglement_stability()
        
        # Store results
        self.analysis_results = {
            'total_games': total_games,
            'draw_rate': draws/total_games*100,
            'decisive_rate': decisive_games/total_games*100,
            'white_advantage': white_advantage if decisive_games > 0 else 0,
            'avg_game_length': np.mean(plies),
            'total_reactive_moves': sum(reactive_moves),
            'total_forced_moves': sum(forced_moves),
            'reactive_forced_ratio': sum(reactive_moves)/max(1, sum(forced_moves))
        }
    
    def _analyze_archetype_performance(self):
        """Analyze archetype performance patterns"""
        print(f"\nArchetype Performance Analysis:")
        
        # Group by archetype
        archetype_stats = defaultdict(lambda: {
            "wins": 0, "losses": 0, "draws": 0, "games": 0,
            "avg_plies": 0, "avg_reactive": 0, "avg_forced": 0
        })
        
        for game in self.games_data:
            white_arch = game.get('white_archetype', 'Unknown')
            black_arch = game.get('black_archetype', 'Unknown')
            result = game.get('result', 'Unknown')
            
            # White archetype stats
            archetype_stats[white_arch]["games"] += 1
            archetype_stats[white_arch]["avg_plies"] += game.get('total_plies', 0)
            archetype_stats[white_arch]["avg_reactive"] += game.get('reactive_moves', 0)
            archetype_stats[white_arch]["avg_forced"] += game.get('forced_moves', 0)
            
            if result == 'W wins':
                archetype_stats[white_arch]["wins"] += 1
            elif result == 'B wins':
                archetype_stats[white_arch]["losses"] += 1
            else:
                archetype_stats[white_arch]["draws"] += 1
            
            # Black archetype stats
            archetype_stats[black_arch]["games"] += 1
            archetype_stats[black_arch]["avg_plies"] += game.get('total_plies', 0)
            archetype_stats[black_arch]["avg_reactive"] += game.get('reactive_moves', 0)
            archetype_stats[black_arch]["avg_forced"] += game.get('forced_moves', 0)
            
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
                stats["avg_reactive"] = stats["avg_reactive"] / stats["games"]
                stats["avg_forced"] = stats["avg_forced"] / stats["games"]
        
        # Print results
        print(f"{'Archetype':<15} {'Games':<6} {'Wins':<5} {'Win%':<6} {'Avg Plies':<10} {'Avg Reactive':<12}")
        print("-" * 70)
        
        sorted_archetypes = sorted(archetype_stats.items(), key=lambda x: x[1]["win_rate"], reverse=True)
        for arch, stats in sorted_archetypes:
            print(f"{arch:<15} {stats['games']:<6} {stats['wins']:<5} "
                  f"{stats['win_rate']:<6.1f} {stats['avg_plies']:<10.1f} {stats['avg_reactive']:<12.1f}")
    
    def _analyze_entanglement_stability(self):
        """Analyze entanglement stability patterns"""
        print(f"\nEntanglement Stability Analysis:")
        
        # Categorize games by entanglement activity
        low_activity = [g for g in self.games_data if g.get('reactive_moves', 0) < 10 and g.get('forced_moves', 0) == 0]
        high_activity = [g for g in self.games_data if g.get('reactive_moves', 0) > 20]
        medium_activity = [g for g in self.games_data if 10 <= g.get('reactive_moves', 0) <= 20]
        
        print(f"  Low entanglement activity: {len(low_activity)} games")
        print(f"  Medium entanglement activity: {len(medium_activity)} games")
        print(f"  High entanglement activity: {len(high_activity)} games")
        
        # Analyze game length by activity level
        for category, games in [("Low", low_activity), ("Medium", medium_activity), ("High", high_activity)]:
            if games:
                avg_plies = np.mean([g.get('total_plies', 0) for g in games])
                draw_rate = sum(1 for g in games if g.get('result') == 'Draw') / len(games) * 100
                print(f"    {category} activity: {avg_plies:.1f} avg plies, {draw_rate:.1f}% draws")
        
        # Correlation analysis
        reactive_moves = [g.get('reactive_moves', 0) for g in self.games_data]
        plies = [g.get('total_plies', 0) for g in self.games_data]
        forced_moves = [g.get('forced_moves', 0) for g in self.games_data]
        
        if len(reactive_moves) > 1:
            reactive_correlation = np.corrcoef(reactive_moves, plies)[0,1]
            print(f"\nCorrelation Analysis:")
            print(f"  Reactive moves vs game length: {reactive_correlation:.3f}")
            
            if len(forced_moves) > 1:
                forced_correlation = np.corrcoef(forced_moves, plies)[0,1]
                print(f"  Forced moves vs game length: {forced_correlation:.3f}")
    
    def test_hypotheses(self):
        """Test specific hypotheses based on ChatGPT's analysis"""
        print(f"\n=== Hypothesis Testing ===")
        
        if not self.games_data:
            print("No data available for hypothesis testing")
            return
        
        # H1: Opening Determinism
        print(f"\nH1: Opening Determinism")
        print(f"  Prediction: First move has exponentially greater impact")
        print(f"  Evidence: Need more sophisticated analysis of first move effects")
        
        # H2: Free-Pawn Centrality  
        print(f"\nH2: Free-Pawn Centrality")
        print(f"  Prediction: Central free pawns correlate with higher win rates")
        print(f"  Evidence: Need free pawn file data to test")
        
        # H4: Second-Player Advantage
        print(f"\nH4: Second-Player Advantage")
        white_wins = sum(1 for g in self.games_data if g.get('result') == 'W wins')
        black_wins = sum(1 for g in self.games_data if g.get('result') == 'B wins')
        decisive_games = white_wins + black_wins
        
        if decisive_games > 0:
            white_advantage = white_wins / decisive_games
            print(f"  Prediction: Black (second player) has advantage")
            print(f"  Evidence: White advantage = {white_advantage:.1%} (opposite of prediction)")
        else:
            print(f"  Evidence: No decisive games to test")
        
        # H5: Entanglement Stability vs Breakage
        print(f"\nH5: Entanglement Stability vs Breakage")
        print(f"  Prediction: Stable entanglement → longer games, breakage → tactical games")
        
        # Analyze by entanglement activity
        low_activity = [g for g in self.games_data if g.get('reactive_moves', 0) < 10]
        high_activity = [g for g in self.games_data if g.get('reactive_moves', 0) > 20]
        
        if low_activity and high_activity:
            low_avg_plies = np.mean([g.get('total_plies', 0) for g in low_activity])
            high_avg_plies = np.mean([g.get('total_plies', 0) for g in high_activity])
            print(f"  Evidence: Low activity avg {low_avg_plies:.1f} plies, high activity avg {high_avg_plies:.1f} plies")
        
        # H6: Reactive-Check Survival Bias
        print(f"\nH6: Reactive-Check Survival Bias")
        print(f"  Prediction: More reactive checks → shorter games")
        
        reactive_moves = [g.get('reactive_moves', 0) for g in self.games_data]
        plies = [g.get('total_plies', 0) for g in self.games_data]
        
        if len(reactive_moves) > 1:
            correlation = np.corrcoef(reactive_moves, plies)[0,1]
            print(f"  Evidence: Reactive moves vs game length correlation = {correlation:.3f}")
            if correlation < 0:
                print(f"    → Supports hypothesis (negative correlation)")
            else:
                print(f"    → Contradicts hypothesis (positive correlation)")
    
    def create_summary_table(self):
        """Create summary table of key findings"""
        if not self.analysis_results:
            print("No analysis results available")
            return
        
        print(f"\n=== QEC Analysis Summary ===")
        print(f"Total games analyzed: {self.analysis_results['total_games']}")
        print(f"Draw rate: {self.analysis_results['draw_rate']:.1f}%")
        print(f"Decisive rate: {self.analysis_results['decisive_rate']:.1f}%")
        print(f"White advantage: {self.analysis_results['white_advantage']:.1f}%")
        print(f"Average game length: {self.analysis_results['avg_game_length']:.1f} plies")
        print(f"Reactive/forced ratio: {self.analysis_results['reactive_forced_ratio']:.1f}")
        
        # Save results
        with open('qec_analysis_summary.json', 'w') as f:
            json.dump(self.analysis_results, f, indent=2)
        print(f"\nSummary saved to qec_analysis_summary.json")
    
    def run_analysis(self):
        """Run complete analysis"""
        print("=== QEC Results Analysis ===")
        
        # Load data
        self.load_data()
        
        if not self.games_data:
            print("No data found to analyze")
            return
        
        # Run analyses
        self.analyze_chatgpt_patterns()
        self.test_hypotheses()
        self.create_summary_table()
        
        print(f"\nAnalysis complete!")

if __name__ == "__main__":
    # Run analysis
    analyzer = QECResultsAnalyzer()
    analyzer.run_analysis()
