"""
QEC-Specific Evaluation Function
Implements the 6 QEC evaluation terms plus material and positional factors
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from main import Board, Piece, Square, Color
from qec_archetypes import QECArchetype

@dataclass
class QECEvaluation:
    """QEC evaluation result with breakdown"""
    total: int
    material: int
    positional: int
    entanglement: int
    forced_replies: int
    free_pieces: int
    king_safety: int
    activity: int
    breakdown: Dict[str, int]

class QECEvaluator:
    """QEC-specific evaluation engine"""
    
    def __init__(self, archetype: QECArchetype):
        self.archetype = archetype
        
        # Material values
        self.piece_values = {
            'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000
        }
        
        # Positional bonuses
        self.center_bonus = 10
        self.development_bonus = 5
        self.mobility_bonus = 2
        
    def evaluate(self, board: Board, color: Color) -> QECEvaluation:
        """Evaluate position from color's perspective"""
        # Basic material and positional evaluation
        material = self._evaluate_material(board, color)
        positional = self._evaluate_positional(board, color)
        
        # QEC-specific terms
        entanglement = self._evaluate_entanglement(board, color)
        forced_replies = self._evaluate_forced_replies(board, color)
        free_pieces = self._evaluate_free_pieces(board, color)
        king_safety = self._evaluate_king_safety(board, color)
        activity = self._evaluate_activity(board, color)
        
        # Calculate total with archetype weights
        total = (material + positional + 
                self.archetype.w1 * entanglement +
                self.archetype.w2 * (-entanglement) +  # Negative for opponent entanglement
                self.archetype.w3 * forced_replies +
                self.archetype.w4 * free_pieces +
                self.archetype.w5 * king_safety +
                self.archetype.w6 * activity)
        
        breakdown = {
            "material": material,
            "positional": positional,
            "entanglement": entanglement,
            "forced_replies": forced_replies,
            "free_pieces": free_pieces,
            "king_safety": king_safety,
            "activity": activity
        }
        
        return QECEvaluation(
            total=int(total),
            material=material,
            positional=positional,
            entanglement=entanglement,
            forced_replies=forced_replies,
            free_pieces=free_pieces,
            king_safety=king_safety,
            activity=activity,
            breakdown=breakdown
        )
    
    def _evaluate_material(self, board: Board, color: Color) -> int:
        """Evaluate material balance"""
        material = 0
        for piece in board.pieces:
            if not piece.alive:
                continue
            
            value = self.piece_values.get(piece.kind, 0)
            if piece.color == color:
                material += value
            else:
                material -= value
        
        return material
    
    def _evaluate_positional(self, board: Board, color: Color) -> int:
        """Evaluate positional factors"""
        score = 0
        
        # Center control
        center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
        for piece in board.pieces:
            if not piece.alive or piece.color != color:
                continue
            
            if piece.pos in center_squares:
                score += self.center_bonus
            
            # Development bonus for pieces off starting rank
            if piece.kind in ['N', 'B']:
                if piece.color == 'W' and piece.pos[1] > 1:
                    score += self.development_bonus
                elif piece.color == 'B' and piece.pos[1] < 6:
                    score += self.development_bonus
        
        return score
    
    def _evaluate_entanglement(self, board: Board, color: Color) -> int:
        """Evaluate entanglement advantage (w1 term)"""
        # This needs access to the game's entanglement mapping
        # For now, return a heuristic based on piece mobility and control
        score = 0
        
        # Count pieces that can move to control key squares
        for piece in board.pieces:
            if not piece.alive or piece.color != color:
                continue
            
            # Bonus for pieces that can move to center
            if piece.kind in ['N', 'B', 'Q']:
                center_control = self._count_center_control(board, piece)
                score += center_control * 5
        
        return score
    
    def _evaluate_forced_replies(self, board: Board, color: Color) -> int:
        """Evaluate forced replies available next ply (w3 term)"""
        # Count moves that would force opponent responses
        forced_count = 0
        
        # Check for checks
        if board.in_check(color):
            forced_count += 1
        
        # Count captures (simplified)
        captures = 0
        for piece in board.pieces:
            if not piece.alive or piece.color != color:
                continue
            
            # Count potential captures
            for frm, to, spec in board._gen_piece_moves(piece, attacks_only=True):
                target = board.piece_at(to)
                if target and target.color != piece.color:
                    captures += 1
        
        forced_count += captures
        return forced_count * 5
    
    def _evaluate_free_pieces(self, board: Board, color: Color) -> int:
        """Evaluate free-piece differential (w4 term)"""
        # Count pieces that can move freely (not pinned, not in danger)
        my_free_pieces = 0
        opponent_free_pieces = 0
        
        for piece in board.pieces:
            if not piece.alive:
                continue
            
            # Simplified: count pieces not in immediate danger
            is_safe = not self._piece_under_attack(piece, board)
            
            if piece.color == color:
                if is_safe:
                    my_free_pieces += 1
            else:
                if is_safe:
                    opponent_free_pieces += 1
        
        return (my_free_pieces - opponent_free_pieces) * 15
    
    def _evaluate_king_safety(self, board: Board, color: Color) -> int:
        """Evaluate king safety (w5 term)"""
        king = next((p for p in board.pieces if p.alive and p.color == color and p.kind == 'K'), None)
        if not king:
            return -1000  # No king = very bad
        
        safety_score = 0
        
        # Check if king is in check
        if board.in_check(color):
            safety_score -= 50
        
        # Check for reactive-check vulnerability
        # (This would need more sophisticated analysis)
        if self._king_exposed(king, board):
            safety_score -= 30
        
        return safety_score
    
    def _evaluate_activity(self, board: Board, color: Color) -> int:
        """Evaluate piece activity (w6 term)"""
        activity = 0
        
        for piece in board.pieces:
            if not piece.alive or piece.color != color:
                continue
            
            # Count legal moves for this piece
            moves = list(board._gen_piece_moves(piece, attacks_only=False))
            activity += len(moves) * self.mobility_bonus
            
            # Bonus for advanced pieces
            if piece.kind in ['Q', 'R']:
                if piece.color == 'W' and piece.pos[1] > 3:
                    activity += 10
                elif piece.color == 'B' and piece.pos[1] < 4:
                    activity += 10
        
        return activity
    
    def _pieces_adjacent(self, pos1: Square, pos2: Square) -> bool:
        """Check if two pieces are adjacent"""
        f1, r1 = pos1
        f2, r2 = pos2
        return abs(f1 - f2) <= 1 and abs(r1 - r2) <= 1
    
    def _piece_under_attack(self, piece: Piece, board: Board) -> bool:
        """Check if piece is under attack (simplified)"""
        # This would need proper attack detection
        # For now, return False (no attacks detected)
        return False
    
    def _king_exposed(self, king: Piece, board: Board) -> bool:
        """Check if king is exposed to reactive checks (simplified)"""
        # This would need proper king safety analysis
        # For now, return False (king not exposed)
        return False

def create_evaluator(archetype: QECArchetype) -> QECEvaluator:
    """Create evaluator for specific archetype"""
    return QECEvaluator(archetype)

def compare_evaluations(eval1: QECEvaluation, eval2: QECEvaluation) -> Dict[str, int]:
    """Compare two evaluations and return differences"""
    return {
        "total_diff": eval1.total - eval2.total,
        "material_diff": eval1.material - eval2.material,
        "positional_diff": eval1.positional - eval2.positional,
        "entanglement_diff": eval1.entanglement - eval2.entanglement,
        "forced_replies_diff": eval1.forced_replies - eval2.forced_replies,
        "free_pieces_diff": eval1.free_pieces - eval2.free_pieces,
        "king_safety_diff": eval1.king_safety - eval2.king_safety,
        "activity_diff": eval1.activity - eval2.activity
    }

if __name__ == "__main__":
    # Test evaluation system
    from qec_archetypes import QEC_ARCHETYPES
    
    print("=== QEC Evaluation System ===")
    
    # Test with different archetypes
    for archetype in QEC_ARCHETYPES[:3]:  # Test first 3
        print(f"\n{archetype.name} Archetype:")
        print(f"  Weights: w1:{archetype.w1:.1f} w2:{archetype.w2:.1f} w3:{archetype.w3:.1f} "
              f"w4:{archetype.w4:.1f} w5:{archetype.w5:.1f} w6:{archetype.w6:.1f}")
        print(f"  Search depth: {archetype.search_depth}")
        print(f"  Move limit: {archetype.move_limit}")
    
    print("\nEvaluation terms:")
    print("  w1: +opponent pieces entangled to your pawns")
    print("  w2: -your pieces entangled to their pawns")
    print("  w3: +forced replies available next ply")
    print("  w4: +free-piece differential after captures/promos")
    print("  w5: -reactive-check vulnerability score")
    print("  w6: +rook/queen activity from opponent-forced drifts")
