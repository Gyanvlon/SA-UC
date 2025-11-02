#!/usr/bin/env python3
"""
Parse gem5 Statistics
Author: Gyanvlon
Date: 2025-11-02
"""

import re
import pandas as pd
from pathlib import Path

def parse_stats_file(stats_file):
    """Parse gem5 stats.txt file"""
    stats = {}
    
    with open(stats_file, 'r') as f:
        for line in f:
            if '::' in line and not line.startswith('#'):
                parts = line.split()
                if len(parts) >= 2:
                    key = parts[0]
                    value = parts[1]
                    try:
                        stats[key] = float(value)
                    except ValueError:
                        stats[key] = value
    
    return stats

def extract_key_metrics(stats):
    """Extract important DLP metrics"""
    metrics = {
        'sim_seconds': stats.get('sim_seconds', 0),
        'sim_ticks': stats.get('sim_ticks', 0),
        'sim_insts': stats.get('system.cpu.committedInsts', 0),
        'ipc': stats.get('system.cpu.ipc', 0),
        'dcache_hit_rate': stats.get('system.cpu.dcache.overallHits::total', 0) / 
                          stats.get('system.cpu.dcache.overallAccesses::total', 1),
        'icache_hit_rate': stats.get('system.cpu.icache.overallHits::total', 0) / 
                          stats.get('system.cpu.icache.overallAccesses::total', 1),
    }
    
    return metrics

def main():
    results_dir = Path('gem5_results')
    all_metrics = []
    
    for stats_file in results_dir.rglob('stats.txt'):
        config_name = stats_file.parent.name
        stats = parse_stats_file(stats_file)
        metrics = extract_key_metrics(stats)
        metrics['config'] = config_name
        all_metrics.append(metrics)
    
    # Create DataFrame
    df = pd.DataFrame(all_metrics)
    df.to_csv('gem5_results/summary.csv', index=False)
    
    print("gem5 Statistics Summary:")
    print(df.to_string())

if __name__ == "__main__":
    main()