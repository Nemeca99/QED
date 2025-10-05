"""
Property-Based Tests for QEC Entanglement Invariants
Tests critical entanglement properties using Hypothesis for comprehensive coverage
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

import main as qec_main
from hypothesis import given, strategies as st, settings, example
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant
import random
from typing import Dict, List, Set, Tuple, Any

class QECEntanglementInvariants:
    """Property-based tests for QEC entanglement invariants"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
    
    @given(st.integers(min_value=1, max_value=10000))
    @settings(max_examples=100)
    def test_entanglement_king_exclusion(self, seed: int):
        """Property: Entanglement links never include kings"""
        random.seed(seed)
        game = qec_main.Game(seed=seed)
        
        # Check white pawn links
        for pawn_id, target_id in game.ent.W_pawn_to_black.items():
            assert not target_id.startswith('B_K_'), f"Black king entangled: {target_id}"
            assert not target_id.startswith('W_K_'), f"White king entangled: {target_id}"
        
        # Check black pawn links  
        for pawn_id, target_id in game.ent.B_pawn_to_white.items():
            assert not target_id.startswith('W_K_'), f"White king entangled: {target_id}"
            assert not target_id.startswith('B_K_'), f"Black king entangled: {target_id}"
        
        self.passed += 1
    
    @given(st.integers(min_value=1, max_value=10000))
    @settings(max_examples=100)
    def test_entanglement_count_invariant(self, seed: int):
        """Property: Exactly 7 entanglement links per side"""
        random.seed(seed)
        game = qec_main.Game(seed=seed)
        
        # Count white pawn links
        w_links = len(game.ent.W_pawn_to_black)
        assert w_links == 7, f"Expected 7 white pawn links, got {w_links}"
        
        # Count black pawn links
        b_links = len(game.ent.B_pawn_to_white)
        assert b_links == 7, f"Expected 7 black pawn links, got {b_links}"
        
        # Check free pawns exist
        assert game.ent.white_free_pawn is not None, "White should have a free pawn"
        assert game.ent.black_free_pawn is not None, "Black should have a free pawn"
        
        # Verify free pawns are not in entanglement maps
        assert game.ent.white_free_pawn not in game.ent.W_pawn_to_black, "Free pawn should not be entangled"
        assert game.ent.black_free_pawn not in game.ent.B_pawn_to_white, "Free pawn should not be entangled"
        
        self.passed += 1
    
    @given(st.integers(min_value=1, max_value=1000))
    @settings(max_examples=50)
    def test_entanglement_break_on_capture(self, seed: int):
        """Property: Entanglement links break when pieces are captured"""
        random.seed(seed)
        game = qec_main.Game(seed=seed)
        
        # Get initial entanglement state
        initial_w_links = set(game.ent.W_pawn_to_black.items())
        initial_b_links = set(game.ent.B_pawn_to_white.items())
        
        # Run a few moves to potentially trigger captures
        for _ in range(10):
            legal_moves = game.board.legal_moves()
            if not legal_moves:
                break
            
            # Make a random move
            move = random.choice(legal_moves)
            piece, to, spec = move
            
            # Check if this is a capture
            target = game.board.piece_at(to)
            if target and target.color != piece.color:
                # This is a capture - check if any links were broken
                current_w_links = set(game.ent.W_pawn_to_black.items())
                current_b_links = set(game.ent.B_pawn_to_white.items())
                
                # Links should be broken if the captured piece was entangled
                for pawn, target_id in initial_w_links:
                    if target_id == target.id:
                        assert (pawn, target_id) not in current_w_links, f"Link not broken after capture: {pawn} -> {target_id}"
                
                for pawn, target_id in initial_b_links:
                    if target_id == target.id:
                        assert (pawn, target_id) not in current_b_links, f"Link not broken after capture: {pawn} -> {target_id}"
            
            # Apply the move
            game.board._apply_move_internal(piece.pos, to, spec)
        
        self.passed += 1
    
    @given(st.integers(min_value=1, max_value=1000))
    @settings(max_examples=50)
    def test_entanglement_break_on_promotion(self, seed: int):
        """Property: Entanglement links break when pawns promote"""
        random.seed(seed)
        game = qec_main.Game(seed=seed)
        
        # Get initial entanglement state
        initial_w_links = set(game.ent.W_pawn_to_black.items())
        initial_b_links = set(game.ent.B_pawn_to_white.items())
        
        # Run moves to potentially trigger promotions
        for _ in range(20):
            legal_moves = game.board.legal_moves()
            if not legal_moves:
                break
            
            # Look for promotion moves
            promotion_moves = [move for move in legal_moves if move[2].get('promotion')]
            if promotion_moves:
                move = random.choice(promotion_moves)
                piece, to, spec = move
                
                # Check if promoting piece was entangled
                for pawn, target_id in initial_w_links:
                    if pawn == piece.id:
                        # This pawn is promoting - link should be broken
                        current_w_links = set(game.ent.W_pawn_to_black.items())
                        assert (pawn, target_id) not in current_w_links, f"Link not broken after promotion: {pawn} -> {target_id}"
                
                for pawn, target_id in initial_b_links:
                    if pawn == piece.id:
                        # This pawn is promoting - link should be broken
                        current_b_links = set(game.ent.B_pawn_to_white.items())
                        assert (pawn, target_id) not in current_b_links, f"Link not broken after promotion: {pawn} -> {target_id}"
            
            # Make a random move
            move = random.choice(legal_moves)
            piece, to, spec = move
            game.board._apply_move_internal(piece.pos, to, spec)
        
        self.passed += 1
    
    @given(st.integers(min_value=1, max_value=1000))
    @settings(max_examples=50)
    def test_entanglement_symmetry(self, seed: int):
        """Property: Entanglement maps are symmetric (no duplicate targets)"""
        random.seed(seed)
        game = qec_main.Game(seed=seed)
        
        # Check white pawn targets are unique
        w_targets = list(game.ent.W_pawn_to_black.values())
        assert len(w_targets) == len(set(w_targets)), f"Duplicate white pawn targets: {w_targets}"
        
        # Check black pawn targets are unique
        b_targets = list(game.ent.B_pawn_to_white.values())
        assert len(b_targets) == len(set(b_targets)), f"Duplicate black pawn targets: {b_targets}"
        
        # Check no overlap between white and black targets
        w_target_set = set(w_targets)
        b_target_set = set(b_targets)
        overlap = w_target_set.intersection(b_target_set)
        assert len(overlap) == 0, f"Overlapping targets between sides: {overlap}"
        
        self.passed += 1
    
    @given(st.integers(min_value=1, max_value=1000))
    @settings(max_examples=50)
    def test_entanglement_persistence(self, seed: int):
        """Property: Entanglement links persist unless broken by capture/promotion"""
        random.seed(seed)
        game = qec_main.Game(seed=seed)
        
        # Get initial entanglement state
        initial_w_links = dict(game.ent.W_pawn_to_black)
        initial_b_links = dict(game.ent.B_pawn_to_white)
        
        # Run several moves
        for _ in range(15):
            legal_moves = game.board.legal_moves()
            if not legal_moves:
                break
            
            # Make a random move
            move = random.choice(legal_moves)
            piece, to, spec = move
            
            # Check that non-capture, non-promotion moves don't break links
            target = game.board.piece_at(to)
            is_capture = target and target.color != piece.color
            is_promotion = spec.get('promotion') is not None
            
            if not is_capture and not is_promotion:
                # Links should persist
                current_w_links = dict(game.ent.W_pawn_to_black)
                current_b_links = dict(game.ent.B_pawn_to_white)
                
                # Check that existing links are still there
                for pawn, target_id in initial_w_links.items():
                    if pawn in current_w_links:
                        assert current_w_links[pawn] == target_id, f"Link changed unexpectedly: {pawn} -> {target_id}"
                
                for pawn, target_id in initial_b_links.items():
                    if pawn in current_b_links:
                        assert current_b_links[pawn] == target_id, f"Link changed unexpectedly: {pawn} -> {target_id}"
            
            # Apply the move
            game.board._apply_move_internal(piece.pos, to, spec)
        
        self.passed += 1
    
    def run_all_tests(self):
        """Run all property-based tests"""
        print("=== QEC Entanglement Property-Based Tests ===")
        
        test_methods = [
            self.test_entanglement_king_exclusion,
            self.test_entanglement_count_invariant,
            self.test_entanglement_break_on_capture,
            self.test_entanglement_break_on_promotion,
            self.test_entanglement_symmetry,
            self.test_entanglement_persistence
        ]
        
        for test_method in test_methods:
            try:
                print(f"Running {test_method.__name__}...")
                test_method()
                print(f"✅ {test_method.__name__} passed")
            except Exception as e:
                print(f"❌ {test_method.__name__} failed: {e}")
                self.failed += 1
        
        print(f"\n=== Property-Based Test Results ===")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Total: {self.passed + self.failed}")
        
        if self.failed == 0:
            print("🎯 All entanglement invariants verified!")
            return True
        else:
            print("❌ Some invariants failed")
            return False

def main():
    """Main test runner"""
    tester = QECEntanglementInvariants()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
