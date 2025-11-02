"""
GPU Acceleration Demo using CuPy (CUDA) or NumPy fallback
Demonstrates matrix multiplication and image processing on GPU
"""

import numpy as np
import time
import matplotlib.pyplot as plt

# Try to import CuPy for GPU acceleration
try:
    import cupy as cp
    GPU_AVAILABLE = True
    print("GPU (CuPy) is available!")
except ImportError:
    print("CuPy not available. Using NumPy (CPU) only.")
    print("To enable GPU: pip install cupy-cuda11x (replace 11x with your CUDA version)")
    GPU_AVAILABLE = False
    cp = np

class GPUBenchmark:
    """Benchmark CPU vs GPU performance"""
    
    def __init__(self):
        self.gpu_available = GPU_AVAILABLE
        
    def matrix_multiply_cpu(self, A, B):
        """CPU matrix multiplication"""
        return np.matmul(A, B)
    
    def matrix_multiply_gpu(self, A, B):
        """GPU matrix multiplication"""
        if not self.gpu_available:
            return self.matrix_multiply_cpu(A, B)
        
        # Transfer to GPU
        A_gpu = cp.asarray(A)
        B_gpu = cp.asarray(B)
        
        # Compute on GPU
        C_gpu = cp.matmul(A_gpu, B_gpu)
        
        # Transfer back to CPU
        return cp.asnumpy(C_gpu)
    
    def benchmark_matrix_multiply(self, sizes=[500, 1000, 2000, 3000]):
        """Benchmark matrix multiplication"""
        print("\n" + "=" * 70)
        print("GPU MATRIX MULTIPLICATION BENCHMARK")
        print("=" * 70)
        
        cpu_times = []
        gpu_times = []
        gpu_with_transfer_times = []
        
        for size in sizes:
            print(f"\nMatrix Size: {size}x{size}")
            
            # Generate test data
            A = np.random.rand(size, size).astype(np.float32)
            B = np.random.rand(size, size).astype(np.float32)
            
            # CPU benchmark
            start = time.time()
            C_cpu = self.matrix_multiply_cpu(A, B)
            cpu_time = time.time() - start
            cpu_times.append(cpu_time)
            print(f"  CPU Time: {cpu_time:.4f}s")
            
            if self.gpu_available:
                # GPU benchmark (including transfer time)
                start = time.time()
                C_gpu = self.matrix_multiply_gpu(A, B)
                gpu_with_transfer_time = time.time() - start
                gpu_with_transfer_times.append(gpu_with_transfer_time)
                print(f"  GPU Time (with transfer): {gpu_with_transfer_time:.4f}s")
                
                # GPU benchmark (computation only)
                A_gpu = cp.asarray(A)
                B_gpu = cp.asarray(B)
                cp.cuda.Stream.null.synchronize()
                
                start = time.time()
                C_gpu = cp.matmul(A_gpu, B_gpu)
                cp.cuda.Stream.null.synchronize()
                gpu_time = time.time() - start
                gpu_times.append(gpu_time)
                print(f"  GPU Time (computation only): {gpu_time:.4f}s")
                
                # Verify correctness
                error = np.max(np.abs(C_cpu - cp.asnumpy(C_gpu)))
                print(f"  Max Error: {error:.2e}")
                print(f"  Speedup (computation only): {cpu_time/gpu_time:.2f}x")
                print(f"  Speedup (with transfer): {cpu_time/gpu_with_transfer_time:.2f}x")
            else:
                gpu_times.append(cpu_time)
                gpu_with_transfer_times.append(cpu_time)
        
        return sizes, cpu_times, gpu_times, gpu_with_transfer_times
    
    def image_processing_cpu(self, image):
        """CPU image processing pipeline"""
        # Gaussian blur
        from scipy.ndimage import gaussian_filter
        blurred = gaussian_filter(image, sigma=2)
        
        # Edge detection (Sobel)
        from scipy.ndimage import sobel
        edges_x = sobel(blurred, axis=0)
        edges_y = sobel(blurred, axis=1)
        edges = np.hypot(edges_x, edges_y)
        
        return edges
    
    def image_processing_gpu(self, image):
        """GPU image processing pipeline"""
        if not self.gpu_available:
            return self.image_processing_cpu(image)
        
        # Transfer to GPU
        image_gpu = cp.asarray(image)
        
        # Simple convolution-based processing on GPU
        # Gaussian kernel
        kernel = cp.array([
            [1, 2, 1],
            [2, 4, 2],
            [1, 2, 1]
        ], dtype=cp.float32) / 16.0
        
        # Manual convolution
        h, w = image_gpu.shape
        kh, kw = kernel.shape
        pad = kh // 2
        
        # Pad image
        padded = cp.pad(image_gpu, pad, mode='edge')
        result = cp.zeros_like(image_gpu)
        
        # Convolution
        for i in range(kh):
            for j in range(kw):
                result += padded[i:i+h, j:j+w] * kernel[i, j]
        
        return cp.asnumpy(result)
    
    def benchmark_image_processing(self, sizes=[512, 1024, 2048, 4096]):
        """Benchmark image processing"""
        print("\n" + "=" * 70)
        print("GPU IMAGE PROCESSING BENCHMARK")
        print("=" * 70)
        
        cpu_times = []
        gpu_times = []
        
        for size in sizes:
            print(f"\nImage Size: {size}x{size}")
            
            # Generate test image
            image = np.random.rand(size, size).astype(np.float32)
            
            # CPU benchmark
            start = time.time()
            result_cpu = self.image_processing_cpu(image)
            cpu_time = time.time() - start
            cpu_times.append(cpu_time)
            print(f"  CPU Time: {cpu_time:.4f}s")
            
            if self.gpu_available:
                # GPU benchmark
                start = time.time()
                result_gpu = self.image_processing_gpu(image)
                gpu_time = time.time() - start
                gpu_times.append(gpu_time)
                print(f"  GPU Time: {gpu_time:.4f}s")
                print(f"  Speedup: {cpu_time/gpu_time:.2f}x")
            else:
                gpu_times.append(cpu_time)
        
        return sizes, cpu_times, gpu_times

def plot_gpu_benchmarks(matrix_data, image_data):
    """Plot GPU benchmark results"""
    fig = plt.figure(figsize=(16, 10))
    
    # Matrix Multiplication - Time Comparison
    ax1 = plt.subplot(2, 3, 1)
    ax1.plot(matrix_data[0], matrix_data[1], 'o-', label='CPU', linewidth=2, markersize=8)
    if GPU_AVAILABLE:
        ax1.plot(matrix_data[0], matrix_data[2], 's-', label='GPU (compute)', linewidth=2, markersize=8)
        ax1.plot(matrix_data[0], matrix_data[3], '^-', label='GPU (with transfer)', linewidth=2, markersize=8)
    ax1.set_xlabel('Matrix Size', fontsize=12)
    ax1.set_ylabel('Time (seconds)', fontsize=12)
    ax1.set_title('Matrix Multiplication: Time Comparison', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # Matrix Multiplication - Speedup
    ax2 = plt.subplot(2, 3, 2)
    if GPU_AVAILABLE:
        speedup_compute = [c/g for c, g in zip(matrix_data[1], matrix_data[2])]
        speedup_transfer = [c/g for c, g in zip(matrix_data[1], matrix_data[3])]
        ax2.plot(matrix_data[0], speedup_compute, 's-', label='Compute Only', 
                linewidth=2, markersize=8, color='green')
        ax2.plot(matrix_data[0], speedup_transfer, '^-', label='With Transfer', 
                linewidth=2, markersize=8, color='orange')
        ax2.axhline(y=1, color='r', linestyle='--', label='No Speedup', alpha=0.5)
    ax2.set_xlabel('Matrix Size', fontsize=12)
    ax2.set_ylabel('Speedup Factor', fontsize=12)
    ax2.set_title('Matrix Multiplication: GPU Speedup', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    # Matrix Multiplication - GFLOPS
    ax3 = plt.subplot(2, 3, 3)
    cpu_gflops = [2 * (s**3) / (t * 1e9) for s, t in zip(matrix_data[0], matrix_data[1])]
    ax3.plot(matrix_data[0], cpu_gflops, 'o-', label='CPU', linewidth=2, markersize=8)
    if GPU_AVAILABLE:
        gpu_gflops = [2 * (s**3) / (t * 1e9) for s, t in zip(matrix_data[0], matrix_data[2])]
        ax3.plot(matrix_data[0], gpu_gflops, 's-', label='GPU', linewidth=2, markersize=8)
    ax3.set_xlabel('Matrix Size', fontsize=12)
    ax3.set_ylabel('GFLOPS', fontsize=12)
    ax3.set_title('Matrix Multiplication: Performance (GFLOPS)', fontsize=14, fontweight='bold')
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)
    
    # Image Processing - Time Comparison
    ax4 = plt.subplot(2, 3, 4)
    ax4.plot(image_data[0], image_data[1], 'o-', label='CPU', linewidth=2, markersize=8)
    if GPU_AVAILABLE:
        ax4.plot(image_data[0], image_data[2], 's-', label='GPU', linewidth=2, markersize=8)
    ax4.set_xlabel('Image Size', fontsize=12)
    ax4.set_ylabel('Time (seconds)', fontsize=12)
    ax4.set_title('Image Processing: Time Comparison', fontsize=14, fontweight='bold')
    ax4.legend(fontsize=10)
    ax4.grid(True, alpha=0.3)
    
    # Image Processing - Speedup
    ax5 = plt.subplot(2, 3, 5)
    if GPU_AVAILABLE:
        speedup = [c/g for c, g in zip(image_data[1], image_data[2])]
        ax5.plot(image_data[0], speedup, 's-', linewidth=2, markersize=8, color='green')
        ax5.axhline(y=1, color='r', linestyle='--', label='No Speedup', alpha=0.5)
    ax5.set_xlabel('Image Size', fontsize=12)
    ax5.set_ylabel('Speedup Factor', fontsize=12)
    ax5.set_title('Image Processing: GPU Speedup', fontsize=14, fontweight='bold')
    ax5.legend(fontsize=10)
    ax5.grid(True, alpha=0.3)
    
    # Throughput comparison
    ax6 = plt.subplot(2, 3, 6)
    cpu_throughput = [(s*s) / (t * 1e6) for s, t in zip(image_data[0], image_data[1])]
    ax6.plot(image_data[0], cpu_throughput, 'o-', label='CPU', linewidth=2, markersize=8)
    if GPU_AVAILABLE:
        gpu_throughput = [(s*s) / (t * 1e6) for s, t in zip(image_data[0], image_data[2])]
        ax6.plot(image_data[0], gpu_throughput, 's-', label='GPU', linewidth=2, markersize=8)
    ax6.set_xlabel('Image Size', fontsize=12)
    ax6.set_ylabel('Megapixels/second', fontsize=12)
    ax6.set_title('Image Processing: Throughput', fontsize=14, fontweight='bold')
    ax6.legend(fontsize=10)
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('gpu_benchmarks.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    benchmark = GPUBenchmark()
    
    # Run matrix multiplication benchmark
    matrix_data = benchmark.benchmark_matrix_multiply()
    
    # Run image processing benchmark
    image_data = benchmark.benchmark_image_processing()
    
    # Plot results
    plot_gpu_benchmarks(matrix_data, image_data)
    
    print("\n" + "=" * 70)
    print("GPU benchmarks complete! Graph saved as 'gpu_benchmarks.png'")
    print("=" * 70)