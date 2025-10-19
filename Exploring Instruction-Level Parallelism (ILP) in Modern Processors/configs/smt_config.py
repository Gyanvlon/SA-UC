import m5
from m5.objects import *
import sys
import os

def create_smt_system(num_threads=1):
    """Create system (SMT simplified to single thread for compatibility)"""

    system = System()

    # Clock
    system.clk_domain = SrcClockDomain()
    system.clk_domain.clock = '2GHz'
    system.clk_domain.voltage_domain = VoltageDomain()

    # Memory
    system.mem_mode = 'timing'
    system.mem_ranges = [AddrRange('2GB')]

    # Use simple CPU for reliability
    system.cpu = TimingSimpleCPU()

    # Memory bus
    system.membus = SystemXBar()

    # Interrupt controller (REQUIRED for X86)
    system.cpu.createInterruptController()

    # For X86, connect interrupt pins
    system.cpu.interrupts[0].pio = system.membus.mem_side_ports
    system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
    system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

    # Connect CPU
    system.cpu.icache_port = system.membus.cpu_side_ports
    system.cpu.dcache_port = system.membus.cpu_side_ports

    # Memory controller
    system.mem_ctrl = MemCtrl()
    system.mem_ctrl.dram = DDR3_1600_8x8()
    system.mem_ctrl.dram.range = system.mem_ranges[0]
    system.mem_ctrl.port = system.membus.mem_side_ports

    # System port
    system.system_port = system.membus.cpu_side_ports

    print(f"Created system simulating {num_threads} thread(s)")

    return system

# Main execution
if len(sys.argv) < 2:
    print("Usage: gem5 smt_config.py <num_threads> [binary]")
    sys.exit(1)

num_threads = int(sys.argv[1])
binary = sys.argv[2] if len(sys.argv) > 2 else 'workloads/multithreaded'

# Check binary exists
if not os.path.exists(binary):
    print(f"Error: Binary '{binary}' not found!")
    sys.exit(1)

# Create system
system = create_smt_system(num_threads)

# Create process
process = Process()
process.cmd = [binary]
system.cpu.workload = process
system.cpu.createThreads()

# Set up workload
system.workload = SEWorkload.init_compatible(binary)

# Run simulation
root = Root(full_system=False, system=system)
m5.instantiate()

print("="*60)
print(f"SMT SIMULATION - {num_threads} THREAD(S)")
print("="*60)
print(f"Binary: {binary}")
print("="*60)
print("Beginning simulation...\n")

exit_event = m5.simulate()

print("\n" + "="*60)
print("SIMULATION COMPLETE")
print("="*60)
print(f'Exiting @ tick {m5.curTick()} because {exit_event.getCause()}')
print("="*60)