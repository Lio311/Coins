import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

# --- Constants ---
SQUARE_SIDE = 10.0  # Side length of the square
CIRCLE_DIAMETER = 1.0
CIRCLE_RADIUS = CIRCLE_DIAMETER / 2.0
DATA_DIR = "data"
COORDS_106_FILE = os.path.join(DATA_DIR, "coords_106.txt")

# --- Coordinate Generation Functions ---

def generate_coords_100_circles():
    """Generates coordinates for a simple 10x10 grid."""
    coords = []
    for row in range(10):
        for col in range(10):
            x = col * CIRCLE_DIAMETER + CIRCLE_RADIUS
            y = row * CIRCLE_DIAMETER + CIRCLE_RADIUS
            coords.append((x, y))
    # Returns coords, packing_width, packing_height
    return np.array(coords), SQUARE_SIDE, SQUARE_SIDE

def generate_coords_105_circles():
    """Generates coordinates for a hexagonal (honeycomb) packing of 105 circles."""
    coords = []
    
    row_height = np.sqrt(3) / 2 * CIRCLE_DIAMETER  # Approx 0.866
    num_rows = 11
    
    # Calculate total packing height
    packing_height = (num_rows - 1) * row_height + CIRCLE_DIAMETER # ~9.66
    
    # Calculate total packing width
    # The long row (10 circles) determines the width
    packing_width = (10 - 1) * CIRCLE_DIAMETER + CIRCLE_DIAMETER # 10.0
    
    num_circles_long_row = 10
    num_circles_short_row = 9
    
    for i in range(num_rows):
        is_long_row = (i % 2 == 0)
        current_num_circles = num_circles_long_row if is_long_row else num_circles_short_row
        y_center = i * row_height + CIRCLE_RADIUS
        
        for j in range(current_num_circles):
            x_center = j * CIRCLE_DIAMETER + CIRCLE_RADIUS
            if not is_long_row:
                x_center += CIRCLE_RADIUS
            coords.append((x_center, y_center))
            
    # Returns coords, packing_width, packing_height
    return np.array(coords), packing_width, packing_height

def load_coords_106_circles():
    """
    Loads the 106-circle optimal solution from a text file and adjusts
    coordinates to start from (0,0) and then determines the actual packing size.
    """
    
    if not os.path.exists(COORDS_106_FILE):
        st.error(f"Data file not found: {COORDS_106_FILE}")
        st.info(f"Please download the file from http://www.packomania.com/txt/csq106.txt and save it as 'data/coords_106.txt'.")
        return np.array([]), 0, 0

    if os.path.getsize(COORDS_106_FILE) == 0:
        st.error(f"Data file is empty: {COORDS_106_FILE}")
        return np.array([]), 0, 0
        
    try:
        raw_coords = np.loadtxt(COORDS_106_FILE, ndmin=2, usecols=(1, 2))
    except Exception as e:
        st.error(f"Error loading data file {COORDS_106_FILE}: {e}")
        st.error("This often means the file is corrupted. Please re-download it.")
        return np.array([]), 0, 0

    if raw_coords.shape[1] != 2:
         st.error(f"Data file {COORDS_106_FILE} is not in the correct (X, Y) format.")
         return np.array([]), 0, 0

    if len(raw_coords) != 106:
        st.warning(f"Warning: {COORDS_106_FILE} was expected to have 106 lines, but has {len(raw_coords)}.")
    
    # Adjust coordinates to start from (0,0) at the edge
    min_x = np.min(raw_coords[:, 0])
    min_y = np.min(raw_coords[:, 1])
    adjusted_coords = raw_coords.copy()
    adjusted_coords[:, 0] -= (min_x - CIRCLE_RADIUS)
    adjusted_coords[:, 1] -= (min_y - CIRCLE_RADIUS)

    # Calculate actual packing dimensions
    packing_width = np.max(adjusted_coords[:, 0]) + CIRCLE_RADIUS
    packing_height = np.max(adjusted_coords[:, 1]) + CIRCLE_RADIUS
    
    # Returns coords, packing_width, packing_height
    return adjusted_coords, packing_width, packing_height

# --- Plotting Function ---

def plot_circles(coords, packing_width, packing_height, title):
    """Uses Matplotlib to draw the circles in the square."""
    
    # --- VISUAL TWEAK 1: Smaller figure size ---
    fig, ax = plt.subplots(figsize=(4, 4)) 

    # Calculate offset for X and Y to center the packing
    offset_x = (SQUARE_SIDE - packing_width) / 2.0
    offset_y = (SQUARE_SIDE - packing_height) / 2.0

    # 1. Draw the outer 10x10 square
    square_outer = patches.Rectangle(
        (0, 0),
        SQUARE_SIDE,
        SQUARE_SIDE,
        fill=False,
        edgecolor='darkred',
        linewidth=2.5,
        label='10x10 Target Square'
    )
    ax.add_patch(square_outer)

    # 2. Draw the inner (minimal) bounding box
    # --- VISUAL TWEAK 2: Correct label and dimensions ---
    label_text = f'Packing Box ({packing_width:.2f} x {packing_height:.2f})'
    
    # Only draw the inner box if it's not identical to the outer one
    if not np.isclose(packing_width, SQUARE_SIDE) or not np.isclose(packing_height, SQUARE_SIDE):
        square_inner = patches.Rectangle(
            (offset_x, offset_y), # Use separate X/Y offsets
            packing_width,       # Use packing width
            packing_height,      # Use packing height
            fill=False,
            edgecolor='navy',
            linestyle='--',
            linewidth=1.5,
            label=label_text
        )
        ax.add_patch(square_inner)

    # 3. Draw all the circles
    for (x, y) in coords:
        circle = patches.Circle(
            (x + offset_x, y + offset_y),  # Apply X and Y offsets
            CIRCLE_RADIUS,
            facecolor='cornflowerblue', 
            edgecolor='black',
            alpha=0.7
        )
        ax.add_patch(circle)

    # --- Final plot adjustments ---
    ax.set_aspect('equal')
    ax.set_xlim(0, SQUARE_SIDE)
    ax.set_ylim(0, SQUARE_SIDE)
    ax.set_title(title, fontsize=16)
    ax.legend(loc='lower right')
    plt.grid(True, linestyle=':', alpha=0.5)
    
    st.pyplot(fig)

# --- Streamlit App UI ---

st.set_page_config(
    page_title="Circle Packing Visualizer",
    page_icon="🔵",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("🔵 Circle Packing Visualizer")
st.markdown("How many coins (Diameter=1) can fit in a 10x10 square? This app visualizes different packing solutions.")
st.markdown("---")

st.sidebar.header("Controls")
option = st.sidebar.radio(
    "Select a packing solution:",
    (
        'Default (Empty Square)',
        '100 Circles (Grid Layout)', 
        '105 Circles (Hexagonal Layout)', 
        '106 Circles (Optimal Solution)'
    )
)

# --- Main Page Logic ---
coords = np.array([])
packing_width = 0.0
packing_height = 0.0
num_circles = 0
plot_title = ""
explanation = ""

if option == 'Default (Empty Square)':
    # Show empty square with a single circle as reference
    coords = np.array([[5.0, 5.0]])  # Single circle in center
    packing_width = CIRCLE_DIAMETER
    packing_height = CIRCLE_DIAMETER
    num_circles = 1
    plot_title = "Empty 10x10 Square with Reference Circle (D=1)"
    explanation = """
    זהו **ריבוע ריק בגודל 10×10** עם **מטבע בודד** (קוטר=1) כנקודת התייחסות.
    * **מטרה:** למקסם את מספר המטבעות שניתן להכניס לריבוע.
    * **מידות המטבע:** קוטר = 1, רדיוס = 0.5
    * **מידות הריבוע:** 10×10
    
    בחר אחת מהאפשרויות בתפריט כדי לראות פתרונות שונים לארגון המטבעות.
    """

elif option == '100 Circles (Grid Layout)':
    coords, packing_width, packing_height = generate_coords_100_circles()
    num_circles = 100
    plot_title = f"{num_circles} Circles (D=1) in 10x10 Square (Simple Grid)"
    explanation = """
    This is the most intuitive solution. A simple **10x10 grid** places 100 circles perfectly.
    * **Efficiency:** This packing fills 100% of the square's width and height.
    * **Space Usage:** The area covered by circles is $100 \times \pi \times (0.5)^2 \approx 78.54$.
    """

elif option == '105 Circles (Hexagonal Layout)':
    coords, packing_width, packing_height = generate_coords_105_circles()
    num_circles = 105
    plot_title = f"{num_circles} Circles (D=1) in 10x10 Square (Hexagonal)"
    explanation = f"""
    This solution uses a **hexagonal (or 'honeycomb') layout**, which is generally denser than a grid.
    * **Arrangement:** It fits 11 rows. 6 rows contain 10 circles, and 5 rows contain 9 circles (total $60 + 45 = 105$).
    * **Efficiency:** The blue dashed line shows the bounding box for this packing, which has a width of **{packing_width:.2f}** and a height of **{packing_height:.2f}**.
    """

elif option == '106 Circles (Optimal Solution)':
    coords, packing_width, packing_height = load_coords_106_circles()
    num_circles = len(coords)
    if num_circles > 0: 
        plot_title = f"{num_circles} Circles (D=1) in 10x10 Square (Optimal)"
        explanation = f"""
        This is the **known optimal solution** (for {num_circles} circles). It was found using computational optimization algorithms.
        * **Arrangement:** The pattern is irregular. It "squeezes" an extra circle in by taking advantage of the small empty spaces.
        * **Dimensions:** The minimal bounding box for this solution is **{packing_width:.2f} x {packing_height:.2f}**.
        * **Source:** The coordinates are from [Packomania.com](http://www.packomania.com).
        """
    else:
        plot_title = "Error Loading 106 Circles Data"

# --- Display the plot and explanations ---

if len(coords) > 0:
    st.subheader(f"Displaying: {num_circles} Circles")
    
    plot_circles(coords, packing_width, packing_height, plot_title)
    
    with st.expander("About This Solution", expanded=True):
        st.markdown(explanation)
    
    st.info("""
    **Key:**
    * **Red Box:** The 10x10 target square.
    * **Blue Dashed Box:** The minimal **bounding box (Width x Height)** for the packing.
    """)
else:
    st.warning("Could not display the selected solution. Please check the error messages above.")
