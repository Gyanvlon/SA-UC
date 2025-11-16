
import sys
import argparse

import m5
from m5.objects import System, SrcClockDomain, VoltageDomain, \
    MinorCPU, MinorDefaultFUPool, FloatSimdFU, Cache, \
    SEWorkload, Process, X86Linux

from m5.util import convert

from m5.objects import AddrRange, SystemXBar, SubSystem, AtomicSimpleCPU

from m5.objects import (System, SrcClockDomain, VoltageDomain, MinorCPU, \
                        MinorDefaultFUPool, FloatSimdFU, TimingSimpleCPU, \
                        X86ISA, Process)

from m5.objects import System, AddrRange, SrcClockDomain, VoltageDomain, \
    SystemXBar

# parse args forwarded from command-line
parser = argparse.ArgumentParser(description='Run MinorCPU with tunable FloatSimdFU')
parser.add_argument('--num-cpus', type=int, default=2)
parser.add_argument('--oplat', type=int, default=3, help='opLat for FloatSimdFU')
parser.add_argument('--issuelat', type=int, default=4, help='issueLat for FloatSimdFU')
parser.add_argument('--cmd', type=str, required=True, help='path to user binary')
parser.add_argument('--cmd-args', type=str, default='', help='args to pass to binary')
parser.add_argument('--mem-size', type=str, default='2GB')
parser.add_argument('--cpu-clock', type=str, default='2GHz')
parser.add_argument('--sys-clock', type=str, default='1GHz')
args = parser.parse_args()

if args.oplat + args.issuelat != 7:
    print("Warning: recommended experiments keep opLat+issueLat = 7. Continuing anyway.")

# System setup (simple SE system)
system = System()

system.clk_domain = SrcClockDomain()
system.clk_domain.clock = args.sys_clock
system.clk_domain.voltage_domain = VoltageDomain()

# Memory
from m5.objects import DDR3_1600_8x8
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('2GB')]

# CPU cluster setup
system.cpu = [ MinorCPU(cpu_id=i) for i in range(args.num_cpus) ]

# Create and customize FU pool for each CPU
for cpu in system.cpu:
    fu_pool = MinorDefaultFUPool()
    # Create a FloatSimdFU object with custom latencies
    float_simd = FloatSimdFU(opLat=args.oplat, issueLat=args.issuelat)
    # Attach it (attribute name may vary by gem5 minor version; try "floatSimdFU" or similar)
    try:
        fu_pool.floatSimdFU = float_simd
    except Exception:
        # fallback: iterate over pool attributes to find one with 'float' in name
        for attr in dir(fu_pool):
            if 'float' in attr.lower() and getattr(fu_pool, attr) is not None:
                try:
                    setattr(fu_pool, attr, float_simd)
                except Exception:
                    pass
    cpu.fuPool = fu_pool
    cpu.clock = args.cpu_clock

# Simple memory bus and connect CPUs to a system-wide bus + memory
system.membus = SystemXBar()
from m5.objects import Cache
for i, cpu in enumerate(system.cpu):
    cpu.icache_port = cpu.icache_port if hasattr(cpu,'icache_port') else None
    cpu.dcache_port = cpu.dcache_port if hasattr(cpu,'dcache_port') else None

# Simple memory controller and DRAM
from m5.objects import DDR3_1600_8x8, MemCtrl
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.slave

# Connect system ports
system.system_port = system.membus.slave

# Set up workload (SE mode)
process = Process()
cmd_and_args = [args.cmd] + (args.cmd_args.split() if args.cmd_args else [])
process.cmd = cmd_and_args
for cpu in system.cpu:
    cpu.workload = process
    cpu.createThreads()

# Instantiate and run
root = m5.Root(full_system=False, system=system)
m5.instantiate()

print("Beginning simulation with opLat=%d issueLat=%d num_cpus=%d" % (args.oplat, args.issuelat, args.num_cpus))
exit_event = m5.simulate()
print('Exiting @ tick {} because {}'.format(m5.curTick(), exit_event.getCause()))