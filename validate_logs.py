"""
CLI Validation Tool for QEC Logs
Validates log directories and provides brief reports
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict, Counter
import csv

class QECLogValidator:
    """Validator for QEC log directories"""
    
    def __init__(self, logs_dir: str):
        self.logs_dir = Path(logs_dir)
        self.errors = []
        self.warnings = []
        self.stats = defaultdict(int)
        self.file_types = defaultdict(list)
        
    def validate_directory(self) -> bool:
        """Validate entire logs directory"""
        print(f"Validating logs directory: {self.logs_dir}")
        
        if not self.logs_dir.exists():
            self.errors.append(f"Logs directory does not exist: {self.logs_dir}")
            return False
        
        # Find all log files
        log_files = list(self.logs_dir.rglob("*.log"))
        pgn_files = list(self.logs_dir.rglob("*.pgn"))
        jsonl_files = list(self.logs_dir.rglob("*.jsonl"))
        json_files = list(self.logs_dir.rglob("*.json"))
        
        print(f"Found {len(log_files)} .log files, {len(pgn_files)} .pgn files, {len(jsonl_files)} .jsonl files, {len(json_files)} .json files")
        
        # Validate each file type
        self._validate_log_files(log_files)
        self._validate_pgn_files(pgn_files)
        self._validate_jsonl_files(jsonl_files)
        self._validate_json_files(json_files)
        
        # Check for missing files
        self._check_missing_files()
        
        # Generate report
        self._generate_report()
        
        return len(self.errors) == 0
    
    def _validate_log_files(self, log_files: List[Path]):
        """Validate .log files"""
        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for basic log structure
                if "Game started" not in content:
                    self.warnings.append(f"Log file {log_file} may not contain game start marker")
                
                if "Game ended" not in content and "Game finished" not in content:
                    self.warnings.append(f"Log file {log_file} may not contain game end marker")
                
                # Count log entries
                lines = content.split('\n')
                self.stats['log_lines'] += len(lines)
                self.stats['log_files'] += 1
                
                # Check for errors in logs
                error_lines = [line for line in lines if 'ERROR' in line or 'Exception' in line]
                if error_lines:
                    self.warnings.append(f"Log file {log_file} contains {len(error_lines)} error lines")
                
            except Exception as e:
                self.errors.append(f"Error reading log file {log_file}: {e}")
    
    def _validate_pgn_files(self, pgn_files: List[Path]):
        """Validate .pgn files"""
        for pgn_file in pgn_files:
            try:
                with open(pgn_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for PGN structure
                if "[Event" not in content:
                    self.warnings.append(f"PGN file {pgn_file} may not contain event header")
                
                if "[Result" not in content:
                    self.warnings.append(f"PGN file {pgn_file} may not contain result header")
                
                # Count moves
                moves = content.split()
                move_count = len([m for m in moves if m[0].isdigit()])
                self.stats['pgn_moves'] += move_count
                self.stats['pgn_files'] += 1
                
            except Exception as e:
                self.errors.append(f"Error reading PGN file {pgn_file}: {e}")
    
    def _validate_jsonl_files(self, jsonl_files: List[Path]):
        """Validate .jsonl files"""
        for jsonl_file in jsonl_files:
            try:
                with open(jsonl_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                valid_records = 0
                for i, line in enumerate(lines):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        record = json.loads(line)
                        valid_records += 1
                        
                        # Check for required fields based on format
                        if 'game_id' in record and 'ply' in record:
                            # Research log format
                            if 'side' not in record:
                                self.warnings.append(f"JSONL record {i+1} in {jsonl_file} missing 'side' field")
                        elif 'kind' in record and 'moved_id' in record:
                            # Move log format
                            if 'from' not in record or 'to' not in record:
                                self.warnings.append(f"JSONL record {i+1} in {jsonl_file} missing 'from' or 'to' field")
                        elif 'move' in record and 'player' in record:
                            # Human simulation format
                            if 'from' not in record or 'to' not in record:
                                self.warnings.append(f"JSONL record {i+1} in {jsonl_file} missing 'from' or 'to' field")
                        else:
                            self.warnings.append(f"JSONL record {i+1} in {jsonl_file} has unknown format")
                    
                    except json.JSONDecodeError as e:
                        self.errors.append(f"Invalid JSON in {jsonl_file} line {i+1}: {e}")
                
                self.stats['jsonl_records'] += valid_records
                self.stats['jsonl_files'] += 1
                
            except Exception as e:
                self.errors.append(f"Error reading JSONL file {jsonl_file}: {e}")
    
    def _validate_json_files(self, json_files: List[Path]):
        """Validate .json files"""
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check for common QEC result fields
                if isinstance(data, dict):
                    if 'result' in data:
                        self.stats['json_results'] += 1
                    if 'total_plies' in data:
                        self.stats['json_plies'] += data['total_plies']
                    if 'forced_moves' in data:
                        self.stats['json_forced_moves'] += data['forced_moves']
                    if 'reactive_moves' in data:
                        self.stats['json_reactive_moves'] += data['reactive_moves']
                
                self.stats['json_files'] += 1
                
            except Exception as e:
                self.errors.append(f"Error reading JSON file {json_file}: {e}")
    
    def _check_missing_files(self):
        """Check for missing expected files"""
        # Look for game directories
        game_dirs = [d for d in self.logs_dir.iterdir() if d.is_dir() and d.name.startswith('game_')]
        
        for game_dir in game_dirs:
            expected_files = ['game.log', 'game.pgn', 'game.jsonl', 'result.json']
            missing_files = []
            
            for expected_file in expected_files:
                if not (game_dir / expected_file).exists():
                    missing_files.append(expected_file)
            
            if missing_files:
                self.warnings.append(f"Game directory {game_dir.name} missing files: {missing_files}")
    
    def _generate_report(self):
        """Generate validation report"""
        print("\n=== QEC Log Validation Report ===")
        
        # File counts
        print(f"Log files: {self.stats['log_files']}")
        print(f"PGN files: {self.stats['pgn_files']}")
        print(f"JSONL files: {self.stats['jsonl_files']}")
        print(f"JSON files: {self.stats['json_files']}")
        
        # Content statistics
        if self.stats['log_lines'] > 0:
            print(f"Total log lines: {self.stats['log_lines']}")
        if self.stats['pgn_moves'] > 0:
            print(f"Total PGN moves: {self.stats['pgn_moves']}")
        if self.stats['jsonl_records'] > 0:
            print(f"Total JSONL records: {self.stats['jsonl_records']}")
        if self.stats['json_plies'] > 0:
            print(f"Total plies: {self.stats['json_plies']}")
        if self.stats['json_forced_moves'] > 0:
            print(f"Total forced moves: {self.stats['json_forced_moves']}")
        if self.stats['json_reactive_moves'] > 0:
            print(f"Total reactive moves: {self.stats['json_reactive_moves']}")
        
        # Errors and warnings
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        # Summary
        if not self.errors and not self.warnings:
            print("\n✅ All logs are valid!")
        elif not self.errors:
            print(f"\n⚠️  {len(self.warnings)} warnings found, but no errors")
        else:
            print(f"\n❌ {len(self.errors)} errors found")
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics"""
        return {
            'log_files': self.stats['log_files'],
            'pgn_files': self.stats['pgn_files'],
            'jsonl_files': self.stats['jsonl_files'],
            'json_files': self.stats['json_files'],
            'log_lines': self.stats['log_lines'],
            'pgn_moves': self.stats['pgn_moves'],
            'jsonl_records': self.stats['jsonl_records'],
            'json_plies': self.stats['json_plies'],
            'json_forced_moves': self.stats['json_forced_moves'],
            'json_reactive_moves': self.stats['json_reactive_moves'],
            'errors': len(self.errors),
            'warnings': len(self.warnings)
        }

def main():
    """Main validation CLI"""
    parser = argparse.ArgumentParser(description='QEC Log Validator')
    parser.add_argument('logs_dir', help='Logs directory to validate')
    parser.add_argument('--summary', action='store_true', help='Show summary statistics only')
    parser.add_argument('--output', type=str, help='Save report to file')
    
    args = parser.parse_args()
    
    validator = QECLogValidator(args.logs_dir)
    success = validator.validate_directory()
    
    if args.summary:
        stats = validator.get_summary_stats()
        print("Summary statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write("QEC Log Validation Report\n")
            f.write("=" * 30 + "\n\n")
            f.write(f"Logs directory: {args.logs_dir}\n")
            f.write(f"Validation successful: {success}\n")
            f.write(f"Errors: {len(validator.errors)}\n")
            f.write(f"Warnings: {len(validator.warnings)}\n")
            
            if validator.errors:
                f.write("\nErrors:\n")
                for error in validator.errors:
                    f.write(f"  - {error}\n")
            
            if validator.warnings:
                f.write("\nWarnings:\n")
                for warning in validator.warnings:
                    f.write(f"  - {warning}\n")
        
        print(f"Report saved to {args.output}")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
