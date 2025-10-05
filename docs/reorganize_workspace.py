"""
QEC Workspace Reorganization Script
Clean up and organize the workspace into logical directories
"""

import os
import shutil
from pathlib import Path

def reorganize_workspace():
    """Reorganize the QEC workspace into logical directories"""
    
    # Define directory structure
    structure = {
        'core': [
            'main.py',
            'qec_v1_rules.txt', 
            'qec_v1_math.txt',
            'requirements.txt',
            'README.md'
        ],
        'research': [
            'qec_archetypes.py',
            'qec_evaluation.py', 
            'qec_research_simulator.py',
            'qec_hypotheses.py',
            'qec_hypothesis_tester.py',
            'run_qec_research.py',
            'README_QEC_RESEARCH.md'
        ],
        'experiments': [
            'simulation_engine.py',
            'comprehensive_simulator.py',
            'human_simulation.py',
            'player_database.py',
            'opening_book.py',
            'tournament_system.py',
            'run_simulation.py',
            'quick_test.py',
            'README_HUMAN_SIMULATION.md'
        ],
        'analysis': [
            'qec_analyzer.py',
            'analyze_qec_data.py',
            'analyze_qec_results.py',
            'qec_visual_analyzer.py',
            'create_research_presentation.py',
            'qec_analysis_summary.json'
        ],
        'docs': [
            'QEC_COMPLETE_RESEARCH_FRAMEWORK.md',
            'QEC_PATTERN_ANALYSIS.md',
            'QEC_RESEARCH_SUMMARY.md',
            'QEC_Research_Presentation.pdf',
            'QEC_TIME_MANAGEMENT_ANALYSIS.md',
            'QEC_ROCK_SOLID_TIMER_SUMMARY.md',
            'QEC_FINAL_IMPLEMENTATION_SUMMARY.md'
        ],
        'logs': [
            # Move all log directories
            'comprehensive_logs',
            'enhanced_qec_time_logs', 
            'fixed_qec_research_logs',
            'hypothesis_test_logs',
            'large_experiment_logs',
            'optimization_logs',
            'qec_research_logs',
            'rock_solid_timer_logs',
            'simulation_logs',
            'simulation_results',
            'test_experiment_logs',
            'time_test_logs',
            'timer_hypotheses_logs'
        ],
        'data': [
            'out',
            'sample_mapping.json',
            'rawchat.txt'
        ]
    }
    
    # Create subdirectories
    subdirs = {
        'research': ['hypotheses', 'simulators', 'archetypes'],
        'experiments': ['simulations', 'tournaments', 'human_ai'],
        'analysis': ['visualizations', 'reports', 'metrics'],
        'docs': ['presentations', 'summaries', 'research_papers'],
        'logs': ['game_logs', 'experiment_logs', 'analysis_logs'],
        'data': ['game_data', 'experiment_data', 'raw_data']
    }
    
    print("=== QEC Workspace Reorganization ===")
    
    # Create subdirectories
    for parent_dir, children in subdirs.items():
        for child in children:
            path = Path(parent_dir) / child
            path.mkdir(parents=True, exist_ok=True)
            print(f"Created: {path}")
    
    # Move files to appropriate directories
    moved_count = 0
    for target_dir, files in structure.items():
        for file in files:
            if os.path.exists(file):
                target_path = Path(target_dir) / file
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    shutil.move(file, target_path)
                    print(f"Moved: {file} -> {target_path}")
                    moved_count += 1
                except Exception as e:
                    print(f"Error moving {file}: {e}")
            else:
                print(f"File not found: {file}")
    
    # Move remaining Python files to appropriate directories
    remaining_files = {
        'qec_time_manager.py': 'research/simulators/',
        'qec_rock_solid_timer.py': 'research/simulators/',
        'qec_timer_hypotheses.py': 'research/hypotheses/',
        'qec_optimizer.py': 'experiments/simulations/',
        'enhanced_qec_with_time.py': 'experiments/simulations/',
        'fixed_qec_research_simulator.py': 'research/simulators/',
        'debug_forced_moves.py': 'experiments/simulations/',
        'test_time_management.py': 'experiments/simulations/',
        'export_detailed_csv.py': 'analysis/metrics/',
        'reorganize_workspace.py': 'docs/'
    }
    
    for file, target in remaining_files.items():
        if os.path.exists(file):
            target_path = Path(target) / file
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                shutil.move(file, target_path)
                print(f"Moved: {file} -> {target_path}")
                moved_count += 1
            except Exception as e:
                print(f"Error moving {file}: {e}")
    
    # Move visualization files
    viz_files = ['qec_comprehensive_analysis.png', 'qec_correlation_matrix.png', 
                 'qec_hypothesis_h5_analysis.png', 'qec_hypothesis_h7_analysis.png']
    
    for file in viz_files:
        if os.path.exists(file):
            target_path = Path('analysis/visualizations') / file
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                shutil.move(file, target_path)
                print(f"Moved: {file} -> {target_path}")
                moved_count += 1
            except Exception as e:
                print(f"Error moving {file}: {e}")
    
    # Clean up empty directories
    for item in os.listdir('.'):
        if os.path.isdir(item) and item not in ['core', 'research', 'experiments', 'analysis', 'docs', 'logs', 'data', '__pycache__', '.specstory', '.venv']:
            try:
                if not os.listdir(item):  # Empty directory
                    os.rmdir(item)
                    print(f"Removed empty directory: {item}")
                else:
                    print(f"Directory not empty, keeping: {item}")
            except Exception as e:
                print(f"Error removing {item}: {e}")
    
    print(f"\\n=== Reorganization Complete ===")
    print(f"Files moved: {moved_count}")
    print(f"\\nNew directory structure:")
    print("core/ - Core game engine and rules")
    print("research/ - Research framework and hypotheses")
    print("experiments/ - Simulation experiments and AI")
    print("analysis/ - Data analysis and visualizations")
    print("docs/ - Documentation and presentations")
    print("logs/ - All experiment logs and data")
    print("data/ - Game data and raw files")

if __name__ == "__main__":
    reorganize_workspace()
