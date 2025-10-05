"""
Quantum Entanglement Chess (QEC) – Terminal Prototype

Notes
- Deterministic, turn-based simulator with random self-play for both sides.
- Implements classical chess legality plus entanglement overlays per project rules:
  - Dual entanglement: 7 white pawns ↔ black non-king; 7 black pawns ↔ white non-king; 1 free pawn per side; kings never entangled.
  - Single forced response per turn: if a moved piece is entangled, its counterpart must make exactly one legal move; the counterpart's owner chooses (here: random).
  - Castling: only the rook's relocation can trigger entanglement. King is never entangled.
  - Reactive check: immediate one-square king escape within the same turn; if none, instant mate.
  - Promotion: auto-queen; promotion or capture frees both linked members; no re-entangle.

This is an engineering prototype to validate rules and surface edge cases. It is not optimized.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Iterable
import os
import json
import argparse


Color = str  # "W" or "B"
PieceType = str  # "K","Q","R","B","N","P"
Square = Tuple[int, int]  # (file 0..7, rank 0..7)


FILES = "abcdefgh"
RANKS = "12345678"


def in_bounds(x: int, y: int) -> bool:
    return 0 <= x < 8 and 0 <= y < 8


def sq_to_str(sq: Square) -> str:
    f, r = sq
    return f"{FILES[f]}{RANKS[r]}"


def opposite(c: Color) -> Color:
    return "B" if c == "W" else "W"


@dataclass
class Piece:
    color: Color
    kind: PieceType
    pos: Square
    alive: bool = True
    id: str = ""  # stable identifier within side (e.g., W_P_a2, B_R_a8)

    def copy(self) -> "Piece":
        return Piece(self.color, self.kind, self.pos, self.alive, self.id)


class Board:
    def __init__(self) -> None:
        self.board: List[List[Optional[Piece]]] = [[None for _ in range(8)] for _ in range(8)]
        self.to_move: Color = "W"
        # Castling rights: (Wk, Wq, Bk, Bq)
        self.castling: Dict[str, bool] = {"K": True, "Q": True, "k": True, "q": True}
        self.en_passant: Optional[Square] = None
        self.halfmove_clock: int = 0
        self.fullmove_number: int = 1

        self.pieces: List[Piece] = []
        self._setup_startpos()

    def _place(self, p: Piece) -> None:
        f, r = p.pos
        self.board[r][f] = p
        self.pieces.append(p)

    def _setup_startpos(self) -> None:
        # Pawns
        for f in range(8):
            self._place(Piece("W", "P", (f, 1), True, id=f"W_P_{FILES[f]}2"))
            self._place(Piece("B", "P", (f, 6), True, id=f"B_P_{FILES[f]}7"))
        # Rooks
        self._place(Piece("W", "R", (0, 0), True, id="W_R_a1"))
        self._place(Piece("W", "R", (7, 0), True, id="W_R_h1"))
        self._place(Piece("B", "R", (0, 7), True, id="B_R_a8"))
        self._place(Piece("B", "R", (7, 7), True, id="B_R_h8"))
        # Knights
        self._place(Piece("W", "N", (1, 0), True, id="W_N_b1"))
        self._place(Piece("W", "N", (6, 0), True, id="W_N_g1"))
        self._place(Piece("B", "N", (1, 7), True, id="B_N_b8"))
        self._place(Piece("B", "N", (6, 7), True, id="B_N_g8"))
        # Bishops
        self._place(Piece("W", "B", (2, 0), True, id="W_B_c1"))
        self._place(Piece("W", "B", (5, 0), True, id="W_B_f1"))
        self._place(Piece("B", "B", (2, 7), True, id="B_B_c8"))
        self._place(Piece("B", "B", (5, 7), True, id="B_B_f8"))
        # Queens
        self._place(Piece("W", "Q", (3, 0), True, id="W_Q_d1"))
        self._place(Piece("B", "Q", (3, 7), True, id="B_Q_d8"))
        # Kings
        self._place(Piece("W", "K", (4, 0), True, id="W_K_e1"))
        self._place(Piece("B", "K", (4, 7), True, id="B_K_e8"))

    def copy(self) -> "Board":
        nb = Board.__new__(Board)
        nb.board = [[None for _ in range(8)] for _ in range(8)]
        nb.pieces = []
        for p in self.pieces:
            cp = p.copy()
            nb.pieces.append(cp)
        # Rebuild board grid
        for p in nb.pieces:
            if p.alive:
                f, r = p.pos
                nb.board[r][f] = p
        nb.to_move = self.to_move
        nb.castling = dict(self.castling)
        nb.en_passant = None if self.en_passant is None else (self.en_passant[0], self.en_passant[1])
        nb.halfmove_clock = self.halfmove_clock
        nb.fullmove_number = self.fullmove_number
        return nb

    def piece_at(self, sq: Square) -> Optional[Piece]:
        f, r = sq
        return self.board[r][f]

    def king_square(self, color: Color) -> Square:
        for p in self.pieces:
            if p.alive and p.color == color and p.kind == "K":
                return p.pos
        raise RuntimeError("King not found")

    def is_attacked(self, sq: Square, by_color: Color) -> bool:
        # Generate pseudo-legal moves for all enemy pieces and see if any hit sq
        for p in self.pieces:
            if not p.alive or p.color != by_color:
                continue
            for _, to, _ in self._gen_piece_moves(p, attacks_only=True):
                if to == sq:
                    return True
                # Pawns: attacks_only will generate diagonals
        return False

    def in_check(self, color: Color) -> bool:
        return self.is_attacked(self.king_square(color), opposite(color))

    def legal_moves(self) -> List[Tuple[Piece, Square, Dict[str, object]]]:
        moves: List[Tuple[Piece, Square, Dict[str, object]]] = []
        for p in self.pieces:
            if not p.alive or p.color != self.to_move:
                continue
            for frm, to, special in self._gen_piece_moves(p, attacks_only=False):
                # Apply move and test king safety
                b2 = self.copy()
                _ = b2._apply_move_internal(frm, to, special)
                if not b2.in_check(p.color):
                    moves.append((p, to, special))
        return moves

    def _gen_piece_moves(self, p: Piece, attacks_only: bool) -> Iterable[Tuple[Square, Square, Dict[str, object]]]:
        f, r = p.pos
        if p.kind == "P":
            dir_ = 1 if p.color == "W" else -1
            start_rank = 1 if p.color == "W" else 6
            # Captures (also used for attacks_only)
            for df in (-1, 1):
                nf, nr = f + df, r + dir_
                if in_bounds(nf, nr):
                    target = self.piece_at((nf, nr))
                    if target and target.alive and target.color != p.color:
                        spec = {"capture": True}
                        # Promotion
                        if nr == (7 if p.color == "W" else 0):
                            spec["promotion"] = "Q"
                        yield (p.pos, (nf, nr), spec)
                    # En passant capture
                    if self.en_passant is not None and self.en_passant == (nf, nr):
                        # en passant target square is empty, but capture pawn is behind it
                        spec = {"en_passant": True}
                        yield (p.pos, (nf, nr), spec)
            if attacks_only:
                return
            # Forward moves
            nf, nr = f, r + dir_
            if in_bounds(nf, nr) and self.piece_at((nf, nr)) is None:
                spec = {}
                if nr == (7 if p.color == "W" else 0):
                    spec["promotion"] = "Q"
                yield (p.pos, (nf, nr), spec)
                # Double push
                if r == start_rank:
                    nr2 = r + 2 * dir_
                    if self.piece_at((nf, nr2)) is None:
                        yield (p.pos, (nf, nr2), {"double_push": True})
        elif p.kind in ("N", "K"):
            deltas = (
                [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]
                if p.kind == "N"
                else [
                    (1, 0), (-1, 0), (0, 1), (0, -1),
                    (1, 1), (1, -1), (-1, 1), (-1, -1),
                ]
            )
            for df, dr in deltas:
                nf, nr = f + df, r + dr
                if not in_bounds(nf, nr):
                    continue
                target = self.piece_at((nf, nr))
                if target is None or target.color != p.color:
                    yield (p.pos, (nf, nr), {})
            if p.kind == "K" and not attacks_only:
                # Castling
                if p.color == "W" and p.pos == (4, 0) and not self.in_check("W"):
                    # King side
                    if self.castling["K"] and self.piece_at((5, 0)) is None and self.piece_at((6, 0)) is None:
                        if not self.is_attacked((5, 0), "B") and not self.is_attacked((6, 0), "B"):
                            yield (p.pos, (6, 0), {"castle": "K"})
                    # Queen side
                    if self.castling["Q"] and self.piece_at((3, 0)) is None and self.piece_at((2, 0)) is None and self.piece_at((1, 0)) is None:
                        if not self.is_attacked((3, 0), "B") and not self.is_attacked((2, 0), "B"):
                            yield (p.pos, (2, 0), {"castle": "Q"})
                if p.color == "B" and p.pos == (4, 7) and not self.in_check("B"):
                    if self.castling["k"] and self.piece_at((5, 7)) is None and self.piece_at((6, 7)) is None:
                        if not self.is_attacked((5, 7), "W") and not self.is_attacked((6, 7), "W"):
                            yield (p.pos, (6, 7), {"castle": "k"})
                    if self.castling["q"] and self.piece_at((3, 7)) is None and self.piece_at((2, 7)) is None and self.piece_at((1, 7)) is None:
                        if not self.is_attacked((3, 7), "W") and not self.is_attacked((2, 7), "W"):
                            yield (p.pos, (2, 7), {"castle": "q"})
        else:
            # Sliding pieces: B, R, Q
            rays = []
            if p.kind in ("B", "Q"):
                rays += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            if p.kind in ("R", "Q"):
                rays += [(1, 0), (-1, 0), (0, 1), (0, -1)]
            for df, dr in rays:
                nf, nr = f + df, r + dr
                while in_bounds(nf, nr):
                    target = self.piece_at((nf, nr))
                    if target is None:
                        yield (p.pos, (nf, nr), {})
                    else:
                        if target.color != p.color:
                            yield (p.pos, (nf, nr), {"capture": True})
                        break
                    nf += df
                    nr += dr

    def _apply_move_internal(self, frm: Square, to: Square, special: Dict[str, object]) -> Dict[str, object]:
        # Returns move metadata including details needed by entanglement layer
        moved: Optional[Piece] = self.piece_at(frm)
        assert moved is not None and moved.alive
        meta: Dict[str, object] = {
            "moved_id": moved.id,
            "moved_kind": moved.kind,
            "from": frm,
            "to": to,
            "capture_id": None,
            "castle_rook_from": None,
            "castle_rook_to": None,
        }

        self.en_passant = None
        # Handle special moves
        if special.get("castle"):
            # Move king
            self._move_piece(moved, to)
            # Move rook accordingly
            if to == (6, 0):  # W king side
                rook_from, rook_to = (7, 0), (5, 0)
            elif to == (2, 0):  # W queen side
                rook_from, rook_to = (0, 0), (3, 0)
            elif to == (6, 7):  # B king side
                rook_from, rook_to = (7, 7), (5, 7)
            else:  # to == (2,7)
                rook_from, rook_to = (0, 7), (3, 7)
            rook = self.piece_at(rook_from)
            assert rook and rook.kind == "R" and rook.color == moved.color
            self._move_piece(rook, rook_to)
            meta["castle_rook_from"] = rook_from
            meta["castle_rook_to"] = rook_to
            # Update castling rights
            if moved.color == "W":
                self.castling["K"] = False
                self.castling["Q"] = False
            else:
                self.castling["k"] = False
                self.castling["q"] = False
        else:
            # Capture (including en passant)
            target = self.piece_at(to)
            if special.get("en_passant"):
                # Captured pawn is behind target square
                df = 1 if moved.color == "W" else -1
                cap_sq = (to[0], to[1] - df)
                cap = self.piece_at(cap_sq)
                if cap:
                    self._capture_piece(cap)
                    meta["capture_id"] = cap.id
            elif target is not None and target.color != moved.color:
                self._capture_piece(target)
                meta["capture_id"] = target.id

            # Move piece
            self._move_piece(moved, to)

            # Promotion
            if special.get("promotion"):
                moved.kind = "Q"

            # Double push sets en passant square
            if special.get("double_push"):
                dir_ = 1 if moved.color == "W" else -1
                self.en_passant = (to[0], to[1] - dir_)

            # Update castling rights if king or rook moved/captured
            self._update_castling_rights_on_move_or_capture(meta)

        # Halfmove clock (reset on pawn move or capture)
        if moved.kind == "P" or meta["capture_id"]:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        # Switch side to move and fullmove number
        self.to_move = opposite(self.to_move)
        if self.to_move == "W":
            self.fullmove_number += 1

        return meta

    def _move_piece(self, p: Piece, to: Square) -> None:
        pf, pr = p.pos
        self.board[pr][pf] = None
        p.pos = to
        tf, tr = to
        self.board[tr][tf] = p

    def _capture_piece(self, p: Piece) -> None:
        f, r = p.pos
        self.board[r][f] = None
        p.alive = False

    def to_fen(self) -> str:
        rows = []
        for r in range(7, -1, -1):
            empty = 0
            row = ""
            for f in range(8):
                p = self.board[r][f]
                if p is None:
                    empty += 1
                else:
                    if empty:
                        row += str(empty)
                        empty = 0
                    ch = p.kind
                    row += ch.lower() if p.color == "B" else ch
            if empty:
                row += str(empty)
            rows.append(row)
        placement = "/".join(rows)
        active = 'w' if self.to_move == 'W' else 'b'
        c = ''
        c += 'K' if self.castling.get('K') else ''
        c += 'Q' if self.castling.get('Q') else ''
        c += 'k' if self.castling.get('k') else ''
        c += 'q' if self.castling.get('q') else ''
        if not c:
            c = '-'
        ep = '-' if self.en_passant is None else sq_to_str(self.en_passant)
        return f"{placement} {active} {c} {ep} {self.halfmove_clock} {self.fullmove_number}"

    def _update_castling_rights_on_move_or_capture(self, meta: Dict[str, object]) -> None:
        moved_id = meta["moved_id"]
        # Moving king loses rights
        if moved_id in ("W_K_e1", "B_K_e8"):
            if moved_id.startswith("W_"):
                self.castling["K"] = False
                self.castling["Q"] = False
            else:
                self.castling["k"] = False
                self.castling["q"] = False
        # Moving rooks loses that side
        if moved_id == "W_R_h1":
            self.castling["K"] = False
        if moved_id == "W_R_a1":
            self.castling["Q"] = False
        if moved_id == "B_R_h8":
            self.castling["k"] = False
        if moved_id == "B_R_a8":
            self.castling["q"] = False
        # Capturing rooks/king squares also affects
        cap_id = meta.get("capture_id")
        if cap_id == "W_R_h1":
            self.castling["K"] = False
        if cap_id == "W_R_a1":
            self.castling["Q"] = False
        if cap_id == "B_R_h8":
            self.castling["k"] = False
        if cap_id == "B_R_a8":
            self.castling["q"] = False


class Entanglement:
    """Manages dual entanglement mappings and invariants."""

    def __init__(self, board: Board) -> None:
        self.W_pawn_to_black: Dict[str, str] = {}
        self.B_pawn_to_white: Dict[str, str] = {}
        self.white_free_pawn: Optional[str] = None
        self.black_free_pawn: Optional[str] = None
        self._init_from_env_or_random(board)

    def _init_from_env_or_random(self, board: Board) -> None:
        map_env = os.getenv("QEC_MAP")
        if map_env:
            data = json.loads(map_env)
            self.W_pawn_to_black = dict(data.get("W_pawn_to_black", {}))
            self.B_pawn_to_white = dict(data.get("B_pawn_to_white", {}))
            self.white_free_pawn = data.get("white_free_pawn")
            self.black_free_pawn = data.get("black_free_pawn")
            return
        self._init_random_dual_mapping(board)

    def _init_random_dual_mapping(self, board: Board) -> None:
        # Collect IDs
        white_pawns = [p.id for p in board.pieces if p.alive and p.color == "W" and p.kind == "P"]
        black_pawns = [p.id for p in board.pieces if p.alive and p.color == "B" and p.kind == "P"]
        black_non_king = [p.id for p in board.pieces if p.alive and p.color == "B" and p.kind != "K"]
        white_non_king = [p.id for p in board.pieces if p.alive and p.color == "W" and p.kind != "K"]

        # Choose free pawns
        self.white_free_pawn = random.choice(white_pawns)
        self.black_free_pawn = random.choice(black_pawns)
        w_candidates = [pid for pid in white_pawns if pid != self.white_free_pawn]
        b_candidates = [pid for pid in black_pawns if pid != self.black_free_pawn]

        # Select 7 targets per side from non-king sets (must be distinct)
        # There are at least 15 non-king targets per side at start, so sample 7 without replacement
        black_targets = random.sample(black_non_king, 7)
        white_targets = random.sample(white_non_king, 7)

        random.shuffle(w_candidates)
        random.shuffle(b_candidates)

        self.W_pawn_to_black = {w_candidates[i]: black_targets[i] for i in range(7)}
        self.B_pawn_to_white = {b_candidates[i]: white_targets[i] for i in range(7)}

    def linked_counterpart_id(self, moved_piece_id: str) -> Optional[str]:
        # If a white pawn moved, its counterpart is the mapped black piece
        if moved_piece_id in self.W_pawn_to_black:
            return self.W_pawn_to_black[moved_piece_id]
        # If a black pawn moved, its counterpart is the mapped white piece
        if moved_piece_id in self.B_pawn_to_white:
            return self.B_pawn_to_white[moved_piece_id]
        # If a black non-king moved that is linked by a white pawn
        for pw, b_id in self.W_pawn_to_black.items():
            if b_id == moved_piece_id:
                return pw
        # If a white non-king moved that is linked by a black pawn
        for pb, w_id in self.B_pawn_to_white.items():
            if w_id == moved_piece_id:
                return pb
        return None

    def break_link_if_member(self, member_id: Optional[str]) -> None:
        if not member_id:
            return
        # Remove any mapping entries that include this member
        self.W_pawn_to_black = {k: v for k, v in self.W_pawn_to_black.items() if k != member_id and v != member_id}
        self.B_pawn_to_white = {k: v for k, v in self.B_pawn_to_white.items() if k != member_id and v != member_id}


class Game:
    def __init__(self, seed: Optional[int] = None) -> None:
        if seed is not None:
            random.seed(seed)
        self.board = Board()
        self.ent = Entanglement(self.board)
        self.move_log: List[str] = []
        self.pgn_moves: List[str] = []
        self.transcript: List[Dict[str, object]] = []
        self.policy = os.getenv("QEC_POLICY", "random")  # "random" | "heuristic"
        self.live: bool = os.getenv("QEC_LIVE", "0") == "1"
        self.live_details: bool = os.getenv("QEC_LIVE_DETAILS", "0") == "1"
        self._state_counts: Dict[str, int] = {}
        self._last_ent_hash: Optional[str] = None

    def run(self, max_plies: int = 600) -> str:
        # Main game loop: returns result string
        for _ in range(max_plies):
            res = self._play_turn()
            if res is not None:
                return res
        return "Result: draw by move limit"

    def _play_turn(self) -> Optional[str]:
        color = self.board.to_move
        legal = self.board.legal_moves()
        if not legal:
            if self.board.in_check(color):
                return f"Checkmate: {opposite(color)} wins"
            return "Stalemate"

        # Choose move per policy
        if self.policy == "minimax":
            p, to, spec = self._choose_minimax(legal, depth=2)
        elif self.policy == "heuristic":
            p, to, spec = self._choose_heuristic(legal)
        else:
            p, to, spec = random.choice(legal)
        live = self._find_piece_by_id(p.id)
        if live is None:
            return "Result: internal error (piece vanished)"
        frm = live.pos
        meta = self.board._apply_move_internal(frm, to, spec)

        # Record SAN-ish compact log entry
        self._log_move(meta)
        self._log_pgn_skeleton(meta)
        self._record_transcript_entry(kind="primary", meta=meta)

        # If primary move caused capture or promotion, break entanglement accordingly
        if meta.get("capture_id"):
            self.ent.break_link_if_member(meta["capture_id"])
        if spec.get("promotion"):
            self.ent.break_link_if_member(p.id)

        # Determine single forced response due to entanglement
        # If castling occurred, only the rook can trigger
        if meta.get("castle_rook_to") is not None:
            rook_sq = meta["castle_rook_to"]
            rook = self.board.piece_at(rook_sq)
            if rook is not None:
                self._maybe_force_counterpart(rook.id)
        else:
            self._maybe_force_counterpart(meta["moved_id"])

        # Reactive check: if defender is in check after move(s), they must move king one square now
        defender = self.board.to_move
        if self.board.in_check(defender):
            if not self._do_reactive_king_escape(defender):
                # No legal one-square king move exists: immediate checkmate
                return f"Checkmate: {opposite(defender)} wins"

        # Continue game
        return None

    def _evaluate(self, color: Color) -> int:
        # Heuristic: material + mobility + entanglement leverage + check terms
        val_map = {"K": 0, "Q": 900, "R": 500, "B": 330, "N": 320, "P": 100}
        score = 0
        for p in self.board.pieces:
            if not p.alive:
                continue
            s = val_map[p.kind]
            score += s if p.color == color else -s
        # Pseudo-mobility (fast, no king-safety filtering)
        def pseudo_count(c: Color) -> int:
            cnt = 0
            for q in self.board.pieces:
                if not q.alive or q.color != c:
                    continue
                for _frm, _to, _spec in self.board._gen_piece_moves(q, attacks_only=False):
                    cnt += 1
            return cnt
        score += 2 * (pseudo_count(color) - pseudo_count(opposite(color)))
        # Entanglement leverage: free pieces more valuable
        ent_members = set(self.ent.W_pawn_to_black.keys()) | set(self.ent.W_pawn_to_black.values()) | set(self.ent.B_pawn_to_white.keys()) | set(self.ent.B_pawn_to_white.values())
        for p in self.board.pieces:
            if not p.alive:
                continue
            if p.id not in ent_members:
                score += 10 if p.color == color else -10
        # Check terms
        if self.board.in_check(color):
            score -= 50
        if self.board.in_check(opposite(color)):
            score += 25
        return score

    def _choose_heuristic(self, legal: List[Tuple[Piece, Square, Dict[str, object]]]) -> Tuple[Piece, Square, Dict[str, object]]:
        color = self.board.to_move
        best = None
        best_score = -10**9
        for p, to, spec in legal:
            # Simulate full turn: primary, possible forced, reactive
            saved = self.board.copy(), self.ent.W_pawn_to_black.copy(), self.ent.B_pawn_to_white.copy()
            live = self._find_piece_by_id(p.id)
            if live is None:
                self._restore_state(saved)
                continue
            meta = self.board._apply_move_internal(live.pos, to, spec)
            # Primary break effects
            if meta.get("capture_id"):
                self.ent.break_link_if_member(meta["capture_id"])
            if spec.get("promotion"):
                self.ent.break_link_if_member(live.id)
            # Forced (castling rook prioritized)
            if meta.get("castle_rook_to") is not None:
                rook_sq = meta["castle_rook_to"]
                rook = self.board.piece_at(rook_sq)
                if rook is not None:
                    self._maybe_force_counterpart(rook.id, record=False)
            else:
                self._maybe_force_counterpart(meta["moved_id"], record=False)
            # Reactive check
            defender = self.board.to_move
            if self.board.in_check(defender):
                self._do_reactive_king_escape(defender, record=False)
            score = self._evaluate(color)
            # Restore
            self._restore_state(saved)
            if score > best_score:
                best_score = score
                best = (p, to, spec)
        assert best is not None
        return best

    def _simulate_full_turn(self, mover_color: Color, move: Tuple[Piece, Square, Dict[str, object]]) -> None:
        p, to, spec = move
        live = self._find_piece_by_id(p.id)
        if live is None:
            return
        meta = self.board._apply_move_internal(live.pos, to, spec)
        if meta.get("capture_id"):
            self.ent.break_link_if_member(meta["capture_id"])
        if spec.get("promotion"):
            self.ent.break_link_if_member(live.id)
        if meta.get("castle_rook_to") is not None:
            rook_sq = meta["castle_rook_to"]
            rook = self.board.piece_at(rook_sq)
            if rook is not None:
                self._maybe_force_counterpart(rook.id, record=False)
        else:
            self._maybe_force_counterpart(meta["moved_id"], record=False)
        defender = self.board.to_move
        if self.board.in_check(defender):
            self._do_reactive_king_escape(defender, record=False)

    def _score_after(self, frm: Square, to: Square, spec: Dict[str, object], pov: Color) -> int:
        # Simulate applying a specific move from current board state and return evaluation from pov
        saved = self.board.copy(), self.ent.W_pawn_to_black.copy(), self.ent.B_pawn_to_white.copy()
        meta = self.board._apply_move_internal(frm, to, spec)
        # Mirror runtime side-effects for fair scoring
        capture_id = meta.get("capture_id")
        if capture_id:
            self.ent.break_link_if_member(capture_id)
        if spec.get("promotion"):
            moved = self._find_piece_by_id(meta["moved_id"])  # type: ignore
            if moved:
                self.ent.break_link_if_member(moved.id)
        # Reactive check inside this simulation
        defender = self.board.to_move
        if self.board.in_check(defender):
            _ = self._do_reactive_king_escape(defender, record=False)
        val = self._evaluate(pov)
        self._restore_state(saved)
        return val

    def _choose_minimax(self, legal: List[Tuple[Piece, Square, Dict[str, object]]], depth: int = 2) -> Tuple[Piece, Square, Dict[str, object]]:
        color = self.board.to_move

        def negamax(d: int, pov: Color) -> int:
            if d == 0:
                # Quiescence: extend one ply if noisy (in check or captures available)
                if self._noisy():
                    best = -10**9
                    lm = self.board.legal_moves()
                    if not lm:
                        return -10**8 if self.board.in_check(self.board.to_move) else 0
                    for mv in lm:
                        # Only consider capture moves or if currently in check
                        to_sq = mv[1]
                        if (self.board.piece_at(to_sq) is None) and (not self.board.in_check(self.board.to_move)):
                            continue
                        saved_q = self.board.copy(), self.ent.W_pawn_to_black.copy(), self.ent.B_pawn_to_white.copy()
                        self._simulate_full_turn(self.board.to_move, mv)
                        # Evaluate directly at the resulting position for quiescence leaf
                        val_q = -self._evaluate(opposite(pov))
                        self._restore_state(saved_q)
                        if val_q > best:
                            best = val_q
                    return best
                return self._evaluate(pov)
            best_val = -10**9
            lm = self.board.legal_moves()
            if not lm:
                if self.board.in_check(self.board.to_move):
                    return -10**8
                return 0
            for mv in lm[:30]:
                saved = self.board.copy(), self.ent.W_pawn_to_black.copy(), self.ent.B_pawn_to_white.copy()
                self._simulate_full_turn(self.board.to_move, mv)
                val = -negamax(d - 1, opposite(pov))
                self._restore_state(saved)
                if val > best_val:
                    best_val = val
            return best_val

        best_move = None
        best_score = -10**9
        for mv in legal:
            saved = self.board.copy(), self.ent.W_pawn_to_black.copy(), self.ent.B_pawn_to_white.copy()
            self._simulate_full_turn(color, mv)
            val = -negamax(depth - 1, opposite(color))
            self._restore_state(saved)
            if val > best_score:
                best_score = val
                best_move = mv
        assert best_move is not None
        return best_move

    def _restore_state(self, saved) -> None:
        bcopy, Wmap, Bmap = saved
        # Restore board by overwriting self with copy (cheap reassign)
        self.board = bcopy
        self.ent.W_pawn_to_black = Wmap
        self.ent.B_pawn_to_white = Bmap

    def _maybe_force_counterpart(self, moved_piece_id: str, record: bool = True) -> bool:
        counterpart_id = self.ent.linked_counterpart_id(moved_piece_id)
        if counterpart_id is None:
            return False
        cp = self._find_piece_by_id(counterpart_id)
        if cp is None or not cp.alive:
            return False
        # Generate legal moves only for this counterpart
        legal = self._safe_moves_for_piece(cp)
        if not legal:
            return False
        # Choose for the owner of the counterpart using evaluator; always use fresh live position
        def _key(mv):
            live_now = self._find_piece_by_id(counterpart_id)
            if live_now is None or not live_now.alive:
                return -10**9
            return self._score_after(live_now.pos, mv[1], mv[2], live_now.color)
        p, to, spec = max(legal, key=_key)
        # Re-fetch live counterpart to avoid stale references after scoring simulations
        live_cp = self._find_piece_by_id(counterpart_id)
        if live_cp is None or not live_cp.alive:
            return False
        frm = live_cp.pos
        meta = self.board._apply_move_internal(frm, to, spec)
        if record:
            self._log_move(meta, forced=True)
            self._log_pgn_skeleton(meta, forced=True)
            self._record_transcript_entry(kind="forced", meta=meta)

        # If promotion or capture freed an entanglement, drop link
        if meta.get("capture_id"):
            self.ent.break_link_if_member(meta["capture_id"])
        # Promotion frees both; applied via piece kind change in board logic
        if spec.get("promotion"):
            self.ent.break_link_if_member(live_cp.id)

        return True

    def _do_reactive_king_escape(self, defender: Color, record: bool = True) -> bool:
        # Defender must move king one square legally now
        # Generate legal king moves only
        to_move_orig = self.board.to_move
        fullmove_orig = self.board.fullmove_number
        self.board.to_move = defender
        king = next(p for p in self.board.pieces if p.alive and p.color == defender and p.kind == "K")
        legal_king_moves = []
        for frm, to, spec in self.board._gen_piece_moves(king, attacks_only=False):
            # Ignore castling for reactive step; only one-square moves
            if spec.get("castle"):
                continue
            b2 = self.board.copy()
            b2._apply_move_internal(frm, to, spec)
            if not b2.in_check(defender):
                legal_king_moves.append((frm, to, spec))
        if not legal_king_moves:
            self.board.to_move = to_move_orig
            self.board.fullmove_number = fullmove_orig
            return False
        # Score each candidate using unified evaluator
        def _score(mv):
            return self._score_after(mv[0], mv[1], mv[2], defender)
        frm, to, spec = max(legal_king_moves, key=_score)
        meta = self.board._apply_move_internal(frm, to, spec)
        self.board.to_move = to_move_orig
        self.board.fullmove_number = fullmove_orig
        if record:
            self._log_move(meta, reactive=True)
            self._log_pgn_skeleton(meta, reactive=True)
            self._record_transcript_entry(kind="reactive", meta=meta)
        return True

    def _noisy(self) -> bool:
        # Noisy if side to move is in check or any capture is available
        if self.board.in_check(self.board.to_move):
            return True
        for p in self.board.pieces:
            if not p.alive or p.color != self.board.to_move:
                continue
            for _frm, to, spec in self.board._gen_piece_moves(p, attacks_only=False):
                tgt = self.board.piece_at(to)
                if tgt is not None and tgt.color != p.color:
                    return True
        return False

    def _safe_moves_for_piece(self, piece: Piece) -> List[Tuple[Piece, Square, Dict[str, object]]]:
        moves: List[Tuple[Piece, Square, Dict[str, object]]] = []
        for frm, to, spec in self.board._gen_piece_moves(piece, attacks_only=False):
            b2 = self.board.copy()
            _ = b2._apply_move_internal(frm, to, spec)
            if not b2.in_check(piece.color):
                moves.append((piece, to, spec))
        return moves

    def _find_piece_by_id(self, pid: str) -> Optional[Piece]:
        for p in self.board.pieces:
            if p.id == pid and p.alive:
                return p
        return None

    def _log_move(self, meta: Dict[str, object], forced: bool = False, reactive: bool = False) -> None:
        tag = "FORCED" if forced else ("REACT" if reactive else "MOVE")
        moved_id = meta.get("moved_id", "?")
        piece = meta.get("moved_kind", "?")
        from_sq = sq_to_str(meta["from"]) if meta.get("from") else "?"
        to_sq = sq_to_str(meta["to"]) if meta.get("to") else "?"
        capture = meta.get("capture_id")
        castle = meta.get("castle_rook_to") is not None
        # Derive mover from moved_id (robust for reactive where to_move was restored)
        side_just_moved = "W" if moved_id.startswith("W_") else "B"
        idx = len(self.move_log) + 1
        ent_cp = self._entanglement_counterpart_for(moved_id)
        w_in_check = self.board.in_check("W")
        b_in_check = self.board.in_check("B")
        base = f"{idx:04d} {side_just_moved} {tag}: {piece} {from_sq}->{to_sq}"
        if capture:
            base += f" x {capture}"
        if castle:
            rf = sq_to_str(meta["castle_rook_from"])  # type: ignore
            rt = sq_to_str(meta["castle_rook_to"])  # type: ignore
            base += f" (castle rook {rf}->{rt})"
        if ent_cp:
            base += f" | ent↔ {ent_cp}"
        base += f" | check W:{int(w_in_check)} B:{int(b_in_check)}"
        # Append entanglement changes
        ent_hash = self._ent_hash()
        if self._last_ent_hash is None:
            ent_change = "ent_map:init"
        elif ent_hash != self._last_ent_hash:
            ent_change = "ent_map:changed"
        else:
            ent_change = "ent_map:same"
        self._last_ent_hash = ent_hash

        # Per-move evaluation snapshot for side just moved
        eval_score = self._evaluate(side_just_moved)
        base_full = f"{base} | {ent_change} | eval({side_just_moved})={eval_score}"

        # Repetition count
        key = self.board.to_fen() + "|" + ent_hash
        self._state_counts[key] = self._state_counts.get(key, 0) + 1
        rep = self._state_counts[key]
        base_full += f" | rep={rep}"

        self.move_log.append(base_full)
        if self.live:
            print(base_full)
            if self.live_details:
                print(f"FEN: {self.board.to_fen()}")

    def _log_pgn_skeleton(self, meta: Dict[str, object], forced: bool = False, reactive: bool = False) -> None:
        # Minimal PGN-like token for inspection (not full SAN)
        piece = str(meta.get("moved_kind", "?"))
        from_sq = sq_to_str(meta["from"]) if meta.get("from") else "?"
        to_sq = sq_to_str(meta["to"]) if meta.get("to") else "?"
        token = f"{piece}:{from_sq}-{to_sq}"
        if meta.get("capture_id"):
            token += "x"
        if meta.get("castle_rook_to") is not None:
            token = "O-O" if to_sq in ("g1", "g8") else "O-O-O"
        if meta.get("promotion"):
            token += f"={meta.get('promotion')}"
        if forced:
            token = f"[{token}]"
        if reactive:
            token = f"<{token}>"
        self.pgn_moves.append(token)

    def print_summary(self) -> None:
        print("Entanglement (W pawns -> B non-king):")
        for wp, bp in self.ent.W_pawn_to_black.items():
            print(f"  {wp} ↔ {bp}")
        print("Entanglement (B pawns -> W non-king):")
        for bp, wp in self.ent.B_pawn_to_white.items():
            print(f"  {bp} ↔ {wp}")
        print("Moves:")
        for i, m in enumerate(self.move_log[:200], 1):
            print(f"  {i:03d}: {m}")
        if len(self.move_log) > 200:
            print(f"  ... ({len(self.move_log)-200} more)")

    def _record_transcript_entry(self, kind: str, meta: Dict[str, object]) -> None:
        entry = {
            "kind": kind,
            "moved_id": meta.get("moved_id"),
            "side": opposite(self.board.to_move),
            "from": sq_to_str(meta["from"]) if meta.get("from") else None,
            "to": sq_to_str(meta["to"]) if meta.get("to") else None,
            "capture_id": meta.get("capture_id"),
            "castle_rook_from": sq_to_str(meta["castle_rook_from"]) if meta.get("castle_rook_from") else None,
            "castle_rook_to": sq_to_str(meta["castle_rook_to"]) if meta.get("castle_rook_to") else None,
            "fen": self.board.to_fen(),
            "check_W": int(self.board.in_check("W")),
            "check_B": int(self.board.in_check("B")),
            "ent_counterpart": self._entanglement_counterpart_for(meta.get("moved_id", "")),
            "ent_map": {
                "W": self.ent.W_pawn_to_black,
                "B": self.ent.B_pawn_to_white,
            },
            "eval": self._evaluate(opposite(self.board.to_move)),
            "rep": self._state_counts.get(self.board.to_fen() + "|" + self._ent_hash(), 1),
        }
        self.transcript.append(entry)

    def _entanglement_counterpart_for(self, moved_id: str) -> Optional[str]:
        if not moved_id:
            return None
        if moved_id in self.ent.W_pawn_to_black:
            return self.ent.W_pawn_to_black[moved_id]
        if moved_id in self.ent.B_pawn_to_white:
            return self.ent.B_pawn_to_white[moved_id]
        for pw, b in self.ent.W_pawn_to_black.items():
            if b == moved_id:
                return pw
        for pb, w in self.ent.B_pawn_to_white.items():
            if w == moved_id:
                return pb
        return None

    def _ent_hash(self) -> str:
        import hashlib
        w = sorted(self.ent.W_pawn_to_black.items())
        b = sorted(self.ent.B_pawn_to_white.items())
        raw = json.dumps({"W": w, "B": b})
        return hashlib.md5(raw.encode()).hexdigest()

    def get_entanglement_hash(self) -> str:
        """Get current entanglement hash for logging"""
        return self._ent_hash()

    def get_changes_log(self) -> str:
        """Get entanglement changes log for this turn"""
        if self._last_ent_hash is None:
            return "ent_map:init"
        current_hash = self._ent_hash()
        if current_hash != self._last_ent_hash:
            return "ent_map:changed"
        else:
            return "ent_map:same"

    def get_full_entanglement_map(self) -> Dict[str, Any]:
        """Get complete entanglement mapping for logging"""
        return {
            "W_pawn_to_black": dict(self.ent.W_pawn_to_black),
            "B_pawn_to_white": dict(self.ent.B_pawn_to_white),
            "white_free_pawn": self.ent.white_free_pawn,
            "black_free_pawn": self.ent.black_free_pawn
        }

    def get_free_pawn(self, color: str) -> Optional[str]:
        """Get the free pawn for a given color"""
        if color == "W":
            return self.ent.white_free_pawn
        elif color == "B":
            return self.ent.black_free_pawn
        return None

    def randomize_entanglement_map(self) -> None:
        """Randomize the entanglement mapping"""
        self.ent._init_random_dual_mapping(self.board)

    def render_board(self) -> str:
        def sym(p: Optional[Piece]) -> str:
            if p is None:
                return "."
            c = p.kind
            return c.lower() if p.color == "B" else c
        rows = []
        for r in range(7, -1, -1):
            row = " ".join(sym(self.board.board[r][f]) for f in range(8))
            rows.append(f"{RANKS[r]} {row}")
        footer = "  " + " ".join(FILES)
        return "\n".join(rows + [footer])


def main() -> None:
    # CLI overrides env for reproducibility and outputs
    parser = argparse.ArgumentParser(description="QEC terminal simulator")
    parser.add_argument("--games", type=int, default=int(os.getenv("QEC_GAMES", "1")))
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--verbose", action="store_true", default=(os.getenv("QEC_VERBOSE", "0") == "1"))
    parser.add_argument("--policy", type=str, default=os.getenv("QEC_POLICY", "random"), choices=["random", "heuristic", "minimax"])
    parser.add_argument("--map_file", type=str, default=None, help="Path to JSON mapping file (overrides QEC_MAP)")
    parser.add_argument("--out_dir", type=str, default="out")
    parser.add_argument("--depth", type=int, default=2, help="Minimax depth (policy=minimax)")
    parser.add_argument("--ui", action="store_true", help="Run with Pygame UI (visualize one game)")
    parser.add_argument("--fps", type=int, default=2, help="UI frames per second (moves per second)")
    parser.add_argument("--live", action="store_true", help="Print moves live to console")
    args = parser.parse_args()

    if args.map_file and os.path.exists(args.map_file):
        os.environ["QEC_MAP"] = open(args.map_file, "r", encoding="utf-8").read()
    os.environ["QEC_POLICY"] = args.policy
    os.environ["QEC_LIVE"] = "1" if args.live else "0"

    os.makedirs(args.out_dir, exist_ok=True)

    # UI mode: visualize a single game step-by-step if pygame available
    if args.ui:
        try:
            import pygame  # type: ignore
        except Exception as e:
            print("Pygame not installed. Install with: pip install pygame")
            return
        seed = None if args.seed is None else int(args.seed)
        game = Game(seed=seed)
        game.policy = args.policy
        _run_ui(game, fps=args.fps, out_dir=args.out_dir)
        return

    results: Dict[str, int] = {"W": 0, "B": 0, "draw": 0}
    for i in range(args.games):
        seed = None if args.seed is None else (int(args.seed) + i)
        game = Game(seed=seed)
        game.policy = args.policy
        result = game.run()
        print(f"Game {i+1}: {result}")
        if args.verbose:
            print(game.render_board())
            game.print_summary()
        # Write logs
        with open(os.path.join(args.out_dir, f"game_{i+1}.log"), "w", encoding="utf-8") as f:
            f.write("\n".join(game.move_log))
        with open(os.path.join(args.out_dir, f"game_{i+1}.pgn"), "w", encoding="utf-8") as f:
            f.write(" ".join(game.pgn_moves))
        with open(os.path.join(args.out_dir, f"game_{i+1}.jsonl"), "w", encoding="utf-8") as f:
            for rec in game.transcript:
                f.write(json.dumps(rec) + "\n")
        if result.startswith("Checkmate: W"):
            results["W"] += 1
        elif result.startswith("Checkmate: B"):
            results["B"] += 1
        else:
            results["draw"] += 1
    if args.games > 1:
        print(f"Summary over {args.games} games: W {results['W']} | B {results['B']} | draw {results['draw']}")
        with open(os.path.join(args.out_dir, "summary.csv"), "w", encoding="utf-8") as f:
            f.write("games,W,B,draw\n")
            f.write(f"{args.games},{results['W']},{results['B']},{results['draw']}\n")


def _run_ui(game: Game, fps: int, out_dir: str) -> None:
    import pygame  # type: ignore
    pygame.init()
    tile = 72
    margin = 40
    w = h = tile * 8
    screen = pygame.display.set_mode((w, h))
    pygame.display.set_caption("QEC Prototype")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 28, bold=True)

    def draw_board():
        colors = [(240, 217, 181), (181, 136, 99)]
        for r in range(8):
            for f in range(8):
                rect = pygame.Rect(f * tile, (7 - r) * tile, tile, tile)
                pygame.draw.rect(screen, colors[(r + f) % 2], rect)
        # Draw pieces
        for p in game.board.pieces:
            if not p.alive:
                continue
            f, r = p.pos
            ch = p.kind
            txt = font.render(ch if p.color == "W" else ch.lower(), True, (20, 20, 20))
            screen.blit(txt, (f * tile + tile // 3, (7 - r) * tile + tile // 4))

    running = True
    finished = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if not finished:
            res = game._play_turn()
            if res is not None:
                finished = True
                print(res)
                # Save logs
                os.makedirs(out_dir, exist_ok=True)
                with open(os.path.join(out_dir, "ui_game.log"), "w", encoding="utf-8") as f:
                    f.write("\n".join(game.move_log))
                with open(os.path.join(out_dir, "ui_game.pgn"), "w", encoding="utf-8") as f:
                    f.write(" ".join(game.pgn_moves))
        screen.fill((0, 0, 0))
        draw_board()
        pygame.display.flip()
        clock.tick(max(1, fps))
    pygame.quit()


if __name__ == "__main__":
    main()


