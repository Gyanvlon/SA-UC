#!/bin/bash
# Complete project execution script
# Author: Gyanvlon
# Date: October 25, 2025

echo "=========================================="
echo "IoT Microprocessor Project - Complete Run"
echo "=========================================="
echo ""

# Step 1: Compile workloads
echo "Step 1: Compiling workloads..."
bash scripts/compile_workloads.sh
if [ $? -ne 0 ]; then
    echo "ERROR: Workload compilation failed!"
    exit 1
fi

echo ""
echo "Press Enter to continue to simulations..."
read

# Step 2: Run DVFS comparison
echo ""
echo "Step 2: Running DVFS comparisons..."
echo "This will take 10-20 minutes..."
bash scripts/run_dvfs_comparison.sh

# Step 3: Analyze results
echo ""
echo "Step 3: Analyzing results..."
python3 scripts/analyze_results.py

echo ""
echo "=========================================="
echo "Project Execution Complete!"
echo "=========================================="
echo ""
echo "Generated files:"
echo "  - workloads/bin/* (compiled binaries)"
echo "  - results/m5out_*/ (simulation outputs)"
echo "  - results/comparison_report.csv"
echo ""
echo "View results:"
echo "  cat results/comparison_report.csv"
echo "  less results/m5out_balanced/stats.txt"
echo "=========================================="