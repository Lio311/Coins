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

# The side of the minimal bounding box for the 106-circle solution
# This is known from the packing research.
# We will use this as a reference, but also dynamically calculate from loaded coords.
SOLUTION_SIDE_106_REFERENCE = 9.697932828

# --- Coordinate Generation Functions ---

def generate_coords_100_circles():
    """Generates coordinates for a simple 10x10 grid."""
    coords = []
    for row in range(10):
        for col in range(10):
            # Circle center
            x = col * CIRCLE_DIAMETER + CIRCLE_RADIUS
            y = row * CIRCLE_DIAMETER + CIRCLE_RADIUS
            coords.append((x, y))
    # This packing perfectly fills the 10x10 square
    return np.array(coords), SQUARE_SIDE

def generate_coords_105_circles():
    """Generates coordinates for a hexagonal (honeycomb) packing of 105 circles."""
    coords = []
    
    # Height of one row in a hexagonal packing (sqrt(3)/2 * diameter)
    row_height = np.sqrt(3) / 2 * CIRCLE_DIAMETER  # Approx 0.866
    
    num_rows = 11  # 11 rows fit inside the 10.0 height
    
    # Calculate the total height of this packing
    total_packing_height = (num_rows - 1) * row_height + CIRCLE_DIAMETER
    
    num_circles_long_row = 10
    num_circles_short_row = 9
    
    for i in range(num_rows):
        is_long_row = (i % 2 == 0)  # Rows 0, 2, 4... are "long"
        
        current_num_circles = num_circles_long_row if is_long_row else num_circles_short_row
        
        # Y center for this row
        y_center = i * row_height + CIRCLE_RADIUS
        
        for j in range(current_num_circles):
            x_center = j * CIRCLE_DIAMETER + CIRCLE_RADIUS
            
            # If it's a "short" row, offset it by half a radius
            if not is_long_row:
                x_center += CIRCLE_RADIUS
            
            coords.append((x_center, y_center))
            
    return np.array(coords), total_packing_height

def load_coords_106_circles():
    """
    Loads the 106-circle optimal solution from a text file and adjusts
    coordinates to start from (0,0) and then determines the actual packing size.
    """
    
    # Check if file exists
    if not os.path.exists(COORDS_106_FILE):
        st.error(f"Data file not found: {COORDS_106_FILE}")
        st.info(f"Please download the file from http://www.packomania.com/txt/csq106.txt and save it as 'data/coords_106.txt' in your project directory.")
        return np.array([]), 0

    # Check if file is empty (causes loadtxt error)
    if os.path.getsize(COORDS_106_FILE) == 0:
        st.error(f"Data file is empty: {COORDS_106_FILE}")
        return np.array([]), 0
        
    try:
        # ndmin=2 ensures a 2D array
        # usecols=(1, 2) skips the first (index) column and reads only X and Y
        raw_coords = np.loadtxt(COORDS_106_FILE, ndmin=2, usecols=(1, 2))
        
    except Exception as e:
        st.error(f"Error loading data file {COORDS_106_FILE}: {e}")
        st.error("This often means the file is corrupted with broken lines or incorrect format. Please re-download it from packomania.com and ensure it's saved correctly.")
        return np.array([]), 0

    # Validate data shape (should be N rows, 2 columns)
    if raw_coords.shape[1] != 2:
         st.error(f"Data file {COORDS_106_FILE} is not in the correct (X, Y) format. Expected 2 columns.")
         return np.array([]), 0

    # Just a warning, not a critical error
    if len(raw_coords) != 106:
        st.warning(f"Warning: {COORDS_106_FILE} was expected to have 106 lines, but has {len(raw_coords)}.")
    
    # --- Crucial adjustment for visualization ---
    # Find the minimum X and Y values
    min_x = np.min(raw_coords[:, 0])
    min_y = np.min(raw_coords[:, 1])

    # Adjust all coordinates so the bottom-leftmost circle's edge is at (0,0)
    # The packomania data often has negative coordinates or starts elsewhere.
    adjusted_coords = raw_coords.copy()
    adjusted_coords[:, 0] -= (min_x - CIRCLE_RADIUS) # Adjust X so min_x - R = 0
    adjusted_coords[:, 1] -= (min_y - CIRCLE_RADIUS) # Adjust Y so min_y - R = 0

    # Calculate the actual required packing size based on adjusted coordinates
    # Max X/Y plus radius for the rightmost/topmost circle
    packing_width = np.max(adjusted_coords[:, 0]) + CIRCLE_RADIUS
    packing_height = np.max(adjusted_coords[:, 1]) + CIRCLE_RADIUS

    # We use the larger of the two to define the square packing_side
    packing_side_actual = max(packing_width, packing_height)

    # For the 106 solution, we know the theoretical minimal side is SOLUTION_SIDE_106_REFERENCE
    # We can use that if the calculated one is slightly off due to float precision or if it's smaller.
    # It's usually safe to just use the calculated one if it's robust.
    # For now, let's use the actual calculated one for better fit.
    
    return adjusted_coords, packing_side_actual

# --- Plotting Function ---

def plot_circles(coords, packing_side, title):
    """Uses Matplotlib to draw the circles in the square."""
    fig, ax = plt.subplots(figsize=(8, 8)) # Good size for Streamlit. Reduced from 10x10 for smaller image.

    # Calculate offset to center the packing inside the 10x10 square
    # Ensure packing_side doesn't exceed SQUARE_SIDE to prevent negative offset
    actual_packing_dim = min(packing_side, SQUARE_SIDE) 
    offset = (SQUARE_SIDE - actual_packing_dim) / 2.0

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
    if actual_packing_dim < SQUARE_SIDE:
        square_inner = patches.Rectangle(
            (offset, offset),
            actual_packing_dim,
            actual_packing_dim,
            fill=False,
            edgecolor='navy',
            linestyle='--',
            linewidth=1.5,
            label=f'Actual Packed Area (~{actual_packing_dim:.3f})'
        )
        ax.add_patch(square_inner)

    # 3. Draw all the circles
    for (x, y) in coords:
        circle = patches.Circle(
            (x + offset, y + offset),  # Apply offset to center the circle
            CIRCLE_RADIUS,
            facecolor='cornflowerblue', # A nice blue
            edgecolor='black',
            alpha=0.7
        )
        ax.add_patch(circle)

    # --- Final plot adjustments ---
    ax.set_aspect('equal') # Ensures circles are not squashed
    ax.set_xlim(0, SQUARE_SIDE)
    ax.set_ylim(0, SQUARE_SIDE)
    ax.set_title(title, fontsize=16)
    ax.legend(loc='lower right')
    plt.grid(True, linestyle=':', alpha=0.5)
    
    st.pyplot(fig) # Display the plot in Streamlit

# --- Streamlit App UI ---

# Set page config for a cleaner look
st.set_page_config(
    page_title="Circle Packing Visualizer",
    page_icon="🔵", # Visual flair
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("🔵 Circle Packing Visualizer")
st.markdown("How many coins (Diameter=1) can fit in a 10x10 square? This app visualizes different packing solutions.")
st.markdown("---") # Horizontal line

# --- Sidebar for selection ---
st.sidebar.header("Controls")
option = st.sidebar.radio(
    "Select a packing solution:",
    (
        '100 Circles (Grid Layout)', 
        '105 Circles (Hexagonal Layout)', 
        '106 Circles (Optimal Solution)'
    )
)

# --- Main Page Logic ---
coords = np.array([])
packing_side = SQUARE_SIDE
num_circles = 0
plot_title = ""
explanation = ""

if option == '100 Circles (Grid Layout)':
    coords, packing_side = generate_coords_100_circles()
    num_circles = 100
    plot_title = f"{num_circles} Circles (D=1) in 10x10 Square (Simple Grid)"
    explanation = """
    This is the most intuitive solution. A simple **10x10 grid** places 100 circles perfectly.
    * **Efficiency:** This packing fills 100% of the square's width and height.
    * **Space Usage:** The area covered by circles is $100 \times \pi \times (0.5)^2 \approx 78.54$. This is the baseline density.
    """

elif option == '105 Circles (Hexagonal Layout)':
    coords, packing_side = generate_coords_105_circles()
    num_circles = 105
    plot_title = f"{num_circles} Circles (D=1) in 10x10 Square (Hexagonal)"
    explanation = """
    This solution uses a **hexagonal (or 'honeycomb') layout**, which is generally denser than a grid.
    * **Arrangement:** It fits 11 rows. 6 rows contain 10 circles, and 5 rows contain 9 circles (total $60 + 45 = 105$).
    * **Efficiency:** As you can see from the blue dashed line, this packing doesn't use the full 10.0 height (it uses ~9.66), but its higher density allows 5 extra circles to be added.
    """

elif option == '106 Circles (Optimal Solution)':
    coords, packing_side = load_coords_106_circles()
    num_circles = len(coords) # Will be 106 if file loaded, 0 if error
    if num_circles > 0: # Check if loading was successful
        plot_title = f"{num_circles} Circles (D=1) in 10x10 Square (Optimal)"
        explanation = f"""
        This is the **known optimal solution** (for {num_circles} circles). It was found using computational optimization algorithms and is not intuitive.
        * **Arrangement:** The pattern is irregular. It "squeezes" an extra circle in by taking advantage of the small empty spaces left by the 105-circle hexagonal layout.
        * **Source:** The coordinates are from [Packomania.com](http://www.packomania.com), a database of optimal packing solutions.
        """
    else:
        plot_title = "Error Loading 106 Circles Data"

# --- Display the plot and explanations ---

if len(coords) > 0:
    st.subheader(f"Displaying: {num_circles} Circles")
    
    # Show the plot
    plot_circles(coords, packing_side, plot_title)
    
    # Show the explanation for the selected option
    with st.expander("About This Solution", expanded=True):
        st.markdown(explanation)
    
    # Show the key
    st.info("""
    **Key:**
    * **Red Box:** The 10x10 target square.
    * **Blue Dashed Box:** The minimal area required for the packing. This visually indicates how tightly the circles fit within the square.
    """)
else:
    # This shows if the 106-file load failed
    st.warning("Could not display the selected solution. Please check the error messages above.")
