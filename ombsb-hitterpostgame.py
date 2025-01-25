import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# Load the CSV data
file_path = 'Spring Intrasquads MASTER.csv'
data = pd.read_csv(file_path, low_memory=False)

# Streamlit app
st.set_page_config(page_title="Post-Game Hitter Report", layout="centered")

# Sidebar for selecting date
selected_date = st.sidebar.selectbox("Select a Date", data['Date'].unique())
data_by_date = data[data['Date'] == selected_date]

# Sidebar for selecting batter
batter_name = st.sidebar.selectbox("Select a Batter", data_by_date['Batter'].unique())

# Filter data for the selected batter
batter_data = data_by_date[data_by_date['Batter'] == batter_name]

# Extract today's date from the "Date" column in the CSV
today_date = batter_data['Date'].iloc[0] if not batter_data.empty else "Unknown Date"

# Calculate values for the game stats table
PA = batter_data[batter_data['PitchofPA'] == 1].shape[0]
H = batter_data[batter_data['PlayResult'].isin(["Single", "Double", "Triple", "HomeRun"])].shape[0]
Doubles = batter_data[batter_data['PlayResult'] == "Double"].shape[0]
Triples = batter_data[batter_data['PlayResult'] == "Triple"].shape[0]
HR = batter_data[batter_data['PlayResult'] == "HomeRun"].shape[0]
TB = (batter_data['PlayResult'] == "Single").sum() * 1 + \
     (batter_data['PlayResult'] == "Double").sum() * 2 + \
     (batter_data['PlayResult'] == "Triple").sum() * 3 + \
     (batter_data['PlayResult'] == "HomeRun").sum() * 4
RBI = batter_data['RunsScored'].sum()
BB = batter_data[batter_data['KorBB'] == "Walk"].shape[0]
HBP = batter_data[batter_data['PitchCall'] == "HitByPitch"].shape[0]
SO = batter_data[batter_data['KorBB'] == "Strikeout"].shape[0]
EVMax = batter_data['ExitSpeed'].max()
EVAvg = batter_data['ExitSpeed'].mean()

# Define game stats for the table
game_stats = pd.DataFrame({
    "PA": [PA], "H": [H], "2B": [Doubles], "3B": [Triples], "HR": [HR],
    "TB": [TB], "RBI": [RBI], "BB": [BB], "HBP": [HBP], "SO": [SO],
    "EVMax": [round(EVMax, 1) if pd.notnull(EVMax) else None],
    "EVAvg": [round(EVAvg, 1) if pd.notnull(EVAvg) else None]
})

# Define plate appearances table dynamically
plate_appearances = []

# Group data by plate appearances dynamically using groupby
plate_appearance_groups = batter_data.groupby((batter_data['PitchofPA'] == 1).cumsum())

for pa_number, pa_data in enumerate(plate_appearance_groups, start=1):
    pa_id, pa_rows = pa_data
    if pa_rows.empty:
        plate_appearances.append([pa_number, "NA", "NA", "NA", 0, "NA", "NA", "NA", "NA", "NA"])
        continue

    inning = pa_rows['Inning'].iloc[0] if not pa_rows['Inning'].isnull().all() else "NA"
    pitcher = pa_rows['Pitcher'].iloc[0] if not pa_rows['Pitcher'].isnull().all() else "NA"

    # Determine result
    result_candidates = [
        ("KorBB", pa_rows[pa_rows['KorBB'].isin(["Strikeout", "Walk"])]),
        ("PlayResult", pa_rows[pa_rows['PlayResult'].isin(["Out", "Single", "Double", "Triple", "HomeRun", "Sacrifice"])]),
        ("PitchCall", pa_rows[pa_rows['PitchCall'] == "HitByPitch"])
    ]
    result = "NA"
    for column, candidates in result_candidates:
        if not candidates.empty:
            result = candidates.iloc[0][column]
            break

    # Runs scored
    runs = pa_rows['RunsScored'].sum()

    # Last pitch data
    last_pitch = pa_rows.iloc[-1]
    pitch = last_pitch['TaggedPitchType'] if pd.notnull(last_pitch['TaggedPitchType']) else "NA"
    pitch_speed = round(last_pitch['RelSpeed'], 1) if pd.notnull(last_pitch['RelSpeed']) else "NA"
    ev = round(last_pitch['ExitSpeed'], 1) if pd.notnull(last_pitch['ExitSpeed']) else "NA"
    la = round(last_pitch['Angle'], 1) if pd.notnull(last_pitch['Angle']) else "NA"
    distance = round(last_pitch['Distance'], 1) if pd.notnull(last_pitch['Distance']) else "NA"

    plate_appearances.append([pa_number, inning, pitcher, result, runs, pitch, pitch_speed, ev, la, distance])

plate_appearances_df = pd.DataFrame(plate_appearances, columns=["PA #", "Inning", "Pitcher", "Result", "Runs", "Pitch", "PitchSpeed", "EV", "LA", "Distance"])

# Ensure all numerical values are rounded to one decimal place in the plate appearances table
numerical_columns = ["PitchSpeed", "EV", "LA", "Distance"]
for col in numerical_columns:
    plate_appearances_df[col] = pd.to_numeric(plate_appearances_df[col], errors='coerce').round(1)

# Streamlit layout
st.title(f"Post-Game Hitter Report: {batter_name}")
st.subheader(f"Date: {selected_date}")

st.markdown("### Game Stats")
st.table(game_stats)

st.markdown("### Plate Appearances")
st.table(plate_appearances_df)

# Add strike zone plots
st.markdown("### Pitches and Results")
strike_zone_width = 17 / 12  # 1.41667 feet
strike_zone_params = {'x_start': -strike_zone_width / 2, 'y_start': 1.5, 'width': strike_zone_width, 'height': 3.3775 - 1.5}

pitch_call_markers = {
    "StrikeCalled": ("red", "D"),
    "StrikeSwinging": ("red", "s"),
    "BallCalled": ("green", "s"),
    "FoulBallFieldable": ("pink", "^"),
    "FoulBallNotFieldable": ("pink", "^"),
    "Out": ("black", "o"),
    "Single": ("blue", "o"),
    "Double": ("purple", "o"),
    "Triple": ("yellow", "o"),
    "HomeRun": ("orange", "o")
}

fig, axes = plt.subplots(1, len(plate_appearance_groups), figsize=(len(plate_appearance_groups) * 4, 6))
if len(plate_appearance_groups) == 1:
    axes = [axes]  # Ensure axes is iterable

for ax, (pa_number, pa_data) in zip(axes, plate_appearance_groups):
    ax.set_xlim([-1, 1])
    ax.set_ylim([1, 4])
    ax.add_patch(Rectangle((strike_zone_params['x_start'], strike_zone_params['y_start']),
                           strike_zone_params['width'], strike_zone_params['height'],
                           fill=False, color="black", lw=2))
    ax.set_title(f"PA {pa_number}")
    ax.set_xlabel("PlateLocSide")
    ax.set_ylabel("PlateLocHeight")

    for _, pitch in pa_data.iterrows():
        pitch_of_pa = int(pitch['PitchofPA'])
        plate_loc_side = pitch['PlateLocSide']
        plate_loc_height = pitch['PlateLocHeight']
        pitch_call = pitch['PitchCall']
        play_result = pitch['PlayResult']

        if pitch_call == "InPlay":
            color, marker = pitch_call_markers.get(play_result, ("gray", "o"))
        else:
            color, marker = pitch_call_markers.get(pitch_call, ("gray", "o"))

        ax.scatter(plate_loc_side, plate_loc_height, color=color, marker=marker, s=100)
        ax.text(plate_loc_side, plate_loc_height, str(pitch_of_pa), color="white", fontsize=8, ha="center", va="center")

st.pyplot(fig)

st.markdown("---")
st.markdown("*Generated by Post-Game Hitter Report App*")
