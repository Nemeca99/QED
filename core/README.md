Quantum Entanglement Chess (QEC)

Overview
- Deterministic variant of chess with a fixed entanglement layer between opposing pieces.
- All classical movement rules remain; QEC adds simultaneous/forced motion and reactive defense.
- Kings are never entangled.

Core differences vs classical chess
- Dual entanglement: seven white pawns are linked one-to-one with black non-king pieces; seven black pawns are linked one-to-one with white non-king pieces. Each side has exactly one free pawn. Links break on capture or promotion and never reform.
- Single forced response: whenever any member of a linked pair physically moves, its counterpart must immediately make exactly one legal move. If no legal move exists, the counterpart stays. The move is chosen by the counterpart’s owner (policy-controlled in the engine).
- Reactive-check: if a move results in check, the checked king immediately attempts one legal one-square move during the same turn; if none exists, it is instant mate.
- Castling: only the rook’s relocation can trigger an entangled response (the king is never linked). At most one forced response occurs per turn.
- Timing (tournament mode): 3 minutes per turn (no overall game clock). Best-of-3 series with dual-king draw = both lose; sudden-death fallback optional.

Rules (concise)
1) Setup: standard 8×8 board and starting position. Choose dual entanglement maps: 7 linked pawns per side, 1 free pawn per side, kings excluded.
2) Turn sequence:
   - Active player makes a legal classical move m.
   - If the moved piece is linked (or a castling rook moved and is linked), the counterpart must make one legal move immediately (chosen by its owner). No second forced move this turn.
   - If the position gives check, the checked side immediately makes one legal one-square king move; if none exists, mate.
   - Switch side to move.
3) Breaking links:
   - Capture of either member or pawn promotion frees both; links never reform.
4) Legality: all moves (base, forced, reactive) must be classical-legal and king-safe. Pinned pieces cannot move illegally.
5) Special moves:
   - Castling: treated as a king move plus rook relocation; only the rook’s relocation can trigger a forced response if that rook is linked.
   - En passant: supported; if a captured pawn was linked, that link is removed exactly once upon resolution; forced steps are evaluated only for the moved piece’s link.
6) Notation (extended): standard SAN/lan augmented with entanglement brackets, e.g. `e2-e4 [↔ h8R:h8-h7]`. In engine logs: MOVE/FORCED/REACT tags plus `ent↔` counterpart.

Mathematical foundation (summary)
- State S_t = (P_t, E_t, τ_t) with piece set, entanglement mapping, and side to move.
- Deterministic transition function T applies base move, optional forced counterpart move, and optional reactive king step.
- State space remains finite; positions are classical-legal; additional edges arise from entanglement relations. Practical upper bound for fixed maps ≈ |S|×(7!)^2.

What the engine implements
- Classical legality including castling, en passant, promotion (auto-queen in prototype).
- Dual entanglement (7 links per side; sample mapping provided in `sample_mapping.json`).
- Single forced response per turn; forced reply chosen by the counterpart’s owner (configurable; default heuristic/minimax supported for primaries; forced reply selection presently random/heuristic depending on setting).
- Reactive-check with immediate one-square king escape.
- Entanglement break on capture/promotion.
- Repetition tracking via (FEN + ent-hash).
- Policies: random, heuristic, minimax(depth 2).
- Optional UI (pygame) for visual runs.

Planned improvements
- Forced reply selection via same policy as the owner (minimax hook).
- Promotion logging/IDs (+Q) and explicit ID update for clarity.
- Reactive-check turn integrity refinements (full turn-state save/restore for counters).
- SAN output and per-move evaluation overlays in UI.

Run
```bash
python main.py
```

Options (env vars)
- QEC_GAMES: number of games (default 1)
- QEC_SEED: base seed for reproducibility (optional)
- QEC_VERBOSE=1: print board and logs
- QEC_POLICY=heuristic: use heuristic move selection (else random)
- QEC_MAP: JSON string to fix entanglement mapping, example:
```json
{
  "W_pawn_to_black": {"W_P_a2": "B_R_a8", "W_P_b2": "B_N_b8"},
  "B_pawn_to_white": {"B_P_a7": "W_R_a1", "B_P_b7": "W_N_b1"},
  "white_free_pawn": "W_P_h2",
  "black_free_pawn": "B_P_h7"
}
```

Example (PowerShell):
```powershell
$env:QEC_GAMES=5; $env:QEC_POLICY=heuristic; python main.py
```

PGN-like output
- `Game X:` line shows the result.
- For debugging, inspect `PGN-like` tokens in verbose mode (forced moves in [brackets], reactive in <angle brackets>).

UI mode (optional)
```powershell
pip install pygame
python main.py --ui --policy heuristic --fps 2
```

Deterministic mapping via file
```powershell
python main.py --map_file sample_mapping.json --verbose
```

Live move stream
```powershell
python main.py --games 1 --policy minimax --depth 2 --map_file sample_mapping.json --live
# Add detailed state per move
$env:QEC_LIVE_DETAILS=1; python main.py --games 1 --live
```

Targeted validation tests (quick manual)
1) Blocked forced: `e2-e3` with `e2↔Bf8` (from sample map) → no forced reply if bishop blocked.
2) Immediate force: `...e7-e5` with `e7↔Bf1` → White bishop must move one legal square.
3) Reactive check: `...Qd8-h4+` triggers `REACT` king step immediately.
4) Castling: only the rook movement can trigger a forced reply; king never triggers.
5) En passant: capture resolves once, breaks captured pawn’s link, no ghost forced steps.

License
- Prototype code and rules draft for research and testing purposes.


