"""
Test QEC Time Management System
Demonstrate 3-minute turn timer with strategic implications
"""

import time
import random
from qec_time_manager import QECTimeManager, QECTimeAwareSimulator, TimePressure

def test_time_pressure_effects():
    """Test how time pressure affects decision quality"""
    print("=== Testing QEC Time Management ===")
    
    # Test time manager
    time_manager = QECTimeManager()
    
    print("\\n1. Testing Time Pressure Levels:")
    for pressure in TimePressure:
        print(f"  {pressure.value}: {time_manager.time_pressure_effects[pressure]:.1%} decision quality")
    
    print("\\n2. Testing Turn Sequence:")
    
    # Simulate a game with time management
    for move in range(1, 6):
        print(f"\\nMove {move}:")
        
        # White's turn
        white_quality = time_manager.start_turn("W")
        white_thinking = time_manager.get_optimal_thinking_time("W", 0.5, 0.6)
        time_manager.end_turn("W", white_thinking)
        
        white_status = time_manager.get_time_status("W")
        print(f"  White: {white_status['time_remaining']:.1f}s remaining, "
              f"{white_status['time_pressure']} pressure, "
              f"{white_status['decision_quality_factor']:.1%} quality")
        
        # Black's turn
        black_quality = time_manager.start_turn("B")
        black_thinking = time_manager.get_optimal_thinking_time("B", 0.5, 0.6)
        time_manager.end_turn("B", black_thinking)
        
        black_status = time_manager.get_time_status("B")
        print(f"  Black: {black_status['time_remaining']:.1f}s remaining, "
              f"{black_status['time_pressure']} pressure, "
              f"{black_status['decision_quality_factor']:.1%} quality")
    
    print("\\n3. Testing Strategic Time Management:")
    
    # Test different scenarios
    scenarios = [
        ("Rapid play", 5.0, 0.3, 0.4),
        ("Normal play", 30.0, 0.5, 0.6),
        ("Deep thinking", 60.0, 0.8, 0.9),
        ("Time trouble", 120.0, 0.9, 0.95)
    ]
    
    for scenario_name, thinking_time, move_complexity, position_complexity in scenarios:
        print(f"\\n  {scenario_name}:")
        
        # Reset time manager
        time_manager = QECTimeManager()
        
        # Simulate thinking time
        time_manager.start_turn("W")
        optimal_time = time_manager.get_optimal_thinking_time("W", move_complexity, position_complexity)
        time_manager.end_turn("W", thinking_time)
        
        status = time_manager.get_time_status("W")
        print(f"    Optimal time: {optimal_time:.1f}s")
        print(f"    Actual time: {thinking_time:.1f}s")
        print(f"    Time pressure: {status['time_pressure']}")
        print(f"    Decision quality: {status['decision_quality_factor']:.1%}")
        
        if thinking_time > optimal_time:
            print(f"    ⚠️  Giving opponent {thinking_time - optimal_time:.1f}s extra thinking time!")
        elif thinking_time < optimal_time * 0.5:
            print(f"    ⚡ Rushing move - may miss tactical opportunities!")

def test_time_aware_simulation():
    """Test full time-aware simulation"""
    print("\\n=== Testing Time-Aware Simulation ===")
    
    simulator = QECTimeAwareSimulator("time_test_logs")
    
    # Run a quick simulation
    result = simulator.simulate_time_aware_game(
        white_arch="Carlsen-like",
        black_arch="Tal-like",
        seed=42
    )
    
    print(f"Simulation complete!")
    print(f"Moves: {result['moves']}")
    print(f"Time summary: {result['time_summary']}")
    
    # Analyze time pressure events
    events = result['time_pressure_events']
    if events:
        print(f"\\nTime Pressure Analysis:")
        print(f"  Total events: {len(events)}")
        
        # Count pressure levels
        pressure_counts = {}
        for event in events:
            pressure = event['time_pressure']
            pressure_counts[pressure] = pressure_counts.get(pressure, 0) + 1
        
        for pressure, count in pressure_counts.items():
            print(f"  {pressure}: {count} events")
        
        # Show time advantage changes
        time_advantages = [event['time_advantage'] for event in events]
        if time_advantages:
            print(f"  Time advantage range: {min(time_advantages):.1f}s to {max(time_advantages):.1f}s")

def demonstrate_strategic_implications():
    """Demonstrate strategic implications of time management"""
    print("\\n=== Strategic Implications of Time Management ===")
    
    print("\\n1. First Move Advantage:")
    print("   - White gets to think first, but if they take too long...")
    print("   - Black gets extra thinking time to prepare response")
    print("   - Strategic trade-off: deliberation vs. tempo denial")
    
    print("\\n2. Time Pressure Effects:")
    print("   - Low pressure (>2min): 100% decision quality")
    print("   - Medium pressure (1-2min): 95% decision quality")
    print("   - High pressure (30s-1min): 85% decision quality")
    print("   - Critical pressure (<30s): 70% decision quality")
    
    print("\\n3. Strategic Time Management:")
    print("   - Fast play: Compresses opponent's thinking time")
    print("   - Slow play: Gives opponent more preparation time")
    print("   - Optimal balance: Position complexity vs. time remaining")
    
    print("\\n4. Entanglement + Time Pressure:")
    print("   - Forced moves must be chosen quickly")
    print("   - Reactive moves under time pressure")
    print("   - Complex positions require more thinking time")
    print("   - Time trouble amplifies tactical mistakes")

if __name__ == "__main__":
    test_time_pressure_effects()
    test_time_aware_simulation()
    demonstrate_strategic_implications()
