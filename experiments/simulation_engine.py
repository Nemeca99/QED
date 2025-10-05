"""
Advanced QEC Simulation Engine
Realistic tournament simulation with statistical analysis and visualization
"""

import os
import json
import time
import random
import statistics
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import pandas as pd
import numpy as np
from tqdm import tqdm
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from tabulate import tabulate

from main import Game, Color

@dataclass
class GameResult:
    """Structured game result with detailed metrics"""
    game_id: int
    policy_w: str
    policy_b: str
    result: str
    moves: int
    duration: float
    final_eval_w: float
    final_eval_b: float
    ent_breaks: int
    forced_moves: int
    reactive_moves: int
    captures: int
    promotions: int
    checks: int
    mate_type: Optional[str] = None
    opening_moves: List[str] = None
    endgame_moves: List[str] = None

@dataclass
class PolicyStats:
    """Statistics for a specific policy"""
    policy: str
    games_played: int
    wins: int
    losses: int
    draws: int
    win_rate: float
    avg_moves: float
    avg_duration: float
    avg_eval: float
    forced_accuracy: float
    reactive_accuracy: float

class QECSimulator:
    """Advanced QEC simulation with statistical analysis"""
    
    def __init__(self, output_dir: str = "simulation_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.console = Console()
        
        # Available policies for realistic simulation
        self.policies = {
            "random": {"name": "Random", "depth": 0},
            "heuristic": {"name": "Heuristic", "depth": 1}, 
            "minimax_2": {"name": "Minimax-2", "depth": 2},
            "minimax_3": {"name": "Minimax-3", "depth": 3},
            "minimax_4": {"name": "Minimax-4", "depth": 4}
        }
        
        self.results: List[GameResult] = []
        self.policy_stats: Dict[str, PolicyStats] = {}
        
    def run_tournament(self, 
                      games_per_matchup: int = 10,
                      policies: List[str] = None,
                      seed_base: int = 42,
                      map_file: str = "sample_mapping.json") -> None:
        """Run comprehensive tournament simulation"""
        
        if policies is None:
            policies = list(self.policies.keys())
            
        self.console.print(f"[bold blue]Starting QEC Tournament Simulation[/bold blue]")
        self.console.print(f"Policies: {', '.join(policies)}")
        self.console.print(f"Games per matchup: {games_per_matchup}")
        
        total_games = len(policies) * len(policies) * games_per_matchup
        game_id = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            
            main_task = progress.add_task("Tournament Progress", total=total_games)
            
            for policy_w in policies:
                for policy_b in policies:
                    for game_num in range(games_per_matchup):
                        game_id += 1
                        seed = seed_base + game_id
                        
                        result = self._play_single_game(
                            game_id, policy_w, policy_b, seed, map_file
                        )
                        self.results.append(result)
                        
                        progress.update(main_task, advance=1, 
                                      description=f"Game {game_id}/{total_games}: {policy_w} vs {policy_b}")
        
        self._analyze_results()
        self._generate_reports()
        
    def _play_single_game(self, game_id: int, policy_w: str, policy_b: str, 
                         seed: int, map_file: str) -> GameResult:
        """Play a single game with detailed tracking"""
        
        start_time = time.time()
        
        # Set up game with specific policies
        os.environ["QEC_POLICY"] = policy_w
        os.environ["QEC_MAP"] = open(map_file, "r").read() if os.path.exists(map_file) else ""
        
        game = Game(seed=seed)
        game.policy = policy_w
        
        # Track detailed metrics
        forced_count = 0
        reactive_count = 0
        capture_count = 0
        promotion_count = 0
        check_count = 0
        ent_break_count = 0
        opening_moves = []
        endgame_moves = []
        
        # Play game with detailed tracking
        for move_num in range(600):  # Max moves
            res = game._play_turn()
            
            # Track move types from transcript
            if game.transcript:
                last_entry = game.transcript[-1]
                if last_entry["kind"] == "forced":
                    forced_count += 1
                elif last_entry["kind"] == "reactive":
                    reactive_count += 1
                    
                # Track captures and promotions
                if last_entry.get("capture_id"):
                    capture_count += 1
                if last_entry.get("moved_kind") == "Q" and "promotion" in str(last_entry):
                    promotion_count += 1
                    
                # Track checks
                if last_entry.get("check_W") or last_entry.get("check_B"):
                    check_count += 1
                    
                # Track entanglement breaks
                if last_entry.get("ent_map", {}).get("changed"):
                    ent_break_count += 1
                    
                # Store opening and endgame moves
                if move_num < 10:
                    opening_moves.append(f"{last_entry.get('from', '?')}-{last_entry.get('to', '?')}")
                if move_num >= len(game.transcript) - 10:
                    endgame_moves.append(f"{last_entry.get('from', '?')}-{last_entry.get('to', '?')}")
            
            if res is not None:
                break
                
        duration = time.time() - start_time
        
        # Determine result and mate type
        result_str = res if res else "Draw by move limit"
        mate_type = None
        if "Checkmate" in result_str:
            mate_type = "checkmate"
        elif "Stalemate" in result_str:
            mate_type = "stalemate"
        elif "move limit" in result_str:
            mate_type = "timeout"
            
        # Get final evaluations
        final_eval_w = game._evaluate("W")
        final_eval_b = game._evaluate("B")
        
        return GameResult(
            game_id=game_id,
            policy_w=policy_w,
            policy_b=policy_b,
            result=result_str,
            moves=len(game.transcript),
            duration=duration,
            final_eval_w=final_eval_w,
            final_eval_b=final_eval_b,
            ent_breaks=ent_break_count,
            forced_moves=forced_count,
            reactive_moves=reactive_count,
            captures=capture_count,
            promotions=promotion_count,
            checks=check_count,
            mate_type=mate_type,
            opening_moves=opening_moves,
            endgame_moves=endgame_moves
        )
    
    def _analyze_results(self) -> None:
        """Analyze results and compute policy statistics"""
        
        df = pd.DataFrame([asdict(r) for r in self.results])
        
        for policy in self.policies.keys():
            policy_data = df[(df['policy_w'] == policy) | (df['policy_b'] == policy)]
            
            if len(policy_data) == 0:
                continue
                
            # Calculate wins/losses/draws
            wins = 0
            losses = 0
            draws = 0
            
            for _, row in policy_data.iterrows():
                if row['policy_w'] == policy:
                    if "W wins" in row['result']:
                        wins += 1
                    elif "B wins" in row['result']:
                        losses += 1
                    else:
                        draws += 1
                else:  # policy_b
                    if "B wins" in row['result']:
                        wins += 1
                    elif "W wins" in row['result']:
                        losses += 1
                    else:
                        draws += 1
            
            # Calculate statistics
            games_played = len(policy_data)
            win_rate = wins / games_played if games_played > 0 else 0
            avg_moves = policy_data['moves'].mean()
            avg_duration = policy_data['duration'].mean()
            
            # Average evaluation (positive for wins, negative for losses)
            eval_data = []
            for _, row in policy_data.iterrows():
                if row['policy_w'] == policy:
                    eval_data.append(row['final_eval_w'])
                else:
                    eval_data.append(row['final_eval_b'])
            avg_eval = statistics.mean(eval_data) if eval_data else 0
            
            # Forced and reactive accuracy (simplified)
            forced_accuracy = 0.8  # Placeholder - would need deeper analysis
            reactive_accuracy = 0.7  # Placeholder
            
            self.policy_stats[policy] = PolicyStats(
                policy=policy,
                games_played=games_played,
                wins=wins,
                losses=losses,
                draws=draws,
                win_rate=win_rate,
                avg_moves=avg_moves,
                avg_duration=avg_duration,
                avg_eval=avg_eval,
                forced_accuracy=forced_accuracy,
                reactive_accuracy=reactive_accuracy
            )
    
    def _generate_reports(self) -> None:
        """Generate comprehensive analysis reports"""
        
        # Save raw results
        results_df = pd.DataFrame([asdict(r) for r in self.results])
        results_df.to_csv(self.output_dir / "detailed_results.csv", index=False)
        
        # Policy comparison table
        self._print_policy_comparison()
        
        # Statistical analysis
        self._generate_statistical_analysis()
        
        # Game length analysis
        self._analyze_game_lengths()
        
        # Opening analysis
        self._analyze_openings()
        
        # Save summary
        self._save_summary_report()
        
    def _print_policy_comparison(self) -> None:
        """Print policy comparison table"""
        
        table = Table(title="Policy Performance Comparison")
        table.add_column("Policy", style="cyan")
        table.add_column("Games", justify="right")
        table.add_column("Win Rate", justify="right")
        table.add_column("Avg Moves", justify="right")
        table.add_column("Avg Duration", justify="right")
        table.add_column("Avg Eval", justify="right")
        
        for policy, stats in self.policy_stats.items():
            table.add_row(
                self.policies[policy]["name"],
                str(stats.games_played),
                f"{stats.win_rate:.1%}",
                f"{stats.avg_moves:.1f}",
                f"{stats.avg_duration:.2f}s",
                f"{stats.avg_eval:.1f}"
            )
        
        self.console.print(table)
    
    def _generate_statistical_analysis(self) -> None:
        """Generate detailed statistical analysis"""
        
        df = pd.DataFrame([asdict(r) for r in self.results])
        
        # Game length distribution
        move_counts = df['moves'].value_counts().sort_index()
        
        # Result distribution
        result_counts = df['result'].value_counts()
        
        # Policy head-to-head
        h2h_table = pd.crosstab(df['policy_w'], df['policy_b'], 
                               values=df['result'], aggfunc='count', fill_value=0)
        
        # Save analysis
        with open(self.output_dir / "statistical_analysis.txt", "w") as f:
            f.write("QEC Statistical Analysis\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("Game Length Distribution:\n")
            f.write(str(move_counts) + "\n\n")
            
            f.write("Result Distribution:\n")
            f.write(str(result_counts) + "\n\n")
            
            f.write("Policy Head-to-Head:\n")
            f.write(str(h2h_table) + "\n\n")
    
    def _analyze_game_lengths(self) -> None:
        """Analyze game length patterns"""
        
        df = pd.DataFrame([asdict(r) for r in self.results])
        
        # Game length by policy
        length_by_policy = df.groupby('policy_w')['moves'].agg(['mean', 'std', 'min', 'max'])
        
        with open(self.output_dir / "game_length_analysis.txt", "w") as f:
            f.write("Game Length Analysis\n")
            f.write("=" * 30 + "\n\n")
            f.write("Length by Policy:\n")
            f.write(str(length_by_policy) + "\n\n")
    
    def _analyze_openings(self) -> None:
        """Analyze opening patterns"""
        
        # Extract opening moves
        all_openings = []
        for result in self.results:
            if result.opening_moves:
                all_openings.extend(result.opening_moves[:5])  # First 5 moves
        
        # Count opening patterns
        opening_counts = pd.Series(all_openings).value_counts()
        
        with open(self.output_dir / "opening_analysis.txt", "w") as f:
            f.write("Opening Analysis\n")
            f.write("=" * 20 + "\n\n")
            f.write("Most Common Opening Moves:\n")
            f.write(str(opening_counts.head(20)) + "\n\n")
    
    def _save_summary_report(self) -> None:
        """Save comprehensive summary report"""
        
        df = pd.DataFrame([asdict(r) for r in self.results])
        
        summary = {
            "total_games": len(self.results),
            "policies_tested": list(self.policies.keys()),
            "average_game_length": df['moves'].mean(),
            "average_duration": df['duration'].mean(),
            "result_distribution": df['result'].value_counts().to_dict(),
            "policy_performance": {k: {
                "win_rate": v.win_rate,
                "avg_moves": v.avg_moves,
                "avg_duration": v.avg_duration
            } for k, v in self.policy_stats.items()}
        }
        
        with open(self.output_dir / "summary_report.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        self.console.print(f"[green]Simulation complete! Results saved to {self.output_dir}[/green]")

def main():
    """Run realistic QEC simulation"""
    
    simulator = QECSimulator()
    
    # Run comprehensive tournament
    simulator.run_tournament(
        games_per_matchup=20,  # 20 games per policy matchup
        policies=["random", "heuristic", "minimax_2", "minimax_3"],
        seed_base=42
    )

if __name__ == "__main__":
    main()
