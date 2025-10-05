"""
QEC Feature Extraction
Extract QEC-specific features from chess games
"""

import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import logging

from .schemas import RawGame, QECFeatures, Result

logger = logging.getLogger(__name__)

class QECFeatureExtractor:
    """Extract QEC-specific features from chess games"""
    
    def __init__(self):
        self.check_pattern = re.compile(r'\+|#')
        self.capture_pattern = re.compile(r'x')
        self.promotion_pattern = re.compile(r'=')
        self.king_move_pattern = re.compile(r'^K')
    
    def extract_features(self, raw_game: RawGame) -> QECFeatures:
        """Extract QEC features from raw game"""
        try:
            # Parse PGN to extract moves
            moves = self._extract_moves_from_pgn(raw_game.pgn)
            
            # Extract basic features
            plies = len(moves)
            checks = self._count_checks(moves)
            captures = self._count_captures(moves)
            promotions = self._count_promotions(moves)
            
            # Extract QEC-specific features
            king_escape_ops = self._count_king_escape_opportunities(moves)
            forced_seq_spans = self._find_forced_sequences(moves)
            opening_phase_end_ply = self._find_opening_phase_end(moves)
            tactical_density = (checks + captures) / plies if plies > 0 else 0.0
            reactive_escape_candidates = self._count_reactive_escape_candidates(moves)
            
            # Extract metadata
            white_rating = self._parse_rating(raw_game.headers.get('WhiteElo', '0'))
            black_rating = self._parse_rating(raw_game.headers.get('BlackElo', '0'))
            time_control = raw_game.headers.get('TimeControl', '')
            result = self._parse_result(raw_game.headers.get('Result', '*'))
            eco = raw_game.headers.get('ECO', '')
            
            # Phase splits
            phase_splits = self._compute_phase_splits(moves, opening_phase_end_ply)
            
            return QECFeatures(
                game_uid=raw_game.game_uid,
                plies=plies,
                checks=checks,
                captures=captures,
                promotions=promotions,
                king_escape_ops=king_escape_ops,
                forced_seq_spans=forced_seq_spans,
                opening_phase_end_ply=opening_phase_end_ply,
                tactical_density=tactical_density,
                reactive_escape_candidates=reactive_escape_candidates,
                white_rating=white_rating,
                black_rating=black_rating,
                time_control=time_control,
                result=result,
                eco=eco,
                phase_splits=phase_splits
            )
            
        except Exception as e:
            logger.error(f"Failed to extract features for game {raw_game.game_uid}: {e}")
            # Return minimal features on error
            return QECFeatures(
                game_uid=raw_game.game_uid,
                plies=0,
                checks=0,
                captures=0,
                promotions=0,
                king_escape_ops=0,
                forced_seq_spans=[],
                opening_phase_end_ply=0,
                tactical_density=0.0,
                reactive_escape_candidates=0,
                white_rating=0,
                black_rating=0,
                time_control='',
                result=Result.UNKNOWN,
                eco='',
                phase_splits={}
            )
    
    def _extract_moves_from_pgn(self, pgn: str) -> List[str]:
        """Extract moves from PGN text"""
        moves = []
        lines = pgn.split('\n')
        
        for line in lines:
            if line.strip() and not line.startswith('['):
                # Split by spaces and filter out move numbers
                move_parts = line.strip().split()
                for part in move_parts:
                    if '.' not in part and part not in ['1-0', '0-1', '1/2-1/2', '*']:
                        moves.append(part)
        
        return moves
    
    def _count_checks(self, moves: List[str]) -> int:
        """Count check moves"""
        return sum(1 for move in moves if self.check_pattern.search(move))
    
    def _count_captures(self, moves: List[str]) -> int:
        """Count capture moves"""
        return sum(1 for move in moves if self.capture_pattern.search(move))
    
    def _count_promotions(self, moves: List[str]) -> int:
        """Count promotion moves"""
        return sum(1 for move in moves if self.promotion_pattern.search(move))
    
    def _count_king_escape_opportunities(self, moves: List[str]) -> int:
        """Count king escape opportunities (king moves after checks)"""
        king_escapes = 0
        in_check = False
        
        for move in moves:
            if self.check_pattern.search(move):
                in_check = True
            elif in_check and self.king_move_pattern.match(move):
                king_escapes += 1
                in_check = False
            elif in_check and not self.check_pattern.search(move):
                in_check = False
        
        return king_escapes
    
    def _find_forced_sequences(self, moves: List[str]) -> List[int]:
        """Find forced move sequences (consecutive checks)"""
        forced_sequences = []
        current_sequence = 0
        
        for move in moves:
            if self.check_pattern.search(move):
                current_sequence += 1
            else:
                if current_sequence > 0:
                    forced_sequences.append(current_sequence)
                current_sequence = 0
        
        # Add final sequence if game ends in check
        if current_sequence > 0:
            forced_sequences.append(current_sequence)
        
        return forced_sequences
    
    def _find_opening_phase_end(self, moves: List[str]) -> int:
        """Find opening phase end (heuristic: first capture or move 20)"""
        for i, move in enumerate(moves):
            if self.capture_pattern.search(move):
                return i + 1
        
        # Default to move 20 if no captures
        return min(20, len(moves))
    
    def _count_reactive_escape_candidates(self, moves: List[str]) -> int:
        """Count reactive escape candidates (king moves in response to threats)"""
        reactive_escapes = 0
        threat_sequence = False
        
        for i, move in enumerate(moves):
            if self.check_pattern.search(move):
                threat_sequence = True
            elif threat_sequence and self.king_move_pattern.match(move):
                reactive_escapes += 1
                threat_sequence = False
            elif threat_sequence and not self.check_pattern.search(move):
                threat_sequence = False
        
        return reactive_escapes
    
    def _parse_rating(self, rating_str: str) -> int:
        """Parse rating string to integer"""
        try:
            return int(rating_str) if rating_str.isdigit() else 0
        except (ValueError, TypeError):
            return 0
    
    def _parse_result(self, result_str: str) -> Result:
        """Parse result string to Result enum"""
        if result_str == "1-0":
            return Result.WHITE_WINS
        elif result_str == "0-1":
            return Result.BLACK_WINS
        elif result_str == "1/2-1/2":
            return Result.DRAW
        else:
            return Result.UNKNOWN
    
    def _compute_phase_splits(self, moves: List[str], opening_end: int) -> Dict[str, int]:
        """Compute phase splits for the game"""
        total_moves = len(moves)
        
        return {
            'opening': min(opening_end, total_moves),
            'middlegame': max(0, min(40, total_moves) - opening_end),
            'endgame': max(0, total_moves - 40)
        }
