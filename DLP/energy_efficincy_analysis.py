"""
Energy Efficiency and Performance Trade-offs Analysis
Simulates and analyzes energy consumption vs performance
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List

@dataclass
class ProcessorConfig:
    """Processor configuration parameters"""
    name: str
    cores: int
    frequency_ghz: float
    voltage: float
    power_tdp: float  # Thermal Design Power in Watts
    simd_width: int
    cache_size_mb: float

class EnergyEfficiencyAnalyzer:
    """Analyze energy efficiency of different DLP approaches"""
    
    def __init__(self):
        # Define different processor configurations
        self.configs = [
            ProcessorConfig("Scalar CPU", 1, 3.5, 1.2, 65, 1, 8),
            ProcessorConfig("SIMD CPU (SSE)", 1, 3.5, 1.2, 65, 4, 8),
            ProcessorConfig("SIMD CPU (AVX2)", 1, 3.5, 1.2, 65, 8, 8),
            ProcessorConfig("SIMD CPU (AVX-512)", 1, 3.5, 1.3, 95, 16, 8),
            ProcessorConfig("Multi-core (4 cores)", 4, 3.0, 1.1, 95, 8, 12),
            ProcessorConfig("Multi-core (8 cores)", 8, 2.8, 1.0, 125, 8, 16),
            ProcessorConfig("GPU (SM)", 32, 1.5, 1.0, 75, 32, 4),
            ProcessorConfig("GPU (Full)", 2048, 1.5, 1.0, 250, 32, 6),
        ]
    
    def calculate_performance(self, config: ProcessorConfig, workload_size: int) -> float:
        """Calculate performance (operations per second)"""
        # Base performance from frequency and cores
        base_perf = config.cores * config.frequency_ghz * 1e9
        
        # SIMD multiplier
        simd_efficiency = 0.85  # 85% efficiency for SIMD
        simd_perf = base_perf * config.simd_width * simd_efficiency
        
        # Cache effects (simplified model)
        cache_factor = min(1.0, config.cache_size_mb / (workload_size / 1e6))
        
        return simd_perf * cache_factor
    
    def calculate_power(self, config: ProcessorConfig, utilization: float = 1.0) -> float:
        """Calculate power consumption"""
        # Dynamic power: P = C * V^2 * f
        # Simplified model: power scales with utilization
        idle_power = config.power_tdp * 0.3  # 30% idle power
        dynamic_power = config.power_tdp * 0.7 * utilization
        
        return idle_power + dynamic_power
    
    def calculate_energy(self, config: ProcessorConfig, workload_size: int) -> float:
        """Calculate total energy consumption for workload"""
        perf = self.calculate_performance(config, workload_size)
        time_seconds = workload_size / perf
        power = self.calculate_power(config, utilization=1.0)
        energy = power * time_seconds  # Joules
        
        return energy
    
    def calculate_energy_efficiency(self, config: ProcessorConfig, workload_size: int) -> float:
        """Calculate energy efficiency (operations per joule)"""
        energy = self.calculate_energy(config, workload_size)
        return workload_size / energy
    
    def analyze_all_configs(self, workload_size: int = int(1e9)):
        """Analyze all processor configurations"""
        print("\n" + "=" * 80)
        print(f"ENERGY EFFICIENCY ANALYSIS (Workload: {workload_size:,} operations)")
        print("=" * 80)
        
        results = []
        
        for config in self.configs:
            perf = self.calculate_performance(config, workload_size)
            power = self.calculate_power(config)
            energy = self.calculate_energy(config, workload_size)
            efficiency = self.calculate_energy_efficiency(config, workload_size)
            execution_time = workload_size / perf
            
            results.append({
                'name': config.name,
                'performance': perf,
                'power': power,
                'energy': energy,
                'efficiency': efficiency,
                'time': execution_time
            })
            
            print(f"\n{config.name}:")
            print(f"  Performance: {perf/1e9:.2f} GOPS")
            print(f"  Power: {power:.2f} W")
            print(f"  Execution Time: {execution_time:.6f} s")
            print(f"  Energy: {energy:.2f} J")
            print(f"  Efficiency: {efficiency/1e6:.2f} MOPS/J")
        
        return results
    
    def compare_scaling(self):
        """Compare how different approaches scale"""
        workload_sizes = [1e6, 1e7, 1e8, 1e9, 1e10]
        
        print("\n" + "=" * 80)
        print("SCALING ANALYSIS")
        print("=" * 80)
        
        scaling_data = {config.name: {'sizes': [], 'energy': [], 'time': [], 'power': []} 
                       for config in self.configs}
        
        for size in workload_sizes:
            print(f"\nWorkload Size: {size:.0e} operations")
            for config in self.configs:
                energy = self.calculate_energy(config, int(size))
                perf = self.calculate_performance(config, int(size))
                time = size / perf
                power = self.calculate_power(config)
                
                scaling_data[config.name]['sizes'].append(size)
                scaling_data[config.name]['energy'].append(energy)
                scaling_data[config.name]['time'].append(time)
                scaling_data[config.name]['power'].append(power)
        
        return scaling_data
    
    def analyze_power_performance_tradeoff(self):
        """Analyze power-performance trade-offs with frequency scaling"""
        print("\n" + "=" * 80)
        print("DVFS (Dynamic Voltage and Frequency Scaling) ANALYSIS")
        print("=" * 80)
        
        base_config = self.configs[2]  # AVX2 CPU
        frequencies = np.linspace(1.0, 3.5, 10)
        workload_size = int(1e9)
        
        results = {
            'frequency': [],
            'voltage': [],
            'power': [],
            'performance': [],
            'energy': [],
            'efficiency': []
        }
        
        for freq in frequencies:
            # Voltage scales roughly linearly with frequency (simplified)
            voltage = 0.8 + (freq / 3.5) * 0.5
            
            # Create temporary config
            temp_config = ProcessorConfig(
                name=f"CPU @ {freq:.1f}GHz",
                cores=base_config.cores,
                frequency_ghz=freq,
                voltage=voltage,
                power_tdp=base_config.power_tdp * (voltage**2) * (freq / base_config.frequency_ghz),
                simd_width=base_config.simd_width,
                cache_size_mb=base_config.cache_size_mb
            )
            
            perf = self.calculate_performance(temp_config, workload_size)
            power = self.calculate_power(temp_config)
            energy = self.calculate_energy(temp_config, workload_size)
            efficiency = self.calculate_energy_efficiency(temp_config, workload_size)
            
            results['frequency'].append(freq)
            results['voltage'].append(voltage)
            results['power'].append(power)
            results['performance'].append(perf / 1e9)  # GOPS
            results['energy'].append(energy)
            results['efficiency'].append(efficiency / 1e6)  # MOPS/J
            
            print(f"\nFrequency: {freq:.2f} GHz, Voltage: {voltage:.2f}V")
            print(f"  Power: {power:.2f}W, Performance: {perf/1e9:.2f} GOPS")
            print(f"  Energy: {energy:.2f}J, Efficiency: {efficiency/1e6:.2f} MOPS/J")
        
        return results

def plot_energy_analysis(base_results, scaling_data, dvfs_results):
    """Plot comprehensive energy efficiency analysis"""
    fig = plt.figure(figsize=(20, 12))
    
    # 1. Performance vs Power
    ax1 = plt.subplot(3, 3, 1)
    perfs = [r['performance']/1e9 for r in base_results]
    powers = [r['power'] for r in base_results]
    names = [r['name'] for r in base_results]
    
    scatter = ax1.scatter(powers, perfs, s=200, c=range(len(base_results)), 
                         cmap='viridis', alpha=0.6, edgecolors='black', linewidth=2)
    for i, name in enumerate(names):
        ax1.annotate(name, (powers[i], perfs[i]), fontsize=8, 
                    xytext=(5, 5), textcoords='offset points')
    ax1.set_xlabel('Power (W)', fontsize=12)
    ax1.set_ylabel('Performance (GOPS)', fontsize=12)
    ax1.set_title('Performance vs Power', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # 2. Energy Efficiency Comparison
    ax2 = plt.subplot(3, 3, 2)
    efficiencies = [r['efficiency']/1e6 for r in base_results]
    colors = plt.cm.viridis(np.linspace(0, 1, len(names)))
    bars = ax2.barh(names, efficiencies, color=colors, edgecolor='black', linewidth=1.5)
    ax2.set_xlabel('Energy Efficiency (MOPS/J)', fontsize=12)
    ax2.set_title('Energy Efficiency Comparison', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='x')
    
    # 3. Execution Time Comparison
    ax3 = plt.subplot(3, 3, 3)
    times = [r['time']*1000 for r in base_results]  # Convert to ms
    bars = ax3.barh(names, times, color=colors, edgecolor='black', linewidth=1.5)
    ax3.set_xlabel('Execution Time (ms)', fontsize=12)
    ax3.set_title('Execution Time Comparison', fontsize=14, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='x')
    ax3.set_xscale('log')
    
    # 4. Energy Scaling
    ax4 = plt.subplot(3, 3, 4)
    for name in ['Scalar CPU', 'SIMD CPU (AVX2)', 'Multi-core (8 cores)', 'GPU (Full)']:
        if name in scaling_data:
            data = scaling_data[name]
            ax4.plot(data['sizes'], data['energy'], 'o-', label=name, linewidth=2, markersize=6)
    ax4.set_xlabel('Workload Size (operations)', fontsize=12)
    ax4.set_ylabel('Energy (J)', fontsize=12)
    ax4.set_title('Energy Consumption Scaling', fontsize=14, fontweight='bold')
    ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.3)
    ax4.set_xscale('log')
    ax4.set_yscale('log')
    
    # 5. Time Scaling
    ax5 = plt.subplot(3, 3, 5)
    for name in ['Scalar CPU', 'SIMD CPU (AVX2)', 'Multi-core (8 cores)', 'GPU (Full)']:
        if name in scaling_data:
            data = scaling_data[name]
            ax5.plot(data['sizes'], data['time'], 'o-', label=name, linewidth=2, markersize=6)
    ax5.set_xlabel('Workload Size (operations)', fontsize=12)
    ax5.set_ylabel('Execution Time (s)', fontsize=12)
    ax5.set_title('Execution Time Scaling', fontsize=14, fontweight='bold')
    ax5.legend(fontsize=9)
    ax5.grid(True, alpha=0.3)
    ax5.set_xscale('log')
    ax5.set_yscale('log')
    
    # 6. Performance per Watt
    ax6 = plt.subplot(3, 3, 6)
    perf_per_watt = [r['performance']/1e9/r['power'] for r in base_results]
    bars = ax6.barh(names, perf_per_watt, color=colors, edgecolor='black', linewidth=1.5)
    ax6.set_xlabel('Performance per Watt (GOPS/W)', fontsize=12)
    ax6.set_title('Performance per Watt', fontsize=14, fontweight='bold')
    ax6.grid(True, alpha=0.3, axis='x')
    
    # 7. DVFS - Frequency vs Power
    ax7 = plt.subplot(3, 3, 7)
    ax7.plot(dvfs_results['frequency'], dvfs_results['power'], 'o-', 
            linewidth=2, markersize=8, color='red')
    ax7.set_xlabel('Frequency (GHz)', fontsize=12)
    ax7.set_ylabel('Power (W)', fontsize=12)
    ax7.set_title('DVFS: Frequency vs Power', fontsize=14, fontweight='bold')
    ax7.grid(True, alpha=0.3)
    
    # 8. DVFS - Frequency vs Energy Efficiency
    ax8