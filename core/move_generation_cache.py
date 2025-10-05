"""
Move Generation Cache for QEC
Per-ply cache invalidation and move list reuse for quiescent plies
"""

import sys
import os
from typing import Dict, List, Tuple, Set, Optional
from dataclasses import dataclass
import hashlib

@dataclass
class MoveCacheEntry:
    """Cache entry for move generation"""
    position_hash: str
    legal_moves: List[Tuple]
    quiescent_moves: List[Tuple]
    ply: int
    cache_time: float

class QECMoveCache:
    """Move generation cache with per-ply invalidation"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: Dict[str, MoveCacheEntry] = {}
        self.position_hashes: Dict[str, str] = {}
        self.slider_rays: Dict[Tuple[int, int, str], Set[Tuple[int, int]]] = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self._precompute_slider_rays()
    
    def _precompute_slider_rays(self):
        """Precompute all slider rays once at import"""
        print("Precomputing slider rays...")
        
        # Precompute for all squares and piece types
        for x in range(8):
            for y in range(8):
                # Bishop rays
                self.slider_rays[(x, y, 'B')] = self._calculate_bishop_rays(x, y)
                # Rook rays  
                self.slider_rays[(x, y, 'R')] = self._calculate_rook_rays(x, y)
                # Queen rays
                self.slider_rays[(x, y, 'Q')] = self._calculate_queen_rays(x, y)
        
        print(f"Precomputed {len(self.slider_rays)} slider ray sets")
    
    def _calculate_bishop_rays(self, x: int, y: int) -> Set[Tuple[int, int]]:
        """Calculate bishop rays for a square"""
        rays = set()
        for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            for i in range(1, 8):
                new_x, new_y = x + i * dx, y + i * dy
                if 0 <= new_x < 8 and 0 <= new_y < 8:
                    rays.add((new_x, new_y))
                else:
                    break
        return rays
    
    def _calculate_rook_rays(self, x: int, y: int) -> Set[Tuple[int, int]]:
        """Calculate rook rays for a square"""
        rays = set()
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            for i in range(1, 8):
                new_x, new_y = x + i * dx, y + i * dy
                if 0 <= new_x < 8 and 0 <= new_y < 8:
                    rays.add((new_x, new_y))
                else:
                    break
        return rays
    
    def _calculate_queen_rays(self, x: int, y: int) -> Set[Tuple[int, int]]:
        """Calculate queen rays for a square"""
        return self._calculate_bishop_rays(x, y) | self._calculate_rook_rays(x, y)
    
    def get_slider_rays(self, x: int, y: int, piece_type: str) -> Set[Tuple[int, int]]:
        """Get precomputed slider rays"""
        return self.slider_rays.get((x, y, piece_type), set())
    
    def get_position_hash(self, board_state: str, ply: int) -> str:
        """Get position hash for caching"""
        cache_key = f"{board_state}_{ply}"
        
        if cache_key in self.position_hashes:
            return self.position_hashes[cache_key]
        
        # Create hash
        position_hash = hashlib.md5(cache_key.encode()).hexdigest()[:12]
        self.position_hashes[cache_key] = position_hash
        return position_hash
    
    def get_legal_moves(self, board_state: str, ply: int, force_refresh: bool = False) -> List[Tuple]:
        """Get cached legal moves with per-ply invalidation"""
        position_hash = self.get_position_hash(board_state, ply)
        
        # Check cache first
        if not force_refresh and position_hash in self.cache:
            entry = self.cache[position_hash]
            if entry.ply == ply:  # Same ply, cache is valid
                self.cache_hits += 1
                return entry.legal_moves
        
        self.cache_misses += 1
        return None  # Cache miss, need to generate moves
    
    def cache_legal_moves(self, board_state: str, ply: int, legal_moves: List[Tuple], 
                         quiescent_moves: List[Tuple] = None) -> None:
        """Cache legal moves for a position"""
        position_hash = self.get_position_hash(board_state, ply)
        
        # Create cache entry
        entry = MoveCacheEntry(
            position_hash=position_hash,
            legal_moves=legal_moves.copy(),
            quiescent_moves=quiescent_moves.copy() if quiescent_moves else [],
            ply=ply,
            cache_time=0.0  # Would use time.time() in real implementation
        )
        
        # Store in cache
        self.cache[position_hash] = entry
        
        # Evict old entries if cache is full
        if len(self.cache) > self.max_size:
            self._evict_oldest()
    
    def get_quiescent_moves(self, board_state: str, ply: int) -> List[Tuple]:
        """Get cached quiescent moves for reuse"""
        position_hash = self.get_position_hash(board_state, ply)
        
        if position_hash in self.cache:
            entry = self.cache[position_hash]
            if entry.ply == ply and entry.quiescent_moves:
                return entry.quiescent_moves
        
        return []
    
    def invalidate_ply(self, ply: int) -> None:
        """Invalidate cache for a specific ply"""
        to_remove = []
        for pos_hash, entry in self.cache.items():
            if entry.ply == ply:
                to_remove.append(pos_hash)
        
        for pos_hash in to_remove:
            del self.cache[pos_hash]
    
    def invalidate_all(self) -> None:
        """Invalidate entire cache"""
        self.cache.clear()
        self.position_hashes.clear()
    
    def _evict_oldest(self) -> None:
        """Evict oldest cache entries"""
        if not self.cache:
            return
        
        # Simple eviction: remove 10% of cache
        evict_count = max(1, len(self.cache) // 10)
        keys_to_remove = list(self.cache.keys())[:evict_count]
        
        for key in keys_to_remove:
            del self.cache[key]
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'total_requests': total_requests,
            'hit_rate': hit_rate,
            'cache_size': len(self.cache),
            'max_size': self.max_size,
            'slider_rays_precomputed': len(self.slider_rays)
        }
    
    def optimize_for_quiescent_plies(self, board_state: str, ply: int) -> List[Tuple]:
        """Optimized move generation for quiescent plies"""
        # Try to reuse moves from previous ply if position is similar
        if ply > 0:
            prev_moves = self.get_quiescent_moves(board_state, ply - 1)
            if prev_moves:
                # Filter moves that are still legal
                # This is a simplified version - real implementation would check legality
                return prev_moves
        
        # Fall back to normal move generation
        return []

# Global cache instance
move_cache = QECMoveCache()

def get_move_cache() -> QECMoveCache:
    """Get the global move cache instance"""
    return move_cache

def get_slider_rays(x: int, y: int, piece_type: str) -> Set[Tuple[int, int]]:
    """Get precomputed slider rays"""
    return move_cache.get_slider_rays(x, y, piece_type)

def get_cache_stats() -> Dict[str, int]:
    """Get cache statistics"""
    return move_cache.get_cache_stats()

def clear_cache():
    """Clear the move cache"""
    move_cache.invalidate_all()
