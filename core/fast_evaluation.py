"""
Fast Evaluation Mode for QEC
Optimized evaluation for bulk simulations
"""

import sys
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class FastEvaluationConfig:
    """Configuration for fast evaluation mode"""
    skip_positional_every_n_plies: int = 3
    skip_entanglement_every_n_plies: int = 5
    skip_activity_every_n_plies: int = 2
    material_only_threshold: int = 50  # Use material-only eval for positions with <50 pieces
    
    def should_skip_positional(self, ply: int) -> bool:
        """Check if positional evaluation should be skipped"""
        return ply % self.skip_positional_every_n_plies != 0
    
    def should_skip_entanglement(self, ply: int) -> bool:
        """Check if entanglement evaluation should be skipped"""
        return ply % self.skip_entanglement_every_n_plies != 0
    
    def should_skip_activity(self, ply: int) -> bool:
        """Check if activity evaluation should be skipped"""
        return ply % self.skip_activity_every_n_plies != 0
    
    def should_use_material_only(self, piece_count: int) -> bool:
        """Check if material-only evaluation should be used"""
        return piece_count < self.material_only_threshold

class FastQECEvaluator:
    """Fast evaluation engine for bulk simulations"""
    
    def __init__(self, config: FastEvaluationConfig = None):
        self.config = config or FastEvaluationConfig()
        self.evaluation_count = 0
        self.fast_evaluations = 0
        self.material_only_evaluations = 0
    
    def evaluate_fast(self, board, color: str, ply: int = 0) -> int:
        """Fast evaluation with configurable skipping"""
        self.evaluation_count += 1
        
        # Count pieces for material-only threshold
        piece_count = sum(1 for piece in board.pieces if piece.alive)
        
        # Use material-only evaluation for sparse positions
        if self.config.should_use_material_only(piece_count):
            self.material_only_evaluations += 1
            return self._evaluate_material_only(board, color)
        
        # Fast evaluation with selective skipping
        self.fast_evaluations += 1
        return self._evaluate_fast_selective(board, color, ply)
    
    def _evaluate_material_only(self, board, color: str) -> int:
        """Material-only evaluation (fastest)"""
        material = 0
        piece_values = {'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000}
        
        for piece in board.pieces:
            if not piece.alive:
                continue
            
            value = piece_values.get(piece.kind, 0)
            if piece.color == color:
                material += value
            else:
                material -= value
        
        return material
    
    def _evaluate_fast_selective(self, board, color: str, ply: int) -> int:
        """Fast evaluation with selective term skipping"""
        score = 0
        
        # Always include material (fastest)
        score += self._evaluate_material_fast(board, color)
        
        # Skip positional evaluation based on ply
        if not self.config.should_skip_positional(ply):
            score += self._evaluate_positional_fast(board, color)
        
        # Skip entanglement evaluation based on ply
        if not self.config.should_skip_entanglement(ply):
            score += self._evaluate_entanglement_fast(board, color)
        
        # Skip activity evaluation based on ply
        if not self.config.should_skip_activity(ply):
            score += self._evaluate_activity_fast(board, color)
        
        return score
    
    def _evaluate_material_fast(self, board, color: str) -> int:
        """Fast material evaluation"""
        material = 0
        piece_values = {'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000}
        
        for piece in board.pieces:
            if not piece.alive:
                continue
            
            value = piece_values.get(piece.kind, 0)
            if piece.color == color:
                material += value
            else:
                material -= value
        
        return material
    
    def _evaluate_positional_fast(self, board, color: str) -> int:
        """Fast positional evaluation"""
        score = 0
        
        # Center control (simplified)
        center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
        for piece in board.pieces:
            if not piece.alive or piece.color != color:
                continue
            
            if piece.pos in center_squares:
                score += 10
        
        return score
    
    def _evaluate_entanglement_fast(self, board, color: str) -> int:
        """Fast entanglement evaluation"""
        # Simplified entanglement scoring
        score = 0
        
        # Count pieces that can move to center (proxy for entanglement)
        for piece in board.pieces:
            if not piece.alive or piece.color != color:
                continue
            
            if piece.kind in ['N', 'B', 'Q']:
                # Simple mobility count
                score += 5
        
        return score
    
    def _evaluate_activity_fast(self, board, color: str) -> int:
        """Fast activity evaluation"""
        score = 0
        
        # Count active pieces (simplified)
        for piece in board.pieces:
            if not piece.alive or piece.color != color:
                continue
            
            if piece.kind in ['Q', 'R']:
                score += 10
            elif piece.kind in ['N', 'B']:
                score += 5
        
        return score
    
    def get_evaluation_stats(self) -> Dict[str, int]:
        """Get evaluation statistics"""
        return {
            'total_evaluations': self.evaluation_count,
            'fast_evaluations': self.fast_evaluations,
            'material_only_evaluations': self.material_only_evaluations,
            'fast_evaluation_rate': (self.fast_evaluations / self.evaluation_count * 100) if self.evaluation_count > 0 else 0,
            'material_only_rate': (self.material_only_evaluations / self.evaluation_count * 100) if self.evaluation_count > 0 else 0
        }
    
    def reset_stats(self):
        """Reset evaluation statistics"""
        self.evaluation_count = 0
        self.fast_evaluations = 0
        self.material_only_evaluations = 0

# Global fast evaluator instance
fast_evaluator = FastQECEvaluator()

def get_fast_evaluator() -> FastQECEvaluator:
    """Get the global fast evaluator instance"""
    return fast_evaluator

def evaluate_fast(board, color: str, ply: int = 0) -> int:
    """Fast evaluation function"""
    return fast_evaluator.evaluate_fast(board, color, ply)

def get_evaluation_stats() -> Dict[str, int]:
    """Get evaluation statistics"""
    return fast_evaluator.get_evaluation_stats()

def reset_evaluation_stats():
    """Reset evaluation statistics"""
    fast_evaluator.reset_stats()
