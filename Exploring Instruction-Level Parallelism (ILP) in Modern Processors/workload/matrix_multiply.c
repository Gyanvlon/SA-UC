#include <stdio.h>
#include <stdlib.h>

#define SIZE 64

// Global matrices to avoid stack overflow
int A[SIZE][SIZE];
int B[SIZE][SIZE];
int C[SIZE][SIZE];

// Matrix multiplication: C = A * B
void matrix_multiply(int A[SIZE][SIZE], int B[SIZE][SIZE], int C[SIZE][SIZE]) {
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            C[i][j] = 0;
            for (int k = 0; k < SIZE; k++) {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }
}

// Initialize matrix with values
void init_matrix(int matrix[SIZE][SIZE], int seed) {
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            matrix[i][j] = ((i + j + seed) * 7) % 10;
        }
    }
}

// Calculate checksum (prevents compiler optimization)
long checksum(int matrix[SIZE][SIZE]) {
    long sum = 0;
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            sum += matrix[i][j];
        }
    }
    return sum;
}

int main() {
    printf("Matrix Multiplication Benchmark\n");
    printf("Matrix size: %d x %d\n", SIZE, SIZE);

    printf("Initializing matrices...\n");
    init_matrix(A, 1);
    init_matrix(B, 2);

    printf("Starting matrix multiplication...\n");
    matrix_multiply(A, B, C);

    long sum = checksum(C);
    printf("Checksum: %ld\n", sum);
    printf("Matrix multiplication completed successfully!\n");

    return 0;
}