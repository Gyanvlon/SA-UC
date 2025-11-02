/**
 * Vector Processing Benchmark for gem5
 * Author: Gyanvlon
 */

#include <iostream>
#include <vector>
#include <chrono>
#include <x86intrin.h>

// Scalar vector addition
void scalar_add(float* a, float* b, float* c, int n) {
    for(int i = 0; i < n; i++) {
        c[i] = a[i] + b[i];
    }
}

// SIMD vector addition (AVX)
void simd_add_avx(float* a, float* b, float* c, int n) {
    int i = 0;
    for(; i <= n-8; i+=8) {
        __m256 va = _mm256_loadu_ps(&a[i]);
        __m256 vb = _mm256_loadu_ps(&b[i]);
        __m256 vc = _mm256_add_ps(va, vb);
        _mm256_storeu_ps(&c[i], vc);
    }
    // Handle remaining elements
    for(; i < n; i++) {
        c[i] = a[i] + b[i];
    }
}

// Matrix multiplication
void matrix_multiply(float* A, float* B, float* C, int N) {
    for(int i = 0; i < N; i++) {
        for(int j = 0; j < N; j++) {
            float sum = 0.0f;
            for(int k = 0; k < N; k++) {
                sum += A[i*N + k] * B[k*N + j];
            }
            C[i*N + j] = sum;
        }
    }
}

int main() {
    const int SIZE = 1000000;
    
    std::vector<float> a(SIZE), b(SIZE), c(SIZE);
    
    // Initialize arrays
    for(int i = 0; i < SIZE; i++) {
        a[i] = i * 0.5f;
        b[i] = i * 0.3f;
    }
    
    // Benchmark scalar
    auto start = std::chrono::high_resolution_clock::now();
    scalar_add(a.data(), b.data(), c.data(), SIZE);
    auto end = std::chrono::high_resolution_clock::now();
    auto scalar_time = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    
    // Benchmark SIMD
    start = std::chrono::high_resolution_clock::now();
    simd_add_avx(a.data(), b.data(), c.data(), SIZE);
    end = std::chrono::high_resolution_clock::now();
    auto simd_time = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    
    std::cout << "Scalar time: " << scalar_time.count() << " us\n";
    std::cout << "SIMD time: " << simd_time.count() << " us\n";
    std::cout << "Speedup: " << (float)scalar_time.count()/simd_time.count() << "x\n";
    
    // Trigger gem5 exit
    m5_exit(0);
    
    return 0;
}