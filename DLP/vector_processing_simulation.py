"""
Vector Architecture Simulation
Demonstrates vector processing vs scalar processing for array operations
"""

import numpy as np
import time
import matplotlib.pyplot as plt

class VectorProcessor:
    def __init__(self, vector_length=64):
        self.vector_length = vector_length
        self.vector_registers = {}
        
    def vector_add(self, vec_a, vec_b, vec_result):
        """Simulate vector addition operation"""
        self.vector_registers[vec_result] = (
            self.vector_registers[vec_a] + self.vector_registers[vec_b]
        )
        
    def vector_multiply(self, vec_a, vec_b, vec_result):
        """Simulate vector multiplication operation"""
        self.vector_registers[vec_result] = (
            self.vector_registers[vec_a] * self.vector_registers[vec_b]
        )
        
    def load_vector(self, name, data):
        """Load data into vector register"""
        self.vector_registers[name] = np.array(data)
        
    def get_vector(self, name):
        """Retrieve vector register contents"""
        return self.vector_registers[name]

def scalar_vector_addition(a, b):
    """Scalar implementation of vector addition"""
    result = np.zeros_like(a)
    for i in range(len(a)):
        result[i] = a[i] + b[i]
    return result

def scalar_vector_multiply(a, b):
    """Scalar implementation of vector multiplication"""
    result = np.zeros_like(a)
    for i in range(len(a)):
        result[i] = a[i] * b[i]
    return result

def benchmark_operations(sizes=[1000, 10000, 100000, 1000000]):
    """Benchmark scalar vs vector operations"""
    scalar_times = []
    vector_times = []
    
    for size in sizes:
        # Generate test data
        a = np.random.rand(size)
        b = np.random.rand(size)
        
        # Scalar timing
        start = time.time()
        scalar_result = scalar_vector_addition(a, b)
        scalar_result = scalar_vector_multiply(scalar_result, b)
        scalar_time = time.time() - start
        scalar_times.append(scalar_time)
        
        # Vector timing (using NumPy's vectorized operations)
        start = time.time()
        vector_result = a + b
        vector_result = vector_result * b
        vector_time = time.time() - start
        vector_times.append(vector_time)
        
        print(f"Size: {size}")
        print(f"  Scalar time: {scalar_time:.6f}s")
        print(f"  Vector time: {vector_time:.6f}s")
        print(f"  Speedup: {scalar_time/vector_time:.2f}x\n")
    
    return sizes, scalar_times, vector_times

def plot_performance(sizes, scalar_times, vector_times):
    """Plot performance comparison"""
    plt.figure(figsize=(12, 5))
    
    # Time comparison
    plt.subplot(1, 2, 1)
    plt.plot(sizes, scalar_times, 'o-', label='Scalar', linewidth=2)
    plt.plot(sizes, vector_times, 's-', label='Vector', linewidth=2)
    plt.xlabel('Array Size')
    plt.ylabel('Execution Time (seconds)')
    plt.title('Scalar vs Vector Performance')
    plt.legend()
    plt.grid(True)
    plt.xscale('log')
    plt.yscale('log')
    
    # Speedup
    plt.subplot(1, 2, 2)
    speedup = [s/v for s, v in zip(scalar_times, vector_times)]
    plt.plot(sizes, speedup, 'o-', color='green', linewidth=2)
    plt.xlabel('Array Size')
    plt.ylabel('Speedup Factor')
    plt.title('Vector Speedup over Scalar')
    plt.grid(True)
    plt.xscale('log')
    
    plt.tight_layout()
    plt.savefig('vector_performance.png', dpi=300)
    plt.show()

def demonstrate_vector_processor():
    """Demonstrate vector processor operations"""
    print("=" * 60)
    print("Vector Processor Demonstration")
    print("=" * 60)
    
    vp = VectorProcessor(vector_length=8)
    
    # Load vectors
    vp.load_vector('V1', [1, 2, 3, 4, 5, 6, 7, 8])
    vp.load_vector('V2', [8, 7, 6, 5, 4, 3, 2, 1])
    
    print("\nVector V1:", vp.get_vector('V1'))
    print("Vector V2:", vp.get_vector('V2'))
    
    # Vector addition
    vp.vector_add('V1', 'V2', 'V3')
    print("\nV3 = V1 + V2:", vp.get_vector('V3'))
    
    # Vector multiplication
    vp.vector_multiply('V1', 'V2', 'V4')
    print("V4 = V1 * V2:", vp.get_vector('V4'))
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    # Demonstrate vector processor
    demonstrate_vector_processor()
    
    # Run benchmarks
    print("\nRunning Performance Benchmarks...")
    print("=" * 60)
    sizes, scalar_times, vector_times = benchmark_operations()
    
    # Plot results
    plot_performance(sizes, scalar_times, vector_times)
    
    print("\nBenchmark complete! Graph saved as 'vector_performance.png'")