import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
import numpy as np
import matplotlib.image as mpimg

# Load the CSV data
file_path = 'Spring Intrasquads MASTER.csv'
data = pd.read_csv(file_path, low_memory=False)

# Load the Ole Miss logo
logo_path = 'OMBaseballLogo.jpeg'
logo_img = mpimg.imread(logo_path)

# Streamlit app
st.set_page_config(page_title="Post-Game Hitter Report", layout="centered")

# Sidebar for selecting date and batter
selected_date = st.sidebar.selectbox("Select a Date", data['Date'].unique())
data_by_date = data[data['Date'] == selected_date]

batter_name = st.sidebar.selectbox("Select a Batter", data_by_date['Batter'].unique())
batter_data = data_by_date[data_by_date['Batter'] == batter_name]

# Group data by plate appearances
plate_appearance_groups = batter_data.groupby((batter_data['PitchofPA'] == 1).cumsum())

# Generate and display the hitting summary graphic
fig = plt.figure(figsize=(11, 8.5))
gs = GridSpec(3, 5, figure=fig, width_ratios=[1, 1, 1, 0.75, 1.25], height_ratios=[1, 1, 1])
gs.update(wspace=0.2, hspace=0.3)

plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

strike_zone_width = 17 / 12
strike_zone_params = {'x_start': -strike_zone_width / 2, 'y_start': 1.5, 'width': strike_zone_width, 'height': 3.3775 - 1.5}
shadow_zone_width = strike_zone_width + 0.245
shadow_zone_params = {'x_start': -shadow_zone_width / 2, 'y_start': 1.37750, 'width': shadow_zone_width, 'height': 3.5000 - 1.37750}
x_buffer = 0.40 * strike_zone_width
y_buffer = 0.40 * (3.3775 - 1.5)

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

    ax.set_xlim(strike_zone_params['x_start'] - x_buffer, strike_zone_params['x_start'] + strike_zone_params['width'] + x_buffer)
    ax.set_ylim(strike_zone_params['y_start'] - y_buffer, strike_zone_params['y_start'] + strike_zone_params['height'] + y_buffer)
    ax.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel('')
    ax.set_ylabel('')

st.pyplot(fig)
st.markdown("### Batted Ball Locations")

fig, ax = plt.subplots(figsize=(10, 10))
LF_foul_pole, LC_gap, CF, RC_gap, RF_foul_pole = 330, 365, 390, 365, 330
angles = np.linspace(-45, 45, 500)
distances = np.interp(angles, [-45, -30, 0, 30, 45], [LF_foul_pole, LC_gap, CF, RC_gap, RF_foul_pole])
x_outfield = distances * np.sin(np.radians(angles))
y_outfield = distances * np.cos(np.radians(angles))
ax.plot(x_outfield, y_outfield, color="black", linewidth=2)
ax.set_xticks([])
ax.set_yticks([])
ax.set_xlabel("")
ax.set_ylabel("")
ax.axis("equal")
ax.set_title(f"Batted Ball Locations for {batter_name} (InPlay)", fontsize=16)
st.pyplot(fig)
