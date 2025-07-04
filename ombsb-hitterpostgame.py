import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
import matplotlib.image as mpimg
import numpy as np

# Load the CSV data
file_path = '2025_SEASON.csv'
data = pd.read_csv(file_path, low_memory=False)
data = data[data['BatterTeam'] == 'OLE_REB']

# Load the Ole Miss logo
logo_path = 'OMBaseballLogo.jpeg'
logo_img = mpimg.imread(logo_path)

# Standardize AutoPitchType values to ensure consistency
data['AutoPitchType'] = data['AutoPitchType'].str.strip().str.capitalize()

# Ensure the 'Date' column is standardized to a single format (YYYY-MM-DD) and drop invalid rows
if 'Date' in data.columns:
    data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
    data = data.dropna(subset=['Date'])
    data['Date'] = data['Date'].dt.strftime('%Y-%m-%d')

# Define color palette for PitchCall
pitch_call_palette = {
    'StrikeCalled': 'orange',
    'BallCalled': 'green',
    'BallinDirt': 'green',
    'Foul': 'tan',
    'InPlay': 'blue',
    'FoulBallNotFieldable': 'tan',
    'StrikeSwinging': 'red',
    'BallIntentional': 'purple',
    'FoulBallFieldable': 'tan',
    'HitByPitch': 'lime'
}

# Define marker styles for AutoPitchType
pitch_type_markers = {
    'Fastball': 'o',
    'Curveball': 's',
    'Slider': '^',
    'Changeup': 'D'
}

# Streamlit app setup
st.title("Hitting Summary Viewer")

# Get unique dates for selection
unique_dates = sorted(data['Date'].unique()) if 'Date' in data.columns else []

# Automatically select the most recent date upon app launch
if unique_dates:
    default_date = max(unique_dates)  # Most recent date
    selected_date = st.selectbox("Select a Date", options=unique_dates, index=unique_dates.index(default_date))
else:
    selected_date = None

# Filter the data based on the selected date first
filtered_data = data[data['Date'] == selected_date] if selected_date else data

# Get unique batters from the **filtered** data
unique_batters = sorted(filtered_data['Batter'].unique()) if not filtered_data.empty else []

# Create batter selection dropdown with only available batters
selected_batter = st.selectbox("Select a Batter", options=unique_batters)

# Filter data further based on selected batter
if selected_batter:
    filtered_data = filtered_data[filtered_data['Batter'] == selected_batter]


# Filter data based on user selection
filtered_data = data
if selected_date:
    filtered_data = filtered_data[filtered_data['Date'] == selected_date]
if selected_batter:
    filtered_data = filtered_data[filtered_data['Batter'] == selected_batter]

# Generate plot for selected batter
if not filtered_data.empty:
    plate_appearance_groups = filtered_data.groupby((filtered_data['PitchofPA'] == 1).cumsum())
    num_pa = len(plate_appearance_groups)

    # Adjustable scaling factor for graphic size
    graphic_scale = 1  # Adjust this value (1.0 is original size, increase for a bigger graphic)

# Create the figure with adjustable size
    fig = plt.figure(figsize=(15, 8.5)) 

    gs = GridSpec(3, 5, figure=fig, width_ratios=[1.5, 1.5, 1.5, 1, 1.5], height_ratios=[1, 1, 1])
    gs.update(wspace=0.2, hspace=0.3)  # Increase vertical space slightly

    # Create small plots in the left half using GridSpec
    axes = []
    for i in range(min(num_pa, 9)):
        ax = fig.add_subplot(gs[i // 3, i % 3])
        ax.set_xlim(-1.5, 1.5)  # Ensuring the same x-limits for consistency
        ax.set_ylim(1, 4)  # Ensuring the same y-limits
        ax.set_xticks([])  # Remove ticks
        ax.set_yticks([])
        ax.set_aspect(1)  # Maintain square aspect ratio
        axes.append(ax)

    table_data = []

    # Strike zone and "Heart" of the zone parameters
    strike_zone_width = 17 / 12  # 1.41667 feet
    strike_zone_params = {'x_start': -strike_zone_width / 2, 'y_start': 1.5, 'width': strike_zone_width, 'height': 3.3775 - 1.5}
    heart_zone_params = {
        'x_start': strike_zone_params['x_start'] + strike_zone_params['width'] * 0.25,
        'y_start': strike_zone_params['y_start'] + strike_zone_params['height'] * 0.25,
        'width': strike_zone_params['width'] * 0.5,
        'height': strike_zone_params['height'] * 0.5
    }
    shadow_zone_params = {'x_start': -strike_zone_width / 2 - 0.2, 'y_start': 1.3, 'width': strike_zone_width + 0.4, 'height': 3.6 - 1.3}

    for i, (pa_id, pa_data) in enumerate(plate_appearance_groups, start=1):
        if i > 9:
            break

        ax = axes[i - 1]

        # Pitcher Information
        pitcher_throws = pa_data.iloc[0]['PitcherThrows']
        handedness_label = 'RHP' if pitcher_throws == 'Right' else 'LHP'
        pitcher_name = pa_data.iloc[0]['Pitcher']

        marker_size = 200  # Adjusted for better visibility
        # Add the PA number and handedness label above each plot
        ax.set_title(f'PA {i} vs {handedness_label}', fontsize=14, fontweight='bold')

        # Add the opposing Pitcher’s name under the PA graph
        ax.text(0.5, -0.12, f'P: {pitcher_name}', fontsize=10, fontstyle='italic', ha='center', transform=ax.transAxes)

       




        pa_rows = []

        # Draw strike zone and shadow zone
        ax.add_patch(plt.Rectangle((shadow_zone_params['x_start'], shadow_zone_params['y_start']),
                                   shadow_zone_params['width'], shadow_zone_params['height'],
                                   fill=False, color='gray', linestyle='--', linewidth=2))
        ax.add_patch(plt.Rectangle((strike_zone_params['x_start'], strike_zone_params['y_start']),
                                   strike_zone_params['width'], strike_zone_params['height'],
                                   fill=False, color='black', linewidth=2))
        ax.add_patch(plt.Rectangle((heart_zone_params['x_start'], heart_zone_params['y_start']),
                                   heart_zone_params['width'], heart_zone_params['height'],
                                   fill=False, color='red', linestyle='--', linewidth=2))

        for _, row in pa_data.iterrows():
            sns.scatterplot(
                x=[row['PlateLocSide']],
                y=[row['PlateLocHeight']],
                hue=[row['PitchCall']],
                palette=pitch_call_palette,
                marker=pitch_type_markers.get(row['AutoPitchType'], 'o'),
                s=150,
                legend=False,
                ax=ax
            )
            offset = -0.05 if row['AutoPitchType'] == 'Slider' else 0
            ax.text(row['PlateLocSide'], row['PlateLocHeight'] + offset, f"{int(row['PitchofPA'])}",
                color='white', fontsize=8, ha='center', va='center', weight='bold')

    
            pitch_speed = f"{round(row['RelSpeed'], 1)} MPH"
            pitch_type = row['AutoPitchType']
    
    # Extract values for the last pitch
            if row.name == pa_data.index[-1]:  # Check if it's the last pitch in PA
                play_result = row['PlayResult']
                kor_bb_result = row['KorBB']
                pitch_call = row['PitchCall']
        
        # Find the first non-"Undefined" value
                outcome_x = next(
                    (result for result in [play_result, kor_bb_result, pitch_call] if result != "Undefined"),
                    "Undefined"
        )
            else:
                outcome_x = row['PitchCall']  # Empty for non-final pitches in the PA

    # Add row to table data
            pa_rows.append([f"Pitch {int(row['PitchofPA'])}", f"{pitch_speed} {pitch_type}", outcome_x])

        

        table_data.append([f'PA {i}', '', ''])
        table_data.extend(pa_rows)

    # Add legends
    legend_ax = fig.add_subplot(gs[2, :2])  # Place legends in the bottom-left area
    legend_ax.axis('off')

    handles1 = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=6, linestyle='', label=label)
                for label, color in pitch_call_palette.items()]
    legend1 = legend_ax.legend(handles=handles1, title='Pitch Call', loc='lower left', bbox_to_anchor=(1, -0.3), fontsize=10, title_fontsize=12)

    handles2 = [plt.Line2D([0], [0], marker=marker, color='black', markersize=6, linestyle='', label=label)
                for label, marker in pitch_type_markers.items()]
    legend2 = legend_ax.legend(handles=handles2, title='Pitch Type', loc='lower left', bbox_to_anchor=(0.6, -0.3), fontsize=10, title_fontsize=12)

    legend_ax.add_artist(legend1)

    # Add the pitch-by-pitch table
    ax_table = fig.add_subplot(gs[:, 3:])  # Use the last column for the table
    ax_table.axis('off')

    y_position = 1.0
    x_position = 0.05
    for row in table_data:
        if 'PA' in row[0]:  # Highlight plate appearances
            ax_table.text(x_position, y_position, f'{row[0]}', fontsize=10, fontweight='bold', fontstyle='italic')
            ax_table.axhline(y=y_position - 0.01, color='black', linewidth=1)  # Add a separator line
            y_position -= 0.05
        else:  # Add pitch details
            text_str = f"  {row[0]}  |  {row[1]}  |  {row[2]}"
            ax_table.text(x_position, y_position, text_str, fontsize=7)  # Adjusted font size for better fit
            y_position -= 0.04  # Adjusted spacing for better fit

    # Add the main title to the figure above the first graphic, aligned with the logo
    fig.suptitle(f"{selected_batter} Report for {selected_date}", fontsize=18, weight='bold')

    # --- Compute Postgame Stats ---
    whiffs = filtered_data['PitchCall'].eq('StrikeSwinging').sum()

    hard_hits = filtered_data[
        (filtered_data['PitchCall'] == 'InPlay') & 
        (filtered_data['ExitSpeed'] >= 95)
    ].shape[0]

    barrels = filtered_data[
        (filtered_data['ExitSpeed'] >= 95) & 
        (filtered_data['Angle'].between(10, 35))
    ].shape[0]

    swing_calls = ['Foul', 'InPlay', 'StrikeSwinging', 'FoulBallFieldable', 'FoulBallNotFieldable']
    swings = filtered_data[filtered_data['PitchCall'].isin(swing_calls)]

    chase_swings = swings[
        (swings['PlateLocSide'] < -0.7083) | (swings['PlateLocSide'] > 0.7083) |
        (swings['PlateLocHeight'] < 1.5) | (swings['PlateLocHeight'] > 3.3775)
    ]
    chase_count = chase_swings.shape[0]

    # --- Add stat line under the title ---
    fig.text(
        0.5, 0.93, 
        f"Whiffs: {whiffs}    Hard Hit: {hard_hits}    Barrels: {barrels}    Chase: {chase_count}", 
        fontsize=12, ha = 'center'
    )



    
    # Add the Ole Miss logo in the top right corner
    logo_ax = fig.add_axes([0.80, 0.92, 0.10, 0.10])  # Adjusted size for alignment
    logo_ax.imshow(logo_img)
    logo_ax.axis('off')  # Hide the axis




    # Display the plot in Streamlit
    st.pyplot(fig)
else:
    st.write("No data available for the selected filters.")






# Initialize session state for rotation
if "rotate_180" not in st.session_state:
    st.session_state.rotate_180 = False  # Start in normal orientation

# Add buttons for rotation and reset
col1, col2 = st.columns(2)
with col1:
    if st.button("Rotate 180°"):
        st.session_state.rotate_180 = not st.session_state.rotate_180  # Toggle rotation
with col2:
    if st.button("Reset"):
        st.session_state.rotate_180 = False  # Reset to normal orientation

# Generate the batted ball graphic
st.markdown("### Batted Ball Locations")

fig, ax = plt.subplots(figsize=(6, 6))

# Draw the outfield fence
LF_foul_pole = 330
LC_gap = 365
CF = 390
RC_gap = 365
RF_foul_pole = 330
angles = np.linspace(-45, 45, 500)
distances = np.interp(angles, [-45, -30, 0, 30, 45], [LF_foul_pole, LC_gap, CF, RC_gap, RF_foul_pole])
x_outfield = distances * np.sin(np.radians(angles))
y_outfield = distances * np.cos(np.radians(angles))

# Rotate the graphic if session state is rotated
if st.session_state.rotate_180:
    x_outfield, y_outfield = -x_outfield, -y_outfield

ax.plot(x_outfield, y_outfield, color="black", linewidth=2)

# Draw the foul lines
foul_x_left = [-LF_foul_pole * np.sin(np.radians(45)), 0]
foul_y_left = [LF_foul_pole * np.cos(np.radians(45)), 0]
foul_x_right = [RF_foul_pole * np.sin(np.radians(45)), 0]
foul_y_right = [RF_foul_pole * np.cos(np.radians(45)), 0]

if st.session_state.rotate_180:
    foul_x_left, foul_y_left = [-x for x in foul_x_left], [-y for y in foul_y_left]
    foul_x_right, foul_y_right = [-x for x in foul_x_right], [-y for y in foul_y_right]

ax.plot(foul_x_left, foul_y_left, color="black", linestyle="-")
ax.plot(foul_x_right, foul_y_right, color="black", linestyle="-")

# Draw the infield
infield_side = 90
bases_x = [0, infield_side, 0, -infield_side, 0]
bases_y = [0, infield_side, 2 * infield_side, infield_side, 0]

if st.session_state.rotate_180:
    bases_x, bases_y = [-x for x in bases_x], [-y for y in bases_y]

ax.plot(bases_x, bases_y, color="brown", linewidth=2)

# Plot batted ball locations with PA numbers and Exit Speed
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

    # Convert polar to Cartesian coordinates
    x = distance * np.sin(bearing)
    y = distance * np.cos(bearing)

    if st.session_state.rotate_180:
        x, y = -x, -y

    # Get play result style
    color, marker = play_result_styles.get(play_result, ("black", "o"))

    # Plot the hit location
    ax.scatter(x, y, color=color, marker=marker, s=150, edgecolor="black")

    # Flip PA number **visually** by rotating it in place
    pa_rotation = 180 if st.session_state.rotate_180 else 0
    ax.text(
        x, y, str(pa_number), 
        color="white", fontsize=10, fontweight="bold", ha="center", va="center",
        rotation=pa_rotation, transform=ax.transData
    )

    # Flip Exit Speed text by rotating it in place
    ev_y_offset = 15 if not st.session_state.rotate_180 else -15
    ev_rotation = 180 if st.session_state.rotate_180 else 0
    ax.text(
        x, y - ev_y_offset, 
        f"{exit_speed} mph" if exit_speed != "NA" else "NA",
        color="red", fontsize=8, fontweight="bold", ha="center",
        rotation=ev_rotation, transform=ax.transData
    )

# Remove axis labels and ticks
ax.set_xticks([])
ax.set_yticks([])
ax.set_xlabel("")
ax.set_ylabel("")
ax.axis("equal")

# Flip the title text if rotated
title_rotation = 180 if st.session_state.rotate_180 else 0
ax.set_title(f"Batted Ball Locations for {selected_batter} (InPlay)", fontsize=16, rotation=title_rotation, va="bottom")

# Add legend for PlayResults
legend_elements = [
    plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="blue", markersize=10, label="Single"),
    plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="purple", markersize=10, label="Double"),
    plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="gold", markersize=10, label="Triple"),
    plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="orange", markersize=10, label="HomeRun"),
    plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="black", markersize=10, label="Out"),
]
fig.legend(handles=legend_elements, loc="lower center", ncol=5, fontsize=10, frameon=False)

# Adjust layout to make room for the legend
plt.subplots_adjust(bottom=0.15)

# Display the plot in Streamlit
st.pyplot(fig)



