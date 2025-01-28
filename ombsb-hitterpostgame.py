import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
import matplotlib.image as mpimg

# Load the CSV data
file_path = 'Spring Master CSV - Spring Intrasquads MASTER.csv'
data = pd.read_csv(file_path, low_memory=False)

# Load the Ole Miss logo
logo_path = 'OMBaseballLogo.jpeg'
logo_img = mpimg.imread(logo_path)

# Standardize TaggedPitchType values to ensure consistency
data['TaggedPitchType'] = data['TaggedPitchType'].str.strip().str.capitalize()

# Ensure the 'Date' column is standardized to a single format (YYYY-MM-DD) and drop invalid rows
if 'Date' in data.columns:
    data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
    data = data.dropna(subset=['Date'])
    data['Date'] = data['Date'].dt.strftime('%Y-%m-%d')

# Define color palette for PitchCall
pitch_call_palette = {
    'StrikeCalled': 'orange',
    'BallCalled': 'green',
    'Foul': 'tan',
    'InPlay': 'blue',
    'FoulBallNotFieldable': 'tan',
    'StrikeSwinging': 'red',
    'BallIntentional': 'purple',
    'FoulBallFieldable': 'tan',
    'HitByPitch': 'lime'
}

# Define marker styles for TaggedPitchType
pitch_type_markers = {
    'Fastball': 'o',
    'Curveball': 's',
    'Slider': '^',
    'Changeup': 'D'
}

# Streamlit app setup
st.title("Hitting Summary Viewer")

# Filters
unique_dates = sorted(data['Date'].unique()) if 'Date' in data.columns else []
unique_batters = sorted(data['Batter'].unique())

selected_date = st.selectbox("Select a Date", options=unique_dates) if unique_dates else None
selected_batter = st.selectbox("Select a Batter", options=unique_batters)

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

    fig = plt.figure(figsize=(11, 8.5))  # Adjusted figure size to fit 8x11 paper
    gs = GridSpec(3, 5, figure=fig, width_ratios=[1, 1, 1, 0.75, 1.25], height_ratios=[1, 1, 1])
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

        ax.set_title(f'PA {i} vs {handedness_label}', fontsize=12, fontweight='bold')
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
                marker=pitch_type_markers.get(row['TaggedPitchType'], 'o'),
                s=150,
                legend=False,
                ax=ax
            )
            ax.text(row['PlateLocSide'], row['PlateLocHeight'], f"{int(row['PitchofPA'])}",
                    color='white', fontsize=8, ha='center', va='center', weight='bold')

            pitch_speed = f"{round(row['RelSpeed'], 1)} MPH"
            pitch_type = row['TaggedPitchType']
            final_outcome = row['PitchCall'] if pd.isna(row['PlayResult']) else row['PlayResult']

            # Add rows to table
            pa_rows.append([f"Pitch {int(row['PitchofPA'])}", f"{pitch_speed} {pitch_type}", final_outcome])

        table_data.append([f'PA {i}', '', ''])
        table_data.extend(pa_rows)

        # Add legends
# Add legends
legend_ax = fig.add_subplot(gs[2, :2])  # Place legends in the bottom-left area
legend_ax.axis('off')

handles1 = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=6, linestyle='', label=label)
            for label, color in pitch_call_palette.items()]
legend1 = legend_ax.legend(handles=handles1, title='Pitch Call', loc='lower left', bbox_to_anchor=(-0.05, -0.3), fontsize=10, title_fontsize=12)

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

# Add the Ole Miss logo in the top right corner
logo_ax = fig.add_axes([0.78, 0.92, 0.08, 0.08], anchor='NE', zorder=1)
logo_ax.imshow(logo_img)
logo_ax.axis('off')  # Turn off the axis

# Display the plot in Streamlit
st.pyplot(fig)

# Else block for handling empty data
else:
    st.write("No data available for the selected filters.")
