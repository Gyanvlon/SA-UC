#include <stdio.h>

#define ARRAY_SIZE 100

int main() {
    printf("===========================================\n");
    printf("IoT Microprocessor - Simple Test Workload\n");
    printf("===========================================\n\n");

    // Test 1: Arithmetic
    printf("Test 1: Arithmetic Operations\n");
    printf("------------------------------\n");

    int a = 10, b = 20, c = 30;
    int result = (a + b) * c - (b / 2);
    printf("Result: %d\n", result);
    printf("✓ Arithmetic test passed\n\n");

    // Test 2: Array
    printf("Test 2: Array Operations\n");
    printf("------------------------\n");

    int array[ARRAY_SIZE];
    int sum = 0;

    for (int i = 0; i < ARRAY_SIZE; i++) {
        array[i] = i * 2;
    }

    for (int i = 0; i < ARRAY_SIZE; i++) {
        sum += array[i];
    }

    printf("Array sum: %d\n", sum);
    printf("✓ Array test passed\n\n");

    // Test 3: Branches
    printf("Test 3: Conditional Branches\n");
    printf("----------------------------\n");

    int even_count = 0, odd_count = 0;
    for (int i = 0; i < 50; i++) {
        if (i % 2 == 0) {
            even_count++;
        } else {
            odd_count++;
        }
    }

    printf("Even: %d, Odd: %d\n", even_count, odd_count);
    printf("✓ Branch test passed\n\n");

    printf("===========================================\n");
    printf("All tests completed successfully!\n");
    printf("===========================================\n");

    return 0;
}