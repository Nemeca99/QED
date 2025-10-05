"""
Chess Player Database - Real player profiles for human-like simulation
Based on actual chess players with realistic skill ratings and playing styles
"""

import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class PlayerStyle(Enum):
    TACTICAL = "tactical"      # Aggressive, sharp, tactical
    POSITIONAL = "positional"  # Strategic, patient, positional
    ENDGAME = "endgame"        # Strong in endgames, technical
    OPENING = "opening"        # Deep opening knowledge
    BLITZ = "blitz"           # Fast time controls, intuitive
    CLASSICAL = "classical"    # Long time controls, deep calculation

@dataclass
class ChessPlayer:
    name: str
    rating: int
    style: PlayerStyle
    strengths: List[str]
    weaknesses: List[str]
    opening_preferences: List[str]
    time_control_preference: str
    aggression_level: float  # 0.0 (passive) to 1.0 (very aggressive)
    calculation_depth: int   # How deep they typically calculate
    blunder_rate: float     # Probability of major blunders
    tactical_vision: float   # Ability to spot tactics (0.0-1.0)
    endgame_strength: float  # Endgame skill (0.0-1.0)
    opening_knowledge: float # Opening theory knowledge (0.0-1.0)

# Real chess players with authentic profiles
CHESS_PLAYERS = [
    # Super Grandmasters (2800+)
    ChessPlayer(
        name="Magnus Carlsen",
        rating=2850,
        style=PlayerStyle.POSITIONAL,
        strengths=["endgame", "positional understanding", "practical play", "time management"],
        weaknesses=["opening theory", "sharp tactical lines"],
        opening_preferences=["1.e4", "1.d4", "English Opening", "Queen's Gambit"],
        time_control_preference="classical",
        aggression_level=0.4,
        calculation_depth=8,
        blunder_rate=0.02,
        tactical_vision=0.9,
        endgame_strength=0.98,
        opening_knowledge=0.85
    ),
    
    ChessPlayer(
        name="Fabiano Caruana",
        rating=2820,
        style=PlayerStyle.TACTICAL,
        strengths=["opening theory", "tactical vision", "calculation", "preparation"],
        weaknesses=["time pressure", "endgame technique"],
        opening_preferences=["Sicilian Defense", "King's Indian", "Nimzo-Indian"],
        time_control_preference="classical",
        aggression_level=0.7,
        calculation_depth=9,
        blunder_rate=0.03,
        tactical_vision=0.95,
        endgame_strength=0.88,
        opening_knowledge=0.95
    ),
    
    ChessPlayer(
        name="Ding Liren",
        rating=2800,
        style=PlayerStyle.POSITIONAL,
        strengths=["positional play", "endgame", "defensive skills", "patience"],
        weaknesses=["aggressive openings", "time pressure"],
        opening_preferences=["Queen's Gambit", "Catalan", "English Opening"],
        time_control_preference="classical",
        aggression_level=0.3,
        calculation_depth=7,
        blunder_rate=0.025,
        tactical_vision=0.85,
        endgame_strength=0.92,
        opening_knowledge=0.88
    ),
    
    # Top Grandmasters (2700-2799)
    ChessPlayer(
        name="Ian Nepomniachtchi",
        rating=2750,
        style=PlayerStyle.TACTICAL,
        strengths=["tactical vision", "aggressive play", "opening preparation", "creativity"],
        weaknesses=["endgame technique", "defensive positions"],
        opening_preferences=["Sicilian Defense", "King's Indian", "Grunfeld"],
        time_control_preference="classical",
        aggression_level=0.8,
        calculation_depth=8,
        blunder_rate=0.04,
        tactical_vision=0.92,
        endgame_strength=0.82,
        opening_knowledge=0.90
    ),
    
    ChessPlayer(
        name="Hikaru Nakamura",
        rating=2720,
        style=PlayerStyle.BLITZ,
        strengths=["blitz play", "tactical vision", "time management", "online play"],
        weaknesses=["classical preparation", "endgame technique"],
        opening_preferences=["1.e4", "Sicilian Defense", "King's Indian"],
        time_control_preference="blitz",
        aggression_level=0.75,
        calculation_depth=6,
        blunder_rate=0.05,
        tactical_vision=0.90,
        endgame_strength=0.80,
        opening_knowledge=0.75
    ),
    
    ChessPlayer(
        name="Wesley So",
        rating=2700,
        style=PlayerStyle.POSITIONAL,
        strengths=["positional understanding", "endgame", "defensive play", "consistency"],
        weaknesses=["aggressive openings", "tactical complications"],
        opening_preferences=["Queen's Gambit", "Catalan", "English Opening"],
        time_control_preference="classical",
        aggression_level=0.35,
        calculation_depth=7,
        blunder_rate=0.03,
        tactical_vision=0.82,
        endgame_strength=0.90,
        opening_knowledge=0.85
    ),
    
    # Strong Grandmasters (2600-2699)
    ChessPlayer(
        name="Levon Aronian",
        rating=2680,
        style=PlayerStyle.TACTICAL,
        strengths=["creativity", "tactical vision", "opening preparation", "artistic play"],
        weaknesses=["consistency", "time pressure"],
        opening_preferences=["King's Indian", "Grunfeld", "Benoni"],
        time_control_preference="classical",
        aggression_level=0.7,
        calculation_depth=8,
        blunder_rate=0.045,
        tactical_vision=0.88,
        endgame_strength=0.85,
        opening_knowledge=0.90
    ),
    
    ChessPlayer(
        name="Anish Giri",
        rating=2650,
        style=PlayerStyle.POSITIONAL,
        strengths=["positional understanding", "opening theory", "defensive skills", "preparation"],
        weaknesses=["aggressive play", "tactical complications"],
        opening_preferences=["Queen's Gambit", "Catalan", "Nimzo-Indian"],
        time_control_preference="classical",
        aggression_level=0.4,
        calculation_depth=8,
        blunder_rate=0.035,
        tactical_vision=0.85,
        endgame_strength=0.88,
        opening_knowledge=0.92
    ),
    
    ChessPlayer(
        name="Maxime Vachier-Lagrave",
        rating=2620,
        style=PlayerStyle.TACTICAL,
        strengths=["tactical vision", "calculation", "aggressive play", "opening preparation"],
        weaknesses=["endgame technique", "defensive positions"],
        opening_preferences=["Sicilian Defense", "King's Indian", "Grunfeld"],
        time_control_preference="classical",
        aggression_level=0.75,
        calculation_depth=9,
        blunder_rate=0.04,
        tactical_vision=0.93,
        endgame_strength=0.82,
        opening_knowledge=0.88
    ),
    
    # International Masters (2400-2599)
    ChessPlayer(
        name="Alexander Grischuk",
        rating=2580,
        style=PlayerStyle.BLITZ,
        strengths=["blitz play", "tactical vision", "time management", "practical play"],
        weaknesses=["classical preparation", "opening theory"],
        opening_preferences=["1.e4", "Sicilian Defense", "King's Indian"],
        time_control_preference="blitz",
        aggression_level=0.6,
        calculation_depth=6,
        blunder_rate=0.06,
        tactical_vision=0.88,
        endgame_strength=0.78,
        opening_knowledge=0.70
    ),
    
    ChessPlayer(
        name="Vladimir Kramnik",
        rating=2550,
        style=PlayerStyle.POSITIONAL,
        strengths=["positional understanding", "endgame", "defensive play", "classical approach"],
        weaknesses=["aggressive openings", "modern theory"],
        opening_preferences=["Queen's Gambit", "Catalan", "English Opening"],
        time_control_preference="classical",
        aggression_level=0.3,
        calculation_depth=8,
        blunder_rate=0.04,
        tactical_vision=0.82,
        endgame_strength=0.92,
        opening_knowledge=0.85
    ),
    
    ChessPlayer(
        name="Viswanathan Anand",
        rating=2520,
        style=PlayerStyle.CLASSICAL,
        strengths=["classical play", "endgame", "positional understanding", "experience"],
        weaknesses=["modern theory", "aggressive openings"],
        opening_preferences=["Queen's Gambit", "Catalan", "English Opening"],
        time_control_preference="classical",
        aggression_level=0.4,
        calculation_depth=7,
        blunder_rate=0.05,
        tactical_vision=0.80,
        endgame_strength=0.90,
        opening_knowledge=0.80
    ),
    
    # Strong Masters (2200-2399)
    ChessPlayer(
        name="Eric Hansen",
        rating=2350,
        style=PlayerStyle.BLITZ,
        strengths=["blitz play", "tactical vision", "online play", "entertainment"],
        weaknesses=["classical preparation", "endgame technique"],
        opening_preferences=["1.e4", "Sicilian Defense", "King's Indian"],
        time_control_preference="blitz",
        aggression_level=0.8,
        calculation_depth=5,
        blunder_rate=0.08,
        tactical_vision=0.85,
        endgame_strength=0.70,
        opening_knowledge=0.65
    ),
    
    ChessPlayer(
        name="John Bartholomew",
        rating=2300,
        style=PlayerStyle.POSITIONAL,
        strengths=["positional understanding", "teaching", "endgame", "defensive play"],
        weaknesses=["aggressive play", "tactical complications"],
        opening_preferences=["Queen's Gambit", "Catalan", "English Opening"],
        time_control_preference="classical",
        aggression_level=0.35,
        calculation_depth=6,
        blunder_rate=0.07,
        tactical_vision=0.75,
        endgame_strength=0.85,
        opening_knowledge=0.80
    ),
    
    ChessPlayer(
        name="GothamChess",
        rating=2250,
        style=PlayerStyle.TACTICAL,
        strengths=["tactical vision", "teaching", "entertainment", "online play"],
        weaknesses=["classical preparation", "endgame technique"],
        opening_preferences=["1.e4", "Sicilian Defense", "King's Indian"],
        time_control_preference="blitz",
        aggression_level=0.7,
        calculation_depth=5,
        blunder_rate=0.09,
        tactical_vision=0.80,
        endgame_strength=0.65,
        opening_knowledge=0.60
    )
]

def get_player_by_name(name: str) -> Optional[ChessPlayer]:
    """Get a player by name"""
    for player in CHESS_PLAYERS:
        if player.name.lower() == name.lower():
            return player
    return None

def get_players_by_rating_range(min_rating: int, max_rating: int) -> List[ChessPlayer]:
    """Get players within a rating range"""
    return [p for p in CHESS_PLAYERS if min_rating <= p.rating <= max_rating]

def get_players_by_style(style: PlayerStyle) -> List[ChessPlayer]:
    """Get players by playing style"""
    return [p for p in CHESS_PLAYERS if p.style == style]

def get_random_player_pool(size: int, min_rating: int = 2200, max_rating: int = 2850) -> List[ChessPlayer]:
    """Get a random pool of players within rating range"""
    eligible = get_players_by_rating_range(min_rating, max_rating)
    return random.sample(eligible, min(size, len(eligible)))

def get_tournament_pools() -> Dict[str, List[ChessPlayer]]:
    """Get pre-defined tournament pools"""
    return {
        "super_gm": get_players_by_rating_range(2800, 2850),
        "top_gm": get_players_by_rating_range(2700, 2799),
        "strong_gm": get_players_by_rating_range(2600, 2699),
        "im": get_players_by_rating_range(2400, 2599),
        "master": get_players_by_rating_range(2200, 2399),
        "mixed": get_random_player_pool(12, 2200, 2850),
        "tactical": get_players_by_style(PlayerStyle.TACTICAL),
        "positional": get_players_by_style(PlayerStyle.POSITIONAL),
        "blitz": get_players_by_style(PlayerStyle.BLITZ)
    }

def get_player_skill_adjustment(player: ChessPlayer, time_control: str = "classical") -> float:
    """Get skill adjustment based on time control preference"""
    if player.time_control_preference == time_control:
        return 1.0
    elif player.time_control_preference == "blitz" and time_control == "classical":
        return 0.9  # Slightly weaker in classical
    elif player.time_control_preference == "classical" and time_control == "blitz":
        return 0.85  # Weaker in blitz
    else:
        return 0.95  # Slight adjustment for mismatch

def get_player_style_bonus(player: ChessPlayer, game_phase: str) -> float:
    """Get style bonus for different game phases"""
    if game_phase == "opening" and player.style in [PlayerStyle.OPENING, PlayerStyle.TACTICAL]:
        return 1.1
    elif game_phase == "middlegame" and player.style in [PlayerStyle.TACTICAL, PlayerStyle.POSITIONAL]:
        return 1.05
    elif game_phase == "endgame" and player.style in [PlayerStyle.ENDGAME, PlayerStyle.POSITIONAL]:
        return 1.1
    else:
        return 1.0

if __name__ == "__main__":
    # Test the database
    print("=== Chess Player Database ===")
    print(f"Total players: {len(CHESS_PLAYERS)}")
    
    # Show rating distribution
    ratings = [p.rating for p in CHESS_PLAYERS]
    print(f"Rating range: {min(ratings)} - {max(ratings)}")
    
    # Show style distribution
    styles = {}
    for player in CHESS_PLAYERS:
        styles[player.style.value] = styles.get(player.style.value, 0) + 1
    print(f"Style distribution: {styles}")
    
    # Test tournament pools
    pools = get_tournament_pools()
    print(f"\nTournament pools:")
    for name, players in pools.items():
        print(f"  {name}: {len(players)} players")
        if players:
            ratings = [p.rating for p in players]
            print(f"    Rating range: {min(ratings)} - {max(ratings)}")
