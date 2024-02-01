#include <math.h>
#include <stdint.h>
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

void mandel(double *data, size_t max_iters, size_t width, size_t height,
            double x0, double y0, double x1, double y1) {
  for (uint32_t h = 0; h < height; h++) {
    for (uint32_t w = 0; w < width; w++) {
      double t, x = 0.0, y = 0.0;
      double px = ((x1 - x0) / (width - 1)) * w + x0;
      double py = ((y1 - y0) / (height - 1)) * h + y0;
      uint32_t i;
      for (i = 0; (i < max_iters) && (x * x + y * y < 4.0); i++) {
        t = x * x - y * y + px;
        y = 2 * x * y + py;
        x = t;
      }
      data[h * width + w] = log(i);
    }
  }
}

void hsv_to_rgb(uint8_t rgb[3], double hue, double sat, double val) {
  uint32_t h = hue * 3600;
  uint32_t s = sat * 1000;
  uint32_t v = val * 1000;

  if (s == 0) {
    rgb[2] = rgb[1] = rgb[0] = (255 * v) / 1000;
  } else {
    uint32_t h_ = h / 600;
    uint32_t f = ((h % 600) * 1000) / 600;
    uint32_t p = (v * (1000 - s)) / 1000;
    uint32_t q = (v * (1000 - ((s * f) / 1000))) / 1000;
    uint32_t t = (v * (1000 - ((s * (1000 - f)) / 1000))) / 1000;

    switch (h_) {
    case 0:
      rgb[0] = (255 * v) / 1000;
      rgb[1] = (255 * t) / 1000;
      rgb[2] = (255 * p) / 1000;
      break;

    case 1:
      rgb[0] = (255 * q) / 1000;
      rgb[1] = (255 * v) / 1000;
      rgb[2] = (255 * p) / 1000;
      break;

    case 2:
      rgb[0] = (255 * p) / 1000;
      rgb[1] = (255 * v) / 1000;
      rgb[2] = (255 * t) / 1000;
      break;

    case 3:
      rgb[0] = (255 * p) / 1000;
      rgb[1] = (255 * q) / 1000;
      rgb[2] = (255 * v) / 1000;
      break;

    case 4:
      rgb[0] = (255 * t) / 1000;
      rgb[1] = (255 * p) / 1000;
      rgb[2] = (255 * v) / 1000;
      break;

    case 5:
      rgb[0] = (255 * v) / 1000;
      rgb[1] = (255 * p) / 1000;
      rgb[2] = (255 * q) / 1000;
      break;
    }
  }
}

int main(/* int argc, char *argv[] */) {
  // Argument parsing
  const char *image_name = "image.ppm";
  const uint32_t resolution = 500;
  const double x0 = -2.5;
  const double y0 = -1.5;
  const double x1 = 1.5;
  const double y1 = 1.5;
  uint32_t height = (y1 - y0) * resolution;
  uint32_t width = (x1 - x0) * resolution;
  size_t max_iters = 1000;

  // Allocate data
  double *data = (double *)calloc(width * height, sizeof(*data));
  if (data == NULL) {
    fprintf(stderr, "Error: Failed to allocate memory\n ");
    return 1;
  }

  // Generate Mandelbrot image
  TIMER("Serial", mandel(data, max_iters, width, height, x0, y0, x1, y1));

  // Output
  FILE *f = fopen(image_name, "w");
  fprintf(f, "P6\n%u %u\n255\n", width, height);
  for (size_t i = 0; i < width * height; i++) {
    uint8_t color[3] = {0, 0, 6};
    hsv_to_rgb(color, data[i] / log(max_iters + 1), 1.0, 1.0);
    fwrite(color, 3, sizeof(uint8_t), f);
  }
  fclose(f);
  free(data);

  return 0;
}
