"""
QEC Schema Validation
Ensures all game logs follow consistent schema
"""

import os
import json
import sys
from typing import Dict, List, Any, Optional

class QECSchemaValidator:
    """Validates QEC log schemas for consistency"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_game_log(self, log_file: str) -> bool:
        """Validate a single game log file"""
        if not os.path.exists(log_file):
            self.errors.append(f"Log file not found: {log_file}")
            return False
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    self.errors.append(f"Empty log file: {log_file}")
                    return False
                
                # Try to parse as JSON if it looks like JSON
                if content.startswith('{'):
                    try:
                        data = json.loads(content)
                        return self._validate_json_schema(data, log_file)
                    except json.JSONDecodeError:
                        # Not JSON, treat as text log
                        return self._validate_text_log(content, log_file)
                else:
                    # Text log
                    return self._validate_text_log(content, log_file)
        
        except Exception as e:
            self.errors.append(f"Error reading {log_file}: {e}")
            return False
    
    def validate_jsonl_file(self, jsonl_file: str) -> bool:
        """Validate a JSONL file"""
        if not os.path.exists(jsonl_file):
            self.errors.append(f"JSONL file not found: {jsonl_file}")
            return False
        
        try:
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            if not lines:
                self.errors.append(f"Empty JSONL file: {jsonl_file}")
                return False
            
            # Validate each line
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                    if not self._validate_jsonl_record(data, jsonl_file, i+1):
                        return False
                except json.JSONDecodeError as e:
                    self.errors.append(f"Invalid JSON on line {i+1} of {jsonl_file}: {e}")
                    return False
            
            return True
        
        except Exception as e:
            self.errors.append(f"Error reading {jsonl_file}: {e}")
            return False
    
    def _validate_json_schema(self, data: Dict[str, Any], filename: str) -> bool:
        """Validate JSON schema for game results"""
        required_fields = [
            'game_id', 'result', 'total_plies', 'white_player', 'black_player',
            'start_fen', 'seed', 'forced_moves', 'reactive_moves', 'captures'
        ]
        
        for field in required_fields:
            if field not in data:
                self.errors.append(f"Missing required field '{field}' in {filename}")
                return False
        
        # Validate data types
        if not isinstance(data['total_plies'], int):
            self.errors.append(f"total_plies must be int in {filename}")
            return False
        
        if not isinstance(data['forced_moves'], int):
            self.errors.append(f"forced_moves must be int in {filename}")
            return False
        
        if not isinstance(data['reactive_moves'], int):
            self.errors.append(f"reactive_moves must be int in {filename}")
            return False
        
        return True
    
    def _validate_jsonl_record(self, data: Dict[str, Any], filename: str, line_num: int) -> bool:
        """Validate a single JSONL record"""
        # Handle different JSONL formats used in QEC
        
        # Format 1: Research logs (game_id, ply, side, primary, etc.)
        if 'game_id' in data and 'ply' in data:
            required_fields = ['game_id', 'ply', 'side', 'primary']
            for field in required_fields:
                if field not in data:
                    self.errors.append(f"Missing required field '{field}' in {filename} line {line_num}")
                    return False
            
            if data['side'] not in ['W', 'B']:
                self.errors.append(f"side must be 'W' or 'B' in {filename} line {line_num}")
                return False
            
            if not isinstance(data['ply'], int):
                self.errors.append(f"ply must be int in {filename} line {line_num}")
                return False
        
        # Format 2: Move logs (kind, moved_id, side, from, to, fen)
        elif 'kind' in data and 'moved_id' in data:
            required_fields = ['kind', 'moved_id', 'side', 'from', 'to', 'fen']
            for field in required_fields:
                if field not in data:
                    self.errors.append(f"Missing required field '{field}' in {filename} line {line_num}")
                    return False
            
            if data['side'] not in ['W', 'B']:
                self.errors.append(f"side must be 'W' or 'B' in {filename} line {line_num}")
                return False
            
            if data['kind'] not in ['primary', 'forced', 'react', 'MOVE', 'FORCED', 'REACT']:
                self.errors.append(f"kind must be valid move type in {filename} line {line_num}")
                return False
        
        # Format 3: Unknown format
        else:
            self.errors.append(f"Unknown JSONL format in {filename} line {line_num}")
            return False
        
        return True
    
    def _validate_text_log(self, content: str, filename: str) -> bool:
        """Validate text log format"""
        lines = content.split('\n')
        
        # Check for basic log structure
        if len(lines) < 3:
            self.warnings.append(f"Very short log file: {filename}")
        
        # Look for key log patterns
        has_move_log = any('MOVE:' in line for line in lines)
        has_result = any('Result:' in line or 'Checkmate:' in line for line in lines)
        
        if not has_move_log:
            self.warnings.append(f"No move logs found in {filename}")
        
        if not has_result:
            self.warnings.append(f"No result found in {filename}")
        
        return True
    
    def validate_directory(self, log_dir: str) -> bool:
        """Validate all logs in a directory"""
        if not os.path.exists(log_dir):
            self.errors.append(f"Log directory not found: {log_dir}")
            return False
        
        print(f"Validating logs in: {log_dir}")
        
        # Find all log files
        log_files = []
        jsonl_files = []
        
        for root, dirs, files in os.walk(log_dir):
            for file in files:
                if file.endswith('.log'):
                    log_files.append(os.path.join(root, file))
                elif file.endswith('.jsonl'):
                    jsonl_files.append(os.path.join(root, file))
        
        print(f"Found {len(log_files)} .log files and {len(jsonl_files)} .jsonl files")
        
        # Validate log files
        log_valid = True
        for log_file in log_files:
            if not self.validate_game_log(log_file):
                log_valid = False
        
        # Validate JSONL files
        jsonl_valid = True
        for jsonl_file in jsonl_files:
            if not self.validate_jsonl_file(jsonl_file):
                jsonl_valid = False
        
        return log_valid and jsonl_valid
    
    def print_results(self):
        """Print validation results"""
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")
        
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ All logs are valid!")
        elif not self.errors:
            print(f"\n✅ All logs are valid (with {len(self.warnings)} warnings)")
        else:
            print(f"\n❌ Validation failed with {len(self.errors)} errors")

def main():
    """Main validation function"""
    if len(sys.argv) != 2:
        print("Usage: python validate_schema.py <log_directory>")
        sys.exit(1)
    
    log_dir = sys.argv[1]
    validator = QECSchemaValidator()
    
    success = validator.validate_directory(log_dir)
    validator.print_results()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
