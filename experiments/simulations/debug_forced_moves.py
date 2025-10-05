"""
Debug Forced Moves in QEC
Test and debug the forced-move rule implementation
"""

import os
import sys
import random
from main import Game, Board, Piece, Square, Color

class QECForcedMoveDebugger:
    """Debug forced-move rule implementation"""
    
    def __init__(self):
        self.debug_log = []
        
    def debug_single_game(self, seed: int = 42):
        """Debug a single game with detailed forced-move tracking"""
        print(f"=== Debugging QEC Forced Moves (Seed: {seed}) ===")
        
        random.seed(seed)
        game = Game(seed=seed)
        game.live = True
        
        # Enable debug logging
        os.environ["QEC_LIVE"] = "1"
        os.environ["QEC_LIVE_DETAILS"] = "1"
        
        move_count = 0
        forced_count = 0
        reactive_count = 0
        
        print(f"Initial entanglement map:")
        print(f"  W_pawn_to_black: {game.ent.W_pawn_to_black}")
        print(f"  B_pawn_to_white: {game.ent.B_pawn_to_white}")
        print()
        
        while move_count < 50:  # Limit for debugging
            current_color = game.board.to_move
            legal_moves = game.board.legal_moves()
            
            if not legal_moves:
                print(f"Game ended at move {move_count}")
                break
            
            print(f"Move {move_count + 1}: {current_color} to move")
            print(f"  Legal moves: {len(legal_moves)}")
            
            # Choose a random move for debugging
            chosen_move = random.choice(legal_moves)
            piece, to, spec = chosen_move
            frm = piece.pos
            
            print(f"  Chosen move: {piece.kind} from {frm} to {to}")
            if spec:
                print(f"  Special: {spec}")
            
            # Apply move
            meta = game.board._apply_move_internal(frm, to, spec)
            move_count += 1
            
            print(f"  Move applied. Meta: {meta}")
            
            # Check for forced counterpart move
            print(f"  Checking for forced counterpart...")
            forced_happened = False
            
            if meta.get("castle_rook_to") is not None:
                rook_sq = meta["castle_rook_to"]
                rook = game.board.piece_at(rook_sq)
                if rook is not None:
                    print(f"    Castling rook at {rook_sq}, checking counterpart...")
                    forced_happened = game._maybe_force_counterpart(rook.id, record=True)
            else:
                moved_id = meta.get("moved_id", "")
                print(f"    Moved piece ID: {moved_id}")
                if moved_id:
                    print(f"    Checking counterpart for {moved_id}...")
                    forced_happened = game._maybe_force_counterpart(moved_id, record=True)
            
            if forced_happened:
                forced_count += 1
                print(f"    ✅ FORCED MOVE TRIGGERED! Total: {forced_count}")
            else:
                print(f"    ❌ No forced move triggered")
            
            # Check for reactive king escape
            defender = game.board.to_move
            if game.board.in_check(defender):
                print(f"  {defender} is in check, checking reactive escape...")
                reactive_happened = game._do_reactive_king_escape(defender, record=True)
                if reactive_happened:
                    reactive_count += 1
                    print(f"    ✅ REACTIVE MOVE TRIGGERED! Total: {reactive_count}")
                else:
                    print(f"    ❌ No reactive escape possible - checkmate!")
                    break
            else:
                print(f"  {defender} not in check")
            
            print(f"  Current entanglement:")
            print(f"    W_pawn_to_black: {game.ent.W_pawn_to_black}")
            print(f"    B_pawn_to_white: {game.ent.B_pawn_to_white}")
            print()
        
        print(f"=== Game Summary ===")
        print(f"Total moves: {move_count}")
        print(f"Forced moves: {forced_count}")
        print(f"Reactive moves: {reactive_count}")
        print(f"Final entanglement:")
        print(f"  W_pawn_to_black: {game.ent.W_pawn_to_black}")
        print(f"  B_pawn_to_white: {game.ent.B_pawn_to_white}")
        
        return {
            'moves': move_count,
            'forced': forced_count,
            'reactive': reactive_count
        }
    
    def debug_entanglement_logic(self):
        """Debug entanglement logic specifically"""
        print("=== Debugging Entanglement Logic ===")
        
        # Create a simple test case
        game = Game(seed=42)
        
        print("Initial entanglement state:")
        print(f"  W_pawn_to_black: {game.ent.W_pawn_to_black}")
        print(f"  B_pawn_to_white: {game.ent.B_pawn_to_white}")
        
        # Check if any pieces are entangled
        entangled_pieces = []
        for piece in game.board.pieces:
            if piece.alive:
                counterpart = game.ent.linked_counterpart_id(piece.id)
                if counterpart:
                    entangled_pieces.append((piece.id, counterpart))
        
        print(f"Entangled pieces: {entangled_pieces}")
        
        if not entangled_pieces:
            print("❌ No entangled pieces found! This explains why no forced moves occur.")
            print("The entanglement map might not be properly initialized.")
        else:
            print("✅ Found entangled pieces, checking forced-move logic...")
            
            # Test forced-move logic for each entangled piece
            for piece_id, counterpart_id in entangled_pieces:
                print(f"Testing forced move for {piece_id} -> {counterpart_id}")
                result = game._maybe_force_counterpart(piece_id, record=False)
                print(f"  Result: {result}")

if __name__ == "__main__":
    debugger = QECForcedMoveDebugger()
    
    # Debug entanglement logic first
    debugger.debug_entanglement_logic()
    print()
    
    # Debug a single game
    result = debugger.debug_single_game(seed=42)
    print(f"Debug result: {result}")
