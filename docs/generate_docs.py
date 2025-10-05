"""
QEC Documentation Generator
Generate API documentation with pdoc
"""

import sys
import os
import subprocess
from pathlib import Path

def generate_api_docs():
    """Generate API documentation using pdoc"""
    print("Generating QEC API documentation...")
    
    # Create docs directory
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    # Generate documentation
    try:
        # Generate HTML documentation
        result = subprocess.run([
            "python", "-m", "pdoc", 
            "--html", 
            "--output-dir", str(docs_dir),
            "--template-dir", "docs/templates",
            "core"
        ], check=True, capture_output=True, text=True)
        
        print("✅ API documentation generated successfully")
        print(f"Documentation saved to: {docs_dir}")
        
        # Generate markdown documentation
        result = subprocess.run([
            "python", "-m", "pdoc", 
            "--pdf",
            "--output-dir", str(docs_dir),
            "core"
        ], check=True, capture_output=True, text=True)
        
        print("✅ PDF documentation generated successfully")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating documentation: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False
    
    return True

def generate_readme():
    """Generate comprehensive README with API examples"""
    readme_content = """# QEC (Quantum Entanglement Chess)

A novel chess variant with quantum mechanics, featuring entanglement between pieces and forced responses.

## Quick Start

```python
from qec import Game, simulate_match, run_sweep

# Simulate a single match
result = simulate_match(white_policy="minimax", black_policy="minimax", seed=42)
print(f"Result: {result['result']}")
print(f"Total plies: {result['total_plies']}")

# Run a parameter sweep
output_file = run_sweep(num_archetypes=10, num_games_per_config=3)
print(f"Results saved to: {output_file}")
```

## Installation

```bash
pip install qec
```

## CLI Usage

```bash
# Simulate a game
qec-simulate --white minimax --black minimax --seed 42

# Run research experiments
qec-research --archetypes 10 --games_per_config 3

# Validate results
qec-validate --schema logs/
```

## Docker Usage

```bash
# Build and run
docker-compose up qec

# Run benchmarks
docker-compose --profile benchmark up qec-benchmark

# Run fuzz tests
docker-compose --profile fuzz up qec-fuzz
```

## API Reference

### Core Classes

- `Game`: Main QEC game engine
- `Board`: Chess board with entanglement support
- `Piece`: Chess pieces with quantum properties
- `Square`: Board positions

### Functions

- `simulate_match()`: Simulate a single game
- `run_sweep()`: Run parameter sweep experiments
- `validate_result_file()`: Validate result schemas

## Examples

See `examples/` directory for:
- Basic simulation configuration
- Expected output formats
- Reproducible experiments

## Research

QEC includes comprehensive research tools:
- Parameter sweep experiments
- Archetype grid search
- Ablation matrix testing
- Performance benchmarking

## Contributing

1. Fork the repository
2. Create a feature branch
3. Run tests: `python test_entanglement_invariants_simple.py`
4. Run benchmarks: `python bench/benchmark_suite.py`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
"""
    
    with open("README.md", "w") as f:
        f.write(readme_content)
    
    print("✅ README.md updated")

def main():
    """Main documentation generator"""
    import argparse
    
    parser = argparse.ArgumentParser(description='QEC Documentation Generator')
    parser.add_argument('--api', action='store_true', help='Generate API documentation')
    parser.add_argument('--readme', action='store_true', help='Generate README')
    parser.add_argument('--all', action='store_true', help='Generate all documentation')
    
    args = parser.parse_args()
    
    if args.all or args.api:
        generate_api_docs()
    
    if args.all or args.readme:
        generate_readme()
    
    if not any([args.api, args.readme, args.all]):
        print("Please specify --api, --readme, or --all")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
