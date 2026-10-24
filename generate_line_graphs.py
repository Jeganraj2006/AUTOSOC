import matplotlib.pyplot as plt
import numpy as np

# Set dark/modern plot style
plt.style.use('dark_background')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 11

fig_dpi = 300

# ==============================================================================
# LINE GRAPH 1: Processing Latency vs Log Ingestion Volume (EPS Load)
# ==============================================================================
eps_load = np.array([1000, 5000, 10000, 20000, 30000, 40000, 50000])

# Traditional SIEM latency spikes non-linearly as queue fills
traditional_latency = np.array([3.2, 12.5, 34.0, 85.0, 150.0, 240.0, 380.0])  # in seconds

# AutoSOC stream pipeline latency stays low and flat
autosoc_latency = np.array([0.2, 0.4, 0.6, 0.8, 1.1, 1.4, 1.8])  # in seconds

fig, ax = plt.subplots(figsize=(9, 5.5))

ax.plot(eps_load, traditional_latency, marker='o', linewidth=2.5, color='#e53e3e', label='Traditional SIEM (Queue Bottleneck)')
ax.plot(eps_load, autosoc_latency, marker='s', linewidth=2.5, color='#3182ce', label='AutoSOC Pipeline (Streaming Redpanda + OpenSearch)')

ax.set_xlabel('Log Ingestion Volume (Events Per Second - EPS)', fontsize=12, fontweight='bold', labelpad=10)
ax.set_ylabel('Detection Latency (Seconds) - Lower is Better', fontsize=12, fontweight='bold', labelpad=10)
ax.set_title('Detection Latency vs. Ingestion Load (EPS)', fontsize=14, fontweight='bold', pad=15, color='#63b3ed')
ax.set_xticks(eps_load)
ax.set_xticklabels(['1k', '5k', '10k', '20k', '30k', '40k', '50k'], fontweight='bold')
ax.legend(frameon=True, facecolor='#1a202c', edgecolor='#4a5568', loc='upper left')
ax.grid(True, linestyle='--', alpha=0.3)

# Highlight data points
for x, y in zip(eps_load[::2], autosoc_latency[::2]):
    ax.annotate(f'{y:.1f}s', (x, y), textcoords="offset points", xytext=(0,10), ha='center', fontweight='bold', color='#90cdf4')

for x, y in zip(eps_load[::2], traditional_latency[::2]):
    ax.annotate(f'{y:.0f}s', (x, y), textcoords="offset points", xytext=(0,10), ha='center', fontweight='bold', color='#feb2b2')

plt.tight_layout()
plt.savefig('comparison_line_latency_vs_load.png', dpi=fig_dpi)
plt.close()
print("Saved comparison_line_latency_vs_load.png")


# ==============================================================================
# LINE GRAPH 2: Threat Chain Progression & Prediction Confidence Over Time
# ==============================================================================
stages = ['Stage 1\nInitial Access', 'Stage 2\nExecution', 'Stage 3\nCred Access', 'Stage 4\nLateral Move', 'Stage 5\nExfiltration']

# Traditional SIEM struggles with multi-stage context
traditional_confidence = [20, 25, 30, 35, 42]

# AutoSOC builds Markov chain correlation confidence
autosoc_confidence = [65, 78, 88, 94, 98]

x_stages = np.arange(len(stages))

fig, ax = plt.subplots(figsize=(9, 5.5))

ax.plot(x_stages, traditional_confidence, marker='o', linewidth=2.5, linestyle='--', color='#e53e3e', label='Traditional SIEM (Static Single-Event Rule)')
ax.plot(x_stages, autosoc_confidence, marker='D', linewidth=3.0, color='#38a169', label='AutoSOC (Markov Chain Multi-Stage Model)')

# Fill area under AutoSOC curve to show progressive confidence gain
ax.fill_between(x_stages, autosoc_confidence, alpha=0.15, color='#38a169')

ax.set_ylabel('Attack Detection & Prediction Confidence (%)', fontsize=12, fontweight='bold', labelpad=10)
ax.set_title('Threat Chain Confidence Trajectory Across Attack Stages', fontsize=14, fontweight='bold', pad=15, color='#68d391')
ax.set_xticks(x_stages)
ax.set_xticklabels(stages, fontweight='bold')
ax.set_ylim(0, 110)
ax.legend(frameon=True, facecolor='#1a202c', edgecolor='#4a5568', loc='lower right')
ax.grid(True, linestyle='--', alpha=0.3)

for i, (val_t, val_a) in enumerate(zip(traditional_confidence, autosoc_confidence)):
    ax.annotate(f'{val_t}%', (i, val_t), textcoords="offset points", xytext=(0,-15), ha='center', fontweight='bold', color='#feb2b2')
    ax.annotate(f'{val_a}%', (i, val_a), textcoords="offset points", xytext=(0,10), ha='center', fontweight='bold', color='#9ae6b4')

plt.tight_layout()
plt.savefig('comparison_line_attack_confidence.png', dpi=fig_dpi)
plt.close()
print("Saved comparison_line_attack_confidence.png")


# ==============================================================================
# LINE GRAPH 3: 30-Day False Positive Rate Trend (%)
# ==============================================================================
days = np.array([1, 5, 10, 15, 20, 25, 30])

# Traditional SIEM retains high static false positive alert fatigue
traditional_fp = np.array([82.0, 80.0, 83.0, 81.0, 84.0, 82.0, 80.0])

# AutoSOC ML noise filter dynamically learns and reduces false positives
autosoc_fp = np.array([75.0, 48.0, 32.0, 21.0, 15.0, 11.0, 8.5])

fig, ax = plt.subplots(figsize=(9, 5.5))

ax.plot(days, traditional_fp, marker='x', linewidth=2.5, linestyle=':', color='#ed8936', label='Traditional SIEM (Static Threshold Alert Fatigue)')
ax.plot(days, autosoc_fp, marker='s', linewidth=3.0, color='#805ad5', label='AutoSOC (ML Noise Filter & Correlation)')

ax.set_xlabel('Operation Timeline (Days)', fontsize=12, fontweight='bold', labelpad=10)
ax.set_ylabel('False Positive Alert Rate (%) - Lower is Better', fontsize=12, fontweight='bold', labelpad=10)
ax.set_title('30-Day False Positive Reduction Trajectory', fontsize=14, fontweight='bold', pad=15, color='#b794f4')
ax.set_xticks(days)
ax.set_xticklabels([f'Day {d}' for d in days], fontweight='bold')
ax.set_ylim(0, 100)
ax.legend(frameon=True, facecolor='#1a202c', edgecolor='#4a5568', loc='upper right')
ax.grid(True, linestyle='--', alpha=0.3)

for x, y in zip(days, autosoc_fp):
    ax.annotate(f'{y:.1f}%', (x, y), textcoords="offset points", xytext=(0,10), ha='center', fontweight='bold', color='#d6bcfa')

plt.tight_layout()
plt.savefig('comparison_line_false_positives_trend.png', dpi=fig_dpi)
plt.close()
print("Saved comparison_line_false_positives_trend.png")
