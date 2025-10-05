"""
Export detailed CSV from rock-solid timer results
"""

import json
import csv
import os

def export_detailed_csv():
    """Export detailed CSV with time fields"""
    results_file = 'rock_solid_timer_logs/rock_solid_results.json'
    
    if not os.path.exists(results_file):
        print('Results file not found')
        return
    
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    # Create detailed CSV with time fields
    csv_file = 'rock_solid_timer_logs/detailed_time_analysis.csv'
    
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow([
            'game_id', 'turn_id', 'side', 'think_ms', 'time_left_ms', 
            'decision_quality', 'primary', 'forced', 'react', 'eval_before', 
            'eval_after', 'eval_drop', 'pressure_level', 'blunder', 
            'expected_think_ms', 'actual_vs_expected'
        ])
        
        # Write data
        total_records = 0
        for result in results:
            game_id = result['game_id']
            turn_logs = result.get('turn_logs', [])
            
            for log in turn_logs:
                writer.writerow([
                    game_id,
                    log['turn_id'],
                    log['side'],
                    log['think_ms'],
                    log['time_left_ms'],
                    log['decision_quality'],
                    log['primary'],
                    log['forced'],
                    log['react'],
                    log['eval_before'],
                    log['eval_after'],
                    log['eval_drop'],
                    log['pressure_level'],
                    log['blunder'],
                    log['expected_think_ms'],
                    log['actual_vs_expected']
                ])
                total_records += 1
    
    print(f'Detailed CSV exported to {csv_file}')
    print(f'Total records: {total_records}')
    print(f'Games: {len(results)}')

if __name__ == "__main__":
    export_detailed_csv()
