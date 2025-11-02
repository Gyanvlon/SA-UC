"""
SIMD vs Scalar Implementation Comparison
Demonstrates SIMD-style operations using NumPy
"""

import numpy as np
import time
import matplotlib.pyplot as plt

def scalar_dot_product(a, b):
    """Scalar implementation of dot product"""
    result = 0.0
    for i in range(len(a)):
        result += a[i] * b[i]
    return result

def simd_dot_product(a, b):
    """SIMD-style implementation using NumPy"""
    return np.dot(a, b)

def scalar_matrix_multiply(A, B):
    """Scalar implementation of matrix multiplication"""
    rows_A, cols_A = A.shape
    rows_B, cols_B = B.shape
    
    result = np.zeros((rows_A, cols_B))
    for i in range(rows_A):
        for j in range(cols_B):
            for k in range(cols_A):
                result[i, j] += A[i, k] * B[k, j]
    return result

def simd_matrix_multiply(A, B):
    """SIMD-style implementation using NumPy"""
    return np.matmul(A, B)

def scalar_image_filter(image, kernel):
    """Scalar implementation of image convolution"""
    h, w = image.shape
    kh, kw = kernel.shape
    pad_h, pad_w = kh // 2, kw // 2
    
    result = np.zeros_like(image)
    
    for i in range(pad_h, h - pad_h):
        for j in range(pad_w, w - pad_w):
            sum_val = 0.0
            for ki in range(kh):
                for kj in range(kw):
                    sum_val += image[i + ki - pad_h, j + kj - pad_w] * kernel[ki, kj]
            result[i, j] = sum_val
    
    return result

def simd_image_filter(image, kernel):
    """SIMD-style implementation using convolution"""
    from scipy.ndimage import convolve
    return convolve(image, kernel, mode='constant')

def benchmark_dot_product(sizes=[1000, 5000, 10000, 50000]):
    """Benchmark dot product operations"""
    print("\n" + "=" * 60)
    print("DOT PRODUCT BENCHMARK")
    print("=" * 60)
    
    scalar_times = []
    simd_times = []
    
    for size in sizes:
        a = np.random.rand(size)
        b = np.random.rand(size)
        
        # Scalar
        start = time.time()
        scalar_result = scalar_dot_product(a, b)
        scalar_time = time.time() - start
        scalar_times.append(scalar_time)
        
        # SIMD
        start = time.time()
        simd_result = simd_dot_product(a, b)
        simd_time = time.time() - start
        simd_times.append(simd_time)
        
        print(f"\nSize: {size}")
        print(f"  Scalar: {scalar_time:.6f}s, Result: {scalar_result:.4f}")
        print(f"  SIMD:   {simd_time:.6f}s, Result: {simd_result:.4f}")
        print(f"  Speedup: {scalar_time/simd_time:.2f}x")
    
    return sizes, scalar_times, simd_times

def benchmark_matrix_multiply(sizes=[50, 100, 200, 300]):
    """Benchmark matrix multiplication"""
    print("\n" + "=" * 60)
    print("MATRIX MULTIPLICATION BENCHMARK")
    print("=" * 60)
    
    scalar_times = []
    simd_times = []
    
    for size in sizes:
        A = np.random.rand(size, size)
        B = np.random.rand(size, size)
        
        # Scalar
        start = time.time()
        scalar_result = scalar_matrix_multiply(A, B)
        scalar_time = time.time() - start
        scalar_times.append(scalar_time)
        
        # SIMD
        start = time.time()
        simd_result = simd_matrix_multiply(A, B)
        simd_time = time.time() - start
        simd_times.append(simd_time)
        
        print(f"\nMatrix Size: {size}x{size}")
        print(f"  Scalar: {scalar_time:.6f}s")
        print(f"  SIMD:   {simd_time:.6f}s")
        print(f"  Speedup: {scalar_time/simd_time:.2f}x")
        
        # Verify correctness
        error = np.max(np.abs(scalar_result - simd_result))
        print(f"  Max Error: {error:.2e}")
    
    return sizes, scalar_times, simd_times

def benchmark_image_filter(sizes=[100, 200, 300, 400]):
    """Benchmark image filtering"""
    print("\n" + "=" * 60)
    print("IMAGE FILTER BENCHMARK")
    print("=" * 60)
    
    kernel = np.array([
        [-1, -1, -1],
        [-1,  8, -1],
        [-1, -1, -1]
    ]) / 8.0
    
    scalar_times = []
    simd_times = []
    
    for size in sizes:
        image = np.random.rand(size, size)
        
        # Scalar
        start = time.time()
        scalar_result = scalar_image_filter(image, kernel)
        scalar_time = time.time() - start
        scalar_times.append(scalar_time)
        
        # SIMD
        start = time.time()
        simd_result = simd_image_filter(image, kernel)
        simd_time = time.time() - start
        simd_times.append(simd_time)
        
        print(f"\nImage Size: {size}x{size}")
        print(f"  Scalar: {scalar_time:.6f}s")
        print(f"  SIMD:   {simd_time:.6f}s")
        print(f"  Speedup: {scalar_time/simd_time:.2f}x")
    
    return sizes, scalar_times, simd_times

def plot_all_benchmarks(dot_data, matrix_data, filter_data):
    """Plot all benchmark results"""
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    
    # Dot Product
    axes[0, 0].plot(dot_data[0], dot_data[1], 'o-', label='Scalar', linewidth=2)
    axes[0, 0].plot(dot_data[0], dot_data[2], 's-', label='SIMD', linewidth=2)
    axes[0, 0].set_xlabel('Vector Size')
    axes[0, 0].set_ylabel('Time (s)')
    axes[0, 0].set_title('Dot Product: Time Comparison')
    axes[0, 0].legend()
    axes[0, 0].grid(True)
    axes[0, 0].set_xscale('log')
    axes[0, 0].set_yscale('log')
    
    speedup = [s/v for s, v in zip(dot_data[1], dot_data[2])]
    axes[1, 0].plot(dot_data[0], speedup, 'o-', color='green', linewidth=2)
    axes[1, 0].set_xlabel('Vector Size')
    axes[1, 0].set_ylabel('Speedup')
    axes[1, 0].set_title('Dot Product: Speedup')
    axes[1, 0].grid(True)
    axes[1, 0].set_xscale('log')
    
    # Matrix Multiplication
    axes[0, 1].plot(matrix_data[0], matrix_data[1], 'o-', label='Scalar', linewidth=2)
    axes[0, 1].plot(matrix_data[0], matrix_data[2], 's-', label='SIMD', linewidth=2)
    axes[0, 1].set_xlabel('Matrix Size')
    axes[0, 1].set_ylabel('Time (s)')
    axes[0, 1].set_title('Matrix Multiply: Time Comparison')
    axes[0, 1].legend()
    axes[0, 1].grid(True)
    
    speedup = [s/v for s, v in zip(matrix_data[1], matrix_data[2])]
    axes[1, 1].plot(matrix_data[0], speedup, 'o-', color='green', linewidth=2)
    axes[1, 1].set_xlabel('Matrix Size')
    axes[1, 1].set_ylabel('Speedup')
    axes[1, 1].set_title('Matrix Multiply: Speedup')
    axes[1, 1].grid(True)
    
    # Image Filter
    axes[0, 2].plot(filter_data[0], filter_data[1], 'o-', label='Scalar', linewidth=2)
    axes[0, 2].plot(filter_data[0], filter_data[2], 's-', label='SIMD', linewidth=2)
    axes[0, 2].set_xlabel('Image Size')
    axes[0, 2].set_ylabel('Time (s)')
    axes[0, 2].set_title('Image Filter: Time Comparison')
    axes[0, 2].legend()
    axes[0, 2].grid(True)
    
    speedup = [s/v for s, v in zip(filter_data[1], filter_data[2])]
    axes[1, 2].plot(filter_data[0], speedup, 'o-', color='green', linewidth=2)
    axes[1, 2].set_xlabel('Image Size')
    axes[1, 2].set_ylabel('Speedup')
    axes[1, 2].set_title('Image Filter: Speedup')
    axes[1, 2].grid(True)
    
    plt.tight_layout()
    plt.savefig('simd_benchmarks.png', dpi=300)
    plt.show()

if __name__ == "__main__":
    # Run all benchmarks
    dot_data = benchmark_dot_product()
    matrix_data = benchmark_matrix_multiply()
    filter_data = benchmark_image_filter()
    
    # Plot results
    plot_all_benchmarks(dot_data, matrix_data, filter_data)
    
    print("\n" + "=" * 60)
    print("All benchmarks complete! Graph saved as 'simd_benchmarks.png'")
    print("=" * 60)