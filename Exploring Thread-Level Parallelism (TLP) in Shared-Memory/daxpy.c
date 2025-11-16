#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <time.h>

static double *x;
static double *y;
static double a = 2.5;

typedef struct {
    long tid;
    long start;
    long end;
    long reps;
} thread_arg_t;

void *thread_daxpy(void *arg) {
    thread_arg_t *t = (thread_arg_t*)arg;
    long reps = t->reps;
    for (long r = 0; r < reps; ++r) {
        for (long i = t->start; i < t->end; ++i) {
            y[i] = a * x[i] + y[i];
        }
    }
    pthread_exit(NULL);
}

int main(int argc, char **argv) {
    if (argc < 4) {
        printf("Usage: %s <n> <threads> <reps>\n", argv[0]);
        return 1;
    }

    long n = atol(argv[1]);
    int threads = atoi(argv[2]);
    long reps = atol(argv[3]);

    x = (double*)aligned_alloc(64, n * sizeof(double));
    y = (double*)aligned_alloc(64, n * sizeof(double));
    if (!x || !y) {
        perror("alloc");
        return 1;
    }

    for (long i = 0; i < n; ++i) {
        x[i] = 1.0*i / (n+1);
        y[i] = 1.0;
    }

    pthread_t *tids = malloc(sizeof(pthread_t) * threads);
    thread_arg_t *args = malloc(sizeof(thread_arg_t) * threads);

    long base = n / threads;
    long rem = n % threads;
    long idx = 0;

    struct timespec ts_start, ts_end;
    clock_gettime(CLOCK_MONOTONIC, &ts_start);

    for (int t = 0; t < threads; ++t) {
        long chunk = base + (t < rem ? 1 : 0);
        args[t].tid = t;
        args[t].start = idx;
        args[t].end = idx + chunk;
        args[t].reps = reps;
        idx += chunk;
        if (pthread_create(&tids[t], NULL, thread_daxpy, &args[t]) != 0) {
            perror("pthread_create");
            return 1;
        }
    }

    for (int t = 0; t < threads; ++t) {
        pthread_join(tids[t], NULL);
    }

    clock_gettime(CLOCK_MONOTONIC, &ts_end);
    double elapsed = (ts_end.tv_sec - ts_start.tv_sec) + (ts_end.tv_nsec - ts_start.tv_nsec) * 1e-9;

    // Simple checksum to avoid optimizer removing work
    double sum = 0.0;
    for (long i = 0; i < n; ++i) sum += y[i];

    printf("n=%ld threads=%d reps=%ld time=%.6f checksum=%f\n", n, threads, reps, elapsed, sum);

    free(x); free(y); free(tids); free(args);
    return 0;
}