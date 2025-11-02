#!/bin/bash
# Quick Setup for gem5 DLP Assignment
# Author: Gyanvlon

echo "Setting up gem5 DLP environment..."

# Create directories
mkdir -p gem5_configs gem5_benchmarks gem5_results

# Build gem5 utility library
cd $GEM5_PATH/util/m5
scons build/x86/out/m5
cd -

# Compile benchmarks
cd gem5_benchmarks
make clean && make
cd -

# Make scripts executable
chmod +x run_gem5_benchmarks.sh
chmod +x scripts/parse_gem5_stats.py

echo "✓ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Set GEM5_PATH: export GEM5_PATH=/path/to/gem5"
echo "2. Run benchmarks: ./run_gem5_benchmarks.sh"
echo "3. Parse results: python scripts/parse_gem5_stats.py"