"""
Loop-Level Parallelism Demonstration
Shows various techniques for parallelizing loops
"""

import numpy as np
import time
from multiprocessing import Pool, cpu_count
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import matplotlib.pyplot as plt

class LoopParallelism:
    """Demonstrate various loop parallelization techniques"""
    
    def __init__(self):
        self.cpu_cores = cpu_count()
        print(f"Available CPU cores: {self.cpu_cores}")
    
    # ========== Sequential Implementations ==========
    
    def sequential_sum(self, n):
        """Sequential sum calculation"""
        total = 0
        for i in range(n):
            total += i * i
        return total
    
    def sequential_matrix_operation(self, matrix):
        """Sequential matrix row operation"""
        result = np.zeros_like(matrix)
        for i in range(matrix.shape[0]):
            result[i] = np.sum(matrix[i] ** 2) + np.mean(matrix[i])
        return result
    
    def sequential_monte_carlo(self, n_samples):
        """Sequential Monte Carlo Pi estimation"""
        inside = 0
        for _ in range(n_samples):
            x, y = np.random.random(), np.random.random()
            if x*x + y*y <= 1:
                inside += 1
        return 4 * inside / n_samples
    
    # ========== Parallel Implementations ==========
    
    def parallel_sum_vectorized(self, n):
        """Vectorized sum using NumPy"""
        arr = np.arange(n)
        return np.sum(arr * arr)
    
    def parallel_matrix_operation_vectorized(self, matrix):
        """Vectorized matrix operation"""
        return np.sum(matrix ** 2, axis=1) + np.mean(matrix, axis=1)
    
    @staticmethod
    def _monte_carlo_chunk(n_samples):
        """Helper for parallel Monte Carlo"""
        inside = 0
        for _ in range(n_samples):
            x, y = np.random.random(), np.random.random()
            if x*x + y*y <= 1:
                inside += 1
        return inside
    
    def parallel_monte_carlo_multiprocessing(self, n_samples, n_processes=None):
        """Parallel Monte Carlo using multiprocessing"""
        if n_processes is None:
            n_processes = self.cpu_cores
        
        chunk_size = n_samples // n_processes
        chunks = [chunk_size] * n_processes
        
        with Pool(n_processes) as pool:
            results = pool.map(self._monte_carlo_chunk, chunks)
        
        return 4 * sum(results) / n_samples
    
    @staticmethod
    def _matrix_row_operation(args):
        """Helper for parallel matrix operation"""
        row, idx = args
        return idx, np.sum(row ** 2) + np.mean(row)
    
    def parallel_matrix_operation_multiprocessing(self, matrix, n_processes=None):
        """Parallel matrix operation using multiprocessing"""
        if n_processes is None:
            n_processes = self.cpu_cores
        
        rows_with_idx = [(matrix[i], i) for i in range(matrix.shape[0])]
        
        with Pool(n_processes) as pool:
            results = pool.map(self._matrix_row_operation, rows_with_idx)
        
        # Sort by index and extract values
        results.sort(key=lambda x: x[0])
        return np.array([r[1] for r in results])
    
    # ========== Benchmarking ==========
    
    def benchmark_sum(self, sizes=[1000000, 5000000, 10000000]):
        """Benchmark sum operations"""
        print("\n" + "=" * 70)
        print("SUM OPERATION BENCHMARK")
        print("=" * 70)
        
        seq_times = []
        par_times = []
        
        for size in sizes:
            print(f"\nSize: {size:,}")
            
            # Sequential
            start = time.time()
            seq_result = self.sequential_sum(size)
            seq_time = time.time() - start
            seq_times.append(seq_time)
            print(f"  Sequential: {seq_time:.4f}s, Result: {seq_result:,}")
            
            # Parallel (Vectorized)
            start = time.time()
            par_result = self.parallel_sum_vectorized(size)
            par_time = time.time() - start
            par_times.append(par_time)
            print(f"  Vectorized: {par_time:.4f}s, Result: {par_result:,}")
            print(f"  Speedup: {seq_time/par_time:.2f}x")
        
        return sizes, seq_times, par_times
    
    def benchmark_matrix_operation(self, sizes=[1000, 5000, 10000]):
        """Benchmark matrix operations"""
        print("\n" + "=" * 70)
        print("MATRIX OPERATION BENCHMARK")
        print("=" * 70)
        
        seq_times = []
        vec_times = []
        mp_times = []
        
        for size in sizes:
            print(f"\nMatrix Size: {size} rows x 1000 columns")
            matrix = np.random.rand(size, 1000)
            
            # Sequential
            start = time.time()
            seq_result = self.sequential_matrix_operation(matrix)
            seq_time = time.time() - start
            seq_times.append(seq_time)
            print(f"  Sequential: {seq_time:.4f}s")
            
            # Vectorized
            start = time.time()
            vec_result = self.parallel_matrix_operation_vectorized(matrix)
            vec_time = time.time() - start
            vec_times.append(vec_time)
            print(f"  Vectorized: {vec_time:.4f}s, Speedup: {seq_time/vec_time:.2f}x")
            
            # Multiprocessing (only for larger matrices)
            if size >= 5000:
                start = time.time()
                mp_result = self.parallel_matrix_operation_multiprocessing(matrix)
                mp_time = time.time() - start
                mp_times.append(mp_time)
                print(f"  Multiprocessing: {mp_time:.4f}s, Speedup: {seq_time/mp_time:.2f}x")
            else:
                mp_times.append(None)
        
        return sizes, seq_times, vec_times, mp_times
    
    def benchmark_monte_carlo(self, sizes=[1000000, 5000000, 10000000]):
        """Benchmark Monte Carlo simulation"""
        print("\n" + "=" * 70)
        print("MONTE CARLO PI ESTIMATION BENCHMARK")
        print("=" * 70)
        
        seq_times = []
        par_times = []
        
        for size in sizes:
            print(f"\nSamples: {size:,}")
            
            # Sequential
            start = time.time()
            seq_result = self.sequential_monte_carlo(size)
            seq_time = time.time() - start
            seq_times.append(seq_time)
            print(f"  Sequential: {seq_time:.4f}s, Pi ≈ {seq_result:.6f}")
            
            # Parallel
            start = time.time()
            par_result = self.parallel_monte_carlo_multiprocessing(size)
            par_time = time.time() - start
            par_times.append(par_time)
            print(f"  Parallel ({self.cpu_cores} cores): {par_time:.4f}s, Pi ≈ {par_result:.6f}")
            print(f"  Speedup: {seq_time/par_time:.2f}x")
            print(f"  Efficiency: {(seq_time/par_time)/self.cpu_cores*100:.1f}%")
        
        return sizes, seq_times, par_times

def analyze_loop_dependencies():
    """Analyze loop dependencies and parallelizability"""
    print("\n" + "=" * 70)
    print("LOOP DEPENDENCY ANALYSIS")
    print("=" * 70)
    
    examples = [
        {
            "name": "Independent Iterations (Parallelizable)",
            "code": """
for i in range(n):
    result[i] = array[i] * 2 + 3
""",
            "dependency": "None - Each iteration is independent",
            "parallelizable": True
        },
        {
            "name": "Read-After-Write Dependency (Not Parallelizable)",
            "code": """
for i in range(1, n):
    array[i] = array[i-1] + array[i]
""",
            "dependency": "Iteration i depends on iteration i-1",
            "parallelizable": False
        },
        {
            "name": "Reduction Operation (Parallelizable with care)",
            "code": """
total = 0
for i in range(n):
    total += array[i]
""",
            "dependency": "Accumulation can be parallelized with reduction",
            "parallelizable": True
        },
        {
            "name": "Independent with Indirect Access (May be parallelizable)",
            "code": """
for i in range(n):
    result[i] = array[index[i]] * 2
""",
            "dependency": "Depends on index array - check for conflicts",
            "parallelizable": "Conditional"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\nExample {i}: {example['name']}")
        print(f"Code: {example['code']}")
        print(f"Dependency: {example['dependency']}")
        print(f"Parallelizable: {example['parallelizable']}")

def plot_loop_parallelism_results(sum_data, matrix_data, mc_data):
    """Plot loop parallelism benchmark results"""
    fig = plt.figure(figsize=(18, 10))
    
    # Sum Operation
    ax1 = plt.subplot(2, 3, 1)
    ax1.plot(sum_data[0], sum_data[1], 'o-', label='Sequential', linewidth=2, markersize=8)
    ax1.plot(sum_data[0], sum_data[2], 's-', label='Vectorized', linewidth=2, markersize=8)
    ax1.set_xlabel('Array Size', fontsize=12)
    ax1.set_ylabel('Time (seconds)', fontsize=12)
    ax1.set_title('Sum Operation: Time Comparison', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    ax2 = plt.subplot(2, 3, 2)
    speedup = [s/p for s, p in zip(sum_data[1], sum_data[2])]
    ax2.plot(sum_data[0], speedup, 's-', linewidth=2, markersize=8, color='green')
    ax2.axhline(y=1, color='r', linestyle='--', alpha=0.5)
    ax2.set_xlabel('Array Size', fontsize=12)
    ax2.set_ylabel('Speedup Factor', fontsize=12)
    ax2.set_title('Sum Operation: Speedup', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # Matrix Operation
    ax3 = plt.subplot(2, 3, 3)
    ax3.plot(matrix_data[0], matrix_data[1], 'o-', label='Sequential', linewidth=2, markersize=8)
    ax3.plot(matrix_data[0], matrix_data[2], 's-', label='Vectorized', linewidth=2, markersize=8)
    ax3.set_xlabel('Matrix Rows', fontsize=12)
    ax3.set_ylabel('Time (seconds)', fontsize=12)
    ax3.set_title('Matrix Operation: Time Comparison', fontsize=14, fontweight='bold')
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)
    
    ax4 = plt.subplot(2, 3, 4)
    speedup = [s/p for s, p in zip(matrix_data[1], matrix_data[2])]
    ax4.plot(matrix_data[0], speedup, 's-', linewidth=2, markersize=8, color='green')
    ax4.axhline(y=1, color='r', linestyle='--', alpha=0.5)
    ax4.set_xlabel('Matrix Rows', fontsize=12)
    ax4.set_ylabel('Speedup Factor', fontsize=12)
    ax4.set_title('Matrix Operation: Speedup', fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    # Monte Carlo
    ax5 = plt.subplot(2, 3, 5)
    ax5.plot(mc_data[0], mc_data[1], 'o-', label='Sequential', linewidth=2, markersize=8)
    ax5.plot(mc_data[0], mc_data[2], 's-', label='Parallel', linewidth=2, markersize=8)
    ax5.set_xlabel('Number of Samples', fontsize=12)
    ax5.set_ylabel('Time (seconds)', fontsize=12)
    ax5.set_title('Monte Carlo: Time Comparison', fontsize=14, fontweight='bold')
    ax5.legend(fontsize=10)
    ax5.grid(True, alpha=0.3)
    
    ax6 = plt.subplot(2, 3, 6)
    speedup = [s/p for s, p in zip(mc_data[1], mc_data[2])]
    efficiency = [sp/cpu_count()*100 for sp in speedup]
    ax6_twin = ax6.twinx()
    
    line1 = ax6.plot(mc_data[0], speedup, 's-', linewidth=2, markersize=8, 
                     color='green', label='Speedup')
    ax6.axhline(y=1, color='r', linestyle='--', alpha=0.5)
    ax6.axhline(y=cpu_count(), color='b', linestyle='--', alpha=0.5, 
                label=f'Max ({cpu_count()} cores)')
    
    line2 = ax6_twin.plot(mc_data[0], efficiency, 'o-', linewidth=2, markersize=8, 
                          color='orange', label='Efficiency (%)')
    
    ax6.set_xlabel('Number of Samples', fontsize=12)
    ax6.set_ylabel('Speedup Factor', fontsize=12)
    ax6_twin.set_ylabel('Parallel Efficiency (%)', fontsize=12)
    ax6.set_title('Monte Carlo: Speedup & Efficiency', fontsize=14, fontweight='bold')
    
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax6.legend(lines, labels, fontsize=10, loc='upper left')
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('loop_parallelism_benchmarks.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    # Create loop parallelism analyzer
    lp = LoopParallelism()
    
    # Analyze loop dependencies
    analyze_loop_dependencies()
    
    # Run benchmarks
    sum_data = lp.benchmark_sum()
    matrix_data = lp.benchmark_matrix_operation()
    mc_data = lp.benchmark_monte_carlo()
    
    # Plot results
    plot_loop_parallelism_results(sum_data, matrix_data, mc_data)
    
    print("\n" + "=" * 70)
    print("Loop parallelism benchmarks complete!")
    print("Graph saved as 'loop_parallelism_benchmarks.png'")
    print("=" * 70)