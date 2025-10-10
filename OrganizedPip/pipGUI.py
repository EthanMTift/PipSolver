import sys
import cv2
from PyQt5.QtWidgets import (
    QApplication, QDialog, QFileDialog, QWidget, QVBoxLayout, QLineEdit, QLabel, QPushButton, QGridLayout, QInputDialog
)
from PyQt5.QtGui import QColor, QBrush, QPainter
from PyQt5.QtCore import Qt
import random
import time
import os
from pipSetInvalid import set_invalid
from pipCreateGrid import create_grid
from pipDominoSolver import solve_domino
from pipCountDigits import countDigits
from pipBadNumPicker import badNumPicker
from pipSelectImage import select_file_qt
from pipAlign import align
from pipGroup import make_groups
from pipDominoExtract import domino_extract
from pipDetectDominos import detect_dominos
import shutil
import json

DOT_RADIUS = 5

DOT_POSITIONS = {
    1: [(0.5, 0.5)],
    2: [(0.25, 0.25), (0.75, 0.75)],
    3: [(0.25, 0.25), (0.5, 0.5), (0.75, 0.75)],
    4: [(0.25, 0.25), (0.25, 0.75), (0.75, 0.25), (0.75, 0.75)],
    5: [(0.25, 0.25), (0.25, 0.75), (0.5, 0.5), (0.75, 0.25), (0.75, 0.75)],
    6: [(0.25, 0.25), (0.25, 0.5), (0.25, 0.75), (0.75, 0.25), (0.75, 0.5), (0.75, 0.75)]
}

OUT_PATH = "grid_overlay.png"
JSON_PATH = "grid_overlay.json"
DOMINO_JSON_PATH = "domino_area.json"

# ------------------- TileWidget -------------------
class TileWidget(QWidget):
    def __init__(self, cell, size=50):
        super().__init__()
        self.cell = cell
        self.setFixedSize(size, size)
        self.bg_color = "#FFFDD0" if self.cell["valid"] else "white"

    def set_bg_color(self, color):
        self.bg_color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        size = min(self.width(), self.height())

        painter.fillRect(0, 0, size, size, QColor(self.bg_color))

        # Draw domino dots if value is set and >0
        if self.cell["value"] is not None and self.cell["value"] > 0 and self.cell["valid"]:
            painter.setBrush(QBrush(Qt.black))
            painter.setPen(Qt.NoPen)
            value = self.cell["value"]
            positions = DOT_POSITIONS.get(value, [(0.5, 0.5)])
            for px, py in positions:
                cx = int(px * size)
                cy = int(py * size)
                painter.drawEllipse(cx - DOT_RADIUS, cy - DOT_RADIUS, DOT_RADIUS*2, DOT_RADIUS*2)

        # Draw border only if valid
        if self.cell["valid"]:
            painter.setBrush(Qt.NoBrush)
            painter.setPen(Qt.black)
            painter.drawRect(0, 0, size-1, size-1)

class GridSizeDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enter Grid Dimensions")
        self.rows = 0
        self.cols = 0

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Enter grid dimensions (rows columns):"))

        self.input_field = QLineEdit()
        self.input_field.returnPressed.connect(self.set_dimensions)
        layout.addWidget(self.input_field)

        self.feedback_label = QLabel("")
        layout.addWidget(self.feedback_label)
        self.setLayout(layout)

    def set_dimensions(self):
        text = self.input_field.text().strip()
        try:
            r, c = map(int, text.split())
            if r <= 0 or c <= 0:
                raise ValueError
            self.rows = r
            self.cols = c
            self.accept()
        except ValueError:
            self.feedback_label.setText("Invalid input! Enter two positive integers.")

    def closeEvent(self, event):
        os._exit(0)


# ------------------- SolverViewer -------------------
class SolverViewer(QDialog):
    def __init__(self, grid, img_path=None):
        super().__init__()
        self.setWindowTitle("Solver Viewer")
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0
        self.img_path = img_path

        self.setStyleSheet("background-color: white;")
        self.main_layout = QVBoxLayout()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(0)
        self.main_layout.addLayout(self.grid_layout)

        # Solve (Visual) button
        self.solve_button = QPushButton("Solve (Visual)")
        self.solve_button.setMinimumHeight(40)
        self.solve_button.setStyleSheet("font-weight: bold; font-size: 16px; color: black;")
        self.solve_button.clicked.connect(self.start_solve)
        self.main_layout.addWidget(self.solve_button)

        # Solve (Final Only) button
        self.solve_final_button = QPushButton("Solve (Final Only)")
        self.solve_final_button.setMinimumHeight(40)
        self.solve_final_button.setStyleSheet("font-weight: bold; font-size: 16px; color: black;")
        self.solve_final_button.clicked.connect(self.start_solve_final)
        self.main_layout.addWidget(self.solve_final_button)

        # Solve (solution_path) button
        self.solve_replay_button = QPushButton("Solve (Replay)")
        self.solve_replay_button.setMinimumHeight(40)
        self.solve_replay_button.setStyleSheet("font-weight: bold; font-size: 16px; color: black;")
        self.solve_replay_button.clicked.connect(self.start_solve_replay)
        self.main_layout.addWidget(self.solve_replay_button)

        # --- Save Setup button ---
        self.save_button = QPushButton("Save Setup")
        self.save_button.setMinimumHeight(40)
        self.save_button.setStyleSheet("font-weight: bold; font-size: 16px; color: black;")
        self.save_button.clicked.connect(self.save_setup)
        self.main_layout.addWidget(self.save_button)

        self.setLayout(self.main_layout)

        
        # Compute tile size and window dimensions
        screen_rect = QApplication.primaryScreen().availableGeometry()
        max_width = screen_rect.width() * 0.9
        max_height = screen_rect.height() * 0.9

        num_buttons = 4  # Solve Visual, Solve Final, Solve Replay, Save Setup
        button_height = 40
        button_spacing = 10
        reserved_height = num_buttons * button_height + (num_buttons - 1) * button_spacing

        available_height = max_height - reserved_height

        tile_width = max_width / self.cols
        tile_height = available_height / self.rows
        self.tile_size = int(min(tile_width, tile_height))

        # Set fixed size of the dialog
        dialog_width = int(self.tile_size * self.cols)
        dialog_height = int(self.tile_size * self.rows + reserved_height + 20)  # extra padding
        self.setFixedSize(dialog_width, dialog_height)
        

        self.tiles = {}
        for i in range(self.rows):
            for j in range(self.cols):
                tile = TileWidget(self.grid[i][j], size=self.tile_size)
                self.grid_layout.addWidget(tile, i, j)
                self.tiles[(i, j)] = tile

        # Domino highlight color management
        self.domino_colors = self.get_color_pool()
        self.active_domino_colors = {} 

        self.draw_board()

    def get_color_pool(self):
        colors = [
            "#FF0000", "#00FF00", "#0000FF", "#FF00FF", "#00FFFF", "#800000", "#008000",
            "#000080", "#808000", "#800080", "#008080", "#C0C0C0", "#FFA500", "#A52A2A",
            "#FFC0CB", "#ADD8E6", "#90EE90", "#D3D3D3", "#FFA07A", "#20B2AA",
            "#87CEFA", "#778899", "#B0C4DE", "#FF1493"
        ]
        return colors

    def draw_board(self):
        for i in range(self.rows):
            for j in range(self.cols):
                self.tiles[(i, j)].update()
        QApplication.processEvents()

    def show_original_image(self):
        if not self.img_path or not os.path.exists(self.img_path):
            print("Original image not found.")
            return

        from PyQt5.QtWidgets import QLabel, QScrollArea
        from PyQt5.QtGui import QPixmap

        dialog = QDialog(self)
        dialog.setWindowTitle("Original Board Image")
        layout = QVBoxLayout(dialog)

        scroll = QScrollArea(dialog)
        layout.addWidget(scroll)

        label = QLabel()
        pixmap = QPixmap(self.img_path)
        label.setPixmap(pixmap)
        label.setScaledContents(True)
        scroll.setWidget(label)
        scroll.setWidgetResizable(True)

        dialog.resize(min(pixmap.width(), 800), min(pixmap.height(), 600))
        dialog.exec_()
  

    # Visual solve
    def start_solve(self):
        normalized_dominos = set((min(a, b), max(a, b)) for a, b in dominos)
        solution_path = []
        solve_domino(self.grid, normalized_dominos, groups, self, solve_visual=True, solution_path=solution_path)
        self.show_original_image()

    # Non-visual / final-only solve
    def start_solve_final(self):
        normalized_dominos = set((min(a, b), max(a, b)) for a, b in dominos)
        solution_path = []
        solve_domino(self.grid, normalized_dominos, groups, self, solve_visual=False, solution_path=solution_path)
        self.draw_board()
        self.show_original_image()
    # Solution path solve
    def start_solve_replay(self):
        normalized_dominos = set((min(a, b), max(a, b)) for a, b in dominos)
        solution_path = []
        solved = solve_domino(self.grid, normalized_dominos, groups, self, solve_visual=False, solution_path=solution_path)

        if not solved:
            print("No solution found")
            return

        # Clear the grid 
        for row in self.grid:
            for cell in row:
                cell["value"] = None

        self.active_domino_colors.clear()
        self.domino_colors = self.get_color_pool()
        self.draw_board()

        # Replay solution path step by step
        for (r1, c1, v1), (r2, c2, v2) in solution_path:
            self.grid[r1][c1]["value"] = v1
            self.grid[r2][c2]["value"] = v2
            self.highlight_domino((r1, c1), (r2, c2))
            self.draw_board()
            QApplication.processEvents()
            time.sleep(1)  
        
        self.show_original_image()


    def highlight_domino(self, coord1, coord2):
        domino_key = frozenset([coord1, coord2])
        if domino_key in self.active_domino_colors:
            color = self.active_domino_colors[domino_key]
        else:
            if self.domino_colors:
                color = self.domino_colors.pop(0)
            else:
                color = "#FF00FF"
            self.active_domino_colors[domino_key] = color

        for coord in [coord1, coord2]:
            self.tiles[coord].set_bg_color(color)

    def clear_domino_highlight(self, coord1, coord2):
        domino_key = frozenset([coord1, coord2])
        if domino_key in self.active_domino_colors:
            color = self.active_domino_colors.pop(domino_key)
            self.domino_colors.append(color)
        for coord in [coord1, coord2]:
            cell = self.grid[coord[0]][coord[1]]
            self.tiles[coord].set_bg_color("#FFFDD0" if cell["valid"] else "white")

    # --- Save Setup ---
    def save_setup(self):
        import shutil
        from datetime import datetime

        # Extract date from filename
        filename = os.path.basename(self.img_path)
        try:
            date_str = filename.split("Screenshot ")[1].split(" at")[0]
        except IndexError:
            date_str = datetime.now().strftime("%Y-%m-%d")

        folder_path = os.path.join("saved_setups", date_str)
        os.makedirs(folder_path, exist_ok=True)

        shutil.copy(self.img_path, folder_path)
        shutil.copy(JSON_PATH, folder_path)
        shutil.copy(DOMINO_JSON_PATH, folder_path)

        print(f"Setup saved to {folder_path}")

    def closeEvent(self, event):
        os._exit(0)


# ------------------- Main -------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # --- Ask user whether to load from folder or select image ---
    use_saved, ok = QInputDialog.getItem(
        None,
        "Load Mode",
        "Select input mode:",
        ["Select Image", "Load Saved Setup Folder"],
        0,
        False
    )

    if not ok:
        sys.exit(0)

    if use_saved == "Select Image":
        img_path = select_file_qt()
        img = cv2.imread(img_path)

        grid_size_dialog = GridSizeDialog()
        if grid_size_dialog.exec_() == QDialog.Accepted:
            rows, cols = grid_size_dialog.rows, grid_size_dialog.cols
            grid = create_grid(rows, cols)

            dominos_data = align(img, rows, cols, OUT_PATH, DOMINO_JSON_PATH, JSON_PATH, img_path)

    else:  # Load from saved folder
        
        folder_path = QFileDialog.getExistingDirectory(None, "Select Folder with Saved Setup")
        if not folder_path or not os.path.isdir(folder_path):
            print("Invalid folder selected. Exiting.")
            sys.exit(1)
        

        # Load base image
        imgs_in_folder = [f for f in os.listdir(folder_path) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        if not imgs_in_folder:
            print("No image found in folder. Exiting.")
            sys.exit(1)
        img_path = os.path.join(folder_path, imgs_in_folder[0])
        img = cv2.imread(img_path)

        # Load JSON files
        json_file = os.path.join(folder_path, os.path.basename(JSON_PATH))
        domino_json_file = os.path.join(folder_path, os.path.basename(DOMINO_JSON_PATH))
        if not os.path.exists(json_file) or not os.path.exists(domino_json_file):
            print("Required JSON files not found in folder. Exiting.")
            sys.exit(1)

        # Read grid info from JSON
        with open(json_file) as f:
            grid_data = json.load(f)
        rows, cols = grid_data["rows"], grid_data["cols"]
        print(rows)
        print(cols)
        grid = create_grid(rows, cols)

        # Read domino area coordinates from domino JSON
        with open(domino_json_file) as f:
            domino_area = json.load(f)

        # Detect dominos using the loaded image and saved domino area
        tile_w = grid_data["tile_width"]
        tile_h = grid_data["tile_height"]
        dominos_data = detect_dominos(img, domino_area, tile_w, tile_h)

    # --- Continue with normal processing ---
    if use_saved == "Select Image":
        groups, invalids = make_groups(img, JSON_PATH, SYMBOL_CONF_THRESHOLD=50, DEBUG_FOLDER=None)
    else:
        groups, invalids = make_groups(img, json_file, SYMBOL_CONF_THRESHOLD=50, DEBUG_FOLDER=None)
    

    set_invalid(grid, invalids)

    dominos = domino_extract(dominos_data)

    digitDict = countDigits(dominos)

    badNumPicker(grid, groups, digitDict)

    print(grid)
    print(dominos)

    solver_viewer = SolverViewer(grid, img_path)
    solver_viewer.exec_()

    sys.exit(app.exec_())
