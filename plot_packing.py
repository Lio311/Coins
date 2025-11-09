import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import sys

# --- הגדרות ---
SQUARE_SIDE = 10.0  # צלע הריבוע שלך
CIRCLE_DIAMETER = 1.0
CIRCLE_RADIUS = CIRCLE_DIAMETER / 2.0
DATA_FILE = "coords.txt"

# גודל הריבוע המינימלי שמכיל את הפתרון של 106 עיגולים (לפי המחקר)
# זה חשוב כדי למרכז את הציור בריבוע ה-10x10
SOLUTION_SIDE_MINIMAL = 9.697932828

# --- טעינת הנתונים ---
try:
    # טעינת הקואורדינטות מקובץ הטקסט
    # הנתונים בקובץ מותאמים לרדיוס 0.5
    coordinates = np.loadtxt(DATA_FILE)
    if len(coordinates) != 106:
        print(f"שגיאה: הקובץ {DATA_FILE} צריך להכיל 106 שורות, אך מכיל {len(coordinates)}")
        sys.exit()
except IOError:
    print(f"שגיאה: לא נמצא הקובץ {DATA_FILE}.")
    print(f"אנא הורד את הנתונים מ-http://www.packomania.com/txt/csq106.txt")
    print(f"ושמור אותם באותה תיקייה בשם {DATA_FILE}")
    sys.exit()

# --- הכנת הציור ---
fig, ax = plt.subplots(figsize=(10, 10))

# חישוב היסט (offset) כדי למרכז את הפתרון (9.7x9.7) בתוך הריבוע (10x10)
offset = (SQUARE_SIDE - SOLUTION_SIDE_MINIMAL) / 2.0

# 1. צייר את הריבוע החיצוני (10x10)
square_outer = patches.Rectangle(
    (0, 0), 
    SQUARE_SIDE, 
    SQUARE_SIDE, 
    fill=False, 
    edgecolor='red', 
    linewidth=2,
    label='Square (10x10)'
)
ax.add_patch(square_outer)

# 2. צייר את הריבוע הפנימי (המינימלי)
square_inner = patches.Rectangle(
    (offset, offset), 
    SOLUTION_SIDE_MINIMAL, 
    SOLUTION_SIDE_MINIMAL, 
    fill=False, 
    edgecolor='blue', 
    linestyle='--',
    linewidth=1,
    label=f'Minimal Square (~{SOLUTION_SIDE_MINIMAL:.3f})'
)
ax.add_patch(square_inner)


# 3. צייר את כל 106 המטבעות
for (x, y) in coordinates:
    # הוסף את ההיסט כדי למרכז את המטבעות
    circle = patches.Circle(
        (x + offset, y + offset), 
        CIRCLE_RADIUS, 
        facecolor='skyblue', 
        edgecolor='black',
        alpha=0.8
    )
    ax.add_patch(circle)

# --- הגדרות תצוגה ---
ax.set_aspect('equal')  # קריטי כדי שעיגולים ייראו עגולים
ax.set_xlim(0, SQUARE_SIDE)
ax.set_ylim(0, SQUARE_SIDE)
ax.set_title(f"Visualizing the Optimal Packing of {len(coordinates)} Circles (D=1) in a 10x10 Square")
ax.legend()
plt.grid(True, linestyle=':', alpha=0.5)
plt.show()
