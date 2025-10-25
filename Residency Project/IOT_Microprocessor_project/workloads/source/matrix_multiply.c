#include <stdio.h>

#define SIZE 20

void matrix_multiply(int a[SIZE][SIZE], int b[SIZE][SIZE], int c[SIZE][SIZE]) {
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            c[i][j] = 0;
            for (int k = 0; k < SIZE; k++) {
                c[i][j] += a[i][k] * b[k][j];
            }
        }
    }
}

int main() {
    printf("===========================================\n");
    printf("Matrix Multiplication Benchmark\n");
    printf("Matrix Size: %dx%d\n", SIZE, SIZE);
    printf("===========================================\n\n");

    static int a[SIZE][SIZE], b[SIZE][SIZE], c[SIZE][SIZE];

    printf("Initializing matrices...\n");
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            a[i][j] = i + j;
            b[i][j] = i * j + 1;
        }
    }

    printf("Performing multiplication...\n");
    matrix_multiply(a, b, c);

    printf("\nSample results (c[0][0] to c[2][2]):\n");
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            printf("%6d ", c[i][j]);
        }
        printf("\n");
    }

    printf("\n===========================================\n");
    printf("Matrix multiplication completed!\n");
    printf("===========================================\n");

    return 0;
}