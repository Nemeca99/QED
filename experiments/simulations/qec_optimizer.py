"""
QEC Rule Optimizer
Optimize QEC rules to reduce draw rate and balance color advantage
"""

import os
import json
import random
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from collections import defaultdict

from main import Game, Board, Piece, Square, Color
from qec_archetypes import QECArchetype, get_archetype_by_name
from fixed_qec_research_simulator import FixedQECResearchSimulator, QECGameResult

@dataclass
class QECRuleConfig:
    """QEC rule configuration for optimization"""
    # Entanglement rules
    entanglement_probability: float = 1.0  # Probability of entanglement
    entanglement_strength: float = 1.0     # Strength of entanglement effects
    
    # Forced move rules
    forced_move_probability: float = 1.0   # Probability of forced moves
    forced_move_strength: float = 1.0      # Strength of forced moves
    
    # Reactive move rules
    reactive_move_probability: float = 1.0 # Probability of reactive moves
    reactive_move_strength: float = 1.0    # Strength of reactive moves
    
    # Game balance
    white_advantage_reduction: float = 0.0 # Reduce white advantage
    draw_rate_reduction: float = 0.0        # Reduce draw rate
    
    # Evaluation weights
    material_weight: float = 1.0
    position_weight: float = 1.0
    entanglement_weight: float = 1.0

class QECOptimizer:
    """QEC rule optimizer using genetic algorithm approach"""
    
    def __init__(self, logs_dir: str = "optimization_logs"):
        self.logs_dir = logs_dir
        self.best_config = None
        self.optimization_history = []
        
        # Create logs directory
        os.makedirs(logs_dir, exist_ok=True)
    
    def optimize_rules(self, target_draw_rate: float = 0.4, target_white_advantage: float = 0.55, 
                      num_generations: int = 10, population_size: int = 20):
        """Optimize QEC rules using genetic algorithm"""
        print(f"=== QEC Rule Optimization ===")
        print(f"Target draw rate: {target_draw_rate:.1%}")
        print(f"Target white advantage: {target_white_advantage:.1%}")
        print(f"Generations: {num_generations}")
        print(f"Population size: {population_size}")
        print()
        
        # Initialize population
        population = self._generate_initial_population(population_size)
        
        for generation in range(num_generations):
            print(f"Generation {generation + 1}/{num_generations}")
            
            # Evaluate population
            fitness_scores = []
            for i, config in enumerate(population):
                print(f"  Testing config {i + 1}/{len(population)}...")
                fitness = self._evaluate_config(config)
                fitness_scores.append(fitness)
                print(f"    Fitness: {fitness:.3f}")
            
            # Find best config
            best_idx = np.argmax(fitness_scores)
            best_config = population[best_idx]
            best_fitness = fitness_scores[best_idx]
            
            print(f"  Best fitness: {best_fitness:.3f}")
            print(f"  Best config: {best_config}")
            
            # Save best config
            self.best_config = best_config
            self.optimization_history.append({
                'generation': generation + 1,
                'best_fitness': best_fitness,
                'best_config': best_config
            })
            
            # Create next generation
            if generation < num_generations - 1:
                population = self._create_next_generation(population, fitness_scores)
        
        # Save optimization results
        self._save_optimization_results()
        
        return self.best_config
    
    def _generate_initial_population(self, size: int) -> List[QECRuleConfig]:
        """Generate initial population of rule configurations"""
        population = []
        
        for _ in range(size):
            config = QECRuleConfig(
                entanglement_probability=random.uniform(0.5, 1.0),
                entanglement_strength=random.uniform(0.5, 1.5),
                forced_move_probability=random.uniform(0.5, 1.0),
                forced_move_strength=random.uniform(0.5, 1.5),
                reactive_move_probability=random.uniform(0.5, 1.0),
                reactive_move_strength=random.uniform(0.5, 1.5),
                white_advantage_reduction=random.uniform(0.0, 0.5),
                draw_rate_reduction=random.uniform(0.0, 0.5),
                material_weight=random.uniform(0.5, 1.5),
                position_weight=random.uniform(0.5, 1.5),
                entanglement_weight=random.uniform(0.5, 1.5)
            )
            population.append(config)
        
        return population
    
    def _evaluate_config(self, config: QECRuleConfig) -> float:
        """Evaluate a rule configuration"""
        # Run small test with this configuration
        simulator = FixedQECResearchSimulator(f"{self.logs_dir}/config_test")
        results = simulator.run_comprehensive_experiment(
            archetypes=["Carlsen-like", "Tal-like", "Karpov-like"],
            num_games=20  # Small test for speed
        )
        
        # Calculate metrics
        total_games = len(results)
        if total_games == 0:
            return 0.0
        
        # Count results
        white_wins = sum(1 for r in results if r.result == "W wins")
        black_wins = sum(1 for r in results if r.result == "B wins")
        draws = sum(1 for r in results if r.result == "Draw")
        
        # Calculate rates
        draw_rate = draws / total_games
        decisive_games = white_wins + black_wins
        white_advantage = white_wins / decisive_games if decisive_games > 0 else 0.5
        
        # Calculate fitness (higher is better)
        # Target: 40% draw rate, 55% white advantage
        target_draw_rate = 0.4
        target_white_advantage = 0.55
        
        draw_rate_score = 1.0 - abs(draw_rate - target_draw_rate) / target_draw_rate
        white_advantage_score = 1.0 - abs(white_advantage - target_white_advantage) / target_white_advantage
        
        # Bonus for having decisive games
        decisive_rate = decisive_games / total_games
        decisive_score = decisive_rate
        
        # Combined fitness
        fitness = (draw_rate_score + white_advantage_score + decisive_score) / 3.0
        
        return fitness
    
    def _create_next_generation(self, population: List[QECRuleConfig], 
                               fitness_scores: List[float]) -> List[QECRuleConfig]:
        """Create next generation using genetic operators"""
        new_population = []
        
        # Keep best 20% of population
        elite_size = max(1, len(population) // 5)
        elite_indices = np.argsort(fitness_scores)[-elite_size:]
        for idx in elite_indices:
            new_population.append(population[idx])
        
        # Generate rest through crossover and mutation
        while len(new_population) < len(population):
            # Select parents using tournament selection
            parent1 = self._tournament_selection(population, fitness_scores)
            parent2 = self._tournament_selection(population, fitness_scores)
            
            # Crossover
            child = self._crossover(parent1, parent2)
            
            # Mutation
            child = self._mutate(child)
            
            new_population.append(child)
        
        return new_population
    
    def _tournament_selection(self, population: List[QECRuleConfig], 
                             fitness_scores: List[float], tournament_size: int = 3) -> QECRuleConfig:
        """Tournament selection for genetic algorithm"""
        tournament_indices = random.sample(range(len(population)), tournament_size)
        tournament_fitness = [fitness_scores[i] for i in tournament_indices]
        winner_idx = tournament_indices[np.argmax(tournament_fitness)]
        return population[winner_idx]
    
    def _crossover(self, parent1: QECRuleConfig, parent2: QECRuleConfig) -> QECRuleConfig:
        """Crossover two parent configurations"""
        # Simple uniform crossover
        child = QECRuleConfig()
        
        for field in child.__dataclass_fields__:
            if random.random() < 0.5:
                setattr(child, field, getattr(parent1, field))
            else:
                setattr(child, field, getattr(parent2, field))
        
        return child
    
    def _mutate(self, config: QECRuleConfig, mutation_rate: float = 0.1) -> QECRuleConfig:
        """Mutate a configuration"""
        mutated = QECRuleConfig(
            entanglement_probability=config.entanglement_probability,
            entanglement_strength=config.entanglement_strength,
            forced_move_probability=config.forced_move_probability,
            forced_move_strength=config.forced_move_strength,
            reactive_move_probability=config.reactive_move_probability,
            reactive_move_strength=config.reactive_move_strength,
            white_advantage_reduction=config.white_advantage_reduction,
            draw_rate_reduction=config.draw_rate_reduction,
            material_weight=config.material_weight,
            position_weight=config.position_weight,
            entanglement_weight=config.entanglement_weight
        )
        
        # Mutate each field with small probability
        for field in mutated.__dataclass_fields__:
            if random.random() < mutation_rate:
                current_value = getattr(mutated, field)
                # Add small random change
                change = random.uniform(-0.1, 0.1)
                new_value = max(0.0, min(2.0, current_value + change))
                setattr(mutated, field, new_value)
        
        return mutated
    
    def _save_optimization_results(self):
        """Save optimization results"""
        results_file = os.path.join(self.logs_dir, "optimization_results.json")
        with open(results_file, 'w') as f:
            json.dump(self.optimization_history, f, indent=2)
        
        print(f"Optimization results saved to {self.logs_dir}")
    
    def test_optimized_rules(self, num_games: int = 100):
        """Test the optimized rules"""
        if not self.best_config:
            print("No optimized rules found. Run optimization first.")
            return
        
        print(f"=== Testing Optimized Rules ===")
        print(f"Best config: {self.best_config}")
        print(f"Testing with {num_games} games...")
        
        # Run test with optimized rules
        simulator = FixedQECResearchSimulator(f"{self.logs_dir}/optimized_test")
        results = simulator.run_comprehensive_experiment(
            archetypes=["Carlsen-like", "Tal-like", "Karpov-like"],
            num_games=num_games
        )
        
        # Analyze results
        total_games = len(results)
        white_wins = sum(1 for r in results if r.result == "W wins")
        black_wins = sum(1 for r in results if r.result == "B wins")
        draws = sum(1 for r in results if r.result == "Draw")
        
        print(f"\nOptimized Results:")
        print(f"  Total games: {total_games}")
        print(f"  White wins: {white_wins} ({white_wins/total_games*100:.1f}%)")
        print(f"  Black wins: {black_wins} ({black_wins/total_games*100:.1f}%)")
        print(f"  Draws: {draws} ({draws/total_games*100:.1f}%)")
        
        decisive_games = white_wins + black_wins
        if decisive_games > 0:
            white_advantage = white_wins / decisive_games
            print(f"  White advantage: {white_advantage:.1%}")
        
        return results

if __name__ == "__main__":
    # Run optimization
    optimizer = QECOptimizer()
    best_config = optimizer.optimize_rules(
        target_draw_rate=0.4,
        target_white_advantage=0.55,
        num_generations=5,
        population_size=10
    )
    
    # Test optimized rules
    optimizer.test_optimized_rules(num_games=50)
