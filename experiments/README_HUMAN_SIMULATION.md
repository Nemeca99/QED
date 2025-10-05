# QEC Human Simulation System

A comprehensive simulation framework for Quantum Entanglement Chess (QEC) that mimics real chess players with authentic skill profiles, playing styles, and error patterns.

## Features

### 🎯 Real Player Profiles
- **15 authentic chess players** with real ratings (2200-2850)
- **6 playing styles**: tactical, positional, endgame, opening, blitz, classical
- **Realistic skill attributes**: blunder rates, tactical vision, endgame strength
- **Time control preferences**: classical vs blitz players

### 🏆 Tournament System
- **Round Robin**: All players face each other
- **Swiss System**: Pair players by score
- **Knockout**: Single elimination brackets
- **World Championship**: Head-to-head matches
- **Player Pools**: Pre-defined groups by rating/style

### 🧠 Human-like AI
- **Skill-based move selection** with realistic error patterns
- **Time pressure effects** that increase blunder rates
- **Style bonuses** for different game phases
- **Consistency modeling** based on player rating
- **Opening preferences** based on player style

### 📊 Comprehensive Analytics
- **Player statistics**: win rates, average moves, performance
- **Style analysis**: which playing styles perform best
- **Game statistics**: moves, captures, entanglement effects
- **Tournament standings** with tiebreak systems

## Quick Start

### Basic Usage

```bash
# Single match between two players
python run_simulation.py match --white "Magnus Carlsen" --black "Fabiano Caruana"

# Multiple games between same players
python run_simulation.py multiple --white "Magnus Carlsen" --black "Fabiano Caruana" --games 10

# Round robin tournament
python run_simulation.py tournament --format round_robin --pool super_gm

# World championship match
python run_simulation.py world_championship --games 12

# Infinite simulation with random pairings
python run_simulation.py infinite --pool mixed
```

### List Available Players

```bash
# Show all players
python run_simulation.py list_players

# Filter by rating range
python run_simulation.py list_players --rating_min 2700 --rating_max 2850

# Filter by playing style
python run_simulation.py list_players --style tactical

# Show specific player pool
python run_simulation.py list_players --pool super_gm
```

## Player Database

### Super Grandmasters (2800+)
- **Magnus Carlsen** (2850) - Positional, endgame specialist
- **Fabiano Caruana** (2820) - Tactical, opening theory expert
- **Ding Liren** (2800) - Positional, defensive skills

### Top Grandmasters (2700-2799)
- **Ian Nepomniachtchi** (2750) - Tactical, aggressive
- **Hikaru Nakamura** (2720) - Blitz specialist, online play
- **Wesley So** (2700) - Positional, consistent

### Strong Grandmasters (2600-2699)
- **Levon Aronian** (2680) - Tactical, creative
- **Anish Giri** (2650) - Positional, defensive
- **Maxime Vachier-Lagrave** (2620) - Tactical, aggressive

### International Masters (2400-2599)
- **Alexander Grischuk** (2580) - Blitz specialist
- **Vladimir Kramnik** (2550) - Positional, classical
- **Viswanathan Anand** (2520) - Classical, experienced

### Strong Masters (2200-2399)
- **Eric Hansen** (2350) - Blitz, entertainment
- **John Bartholomew** (2300) - Positional, teaching
- **GothamChess** (2250) - Tactical, teaching

## Playing Styles

### Tactical Players
- **Strengths**: Sharp tactical vision, calculation, aggressive play
- **Weaknesses**: Endgame technique, defensive positions
- **Examples**: Fabiano Caruana, Ian Nepomniachtchi, Maxime Vachier-Lagrave

### Positional Players
- **Strengths**: Strategic understanding, endgame, defensive skills
- **Weaknesses**: Aggressive openings, tactical complications
- **Examples**: Magnus Carlsen, Ding Liren, Wesley So

### Blitz Players
- **Strengths**: Fast play, tactical vision, time management
- **Weaknesses**: Classical preparation, endgame technique
- **Examples**: Hikaru Nakamura, Alexander Grischuk, Eric Hansen

## Tournament Formats

### Round Robin
- All players face each other
- Most comprehensive format
- Best for determining overall strength

### Swiss System
- Players paired by score
- Good for large tournaments
- Balances competitive games

### Knockout
- Single elimination
- Most exciting format
- Best for determining champion

### World Championship
- Head-to-head match
- Multiple games
- Most prestigious format

## Player Pools

### By Rating
- **super_gm**: 2800+ (3 players)
- **top_gm**: 2700-2799 (3 players)
- **strong_gm**: 2600-2699 (3 players)
- **im**: 2400-2599 (3 players)
- **master**: 2200-2399 (3 players)

### By Style
- **tactical**: Aggressive, sharp players (5 players)
- **positional**: Strategic, patient players (6 players)
- **blitz**: Fast, intuitive players (3 players)

### Mixed
- **mixed**: All players (12 players)

## Human-like AI Features

### Skill Modeling
- **Base skill**: Normalized rating (0-1 scale)
- **Time control adjustment**: Players perform better in preferred time controls
- **Style bonuses**: Extra skill in preferred game phases
- **Time pressure**: Performance degrades under pressure

### Error Patterns
- **Blunder rates**: Based on player profile and game state
- **Consistency**: Better players more consistent
- **Time pressure effects**: Increased errors under pressure
- **Game phase effects**: Different performance in opening/middlegame/endgame

### Move Selection
- **Quality-based filtering**: Choose from best/middle/worst moves based on skill
- **Blunder simulation**: Occasionally choose suboptimal moves
- **Style preferences**: Tactical players prefer sharp moves, positional players prefer solid moves

## Output and Logging

### Game Logs
- **Detailed move logs** with player names and move notation
- **PGN format** for chess analysis
- **JSONL format** for programmatic analysis
- **Summary statistics** for each game

### Tournament Results
- **Standings tables** with win/loss/draw records
- **Player statistics** with performance metrics
- **Style analysis** showing which styles perform best
- **Comprehensive statistics** saved to JSON files

### Log Directory Structure
```
simulation_logs/
└── 20250101/
    ├── game_0001_120000.log
    ├── game_0001_120000_summary.json
    ├── game_0001_120000.jsonl
    └── simulation_statistics.json
```

## Advanced Usage

### Custom Player Pools
```python
from player_database import get_players_by_rating_range, get_players_by_style

# Get players by rating range
players = get_players_by_rating_range(2600, 2800)

# Get players by style
tactical_players = get_players_by_style(PlayerStyle.TACTICAL)
```

### Custom Tournament Formats
```python
from tournament_system import TournamentSystem

# Create custom tournament
system = TournamentSystem()
tournament = system.create_round_robin_tournament("Custom Tournament", players)
tournament = system.run_tournament(tournament, live=True)
```

### Custom Simulation Parameters
```python
from comprehensive_simulator import ComprehensiveSimulator, SimulationConfig

# Custom configuration
config = SimulationConfig(
    white_player="Magnus Carlsen",
    black_player="Fabiano Caruana",
    num_games=10,
    tournament_format="round_robin",
    player_pool="super_gm",
    logs_dir="custom_logs",
    seed_base=42,
    max_moves=200,
    live_details=True,
    infinite=False,
    save_logs=True
)

# Run simulation
simulator = ComprehensiveSimulator(config)
results = simulator.run_multiple_games()
simulator.analyze_results(results)
```

## Examples

### World Championship Simulation
```bash
python run_simulation.py world_championship --games 12 --save_logs
```

### Tactical vs Positional Tournament
```bash
python run_simulation.py tournament --format round_robin --pool tactical --save_logs
```

### Blitz Players Only
```bash
python run_simulation.py tournament --format swiss --pool blitz --save_logs
```

### Infinite Simulation
```bash
python run_simulation.py infinite --pool mixed --save_logs --live_details
```

## Technical Details

### Dependencies
- Python 3.7+
- Standard library only (no external dependencies)

### File Structure
```
QEC/
├── main.py                    # Core QEC game engine
├── player_database.py         # Real chess player profiles
├── human_simulation.py       # Human-like AI simulation
├── opening_book.py           # Chess opening patterns
├── tournament_system.py      # Tournament management
├── comprehensive_simulator.py # Complete simulation framework
├── run_simulation.py         # CLI interface
└── README_HUMAN_SIMULATION.md # This documentation
```

### Performance
- **Single game**: ~0.4 seconds
- **Tournament (12 players)**: ~5 minutes
- **Infinite simulation**: Continuous with automatic logging

## Contributing

To add new players or modify existing ones, edit `player_database.py`:

```python
ChessPlayer(
    name="Your Player Name",
    rating=2600,
    style=PlayerStyle.TACTICAL,
    strengths=["tactical vision", "calculation"],
    weaknesses=["endgame technique"],
    opening_preferences=["Sicilian Defense", "King's Indian"],
    time_control_preference="classical",
    aggression_level=0.7,
    calculation_depth=8,
    blunder_rate=0.04,
    tactical_vision=0.90,
    endgame_strength=0.80,
    opening_knowledge=0.85
)
```

## License

This project is part of the QEC (Quantum Entanglement Chess) simulation framework.
