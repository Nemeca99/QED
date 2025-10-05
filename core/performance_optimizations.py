"""
Performance Optimizations for QEC
Caching and memoization for frequently called functions
"""

import sys
import os
from typing import Dict, Set, Tuple, Optional
from functools import lru_cache
import hashlib

class QECPerformanceCache:
    """Performance cache for QEC operations"""
    
    def __init__(self):
        self.slider_rays_cache = {}
        self.is_attacked_cache = {}
        self.position_hash_cache = {}
        self.evaluation_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
    
    def get_slider_rays(self, piece_pos: Tuple[int, int], piece_type: str, board_state: str) -> Set[Tuple[int, int]]:
        """Get cached slider rays for a piece"""
        cache_key = f"{piece_pos}_{piece_type}_{board_state}"
        
        if cache_key in self.slider_rays_cache:
            self.cache_hits += 1
            return self.slider_rays_cache[cache_key]
        
        self.cache_misses += 1
        # Calculate rays (this would be implemented based on piece type)
        rays = self._calculate_slider_rays(piece_pos, piece_type, board_state)
        self.slider_rays_cache[cache_key] = rays
        return rays
    
    def _calculate_slider_rays(self, piece_pos: Tuple[int, int], piece_type: str, board_state: str) -> Set[Tuple[int, int]]:
        """Calculate slider rays for a piece"""
        rays = set()
        x, y = piece_pos
        
        if piece_type in ['B', 'Q']:
            # Diagonal rays
            for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                for i in range(1, 8):
                    new_x, new_y = x + i * dx, y + i * dy
                    if 0 <= new_x < 8 and 0 <= new_y < 8:
                        rays.add((new_x, new_y))
                    else:
                        break
        
        if piece_type in ['R', 'Q']:
            # Orthogonal rays
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                for i in range(1, 8):
                    new_x, new_y = x + i * dx, y + i * dy
                    if 0 <= new_x < 8 and 0 <= new_y < 8:
                        rays.add((new_x, new_y))
                    else:
                        break
        
        return rays
    
    def get_position_hash(self, board_state: str, color: str) -> str:
        """Get cached position hash"""
        cache_key = f"{board_state}_{color}"
        
        if cache_key in self.position_hash_cache:
            self.cache_hits += 1
            return self.position_hash_cache[cache_key]
        
        self.cache_misses += 1
        position_hash = hashlib.md5(f"{board_state}_{color}".encode()).hexdigest()[:8]
        self.position_hash_cache[cache_key] = position_hash
        return position_hash
    
    def is_attacked_memoized(self, square: Tuple[int, int], color: str, board_state: str, position_hash: str) -> bool:
        """Memoized is_attacked check"""
        cache_key = f"{square}_{color}_{position_hash}"
        
        if cache_key in self.is_attacked_cache:
            self.cache_hits += 1
            return self.is_attacked_cache[cache_key]
        
        self.cache_misses += 1
        # This would call the actual is_attacked function
        is_attacked = self._calculate_is_attacked(square, color, board_state)
        self.is_attacked_cache[cache_key] = is_attacked
        return is_attacked
    
    def _calculate_is_attacked(self, square: Tuple[int, int], color: str, board_state: str) -> bool:
        """Calculate if square is attacked (placeholder implementation)"""
        # This would be the actual is_attacked logic
        # For now, return a simple heuristic
        return False
    
    def get_evaluation_memoized(self, board_state: str, color: str, position_hash: str) -> int:
        """Memoized position evaluation"""
        cache_key = f"{position_hash}_{color}"
        
        if cache_key in self.evaluation_cache:
            self.cache_hits += 1
            return self.evaluation_cache[cache_key]
        
        self.cache_misses += 1
        # This would call the actual evaluation function
        evaluation = self._calculate_evaluation(board_state, color)
        self.evaluation_cache[cache_key] = evaluation
        return evaluation
    
    def _calculate_evaluation(self, board_state: str, color: str) -> int:
        """Calculate position evaluation (placeholder implementation)"""
        # This would be the actual evaluation logic
        # For now, return a simple heuristic
        return 0
    
    def clear_cache(self):
        """Clear all caches"""
        self.slider_rays_cache.clear()
        self.is_attacked_cache.clear()
        self.position_hash_cache.clear()
        self.evaluation_cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'total_requests': total_requests,
            'hit_rate': hit_rate,
            'slider_rays_cache_size': len(self.slider_rays_cache),
            'is_attacked_cache_size': len(self.is_attacked_cache),
            'position_hash_cache_size': len(self.position_hash_cache),
            'evaluation_cache_size': len(self.evaluation_cache)
        }

# Global cache instance
performance_cache = QECPerformanceCache()

def get_performance_cache() -> QECPerformanceCache:
    """Get the global performance cache instance"""
    return performance_cache

def clear_performance_cache():
    """Clear the global performance cache"""
    performance_cache.clear_cache()

def get_cache_stats() -> Dict[str, int]:
    """Get global cache statistics"""
    return performance_cache.get_cache_stats()
