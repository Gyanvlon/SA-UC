import re
import sys
import os
from pathlib import Path

def parse_stats_file(filename):
    """Parse gem5 stats.txt file"""

    stats = {}

    if not os.path.exists(filename):
        print(f"Warning: {filename} not found")
        return stats

    with open(filename, 'r') as f:
        for line in f:
            # Skip comments and empty lines
            if line.startswith('#') or not line.strip():
                continue

            # Parse stat lines
            parts = line.split()
            if len(parts) >= 2:
                stat_name = parts[0]
                stat_value = parts[1]

                try:
                    # Try to convert to number
                    if '.' in stat_value:
                        stats[stat_name] = float(stat_value)
                    else:
                        stats[stat_name] = int(stat_value)
                except ValueError:
                    stats[stat_name] = stat_value

    return stats

def analyze_experiment(name, stats_file):
    """Analyze a single experiment"""

    print(f"\n{'='*60}")
    print(f"{name}")
    print(f"{'='*60}")

    stats = parse_stats_file(stats_file)

    if not stats:
        print("No statistics found!")
        return None

    # Extract key metrics
    results = {}

    # Try different stat names (gem5 versions vary)
    insts_keys = ['system.cpu.numInsts', 'system.cpu.commitStats0.committedInsts']
    cycles_key = 'system.cpu.numCycles'

    insts = None
    for key in insts_keys:
        if key in stats:
            insts = stats[key]
            break

    cycles = stats.get(cycles_key, 0)

    if insts and cycles:
        ipc = insts / cycles
        cpi = cycles / insts

        results['instructions'] = insts
        results['cycles'] = cycles
        results['ipc'] = ipc
        results['cpi'] = cpi

        print(f"Total Instructions: {int(insts):,}")
        print(f"Total Cycles: {int(cycles):,}")
        print(f"IPC: {ipc:.4f}")
        print(f"CPI: {cpi:.4f}")

        # Branch prediction stats
        bp_predicted = stats.get('system.cpu.branchPred.condPredicted', 0)
        bp_incorrect = stats.get('system.cpu.branchPred.condIncorrect', 0)

        if bp_predicted > 0:
            bp_accuracy = ((bp_predicted - bp_incorrect) / bp_predicted) * 100
            results['branch_accuracy'] = bp_accuracy
            print(f"Branch Accuracy: {bp_accuracy:.2f}%")

    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_results.py <results_directory>")
        sys.exit(1)

    results_dir = Path(sys.argv[1])

    print("\n" + "="*60)
    print("ILP EXPERIMENTS ANALYSIS")
    print("="*60)

    # Analyze each experiment
    all_results = {}

    # 1. Pipeline
    pipeline_stats = results_dir / "pipeline" / "stats.txt"
    if pipeline_stats.exists():
        all_results['pipeline'] = analyze_experiment("BASIC PIPELINE", pipeline_stats)

    # 2. Branch Prediction
    bp_types = ['none', 'local', 'tournament', 'bimode']
    all_results['branch_prediction'] = {}

    for bp_type in bp_types:
        bp_stats = results_dir / "branch_pred" / bp_type / "stats.txt"
        if bp_stats.exists():
            result = analyze_experiment(f"BRANCH PREDICTION - {bp_type.upper()}", bp_stats)
            if result:
                all_results['branch_prediction'][bp_type] = result

    # 3. Superscalar
    widths = [1, 2, 4, 8]
    all_results['superscalar'] = {}

    for width in widths:
        ss_stats = results_dir / "superscalar" / f"width_{width}" / "stats.txt"
        if ss_stats.exists():
            result = analyze_experiment(f"SUPERSCALAR - {width}-WIDE", ss_stats)
            if result:
                all_results['superscalar'][width] = result

    # 4. SMT
    thread_counts = [1, 2, 4]
    all_results['smt'] = {}

    for threads in thread_counts:
        smt_stats = results_dir / "smt" / f"threads_{threads}" / "stats.txt"
        if smt_stats.exists():
            result = analyze_experiment(f"SMT - {threads} THREAD(S)", smt_stats)
            if result:
                all_results['smt'][threads] = result

    # Generate summary report
    generate_summary_report(results_dir, all_results)

    print("\n" + "="*60)
    print("Analysis complete!")
    print(f"Results directory: {results_dir}")
    print("="*60 + "\n")

def generate_summary_report(results_dir, all_results):
    """Generate text summary report"""

    report_file = results_dir / "summary_report.txt"

    with open(report_file, 'w') as f:
        f.write("="*70 + "\n")
        f.write("ILP EXPERIMENTS - SUMMARY REPORT\n")
        f.write("="*70 + "\n\n")

        # Pipeline
        if 'pipeline' in all_results and all_results['pipeline']:
            f.write("1. BASIC PIPELINE\n")
            f.write("-" * 50 + "\n")
            r = all_results['pipeline']
            f.write(f"   Instructions: {int(r['instructions']):,}\n")
            f.write(f"   Cycles: {int(r['cycles']):,}\n")
            f.write(f"   IPC: {r['ipc']:.4f}\n")
            f.write(f"   CPI: {r['cpi']:.4f}\n\n")

        # Branch Prediction
        if 'branch_prediction' in all_results and all_results['branch_prediction']:
            f.write("2. BRANCH PREDICTION\n")
            f.write("-" * 50 + "\n")
            for bp_type, r in all_results['branch_prediction'].items():
                f.write(f"   {bp_type.upper()}:\n")
                f.write(f"      IPC: {r['ipc']:.4f}\n")
                if 'branch_accuracy' in r:
                    f.write(f"      Accuracy: {r['branch_accuracy']:.2f}%\n")
            f.write("\n")

        # Superscalar
        if 'superscalar' in all_results and all_results['superscalar']:
            f.write("3. SUPERSCALAR\n")
            f.write("-" * 50 + "\n")
            baseline_cycles = None
            for width, r in sorted(all_results['superscalar'].items()):
                if baseline_cycles is None:
                    baseline_cycles = r['cycles']
                speedup = baseline_cycles / r['cycles']
                f.write(f"   {width}-Wide:\n")
                f.write(f"      IPC: {r['ipc']:.4f}\n")
                f.write(f"      Speedup: {speedup:.2f}x\n")
            f.write("\n")

        # SMT
        if 'smt' in all_results and all_results['smt']:
            f.write("4. SIMULTANEOUS MULTITHREADING (SMT)\n")
            f.write("-" * 50 + "\n")
            baseline_ipc = None
            for threads, r in sorted(all_results['smt'].items()):
                if baseline_ipc is None:
                    baseline_ipc = r['ipc']
                throughput_gain = r['ipc'] / baseline_ipc
                f.write(f"   {threads} Thread(s):\n")
                f.write(f"      IPC: {r['ipc']:.4f}\n")
                f.write(f"      Throughput Gain: {throughput_gain:.2f}x\n")
            f.write("\n")

        f.write("="*70 + "\n")

    print(f"\nSummary report saved to: {report_file}")

if __name__ == '__main__':
    main()