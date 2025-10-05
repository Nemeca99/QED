"""
QEC Benchmark Suite
Performance benchmarks for move generation, evaluation, and full games
"""

import sys
import os
import time
import csv
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import statistics

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))

import main as qec_main
from move_generation_cache import get_move_cache, get_cache_stats
from fast_evaluation import get_fast_evaluator, get_evaluation_stats
from performance_optimizations import get_performance_cache, get_cache_stats as get_perf_cache_stats

@dataclass
class BenchmarkResult:
    """Result of a benchmark test"""
    test_name: str
    iterations: int
    total_time_ms: float
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    std_dev_ms: float
    throughput: float  # operations per second

class QECBenchmarkSuite:
    """Comprehensive benchmark suite for QEC"""
    
    def __init__(self, output_dir: str = "bench"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results = []
        self.thresholds = {
            'move_generation_ms': 1.0,
            'evaluation_ms': 0.5,
            'full_game_ms': 1000.0,
            'cache_hit_rate': 0.8
        }
    
    def benchmark_move_generation(self, iterations: int = 1000) -> BenchmarkResult:
        """Benchmark move generation performance"""
        print(f"Benchmarking move generation ({iterations} iterations)...")
        
        times = []
        cache = get_move_cache()
        
        for i in range(iterations):
            game = qec_main.Game(seed=42 + i)
            
            start_time = time.perf_counter()
            legal_moves = game.board.legal_moves()
            end_time = time.perf_counter()
            
            times.append((end_time - start_time) * 1000)  # Convert to ms
        
        return self._calculate_benchmark_result("move_generation", iterations, times)
    
    def benchmark_evaluation(self, iterations: int = 1000) -> BenchmarkResult:
        """Benchmark position evaluation performance"""
        print(f"Benchmarking evaluation ({iterations} iterations)...")
        
        times = []
        evaluator = get_fast_evaluator()
        
        for i in range(iterations):
            game = qec_main.Game(seed=42 + i)
            
            start_time = time.perf_counter()
            eval_score = evaluator.evaluate_fast(game.board, 'W', i)
            end_time = time.perf_counter()
            
            times.append((end_time - start_time) * 1000)  # Convert to ms
        
        return self._calculate_benchmark_result("evaluation", iterations, times)
    
    def benchmark_full_game(self, iterations: int = 100) -> BenchmarkResult:
        """Benchmark full game performance"""
        print(f"Benchmarking full games ({iterations} iterations)...")
        
        times = []
        
        for i in range(iterations):
            game = qec_main.Game(seed=42 + i)
            
            start_time = time.perf_counter()
            result = game.run(max_plies=50)  # Shorter games for benchmarking
            end_time = time.perf_counter()
            
            times.append((end_time - start_time) * 1000)  # Convert to ms
        
        return self._calculate_benchmark_result("full_game", iterations, times)
    
    def benchmark_cache_performance(self, iterations: int = 1000) -> BenchmarkResult:
        """Benchmark cache performance"""
        print(f"Benchmarking cache performance ({iterations} iterations)...")
        
        times = []
        cache = get_move_cache()
        
        for i in range(iterations):
            game = qec_main.Game(seed=42 + i)
            
            start_time = time.perf_counter()
            # Test cache operations
            board_state = game.board.to_fen()
            cached_moves = cache.get_legal_moves(board_state, i)
            if cached_moves is None:
                legal_moves = game.board.legal_moves()
                cache.cache_legal_moves(board_state, i, legal_moves)
            end_time = time.perf_counter()
            
            times.append((end_time - start_time) * 1000)  # Convert to ms
        
        return self._calculate_benchmark_result("cache_performance", iterations, times)
    
    def _calculate_benchmark_result(self, test_name: str, iterations: int, times: List[float]) -> BenchmarkResult:
        """Calculate benchmark result from timing data"""
        total_time = sum(times)
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0.0
        throughput = iterations / (total_time / 1000) if total_time > 0 else 0
        
        return BenchmarkResult(
            test_name=test_name,
            iterations=iterations,
            total_time_ms=total_time,
            avg_time_ms=avg_time,
            min_time_ms=min_time,
            max_time_ms=max_time,
            std_dev_ms=std_dev,
            throughput=throughput
        )
    
    def run_all_benchmarks(self) -> List[BenchmarkResult]:
        """Run all benchmark tests"""
        print("Running QEC benchmark suite...")
        
        benchmarks = [
            self.benchmark_move_generation(1000),
            self.benchmark_evaluation(1000),
            self.benchmark_full_game(100),
            self.benchmark_cache_performance(1000)
        ]
        
        self.results = benchmarks
        return benchmarks
    
    def check_regressions(self) -> Dict[str, bool]:
        """Check for performance regressions against thresholds"""
        regressions = {}
        
        for result in self.results:
            threshold_key = f"{result.test_name}_ms"
            if threshold_key in self.thresholds:
                threshold = self.thresholds[threshold_key]
                regressions[result.test_name] = result.avg_time_ms > threshold
        
        # Check cache hit rate
        cache_stats = get_cache_stats()
        if cache_stats['total_requests'] > 0:
            hit_rate = cache_stats['hit_rate'] / 100
            regressions['cache_hit_rate'] = hit_rate < self.thresholds['cache_hit_rate']
        
        return regressions
    
    def save_results(self, filename: str = "last_run.csv") -> str:
        """Save benchmark results to CSV"""
        output_file = self.output_dir / filename
        
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = [
                'test_name', 'iterations', 'total_time_ms', 'avg_time_ms',
                'min_time_ms', 'max_time_ms', 'std_dev_ms', 'throughput'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in self.results:
                writer.writerow({
                    'test_name': result.test_name,
                    'iterations': result.iterations,
                    'total_time_ms': result.total_time_ms,
                    'avg_time_ms': result.avg_time_ms,
                    'min_time_ms': result.min_time_ms,
                    'max_time_ms': result.max_time_ms,
                    'std_dev_ms': result.std_dev_ms,
                    'throughput': result.throughput
                })
        
        print(f"Benchmark results saved to {output_file}")
        return str(output_file)
    
    def generate_report(self) -> str:
        """Generate benchmark report"""
        report_lines = [
            "QEC Benchmark Report",
            "=" * 50,
            ""
        ]
        
        for result in self.results:
            report_lines.extend([
                f"Test: {result.test_name}",
                f"  Iterations: {result.iterations}",
                f"  Average time: {result.avg_time_ms:.3f} ms",
                f"  Min time: {result.min_time_ms:.3f} ms",
                f"  Max time: {result.max_time_ms:.3f} ms",
                f"  Std dev: {result.std_dev_ms:.3f} ms",
                f"  Throughput: {result.throughput:.1f} ops/sec",
                ""
            ])
        
        # Check regressions
        regressions = self.check_regressions()
        if any(regressions.values()):
            report_lines.extend([
                "Performance Regressions Detected:",
                "-" * 30
            ])
            for test, is_regression in regressions.items():
                if is_regression:
                    report_lines.append(f"  ❌ {test}")
                else:
                    report_lines.append(f"  ✅ {test}")
        else:
            report_lines.extend([
                "All benchmarks within thresholds:",
                "✅ No regressions detected"
            ])
        
        report_text = "\n".join(report_lines)
        
        # Save report
        report_file = self.output_dir / "benchmark_report.txt"
        with open(report_file, 'w') as f:
            f.write(report_text)
        
        print(report_text)
        return report_text

def main():
    """Main benchmark runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='QEC Benchmark Suite')
    parser.add_argument('--output-dir', type=str, default='bench', help='Output directory')
    parser.add_argument('--csv', type=str, default='last_run.csv', help='CSV output filename')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--check-regressions', action='store_true', help='Check for regressions')
    
    args = parser.parse_args()
    
    # Run benchmarks
    suite = QECBenchmarkSuite(args.output_dir)
    results = suite.run_all_benchmarks()
    
    # Save results
    csv_file = suite.save_results(args.csv)
    
    # Generate report
    if args.report:
        suite.generate_report()
    
    # Check regressions
    if args.check_regressions:
        regressions = suite.check_regressions()
        if any(regressions.values()):
            print("❌ Performance regressions detected!")
            for test, is_regression in regressions.items():
                if is_regression:
                    print(f"  - {test}")
            return 1
        else:
            print("✅ No performance regressions detected")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
