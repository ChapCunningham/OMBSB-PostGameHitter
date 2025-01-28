import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
import matplotlib.image as mpimg

# Load the CSV data
file_path = 'Spring Intrasquads MASTER.csv'
data = pd.read_csv(file_path, low_memory=False)

# Load the Ole Miss logo
logo_path = 'OMBaseballLogo.jpeg'
logo_img = mpimg.imread(logo_path)

# Streamlit app
st.set_page_config(page_title="Post-Game Hitter Report", layout="wide")

# Sidebar for selecting date
selected_date = st.sidebar.selectbox("Select a Date", data['Date'].unique())
data_by_date = data[data['Date'] == selected_date]

# Sidebar for selecting batter
batter_name = st.sidebar.selectbox("Select a Batter", data_by_date['Batter'].unique())

# Filter data for the selected batter
batter_data = data_by_date[data_by_date['Batter'] == batter_name]

### HITTING SUMMARY GRAPHIC ###
def generate_hitting_summary(batter_data):
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

    return fig

st.title(f"Post-Game Hitter Report: {batter_name}")
st.subheader(f"Date: {selected_date}")

# Display the hitting summary graphic
summary_fig = generate_hitting_summary(batter_data)
st.pyplot(summary_fig)

st.markdown("---")

### BATTED BALL FIELD OUTLINE GRAPHIC ###
def generate_batted_ball_field(batter_data):
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Load baseball field image (Ensure path is correct)
    field_image_path = 'baseball_field.png'
    field_img = mpimg.imread(field_image_path)
    
    ax.imshow(field_img, extent=[-250, 250, 0, 400], aspect='auto')

    # Plot batted balls
    in_play = batter_data[batter_data['PlayResult'].isin(["Single", "Double", "Triple", "HomeRun", "Out"])]
    
    color_map = {
        "Out": "black",
        "Single": "blue",
        "Double": "purple",
        "Triple": "yellow",
        "HomeRun": "orange"
    }

    for _, row in in_play.iterrows():
        play_result = row['PlayResult']
        x_coord, y_coord = row['HitX'], row['HitY']
        
        ax.scatter(x_coord, y_coord, color=color_map.get(play_result, "gray"), s=80, label=play_result, edgecolors="white", linewidth=1.2)
        ax.text(x_coord, y_coord, play_result[0], fontsize=12, fontweight="bold", ha="center", va="center", color="white")

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_title("Batted Ball Locations", fontsize=14, fontweight="bold")

    return fig

# Display the batted ball field graphic
field_fig = generate_batted_ball_field(batter_data)
st.pyplot(field_fig)

st.markdown("---")
st.markdown("*Generated by Post-Game Hitter Report App*")
