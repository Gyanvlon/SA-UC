import m5
from m5.objects import *
import argparse
import sys

def create_system(args):
    """Create the IoT microprocessor system"""

    # Create the system
    system = System()

    # System-wide clock domain (1GHz reference)
    system.clk_domain = SrcClockDomain()
    system.clk_domain.clock = '1GHz'
    system.clk_domain.voltage_domain = VoltageDomain(voltage='1.0V')

    # Memory mode and address range
    system.mem_mode = 'timing'
    system.mem_ranges = [AddrRange('256MB')]

    # CPU voltage and frequency domains (for DVFS)
    system.cpu_voltage_domain = VoltageDomain(voltage=args.cpu_voltage)
    system.cpu_clk_domain = SrcClockDomain(
        clock=args.cpu_clock,
        voltage_domain=system.cpu_voltage_domain
    )

    # Create MinorCPU (4-stage in-order pipeline)
    system.cpu = MinorCPU()
    system.cpu.clk_domain = system.cpu_clk_domain

    # MinorCPU pipeline configuration
    system.cpu.decodeToExecuteForwardDelay = 1
    system.cpu.executeCommitLimit = 2
    system.cpu.executeCycleInput = True

    # L1 Instruction Cache (16KB, 4-way)
    system.cpu.icache = Cache(
        size='16kB',
        assoc=4,
        tag_latency=1,
        data_latency=1,
        response_latency=1,
        mshrs=4,
        tgts_per_mshr=8,
        writeback_clean=False
    )

    # L1 Data Cache (16KB, 4-way)
    system.cpu.dcache = Cache(
        size='16kB',
        assoc=4,
        tag_latency=1,
        data_latency=1,
        response_latency=1,
        mshrs=4,
        tgts_per_mshr=8,
        writeback_clean=False
    )

    # L2 Cache voltage domain (separate for power gating)
    system.l2_voltage_domain = VoltageDomain(voltage=args.l2_voltage)
    system.l2_clk_domain = SrcClockDomain(
        clock=args.cpu_clock,
        voltage_domain=system.l2_voltage_domain
    )

    # L2 Cache (64KB, 8-way)
    system.l2cache = Cache(
        size='64kB',
        assoc=8,
        tag_latency=4,
        data_latency=4,
        response_latency=1,
        mshrs=20,
        tgts_per_mshr=12,
        writeback_clean=False
    )
    system.l2cache.clk_domain = system.l2_clk_domain

    # Connect L1 caches to CPU
    system.cpu.icache_port = system.cpu.icache.cpu_side
    system.cpu.dcache_port = system.cpu.dcache.cpu_side

    # Create L2 bus
    system.l2bus = L2XBar()
    system.cpu.icache.mem_side = system.l2bus.cpu_side_ports
    system.cpu.dcache.mem_side = system.l2bus.cpu_side_ports
    system.l2cache.cpu_side = system.l2bus.mem_side_ports

    # Create memory bus
    system.membus = SystemXBar()
    system.l2cache.mem_side = system.membus.cpu_side_ports

    # Interrupt controller (required for ARM)
    system.cpu.createInterruptController()

    # Memory controller with DDR3
    system.mem_ctrl = MemCtrl()
    system.mem_ctrl.dram = DDR3_1600_8x8(range=system.mem_ranges[0])
    system.mem_ctrl.port = system.membus.mem_side_ports

    # System port
    system.system_port = system.membus.cpu_side_ports

    return system


def print_config_summary(args):
    """Print configuration summary"""
    print("\n" + "="*70)
    print("IoT Microprocessor Configuration Summary")
    print("="*70)
    print(f"Workload:         {args.cmd}")
    print(f"CPU Model:        MinorCPU (4-stage in-order)")
    print(f"CPU Clock:        {args.cpu_clock}")
    print(f"CPU Voltage:      {args.cpu_voltage}")
    print(f"L2 Voltage:       {args.l2_voltage}")
    print("-"*70)
    print("Cache Configuration:")
    print("  L1 I-Cache:     16KB, 4-way set-associative")
    print("  L1 D-Cache:     16KB, 4-way set-associative")
    print("  L2 Cache:       64KB, 8-way set-associative")
    print("-"*70)
    print("Memory:           256MB DDR3-1600")
    print("="*70 + "\n")


def main():
    """Main simulation function"""
    parser = argparse.ArgumentParser(
        description='IoT Microprocessor Simulation in gem5'
    )

    parser.add_argument('--cmd', type=str, required=True,
                       help='Binary executable to simulate')
    parser.add_argument('--cpu-clock', type=str, default='200MHz',
                       help='CPU clock frequency (default: 200MHz)')
    parser.add_argument('--cpu-voltage', type=str, default='0.75V',
                       help='CPU voltage (default: 0.75V)')
    parser.add_argument('--l2-voltage', type=str, default='0.75V',
                       help='L2 cache voltage (default: 0.75V)')
    parser.add_argument('--options', type=str, default='',
                       help='Command line options for binary')

    args = parser.parse_args()

    # Print configuration
    print_config_summary(args)

    # Create system
    system = create_system(args)

    # Set up workload
    system.workload = SEWorkload.init_compatible(args.cmd)

    # Create process
    process = Process()
    process.cmd = [args.cmd]
    if args.options:
        process.cmd += args.options.split()

    system.cpu.workload = process
    system.cpu.createThreads()

    # Instantiate
    root = Root(full_system=False, system=system)
    m5.instantiate()

    # Run simulation
    print("Starting simulation...")
    print("-"*70)

    start_tick = m5.curTick()
    exit_event = m5.simulate()
    end_tick = m5.curTick()

    sim_seconds = (end_tick - start_tick) / 1e12

    # Print results
    print("-"*70)
    print("\n" + "="*70)
    print("Simulation Complete!")
    print("="*70)
    print(f"Exit Reason:      {exit_event.getCause()}")
    print(f"Simulated Time:   {sim_seconds:.9f} seconds")
    print(f"Total Ticks:      {end_tick - start_tick:,}")
    print("="*70)
    print(f"\nStatistics:       m5out/stats.txt")
    print(f"Configuration:    m5out/config.ini\n")


if __name__ == '__m5_main__':
    main()