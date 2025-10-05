"""
Verify QEC Workspace Organization
Check that all files are in the correct locations and accessible
"""

import os
import sys
from pathlib import Path

def verify_workspace():
    """Verify the workspace organization is correct"""
    
    print("=== QEC Workspace Verification ===")
    
    # Define expected structure
    expected_structure = {
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
        ]
    }
    
    # Check main directories exist
    main_dirs = ['core', 'research', 'experiments', 'analysis', 'docs', 'logs', 'data']
    missing_dirs = []
    
    for dir_name in main_dirs:
        if not os.path.exists(dir_name):
            missing_dirs.append(dir_name)
        else:
            print(f"✅ {dir_name}/ directory exists")
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    
    # Check key files exist
    missing_files = []
    for dir_name, files in expected_structure.items():
        for file in files:
            file_path = Path(dir_name) / file
            if not file_path.exists():
                missing_files.append(str(file_path))
            else:
                print(f"✅ {file_path} exists")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    # Check subdirectories
    subdirs = {
        'research': ['hypotheses', 'simulators', 'archetypes'],
        'experiments': ['simulations', 'tournaments', 'human_ai'],
        'analysis': ['visualizations', 'reports', 'metrics'],
        'docs': ['presentations', 'summaries', 'research_papers'],
        'logs': ['game_logs', 'experiment_logs', 'analysis_logs'],
        'data': ['game_data', 'experiment_data', 'raw_data']
    }
    
    missing_subdirs = []
    for parent_dir, children in subdirs.items():
        for child in children:
            subdir_path = Path(parent_dir) / child
            if not subdir_path.exists():
                missing_subdirs.append(str(subdir_path))
            else:
                print(f"✅ {subdir_path}/ exists")
    
    if missing_subdirs:
        print(f"❌ Missing subdirectories: {missing_subdirs}")
        return False
    
    # Check key functionality
    print("\\n=== Functionality Check ===")
    
    # Test core imports
    try:
        sys.path.append('core')
        import main
        print("✅ Core game engine imports successfully")
    except Exception as e:
        print(f"❌ Core import failed: {e}")
        return False
    
    # Test research imports
    try:
        sys.path.append('research')
        import qec_archetypes
        print("✅ Research framework imports successfully")
    except Exception as e:
        print(f"❌ Research import failed: {e}")
        return False
    
    # Test experiments imports
    try:
        sys.path.append('experiments')
        import simulation_engine
        print("✅ Experiment framework imports successfully")
    except Exception as e:
        print(f"❌ Experiment import failed: {e}")
        return False
    
    # Check log directories have data
    log_dirs = [
        'logs/rock_solid_timer_logs',
        'logs/fixed_qec_research_logs',
        'logs/optimization_logs'
    ]
    
    log_data_found = False
    for log_dir in log_dirs:
        if os.path.exists(log_dir):
            files = os.listdir(log_dir)
            if files:
                print(f"✅ {log_dir} contains {len(files)} files")
                log_data_found = True
            else:
                print(f"⚠️  {log_dir} is empty")
    
    if not log_data_found:
        print("⚠️  No log data found - run some experiments first")
    
    # Check visualization files
    viz_dir = Path('analysis/visualizations')
    if viz_dir.exists():
        viz_files = list(viz_dir.glob('*.png'))
        if viz_files:
            print(f"✅ {len(viz_files)} visualization files found")
        else:
            print("⚠️  No visualization files found")
    
    print("\\n=== Workspace Verification Complete ===")
    print("✅ All core components are in place")
    print("✅ Directory structure is correct")
    print("✅ Key files are accessible")
    print("✅ Import paths are working")
    
    return True

if __name__ == "__main__":
    success = verify_workspace()
    if success:
        print("\\n🎯 QEC Workspace is properly organized and ready to use!")
    else:
        print("\\n❌ Workspace verification failed - check for missing files")
