"""
Parameter Sweep Runner for QEC Research
Systematic exploration of archetype parameters and map entropy
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))

import main as qec_main
import json
import csv
import random
import itertools
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import numpy as np

@dataclass
class ArchetypeVector:
    """Archetype parameter vector"""
    aggression: float
    risk: float
    tempo: float
    king_safety: float
    pawn_control: float
    disentangle_bias: float
    complexity: float
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary"""
        return {
            'aggression': self.aggression,
            'risk': self.risk,
            'tempo': self.tempo,
            'king_safety': self.king_safety,
            'pawn_control': self.pawn_control,
            'disentangle_bias': self.disentangle_bias,
            'complexity': self.complexity
        }

@dataclass
class MapEntropyConfig:
    """Entanglement map entropy configuration"""
    entropy_level: float  # 0.0 to 1.0
    clustering_factor: float  # 0.0 to 1.0
    symmetry_bias: float  # 0.0 to 1.0
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary"""
        return {
            'entropy_level': self.entropy_level,
            'clustering_factor': self.clustering_factor,
            'symmetry_bias': self.symmetry_bias
        }

@dataclass
class SweepResult:
    """Result of a parameter sweep experiment"""
    experiment_id: str
    white_archetype: ArchetypeVector
    black_archetype: ArchetypeVector
    map_entropy: MapEntropyConfig
    seed: int
    result: str
    total_plies: int
    forced_moves: int
    reactive_moves: int
    captures: int
    promotions: int
    final_fen: str
    outcome_hash: str

class QECParameterSweep:
    """Parameter sweep runner for QEC research"""
    
    def __init__(self, output_file: str = "parameter_sweep_results.csv"):
        self.output_file = output_file
        self.manifest_file = output_file.replace('.csv', '_manifest.json')
        self.results = []
        self.experiment_count = 0
        self.completed_seeds = set()
    
    def generate_archetype_grid(self, num_points: int = 5) -> List[ArchetypeVector]:
        """Generate grid of archetype vectors"""
        archetypes = []
        
        # Create parameter ranges
        param_ranges = {
            'aggression': np.linspace(0.1, 0.9, num_points),
            'risk': np.linspace(0.1, 0.9, num_points),
            'tempo': np.linspace(0.1, 0.9, num_points),
            'king_safety': np.linspace(0.1, 0.9, num_points),
            'pawn_control': np.linspace(0.1, 0.9, num_points),
            'disentangle_bias': np.linspace(0.1, 0.9, num_points),
            'complexity': np.linspace(0.1, 0.9, num_points)
        }
        
        # Generate combinations (sample to avoid explosion)
        param_names = list(param_ranges.keys())
        param_values = list(param_ranges.values())
        
        # Sample combinations
        for _ in range(num_points * 2):  # 2x oversampling
            params = {}
            for name, values in param_ranges.items():
                params[name] = random.choice(values)
            
            archetype = ArchetypeVector(**params)
            archetypes.append(archetype)
        
        return archetypes
    
    def generate_entropy_configs(self, num_configs: int = 10) -> List[MapEntropyConfig]:
        """Generate entropy configurations"""
        configs = []
        
        for _ in range(num_configs):
            config = MapEntropyConfig(
                entropy_level=random.uniform(0.1, 0.9),
                clustering_factor=random.uniform(0.1, 0.9),
                symmetry_bias=random.uniform(0.1, 0.9)
            )
            configs.append(config)
        
        return configs
    
    def run_single_experiment(self, white_archetype: ArchetypeVector, 
                            black_archetype: ArchetypeVector,
                            map_entropy: MapEntropyConfig,
                            seed: int) -> SweepResult:
        """Run a single parameter sweep experiment"""
        self.experiment_count += 1
        experiment_id = f"exp_{self.experiment_count:06d}"
        
        # Create game with custom parameters
        game = qec_main.Game(seed=seed)
        
        # Apply archetype parameters (this would be implemented in the actual game)
        # For now, we'll simulate the game
        result = game.run(max_plies=100)
        
        # Collect metrics
        forced_moves = sum(1 for log in game.move_log if 'FORCED' in log)
        reactive_moves = sum(1 for log in game.move_log if 'REACT' in log)
        captures = sum(1 for log in game.move_log if ' x ' in log)
        promotions = sum(1 for log in game.move_log if '=' in log)
        
        # Create outcome hash
        outcome_data = {
            'result': result,
            'total_plies': len(game.move_log),
            'forced_moves': forced_moves,
            'reactive_moves': reactive_moves,
            'captures': captures,
            'promotions': promotions,
            'final_fen': game.board.to_fen()
        }
        outcome_hash = hash(json.dumps(outcome_data, sort_keys=True)) % 1000000
        
        return SweepResult(
            experiment_id=experiment_id,
            white_archetype=white_archetype,
            black_archetype=black_archetype,
            map_entropy=map_entropy,
            seed=seed,
            result=result,
            total_plies=len(game.move_log),
            forced_moves=forced_moves,
            reactive_moves=reactive_moves,
            captures=captures,
            promotions=promotions,
            final_fen=game.board.to_fen(),
            outcome_hash=outcome_hash
        )
    
    def load_manifest(self):
        """Load completed seeds from manifest"""
        try:
            with open(self.manifest_file, 'r') as f:
                manifest = json.load(f)
                self.completed_seeds = set(manifest.get('completed_seeds', []))
                print(f"Loaded manifest: {len(self.completed_seeds)} completed seeds")
        except FileNotFoundError:
            print("No manifest found, starting fresh")
            self.completed_seeds = set()
    
    def save_manifest(self):
        """Save completed seeds to manifest"""
        manifest = {
            'completed_seeds': list(self.completed_seeds),
            'total_experiments': len(self.results),
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
    
    def run_parameter_sweep(self, num_archetypes: int = 10, num_entropy_configs: int = 5, 
                          num_games_per_config: int = 3, seed_base: int = 42, resume: bool = False):
        """Run parameter sweep experiments with resume support"""
        if resume:
            self.load_manifest()
        
        print(f"Running parameter sweep with {num_archetypes} archetypes, {num_entropy_configs} entropy configs, {num_games_per_config} games per config")
        
        # Generate parameter grids
        archetypes = self.generate_archetype_grid(num_archetypes)
        entropy_configs = self.generate_entropy_configs(num_entropy_configs)
        
        print(f"Generated {len(archetypes)} archetypes and {len(entropy_configs)} entropy configs")
        
        # Run experiments
        total_experiments = len(archetypes) * len(entropy_configs) * num_games_per_config
        print(f"Total experiments: {total_experiments}")
        
        if resume:
            print(f"Skipping {len(self.completed_seeds)} already completed experiments")
        
        experiment_num = 0
        skipped = 0
        
        for white_archetype in archetypes:
            for black_archetype in archetypes:
                for map_entropy in entropy_configs:
                    for game_num in range(num_games_per_config):
                        seed = seed_base + experiment_num
                        
                        # Skip if already completed
                        if resume and seed in self.completed_seeds:
                            skipped += 1
                            experiment_num += 1
                            continue
                        
                        print(f"Running experiment {experiment_num + 1}/{total_experiments} (seed={seed})")
                        
                        result = self.run_single_experiment(
                            white_archetype, black_archetype, map_entropy, seed
                        )
                        self.results.append(result)
                        self.completed_seeds.add(seed)
                        
                        # Save progress periodically
                        if experiment_num % 10 == 0:
                            self.save_manifest()
                        
                        experiment_num += 1
        
        print(f"Completed {len(self.results)} experiments (skipped {skipped} already completed)")
        self.save_manifest()
    
    def save_results(self):
        """Save results to CSV with explicit columns"""
        print(f"Saving results to {self.output_file}")
        
        with open(self.output_file, 'w', newline='') as csvfile:
            # Explicit column order as requested
            fieldnames = [
                'map_entropy', 'arch_vector', 'seed', 'result', 'plies', 'forced', 'reactive',
                'experiment_id', 'captures', 'promotions', 'final_fen', 'outcome_hash',
                'white_aggression', 'white_risk', 'white_tempo', 'white_king_safety',
                'white_pawn_control', 'white_disentangle_bias', 'white_complexity',
                'black_aggression', 'black_risk', 'black_tempo', 'black_king_safety',
                'black_pawn_control', 'black_disentangle_bias', 'black_complexity',
                'entropy_level', 'clustering_factor', 'symmetry_bias'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in self.results:
                # Create arch_vector string
                arch_vector = f"W({result.white_archetype.aggression:.2f},{result.white_archetype.risk:.2f},{result.white_archetype.tempo:.2f})_B({result.black_archetype.aggression:.2f},{result.black_archetype.risk:.2f},{result.black_archetype.tempo:.2f})"
                
                row = {
                    'map_entropy': result.map_entropy.entropy_level,
                    'arch_vector': arch_vector,
                    'seed': result.seed,
                    'result': result.result,
                    'plies': result.total_plies,
                    'forced': result.forced_moves,
                    'reactive': result.reactive_moves,
                    'experiment_id': result.experiment_id,
                    'captures': result.captures,
                    'promotions': result.promotions,
                    'final_fen': result.final_fen,
                    'outcome_hash': result.outcome_hash,
                    **result.white_archetype.to_dict(),
                    **{f'black_{k}': v for k, v in result.black_archetype.to_dict().items()},
                    **result.map_entropy.to_dict()
                }
                writer.writerow(row)
        
        print(f"Saved {len(self.results)} results to {self.output_file}")
    
    def run_power_analysis(self, effect_size: float = 0.05, alpha: float = 0.05, 
                         power: float = 0.8) -> int:
        """Estimate games needed per hypothesis for statistical power"""
        from scipy import stats
        
        # Calculate sample size for t-test
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(power)
        
        n = ((z_alpha + z_beta) / effect_size) ** 2
        
        print(f"Power analysis for effect size {effect_size}, alpha {alpha}, power {power}")
        print(f"Estimated games needed per hypothesis: {int(n)}")
        
        return int(n)
    
    def generate_entanglement_map_v2(self, entropy_config: MapEntropyConfig, 
                                    seed: int) -> Dict[str, Any]:
        """Generate entanglement map with controllable parameters"""
        random.seed(seed)
        
        # Apply entropy level
        num_links = int(7 * entropy_config.entropy_level)
        num_links = max(1, min(7, num_links))  # Clamp to 1-7
        
        # Apply clustering factor
        if entropy_config.clustering_factor > 0.5:
            # High clustering: group links by file
            files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
            cluster_files = random.sample(files, num_links)
        else:
            # Low clustering: random distribution
            cluster_files = random.sample(files, num_links)
        
        # Apply symmetry bias
        if entropy_config.symmetry_bias > 0.5:
            # High symmetry: mirror links
            pass  # Implement mirroring logic
        else:
            # Low symmetry: random links
            pass  # Implement random logic
        
        # Generate actual map (simplified)
        w_pawn_to_black = {}
        b_pawn_to_white = {}
        
        for i in range(num_links):
            w_pawn = f"W_P_{cluster_files[i]}2"
            b_target = f"B_{random.choice(['P', 'R', 'N', 'B', 'Q'])}_"
            b_pawn = f"B_P_{cluster_files[i]}7"
            w_target = f"W_{random.choice(['P', 'R', 'N', 'B', 'Q'])}_"
            
            w_pawn_to_black[w_pawn] = b_target
            b_pawn_to_white[b_pawn] = w_target
        
        return {
            'W_pawn_to_black': w_pawn_to_black,
            'B_pawn_to_white': b_pawn_to_white,
            'white_free_pawn': f"W_P_{random.choice([f for f in files if f not in cluster_files])}2",
            'black_free_pawn': f"B_P_{random.choice([f for f in files if f not in cluster_files])}7",
            'entropy_level': entropy_config.entropy_level,
            'clustering_factor': entropy_config.clustering_factor,
            'symmetry_bias': entropy_config.symmetry_bias
        }

def main():
    """Main parameter sweep runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='QEC Parameter Sweep Runner')
    parser.add_argument('--archetypes', type=int, default=10, help='Number of archetypes to test')
    parser.add_argument('--entropy_configs', type=int, default=5, help='Number of entropy configurations')
    parser.add_argument('--games_per_config', type=int, default=3, help='Games per configuration')
    parser.add_argument('--output', type=str, default='parameter_sweep_results.csv', help='Output CSV file')
    parser.add_argument('--seed_base', type=int, default=42, help='Base seed')
    parser.add_argument('--resume', action='store_true', help='Resume from manifest')
    parser.add_argument('--power_analysis', action='store_true', help='Run power analysis')
    
    args = parser.parse_args()
    
    # Run power analysis if requested
    if args.power_analysis:
        runner = QECParameterSweep()
        runner.run_power_analysis()
        return
    
    # Run parameter sweep
    runner = QECParameterSweep(args.output)
    runner.run_parameter_sweep(
        num_archetypes=args.archetypes,
        num_entropy_configs=args.entropy_configs,
        num_games_per_config=args.games_per_config,
        seed_base=args.seed_base,
        resume=args.resume
    )
    runner.save_results()
    
    print("Parameter sweep completed!")

if __name__ == "__main__":
    main()
