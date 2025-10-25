#!/usr/bin/env python3
"""
Extract enhanced comparison report with power metrics
Author: Gyanvlon
Date: 2025-10-25
"""

import os
import re
import csv
import sys

def parse_stats_file(stats_file):
    """Parse stats file and extract metrics"""
    
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
            'num_cycles': r'system\.cpu\.numCycles\s+([\d]+)',
            'icache_miss_rate': r'system\.cpu\.icache\.overallMissRate::total\s+([\d.]+)',
            'dcache_miss_rate': r'system\.cpu\.dcache\.overallMissRate::total\s+([\d.]+)',
            'l2cache_miss_rate': r'system\.l2cache\.overallMissRate::total\s+([\d.]+)',
            'icache_misses': r'system\.cpu\.icache\.overallMisses::total\s+([\d]+)',
            'dcache_misses': r'system\.cpu\.dcache\.overallMisses::total\s+([\d]+)',
            'l2cache_misses': r'system\.l2cache\.overallMisses::total\s+([\d]+)',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, content)
            metrics[key] = float(match.group(1)) if match else 0.0
        
        # Calculate hit rates
        metrics['icache_hit_rate'] = 1.0 - metrics.get('icache_miss_rate', 0.0)
        metrics['dcache_hit_rate'] = 1.0 - metrics.get('dcache_miss_rate', 0.0)
        metrics['l2cache_hit_rate'] = 1.0 - metrics.get('l2cache_miss_rate', 0.0)
        
        return metrics
        
    except Exception as e:
        print(f"Error: {e}")
        return None


def calculate_power_metrics(metrics, op_name):
    """Calculate estimated power metrics"""
    
    op_params = {
        'low_power': (100e6, 0.6),
        'balanced': (200e6, 0.75),
        'high_perf': (350e6, 0.9),
        'max_perf': (500e6, 1.0)
    }
    
    freq, voltage = op_params.get(op_name, (200e6, 0.75))
    
    # Simplified power model
    base_cap = 50e-12  # 50 pF
    activity = 0.5  # Default activity factor
    
    dynamic_power = base_cap * (voltage ** 2) * freq * activity
    static_power = 0.003 * (voltage ** 1.5)  # 3mW base at 1.0V
    total_power = dynamic_power + static_power
    
    total_energy = total_power * metrics['sim_seconds']
    energy_per_inst = total_energy / metrics['sim_insts'] if metrics['sim_insts'] > 0 else 0
    
    return {
        'frequency_MHz': freq / 1e6,
        'voltage_V': voltage,
        'dynamic_power_mW': dynamic_power * 1000,
        'static_power_mW': static_power * 1000,
        'total_power_mW': total_power * 1000,
        'total_energy_mJ': total_energy * 1000,
        'energy_per_inst_pJ': energy_per_inst * 1e12
    }


def generate_enhanced_csv(output_file='results/comparison_report_enhanced.csv'):
    """Generate enhanced CSV with power metrics"""
    
    print("\n" + "="*80)
    print("Generating Enhanced Comparison Report CSV")
    print("="*80)
    print()
    
    operating_points = ['low_power', 'balanced', 'high_perf', 'max_perf']
    all_data = {}
    
    for op in operating_points:
        stats_file = f'results/m5out_{op}/stats.txt'
        print(f"Processing {op}...")
        
        metrics = parse_stats_file(stats_file)
        if metrics:
            power_metrics = calculate_power_metrics(metrics, op)
            all_data[op] = {**metrics, **power_metrics}
            print(f"  ✓ Extracted metrics with power data")
        else:
            print(f"  ✗ Failed")
    
    if not all_data:
        print("\nERROR: No data found!")
        sys.exit(1)
    
    # Create enhanced CSV
    try:
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = [
                'Operating Point',
                'Frequency (MHz)',
                'Voltage (V)',
                'Sim Time (s)',
                'IPC',
                'Instructions',
                'I-Cache Hit Rate (%)',
                'D-Cache Hit Rate (%)',
                'L2 Hit Rate (%)',
                'Total Power (mW)',
                'Dynamic Power (mW)',
                'Static Power (mW)',
                'Energy per Inst (pJ)',
                'Total Energy (mJ)'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for op in operating_points:
                if op in all_data:
                    d = all_data[op]
                    writer.writerow({
                        'Operating Point': op,
                        'Frequency (MHz)': f"{d['frequency_MHz']:.0f}",
                        'Voltage (V)': f"{d['voltage_V']:.2f}",
                        'Sim Time (s)': f"{d['sim_seconds']:.9f}",
                        'IPC': f"{d['ipc']:.6f}",
                        'Instructions': int(d['sim_insts']),
                        'I-Cache Hit Rate (%)': f"{d['icache_hit_rate']*100:.2f}",
                        'D-Cache Hit Rate (%)': f"{d['dcache_hit_rate']*100:.2f}",
                        'L2 Hit Rate (%)': f"{d['l2cache_hit_rate']*100:.2f}",
                        'Total Power (mW)': f"{d['total_power_mW']:.2f}",
                        'Dynamic Power (mW)': f"{d['dynamic_power_mW']:.2f}",
                        'Static Power (mW)': f"{d['static_power_mW']:.2f}",
                        'Energy per Inst (pJ)': f"{d['energy_per_inst_pJ']:.3f}",
                        'Total Energy (mJ)': f"{d['total_energy_mJ']:.4f}"
                    })
        
        print()
        print("="*80)
        print(f"✓ Enhanced CSV created: {output_file}")
        print("="*80)
        print()
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False


if __name__ == '__main__':
    generate_enhanced_csv()
