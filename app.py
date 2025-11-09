import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

# --- הגדרות קבועות ---
SQUARE_SIDE = 10.0  # צלע הריבוע
CIRCLE_DIAMETER = 1.0
CIRCLE_RADIUS = CIRCLE_DIAMETER / 2.0
DATA_DIR = "data"
COORDS_106_FILE = os.path.join(DATA_DIR, "coords_106.txt")

# גודל הריבוע המינימלי שמכיל את הפתרון של 106 עיגולים (לפי המחקר)
SOLUTION_SIDE_106_MINIMAL = 9.697932828

# --- פונקציות ליצירת קואורדינטות ---

def generate_coords_100_circles():
    """יוצר קואורדינטות לסידור 10x10 של 100 מטבעות."""
    coords = []
    for row in range(10):
        for col in range(10):
            # מרכז המעגל
            x = col * CIRCLE_DIAMETER + CIRCLE_RADIUS
            y = row * CIRCLE_DIAMETER + CIRCLE_RADIUS
            coords.append((x, y))
    return np.array(coords), SQUARE_SIDE # 100% ניצול גובה/רוחב

def generate_coords_105_circles():
    """יוצר קואורדינטות לסידור משושה (כוורת) של 105 מטבעות."""
    coords = []
    
    # גובה שורה אחת בסידור משושה (sqrt(3)/2 * קוטר)
    # 0.86602540378 * 1 = 0.86602540378
    row_height = np.sqrt(3) / 2 * CIRCLE_DIAMETER 
    
    num_rows = 11 # כפי שחישבנו, 11 שורות נכנסות בריבוע 10x10
    
    # חישוב הגובה הכולל של הסידור
    total_packing_height = (num_rows - 1) * row_height + CIRCLE_DIAMETER
    
    # מספר מטבעות בשורות לסירוגין
    num_circles_even_row = 10 # 10 מטבעות
    num_circles_odd_row = 9  # 9 מטבעות
    
    for i in range(num_rows):
        is_even_row = (i % 2 == 0) # שורות 0, 2, 4... הן שורות "ארוכות"
        
        current_num_circles = num_circles_even_row if is_even_row else num_circles_odd_row
        
        # מרכז y של השורה
        y_center = i * row_height + CIRCLE_RADIUS
        
        for j in range(current_num_circles):
            x_center = j * CIRCLE_DIAMETER + CIRCLE_RADIUS
            
            # אם זו שורה "אי-זוגית" (קצרה), צריך להזיז אותה חצי קוטר
            if not is_even_row:
                x_center += CIRCLE_RADIUS
            
            coords.append((x_center, y_center))
            
    return np.array(coords), total_packing_height

def load_coords_106_circles():
    """טוען קואורדינטות ל-106 מטבעות מקובץ."""
    if not os.path.exists(COORDS_106_FILE):
        st.error(f"קובץ הקואורדינטות ל-106 מטבעות לא נמצא: {COORDS_106_FILE}")
        st.info("אנא וודא שהורדת את הקובץ מ-http://www.packomania.com/txt/csq106.txt ושמרת אותו בתיקייה data/ בשם coords_106.txt")
        return np.array([]), 0
    
    coords = np.loadtxt(COORDS_106_FILE)
    if len(coords) != 106:
        st.warning(f"קובץ {COORDS_106_FILE} צפוי להכיל 106 שורות, אך מכיל {len(coords)}.")
    
    return coords, SOLUTION_SIDE_106_MINIMAL

# --- פונקציית ציור ---

def plot_circles(coords, packing_side, title):
    """מציירת את המטבעות בתוך הריבוע."""
    fig, ax = plt.subplots(figsize=(8, 8)) # גודל fig מספיק ל-Streamlit

    # חישוב היסט כדי למרכז את הסידור בריבוע ה-10x10
    offset = (SQUARE_SIDE - packing_side) / 2.0

    # צייר את הריבוע החיצוני (10x10)
    square_outer = patches.Rectangle(
        (0, 0),
        SQUARE_SIDE,
        SQUARE_SIDE,
        fill=False,
        edgecolor='red',
        linewidth=2,
        label='10x10 Square'
    )
    ax.add_patch(square_outer)

    # צייר את הריבוע הפנימי (אזור האריזה בפועל)
    if packing_side < SQUARE_SIDE:
        square_inner = patches.Rectangle(
            (offset, offset),
            packing_side,
            packing_side,
            fill=False,
            edgecolor='blue',
            linestyle='--',
            linewidth=1,
            label=f'Packed Area (~{packing_side:.3f})'
        )
        ax.add_patch(square_inner)

    # צייר את כל המטבעות
    for (x, y) in coords:
        circle = patches.Circle(
            (x + offset, y + offset),
            CIRCLE_RADIUS,
            facecolor='skyblue',
            edgecolor='black',
            alpha=0.8
        )
        ax.add_patch(circle)

    ax.set_aspect('equal')
    ax.set_xlim(0, SQUARE_SIDE)
    ax.set_ylim(0, SQUARE_SIDE)
    ax.set_title(title)
    ax.legend(loc='lower right')
    plt.grid(True, linestyle=':', alpha=0.5)
    
    st.pyplot(fig) # הצגת הגרף ב-Streamlit

# --- ממשק Streamlit ---

st.set_page_config(
    page_title="Circle Packing in a Square",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("כמה מטבעות (קוטר 1) בריבוע (10x10)?")
st.markdown("אפליקציה זו מדגימה סידורים שונים של מטבעות עם קוטר 1 בריבוע בגודל 10x10.")
st.markdown(" ") # רווח

option = st.sidebar.radio(
    "בחר את מספר המטבעות להצגה:",
    ('100 מטבעות (סידור רשת)', '105 מטבעות (סידור משושה)', '106 מטבעות (האופטימלי)')
)

coords = np.array([])
packing_side = SQUARE_SIDE
num_circles = 0
plot_title = ""

if option == '100 מטבעות (סידור רשת)':
    coords, packing_side = generate_coords_100_circles()
    num_circles = 100
    plot_title = f"{num_circles} Circles (D=1) in 10x10 Square (Grid)"
elif option == '105 מטבעות (סידור משושה)':
    coords, packing_side = generate_coords_105_circles()
    num_circles = 105
    plot_title = f"{num_circles} Circles (D=1) in 10x10 Square (Hexagonal)"
elif option == '106 מטבעות (האופטימלי)':
    coords, packing_side = load_coords_106_circles()
    num_circles = len(coords) # יעדכן אם קובץ ריק
    if num_circles == 106:
        plot_title = f"{num_circles} Circles (D=1) in 10x10 Square (Optimal)"
    else:
        plot_title = "Error Loading 106 Circles Data"

if len(coords) > 0:
    st.subheader(f"הצגת: {num_circles} מטבעות")
    plot_circles(coords, packing_side, plot_title)
    
    st.markdown("---")
    st.markdown("""
    **הערות:**
    * **ריבוע אדום:** מייצג את הריבוע המקורי בגודל 10x10.
    * **ריבוע כחול מקווקו:** מייצג את השטח המינימלי הנדרש לאריזה בפועל של המטבעות בסידור נתון.
        * עבור 100 מטבעות, זה בדיוק 10x10.
        * עבור 105 ו-106, השטח קטן מעט מ-10x10, מה שמשאיר מעט 'ריפוד' בקצוות, אבל המטבעות נמצאים בתוך הריבוע האדום.
    """)
else:
    st.warning("לא ניתן להציג סידור. אנא בדוק את שגיאות הקונסול או את קובץ הנתונים.")
