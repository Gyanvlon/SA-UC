import m5
from m5.objects import *
import sys
import os

# Define cache classes
class L1ICache(Cache):
    """L1 Instruction Cache"""
    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20
    size = '32kB'

class L1DCache(Cache):
    """L1 Data Cache"""
    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20
    size = '64kB'

class L2Cache(Cache):
    """L2 Unified Cache"""
    assoc = 8
    tag_latency = 20
    data_latency = 20
    response_latency = 20
    mshrs = 20
    tgts_per_mshr = 12
    size = '256kB'

def create_superscalar_system(issue_width=2):
    """Create superscalar processor"""

    system = System()

    # Clock
    system.clk_domain = SrcClockDomain()
    system.clk_domain.clock = '2GHz'
    system.clk_domain.voltage_domain = VoltageDomain()

    # Memory
    system.mem_mode = 'timing'
    system.mem_ranges = [AddrRange('2GB')]

    # Use O3CPU for out-of-order superscalar
    system.cpu = X86O3CPU()

    # Limit fetch width to avoid MaxWidth error (max is 12)
    max_width = min(issue_width * 2, 12)

    # Configure widths
    system.cpu.fetchWidth = max_width
    system.cpu.decodeWidth = max_width
    system.cpu.renameWidth = max_width
    system.cpu.issueWidth = min(issue_width, 6)  # Limit to 6
    system.cpu.dispatchWidth = min(issue_width, 6)
    system.cpu.commitWidth = min(issue_width, 6)
    system.cpu.squashWidth = min(issue_width, 6)

    # Buffer sizes
    system.cpu.numIQEntries = 64
    system.cpu.numROBEntries = 192
    system.cpu.numPhysIntRegs = 256
    system.cpu.numPhysFloatRegs = 256

    # Create caches
    system.cpu.icache = L1ICache()
    system.cpu.dcache = L1DCache()

    # Connect L1 caches to CPU
    system.cpu.icache.cpu_side = system.cpu.icache_port
    system.cpu.dcache.cpu_side = system.cpu.dcache_port

    # L2 bus and cache
    system.l2bus = L2XBar()
    system.cpu.icache.mem_side = system.l2bus.cpu_side_ports
    system.cpu.dcache.mem_side = system.l2bus.cpu_side_ports

    system.l2cache = L2Cache()
    system.l2cache.cpu_side = system.l2bus.mem_side_ports

    # Memory bus
    system.membus = SystemXBar()
    system.l2cache.mem_side = system.membus.cpu_side_ports

    # Interrupt controller (REQUIRED for X86)
    system.cpu.createInterruptController()

    # For X86, connect interrupt pins
    system.cpu.interrupts[0].pio = system.membus.mem_side_ports
    system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
    system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

    # Memory controller
    system.mem_ctrl = MemCtrl()
    system.mem_ctrl.dram = DDR3_1600_8x8()
    system.mem_ctrl.dram.range = system.mem_ranges[0]
    system.mem_ctrl.port = system.membus.mem_side_ports

    # System port
    system.system_port = system.membus.cpu_side_ports

    print(f"Created {issue_width}-wide superscalar processor")
    print(f"  - Fetch width: {system.cpu.fetchWidth}")
    print(f"  - Issue width: {system.cpu.issueWidth}")
    print(f"  - Commit width: {system.cpu.commitWidth}")

    return system

# Main execution
if len(sys.argv) < 2:
    print("Usage: gem5 superscalar.py <issue_width> [binary]")
    sys.exit(1)

issue_width = int(sys.argv[1])
binary = sys.argv[2] if len(sys.argv) > 2 else 'workloads/matrix_multiply'

# Validate issue width
if issue_width > 6:
    print(f"Warning: Issue width {issue_width} exceeds recommended limit.")
    print("Setting to maximum supported width of 6")
    issue_width = 6

# Check binary exists
if not os.path.exists(binary):
    print(f"Error: Binary '{binary}' not found!")
    sys.exit(1)

# Create system
system = create_superscalar_system(issue_width)

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
print(f"SUPERSCALAR SIMULATION - {issue_width}-WIDE")
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