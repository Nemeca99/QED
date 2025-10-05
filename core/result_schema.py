"""
QEC Result Schema v1
Defines the contract for _result.json files with versioning
"""

import json
import hashlib
import subprocess
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class QECResultSchemaV1:
    """QEC Result Schema Version 1"""
    # Schema metadata
    schema_version: str = "v1"
    timestamp: str = ""
    git_sha: str = ""
    config_hash: str = ""
    
    # Game identification
    game_id: str = ""
    seed: int = 0
    
    # Game result
    result: str = ""  # "white_wins", "black_wins", "draw", "timeout", "move_limit"
    total_plies: int = 0
    
    # Move statistics
    forced_moves: int = 0
    reactive_moves: int = 0
    captures: int = 0
    promotions: int = 0
    
    # Entanglement statistics
    entanglement_breaks: int = 0
    entanglement_persists: int = 0
    
    # Performance metrics
    total_time_ms: int = 0
    avg_time_per_ply_ms: float = 0.0
    
    # Board state
    final_fen: str = ""
    final_entanglement_hash: str = ""
    
    # Validation
    schema_valid: bool = True
    validation_errors: list = None
    
    def __post_init__(self):
        """Initialize default values"""
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if not self.git_sha:
            self.git_sha = self._get_git_sha()
        if self.validation_errors is None:
            self.validation_errors = []
    
    def _get_git_sha(self) -> str:
        """Get current git SHA"""
        try:
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip()[:8]
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)
    
    def save_to_file(self, filepath: str) -> None:
        """Save result to file"""
        with open(filepath, 'w') as f:
            f.write(self.to_json())
    
    def validate_schema(self) -> bool:
        """Validate schema compliance"""
        errors = []
        
        # Required fields
        required_fields = [
            'schema_version', 'game_id', 'seed', 'result', 'total_plies',
            'forced_moves', 'reactive_moves', 'final_fen'
        ]
        
        for field in required_fields:
            if not hasattr(self, field) or getattr(self, field) is None:
                errors.append(f"Missing required field: {field}")
        
        # Validate field types
        if not isinstance(self.total_plies, int) or self.total_plies < 0:
            errors.append("total_plies must be non-negative integer")
        
        if not isinstance(self.forced_moves, int) or self.forced_moves < 0:
            errors.append("forced_moves must be non-negative integer")
        
        if not isinstance(self.reactive_moves, int) or self.reactive_moves < 0:
            errors.append("reactive_moves must be non-negative integer")
        
        if self.result not in ["white_wins", "black_wins", "draw", "timeout", "move_limit"]:
            errors.append(f"Invalid result: {self.result}")
        
        if not self.schema_version == "v1":
            errors.append(f"Invalid schema version: {self.schema_version}")
        
        self.validation_errors = errors
        self.schema_valid = len(errors) == 0
        
        return self.schema_valid
    
    def get_deterministic_hash(self) -> str:
        """Get deterministic hash for this result"""
        # Create hash from deterministic fields only
        deterministic_data = {
            'schema_version': self.schema_version,
            'game_id': self.game_id,
            'seed': self.seed,
            'result': self.result,
            'total_plies': self.total_plies,
            'forced_moves': self.forced_moves,
            'reactive_moves': self.reactive_moves,
            'final_fen': self.final_fen,
            'git_sha': self.git_sha,
            'config_hash': self.config_hash
        }
        
        data_str = json.dumps(deterministic_data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()[:8]

class QECResultValidator:
    """Validator for QEC result schemas"""
    
    def __init__(self):
        self.supported_versions = ["v1"]
    
    def validate_file(self, filepath: str) -> tuple[bool, list]:
        """Validate a result file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Check schema version
            schema_version = data.get('schema_version', 'unknown')
            if schema_version not in self.supported_versions:
                return False, [f"Unsupported schema version: {schema_version}"]
            
            # Create schema object and validate
            if schema_version == "v1":
                result = QECResultSchemaV1(**data)
                is_valid = result.validate_schema()
                return is_valid, result.validation_errors
            
            return False, ["Unknown schema version"]
            
        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON: {e}"]
        except Exception as e:
            return False, [f"Validation error: {e}"]
    
    def validate_directory(self, dirpath: str) -> Dict[str, Any]:
        """Validate all result files in a directory"""
        import os
        from pathlib import Path
        
        results = {
            'valid_files': 0,
            'invalid_files': 0,
            'total_files': 0,
            'errors': []
        }
        
        for filepath in Path(dirpath).rglob("*_result.json"):
            results['total_files'] += 1
            
            is_valid, errors = self.validate_file(str(filepath))
            if is_valid:
                results['valid_files'] += 1
            else:
                results['invalid_files'] += 1
                results['errors'].append({
                    'file': str(filepath),
                    'errors': errors
                })
        
        return results

def create_result_v1(game_id: str, seed: int, result: str, total_plies: int,
                    forced_moves: int = 0, reactive_moves: int = 0,
                    captures: int = 0, promotions: int = 0,
                    final_fen: str = "", config_hash: str = "") -> QECResultSchemaV1:
    """Create a v1 result schema"""
    return QECResultSchemaV1(
        game_id=game_id,
        seed=seed,
        result=result,
        total_plies=total_plies,
        forced_moves=forced_moves,
        reactive_moves=reactive_moves,
        captures=captures,
        promotions=promotions,
        final_fen=final_fen,
        config_hash=config_hash
    )

def validate_result_file(filepath: str) -> bool:
    """Validate a single result file"""
    validator = QECResultValidator()
    is_valid, errors = validator.validate_file(filepath)
    
    if not is_valid:
        print(f"Validation errors in {filepath}:")
        for error in errors:
            print(f"  - {error}")
    
    return is_valid

def main():
    """CLI for result schema validation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='QEC Result Schema Validator')
    parser.add_argument('file_or_dir', help='Result file or directory to validate')
    parser.add_argument('--version', action='store_true', help='Show schema version')
    
    args = parser.parse_args()
    
    if args.version:
        print("QEC Result Schema v1")
        return
    
    validator = QECResultValidator()
    
    if os.path.isfile(args.file_or_dir):
        # Single file
        is_valid, errors = validator.validate_file(args.file_or_dir)
        if is_valid:
            print(f"✅ {args.file_or_dir} is valid")
        else:
            print(f"❌ {args.file_or_dir} has errors:")
            for error in errors:
                print(f"  - {error}")
    else:
        # Directory
        results = validator.validate_directory(args.file_or_dir)
        print(f"Validation results for {args.file_or_dir}:")
        print(f"  Valid files: {results['valid_files']}")
        print(f"  Invalid files: {results['invalid_files']}")
        print(f"  Total files: {results['total_files']}")
        
        if results['errors']:
            print("\nErrors:")
            for error_info in results['errors']:
                print(f"  {error_info['file']}:")
                for error in error_info['errors']:
                    print(f"    - {error}")

if __name__ == "__main__":
    main()
