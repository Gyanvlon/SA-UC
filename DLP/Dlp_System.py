"""
gem5 Configuration for DLP Benchmarks
Author: Gyanvlon
Date: 2025-11-02
"""

import m5
from m5.objects import *

class DLPSystem(System):
    def __init__(self, cpu_type="O3CPU", num_cores=8, **kwargs):
        super(DLPSystem, self).__init__(**kwargs)
        
        # Memory configuration
        self.mem_mode = 'timing'
        self.mem_ranges = [AddrRange('8GB')]
        
        # CPU configuration
        if cpu_type == "O3CPU":
            self.cpu = [X86O3CPU() for _ in range(num_cores)]
        elif cpu_type == "MinorCPU":
            self.cpu = [X86MinorCPU() for _ in range(num_cores)]
        else:
            self.cpu = [X86TimingSimpleCPU() for _ in range(num_cores)]
        
        # Configure SIMD/Vector units
        for cpu in self.cpu:
            cpu.isa = [X86ISA()] * len(self.cpu)
        
        # Memory system
        self.membus = SystemXBar()
        self.system_port = self.membus.cpu_side_ports
        
        # Cache hierarchy
        for cpu in self.cpu:
            cpu.icache = L1ICache(size='32kB', assoc=8)
            cpu.dcache = L1DCache(size='32kB', assoc=8)
            cpu.icache.cpu_side = cpu.icache_port
            cpu.dcache.cpu_side = cpu.dcache_port
            cpu.icache.mem_side = self.membus.cpu_side_ports
            cpu.dcache.mem_side = self.membus.cpu_side_ports
        
        # L2 Cache
        self.l2cache = L2Cache(size='256kB', assoc=16)
        self.l2cache.cpu_side = self.membus.mem_side_ports
        self.l2cache.mem_side = self.membus.cpu_side_ports
        
        # Memory controller
        self.mem_ctrl = MemCtrl()
        self.mem_ctrl.dram = DDR4_2400_16x4()
        self.mem_ctrl.dram.range = self.mem_ranges[0]
        self.mem_ctrl.port = self.membus.mem_side_ports

# Create system
system = DLPSystem(cpu_type="O3CPU", num_cores=4)
system.workload = SEWorkload.init_compatible("dlp_benchmark")

# Setup root
root = Root(full_system=False, system=system)
m5.instantiate()

print("Beginning simulation!")
exit_event = m5.simulate()
print(f'Exiting @ tick {m5.curTick()} because {exit_event.getCause()}')