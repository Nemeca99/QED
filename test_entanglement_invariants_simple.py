"""
Simple Entanglement Invariants Tests for QEC
Tests critical entanglement properties without Hypothesis dependency
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

import main as qec_main
import random
from typing import Dict, List, Set, Tuple, Any

class QECEntanglementInvariants:
    """Simple property-based tests for QEC entanglement invariants"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
    
    def test_entanglement_king_exclusion(self, num_tests: int = 100):
        """Property: Entanglement links never include kings"""
        print("Testing entanglement king exclusion...")
        
        for i in range(num_tests):
            seed = 42 + i
            random.seed(seed)
            game = qec_main.Game(seed=seed)
            
            # Check white pawn links
            for pawn_id, target_id in game.ent.W_pawn_to_black.items():
                if target_id.startswith('B_K_') or target_id.startswith('W_K_'):
                    print(f"❌ King entanglement found: {target_id}")
                    self.failed += 1
                    return False
            
            # Check black pawn links  
            for pawn_id, target_id in game.ent.B_pawn_to_white.items():
                if target_id.startswith('W_K_') or target_id.startswith('B_K_'):
                    print(f"❌ King entanglement found: {target_id}")
                    self.failed += 1
                    return False
        
        self.passed += 1
        print(f"✅ King exclusion test passed ({num_tests} tests)")
        return True
    
    def test_entanglement_count_invariant(self, num_tests: int = 100):
        """Property: Exactly 7 entanglement links per side"""
        print("Testing entanglement count invariant...")
        
        for i in range(num_tests):
            seed = 42 + i
            random.seed(seed)
            game = qec_main.Game(seed=seed)
            
            # Count white pawn links
            w_links = len(game.ent.W_pawn_to_black)
            if w_links != 7:
                print(f"❌ Expected 7 white pawn links, got {w_links}")
                self.failed += 1
                return False
            
            # Count black pawn links
            b_links = len(game.ent.B_pawn_to_white)
            if b_links != 7:
                print(f"❌ Expected 7 black pawn links, got {b_links}")
                self.failed += 1
                return False
            
            # Check free pawns exist
            if game.ent.white_free_pawn is None:
                print("❌ White should have a free pawn")
                self.failed += 1
                return False
            
            if game.ent.black_free_pawn is None:
                print("❌ Black should have a free pawn")
                self.failed += 1
                return False
            
            # Verify free pawns are not in entanglement maps
            if game.ent.white_free_pawn in game.ent.W_pawn_to_black:
                print("❌ Free pawn should not be entangled")
                self.failed += 1
                return False
            
            if game.ent.black_free_pawn in game.ent.B_pawn_to_white:
                print("❌ Free pawn should not be entangled")
                self.failed += 1
                return False
        
        self.passed += 1
        print(f"✅ Count invariant test passed ({num_tests} tests)")
        return True
    
    def test_entanglement_symmetry(self, num_tests: int = 100):
        """Property: Entanglement maps are symmetric (no duplicate targets)"""
        print("Testing entanglement symmetry...")
        
        for i in range(num_tests):
            seed = 42 + i
            random.seed(seed)
            game = qec_main.Game(seed=seed)
            
            # Check white pawn targets are unique
            w_targets = list(game.ent.W_pawn_to_black.values())
            if len(w_targets) != len(set(w_targets)):
                print(f"❌ Duplicate white pawn targets: {w_targets}")
                self.failed += 1
                return False
            
            # Check black pawn targets are unique
            b_targets = list(game.ent.B_pawn_to_white.values())
            if len(b_targets) != len(set(b_targets)):
                print(f"❌ Duplicate black pawn targets: {b_targets}")
                self.failed += 1
                return False
            
            # Check no overlap between white and black targets
            w_target_set = set(w_targets)
            b_target_set = set(b_targets)
            overlap = w_target_set.intersection(b_target_set)
            if len(overlap) > 0:
                print(f"❌ Overlapping targets between sides: {overlap}")
                self.failed += 1
                return False
        
        self.passed += 1
        print(f"✅ Symmetry test passed ({num_tests} tests)")
        return True
    
    def run_all_tests(self):
        """Run all invariant tests"""
        print("=== QEC Entanglement Invariant Tests ===")
        
        test_methods = [
            (self.test_entanglement_king_exclusion, 50),
            (self.test_entanglement_count_invariant, 50),
            (self.test_entanglement_symmetry, 50)
        ]
        
        for test_method, num_tests in test_methods:
            try:
                test_method(num_tests)
            except Exception as e:
                print(f"❌ {test_method.__name__} failed: {e}")
                self.failed += 1
        
        print(f"\n=== Invariant Test Results ===")
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
