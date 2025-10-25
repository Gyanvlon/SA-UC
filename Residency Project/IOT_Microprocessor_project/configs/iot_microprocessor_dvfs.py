import m5
from m5.objects import *
import argparse

# DVFS Operating Points
OPERATING_POINTS = {
    'low_power': {
        'freq': '100MHz',
        'voltage': '0.6V',
        'description': 'Idle monitoring and standby'
    },
    'balanced': {
        'freq': '200MHz',
        'voltage': '0.75V',
        'description': 'Normal sensor processing'
    },
    'high_perf': {
        'freq': '350MHz',
        'voltage': '0.9V',
        'description': 'Complex computation'
    },
    'max_perf': {
        'freq': '500MHz',
        'voltage': '1.0V',
        'description': 'Peak performance'
    }
}

def create_iot_system(operating_point):
    """Create IoT system with specified operating point"""

    system = System()

    # System clock
    system.clk_domain = SrcClockDomain()
    system.clk_domain.clock = '1GHz'
    system.clk_domain.voltage_domain = VoltageDomain(voltage='1.0V')

    # Memory configuration
    system.mem_mode = 'timing'
    system.mem_ranges = [AddrRange('256MB')]

    # Get operating point parameters
    freq = OPERATING_POINTS[operating_point]['freq']
    voltage = OPERATING_POINTS[operating_point]['voltage']

    # CPU voltage and frequency domain
    system.cpu_voltage_domain = VoltageDomain(voltage=voltage)
    system.cpu_clk_domain = SrcClockDomain(
        clock=freq,
        voltage_domain=system.cpu_voltage_domain
    )

    # Create MinorCPU
    system.cpu = MinorCPU()
    system.cpu.clk_domain = system.cpu_clk_domain
    system.cpu.decodeToExecuteForwardDelay = 1
    system.cpu.executeCommitLimit = 2

    # L1 Caches
    system.cpu.icache = Cache(size='16kB', assoc=4, tag_latency=1,
                              data_latency=1, response_latency=1,
                              mshrs=4, tgts_per_mshr=8)

    system.cpu.dcache = Cache(size='16kB', assoc=4, tag_latency=1,
                              data_latency=1, response_latency=1,
                              mshrs=4, tgts_per_mshr=8)

    # L2 Cache with separate power domain
    system.l2_voltage_domain = VoltageDomain(voltage=voltage)
    system.l2_clk_domain = SrcClockDomain(
        clock=freq,
        voltage_domain=system.l2_voltage_domain
    )

    system.l2cache = Cache(size='64kB', assoc=8, tag_latency=4,
                           data_latency=4, response_latency=1,
                           mshrs=20, tgts_per_mshr=12)
    system.l2cache.clk_domain = system.l2_clk_domain

    # Connect caches
    system.cpu.icache_port = system.cpu.icache.cpu_side
    system.cpu.dcache_port = system.cpu.dcache.cpu_side

    # L2 bus
    system.l2bus = L2XBar()
    system.cpu.icache.mem_side = system.l2bus.cpu_side_ports
    system.cpu.dcache.mem_side = system.l2bus.cpu_side_ports
    system.l2cache.cpu_side = system.l2bus.mem_side_ports

    # Memory bus
    system.membus = SystemXBar()
    system.l2cache.mem_side = system.membus.cpu_side_ports

    # Interrupt controller
    system.cpu.createInterruptController()

    # Memory controller
    system.mem_ctrl = MemCtrl()
    system.mem_ctrl.dram = DDR3_1600_8x8(range=system.mem_ranges[0])
    system.mem_ctrl.port = system.membus.mem_side_ports

    # System port
    system.system_port = system.membus.cpu_side_ports

    return system


def print_dvfs_config(operating_point):
    """Print DVFS configuration"""
    op = OPERATING_POINTS[operating_point]

    print("\n" + "="*70)
    print("IoT Microprocessor - DVFS Configuration")
    print("="*70)
    print(f"Operating Point:  {operating_point.upper()}")
    print(f"Frequency:        {op['freq']}")
    print(f"Voltage:          {op['voltage']}")
    print(f"Description:      {op['description']}")
    print("="*70 + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cmd', type=str, required=True)
    parser.add_argument('--operating-point', type=str, default='balanced',
                       choices=['low_power', 'balanced', 'high_perf', 'max_perf'])

    args = parser.parse_args()

    # Print configuration
    print_dvfs_config(args.operating_point)

    # Create system
    system = create_iot_system(args.operating_point)

    # Set up workload
    system.workload = SEWorkload.init_compatible(args.cmd)
    process = Process()
    process.cmd = [args.cmd]
    system.cpu.workload = process
    system.cpu.createThreads()

    # Instantiate and run
    root = Root(full_system=False, system=system)
    m5.instantiate()

    print("Starting simulation...")
    start_tick = m5.curTick()
    exit_event = m5.simulate()
    end_tick = m5.curTick()

    sim_seconds = (end_tick - start_tick) / 1e12

    print("\n" + "="*70)
    print("Simulation Complete!")
    print("="*70)
    print(f"Exit Reason:      {exit_event.getCause()}")
    print(f"Simulated Time:   {sim_seconds:.9f} seconds")
    print("="*70 + "\n")


if __name__ == '__m5_main__':
    main()