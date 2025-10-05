# QEC Research Framework

A comprehensive research framework for analyzing Quantum Entanglement Chess (QEC) rules, patterns, and player behavior through archetype-based simulation and data collection.

## 🎯 Research Goals

- **Rule Analysis**: Understand which QEC rules create interesting gameplay
- **Pattern Discovery**: Identify emergent patterns in QEC games
- **Player Behavior**: Analyze how different playing styles perform in QEC
- **Rule Optimization**: Determine optimal rule configurations
- **Data Collection**: Gather comprehensive data for statistical analysis

## 🧠 Archetype System

### 7-Dimensional Player Vectors

Each archetype is defined by 7 parameters (0-1 scale):

- **Aggression (A)**: Prefers forcing chains and checks
- **Risk (R)**: Accepts material loss for entanglement gains  
- **Tempo (T)**: Plays fast forcing moves creating time pressure
- **King Safety (K)**: Penalizes reactive-check exposure
- **Pawn Control (P)**: Values "my-pawn-controls-your-piece"
- **Disentangle Bias (D)**: Aims to free own pieces vs keep opponent bound
- **Complexity (C)**: Seeks positions with many forced replies

### Pre-defined Archetypes

1. **Carlsen-like**: Balanced, positional, endgame specialist
   - Vector: [0.4, 0.3, 0.5, 0.9, 0.8, 0.6, 0.7]
   - Weights: w1:30 w2:-18 w3:28 w4:20 w5:-90 w6:18

2. **Tal-like**: Aggressive, tactical, complex positions
   - Vector: [0.9, 0.8, 0.7, 0.4, 0.5, 0.7, 0.9]
   - Weights: w1:35 w2:-21 w3:36 w4:13 w5:-40 w6:25

3. **Karpov-like**: Positional, solid, low risk
   - Vector: [0.3, 0.2, 0.4, 0.95, 0.9, 0.4, 0.3]
   - Weights: w1:20 w2:-12 w3:12 w4:23 w5:-95 w6:14

4. **Pragmatic**: Material-first, simple positions
   - Vector: [0.5, 0.3, 0.6, 0.7, 0.6, 0.5, 0.2]
   - Weights: w1:25 w2:-15 w3:8 w4:15 w5:-70 w6:21

5. **Hypermodern**: Complex, tempo-focused
   - Vector: [0.6, 0.6, 0.8, 0.6, 0.7, 0.8, 0.8]
   - Weights: w1:40 w2:-24 w3:32 w4:18 w5:-60 w6:28

6. **Defensive**: King safety first, low complexity
   - Vector: [0.2, 0.1, 0.3, 0.95, 0.8, 0.3, 0.2]
   - Weights: w1:15 w2:-9 w3:8 w4:20 w5:-95 w6:11

## 📊 QEC-Specific Evaluation

### 6 QEC Evaluation Terms

- **w1**: +opponent pieces entangled to your pawns
- **w2**: -your pieces entangled to their pawns  
- **w3**: +forced replies available next ply
- **w4**: +free-piece differential after captures/promos
- **w5**: -reactive-check vulnerability score
- **w6**: +rook/queen activity from opponent-forced drifts

### Evaluation Weights by Archetype

| Archetype | w1 | w2 | w3 | w4 | w5 | w6 |
|-----------|----|----|----|----|----|----|
| Carlsen-like | 30 | -18 | 28 | 20 | -90 | 18 |
| Tal-like | 35 | -21 | 36 | 13 | -40 | 25 |
| Karpov-like | 20 | -12 | 12 | 23 | -95 | 14 |
| Pragmatic | 25 | -15 | 8 | 15 | -70 | 21 |
| Hypermodern | 40 | -24 | 32 | 18 | -60 | 28 |
| Defensive | 15 | -9 | 8 | 20 | -95 | 11 |

## 🔬 Research Commands

### Basic Usage

```bash
# List available archetypes
python run_qec_research.py list --show_weights

# Run small experiment
python run_qec_research.py experiment --archetypes "Carlsen-like,Tal-like" --games 10 --maps 5

# Run large experiment with all archetypes
python run_qec_research.py experiment --archetypes all --games 50 --maps 20 --save_logs --save_plys

# Compare two specific archetypes
python run_qec_research.py compare --archetype1 "Carlsen-like" --archetype2 "Tal-like" --games 100

# Analyze existing data
python run_qec_research.py analyze --logs_dir qec_research_logs --create_csv --create_plots
```

### Advanced Usage

```bash
# Run ablation study (remove specific rules)
python run_qec_research.py ablation --rule reactive_check --games 20

# Run with custom parameters
python run_qec_research.py experiment --archetypes "Tal-like,Hypermodern" --games 30 --maps 10 --depth 3 --max_moves 300

# Analyze with custom output
python run_qec_research.py analyze --logs_dir my_logs --output_dir analysis_results --create_csv --create_plots
```

## 📈 Data Collection

### Per-Game Data

Each game records:
- **Basic**: Result, plies, captures, promotions
- **QEC-Specific**: Forced moves, reactive moves, reactive mates
- **Entanglement**: Pairs remaining at moves 10/20/30
- **King Activity**: Reactive moves, distance traveled
- **Evaluation**: Swing (volatility), average legal moves
- **Timing**: First move advantage, duration

### Per-Ply Data (JSONL)

Each ply records:
```json
{
  "game_id": "game_0001",
  "ply": 42,
  "side": "W",
  "primary": "e5e6",
  "forced": "— or h8f8",
  "react": "— or f2e2",
  "ent_map_hash": "a1b2c3d4",
  "ent_changes": ["b2↔Nb8:break"],
  "eval": 2273,
  "phase": "mid",
  "legal_count": 23,
  "time_used_ms": 531,
  "notes": "check; chain=2"
}
```

### Output Files

- **Summary CSV**: `qec_summary.csv` - All game results
- **Ply CSV**: `qec_plys.csv` - All ply data
- **Analysis JSON**: `research_analysis.json` - Statistical analysis
- **Visualizations**: `qec_analysis.png` - Performance plots

## 🔍 Analysis Features

### Archetype Performance
- Win rates by archetype
- Average game length
- Forced/reactive move patterns
- Entanglement persistence

### QEC-Specific Patterns
- Forced move frequency
- Reactive mate rates
- Entanglement breakdown over time
- King activity patterns

### Statistical Analysis
- First move advantage
- Archetype correlations
- Rule effectiveness
- Pattern discovery

## 🧪 Experimental Design

### Matchup Matrix
- Full round-robin of archetypes
- Multiple games per pairing
- Color swapping for fairness
- Multiple entanglement maps

### Controls
- Same map played twice (colors swapped)
- Isolates first/second advantage
- Controls for entanglement effects

### Replicates
- ≥100 maps per pairing
- Smooths variance
- Enables statistical significance

## 📊 Sample Results

### Archetype Performance
```
Archetype       Games  Wins  Losses  Draws Win%
------------------------------------------------------------
Carlsen-like    36     1     2       33    2.8
Tal-like        36     1     2       33    2.8
Karpov-like     36     3     1       32    8.3
```

### QEC Statistics
```
Total forced moves: 0
Total reactive moves: 724
Total reactive mates: 5
Average plies: 187.2
Average captures: 23.3
```

## 🎯 Research Applications

### Rule Analysis
- Which rules create interesting gameplay?
- What are the effects of rule modifications?
- How do rules interact with each other?

### Player Behavior
- Which playing styles work best in QEC?
- How do archetypes adapt to QEC rules?
- What are the optimal playing strategies?

### Pattern Discovery
- What emergent patterns appear in QEC?
- How do games differ from regular chess?
- What makes QEC unique?

### Rule Optimization
- What are the optimal rule configurations?
- How can rules be improved?
- What balance creates the best gameplay?

## 🛠️ Technical Details

### Dependencies
- Python 3.7+
- Standard library only
- Optional: matplotlib, pandas, numpy for analysis

### File Structure
```
QEC/
├── qec_archetypes.py          # Player archetype definitions
├── qec_evaluation.py          # QEC-specific evaluation
├── qec_research_simulator.py  # Research simulation engine
├── analyze_qec_data.py        # Data analysis tools
├── run_qec_research.py        # CLI interface
└── README_QEC_RESEARCH.md     # This documentation
```

### Performance
- **Single game**: ~0.5 seconds
- **Small experiment (54 games)**: ~30 seconds
- **Large experiment (1000+ games)**: ~10 minutes
- **Analysis**: ~1 minute

## 📚 Usage Examples

### Quick Start
```bash
# Run a small experiment
python run_qec_research.py experiment --archetypes "Carlsen-like,Tal-like" --games 10

# Analyze the results
python run_qec_research.py analyze --logs_dir qec_research_logs --create_csv
```

### Large Scale Research
```bash
# Run comprehensive experiment
python run_qec_research.py experiment --archetypes all --games 100 --maps 20 --save_logs --save_plys

# Deep analysis with visualizations
python run_qec_research.py analyze --logs_dir qec_research_logs --output_dir results --create_csv --create_plots
```

### Comparative Studies
```bash
# Compare specific archetypes
python run_qec_research.py compare --archetype1 "Carlsen-like" --archetype2 "Tal-like" --games 200

# Run ablation study
python run_qec_research.py ablation --rule reactive_check --games 50
```

## 🎯 Next Steps

1. **Run Large Experiments**: Collect data on 1000+ games
2. **Pattern Analysis**: Identify emergent QEC patterns
3. **Rule Optimization**: Test rule modifications
4. **Player Development**: Create new archetypes
5. **Statistical Analysis**: Deep dive into the data

This framework provides everything needed to conduct comprehensive QEC research and discover the patterns that make Quantum Entanglement Chess unique and engaging!
