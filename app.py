import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import pickle 
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
from matplotlib.backends.backend_pdf import PdfPages
import io

st.set_page_config(
    page_title = 'Purdue Baseball Optimal Pitch Locations',
    page_icon = '⚾',
    layout = 'wide',
    initial_sidebar_state='expanded'
)

alt.themes.enable(None)

#### 
fall_data = pd.read_csv("/Users/aidanbeilke/Desktop/Purdue_Base/newman_proj/csvs/fall_xrv.csv")

####
st.sidebar.header("Select a Player-Pitch Type")
player_list = sorted(fall_data['player_name'].unique())
selected_player = st.sidebar.selectbox("Select Player", player_list)

player_data = fall_data[fall_data['player_name'] == selected_player]
pitch_types = sorted(player_data['pitch_type'].unique())
selected_pitch_type = st.sidebar.multiselect("Select Pitch Type", 
                                             pitch_types,
                                             help = "Choose 1 or More Pitch Types")


#### 

def create_plot(df, player, pitch_types, count, return_pdf = False):
    fall_xrv = df[(df['player_name'] == player) &
                   (df['pitch_type'].isin(pitch_types))]

    fall_xrv = fall_xrv.groupby('pitch_type')[['RelSpeed', 'release_pos_x', 'release_pos_z', 
                'HorzBreak', 'InducedVertBreak', 'release_extension',
                'SpinRate', 'SpinAxis', 'avg_RelSpeed', 'avg_release_pos_x', 
                'avg_release_pos_z', 'avg_HorzBreak', 'avg_InducedVertBreak', 
                'arm_angle', 'VertApprAngle', 'iVB_oe']].mean().reset_index()
    
    fall_xrv = pd.concat([fall_xrv] * 50000, ignore_index=True)
    fall_xrv['PlateLocSide'] = np.random.uniform(-2, 2, size=len(fall_xrv)).round(2)
    fall_xrv['PlateLocHeight'] = np.random.uniform(0.5, 4.5, size=len(fall_xrv)).round(2)

    lefties = ['Michael Vallone', 'Easton Storey', 'Justin Guiliano', 'Luke Reasor', 'Issac Milburn']
    if player in lefties:
        fall_xrv['platoon_state'] = np.random.choice([0, 2], size = len(fall_xrv))
    else:
        fall_xrv['platoon_state'] = np.random.choice([1, 3], size = len(fall_xrv))


    if count == 'Ahead in Count':
        fall_xrv['count'] = np.random.choice([1, 2, 5], size = len(fall_xrv))
    elif count == 'Behind in Count':
        fall_xrv['count'] = np.random.choice([3, 6, 7, 9, 10], size = len(fall_xrv))
    elif count == '2 Strikes':
        fall_xrv['count'] = np.random.choice([2, 5, 8, 11], size = len(fall_xrv))
    elif count == 'All':
        fall_xrv['count'] = np.random.randint(0, 11, size = len(fall_xrv))

    xrv_model = "/Users/aidanbeilke/Desktop/Purdue_Base/newman_proj/models/xrv_model.pkl"

    with open(xrv_model, 'rb') as file:
        xrv_model = pickle.load(file)

    loc_features = ['RelSpeed', 'release_pos_x', 'release_pos_z', 'platoon_state', 
                'count', 'HorzBreak', 'InducedVertBreak', 'release_extension',
                'SpinRate', 'PlateLocHeight', 'PlateLocSide', 'SpinAxis', 'avg_RelSpeed',
                'avg_release_pos_x', 'avg_release_pos_z', 'avg_HorzBreak', 'avg_InducedVertBreak', 
                'arm_angle', 'VertApprAngle', 'iVB_oe']

    fall_xrv['xrv'] = xrv_model.predict(fall_xrv[loc_features])

    platoon_states = fall_xrv['platoon_state'].unique()
    pitch_types = fall_xrv['pitch_type'].unique()
    num_pitch_types = len(pitch_types)
    rows = num_pitch_types 
    cols = len(platoon_states)  
    rimage_path = "/Users/aidanbeilke/Desktop/Purdue_Base/newman_proj/location_folder/rbatter.jpg"
    limage_path = "/Users/aidanbeilke/Desktop/Purdue_Base/newman_proj/location_folder/lbatter.jpg"

    # Create the subplots
    fig, axes = plt.subplots(rows, cols, figsize=(6 * cols, 4 * rows), sharex=True, sharey=True)
    if rows == 1 and cols == 1:
        axes = np.array([[axes]])  # Ensure it's 2D for consistent indexing
    elif rows == 1 or cols == 1:
        axes = np.atleast_2d(axes)  # Convert to 2D array if single row/column

    fig.suptitle(
        f"{selected_player}\nPitcher's Perspective",
        fontsize=16, 
        fontweight='bold',
        y=.97,
        x = .47
    )

    rimg = mpimg.imread(rimage_path)
    limg = mpimg.imread(limage_path)

    # Add individual plots
    for col_idx, platoon_state in enumerate(platoon_states):
        data_platoon = fall_xrv[fall_xrv['platoon_state'] == platoon_state]
        for row_idx, pitch_type in enumerate(pitch_types):
            ax = axes[row_idx, col_idx] if rows > 1 else axes[0, col_idx]
            data = data_platoon[data_platoon['pitch_type'] == pitch_type]
            
            # Sort values to get the third lowest
            sorted_xrv = data.sort_values(by='xrv')
            if len(sorted_xrv) > 1:  # Check if there are enough data points
                third_lowest = sorted_xrv.iloc[0]
                third_lowest_x = third_lowest['PlateLocSide']
                third_lowest_y = third_lowest['PlateLocHeight']
            
            # Hexbin plot
            hb = ax.hexbin(
                data['PlateLocSide'], 
                data['PlateLocHeight'], 
                C=data['xrv'], 
                gridsize=20, 
                reduce_C_function=np.median, 
                cmap='RdBu'
            )
            
            # Add strike zone rectangle
            strike_zone = Rectangle((-0.71, 1.6), 1.42, 1.9, linewidth=1, edgecolor='black', facecolor='none')
            ax.add_patch(strike_zone)
            
            # Add circle for third lowest
            if len(sorted_xrv) > 1:
                circle = Circle((third_lowest_x, third_lowest_y), 
                                radius=0.3, edgecolor='black', facecolor='none', linewidth=2)
                ax.add_patch(circle)

            if platoon_state in [0, 1]:
                image = limg
                image_box = OffsetImage(image, zoom=0.5)  # Adjust `zoom` for image size
                ab = AnnotationBbox(
                    image_box, 
                    (-1.3, 2.5),  # Adjust coordinates to position the image
                    frameon=False
                )
                ax.add_artist(ab)
            else:
                image = rimg
                image_box = OffsetImage(image, zoom=0.5)  # Adjust `zoom` for image size
                ab = AnnotationBbox(
                    image_box, 
                    (1.3, 2.7),  # Adjust coordinates to position the image
                    frameon=False
                )
                ax.add_artist(ab)
            
            # Add titles for each plot with pitch type
            ax.set_title(f"{pitch_type}", fontsize=10)

            # Label the leftmost plots with y-axis labels
            if col_idx == 0:
                ax.set_ylabel("Plate Location Height", fontsize=10)

            # Label the bottom plots with x-axis labels
            if row_idx == rows - 1:
                ax.set_xlabel("Plate Location Side", fontsize=10)

    # Adjust layout and add a colorbar
    plt.tight_layout(rect=[0, 0, 0.9, .999])

    pdf_buffer = io.BytesIO()


    with PdfPages(pdf_buffer) as pdf:
        # Save the figure to the PDF buffer
        plt.tight_layout(rect=[0, 0, 0.9, .999])
        pdf.savefig(fig)
        plt.close(fig)

    pdf_buffer.seek(0) 

    return fig, pdf_buffer


if selected_pitch_type:
    fig, pdf_buffer = create_plot(fall_data, selected_player, selected_pitch_type, "All", return_pdf=True)
    
    # Display the download button at the top
    st.download_button(
        label="Download Plots as PDF",
        data=pdf_buffer,
        file_name=f"{selected_player}_optimal_pitch_locations.pdf",
        mime="application/pdf",
    )
    
    st.pyplot(fig)
else:
    st.warning("Please select at least one pitch type.")