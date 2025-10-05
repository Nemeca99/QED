"""
QEC Player Archetypes - Parameterized playing styles for research
Based on real chess player characteristics with QEC-specific adaptations
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import random
import math

@dataclass
class QECArchetype:
    """Parameterized player archetype for QEC research"""
    name: str
    aggression: float      # A: prefers forcing chains/checks (0-1)
    risk: float          # R: accepts material loss for ent-map gains (0-1)
    tempo: float         # T: plays fast forcing moves (0-1)
    king_safety: float   # K: penalizes reactive-check exposure (0-1)
    pawn_control: float  # P: values "my-pawn-controls-your-piece" (0-1)
    disentangle_bias: float  # D: aims to free own pieces (0-1)
    complexity: float     # C: seeks positions with many forced replies (0-1)
    
    # QEC-specific evaluation weights
    w1: float = 0.0  # +opponent pieces entangled to your pawns
    w2: float = 0.0  # -your pieces entangled to their pawns
    w3: float = 0.0  # +forced replies available next ply
    w4: float = 0.0  # +free-piece differential after captures/promos
    w5: float = 0.0  # -reactive-check vulnerability score
    w6: float = 0.0  # +rook/queen activity from opponent-forced drifts
    
    # Search parameters
    search_depth: int = 2
    move_limit: int = 30  # Top N moves to consider
    
    def __post_init__(self):
        """Calculate QEC evaluation weights based on archetype vector"""
        # Map archetype parameters to evaluation weights
        self.w1 = self.disentangle_bias * 50  # Free opponent pieces from entanglement
        self.w2 = -self.disentangle_bias * 30  # Keep own pieces entangled
        self.w3 = self.complexity * 40  # Create forced replies
        self.w4 = self.pawn_control * 25  # Free-piece differential
        self.w5 = -self.king_safety * 100  # Avoid reactive-check exposure
        self.w6 = self.tempo * 35  # Create activity from forced moves
        
        # Adjust search depth based on complexity preference
        self.search_depth = max(1, min(3, int(2 + self.complexity)))

# Real chess player archetypes adapted for QEC
QEC_ARCHETYPES = [
    # Magnus Carlsen-like: Balanced, positional, endgame specialist
    QECArchetype(
        name="Carlsen-like",
        aggression=0.4,
        risk=0.3,
        tempo=0.5,
        king_safety=0.9,
        pawn_control=0.8,
        disentangle_bias=0.6,
        complexity=0.7
    ),
    
    # Mikhail Tal-like: Aggressive, tactical, complex positions
    QECArchetype(
        name="Tal-like",
        aggression=0.9,
        risk=0.8,
        tempo=0.7,
        king_safety=0.4,
        pawn_control=0.5,
        disentangle_bias=0.7,
        complexity=0.9
    ),
    
    # Anatoly Karpov-like: Positional, solid, low risk
    QECArchetype(
        name="Karpov-like",
        aggression=0.3,
        risk=0.2,
        tempo=0.4,
        king_safety=0.95,
        pawn_control=0.9,
        disentangle_bias=0.4,
        complexity=0.3
    ),
    
    # Pragmatic: Material-first, simple positions
    QECArchetype(
        name="Pragmatic",
        aggression=0.5,
        risk=0.3,
        tempo=0.6,
        king_safety=0.7,
        pawn_control=0.6,
        disentangle_bias=0.5,
        complexity=0.2
    ),
    
    # Hypermodern: Complex, tempo-focused
    QECArchetype(
        name="Hypermodern",
        aggression=0.6,
        risk=0.6,
        tempo=0.8,
        king_safety=0.6,
        pawn_control=0.7,
        disentangle_bias=0.8,
        complexity=0.8
    ),
    
    # Defensive: King safety first, low complexity
    QECArchetype(
        name="Defensive",
        aggression=0.2,
        risk=0.1,
        tempo=0.3,
        king_safety=0.95,
        pawn_control=0.8,
        disentangle_bias=0.3,
        complexity=0.2
    )
]

def get_archetype_by_name(name: str) -> Optional[QECArchetype]:
    """Get archetype by name"""
    for archetype in QEC_ARCHETYPES:
        if archetype.name.lower() == name.lower():
            return archetype
    return None

def get_archetype_vector(archetype: QECArchetype) -> List[float]:
    """Get the 7-dimensional archetype vector"""
    return [
        archetype.aggression,
        archetype.risk,
        archetype.tempo,
        archetype.king_safety,
        archetype.pawn_control,
        archetype.disentangle_bias,
        archetype.complexity
    ]

def create_custom_archetype(name: str, vector: List[float]) -> QECArchetype:
    """Create custom archetype from 7D vector"""
    if len(vector) != 7:
        raise ValueError("Archetype vector must have 7 dimensions")
    
    return QECArchetype(
        name=name,
        aggression=vector[0],
        risk=vector[1],
        tempo=vector[2],
        king_safety=vector[3],
        pawn_control=vector[4],
        disentangle_bias=vector[5],
        complexity=vector[6]
    )

def get_archetype_similarity(arch1: QECArchetype, arch2: QECArchetype) -> float:
    """Calculate cosine similarity between two archetypes"""
    v1 = get_archetype_vector(arch1)
    v2 = get_archetype_vector(arch2)
    
    dot_product = sum(a * b for a, b in zip(v1, v2))
    magnitude1 = math.sqrt(sum(a * a for a in v1))
    magnitude2 = math.sqrt(sum(a * a for a in v2))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)

def get_archetype_clusters() -> Dict[str, List[QECArchetype]]:
    """Group archetypes by similarity"""
    clusters = {}
    threshold = 0.7
    
    for archetype in QEC_ARCHETYPES:
        cluster_name = f"{archetype.name}_cluster"
        if cluster_name not in clusters:
            clusters[cluster_name] = [archetype]
        else:
            clusters[cluster_name].append(archetype)
    
    return clusters

def generate_random_archetype(name: str = "Random") -> QECArchetype:
    """Generate random archetype for experimentation"""
    return QECArchetype(
        name=name,
        aggression=random.random(),
        risk=random.random(),
        tempo=random.random(),
        king_safety=random.random(),
        pawn_control=random.random(),
        disentangle_bias=random.random(),
        complexity=random.random()
    )

def get_archetype_by_style(style: str) -> List[QECArchetype]:
    """Get archetypes by playing style"""
    style_mapping = {
        "aggressive": ["Tal-like", "Hypermodern"],
        "positional": ["Carlsen-like", "Karpov-like"],
        "defensive": ["Karpov-like", "Defensive"],
        "tactical": ["Tal-like", "Hypermodern"],
        "pragmatic": ["Pragmatic"],
        "complex": ["Tal-like", "Hypermodern"],
        "simple": ["Pragmatic", "Defensive"]
    }
    
    if style not in style_mapping:
        return QEC_ARCHETYPES
    
    return [get_archetype_by_name(name) for name in style_mapping[style] 
            if get_archetype_by_name(name) is not None]

if __name__ == "__main__":
    # Test archetype system
    print("=== QEC Archetype System ===")
    print(f"Total archetypes: {len(QEC_ARCHETYPES)}")
    
    # Show archetype vectors
    print("\nArchetype Vectors:")
    for arch in QEC_ARCHETYPES:
        vector = get_archetype_vector(arch)
        print(f"{arch.name:12} | {vector}")
    
    # Show evaluation weights
    print("\nEvaluation Weights:")
    for arch in QEC_ARCHETYPES:
        print(f"{arch.name:12} | w1:{arch.w1:4.0f} w2:{arch.w2:4.0f} w3:{arch.w3:4.0f} "
              f"w4:{arch.w4:4.0f} w5:{arch.w5:4.0f} w6:{arch.w6:4.0f}")
    
    # Show similarities
    print("\nArchetype Similarities:")
    for i, arch1 in enumerate(QEC_ARCHETYPES):
        for j, arch2 in enumerate(QEC_ARCHETYPES):
            if i < j:
                sim = get_archetype_similarity(arch1, arch2)
                print(f"{arch1.name:12} vs {arch2.name:12} | {sim:.3f}")
    
    # Test custom archetype
    custom = create_custom_archetype("Test", [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5])
    print(f"\nCustom archetype: {custom.name}")
    print(f"Vector: {get_archetype_vector(custom)}")
    print(f"Weights: w1:{custom.w1:.1f} w2:{custom.w2:.1f} w3:{custom.w3:.1f} "
          f"w4:{custom.w4:.1f} w5:{custom.w5:.1f} w6:{custom.w6:.1f}")
