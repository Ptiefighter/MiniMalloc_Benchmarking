# MiniMalloc_Benchmarking

This repository contains the scripts, synthetic benchmark suites, and results used to evaluate the [MiniMalloc](https://github.com/google/minimalloc) memory allocator. The benchmarks were designed to test MiniMalloc under a variety of allocation patterns, including CNN-like workloads, random allocations, and stress tests with high memory overlap.

<!--## Getting Started

### Prerequisites

- Python 3.10+  
- [pandas](https://pandas.pydata.org/)  
- [numpy](https://numpy.org/)  
- [matplotlib](https://matplotlib.org/)  
- [seaborn](https://seaborn.pydata.org/)  
- [psutil](https://pypi.org/project/psutil/)  

Install Python dependencies with:

```bash
pip install pandas numpy matplotlib seaborn psutil
```

- C++ compiler to build MiniMalloc (g++ / clang++ / Visual Studio on Windows)
### Build MiniMalloc

Clone the official MiniMalloc repository and build the executable:

```bash
git clone https://github.com/google/minimalloc.git
cd minimalloc
mkdir build && cd build
cmake ..
cmake --build . -j$(nproc)
```

Copy the resulting executable to this repository or update the path in scripts/run_benchmarks.py.
-->
