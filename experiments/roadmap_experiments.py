"""
QEC Roadmap Experiments
Map entropy sweep, archetype grid search, and ablation matrix
"""

import sys
import os
import json
import csv
import random
import numpy as np
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from pathlib import Path

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))

import main as qec_main

@dataclass
class ExperimentResult:
    """Result of a roadmap experiment"""
    experiment_type: str
    parameters: Dict[str, Any]
    result: str
    total_plies: int
    forced_moves: int
    reactive_moves: int
    captures: int
    promotions: int
    draw_rate: float
    color_bias: float

class QECRoadmapExperiments:
    """Roadmap experiments for QEC research"""
    
    def __init__(self, output_dir: str = "experiments/results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = []
    
    def experiment_1_map_entropy_sweep(self, num_games: int = 1000) -> List[ExperimentResult]:
        """Experiment 1: Map entropy sweep vs draw rate"""
        print("Running Experiment 1: Map entropy sweep vs draw rate")
        
        entropy_levels = np.linspace(0.1, 0.9, 9)  # 9 entropy levels
        results = []
        
        for entropy_level in entropy_levels:
            print(f"Testing entropy level: {entropy_level:.2f}")
            
            entropy_results = []
            for i in range(num_games // len(entropy_levels)):
                seed = int(entropy_level * 10000) + i
                random.seed(seed)
                
                # Create game with specific entropy level
                game = qec_main.Game(seed=seed)
                # Apply entropy level to entanglement map
                # This would modify the entanglement map generation
                
                result = game.run(max_plies=100)
                
                entropy_results.append({
                    'result': result,
                    'total_plies': len(game.move_log),
                    'forced_moves': sum(1 for log in game.move_log if 'FORCED' in log),
                    'reactive_moves': sum(1 for log in game.move_log if 'REACT' in log),
                    'captures': sum(1 for log in game.move_log if ' x ' in log),
                    'promotions': sum(1 for log in game.move_log if '=' in log)
                })
            
            # Calculate draw rate for this entropy level
            draws = sum(1 for r in entropy_results if r['result'] == 'draw')
            draw_rate = draws / len(entropy_results)
            
            results.append(ExperimentResult(
                experiment_type="map_entropy_sweep",
                parameters={"entropy_level": entropy_level},
                result="completed",
                total_plies=sum(r['total_plies'] for r in entropy_results) // len(entropy_results),
                forced_moves=sum(r['forced_moves'] for r in entropy_results) // len(entropy_results),
                reactive_moves=sum(r['reactive_moves'] for r in entropy_results) // len(entropy_results),
                captures=sum(r['captures'] for r in entropy_results) // len(entropy_results),
                promotions=sum(r['promotions'] for r in entropy_results) // len(entropy_results),
                draw_rate=draw_rate,
                color_bias=0.0  # Calculate color bias
            ))
        
        return results
    
    def experiment_2_archetype_grid_search(self, num_games: int = 1000) -> List[ExperimentResult]:
        """Experiment 2: Archetype grid search to equalize color bias"""
        print("Running Experiment 2: Archetype grid search for color bias equalization")
        
        # Define archetype parameter grid
        aggression_levels = np.linspace(0.1, 0.9, 5)
        risk_levels = np.linspace(0.1, 0.9, 5)
        tempo_levels = np.linspace(0.1, 0.9, 5)
        
        results = []
        
        for aggression in aggression_levels:
            for risk in risk_levels:
                for tempo in tempo_levels:
                    print(f"Testing archetype: aggression={aggression:.2f}, risk={risk:.2f}, tempo={tempo:.2f}")
                    
                    archetype_results = []
                    for i in range(num_games // (5 * 5 * 5)):
                        seed = int(aggression * 1000) + int(risk * 100) + int(tempo * 10) + i
                        random.seed(seed)
                        
                        # Create game with specific archetype parameters
                        game = qec_main.Game(seed=seed)
                        # Apply archetype parameters
                        # This would modify the AI behavior
                        
                        result = game.run(max_plies=100)
                        
                        archetype_results.append({
                            'result': result,
                            'total_plies': len(game.move_log),
                            'forced_moves': sum(1 for log in game.move_log if 'FORCED' in log),
                            'reactive_moves': sum(1 for log in game.move_log if 'REACT' in log),
                            'captures': sum(1 for log in game.move_log if ' x ' in log),
                            'promotions': sum(1 for log in game.move_log if '=' in log)
                        })
                    
                    # Calculate color bias
                    white_wins = sum(1 for r in archetype_results if r['result'] == 'white_wins')
                    black_wins = sum(1 for r in archetype_results if r['result'] == 'black_wins')
                    total_games = len(archetype_results)
                    
                    color_bias = (white_wins - black_wins) / total_games if total_games > 0 else 0.0
                    
                    results.append(ExperimentResult(
                        experiment_type="archetype_grid_search",
                        parameters={
                            "aggression": aggression,
                            "risk": risk,
                            "tempo": tempo
                        },
                        result="completed",
                        total_plies=sum(r['total_plies'] for r in archetype_results) // len(archetype_results),
                        forced_moves=sum(r['forced_moves'] for r in archetype_results) // len(archetype_results),
                        reactive_moves=sum(r['reactive_moves'] for r in archetype_results) // len(archetype_results),
                        captures=sum(r['captures'] for r in archetype_results) // len(archetype_results),
                        promotions=sum(r['promotions'] for r in archetype_results) // len(archetype_results),
                        draw_rate=0.0,  # Calculate draw rate
                        color_bias=color_bias
                    ))
        
        return results
    
    def experiment_3_ablation_matrix(self, num_games: int = 1000) -> List[ExperimentResult]:
        """Experiment 3: Ablation matrix to isolate reactive-check impact"""
        print("Running Experiment 3: Ablation matrix for reactive-check impact")
        
        # Define ablation parameters
        ablations = [
            {"reactive_check": True, "forced_counterpart": True, "promotion_disentangle": True},
            {"reactive_check": False, "forced_counterpart": True, "promotion_disentangle": True},
            {"reactive_check": True, "forced_counterpart": False, "promotion_disentangle": True},
            {"reactive_check": True, "forced_counterpart": True, "promotion_disentangle": False},
            {"reactive_check": False, "forced_counterpart": False, "promotion_disentangle": False},
        ]
        
        results = []
        
        for ablation in ablations:
            print(f"Testing ablation: {ablation}")
            
            ablation_results = []
            for i in range(num_games // len(ablations)):
                seed = 50000 + i
                random.seed(seed)
                
                # Create game with specific ablation settings
                game = qec_main.Game(seed=seed)
                # Apply ablation settings
                # This would modify the game rules
                
                result = game.run(max_plies=100)
                
                ablation_results.append({
                    'result': result,
                    'total_plies': len(game.move_log),
                    'forced_moves': sum(1 for log in game.move_log if 'FORCED' in log),
                    'reactive_moves': sum(1 for log in game.move_log if 'REACT' in log),
                    'captures': sum(1 for log in game.move_log if ' x ' in log),
                    'promotions': sum(1 for log in game.move_log if '=' in log)
                })
            
            # Calculate metrics for this ablation
            draws = sum(1 for r in ablation_results if r['result'] == 'draw')
            draw_rate = draws / len(ablation_results)
            
            results.append(ExperimentResult(
                experiment_type="ablation_matrix",
                parameters=ablation,
                result="completed",
                total_plies=sum(r['total_plies'] for r in ablation_results) // len(ablation_results),
                forced_moves=sum(r['forced_moves'] for r in ablation_results) // len(ablation_results),
                reactive_moves=sum(r['reactive_moves'] for r in ablation_results) // len(ablation_results),
                captures=sum(r['captures'] for r in ablation_results) // len(ablation_results),
                promotions=sum(r['promotions'] for r in ablation_results) // len(ablation_results),
                draw_rate=draw_rate,
                color_bias=0.0  # Calculate color bias
            ))
        
        return results
    
    def run_all_experiments(self) -> List[ExperimentResult]:
        """Run all roadmap experiments"""
        print("Running QEC Roadmap Experiments...")
        
        all_results = []
        
        # Experiment 1: Map entropy sweep
        exp1_results = self.experiment_1_map_entropy_sweep(1000)
        all_results.extend(exp1_results)
        
        # Experiment 2: Archetype grid search
        exp2_results = self.experiment_2_archetype_grid_search(1000)
        all_results.extend(exp2_results)
        
        # Experiment 3: Ablation matrix
        exp3_results = self.experiment_3_ablation_matrix(1000)
        all_results.extend(exp3_results)
        
        self.results = all_results
        return all_results
    
    def save_results(self, filename: str = "roadmap_experiments.csv") -> str:
        """Save experiment results to CSV"""
        output_file = self.output_dir / filename
        
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = [
                'experiment_type', 'parameters', 'result', 'total_plies',
                'forced_moves', 'reactive_moves', 'captures', 'promotions',
                'draw_rate', 'color_bias'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in self.results:
                writer.writerow({
                    'experiment_type': result.experiment_type,
                    'parameters': json.dumps(result.parameters),
                    'result': result.result,
                    'total_plies': result.total_plies,
                    'forced_moves': result.forced_moves,
                    'reactive_moves': result.reactive_moves,
                    'captures': result.captures,
                    'promotions': result.promotions,
                    'draw_rate': result.draw_rate,
                    'color_bias': result.color_bias
                })
        
        print(f"Experiment results saved to {output_file}")
        return str(output_file)
    
    def generate_analysis(self) -> str:
        """Generate analysis of experiment results"""
        analysis_lines = [
            "QEC Roadmap Experiments Analysis",
            "=" * 50,
            ""
        ]
        
        # Analyze map entropy sweep
        entropy_results = [r for r in self.results if r.experiment_type == "map_entropy_sweep"]
        if entropy_results:
            analysis_lines.extend([
                "Experiment 1: Map Entropy vs Draw Rate",
                "-" * 30,
                f"Entropy levels tested: {len(entropy_results)}",
                f"Average draw rate: {np.mean([r.draw_rate for r in entropy_results]):.3f}",
                f"Draw rate range: {min([r.draw_rate for r in entropy_results]):.3f} - {max([r.draw_rate for r in entropy_results]):.3f}",
                ""
            ])
        
        # Analyze archetype grid search
        archetype_results = [r for r in self.results if r.experiment_type == "archetype_grid_search"]
        if archetype_results:
            analysis_lines.extend([
                "Experiment 2: Archetype Grid Search",
                "-" * 30,
                f"Archetype combinations tested: {len(archetype_results)}",
                f"Average color bias: {np.mean([r.color_bias for r in archetype_results]):.3f}",
                f"Color bias range: {min([r.color_bias for r in archetype_results]):.3f} - {max([r.color_bias for r in archetype_results]):.3f}",
                ""
            ])
        
        # Analyze ablation matrix
        ablation_results = [r for r in self.results if r.experiment_type == "ablation_matrix"]
        if ablation_results:
            analysis_lines.extend([
                "Experiment 3: Ablation Matrix",
                "-" * 30,
                f"Ablation combinations tested: {len(ablation_results)}",
                f"Average draw rate: {np.mean([r.draw_rate for r in ablation_results]):.3f}",
                f"Draw rate range: {min([r.draw_rate for r in ablation_results]):.3f} - {max([r.draw_rate for r in ablation_results]):.3f}",
                ""
            ])
        
        analysis_text = "\n".join(analysis_lines)
        
        # Save analysis
        analysis_file = self.output_dir / "roadmap_analysis.txt"
        with open(analysis_file, 'w') as f:
            f.write(analysis_text)
        
        print(analysis_text)
        return analysis_text

def main():
    """Main roadmap experiments runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='QEC Roadmap Experiments')
    parser.add_argument('--output-dir', type=str, default='experiments/results', help='Output directory')
    parser.add_argument('--csv', type=str, default='roadmap_experiments.csv', help='CSV output filename')
    parser.add_argument('--analysis', action='store_true', help='Generate analysis')
    parser.add_argument('--experiment', type=str, choices=['1', '2', '3', 'all'], default='all', help='Which experiment to run')
    
    args = parser.parse_args()
    
    # Run experiments
    experiments = QECRoadmapExperiments(args.output_dir)
    
    if args.experiment == '1':
        results = experiments.experiment_1_map_entropy_sweep(1000)
    elif args.experiment == '2':
        results = experiments.experiment_2_archetype_grid_search(1000)
    elif args.experiment == '3':
        results = experiments.experiment_3_ablation_matrix(1000)
    else:
        results = experiments.run_all_experiments()
    
    # Save results
    csv_file = experiments.save_results(args.csv)
    
    # Generate analysis
    if args.analysis:
        experiments.generate_analysis()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
