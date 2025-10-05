"""
Configuration Manager for QEC
Handles TOML configuration loading and validation
"""

import os
import toml
import json
import hashlib
import subprocess
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class QECConfig:
    """QEC configuration container"""
    max_plies: int = 200
    move_cap: int = 100
    timeout_seconds: int = 300
    seed_base: int = 42
    
    # Logging
    enable_detailed_logs: bool = True
    enable_fen_logging: bool = True
    enable_entanglement_logging: bool = True
    log_level: str = "INFO"
    save_pgn: bool = True
    save_jsonl: bool = True
    save_summary: bool = True
    
    # AI Policies
    default_white_policy: str = "minimax"
    default_black_policy: str = "minimax"
    minimax_depth: int = 3
    quiescence_depth: int = 2
    enable_killer_moves: bool = True
    enable_history_heuristic: bool = True
    
    # Performance
    enable_caching: bool = True
    cache_size_mb: int = 100
    enable_fast_evaluation: bool = True
    fast_eval_skip_positional_every: int = 3
    fast_eval_skip_entanglement_every: int = 5
    fast_eval_skip_activity_every: int = 2
    material_only_threshold: int = 50
    
    # Research
    default_hypothesis_tests: List[str] = None
    default_archetype_pairs: List[str] = None
    default_map_entropy_levels: List[float] = None
    default_replicates: int = 100
    enable_power_analysis: bool = True
    effect_size_threshold: float = 0.05
    alpha_level: float = 0.05
    power_level: float = 0.8
    
    # Output
    results_directory: str = "results"
    logs_directory: str = "logs"
    plots_directory: str = "plots"
    enable_csv_export: bool = True
    enable_json_export: bool = True
    enable_plot_generation: bool = True
    plot_format: str = "png"
    plot_dpi: int = 300
    
    # Validation
    enable_schema_validation: bool = True
    strict_mode: bool = False
    ignore_malformed_logs: bool = True
    validate_entanglement_maps: bool = True
    validate_move_sequences: bool = True
    
    # CI/CD
    enable_github_actions: bool = True
    run_unit_tests: bool = True
    run_smoke_tests: bool = True
    run_performance_tests: bool = True
    run_correctness_tests: bool = True
    generate_artifacts: bool = True
    
    def __post_init__(self):
        """Initialize default lists"""
        if self.default_hypothesis_tests is None:
            self.default_hypothesis_tests = ["H1", "H2", "H3", "H4", "H5", "H6"]
        if self.default_archetype_pairs is None:
            self.default_archetype_pairs = ["aggressive", "defensive", "balanced"]
        if self.default_map_entropy_levels is None:
            self.default_map_entropy_levels = [0.2, 0.5, 0.8]

class QECConfigManager:
    """Configuration manager for QEC"""
    
    def __init__(self, config_file: str = "config/qec_config.toml"):
        self.config_file = config_file
        self.config = QECConfig()
        self.git_sha = self._get_git_sha()
        self.config_hash = None
    
    def _get_git_sha(self) -> str:
        """Get current git SHA"""
        try:
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip()[:8]
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "unknown"
    
    def load_config(self) -> QECConfig:
        """Load configuration from TOML file"""
        if not os.path.exists(self.config_file):
            print(f"Config file {self.config_file} not found, using defaults")
            return self.config
        
        try:
            with open(self.config_file, 'r') as f:
                config_data = toml.load(f)
            
            # Update config with loaded data
            self._update_config_from_dict(config_data)
            
            # Calculate config hash
            self.config_hash = self._calculate_config_hash()
            
            print(f"Loaded configuration from {self.config_file}")
            return self.config
            
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.config
    
    def _update_config_from_dict(self, config_data: Dict[str, Any]):
        """Update config from dictionary"""
        # General settings
        if 'general' in config_data:
            general = config_data['general']
            self.config.max_plies = general.get('max_plies', self.config.max_plies)
            self.config.move_cap = general.get('move_cap', self.config.move_cap)
            self.config.timeout_seconds = general.get('timeout_seconds', self.config.timeout_seconds)
            self.config.seed_base = general.get('seed_base', self.config.seed_base)
        
        # Logging settings
        if 'logging' in config_data:
            logging = config_data['logging']
            self.config.enable_detailed_logs = logging.get('enable_detailed_logs', self.config.enable_detailed_logs)
            self.config.enable_fen_logging = logging.get('enable_fen_logging', self.config.enable_fen_logging)
            self.config.enable_entanglement_logging = logging.get('enable_entanglement_logging', self.config.enable_entanglement_logging)
            self.config.log_level = logging.get('log_level', self.config.log_level)
            self.config.save_pgn = logging.get('save_pgn', self.config.save_pgn)
            self.config.save_jsonl = logging.get('save_jsonl', self.config.save_jsonl)
            self.config.save_summary = logging.get('save_summary', self.config.save_summary)
        
        # AI policy settings
        if 'ai_policies' in config_data:
            ai_policies = config_data['ai_policies']
            self.config.default_white_policy = ai_policies.get('default_white_policy', self.config.default_white_policy)
            self.config.default_black_policy = ai_policies.get('default_black_policy', self.config.default_black_policy)
            self.config.minimax_depth = ai_policies.get('minimax_depth', self.config.minimax_depth)
            self.config.quiescence_depth = ai_policies.get('quiescence_depth', self.config.quiescence_depth)
            self.config.enable_killer_moves = ai_policies.get('enable_killer_moves', self.config.enable_killer_moves)
            self.config.enable_history_heuristic = ai_policies.get('enable_history_heuristic', self.config.enable_history_heuristic)
        
        # Performance settings
        if 'performance' in config_data:
            performance = config_data['performance']
            self.config.enable_caching = performance.get('enable_caching', self.config.enable_caching)
            self.config.cache_size_mb = performance.get('cache_size_mb', self.config.cache_size_mb)
            self.config.enable_fast_evaluation = performance.get('enable_fast_evaluation', self.config.enable_fast_evaluation)
            self.config.fast_eval_skip_positional_every = performance.get('fast_eval_skip_positional_every', self.config.fast_eval_skip_positional_every)
            self.config.fast_eval_skip_entanglement_every = performance.get('fast_eval_skip_entanglement_every', self.config.fast_eval_skip_entanglement_every)
            self.config.fast_eval_skip_activity_every = performance.get('fast_eval_skip_activity_every', self.config.fast_eval_skip_activity_every)
            self.config.material_only_threshold = performance.get('material_only_threshold', self.config.material_only_threshold)
        
        # Research settings
        if 'research' in config_data:
            research = config_data['research']
            self.config.default_hypothesis_tests = research.get('default_hypothesis_tests', self.config.default_hypothesis_tests)
            self.config.default_archetype_pairs = research.get('default_archetype_pairs', self.config.default_archetype_pairs)
            self.config.default_map_entropy_levels = research.get('default_map_entropy_levels', self.config.default_map_entropy_levels)
            self.config.default_replicates = research.get('default_replicates', self.config.default_replicates)
            self.config.enable_power_analysis = research.get('enable_power_analysis', self.config.enable_power_analysis)
            self.config.effect_size_threshold = research.get('effect_size_threshold', self.config.effect_size_threshold)
            self.config.alpha_level = research.get('alpha_level', self.config.alpha_level)
            self.config.power_level = research.get('power_level', self.config.power_level)
        
        # Output settings
        if 'output' in config_data:
            output = config_data['output']
            self.config.results_directory = output.get('results_directory', self.config.results_directory)
            self.config.logs_directory = output.get('logs_directory', self.config.logs_directory)
            self.config.plots_directory = output.get('plots_directory', self.config.plots_directory)
            self.config.enable_csv_export = output.get('enable_csv_export', self.config.enable_csv_export)
            self.config.enable_json_export = output.get('enable_json_export', self.config.enable_json_export)
            self.config.enable_plot_generation = output.get('enable_plot_generation', self.config.enable_plot_generation)
            self.config.plot_format = output.get('plot_format', self.config.plot_format)
            self.config.plot_dpi = output.get('plot_dpi', self.config.plot_dpi)
        
        # Validation settings
        if 'validation' in config_data:
            validation = config_data['validation']
            self.config.enable_schema_validation = validation.get('enable_schema_validation', self.config.enable_schema_validation)
            self.config.strict_mode = validation.get('strict_mode', self.config.strict_mode)
            self.config.ignore_malformed_logs = validation.get('ignore_malformed_logs', self.config.ignore_malformed_logs)
            self.config.validate_entanglement_maps = validation.get('validate_entanglement_maps', self.config.validate_entanglement_maps)
            self.config.validate_move_sequences = validation.get('validate_move_sequences', self.config.validate_move_sequences)
        
        # CI/CD settings
        if 'ci_cd' in config_data:
            ci_cd = config_data['ci_cd']
            self.config.enable_github_actions = ci_cd.get('enable_github_actions', self.config.enable_github_actions)
            self.config.run_unit_tests = ci_cd.get('run_unit_tests', self.config.run_unit_tests)
            self.config.run_smoke_tests = ci_cd.get('run_smoke_tests', self.config.run_smoke_tests)
            self.config.run_performance_tests = ci_cd.get('run_performance_tests', self.config.run_performance_tests)
            self.config.run_correctness_tests = ci_cd.get('run_correctness_tests', self.config.run_correctness_tests)
            self.config.generate_artifacts = ci_cd.get('generate_artifacts', self.config.generate_artifacts)
    
    def _calculate_config_hash(self) -> str:
        """Calculate hash of current configuration"""
        config_dict = asdict(self.config)
        config_str = json.dumps(config_dict, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()[:8]
    
    def get_deterministic_artifacts(self) -> Dict[str, Any]:
        """Get deterministic artifacts for logging"""
        return {
            'git_sha': self.git_sha,
            'config_hash': self.config_hash,
            'config_file': self.config_file,
            'timestamp': self._get_timestamp(),
            'version': self._get_version()
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _get_version(self) -> str:
        """Get QEC version"""
        return "1.0.0"  # This could be read from a version file
    
    def save_config(self, output_file: str = None):
        """Save current configuration to file"""
        if output_file is None:
            output_file = self.config_file
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Convert config to dictionary
        config_dict = asdict(self.config)
        
        # Save as TOML
        with open(output_file, 'w') as f:
            toml.dump(config_dict, f)
        
        print(f"Configuration saved to {output_file}")
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return any errors"""
        errors = []
        
        # Validate numeric ranges
        if self.config.max_plies < 1:
            errors.append("max_plies must be >= 1")
        if self.config.move_cap < 1:
            errors.append("move_cap must be >= 1")
        if self.config.timeout_seconds < 1:
            errors.append("timeout_seconds must be >= 1")
        if self.config.seed_base < 0:
            errors.append("seed_base must be >= 0")
        
        # Validate AI policy settings
        if self.config.minimax_depth < 1:
            errors.append("minimax_depth must be >= 1")
        if self.config.quiescence_depth < 1:
            errors.append("quiescence_depth must be >= 1")
        
        # Validate performance settings
        if self.config.cache_size_mb < 1:
            errors.append("cache_size_mb must be >= 1")
        if self.config.fast_eval_skip_positional_every < 1:
            errors.append("fast_eval_skip_positional_every must be >= 1")
        if self.config.fast_eval_skip_entanglement_every < 1:
            errors.append("fast_eval_skip_entanglement_every must be >= 1")
        if self.config.fast_eval_skip_activity_every < 1:
            errors.append("fast_eval_skip_activity_every must be >= 1")
        if self.config.material_only_threshold < 1:
            errors.append("material_only_threshold must be >= 1")
        
        # Validate research settings
        if self.config.default_replicates < 1:
            errors.append("default_replicates must be >= 1")
        if not (0 < self.config.effect_size_threshold < 1):
            errors.append("effect_size_threshold must be between 0 and 1")
        if not (0 < self.config.alpha_level < 1):
            errors.append("alpha_level must be between 0 and 1")
        if not (0 < self.config.power_level < 1):
            errors.append("power_level must be between 0 and 1")
        
        return errors

def load_qec_config(config_file: str = "config/qec_config.toml") -> QECConfig:
    """Load QEC configuration from file"""
    manager = QECConfigManager(config_file)
    return manager.load_config()

def get_deterministic_artifacts(config_file: str = "config/qec_config.toml") -> Dict[str, Any]:
    """Get deterministic artifacts for logging"""
    manager = QECConfigManager(config_file)
    manager.load_config()
    return manager.get_deterministic_artifacts()

def validate_qec_config(config_file: str = "config/qec_config.toml") -> bool:
    """Validate QEC configuration"""
    manager = QECConfigManager(config_file)
    manager.load_config()
    errors = manager.validate_config()
    
    if errors:
        print("Configuration validation errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("Configuration is valid")
        return True

def main():
    """Main configuration manager CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description='QEC Configuration Manager')
    parser.add_argument('--config', type=str, default='config/qec_config.toml', help='Config file path')
    parser.add_argument('--validate', action='store_true', help='Validate configuration')
    parser.add_argument('--save', type=str, help='Save configuration to file')
    parser.add_argument('--artifacts', action='store_true', help='Show deterministic artifacts')
    
    args = parser.parse_args()
    
    if args.validate:
        success = validate_qec_config(args.config)
        return 0 if success else 1
    
    if args.save:
        manager = QECConfigManager(args.config)
        manager.load_config()
        manager.save_config(args.save)
        return 0
    
    if args.artifacts:
        artifacts = get_deterministic_artifacts(args.config)
        print("Deterministic artifacts:")
        for key, value in artifacts.items():
            print(f"  {key}: {value}")
        return 0
    
    # Default: load and show config
    config = load_qec_config(args.config)
    print(f"Loaded configuration from {args.config}")
    print(f"Max plies: {config.max_plies}")
    print(f"Move cap: {config.move_cap}")
    print(f"Seed base: {config.seed_base}")
    print(f"Log level: {config.log_level}")
    print(f"Results directory: {config.results_directory}")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
