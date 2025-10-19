#include <stdio.h>

int main() {
    int a = 5;
    int b = 10;
    int c = 0;
    int array[10];

    printf("Starting simple program run...\n");

    // Arithmetic operations
    c = a + b;
    c = c * 2;
    c = c - a;

    // Memory operations - write
    for (int i = 0; i < 10; i++) {
        array[i] = i * 2;
    }

    // Memory operations - read
    int sum = 0;
    for (int i = 0; i < 10; i++) {
        sum += array[i];
    }

    // Conditional branch
    if (sum > 50) {
        printf("Sum is greater than 50: %d\n", sum);
    } else {
        printf("Sum is less than or equal to 50: %d\n", sum);
    }

    printf("Final result: c=%d, sum=%d\n", c, sum);
    printf("Simple program run successfully!\n");

    return 0;
}