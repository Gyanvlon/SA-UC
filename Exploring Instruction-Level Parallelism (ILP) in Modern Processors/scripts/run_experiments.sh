#!/bin/bash

# Master script to run all ILP experiments
# Filename: scripts/run_experiments.sh

# Configuration - Auto-detect project directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
GEM5_PATH="$HOME/gem5"
GEM5_BUILD="$GEM5_PATH/build/X86/gem5.opt"
RESULTS_DIR="results"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "======================================"
echo " ILP EXPERIMENTS RUNNER"
echo "======================================"
echo ""
echo "Project Directory: $PROJECT_DIR"
echo "gem5 Build: $GEM5_BUILD"
echo ""

# Check if gem5 exists
if [ ! -f "$GEM5_BUILD" ]; then
    echo -e "${RED}Error: gem5 not found at $GEM5_BUILD${NC}"
    echo "Please build gem5 first:"
    echo "  cd ~/gem5"
    echo "  scons build/X86/gem5.opt -j\$(nproc)"
    exit 1
fi

# Navigate to project directory
cd "$PROJECT_DIR" || exit 1
echo "Working directory: $(pwd)"
echo ""

# Verify workloads exist
echo "Checking workloads..."
for workload in simple_test branch_intensive matrix_multiply multithreaded; do
    if [ ! -f "workloads/$workload" ]; then
        echo -e "${RED}Error: workloads/$workload not found!${NC}"
        echo "Please compile: cd workloads && gcc -static -o $workload ${workload}.c"
        exit 1
    fi
done
echo -e "${GREEN}✓ All workloads found${NC}"
echo ""

# Create results directories
mkdir -p $RESULTS_DIR/{pipeline,branch_pred/{none,local,tournament,bimode},superscalar,smt}

# Experiment 1: Basic Pipeline
echo -e "\n${GREEN}[1/4] Running Basic Pipeline Simulation...${NC}"
echo "=========================================="

$GEM5_BUILD \
    --outdir=$RESULTS_DIR/pipeline \
    configs/simple_pipeline.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Pipeline simulation complete${NC}"
else
    echo -e "${RED}✗ Pipeline simulation failed${NC}"
fi

# Experiment 2: Branch Prediction
echo -e "\n${GREEN}[2/4] Running Branch Prediction Experiments...${NC}"
echo "=========================================="

for bp_type in none local tournament bimode; do
    echo -e "${YELLOW}Testing $bp_type predictor...${NC}"

    $GEM5_BUILD \
        --outdir=$RESULTS_DIR/branch_pred/$bp_type \
        configs/branch_prediction.py \
        $bp_type \
        workloads/branch_intensive

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $bp_type predictor complete${NC}"
    else
        echo -e "${RED}✗ $bp_type predictor failed${NC}"
    fi
done

# Experiment 3: Superscalar
echo -e "\n${GREEN}[3/4] Running Superscalar Experiments...${NC}"
echo "=========================================="

for width in 1 2 4 8; do
    echo -e "${YELLOW}Testing $width-wide issue...${NC}"

    mkdir -p $RESULTS_DIR/superscalar/width_$width

    $GEM5_BUILD \
        --outdir=$RESULTS_DIR/superscalar/width_$width \
        configs/superscalar.py \
        $width \
        workloads/matrix_multiply

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $width-wide complete${NC}"
    else
        echo -e "${RED}✗ $width-wide failed${NC}"
    fi
done

# Experiment 4: SMT
echo -e "\n${GREEN}[4/4] Running SMT Experiments...${NC}"
echo "=========================================="

for threads in 1 2 4; do
    echo -e "${YELLOW}Testing $threads hardware thread(s)...${NC}"

    mkdir -p $RESULTS_DIR/smt/threads_$threads

    $GEM5_BUILD \
        --outdir=$RESULTS_DIR/smt/threads_$threads \
        configs/smt_config.py \
        $threads \
        workloads/multithreaded

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $threads thread(s) complete${NC}"
    else
        echo -e "${RED}✗ $threads thread(s) failed${NC}"
    fi
done

# Generate analysis
echo -e "\n${GREEN}Generating Analysis Reports...${NC}"
echo "=========================================="

python3 scripts/analyze_results.py $RESULTS_DIR

echo -e "\n======================================"
echo -e "${GREEN}ALL EXPERIMENTS COMPLETE!${NC}"
echo "======================================"
echo ""
echo "Results are available in the $RESULTS_DIR/ directory:"
echo "  - stats.txt files for each experiment"
echo "  - summary_report.txt with all findings"
echo ""
echo "Next steps:"
echo "  1. Review results: less $RESULTS_DIR/summary_report.txt"
echo "  2. Take screenshots of key statistics"
echo "  3. Write your report using the data"
echo ""