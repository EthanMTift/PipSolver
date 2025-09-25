import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QWidget, QVBoxLayout, QLineEdit, QLabel, QPushButton, QGridLayout, QInputDialog
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

DOT_RADIUS = 5

DOT_POSITIONS = {
    1: [(0.5, 0.5)],
    2: [(0.25, 0.25), (0.75, 0.75)],
    3: [(0.25, 0.25), (0.5, 0.5), (0.75, 0.75)],
    4: [(0.25, 0.25), (0.25, 0.75), (0.75, 0.25), (0.75, 0.75)],
    5: [(0.25, 0.25), (0.25, 0.75), (0.5, 0.5), (0.75, 0.25), (0.75, 0.75)],
    6: [(0.25, 0.25), (0.25, 0.5), (0.25, 0.75), (0.75, 0.25), (0.75, 0.5), (0.75, 0.75)]
}

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

# ------------------- DominoDialog -------------------
class DominoDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enter Dominos")
        self.dominos = set()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Enter a domino (two numbers separated by space). Leave empty to finish:"))

        self.input_field = QLineEdit()
        self.input_field.returnPressed.connect(self.add_domino)
        layout.addWidget(self.input_field)

        self.feedback_label = QLabel("")
        layout.addWidget(self.feedback_label)
        self.setLayout(layout)

    def add_domino(self):
        text = self.input_field.text().strip()
        if text == "":
            self.accept()
            return
        try:
            a, b = map(int, text.split())
            self.dominos.add((a, b))
            self.feedback_label.setText(f"Dominos so far: {self.dominos}")
            self.input_field.clear()
        except ValueError:
            self.feedback_label.setText("Invalid input! Enter two numbers separated by a space.")
            self.input_field.clear()
    
    def closeEvent(self, event):
        os._exit(0)

# ------------------- GridSizeDialog -------------------
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

# ------------------- GridEditor -------------------
class GridEditor(QDialog):
    def __init__(self, grid):
        super().__init__()
        self.setWindowTitle("Grid Editor")
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0
        self.toggled_tiles = set()

        self.setStyleSheet("background-color: white;")
        main_layout = QVBoxLayout()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(0)
        main_layout.addLayout(self.grid_layout)

        self.set_grid_button = QPushButton("Set grid")
        self.set_grid_button.setMinimumHeight(40)
        self.set_grid_button.setStyleSheet("font-weight: bold; font-size: 16px; color: black;")
        self.set_grid_button.clicked.connect(self.accept)
        main_layout.addWidget(self.set_grid_button)
        self.setLayout(main_layout)

        # Calculate tile size
        screen_rect = QApplication.primaryScreen().availableGeometry()
        max_width = screen_rect.width() * 0.9
        max_height = screen_rect.height() * 0.9
        tile_width = max_width / self.cols
        tile_height = max_height / self.rows
        tile_size = int(min(tile_width, tile_height))

        self.tiles = {}
        for i in range(self.rows):
            for j in range(self.cols):
                tile = QPushButton()
                tile.setFixedSize(tile_size, tile_size)
                tile.setStyleSheet("background-color: grey; border: 1px solid black;")
                tile.clicked.connect(lambda checked, x=i, y=j: self.toggle_tile(x, y))
                self.grid_layout.addWidget(tile, i, j)
                self.tiles[(i, j)] = tile

    def toggle_tile(self, x, y):
        tile = self.tiles[(x, y)]
        if (x, y) in self.toggled_tiles:
            tile.setStyleSheet("background-color: grey; border: 1px solid black;")
            self.toggled_tiles.remove((x, y))
        else:
            tile.setStyleSheet("background-color: white; border: 0px;")
            self.toggled_tiles.add((x, y))

    def get_toggled_tiles(self):
        return self.toggled_tiles
    
    def closeEvent(self, event):
        os._exit(0)

# ------------------- BoardViewer -------------------
class BoardViewer(QDialog):
    def __init__(self, grid):
        super().__init__()
        self.setWindowTitle("Board Viewer")
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0
        self.setStyleSheet("background-color: white;")
        self.groups = []
        self.group_colors = self.get_color_pool()
        self.current_selection = set()
        self.selection_mode = False

        main_layout = QVBoxLayout()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(0)
        main_layout.addLayout(self.grid_layout)

        self.set_group_button = QPushButton("Set group")
        self.set_group_button.setMinimumHeight(40)
        self.set_group_button.setStyleSheet("font-weight: bold; font-size: 16px; color: black;")
        self.set_group_button.clicked.connect(self.toggle_group_mode)
        main_layout.addWidget(self.set_group_button)

        self.finalize_board_button = QPushButton("Finalize Board")
        self.finalize_board_button.setMinimumHeight(40)
        self.finalize_board_button.setStyleSheet("font-weight: bold; font-size: 16px; color: black;")
        main_layout.addWidget(self.finalize_board_button)
        self.setLayout(main_layout)

        # Tile size
        screen_rect = QApplication.primaryScreen().availableGeometry()
        max_width = screen_rect.width() * 0.9
        max_height = screen_rect.height() * 0.9
        reserved_height = self.set_group_button.minimumHeight() + self.finalize_board_button.minimumHeight() + 20
        available_height = max_height - reserved_height
        tile_width = max_width / self.cols
        tile_height = available_height / self.rows
        self.tile_size = int(min(tile_width, tile_height))

        self.finalized_groups = None
        self.finalize_board_button.clicked.connect(self.finalize_board)

        # Create tiles
        self.tiles = {}
        for i in range(self.rows):
            for j in range(self.cols):
                cell = self.grid[i][j]
                tile = QPushButton()
                tile.setFixedSize(self.tile_size, self.tile_size)
                if not cell["valid"]:
                    tile.setStyleSheet("background-color: white; border: 0px;")
                else:
                    tile.setStyleSheet("background-color: grey; border: 1px solid black;")
                    tile.clicked.connect(lambda checked, x=i, y=j: self.select_tile(x, y))
                self.grid_layout.addWidget(tile, i, j)
                self.tiles[(i, j)] = tile

    # ----- Group logic -----
    def toggle_group_mode(self):
        if not self.selection_mode:
            self.selection_mode = True
            self.set_group_button.setText("Finish group")
        else:
            self.finish_group()
            self.selection_mode = False
            self.set_group_button.setText("Set group")
            self.current_selection.clear()

    def select_tile(self, x, y):
        if not self.selection_mode:
            return
        pos = (x, y)
        for group in self.groups:
            if pos in group["tiles"]:
                return
        tile = self.tiles[pos]
        if pos in self.current_selection:
            tile.setStyleSheet("background-color: grey; border: 1px solid black;")
            self.current_selection.remove(pos)
        else:
            tile.setStyleSheet("background-color: yellow; border: 1px solid black;")
            self.current_selection.add(pos)

    def finish_group(self):
        if not self.current_selection:
            return
        rules = ['sum', '<sum', '>sum', '=', '!=', 'constant', '!constant', '<constant', '>constant']
        dialog = QInputDialog(self)
        dialog.setWindowTitle("Select rule")
        dialog.setLabelText("Rule:")
        dialog.setComboBoxItems(rules)
        dialog.setStyleSheet("color: black;")
        if dialog.exec_() != QInputDialog.Accepted:
            return
        rule = dialog.textValue()

        if rule in ["=", "!="]:
            rule_value = None
        else:
            while True:
                dialog = QInputDialog(self)
                dialog.setWindowTitle("Enter rule value")
                dialog.setLabelText("Rule value (number):")
                dialog.setTextValue("")
                dialog.setStyleSheet("color: black;")
                if dialog.exec_() != QInputDialog.Accepted:
                    return
                value = dialog.textValue()
                try:
                    rule_value = int(value)
                    break
                except ValueError:
                    continue

        group = {
            "tiles": list(self.current_selection),
            "rule": rule,
            "rule_value": rule_value
        }
        self.groups.append(group)
        if self.group_colors:
            color = random.choice(self.group_colors)
            self.group_colors.remove(color)
        else:
            color = "#FF00FF"
        for pos in group["tiles"]:
            self.tiles[pos].setStyleSheet(f"background-color: {color}; border: 1px solid black;")

    def get_color_pool(self):
        colors = [
            "#FF0000", "#00FF00", "#0000FF", "#FF00FF", "#00FFFF", "#800000", "#008000",
            "#000080", "#808000", "#800080", "#008080", "#C0C0C0", "#FFA500", "#A52A2A",
            "#FFC0CB", "#ADD8E6", "#90EE90", "#D3D3D3", "#FFA07A", "#20B2AA",
            "#87CEFA", "#778899", "#B0C4DE"
        ]
        return colors

    def finalize_board(self):
        self.finalized_groups = self.groups.copy()
        self.accept()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.set_group_button.click()
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        os._exit(0)

# ------------------- SolverViewer -------------------
class SolverViewer(QDialog):
    def __init__(self, grid):
        super().__init__()
        self.setWindowTitle("Solver Viewer")
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0

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

        self.setLayout(self.main_layout)

        screen_rect = QApplication.primaryScreen().availableGeometry()
        max_width = screen_rect.width() * 0.9
        max_height = screen_rect.height() * 0.9
        reserved_height = self.solve_button.minimumHeight() + self.solve_final_button.minimumHeight() + 20
        available_height = max_height - reserved_height
        tile_width = max_width / self.cols
        tile_height = available_height / self.rows
        self.tile_size = int(min(tile_width, tile_height))

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

    # Visual solve
    def start_solve(self):
        normalized_dominos = set((min(a, b), max(a, b)) for a, b in dominos)
        solve_domino(self.grid, normalized_dominos, groups, self, solve_visual=True)

    # Non-visual / final-only solve
    def start_solve_final(self):
        normalized_dominos = set((min(a, b), max(a, b)) for a, b in dominos)
        solve_domino(self.grid, normalized_dominos, groups, self, solve_visual=False)
        self.draw_board()

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

    def closeEvent(self, event):
        os._exit(0)


# ------------------- Main -------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)

    domino_dialog = DominoDialog()
    if domino_dialog.exec_() == QDialog.Accepted:
        dominos = domino_dialog.dominos

        grid_size_dialog = GridSizeDialog()
        if grid_size_dialog.exec_() == QDialog.Accepted:
            rows, cols = grid_size_dialog.rows, grid_size_dialog.cols
            grid = create_grid(rows, cols)

            grid_editor = GridEditor(grid)
            if grid_editor.exec_() == QDialog.Accepted:
                toggled_tiles = grid_editor.get_toggled_tiles()
                set_invalid(grid, toggled_tiles)

                board_viewer = BoardViewer(grid)
                if board_viewer.exec_() == QDialog.Accepted:
                    groups = board_viewer.finalized_groups
                    digitDict = countDigits(dominos)
                    badNumPicker(grid, groups, digitDict)

                    solver_viewer = SolverViewer(grid)
                    solver_viewer.exec_()

    sys.exit(app.exec_())

