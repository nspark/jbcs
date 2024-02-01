# Parallel Programming Workshop Exercises

Jean Bartik Computing Symposium 2024

## Python

```shell
% cd python
% python -m venv env
% source env/bin/activate
% pip install -r requirements.txt
% python pi.py
% python mandel.py image.ppm
```

## C + OpenMP

```shell
% cd openmp
% mkdir build && cd build
% cmake .. && make
% ./pi
% ./mandel image.ppm
```
