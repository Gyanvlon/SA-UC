#!/usr/bin/env python3
"""
Simple Cache Configuration Script for gem5
Author: Gyanvlon
Date: 2025-10-06 05:01:21

This script runs hello program with cache configurations and provides memory analysis.
"""

import m5
from m5.objects import *
import os
import sys
import json
import time

# Print startup information
print("gem5 Cache Configuration Analysis")
print("Author: Gyanvlon") 
print("Date: 2025-10-06 05:01:21")
print("="*50)

# Check if hello program exists
if not os.path.exists('hello'):
    print("ERROR: 'hello' program not found!")
    sys.exit(1)

print("Found hello program - starting simulation setup...")

# Create the system
system = System()

# Set the clock frequency
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

# Set up memory
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

# Create a simple CPU
system.cpu = X86TimingSimpleCPU()

# Create an L1 instruction and data cache
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

# Connect the instruction and data caches to the CPU
system.cpu.icache.cpu_side = system.cpu.icache_port
system.cpu.dcache.cpu_side = system.cpu.dcache_port

# Create a memory bus
system.membus = SystemXBar()

# Connect the caches to the memory bus
system.cpu.icache.mem_side = system.membus.cpu_side_ports
system.cpu.dcache.mem_side = system.membus.cpu_side_ports

# Create a DDR3 memory controller
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# CRITICAL FIX: Create proper SE workload for gem5 v23.0
system.workload = X86EmuLinux()

# Create the interrupt controller for X86
system.cpu.createInterruptController()

# FIX: Connect interrupt ports properly without double connection
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
# REMOVED: Don't connect int_responder to avoid double connection error

# Create the hello process
print("Setting up hello program as workload...")

process = Process()
process.cmd = ['hello']
system.cpu.workload = process
system.cpu.createThreads()

print("Cache Configuration:")
print("  L1I Cache: 32kB, 2-way, 2-cycle latency")
print("  L1D Cache: 32kB, 2-way, 2-cycle latency") 
print("  Memory: 512MB DDR3")
print("  CPU: X86 Timing Simple CPU")
print("  Workload: hello program")
print("  SE Workload: X86EmuLinux")
print("="*50)

# Set up the root SimObject
root = Root(full_system=False, system=system)

print("Instantiating gem5 simulation...")

# Instantiate all objects
m5.instantiate()

print("Starting simulation of hello program...")
print("Expected output: Hello, World!")
print("="*50)

# Start the simulation
start_time = time.time()
exit_event = m5.simulate()
end_time = time.time()

# Print simulation results
print("="*50)
print("Simulation Completed Successfully!")
print(f"Exit event: {exit_event.getCause()}")
print(f"Simulated time: {m5.curTick():,} ticks")
print(f"Real execution time: {end_time - start_time:.2f} seconds")

# Extract performance metrics from stats
def extract_and_analyze_metrics():
    stats_file = "m5out/stats.txt"
    metrics = {
        'l1d_miss_rate': 0.0,
        'l1i_miss_rate': 0.0,
        'l1d_accesses': 0,
        'l1i_accesses': 0,
        'l1d_misses': 0,
        'l1i_misses': 0,
        'memory_reads': 0,
        'memory_writes': 0,
        'instructions': 0,
        'sim_ticks': m5.curTick()
    }
    
    if os.path.exists(stats_file):
        print(f"Analyzing performance metrics from {stats_file}...")
        
        try:
            with open(stats_file, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue
                    
                    # L1 Data Cache metrics
                    if 'system.cpu.dcache.overall_miss_rate::total' in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            metrics['l1d_miss_rate'] = float(parts[1])
                    elif 'system.cpu.dcache.overall_accesses::total' in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            metrics['l1d_accesses'] = int(parts[1])
                    elif 'system.cpu.dcache.overall_misses::total' in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            metrics['l1d_misses'] = int(parts[1])
                    
                    # L1 Instruction Cache metrics
                    elif 'system.cpu.icache.overall_miss_rate::total' in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            metrics['l1i_miss_rate'] = float(parts[1])
                    elif 'system.cpu.icache.overall_accesses::total' in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            metrics['l1i_accesses'] = int(parts[1])
                    elif 'system.cpu.icache.overall_misses::total' in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            metrics['l1i_misses'] = int(parts[1])
                    
                    # Memory controller metrics
                    elif 'system.mem_ctrl.bytes_read::total' in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            metrics['memory_reads'] = int(parts[1])
                    elif 'system.mem_ctrl.bytes_written::total' in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            metrics['memory_writes'] = int(parts[1])
                    
                    # CPU metrics
                    elif 'system.cpu.committedInsts' in line and '::total' in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            metrics['instructions'] = int(parts[1])
            
            # Print detailed analysis
            print("="*70)
            print("CACHE MEMORY PERFORMANCE ANALYSIS")
            print("Date: 2025-10-06 05:01:21")
            print("User: Gyanvlon")
            print("="*70)
            
            print(f"\nSimulation Summary:")
            print(f"  Program: hello")
            print(f"  Execution Time: {metrics['sim_ticks']:,} ticks")
            print(f"  Instructions Executed: {metrics['instructions']:,}")
            print(f"  Real Time: {end_time - start_time:.2f} seconds")
            
            if metrics['l1d_accesses'] > 0:
                hit_rate = (1 - metrics['l1d_miss_rate']) * 100
                print(f"\nL1 Data Cache Performance:")
                print(f"  Total Accesses: {metrics['l1d_accesses']:,}")
                print(f"  Cache Misses: {metrics['l1d_misses']:,}")
                print(f"  Hit Rate: {hit_rate:.2f}%")
                print(f"  Miss Rate: {metrics['l1d_miss_rate']*100:.2f}%")
            else:
                print(f"\nL1 Data Cache Performance: No accesses recorded")
            
            if metrics['l1i_accesses'] > 0:
                hit_rate = (1 - metrics['l1i_miss_rate']) * 100
                print(f"\nL1 Instruction Cache Performance:")
                print(f"  Total Accesses: {metrics['l1i_accesses']:,}")
                print(f"  Cache Misses: {metrics['l1i_misses']:,}")
                print(f"  Hit Rate: {hit_rate:.2f}%")
                print(f"  Miss Rate: {metrics['l1i_miss_rate']*100:.2f}%")
            else:
                print(f"\nL1 Instruction Cache Performance: No accesses recorded")
            
            print(f"\nMemory System Performance:")
            print(f"  Memory Bytes Read: {metrics['memory_reads']:,}")
            print(f"  Memory Bytes Written: {metrics['memory_writes']:,}")
            print(f"  Total Memory Traffic: {metrics['memory_reads'] + metrics['memory_writes']:,} bytes")
            
            # Calculate performance metrics
            if metrics['sim_ticks'] > 0 and metrics['instructions'] > 0:
                cycles = metrics['sim_ticks'] / 1000  # Convert to cycles (1GHz = 1000 ticks per cycle)
                ipc = metrics['instructions'] / cycles if cycles > 0 else 0
                print(f"\nPerformance Metrics:")
                print(f"  Instructions Per Cycle (IPC): {ipc:.4f}")
                print(f"  Cycles: {cycles:,.0f}")
            
            # Save comprehensive results
            results = {
                'analysis_info': {
                    'date': '2025-10-06 05:01:21',
                    'user': 'Gyanvlon',
                    'program': 'hello',
                    'gem5_version': '23.0.0.1'
                },
                'cache_configuration': {
                    'l1d_size': '32kB',
                    'l1i_size': '32kB',
                    'associativity': 2,
                    'latency': '2 cycles',
                    'cpu_type': 'X86TimingSimpleCPU',
                    'clock_frequency': '1GHz'
                },
                'simulation_results': {
                    'simulation_ticks': metrics['sim_ticks'],
                    'real_time': end_time - start_time,
                    'exit_reason': str(exit_event.getCause())
                },
                'performance_metrics': metrics
            }
            
            result_file = 'm5out/hello_cache_analysis_2025_10_06.json'
            with open(result_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            print("="*70)
            print("CACHE ANALYSIS COMPLETED SUCCESSFULLY!")
            print(f"Complete results saved to: {result_file}")
            print("Detailed gem5 statistics available in: m5out/stats.txt")
            print("Configuration files: m5out/config.ini and m5out/config.json")
            print("="*70)
            
        except Exception as e:
            print(f"Error analyzing stats: {e}")
            print("Basic simulation completed, but metrics extraction failed")
    else:
        print("Warning: stats.txt not found - simulation may not have completed properly")

# Extract and display metrics
extract_and_analyze_metrics()