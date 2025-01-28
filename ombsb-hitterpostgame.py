import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.gridspec import GridSpec
import matplotlib.image as mpimg

# Load the CSV data
file_path = 'Spring Intrasquads MASTER.csv'
data = pd.read_csv(file_path, low_memory=False)

# Load the Ole Miss logo
logo_path = 'OMBaseballLogo.jpeg'
logo_img = mpimg.imread(logo_path)

# Streamlit app configuration
st.set_page_config(page_title="Post-Game Hitter Report", layout="centered")

# Sidebar for selecting date and batter
selected_date = st.sidebar.selectbox("Select a Date", data['Date'].unique())
data_by_date = data[data['Date'] == selected_date]

batter_name = st.sidebar.selectbox("Select a Batter", data_by_date['Batter'].unique())
batter_data = data_by_date[data_by_date['Batter'] == batter_name]

# Group data by plate appearances
plate_appearance_groups = batter_data.groupby((batter_data['PitchofPA'] == 1).cumsum())

# Plot Hitting Summary Graphic
fig = plt.figure(figsize=(11, 8.5))
gs = GridSpec(3, 5, figure=fig, width_ratios=[1, 1, 1, 0.75, 1.25], height_ratios=[1, 1, 1])
gs.update(wspace=0.2, hspace=0.3)
plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

# Strike zone parameters
strike_zone_width = 17 / 12
strike_zone_params = {'x_start': -strike_zone_width / 2, 'y_start': 1.5, 'width': strike_zone_width, 'height': 3.3775 - 1.5}
shadow_zone_width = strike_zone_width + 0.245
shadow_zone_params = {'x_start': -shadow_zone_width / 2, 'y_start': 1.37750, 'width': shadow_zone_width, 'height': 3.5000 - 1.37750}

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

    shadow_zone = plt.Rectangle((shadow_zone_params['x_start'], shadow_zone_params['y_start']),
                                shadow_zone_params['width'], shadow_zone_params['height'],
                                fill=False, color='gray', linestyle='--', linewidth=2, zorder=1)
    ax.add_patch(shadow_zone)

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

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(strike_zone_params['x_start'] - 0.5, strike_zone_params['x_start'] + strike_zone_params['width'] + 0.5)
    ax.set_ylim(strike_zone_params['y_start'] - 0.5, strike_zone_params['y_start'] + strike_zone_params['height'] + 0.5)

# Add Ole Miss logo
logo_ax = fig.add_axes([0.78, 0.92, 0.08, 0.08], anchor='NE', zorder=1)
logo_ax.imshow(logo_img)
logo_ax.axis('off')

# Add Title
fig.suptitle(f'Hitting Summary for {batter_name}', fontsize=16, weight='bold')

# Display the figure in Streamlit
st.pyplot(fig)

# --------------------------- BATTED BALL FIELD GRAPHIC ---------------------------

st.markdown("### Batted Ball Locations")

fig, ax = plt.subplots(figsize=(10, 10))

# Draw the outfield fence
LF_foul_pole, LC_gap, CF, RC_gap, RF_foul_pole = 330, 365, 390, 365, 330
angles = np.linspace(-45, 45, 500)
distances = np.interp(angles, [-45, -30, 0, 30, 45], [LF_foul_pole, LC_gap, CF, RC_gap, RF_foul_pole])
x_outfield = distances * np.sin(np.radians(angles))
y_outfield = distances * np.cos(np.radians(angles))
ax.plot(x_outfield, y_outfield, color="black", linewidth=2)

# Draw the foul lines
ax.plot([-LF_foul_pole * np.sin(np.radians(45)), 0], [LF_foul_pole * np.cos(np.radians(45)), 0], color="black")
ax.plot([RF_foul_pole * np.sin(np.radians(45)), 0], [RF_foul_pole * np.cos(np.radians(45)), 0], color="black")

# Draw the infield
infield_side = 90
ax.plot([0, infield_side, 0, -infield_side, 0], [0, infield_side, 2 * infield_side, infield_side, 0], color="brown", linewidth=2)

# Plot batted ball locations
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
    
    x, y = distance * np.sin(bearing), distance * np.cos(bearing)
    color, marker = play_result_styles.get(play_result, ("black", "o"))
    
    ax.scatter(x, y, color=color, marker=marker, s=150, edgecolor="black")
    ax.text(x, y, str(pa_number), color="white", fontsize=10, fontweight="bold", ha="center", va="center")
    ax.text(x, y - 15, f"{exit_speed} mph" if exit_speed != "NA" else "NA", color="red", fontsize=8, fontweight="bold", ha="center")

ax.set_xticks([])
ax.set_yticks([])
ax.axis("equal")
ax.set_title(f"Batted Ball Locations for {batter_name}", fontsize=16)

# Add legend
legend_elements = [plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=color, markersize=10, label=label)
                   for label, color in play_result_styles.items()]
fig.legend(handles=legend_elements, loc="lower center", ncol=5, fontsize=10, frameon=False)
plt.subplots_adjust(bottom=0.15)

# Display field plot
st.pyplot(fig)

st.markdown("---")
st.markdown("*Generated by Post-Game Hitter Report App*")
