"""
QEC Research Hypotheses
Testable hypotheses for QEC rule analysis and pattern discovery
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum

class HypothesisStatus(Enum):
    UNTESTED = "untested"
    TESTING = "testing"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    PARTIAL = "partial"

@dataclass
class QECHypothesis:
    """A testable hypothesis about QEC behavior"""
    id: str
    title: str
    description: str
    prediction: str
    data_needed: List[str]
    metrics: List[str]
    test_method: str
    expected_result: str
    status: HypothesisStatus = HypothesisStatus.UNTESTED
    notes: str = ""

# Core QEC Hypotheses
QEC_HYPOTHESES = [
    QECHypothesis(
        id="H1",
        title="Opening Determinism Hypothesis",
        description="The first legal move collapses the entire entangled configuration tree; therefore early moves carry exponentially greater impact on outcome probability.",
        prediction="Win-rate variance after move 1 should be larger than after any other single move.",
        data_needed=[
            "first_move_notation",
            "first_move_eval_delta", 
            "game_outcome",
            "move_1_win_rate_variance",
            "move_2_win_rate_variance",
            "move_3_win_rate_variance"
        ],
        metrics=[
            "variance_after_move_1",
            "variance_after_move_2", 
            "variance_after_move_3",
            "first_move_impact_score"
        ],
        test_method="Compare win-rate variance by move number across large sample",
        expected_result="Move 1 variance > Move 2 variance > Move 3 variance",
        notes="Test with 1000+ games, measure outcome variance by move number"
    ),
    
    QECHypothesis(
        id="H2", 
        title="Free-Pawn Centrality",
        description="The location of the free pawn drives the overall mobility and tempo of the side that owns it. Certain free-pawn files (e.g., central vs. wing) will statistically correlate with higher win rates.",
        prediction="Central free pawns (d/e files) will correlate with higher win rates than wing pawns (a/h files).",
        data_needed=[
            "white_free_pawn_file",
            "black_free_pawn_file",
            "free_pawn_centrality_score",
            "game_outcome",
            "mobility_metrics",
            "tempo_metrics"
        ],
        metrics=[
            "win_rate_by_free_pawn_file",
            "centrality_correlation",
            "mobility_differential",
            "tempo_advantage"
        ],
        test_method="Correlate free pawn file with win rate and mobility metrics",
        expected_result="d/e files > c/f files > b/g files > a/h files in win rate",
        notes="Central files (d,e) should show highest win rates"
    ),
    
    QECHypothesis(
        id="H3",
        title="Information-Asymmetry Effect", 
        description="Knowing your own free pawn gives you hidden information. Players who can leverage this asymmetry faster—by forcing discovery of the opponent's free pawn—gain a measurable early advantage.",
        prediction="Games where one side discovers opponent's free pawn earlier will show measurable advantage for the discovering side.",
        data_needed=[
            "free_pawn_discovery_ply",
            "discovery_side",
            "eval_after_discovery",
            "game_outcome",
            "information_advantage_metrics"
        ],
        metrics=[
            "discovery_ply_correlation",
            "post_discovery_eval_delta",
            "information_advantage_score",
            "early_discovery_win_rate"
        ],
        test_method="Track when each side's free pawn is revealed, correlate with outcomes",
        expected_result="Earlier discovery correlates with higher win rate",
        notes="Measure when entanglement moves reveal free pawns"
    ),
    
    QECHypothesis(
        id="H4",
        title="Second-Player Advantage Hypothesis",
        description="Because player 2 can see and react to player 1's entanglement activation before moving, the second player may have a higher expected evaluation after the opening phase.",
        prediction="Black (second player) will show higher average evaluation after opening phase (moves 1-10).",
        data_needed=[
            "opening_phase_evals",
            "first_player_entanglement_activation",
            "second_player_reaction_time",
            "eval_after_opening",
            "color_advantage_metrics"
        ],
        metrics=[
            "black_avg_eval_after_opening",
            "white_avg_eval_after_opening", 
            "second_player_advantage_score",
            "opening_phase_eval_delta"
        ],
        test_method="Compare average evaluations by color after opening phase",
        expected_result="Black average eval > White average eval after opening",
        notes="Test with 500+ games, measure eval after moves 1-10"
    ),
    
    QECHypothesis(
        id="H5",
        title="Entanglement Stability vs. Breakage",
        description="Longer-lasting entanglement networks might correlate with control, while rapid breakage could correlate with tactical volatility.",
        prediction="Games with stable entanglement (fewer breaks) will be longer and more positional, while rapid breakage correlates with shorter, more tactical games.",
        data_needed=[
            "entanglement_break_count",
            "entanglement_persistence_ratio",
            "game_length",
            "tactical_vs_positional_score",
            "entanglement_stability_metrics"
        ],
        metrics=[
            "stability_correlation_with_length",
            "breakage_correlation_with_tactics",
            "entanglement_persistence_score",
            "control_vs_volatility_ratio"
        ],
        test_method="Correlate entanglement stability with game characteristics",
        expected_result="Stable entanglement → longer games, rapid breakage → tactical games",
        notes="Measure entanglement changes over time"
    ),
    
    QECHypothesis(
        id="H6",
        title="Reactive-Check Survival Bias",
        description="Games in which kings are forced to REACT multiple times will tend to shorten; you can measure how many reactive checks occur before the losing side collapses.",
        prediction="Games with more reactive checks will be shorter, and there's a threshold number of reactive checks that predicts game end.",
        data_needed=[
            "reactive_check_count",
            "reactive_check_sequence",
            "game_length",
            "reactive_check_survival_rate",
            "collapse_prediction_metrics"
        ],
        metrics=[
            "reactive_checks_vs_length_correlation",
            "survival_rate_by_reactive_count",
            "collapse_threshold",
            "reactive_check_volatility_score"
        ],
        test_method="Track reactive check sequences and correlate with game outcomes",
        expected_result="More reactive checks → shorter games, threshold exists for collapse",
        notes="Measure reactive check patterns and survival rates"
    ),
    
    QECHypothesis(
        id="H7",
        title="Archetype-Entanglement Interaction",
        description="Different playing styles (archetypes) will interact differently with entanglement rules, creating distinct gameplay patterns.",
        prediction="Tactical archetypes will benefit more from entanglement breakage, while positional archetypes will prefer stable entanglement.",
        data_needed=[
            "archetype_style",
            "entanglement_interaction_patterns",
            "archetype_win_rate_by_entanglement_type",
            "style_entanglement_correlation"
        ],
        metrics=[
            "tactical_archetype_breakage_advantage",
            "positional_archetype_stability_advantage",
            "archetype_entanglement_interaction_score"
        ],
        test_method="Compare archetype performance across different entanglement scenarios",
        expected_result="Tactical archetypes win more in high-breakage games, positional in stable games",
        notes="Test archetype performance across entanglement stability levels"
    ),
    
    QECHypothesis(
        id="H8",
        title="Forced-Move Cascade Effect",
        description="Forced moves create cascading effects that amplify tactical complexity and reduce game predictability.",
        prediction="Games with more forced moves will show higher evaluation volatility and more tactical complexity.",
        data_needed=[
            "forced_move_count",
            "forced_move_cascade_length",
            "evaluation_volatility",
            "tactical_complexity_score",
            "game_predictability_metrics"
        ],
        metrics=[
            "forced_moves_vs_volatility_correlation",
            "cascade_length_vs_complexity",
            "forced_move_amplification_score"
        ],
        test_method="Measure forced move patterns and correlate with game characteristics",
        expected_result="More forced moves → higher volatility and complexity",
        notes="Track forced move sequences and their effects"
    )
]

def get_hypothesis_by_id(hypothesis_id: str) -> Optional[QECHypothesis]:
    """Get hypothesis by ID"""
    for hyp in QEC_HYPOTHESES:
        if hyp.id == hypothesis_id:
            return hyp
    return None

def get_hypotheses_by_status(status: HypothesisStatus) -> List[QECHypothesis]:
    """Get hypotheses by status"""
    return [hyp for hyp in QEC_HYPOTHESES if hyp.status == status]

def get_required_data_fields() -> List[str]:
    """Get all unique data fields needed for hypothesis testing"""
    all_fields = set()
    for hyp in QEC_HYPOTHESES:
        all_fields.update(hyp.data_needed)
    return sorted(list(all_fields))

def get_required_metrics() -> List[str]:
    """Get all unique metrics needed for hypothesis testing"""
    all_metrics = set()
    for hyp in QEC_HYPOTHESES:
        all_metrics.update(hyp.metrics)
    return sorted(list(all_metrics))

def create_hypothesis_test_plan() -> Dict[str, Any]:
    """Create a comprehensive test plan for all hypotheses"""
    return {
        "total_hypotheses": len(QEC_HYPOTHESES),
        "required_data_fields": get_required_data_fields(),
        "required_metrics": get_required_metrics(),
        "test_phases": [
            {
                "phase": "Data Collection",
                "description": "Run large-scale simulations to collect required data",
                "games_needed": 1000,
                "hypotheses": [hyp.id for hyp in QEC_HYPOTHESES]
            },
            {
                "phase": "Statistical Analysis", 
                "description": "Analyze collected data for hypothesis testing",
                "methods": ["correlation_analysis", "variance_analysis", "regression_analysis"],
                "hypotheses": [hyp.id for hyp in QEC_HYPOTHESES]
            },
            {
                "phase": "Validation",
                "description": "Run additional targeted experiments to validate findings",
                "games_needed": 500,
                "hypotheses": [hyp.id for hyp in QEC_HYPOTHESES if hyp.status == HypothesisStatus.PARTIAL]
            }
        ]
    }

def print_hypothesis_summary():
    """Print a summary of all hypotheses"""
    print("=== QEC Research Hypotheses ===")
    print(f"Total hypotheses: {len(QEC_HYPOTHESES)}")
    print()
    
    for hyp in QEC_HYPOTHESES:
        print(f"{hyp.id}: {hyp.title}")
        print(f"  Prediction: {hyp.prediction}")
        print(f"  Status: {hyp.status.value}")
        print(f"  Data needed: {len(hyp.data_needed)} fields")
        print(f"  Metrics: {len(hyp.metrics)} metrics")
        print()
    
    print("Required data fields:")
    fields = get_required_data_fields()
    for i, field in enumerate(fields, 1):
        print(f"  {i:2d}. {field}")
    
    print(f"\nTotal unique data fields: {len(fields)}")
    print(f"Total unique metrics: {len(get_required_metrics())}")

if __name__ == "__main__":
    print_hypothesis_summary()
    
    print("\n=== Test Plan ===")
    plan = create_hypothesis_test_plan()
    print(f"Total hypotheses: {plan['total_hypotheses']}")
    print(f"Required data fields: {len(plan['required_data_fields'])}")
    print(f"Required metrics: {len(plan['required_metrics'])}")
    
    print("\nTest phases:")
    for phase in plan['test_phases']:
        print(f"  {phase['phase']}: {phase['description']}")
        if 'games_needed' in phase:
            print(f"    Games needed: {phase['games_needed']}")
        if 'methods' in phase:
            print(f"    Methods: {', '.join(phase['methods'])}")
