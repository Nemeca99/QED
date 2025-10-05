# QEC Research Plan: Theory-Driven Data Collection

## 🎯 Research Philosophy

**Theory First, Data Second**: We design our experiments around specific testable hypotheses rather than collecting data blindly. This ensures our computational resources are used efficiently and our results are interpretable.

## 📋 Research Hypotheses

### H1: Opening Determinism Hypothesis
**Theory**: The first legal move collapses the entire entangled configuration tree; therefore early moves carry exponentially greater impact on outcome probability.

**Prediction**: Win-rate variance after move 1 should be larger than after any other single move.

**Data Needed**:
- `first_move_notation`
- `first_move_eval_delta`
- `move_1_win_rate_variance`
- `move_2_win_rate_variance`
- `move_3_win_rate_variance`

**Test Method**: Compare win-rate variance by move number across large sample (1000+ games)

---

### H2: Free-Pawn Centrality
**Theory**: The location of the free pawn drives the overall mobility and tempo of the side that owns it. Certain free-pawn files (e.g., central vs. wing) will statistically correlate with higher win rates.

**Prediction**: Central free pawns (d/e files) will correlate with higher win rates than wing pawns (a/h files).

**Data Needed**:
- `white_free_pawn_file`
- `black_free_pawn_file`
- `free_pawn_centrality_score`
- `mobility_metrics`
- `tempo_metrics`

**Test Method**: Correlate free pawn file with win rate and mobility metrics

---

### H3: Information-Asymmetry Effect
**Theory**: Knowing your own free pawn gives you hidden information. Players who can leverage this asymmetry faster—by forcing discovery of the opponent's free pawn—gain a measurable early advantage.

**Prediction**: Games where one side discovers opponent's free pawn earlier will show measurable advantage for the discovering side.

**Data Needed**:
- `free_pawn_discovery_ply`
- `discovery_side`
- `eval_after_discovery`
- `information_advantage_metrics`

**Test Method**: Track when each side's free pawn is revealed, correlate with outcomes

---

### H4: Second-Player Advantage Hypothesis
**Theory**: Because player 2 can see and react to player 1's entanglement activation before moving, the second player may have a higher expected evaluation after the opening phase.

**Prediction**: Black (second player) will show higher average evaluation after opening phase (moves 1-10).

**Data Needed**:
- `opening_phase_evals`
- `first_player_entanglement_activation`
- `second_player_reaction_time`
- `eval_after_opening`
- `color_advantage_metrics`

**Test Method**: Compare average evaluations by color after opening phase

---

### H5: Entanglement Stability vs. Breakage
**Theory**: Longer-lasting entanglement networks might correlate with control, while rapid breakage could correlate with tactical volatility.

**Prediction**: Games with stable entanglement (fewer breaks) will be longer and more positional, while rapid breakage correlates with shorter, more tactical games.

**Data Needed**:
- `entanglement_break_count`
- `entanglement_persistence_ratio`
- `game_length`
- `tactical_vs_positional_score`
- `entanglement_stability_metrics`

**Test Method**: Correlate entanglement stability with game characteristics

---

### H6: Reactive-Check Survival Bias
**Theory**: Games in which kings are forced to REACT multiple times will tend to shorten; you can measure how many reactive checks occur before the losing side collapses.

**Prediction**: Games with more reactive checks will be shorter, and there's a threshold number of reactive checks that predicts game end.

**Data Needed**:
- `reactive_check_count`
- `reactive_check_sequence`
- `reactive_check_survival_rate`
- `collapse_prediction_metrics`

**Test Method**: Track reactive check sequences and correlate with game outcomes

---

### H7: Archetype-Entanglement Interaction
**Theory**: Different playing styles (archetypes) will interact differently with entanglement rules, creating distinct gameplay patterns.

**Prediction**: Tactical archetypes will benefit more from entanglement breakage, while positional archetypes will prefer stable entanglement.

**Data Needed**:
- `archetype_style`
- `entanglement_interaction_patterns`
- `archetype_win_rate_by_entanglement_type`
- `style_entanglement_correlation`

**Test Method**: Compare archetype performance across different entanglement scenarios

---

### H8: Forced-Move Cascade Effect
**Theory**: Forced moves create cascading effects that amplify tactical complexity and reduce game predictability.

**Prediction**: Games with more forced moves will show higher evaluation volatility and more tactical complexity.

**Data Needed**:
- `forced_move_count`
- `forced_move_cascade_length`
- `evaluation_volatility`
- `tactical_complexity_score`
- `game_predictability_metrics`

**Test Method**: Measure forced move patterns and correlate with game characteristics

## 🔬 Experimental Design

### Phase 1: Data Collection (1000+ games)
```bash
# Run comprehensive hypothesis testing
python qec_hypothesis_tester.py --archetypes "Carlsen-like,Tal-like,Karpov-like,Hypermodern,Defensive" --games 1000
```

**Target Metrics**:
- 1000+ games with full hypothesis data
- All 38 required data fields collected
- Per-ply JSONL logging for detailed analysis

### Phase 2: Statistical Analysis
```bash
# Analyze collected data
python analyze_qec_data.py --logs_dir hypothesis_test_logs --create_csv --create_plots
```

**Analysis Methods**:
- Correlation analysis for H2, H3, H5, H6, H7, H8
- Variance analysis for H1, H4
- Regression analysis for all hypotheses
- Statistical significance testing

### Phase 3: Validation (500+ games)
```bash
# Run targeted validation experiments
python run_qec_research.py experiment --archetypes "Carlsen-like,Tal-like" --games 500 --maps 20
```

**Validation Focus**:
- Confirm significant findings
- Test edge cases
- Refine hypothesis parameters

## 📊 Data Collection Schema

### Per-Game Data (38 fields)
```json
{
  "game_id": "hyp_game_0001",
  "white_archetype": "Carlsen-like",
  "black_archetype": "Tal-like",
  "result": "W wins",
  "total_plies": 45,
  
  // H1: Opening Determinism
  "first_move_notation": "e2e4",
  "first_move_eval_delta": 0.3,
  "move_1_win_rate_variance": 0.15,
  "move_2_win_rate_variance": 0.12,
  "move_3_win_rate_variance": 0.08,
  
  // H2: Free-Pawn Centrality
  "white_free_pawn_file": "d",
  "black_free_pawn_file": "e", 
  "free_pawn_centrality_score": 0.85,
  "mobility_metrics": {"white": 0.7, "black": 0.6},
  "tempo_metrics": {"white": 0.8, "black": 0.5},
  
  // ... (all 38 fields)
}
```

### Per-Ply Data (JSONL)
```json
{
  "game_id": "hyp_game_0001",
  "ply": 15,
  "side": "W",
  "move": "e2e4",
  "eval": 0.3,
  "reactive_check": false,
  "forced_move": true,
  "entanglement_break": false,
  "ent_map_hash": "a1b2c3d4",
  "phase": "opening"
}
```

## 🎯 Success Metrics

### Hypothesis Testing Results
- **H1**: Move 1 variance > Move 2 variance > Move 3 variance
- **H2**: d/e files > c/f files > b/g files > a/h files in win rate
- **H3**: Earlier discovery correlates with higher win rate
- **H4**: Black average eval > White average eval after opening
- **H5**: Stable entanglement → longer games, rapid breakage → tactical games
- **H6**: More reactive checks → shorter games, threshold exists for collapse
- **H7**: Tactical archetypes win more in high-breakage games, positional in stable games
- **H8**: More forced moves → higher volatility and complexity

### Statistical Significance
- p < 0.05 for all correlations
- Effect size > 0.1 for practical significance
- 95% confidence intervals for all metrics

## 🛠️ Implementation Status

### ✅ Completed
- [x] Hypothesis framework (8 testable hypotheses)
- [x] Archetype system (6 archetypes with 7D vectors)
- [x] QEC-specific evaluation (6 evaluation terms)
- [x] Data collection schema (38 fields + per-ply JSONL)
- [x] Research simulator with hypothesis tracking
- [x] Analysis tools for pattern discovery

### 🚧 In Progress
- [ ] Full statistical analysis implementation
- [ ] Advanced entanglement tracking
- [ ] Free pawn discovery detection
- [ ] Evaluation volatility calculation
- [ ] Correlation analysis tools

### 📋 Next Steps
1. **Run Large Experiment**: 1000+ games with full hypothesis data
2. **Statistical Analysis**: Implement all correlation and variance tests
3. **Pattern Discovery**: Identify emergent QEC patterns
4. **Rule Optimization**: Use findings to improve QEC rules
5. **Validation**: Confirm findings with targeted experiments

## 🎯 Expected Outcomes

### Scientific Insights
- Which QEC rules create the most interesting gameplay?
- How do different playing styles interact with entanglement?
- What patterns emerge in QEC that don't exist in regular chess?
- How can we optimize QEC rules for better gameplay?

### Practical Applications
- Improved QEC rule set based on data
- Better understanding of player behavior in QEC
- Guidelines for QEC tournament organization
- Insights for QEC strategy development

This research plan provides a clear roadmap for understanding QEC through systematic hypothesis testing and data-driven analysis!
