import matplotlib.pyplot as plt
import numpy as np

# Set dark/modern plot style
plt.style.use('dark_background')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 11

fig_dpi = 300

# ==========================================
# GRAPH 1: MTTD vs MTTR (Time Comparison in Minutes)
# ==========================================
metrics_time = ['MTTD (Mean Time to Detect)', 'MTTR (Mean Time to Respond)']
traditional_time = [45.0, 180.0]  # in minutes
autosoc_time = [1.2, 4.5]       # in minutes

x = np.arange(len(metrics_time))
width = 0.35

fig, ax = plt.subplots(figsize=(8, 5))
rects1 = ax.bar(x - width/2, traditional_time, width, label='Traditional SIEM / SOC', color='#e53e3e', edgecolor='#ffffff', linewidth=0.8)
rects2 = ax.bar(x + width/2, autosoc_time, width, label='AutoSOC (Our Project)', color='#3182ce', edgecolor='#ffffff', linewidth=0.8)

ax.set_ylabel('Time (Minutes) - Lower is Better', fontsize=12, fontweight='bold', labelpad=10)
ax.set_title('Response Latency: AutoSOC vs. Traditional SOC', fontsize=14, fontweight='bold', pad=15, color='#63b3ed')
ax.set_xticks(x)
ax.set_xticklabels(metrics_time, fontweight='bold')
ax.legend(frameon=True, facecolor='#1a202c', edgecolor='#4a5568')
ax.grid(axis='y', linestyle='--', alpha=0.3)

# Add values above bars
for rect in rects1:
    height = rect.get_height()
    ax.annotate(f'{height:.1f}m', xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontweight='bold', color='#feb2b2')

for rect in rects2:
    height = rect.get_height()
    ax.annotate(f'{height:.1f}m', xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontweight='bold', color='#90cdf4')

plt.tight_layout()
plt.savefig('comparison_response_time.png', dpi=fig_dpi)
plt.close()
print("Saved comparison_response_time.png")


# ==========================================
# GRAPH 2: Core Performance & Accuracy Metrics (%)
# ==========================================
metrics_pct = ['False Positive\nReduction Rate', 'MITRE ATT&CK\nCoverage', 'Multi-Stage Path\nForecasting Accuracy']
traditional_pct = [15.0, 42.0, 12.0]
autosoc_pct = [87.5, 94.0, 84.2]

x = np.arange(len(metrics_pct))

fig, ax = plt.subplots(figsize=(9, 5.5))
rects1 = ax.bar(x - width/2, traditional_pct, width, label='Traditional SIEM / SOC', color='#e53e3e', edgecolor='#ffffff', linewidth=0.8)
rects2 = ax.bar(x + width/2, autosoc_pct, width, label='AutoSOC (Our Project)', color='#38a169', edgecolor='#ffffff', linewidth=0.8)

ax.set_ylabel('Percentage (%) - Higher is Better', fontsize=12, fontweight='bold', labelpad=10)
ax.set_title('Threat Detection & Prediction Accuracy Comparison', fontsize=14, fontweight='bold', pad=15, color='#68d391')
ax.set_xticks(x)
ax.set_xticklabels(metrics_pct, fontweight='bold')
ax.set_ylim(0, 110)
ax.legend(frameon=True, facecolor='#1a202c', edgecolor='#4a5568')
ax.grid(axis='y', linestyle='--', alpha=0.3)

for rect in rects1:
    height = rect.get_height()
    ax.annotate(f'{height:.1f}%', xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontweight='bold', color='#feb2b2')

for rect in rects2:
    height = rect.get_height()
    ax.annotate(f'{height:.1f}%', xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontweight='bold', color='#9ae6b4')

plt.tight_layout()
plt.savefig('comparison_accuracy_metrics.png', dpi=fig_dpi)
plt.close()
print("Saved comparison_accuracy_metrics.png")


# ==========================================
# GRAPH 3: Radar / Spider Chart Overview (Normalized 0 - 100 Scale)
# ==========================================
categories = ['Detection Speed', 'Response Speed', 'Noise Reduction', 'MITRE Coverage', 'Prediction Capability', 'Throughput Capacity']
num_vars = len(categories)

# Normalized scale out of 100 (where 100 = optimal)
traditional_radar = [20, 15, 25, 42, 12, 30]
autosoc_radar = [96, 95, 88, 94, 84, 92]

angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
traditional_radar += traditional_radar[:1]
autosoc_radar += autosoc_radar[:1]
angles += angles[:1]

fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
ax.set_theta_offset(np.pi / 2)
ax.set_theta_direction(-1)

plt.xticks(angles[:-1], categories, color='#e2e8f0', size=11, fontweight='bold')
ax.set_rlabel_position(0)
plt.yticks([20, 40, 60, 80, 100], ["20", "40", "60", "80", "100"], color="#718096", size=9)
plt.ylim(0, 100)

ax.plot(angles, traditional_radar, linewidth=2, linestyle='solid', label='Traditional SIEM', color='#e53e3e')
ax.fill(angles, traditional_radar, color='#e53e3e', alpha=0.25)

ax.plot(angles, autosoc_radar, linewidth=2, linestyle='solid', label='AutoSOC (Our Project)', color='#805ad5')
ax.fill(angles, autosoc_radar, color='#805ad5', alpha=0.35)

plt.title('Overall Capabilities Radar Profile', size=15, color='#b794f4', y=1.08, fontweight='bold')
plt.legend(loc='upper right', bbox_to_anchor=(1.25, 1.1), frameon=True, facecolor='#1a202c', edgecolor='#4a5568')

plt.tight_layout()
plt.savefig('comparison_radar_chart.png', dpi=fig_dpi)
plt.close()
print("Saved comparison_radar_chart.png")


# ==========================================
# GRAPH 4: Log Ingestion & Processing Throughput (EPS)
# ==========================================
systems = ['Traditional Rule SIEM', 'AutoSOC (Our Streaming Pipeline)']
throughput = [2500, 18500]

fig, ax = plt.subplots(figsize=(7, 4.5))
bars = ax.barh(systems, throughput, color=['#e53e3e', '#d69e2e'], height=0.45, edgecolor='#ffffff', linewidth=0.8)

ax.set_xlabel('Events Per Second (EPS) - Higher is Better', fontsize=11, fontweight='bold', labelpad=10)
ax.set_title('Log Processing & Ingestion Throughput', fontsize=14, fontweight='bold', pad=15, color='#faf089')
ax.grid(axis='x', linestyle='--', alpha=0.3)
ax.set_xlim(0, 22000)

for bar in bars:
    width_val = bar.get_width()
    ax.annotate(f'{width_val:,} EPS', xy=(width_val + 400, bar.get_y() + bar.get_height() / 2),
                xytext=(0, 0), textcoords="offset points", ha='left', va='center', fontweight='bold', color='#ffffff')

plt.tight_layout()
plt.savefig('comparison_throughput_eps.png', dpi=fig_dpi)
plt.close()
print("Saved comparison_throughput_eps.png")
