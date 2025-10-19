import m5
from m5.objects import *
import sys
import os

# Create system
system = System()

# Clock configuration
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

# Memory configuration
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

# Create CPU
system.cpu = TimingSimpleCPU()

# Create memory bus FIRST
system.membus = SystemXBar()

# Create interrupt controller (REQUIRED for X86)
system.cpu.createInterruptController()

# For X86, connect interrupt pins
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

# Connect CPU to memory bus
system.cpu.icache_port = system.membus.cpu_side_ports
system.cpu.dcache_port = system.membus.cpu_side_ports

# Memory controller
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# System port
system.system_port = system.membus.cpu_side_ports

# Set up the workload
binary = 'workloads/simple_test'

# Check if binary exists
if not os.path.exists(binary):
    print(f"Error: Binary '{binary}' not found!")
    sys.exit(1)

# Set up workload
system.workload = SEWorkload.init_compatible(binary)

# Create process
process = Process()
process.cmd = [binary]
system.cpu.workload = process
system.cpu.createThreads()

# Instantiate system
root = Root(full_system=False, system=system)
m5.instantiate()

print("="*60)
print("SIMPLE PIPELINE SIMULATION")
print("="*60)
print(f"Binary: {binary}")
print(f"Clock: {system.clk_domain.clock}")
print("="*60)
print("Beginning simulation...\n")

exit_event = m5.simulate()

print("\n" + "="*60)
print("SIMULATION COMPLETE")
print("="*60)
print(f'Exiting @ tick {m5.curTick()} because {exit_event.getCause()}')
print("="*60)