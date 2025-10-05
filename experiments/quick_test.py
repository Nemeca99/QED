"""
Quick QEC Test - Focused realistic simulation
Now supports per-game randomized entanglement (hidden), free-pawn announcements,
per-game log saving, and infinite test loop via CLI.
"""

import os
import json
import time
import random
import argparse
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import main
Game = main.Game

def run_quick_test():
    """Run a focused test with realistic settings"""
    
    parser = argparse.ArgumentParser(description="Quick QEC test runner")
    parser.add_argument("--policy_w", type=str, default="heuristic", choices=["random","heuristic","minimax"], help="White policy")
    parser.add_argument("--policy_b", type=str, default="minimax", choices=["random","heuristic","minimax"], help="Black policy")
    parser.add_argument("--games", type=int, default=3, help="Number of games to run (ignored if --infinite)")
    parser.add_argument("--infinite", action="store_true", help="Run games forever until stopped")
    parser.add_argument("--logs_dir", type=str, default="logs", help="Directory to write per-game logs")
    parser.add_argument("--fixed_map", type=str, default=None, help="Path to fixed mapping JSON; if unset, use randomized entanglement per game")
    parser.add_argument("--seed_base", type=int, default=42, help="Base seed for reproducibility")
    parser.add_argument("--live_details", action="store_true", help="Print FEN after each move")
    args = parser.parse_args()

    print("=== QEC Realistic Test ===")
    print("Testing with policies and per-game randomized entanglement")

    results = []
    logs_dir = args.logs_dir
    os.makedirs(logs_dir, exist_ok=True)

    def iterate_games():
        i = 0
        while True:
            i += 1
            yield i, (args.policy_w, args.policy_b)
            if not args.infinite and i >= args.games:
                break

    for i, (policy_w, policy_b) in iterate_games():
        print(f"\n--- Test {i+1}: {policy_w} vs {policy_b} ---")
        
        # Set up deterministic seed per game
        seed = args.seed_base + i
        os.environ["QEC_POLICY"] = policy_w
        # Entanglement: randomized per game unless fixed_map provided
        if args.fixed_map and os.path.exists(args.fixed_map):
            os.environ["QEC_MAP"] = open(args.fixed_map, "r", encoding="utf-8").read()
        else:
            if "QEC_MAP" in os.environ:
                del os.environ["QEC_MAP"]
        # Ensure live move printing from main.py's _log_move
        os.environ["QEC_LIVE"] = "1"
        os.environ["QEC_LIVE_DETAILS"] = "1" if args.live_details else "0"
        # Optional detailed FEN per move
        # os.environ["QEC_LIVE_DETAILS"] = "1"
        
        game = Game(seed=seed)
        game.policy = policy_w
        # Double-ensure live printing even if env missed
        game.live = True

        # Announce free pawns to each player (private knowledge; included here as preface lines)
        w_free = game.ent.white_free_pawn
        b_free = game.ent.black_free_pawn
        announce_w = f"ANNOUNCE W FREE: {w_free}"
        announce_b = f"ANNOUNCE B FREE: {b_free}"
        print(announce_w)
        print(announce_b)
        game.move_log.append(announce_w)
        game.move_log.append(announce_b)
        
        start_time = time.time()
        
        # Play with move limit to prevent infinite loops
        max_moves = 200
        move_count = 0
        
        try:
            for _ in range(max_moves):
                res = game._play_turn()
                move_count += 1
                
                if res is not None:
                    break
                    
                # Check for repetition (simple)
                if len(game.transcript) > 10:
                    recent = game.transcript[-10:]
                    if len(set(str(entry) for entry in recent)) < 5:
                        res = "Draw by repetition"
                        break
                        
        except Exception as e:
            res = f"Error: {str(e)[:50]}"
            
        duration = time.time() - start_time
        
        # Analyze result
        result_info = {
            "test": f"{policy_w} vs {policy_b}",
            "result": res,
            "moves": move_count,
            "duration": f"{duration:.2f}s",
            "forced_moves": sum(1 for entry in game.transcript if entry.get("kind") == "forced"),
            "reactive_moves": sum(1 for entry in game.transcript if entry.get("kind") == "reactive"),
            "captures": sum(1 for entry in game.transcript if entry.get("capture_id")),
            "ent_breaks": sum(1 for entry in game.transcript if "changed" in str(entry.get("ent_map", {})))
        }
        
        results.append(result_info)

        # Persist logs for this game
        base = f"test_{i+1}_{policy_w}_vs_{policy_b}_seed{seed}"
        with open(os.path.join(logs_dir, f"{base}.log"), "w", encoding="utf-8") as f:
            f.write("\n".join(game.move_log))
        with open(os.path.join(logs_dir, f"{base}.pgn"), "w", encoding="utf-8") as f:
            f.write(" ".join(game.pgn_moves))
        # Full transcript (internal)
        with open(os.path.join(logs_dir, f"{base}.jsonl"), "w", encoding="utf-8") as f:
            for rec in game.transcript:
                f.write(json.dumps(rec) + "\n")
        # Public transcript (hide ent_map)
        with open(os.path.join(logs_dir, f"{base}_public.jsonl"), "w", encoding="utf-8") as f:
            for rec in game.transcript:
                pub = dict(rec)
                if "ent_map" in pub:
                    del pub["ent_map"]
                f.write(json.dumps(pub) + "\n")
        print(f"Saved logs: {os.path.join(logs_dir, base)}.[log|pgn|jsonl]")
        
        print(f"Result: {res}")
        print(f"Moves: {move_count} in {duration:.2f}s")
        print(f"Forced: {result_info['forced_moves']}, Reactive: {result_info['reactive_moves']}")
        print(f"Captures: {result_info['captures']}, Ent. breaks: {result_info['ent_breaks']}")
        
        # Show final position
        if move_count < 50:  # Only for shorter games
            print("Final position:")
            print(game.render_board())
    
    # Summary
    print("\n=== SUMMARY ===")
    for result in results:
        result_str = result['result'] if result['result'] else "Draw by move limit"
        print(f"{result['test']:20} | {result_str:20} | {result['moves']:3} moves | {result['duration']}")
    
    # Policy performance
    print("\n=== POLICY ANALYSIS ===")
    policy_stats = {}
    for result in results:
        policy = result['test'].split(' vs ')[0]
        if policy not in policy_stats:
            policy_stats[policy] = {'wins': 0, 'total': 0, 'avg_moves': 0}
        
        policy_stats[policy]['total'] += 1
        result_str = result['result'] if result['result'] else "Draw by move limit"
        if 'wins' in result_str.lower():
            policy_stats[policy]['wins'] += 1
        policy_stats[policy]['avg_moves'] += result['moves']
    
    for policy, stats in policy_stats.items():
        win_rate = stats['wins'] / stats['total'] * 100
        avg_moves = stats['avg_moves'] / stats['total']
        print(f"{policy:12}: {win_rate:5.1f}% win rate, {avg_moves:5.1f} avg moves")

if __name__ == "__main__":
    run_quick_test()
