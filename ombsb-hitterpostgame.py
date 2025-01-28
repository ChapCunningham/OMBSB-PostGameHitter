import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
import numpy as np
from matplotlib.patches import Rectangle

# Load the CSV data
file_path = 'Spring Intrasquads MASTER.csv'  # Ensure this is the correct CSV
data = pd.read_csv(file_path, low_memory=False)

# Streamlit app setup
st.set_page_config(page_title="Post-Game Hitter Report", layout="centered")

# Sidebar for user selection
selected_date = st.sidebar.selectbox("Select a Date", data['Date'].unique())
data_by_date = data[data['Date'] == selected_date]

batter_name = st.sidebar.selectbox("Select a Batter", data_by_date['Batter'].unique())
batter_data = data_by_date[data_by_date['Batter'] == batter_name]

if batter_data.empty:
    st.warning("No data available for the selected batter and date.")
    st.stop()

# Extract today's date
today_date = batter_data['Date'].iloc[0]

# PITCH TRACKING GRAPHIC
st.markdown(f"## Hitting Summary for {batter_name}")

fig = plt.figure(figsize=(11, 8.5))
gs = GridSpec(3, 5, figure=fig, width_ratios=[1, 1, 1, 0.75, 1.25], height_ratios=[1, 1, 1])
gs.update(wspace=0.2, hspace=0.3)

strike_zone_width = 17 / 12
strike_zone_params = {'x_start': -strike_zone_width / 2, 'y_start': 1.5, 'width': strike_zone_width, 'height': 3.3775 - 1.5}

plate_appearance_groups = batter_data.groupby((batter_data['PitchofPA'] == 1).cumsum())

axes = []
for i in range(min(len(plate_appearance_groups), 9)):
    ax = fig.add_subplot(gs[i // 3, i % 3])
    axes.append(ax)

for i, (pa_id, pa_data) in enumerate(plate_appearance_groups, start=1):
    if i > 9:
        break

    ax = axes[i - 1]
    ax.set_aspect(1)
    pitcher_name = pa_data.iloc[0]['Pitcher']

    ax.set_title(f'PA {i} vs {pitcher_name}', fontsize=12, fontweight='bold')

    strike_zone = plt.Rectangle((strike_zone_params['x_start'], strike_zone_params['y_start']),
                                strike_zone_params['width'], strike_zone_params['height'],
                                fill=False, color='black', linewidth=2, zorder=1)
    ax.add_patch(strike_zone)

    for _, row in pa_data.iterrows():
        sns.scatterplot(
            x=[row['PlateLocSide']],
            y=[row['PlateLocHeight']],
            color='blue',
            marker='o',
            s=150,
            legend=False,
            ax=ax,
            zorder=2
        )
        ax.text(row['PlateLocSide'], row['PlateLocHeight'], str(int(row['PitchofPA'])),
                color='white', fontsize=8, ha='center', va='center', weight='bold', zorder=3)

    ax.set_xlim(strike_zone_params['x_start'] - 0.5, strike_zone_params['x_start'] + strike_zone_params['width'] + 0.5)
    ax.set_ylim(strike_zone_params['y_start'] - 0.5, strike_zone_params['y_start'] + strike_zone_params['height'] + 0.5)
    ax.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel('')
    ax.set_ylabel('')

st.pyplot(fig)

# BATTED BALL FIELD GRAPHIC
st.markdown("### Batted Ball Locations")

fig, ax = plt.subplots(figsize=(10, 10))

# Define field dimensions
LF_foul_pole = 330
LC_gap = 365
CF = 390
RC_gap = 365
RF_foul_pole = 330

angles = np.linspace(-45, 45, 500)
distances = np.interp(angles, [-45, -30, 0, 30, 45], [LF_foul_pole, LC_gap, CF, RC_gap, RF_foul_pole])
x_outfield = distances * np.sin(np.radians(angles))
y_outfield = distances * np.cos(np.radians(angles))
ax.plot(x_outfield, y_outfield, color="black", linewidth=2)

# Draw foul lines
foul_x_left = [-LF_foul_pole * np.sin(np.radians(45)), 0]
foul_y_left = [LF_foul_pole * np.cos(np.radians(45)), 0]
foul_x_right = [RF_foul_pole * np.sin(np.radians(45)), 0]
foul_y_right = [RF_foul_pole * np.cos(np.radians(45)), 0]
ax.plot(foul_x_left, foul_y_left, color="black", linestyle="-")
ax.plot(foul_x_right, foul_y_right, color="black", linestyle="-")

# Draw infield
infield_side = 90
bases_x = [0, infield_side, 0, -infield_side, 0]
bases_y = [0, infield_side, 2 * infield_side, infield_side, 0]
ax.plot(bases_x, bases_y, color="brown", linewidth=2)

# Plot batted ball locations with PA numbers and ExitSpeed
play_result_styles = {
    "Single": ("blue", "o"),
    "Double": ("purple", "o"),
    "Triple": ("gold", "o"),
    "HomeRun": ("orange", "o"),
    "Out": ("black", "o"),
}

for pa_number, pa_data in plate_appearance_groups:
    if pa_data.empty:
        continue
    last_pitch = pa_data.iloc[-1]
    bearing = np.radians(last_pitch["Bearing"])
    distance = last_pitch["Distance"]
    exit_speed = round(last_pitch["ExitSpeed"], 1) if pd.notnull(last_pitch["ExitSpeed"]) else "NA"
    play_result = last_pitch["PlayResult"]

    x = distance * np.sin(bearing)
    y = distance * np.cos(bearing)
    color, marker = play_result_styles.get(play_result, ("black", "o"))

    ax.scatter(x, y, color=color, marker=marker, s=150, edgecolor="black")
    ax.text(x, y, str(pa_number), color="white", fontsize=10, fontweight="bold", ha="center", va="center")

    ax.text(
        x, y - 15,
        f"{exit_speed} mph" if exit_speed != "NA" else "NA",
        color="red", fontsize=8, fontweight="bold", ha="center",
    )

# Remove axis labels and ticks
ax.set_xticks([])
ax.set_yticks([])
ax.set_xlabel("")
ax.set_ylabel("")
ax.axis("equal")
ax.set_title(f"Batted Ball Locations for {batter_name} (InPlay)", fontsize=16)

# Add legend for PlayResults
legend_elements = [
    plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="blue", markersize=10, label="Single"),
    plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="purple", markersize=10, label="Double"),
    plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="gold", markersize=10, label="Triple"),
    plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="orange", markersize=10, label="HomeRun"),
    plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="black", markersize=10, label="Out"),
]
fig.legend(handles=legend_elements, loc="lower center", ncol=5, fontsize=10, frameon=False)

plt.subplots_adjust(bottom=0.15)
st.pyplot(fig)

st.markdown("---")
st.markdown("*Generated by Post-Game Hitter Report App*")
