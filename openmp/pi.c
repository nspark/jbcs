#include <omp.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

double get_time(void) {
  struct timespec tp;
  clock_gettime(CLOCK_REALTIME, &tp);
  return (double)tp.tv_sec + 1e-9 * tp.tv_nsec;
}

#define TIMER(LABEL, EXPR)                                                     \
  do {                                                                         \
    double elapsed = get_time();                                               \
    (EXPR);                                                                    \
    elapsed = get_time() - elapsed;                                            \
    printf("Elapsed: %7.3f seconds [%s]\n", elapsed, LABEL);                   \
  } while (0)

double pi_serial(const size_t N) {
  size_t hits = 0;
  for (size_t i = 0; i < N; i++) {
    double x = drand48();
    double y = drand48();
    if (x * x + y * y < 1.0)
      hits++;
  }
  return 4.0 * hits / N;
}

double pi_omp1(const size_t N) {
  size_t hits = 0;
#pragma omp parallel for reduction(+ : hits)
  for (size_t i = 0; i < N; i++) {
    double x = drand48();
    double y = drand48();
    if (x * x + y * y < 1.0)
      hits++;
  }
  return 4.0 * hits / N;
}

double pi_omp2(const size_t N) {
  size_t hits = 0;
  const size_t seed = random();
#pragma omp parallel reduction(+ : hits)
  {
    struct drand48_data rngbuf;
    srand48_r(seed + omp_get_thread_num(), &rngbuf);
#pragma omp for
    for (size_t i = 0; i < N; i++) {
      double x, y;
      drand48_r(&rngbuf, &x);
      drand48_r(&rngbuf, &y);
      if (x * x + y * y < 1.0)
        hits++;
    }
  }
  return 4.0 * hits / N;
}

int main(int argc, char *argv[]) {
  if (argc > 2) {
    fprintf(stderr, "Usage: pi [niters]\n");
    return 1;
  }

  const size_t N = (argc == 2) ? strtoul(argv[1], NULL, 0) : (size_t)1e8;
  srand48(time(NULL));
  double pi = 0.0;

  TIMER("Serial", pi = pi_serial(N));
  printf("pi ≈ %.9f\n", pi);

  TIMER("OpenMP #1", pi = pi_omp1(N));
  printf("pi ≈ %.9f\n", pi);

  TIMER("OpenMP #2", pi = pi_omp2(N));
  printf("pi ≈ %.9f\n", pi);

  return 0;
}
