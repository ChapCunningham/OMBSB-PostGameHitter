import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the CSV data
file_path = 'Spring Intrasquads MASTER.csv'
data = pd.read_csv(file_path, low_memory=False)

# Sidebar for selecting date and batter
selected_date = st.sidebar.selectbox("Select a Date", data['Date'].unique())
data_by_date = data[data['Date'] == selected_date]
batter_name = st.sidebar.selectbox("Select a Batter", data_by_date['Batter'].unique())

# Filter data for the selected batter
batter_data = data_by_date[data_by_date['Batter'] == batter_name]

# Group by plate appearances
plate_appearance_groups = batter_data.groupby((batter_data['PitchofPA'] == 1).cumsum())

# Batted Ball Field Map
st.markdown("### Batted Ball Locations")

fig, ax = plt.subplots(figsize=(10, 10))

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
ax.plot(x_outfield, y_outfield, color="black", linewidth=2)

# Draw the foul lines
foul_x_left = [-LF_foul_pole * np.sin(np.radians(45)), 0]
foul_y_left = [LF_foul_pole * np.cos(np.radians(45)), 0]
foul_x_right = [RF_foul_pole * np.sin(np.radians(45)), 0]
foul_y_right = [RF_foul_pole * np.cos(np.radians(45)), 0]
ax.plot(foul_x_left, foul_y_left, color="black", linestyle="-")
ax.plot(foul_x_right, foul_y_right, color="black", linestyle="-")

# Draw the infield
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

    # Convert polar to Cartesian coordinates
    x = distance * np.sin(bearing)
    y = distance * np.cos(bearing)

    # Get play result style
    color, marker = play_result_styles.get(play_result, ("black", "o"))

    # Plot the hit location
    ax.scatter(x, y, color=color, marker=marker, s=150, edgecolor="black")

    # Add PA number in bold white
    ax.text(x, y, str(pa_number), color="white", fontsize=10, fontweight="bold", ha="center", va="center")

    # Add ExitSpeed below the plot
    ax.text(
        x, y - 15,  # Adjust y-coordinate to position below
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

# Adjust layout to make room for the legend
plt.subplots_adjust(bottom=0.15)

# Display the plot in Streamlit
st.pyplot(fig)
