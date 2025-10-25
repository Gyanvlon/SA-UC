#!/usr/bin/env python3
"""
Analyze simulation results across DVFS operating points
Author: Gyanvlon
Date: October 25, 2025
"""

import os
import re
import sys

def parse_stats_file(stats_file):
    """Parse gem5 stats.txt"""

    if not os.path.exists(stats_file):
        return None

    metrics = {}

    try:
        with open(stats_file, 'r') as f:
            content = f.read()

        patterns = {
            'sim_seconds': r'sim_seconds\s+([\d.]+)',
            'sim_insts': r'sim_insts\s+([\d]+)',
            'ipc': r'system\.cpu\.ipc\s+([\d.]+)',
            'icache_miss_rate': r'system\.cpu\.icache\.overallMissRate::total\s+([\d.]+)',
            'dcache_miss_rate': r'system\.cpu\.dcache\.overallMissRate::total\s+([\d.]+)',
            'l2cache_miss_rate': r'system\.l2cache\.overallMissRate::total\s+([\d.]+)',
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, content)
            metrics[key] = float(match.group(1)) if match else 0.0

        metrics['icache_hit_rate'] = 1.0 - metrics.get('icache_miss_rate', 0.0)
        metrics['dcache_hit_rate'] = 1.0 - metrics.get('dcache_miss_rate', 0.0)
        metrics['l2cache_hit_rate'] = 1.0 - metrics.get('l2cache_miss_rate', 0.0)

        return metrics

    except Exception as e:
        print(f"Error parsing {stats_file}: {e}")
        return None


def generate_comparison_table(results):
    """Generate comparison table"""

    print("\n" + "="*90)
    print("IoT Microprocessor - DVFS Operating Point Comparison")
    print("="*90)
    print()

    print(f"{'Operating Point':<18} {'Sim Time (s)':<15} {'IPC':<10} "
          f"{'I$ Hit':<10} {'D$ Hit':<10} {'L2 Hit':<10}")
    print("-"*90)

    for op in ['low_power', 'balanced', 'high_perf', 'max_perf']:
        if op in results and results[op]:
            m = results[op]
            print(f"{op:<18} "
                  f"{m['sim_seconds']:<15.9f} "
                  f"{m['ipc']:<10.4f} "
                  f"{m['icache_hit_rate']*100:<9.2f}% "
                  f"{m['dcache_hit_rate']*100:<9.2f}% "
                  f"{m['l2cache_hit_rate']*100:<9.2f}%")

    print("="*90)
    print()


def generate_detailed_analysis(results):
    """Generate detailed analysis"""

    print("="*90)
    print("Detailed Performance Analysis")
    print("="*90)
    print()

    valid_results = {k: v for k, v in results.items() if v is not None}

    if not valid_results:
        print("No valid results found!")
        return

    best_ipc_op = max(valid_results.keys(), key=lambda x: valid_results[x]['ipc'])
    print(f"Highest IPC:")
    print(f"  Operating Point: {best_ipc_op}")
    print(f"  IPC Value: {valid_results[best_ipc_op]['ipc']:.4f}")
    print()

    fastest_op = min(valid_results.keys(), key=lambda x: valid_results[x]['sim_seconds'])
    print(f"Fastest Execution:")
    print(f"  Operating Point: {fastest_op}")
    print(f"  Execution Time: {valid_results[fastest_op]['sim_seconds']:.9f} seconds")
    print()

    if 'low_power' in valid_results and 'max_perf' in valid_results:
        speedup = valid_results['low_power']['sim_seconds'] / valid_results['max_perf']['sim_seconds']
        print(f"Performance Scaling:")
        print(f"  Speedup (low_power → max_perf): {speedup:.2f}x")
        print()

    print("Cache Performance Summary:")
    for op in ['low_power', 'balanced', 'high_perf', 'max_perf']:
        if op in valid_results:
            m = valid_results[op]
            print(f"  {op}:")
            print(f"    L1 I-Cache Hit Rate: {m['icache_hit_rate']*100:.2f}%")
            print(f"    L1 D-Cache Hit Rate: {m['dcache_hit_rate']*100:.2f}%")
            print(f"    L2 Cache Hit Rate:   {m['l2cache_hit_rate']*100:.2f}%")

    print()
    print("="*90)
    print()


def save_csv_report(results):
    """Save CSV report"""

    filename = 'results/comparison_report.csv'

    try:
        with open(filename, 'w') as f:
            f.write("Operating Point,Sim Time (s),IPC,Instructions,")
            f.write("I-Cache Hit Rate,D-Cache Hit Rate,L2 Hit Rate\n")

            for op in ['low_power', 'balanced', 'high_perf', 'max_perf']:
                if op in results and results[op]:
                    m = results[op]
                    f.write(f"{op},{m['sim_seconds']:.9f},{m['ipc']:.4f},")
                    f.write(f"{int(m['sim_insts'])},")
                    f.write(f"{m['icache_hit_rate']:.6f},{m['dcache_hit_rate']:.6f},")
                    f.write(f"{m['l2cache_hit_rate']:.6f}\n")

        print(f"✓ CSV report saved to: {filename}")
        print()

    except Exception as e:
        print(f"Error saving CSV: {e}")


def main():
    """Main analysis function"""

    print("\n" + "="*90)
    print("IoT Microprocessor Results Analysis")
    print("="*90)
    print()

    results = {}
    operating_points = ['low_power', 'balanced', 'high_perf', 'max_perf']

    print("Loading simulation results...")
    for op in operating_points:
        stats_file = f"results/m5out_{op}/stats.txt"
        print(f"  {op}: ", end='')

        metrics = parse_stats_file(stats_file)
        if metrics:
            results[op] = metrics
            print("✓ Loaded")
        else:
            print("✗ Not found")
            results[op] = None

    print()

    valid_count = sum(1 for v in results.values() if v is not None)

    if valid_count == 0:
        print("ERROR: No simulation results found!")
        print("\nPlease run simulations first:")
        print("  bash scripts/run_dvfs_comparison.sh")
        sys.exit(1)

    generate_comparison_table(results)
    generate_detailed_analysis(results)
    save_csv_report(results)

    print("Analysis complete!")
    print()


if __name__ == '__main__':
    main()
linuxking@Dev-PC:~/gem5/iot_microprocessor_project/scripts$ ls
analyze_results.py  compile_workloads.sh  run_dvfs_comparison.sh  run_single_sim.sh
linuxking@Dev-PC:~/gem5/iot_microprocessor_project/scripts$ cat  compile_workloads.sh
#!/bin/bash
# Compile all workloads for ARM
# Author: Gyanvlon

echo "=========================================="
echo "Compiling IoT Microprocessor Workloads"
echo "=========================================="

# Check compiler
if ! command -v arm-linux-gnueabi-gcc &> /dev/null; then
    echo "ERROR: ARM compiler not found!"
    echo "Install: sudo apt-get install gcc-arm-linux-gnueabi"
    exit 1
fi

SRC_DIR="workloads/source"
BIN_DIR="workloads/bin"
mkdir -p $BIN_DIR

CFLAGS="-O2 -march=armv7-a -static -lm"

echo ""
echo "Compiling workloads..."
echo "----------------------"

# Simple test
echo -n "1. simple_test.c ... "
arm-linux-gnueabi-gcc $CFLAGS $SRC_DIR/simple_test.c -o $BIN_DIR/simple_test
[ $? -eq 0 ] && echo "✓ Success" || { echo "✗ Failed"; exit 1; }

# Sensor simulation
echo -n "2. sensor_simulation.c ... "
arm-linux-gnueabi-gcc $CFLAGS $SRC_DIR/sensor_simulation.c -o $BIN_DIR/sensor_simulation
[ $? -eq 0 ] && echo "✓ Success" || { echo "✗ Failed"; exit 1; }

# Matrix multiply
echo -n "3. matrix_multiply.c ... "
arm-linux-gnueabi-gcc $CFLAGS $SRC_DIR/matrix_multiply.c -o $BIN_DIR/matrix_multiply
[ $? -eq 0 ] && echo "✓ Success" || { echo "✗ Failed"; exit 1; }

echo ""
echo "=========================================="
echo "Compilation Complete!"
echo "=========================================="
echo ""
echo "Compiled binaries:"
ls -lh $BIN_DIR/

echo ""
echo "Verifying ARM binaries:"
for binary in $BIN_DIR/*; do
    if [ -f "$binary" ]; then
        echo -n "$(basename $binary): "
        file $binary | grep -q "ARM" && echo "✓ ARM" || echo "✗ Not ARM"
    fi
done
echo ""