#include <stdio.h>
#include <stdlib.h>

#define ARRAY_SIZE 5000
#define NUM_ITERATIONS 50
#define NUM_THREADS 4

// Global array
int global_array[ARRAY_SIZE];
long thread_results[NUM_THREADS];

// Compute-intensive function
long compute_sum(int start, int end, int thread_id) {
    long sum = 0;

    for (int iter = 0; iter < NUM_ITERATIONS; iter++) {
        for (int i = start; i < end; i++) {
            sum += global_array[i] * global_array[i];
            sum = sum % 1000000;
        }
    }

    return sum;
}

// Simulated parallel execution (manual threading)
void parallel_compute() {
    int chunk_size = ARRAY_SIZE / NUM_THREADS;

    // Simulate thread 0
    thread_results[0] = compute_sum(0, chunk_size, 0);
    printf("Thread 0: sum = %ld\n", thread_results[0]);

    // Simulate thread 1
    thread_results[1] = compute_sum(chunk_size, 2 * chunk_size, 1);
    printf("Thread 1: sum = %ld\n", thread_results[1]);

    // Simulate thread 2
    thread_results[2] = compute_sum(2 * chunk_size, 3 * chunk_size, 2);
    printf("Thread 2: sum = %ld\n", thread_results[2]);

    // Simulate thread 3
    thread_results[3] = compute_sum(3 * chunk_size, ARRAY_SIZE, 3);
    printf("Thread 3: sum = %ld\n", thread_results[3]);
}

int main() {
    printf("Multi-threaded Workload\n");
    printf("Array size: %d, Threads: %d\n", ARRAY_SIZE, NUM_THREADS);

    // Initialize array
    for (int i = 0; i < ARRAY_SIZE; i++) {
        global_array[i] = i % 100;
    }

    printf("Starting parallel computation...\n");
    parallel_compute();

    // Calculate total sum
    long total_sum = 0;
    for (int i = 0; i < NUM_THREADS; i++) {
        total_sum += thread_results[i];
    }

    printf("\nResults \n");
    printf("Total sum: %ld\n", total_sum);
    printf("Multi-threaded run completed!\n");

    return 0;
}