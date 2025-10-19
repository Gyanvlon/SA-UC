#include <stdio.h>
#include <stdlib.h>

#define ARRAY_SIZE 1000
#define ITERATIONS 10

int main() {
    int array[ARRAY_SIZE];
    int sum_even = 0, sum_odd = 0;
    int count_positive = 0, count_negative = 0;

    // Initialize array with pseudo-random values
    for (int i = 0; i < ARRAY_SIZE; i++) {
        array[i] = (i * 7919) % 201 - 100;  // Values from -100 to 100
    }

    printf("Starting branch intensive computation...\n");
    printf("Array size: %d, Iterations: %d\n", ARRAY_SIZE, ITERATIONS);

    for (int iter = 0; iter < ITERATIONS; iter++) {
        // Test 1: Even/odd branching (predictable pattern)
        for (int i = 0; i < ARRAY_SIZE; i++) {
            if (i % 2 == 0) {
                sum_even += array[i];
            } else {
                sum_odd += array[i];
            }
        }

        // Test 2: Value-based branching (less predictable)
        for (int i = 0; i < ARRAY_SIZE; i++) {
            if (array[i] > 0) {
                count_positive++;
            } else {
                count_negative++;
            }
        }

        // Test 3: Nested branches
        for (int i = 0; i < ARRAY_SIZE; i++) {
            if (array[i] > 50) {
                if (array[i] % 2 == 0) {
                    sum_even += 2;
                } else {
                    sum_odd += 2;
                }
            } else if (array[i] < -50) {
                if (array[i] % 2 == 0) {
                    sum_even -= 2;
                } else {
                    sum_odd -= 2;
                }
            }
        }

        // Test 4: Complex conditional
        for (int i = 0; i < ARRAY_SIZE - 1; i++) {
            if ((array[i] + array[i+1]) > 0 && array[i] != 0) {
                sum_even++;
            } else if (array[i] < array[i+1]) {
                sum_odd++;
            }
        }
    }

    printf("\nResults: \n");
    printf("Sum Even: %d\n", sum_even);
    printf("Sum Odd: %d\n", sum_odd);
    printf("Positive Count: %d\n", count_positive);
    printf("Negative Count: %d\n", count_negative);
    printf("Branch-intensive run completed!\n");

    return 0;
}