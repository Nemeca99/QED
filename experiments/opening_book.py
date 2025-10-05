"""
Opening Book for QEC Human Simulation
Based on real chess openings and historical game patterns
"""

import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class OpeningMove:
    move: str
    frequency: float  # How often this move is played
    win_rate: float   # Win rate for this move
    style_preference: List[str]  # Which player styles prefer this move

@dataclass
class Opening:
    name: str
    moves: List[OpeningMove]
    popularity: float  # How popular this opening is
    style_preference: List[str]  # Which player styles prefer this opening
    complexity: str  # "simple", "moderate", "complex"
    aggression_level: float  # 0.0 (passive) to 1.0 (aggressive)

# Real chess openings with authentic patterns
OPENINGS = {
    "1.e4": {
        "name": "King's Pawn Opening",
        "moves": [
            OpeningMove("1.e4", 1.0, 0.52, ["tactical", "aggressive"]),
            OpeningMove("1.e4 e5", 0.8, 0.51, ["classical", "positional"]),
            OpeningMove("1.e4 c5", 0.6, 0.49, ["tactical", "sharp"]),
            OpeningMove("1.e4 e6", 0.3, 0.48, ["positional", "defensive"]),
            OpeningMove("1.e4 c6", 0.2, 0.47, ["positional", "solid"])
        ],
        "popularity": 0.4,
        "style_preference": ["tactical", "aggressive"],
        "complexity": "moderate",
        "aggression_level": 0.7
    },
    
    "1.d4": {
        "name": "Queen's Pawn Opening",
        "moves": [
            OpeningMove("1.d4", 1.0, 0.53, ["positional", "strategic"]),
            OpeningMove("1.d4 d5", 0.7, 0.52, ["positional", "classical"]),
            OpeningMove("1.d4 Nf6", 0.6, 0.51, ["positional", "flexible"]),
            OpeningMove("1.d4 d5 c4", 0.5, 0.54, ["positional", "strategic"]),
            OpeningMove("1.d4 Nf6 c4", 0.4, 0.53, ["positional", "flexible"])
        ],
        "popularity": 0.35,
        "style_preference": ["positional", "strategic"],
        "complexity": "moderate",
        "aggression_level": 0.4
    },
    
    "1.Nf3": {
        "name": "Reti Opening",
        "moves": [
            OpeningMove("1.Nf3", 1.0, 0.52, ["positional", "flexible"]),
            OpeningMove("1.Nf3 d5", 0.6, 0.51, ["positional", "flexible"]),
            OpeningMove("1.Nf3 Nf6", 0.5, 0.52, ["positional", "flexible"]),
            OpeningMove("1.Nf3 d5 c4", 0.4, 0.53, ["positional", "strategic"])
        ],
        "popularity": 0.15,
        "style_preference": ["positional", "flexible"],
        "complexity": "moderate",
        "aggression_level": 0.3
    },
    
    "1.c4": {
        "name": "English Opening",
        "moves": [
            OpeningMove("1.c4", 1.0, 0.52, ["positional", "strategic"]),
            OpeningMove("1.c4 e5", 0.5, 0.51, ["positional", "strategic"]),
            OpeningMove("1.c4 c5", 0.4, 0.52, ["positional", "strategic"]),
            OpeningMove("1.c4 Nf6", 0.3, 0.51, ["positional", "flexible"])
        ],
        "popularity": 0.1,
        "style_preference": ["positional", "strategic"],
        "complexity": "moderate",
        "aggression_level": 0.2
    }
}

# Specific opening variations
OPENING_VARIATIONS = {
    "Sicilian Defense": {
        "moves": ["1.e4 c5", "2.Nf3 d6", "3.d4 cxd4", "4.Nxd4 Nf6"],
        "style_preference": ["tactical", "sharp"],
        "complexity": "complex",
        "aggression_level": 0.8
    },
    
    "King's Indian Defense": {
        "moves": ["1.d4 Nf6", "2.c4 g6", "3.Nc3 Bg7"],
        "style_preference": ["tactical", "aggressive"],
        "complexity": "complex",
        "aggression_level": 0.7
    },
    
    "Queen's Gambit": {
        "moves": ["1.d4 d5", "2.c4 e6", "3.Nc3 Nf6"],
        "style_preference": ["positional", "strategic"],
        "complexity": "moderate",
        "aggression_level": 0.4
    },
    
    "Catalan Opening": {
        "moves": ["1.d4 Nf6", "2.c4 e6", "3.g3 d5", "4.Bg2"],
        "style_preference": ["positional", "strategic"],
        "complexity": "moderate",
        "aggression_level": 0.3
    },
    
    "Nimzo-Indian Defense": {
        "moves": ["1.d4 Nf6", "2.c4 e6", "3.Nc3 Bb4"],
        "style_preference": ["positional", "strategic"],
        "complexity": "moderate",
        "aggression_level": 0.4
    },
    
    "Grunfeld Defense": {
        "moves": ["1.d4 Nf6", "2.c4 g6", "3.Nc3 d5"],
        "style_preference": ["tactical", "aggressive"],
        "complexity": "complex",
        "aggression_level": 0.6
    },
    
    "Benoni Defense": {
        "moves": ["1.d4 Nf6", "2.c4 c5", "3.d5 e6"],
        "style_preference": ["tactical", "aggressive"],
        "complexity": "complex",
        "aggression_level": 0.7
    }
}

def get_opening_by_style(player_style: str) -> str:
    """Get opening based on player style preference"""
    style_openings = {
        "tactical": ["1.e4", "Sicilian Defense", "King's Indian Defense", "Grunfeld Defense"],
        "positional": ["1.d4", "Queen's Gambit", "Catalan Opening", "Nimzo-Indian Defense"],
        "aggressive": ["1.e4", "Sicilian Defense", "King's Indian Defense", "Benoni Defense"],
        "defensive": ["1.d4", "Queen's Gambit", "Catalan Opening", "Nimzo-Indian Defense"],
        "classical": ["1.e4", "1.d4", "Queen's Gambit", "Catalan Opening"],
        "modern": ["1.e4", "Sicilian Defense", "King's Indian Defense", "Grunfeld Defense"]
    }
    
    if player_style in style_openings:
        return random.choice(style_openings[player_style])
    else:
        return random.choice(list(OPENINGS.keys()))

def get_opening_complexity(opening_name: str) -> str:
    """Get opening complexity level"""
    if opening_name in OPENING_VARIATIONS:
        return OPENING_VARIATIONS[opening_name]["complexity"]
    elif opening_name in OPENINGS:
        return OPENINGS[opening_name]["complexity"]
    else:
        return "moderate"

def get_opening_aggression(opening_name: str) -> float:
    """Get opening aggression level"""
    if opening_name in OPENING_VARIATIONS:
        return OPENING_VARIATIONS[opening_name]["aggression_level"]
    elif opening_name in OPENINGS:
        return OPENINGS[opening_name]["aggression_level"]
    else:
        return 0.5

def get_opening_moves(opening_name: str, num_moves: int = 4) -> List[str]:
    """Get opening moves for a specific opening"""
    if opening_name in OPENING_VARIATIONS:
        return OPENING_VARIATIONS[opening_name]["moves"][:num_moves]
    elif opening_name in OPENINGS:
        moves = []
        for move_obj in OPENINGS[opening_name]["moves"][:num_moves]:
            moves.append(move_obj.move)
        return moves
    else:
        return []

def get_opening_popularity(opening_name: str) -> float:
    """Get opening popularity"""
    if opening_name in OPENINGS:
        return OPENINGS[opening_name]["popularity"]
    else:
        return 0.1

def get_opening_style_preference(opening_name: str) -> List[str]:
    """Get opening style preference"""
    if opening_name in OPENING_VARIATIONS:
        return OPENING_VARIATIONS[opening_name]["style_preference"]
    elif opening_name in OPENINGS:
        return OPENINGS[opening_name]["style_preference"]
    else:
        return ["positional"]

def get_opening_win_rate(opening_name: str) -> float:
    """Get opening win rate"""
    if opening_name in OPENINGS:
        # Return average win rate for the opening
        moves = OPENINGS[opening_name]["moves"]
        if moves:
            return sum(move.win_rate for move in moves) / len(moves)
    return 0.5

def get_opening_frequency(opening_name: str) -> float:
    """Get opening frequency"""
    if opening_name in OPENINGS:
        return OPENINGS[opening_name]["popularity"]
    else:
        return 0.1

def get_opening_by_rating(rating: int) -> str:
    """Get opening based on player rating"""
    if rating >= 2700:
        # Super GMs - prefer complex, theoretical openings
        complex_openings = ["Sicilian Defense", "King's Indian Defense", "Grunfeld Defense", "Benoni Defense"]
        return random.choice(complex_openings)
    elif rating >= 2500:
        # GMs - prefer balanced openings
        balanced_openings = ["1.e4", "1.d4", "Queen's Gambit", "Catalan Opening", "Nimzo-Indian Defense"]
        return random.choice(balanced_openings)
    elif rating >= 2300:
        # IMs - prefer solid, well-known openings
        solid_openings = ["1.e4", "1.d4", "Queen's Gambit", "Catalan Opening"]
        return random.choice(solid_openings)
    else:
        # Lower rated - prefer simple, safe openings
        simple_openings = ["1.e4", "1.d4", "Queen's Gambit"]
        return random.choice(simple_openings)

def get_opening_by_time_control(time_control: str) -> str:
    """Get opening based on time control"""
    if time_control == "blitz":
        # Blitz players prefer sharp, tactical openings
        blitz_openings = ["1.e4", "Sicilian Defense", "King's Indian Defense", "Grunfeld Defense"]
        return random.choice(blitz_openings)
    elif time_control == "classical":
        # Classical players prefer positional, strategic openings
        classical_openings = ["1.d4", "Queen's Gambit", "Catalan Opening", "Nimzo-Indian Defense"]
        return random.choice(classical_openings)
    else:
        # Default to balanced openings
        balanced_openings = ["1.e4", "1.d4", "Queen's Gambit", "Catalan Opening"]
        return random.choice(balanced_openings)

def get_opening_by_game_phase(game_phase: str) -> str:
    """Get opening based on game phase"""
    if game_phase == "opening":
        # Return actual opening
        return random.choice(list(OPENINGS.keys()))
    elif game_phase == "middlegame":
        # Return middlegame patterns
        return "middlegame_pattern"
    elif game_phase == "endgame":
        # Return endgame patterns
        return "endgame_pattern"
    else:
        return "unknown"

def get_opening_by_opponent_style(opponent_style: str) -> str:
    """Get opening based on opponent's style"""
    if opponent_style == "tactical":
        # Against tactical players, prefer positional openings
        positional_openings = ["1.d4", "Queen's Gambit", "Catalan Opening", "Nimzo-Indian Defense"]
        return random.choice(positional_openings)
    elif opponent_style == "positional":
        # Against positional players, prefer tactical openings
        tactical_openings = ["1.e4", "Sicilian Defense", "King's Indian Defense", "Grunfeld Defense"]
        return random.choice(tactical_openings)
    else:
        # Default to balanced openings
        balanced_openings = ["1.e4", "1.d4", "Queen's Gambit", "Catalan Opening"]
        return random.choice(balanced_openings)

def get_opening_by_rating_difference(rating_diff: int) -> str:
    """Get opening based on rating difference"""
    if rating_diff > 200:
        # Much stronger opponent - prefer solid, safe openings
        safe_openings = ["1.d4", "Queen's Gambit", "Catalan Opening", "Nimzo-Indian Defense"]
        return random.choice(safe_openings)
    elif rating_diff < -200:
        # Much weaker opponent - prefer aggressive, tactical openings
        aggressive_openings = ["1.e4", "Sicilian Defense", "King's Indian Defense", "Grunfeld Defense"]
        return random.choice(aggressive_openings)
    else:
        # Similar strength - prefer balanced openings
        balanced_openings = ["1.e4", "1.d4", "Queen's Gambit", "Catalan Opening"]
        return random.choice(balanced_openings)

def get_opening_by_tournament_importance(importance: str) -> str:
    """Get opening based on tournament importance"""
    if importance == "high":
        # Important games - prefer well-prepared, solid openings
        solid_openings = ["1.d4", "Queen's Gambit", "Catalan Opening", "Nimzo-Indian Defense"]
        return random.choice(solid_openings)
    elif importance == "low":
        # Less important games - prefer experimental, creative openings
        creative_openings = ["1.e4", "Sicilian Defense", "King's Indian Defense", "Grunfeld Defense"]
        return random.choice(creative_openings)
    else:
        # Normal games - prefer balanced openings
        balanced_openings = ["1.e4", "1.d4", "Queen's Gambit", "Catalan Opening"]
        return random.choice(balanced_openings)

if __name__ == "__main__":
    # Test the opening book
    print("=== QEC Opening Book ===")
    
    # Test style-based opening selection
    styles = ["tactical", "positional", "aggressive", "defensive", "classical", "modern"]
    for style in styles:
        opening = get_opening_by_style(style)
        print(f"{style:12} -> {opening}")
    
    # Test rating-based opening selection
    ratings = [2200, 2400, 2600, 2800]
    for rating in ratings:
        opening = get_opening_by_rating(rating)
        print(f"Rating {rating} -> {opening}")
    
    # Test time control-based opening selection
    time_controls = ["blitz", "classical"]
    for tc in time_controls:
        opening = get_opening_by_time_control(tc)
        print(f"{tc:12} -> {opening}")
    
    # Test opening properties
    test_openings = ["1.e4", "1.d4", "Sicilian Defense", "Queen's Gambit"]
    for opening in test_openings:
        complexity = get_opening_complexity(opening)
        aggression = get_opening_aggression(opening)
        popularity = get_opening_popularity(opening)
        print(f"{opening:20} | {complexity:8} | {aggression:.2f} | {popularity:.2f}")
