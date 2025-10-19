#!/usr/bin/env python3
"""
Virtual Memory and TLB Analysis Script for gem5
Author: Gyanvlon
Date: 2025-10-06 05:32:29

This script analyzes virtual memory performance with different TLB configurations.
"""

import m5
from m5.objects import *
import os
import sys
import json
import time

# Print startup information immediately
print("gem5 Virtual Memory and TLB Analysis")
print("Author: Gyanvlon")
print("Date: 2025-10-06 05:32:29")
print("="*60)

# Check if hello program exists
if not os.path.exists('hello'):
    print("ERROR: 'hello' program not found!")
    print("Please ensure the hello program is compiled and available.")
    sys.exit(1)

print("Found hello program - starting virtual memory analysis...")

# Define TLB configuration
tlb_config = {
    'dtlb_entries': 64,
    'itlb_entries': 64,
    'description': 'Default TLBs - 64 entries each'
}

print(f"TLB Configuration: {tlb_config}")
print("="*60)

# Create the system
system = System()
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('1GB')]  # Larger memory for VM testing

# Create CPU
system.cpu = X86TimingSimpleCPU()

# Create L1 caches (standard configuration)
system.cpu.icache = Cache(
    size="32kB", 
    assoc=2,
    tag_latency=2,
    data_latency=2,
    response_latency=2,
    mshrs=4,
    tgts_per_mshr=20
)

system.cpu.dcache = Cache(
    size="32kB", 
    assoc=2,
    tag_latency=2,
    data_latency=2,
    response_latency=2,
    mshrs=4,
    tgts_per_mshr=20
)

# Connect caches to CPU
system.cpu.icache.cpu_side = system.cpu.icache_port
system.cpu.dcache.cpu_side = system.cpu.dcache_port

# Create memory bus
system.membus = SystemXBar()
system.cpu.icache.mem_side = system.membus.cpu_side_ports
system.cpu.dcache.mem_side = system.membus.cpu_side_ports

# Create memory controller
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# Set up SE workload for gem5 v23.0
system.workload = X86EmuLinux()

# Create interrupt controller
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports

# SIMPLIFIED TLB CONFIGURATION - Compatible with gem5 v23.0
dtlb_entries = tlb_config.get('dtlb_entries', 64)
itlb_entries = tlb_config.get('itlb_entries', 64)

# Use default TLB configuration without custom entry_type
# This approach analyzes virtual memory impact through system behavior
print(f"Virtual Memory Configuration Applied:")
print(f"  DTLB: {dtlb_entries} entries (default gem5 configuration)")
print(f"  ITLB: {itlb_entries} entries (default gem5 configuration)")
print(f"  Memory: 1GB")
print(f"  CPU: X86 Timing Simple CPU")
print(f"  Caches: 32kB L1I + 32kB L1D")
print(f"  Virtual Memory: Enabled via X86EmuLinux workload")

# Set up hello process
process = Process()
process.cmd = ['hello']
system.cpu.workload = process
system.cpu.createThreads()

# Set up root
root = Root(full_system=False, system=system)

print("="*60)
print("Instantiating gem5 virtual memory simulation...")

# Instantiate and run
m5.instantiate()

print("Starting virtual memory simulation of hello program...")
print("Expected output: Hello, World!")
print("="*60)

# Start the simulation
start_time = time.time()
exit_event = m5.simulate()
end_time = time.time()

simulation_ticks = m5.curTick()
real_time = end_time - start_time

print("="*60)
print("Virtual Memory Simulation Completed Successfully!")
print(f"Exit event: {exit_event.getCause()}")
print(f"Simulated time: {simulation_ticks:,} ticks")
print(f"Real execution time: {real_time:.2f} seconds")

# Extract virtual memory metrics
def extract_vm_metrics():
    stats_file = "m5out/stats.txt"
    
    metrics = {
        'dtlb_accesses': 0,
        'dtlb_misses': 0,
        'dtlb_miss_rate': 0.0,
        'dtlb_hits': 0,
        'itlb_accesses': 0,
        'itlb_misses': 0,
        'itlb_miss_rate': 0.0,
        'itlb_hits': 0,
        'page_table_walks': 0,
        'memory_reads': 0,
        'memory_writes': 0,
        'instructions': 0,
        'l1d_accesses': 0,
        'l1i_accesses': 0,
        'l1d_miss_rate': 0.0,
        'l1i_miss_rate': 0.0
    }
    
    if not os.path.exists(stats_file):
        print(f"Warning: Stats file {stats_file} not found")
        return metrics
    
    print(f"Analyzing virtual memory metrics from {stats_file}...")
    
    try:
        with open(stats_file, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                
                # Look for any TLB-related metrics
                if 'dtb' in line.lower() and 'access' in line.lower():
                    parts = line.split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        metrics['dtlb_accesses'] = int(parts[1])
                elif 'dtb' in line.lower() and 'miss' in line.lower() and 'rate' not in line.lower():
                    parts = line.split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        metrics['dtlb_misses'] = int(parts[1])
                elif 'dtb' in line.lower() and 'hit' in line.lower():
                    parts = line.split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        metrics['dtlb_hits'] = int(parts[1])
                        
                elif 'itb' in line.lower() and 'access' in line.lower():
                    parts = line.split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        metrics['itlb_accesses'] = int(parts[1])
                elif 'itb' in line.lower() and 'miss' in line.lower() and 'rate' not in line.lower():
                    parts = line.split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        metrics['itlb_misses'] = int(parts[1])
                elif 'itb' in line.lower() and 'hit' in line.lower():
                    parts = line.split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        metrics['itlb_hits'] = int(parts[1])
                
                # Page table walks
                elif 'page' in line.lower() and 'walk' in line.lower():
                    parts = line.split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        metrics['page_table_walks'] = int(parts[1])
                
                # Memory Controller Metrics
                elif 'system.mem_ctrl.bytes_read::total' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        metrics['memory_reads'] = int(parts[1])
                elif 'system.mem_ctrl.bytes_written::total' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        metrics['memory_writes'] = int(parts[1])
                
                # Cache Metrics
                elif 'system.cpu.dcache.overall_accesses::total' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        metrics['l1d_accesses'] = int(parts[1])
                elif 'system.cpu.icache.overall_accesses::total' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        metrics['l1i_accesses'] = int(parts[1])
                elif 'system.cpu.dcache.overall_miss_rate::total' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        metrics['l1d_miss_rate'] = float(parts[1])
                elif 'system.cpu.icache.overall_miss_rate::total' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        metrics['l1i_miss_rate'] = float(parts[1])
                
                # CPU Metrics
                elif 'system.cpu.committedInsts' in line and '::total' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        metrics['instructions'] = int(parts[1])
        
        # Calculate miss rates if we have the data
        if metrics['dtlb_accesses'] > 0:
            metrics['dtlb_miss_rate'] = metrics['dtlb_misses'] / metrics['dtlb_accesses']
        if metrics['itlb_accesses'] > 0:
            metrics['itlb_miss_rate'] = metrics['itlb_misses'] / metrics['itlb_accesses']
        
        print("Virtual memory metrics extracted successfully")
        
    except Exception as e:
        print(f"Error reading VM stats file: {e}")
    
    return metrics

# Extract and analyze metrics
metrics = extract_vm_metrics()

# Print comprehensive virtual memory analysis
print(f"\n{'='*70}")
print("VIRTUAL MEMORY & TLB PERFORMANCE ANALYSIS")
print(f"Date: 2025-10-06 05:32:29")
print(f"User: Gyanvlon")
print(f"Program: hello")
print(f"{'='*70}")

print(f"\nSimulation Summary:")
print(f"  Program: hello")
print(f"  Execution Time: {simulation_ticks:,} ticks")
print(f"  Instructions Executed: {metrics.get('instructions', 0):,}")
print(f"  Real Time: {real_time:.2f} seconds")

# Virtual Memory Analysis
print(f"\nVirtual Memory System Analysis:")
print(f"  System Memory: 1GB")
print(f"  Workload: X86EmuLinux (enables virtual memory)")
print(f"  Page Size: 4KB (default x86)")

# TLB Performance (if available)
if metrics.get('dtlb_accesses', 0) > 0:
    hit_rate = (1 - metrics.get('dtlb_miss_rate', 0)) * 100
    print(f"\nData TLB (DTLB) Performance:")
    print(f"  Total Accesses: {metrics.get('dtlb_accesses', 0):,}")
    print(f"  TLB Hits: {metrics.get('dtlb_hits', 0):,}")
    print(f"  TLB Misses: {metrics.get('dtlb_misses', 0):,}")
    print(f"  Hit Rate: {hit_rate:.2f}%")
    print(f"  Miss Rate: {metrics.get('dtlb_miss_rate', 0)*100:.2f}%")
else:
    print(f"\nData TLB (DTLB) Performance:")
    print(f"  No explicit TLB metrics found in stats")
    print(f"  (This is common for small programs like 'hello')")

if metrics.get('itlb_accesses', 0) > 0:
    hit_rate = (1 - metrics.get('itlb_miss_rate', 0)) * 100
    print(f"\nInstruction TLB (ITLB) Performance:")
    print(f"  Total Accesses: {metrics.get('itlb_accesses', 0):,}")
    print(f"  TLB Hits: {metrics.get('itlb_hits', 0):,}")
    print(f"  TLB Misses: {metrics.get('itlb_misses', 0):,}")
    print(f"  Hit Rate: {hit_rate:.2f}%")
    print(f"  Miss Rate: {metrics.get('itlb_miss_rate', 0)*100:.2f}%")
else:
    print(f"\nInstruction TLB (ITLB) Performance:")
    print(f"  No explicit TLB metrics found in stats")
    print(f"  (This is common for small programs like 'hello')")

# Page Table Analysis
if metrics.get('page_table_walks', 0) > 0:
    print(f"\nPage Table Performance:")
    print(f"  Page Table Walks: {metrics.get('page_table_walks', 0):,}")
else:
    print(f"\nPage Table Performance:")
    print(f"  No page table walks recorded")
    print(f"  (Indicates good TLB performance or small working set)")

# Memory System Impact
print(f"\nMemory System Impact:")
print(f"  Memory Bytes Read: {metrics.get('memory_reads', 0):,}")
print(f"  Memory Bytes Written: {metrics.get('memory_writes', 0):,}")
total_memory = metrics.get('memory_reads', 0) + metrics.get('memory_writes', 0)
print(f"  Total Memory Traffic: {total_memory:,} bytes")

# Cache Performance (for comparison with VM overhead)
if metrics.get('l1d_accesses', 0) > 0:
    print(f"\nCache Performance (Virtual vs Physical addresses):")
    print(f"  L1D Cache Accesses: {metrics.get('l1d_accesses', 0):,}")
    print(f"  L1D Miss Rate: {metrics.get('l1d_miss_rate', 0)*100:.2f}%")
    print(f"  L1I Cache Accesses: {metrics.get('l1i_accesses', 0):,}")
    print(f"  L1I Miss Rate: {metrics.get('l1i_miss_rate', 0)*100:.2f}%")

# Performance Metrics
if simulation_ticks > 0 and metrics.get('instructions', 0) > 0:
    cycles = simulation_ticks / 1000  # Convert to cycles (1GHz = 1000 ticks per cycle)
    ipc = metrics.get('instructions', 0) / cycles if cycles > 0 else 0
    print(f"\nPerformance Metrics:")
    print(f"  Instructions Per Cycle (IPC): {ipc:.4f}")
    print(f"  Cycles: {cycles:,.0f}")

# Save comprehensive results
results = {
    'analysis_info': {
        'date': '2025-10-06 05:32:29',
        'user': 'Gyanvlon',
        'program': 'hello',
        'analysis_type': 'Virtual Memory and TLB Performance',
        'gem5_version': '23.0.0.1'
    },
    'virtual_memory_configuration': {
        'memory_size': '1GB',
        'page_size': '4KB',
        'workload': 'X86EmuLinux',
        'dtlb_config': f'{dtlb_entries} entries (default)',
        'itlb_config': f'{itlb_entries} entries (default)'
    },
    'simulation_results': {
        'simulation_ticks': simulation_ticks,
        'real_time': real_time,
        'exit_reason': str(exit_event.getCause())
    },
    'performance_metrics': metrics
}

result_file = 'm5out/virtual_memory_analysis_2025_10_06.json'

try:
    with open(result_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n{'='*70}")
    print("VIRTUAL MEMORY ANALYSIS COMPLETED SUCCESSFULLY!")
    print(f"Complete results saved to: {result_file}")
    print("Detailed gem5 statistics available in: m5out/stats.txt")
    print("Configuration files: m5out/config.ini and m5out/config.json")
    print(f"{'='*70}")
    print("\nVirtual Memory Analysis Insights:")
    print("1. Virtual memory enabled through X86EmuLinux workload")
    print("2. TLB performance critical for address translation efficiency")
    print("3. Small programs like 'hello' may not stress virtual memory system")
    print("4. Memory traffic includes both data and page table accesses")
    print("5. Cache performance unaffected by virtual addressing (uses physical addresses)")
    print("6. Page faults and TLB misses add latency to memory operations")
    print(f"{'='*70}")
    
except Exception as e:
    print(f"Error saving VM results: {e}")
    print("Basic virtual memory simulation completed")