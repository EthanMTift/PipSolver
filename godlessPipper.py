import sys
import random
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QGridLayout, QPushButton, QVBoxLayout,
    QInputDialog, QMessageBox, QDialog, QLineEdit, QLabel
)
from PyQt5.QtGui import QColor, QPainter, QFont
from PyQt5.QtCore import Qt


class DominoInputWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Domino Input")
        self.layout = QVBoxLayout()
        self.dominoes = []

        self.info_label = QLabel("Enter domino values (e.g., '1 2'), leave blank to finish:")
        self.layout.addWidget(self.info_label)

        self.input_line = QLineEdit()
        self.input_line.returnPressed.connect(self.add_domino)
        self.layout.addWidget(self.input_line)

        self.display_label = QLabel("Dominoes entered: []")
        self.layout.addWidget(self.display_label)

        self.setLayout(self.layout)

    def add_domino(self):
        text = self.input_line.text().strip()
        if not text:
            self.accept()
            return
        try:
            a, b = map(int, text.split())
            self.dominoes.append((a, b))
            self.display_label.setText(f"Dominoes entered: {self.dominoes}")
            self.input_line.clear()
        except:
            QMessageBox.warning(self, "Invalid input", "Enter two integers separated by space.")


class TileButton(QPushButton):
    def __init__(self, row, col, size, font_size_main, font_size_rule):
        super().__init__("O")
        self.row = row
        self.col = col
        self.value = "O"
        self.bg_color = QColor("lightgray")
        self.group_color = None
        self.rule_annotation = None
        self.highlighted = False
        self.tile_number = None
        self.setFixedSize(size, size)
        self.font_size_main = font_size_main
        self.font_size_rule = font_size_rule

    def toggle(self):
        if self.value == "O":
            self.value = "X"
            self.bg_color = QColor("black")
        else:
            self.value = "O"
            self.bg_color = QColor("lightgray")
        self.group_color = None
        self.rule_annotation = None
        self.update()

    def toggle_highlight(self):
        self.highlighted = not self.highlighted
        self.update()

    def set_group(self, color, annotation=None):
        self.group_color = color
        self.rule_annotation = annotation
        self.highlighted = False
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        rect = self.rect()

        if self.highlighted:
            painter.fillRect(rect, QColor(255, 255, 0, 160))
        elif self.group_color:
            painter.fillRect(rect, self.group_color)
        else:
            painter.fillRect(rect, self.bg_color)

        painter.setFont(QFont("Arial", self.font_size_main, QFont.Bold))
        if self.value == "X":
            painter.setPen(Qt.black)
            painter.drawText(rect, Qt.AlignCenter, self.value)
        else:
            painter.setPen(Qt.darkGray)
            painter.drawText(rect, Qt.AlignCenter, self.value)

        # Draw domino number in top-left
        if self.tile_number is not None:
            painter.setPen(Qt.white)
            painter.setFont(QFont("Arial", self.font_size_rule, QFont.Bold))
            tl_rect = rect.adjusted(2, 2, -rect.width()+self.font_size_rule*2, -rect.height()+self.font_size_rule*2)
            painter.drawText(tl_rect, Qt.AlignLeft | Qt.AlignTop, str(self.tile_number))

        # Draw group annotation
        if self.rule_annotation:
            painter.setPen(Qt.black)
            painter.setFont(QFont("Arial", self.font_size_rule, QFont.Bold))
            painter.drawText(rect.adjusted(0,0,-3,-self.height()//4), Qt.AlignRight | Qt.AlignTop, self.rule_annotation)


class GridApp(QWidget):
    def __init__(self, rows, cols, dominoes):
        super().__init__()
        self.rows = rows
        self.cols = cols
        self.dominoes = dominoes
        self.grid = []
        self.groups = []
        self.current_group_tiles = []
        self.grouping_mode = False

        self.group_colors = [QColor(c) for c in [
            "red", "green", "blue", "orange", "purple", "brown", "pink",
            "cyan", "magenta", "lime", "teal", "navy", "maroon", "olive",
            "gold", "indigo", "violet", "salmon", "coral", "turquoise",
            "orchid", "chocolate", "crimson", "darkgreen"
        ]]

        # Compute tile size to fit screen
        screen_geom = QApplication.primaryScreen().availableGeometry()
        max_width = screen_geom.width() * 0.8
        max_height = screen_geom.height() * 0.8
        self.tile_size = int(min(max_width / cols, max_height / rows))
        self.font_size_main = int(self.tile_size*0.35)
        self.font_size_rule = int(self.tile_size*0.2)

        layout = QVBoxLayout()
        self.grid_layout = QGridLayout()
        self.grid_layout.setHorizontalSpacing(5)
        self.grid_layout.setVerticalSpacing(5)

        for r in range(rows):
            row_buttons = []
            for c in range(cols):
                btn = TileButton(r,c,self.tile_size,self.font_size_main,self.font_size_rule)
                btn.clicked.connect(lambda _, b=btn: self.tile_clicked(b))
                self.grid_layout.addWidget(btn,r,c)
                row_buttons.append(btn)
            self.grid.append(row_buttons)

        layout.addLayout(self.grid_layout)

        self.submit_btn = QPushButton("Submit Grid")
        self.submit_btn.clicked.connect(self.submit_grid)
        layout.addWidget(self.submit_btn)

        self.create_group_btn = QPushButton("Create Group")
        self.create_group_btn.setEnabled(False)
        self.create_group_btn.clicked.connect(self.start_group)
        layout.addWidget(self.create_group_btn)

        self.group_selected_btn = QPushButton("Group Selected")
        self.group_selected_btn.setEnabled(False)
        self.group_selected_btn.clicked.connect(self.finalize_group)
        layout.addWidget(self.group_selected_btn)

        self.solve_btn = QPushButton("Solve")
        self.solve_btn.setEnabled(False)
        self.solve_btn.clicked.connect(self.solve_with_dominoes)
        layout.addWidget(self.solve_btn)

        self.setLayout(layout)
        self.setWindowTitle("Grid App")
        self.resize(self.tile_size*cols+100,self.tile_size*rows+150)

    def tile_clicked(self, btn):
        if self.grouping_mode:
            if btn in self.current_group_tiles:
                self.current_group_tiles.remove(btn)
                btn.toggle_highlight()
            else:
                self.current_group_tiles.append(btn)
                btn.toggle_highlight()
        elif self.submit_btn.isEnabled():
            btn.toggle()

    def submit_grid(self):
        for row in self.grid:
            for btn in row:
                btn.bg_color = QColor("lightgray") if btn.value=="O" else QColor("black")
                btn.group_color = None
                btn.rule_annotation = None
                btn.highlighted = False
                btn.update()

        # Build valid tile mask
        self.valid_tiles = [[btn.value=="O" for btn in row] for row in self.grid]

        self.submit_btn.setEnabled(False)
        self.create_group_btn.setEnabled(True)
        self.solve_btn.setEnabled(True)

    def start_group(self):
        self.create_group_btn.setEnabled(False)
        self.group_selected_btn.setEnabled(True)
        self.current_group_tiles = []
        self.grouping_mode = True

    def finalize_group(self):
        if not self.current_group_tiles:
            QMessageBox.warning(self,"Invalid Group","You must select at least one tile.")
            return

        rule, ok = QInputDialog.getItem(self,"Select Rule","Choose a rule:",
                                        ["SUM","=","!=","Constant","<Constant",">Constant"],0,False)
        if not ok:
            return
        value = None
        if rule in ["SUM","!=","Constant","<Constant",">Constant"]:
            value, ok = QInputDialog.getInt(self,"Rule Value",f"Enter value for {rule}:")
            if not ok:
                return

        color = random.choice(self.group_colors) if self.group_colors else QColor("cyan")
        if color in self.group_colors:
            self.group_colors.remove(color)

        if rule=="SUM":
            annotation = f"∑{value}" if value is not None else "Σ"
        elif rule=="=":
            annotation = "="
        elif rule=="!=":
            annotation = f"≠{value}" if value is not None else "≠"
        elif rule=="Constant":
            annotation = str(value)
        elif rule in ["<Constant",">Constant"]:
            annotation = f"{rule[0]}{value}"
        else:
            annotation = "?"

        group_data = {"tiles": self.current_group_tiles[:],"rule":rule,"value":value}
        self.groups.append(group_data)
        for btn in self.current_group_tiles:
            btn.set_group(color,annotation)
        self.current_group_tiles=[]
        self.create_group_btn.setEnabled(True)
        self.group_selected_btn.setEnabled(False)
        self.grouping_mode=False

    # --- Solver helpers ---
    def count_domino_digits(self):
        self.digit_counts={}
        for a,b in self.dominoes:
            for v in (a,b):
                self.digit_counts[v] = self.digit_counts.get(v,0)+1
        print("Domino digit counts:",self.digit_counts)

    def can_place_domino(self, r1, c1, r2, c2, board):
        if not (0<=r1<self.rows and 0<=c1<self.cols and 0<=r2<self.rows and 0<=c2<self.cols):
            return False
        if not board[r1][c1] or not board[r2][c2]:
            return False
        for (tile_r, tile_c, other_r, other_c) in [(r1,c1,r2,c2),(r2,c2,r1,c1)]:
            free_neighbors=0
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = tile_r+dr, tile_c+dc
                if nr==other_r and nc==other_c:
                    continue
                if 0<=nr<self.rows and 0<=nc<self.cols and board[nr][nc]:
                    free_neighbors+=1
            if free_neighbors==0:
                return False
        return True

    def validate_groups(self, board_values):
        for group in self.groups:
            tiles = group["tiles"]
            values = [board_values[t.row][t.col] for t in tiles]
            if None in values:
                continue  # not all tiles filled yet
            rule = group["rule"]
            val = group.get("value")
            if rule=="=":
                if len(set(values))>1:
                    return False
            elif rule=="SUM":
                if sum(values)!=val:
                    return False
            elif rule=="!=":
                if val in values:
                    return False
            elif rule=="Constant":
                if values[0]!=val:
                    return False
            elif rule=="<Constant":
                if any(v>=val for v in values):
                    return False
            elif rule==">Constant":
                if any(v<=val for v in values):
                    return False
        return True

    def solve_with_dominoes(self):
        self.count_domino_digits()
        board_values=[[None for _ in range(self.cols)] for _ in range(self.rows)]
        board_tiles=[[self.grid[r][c] for c in range(self.cols)] for r in range(self.rows)]

        def backtrack(idx):
            if idx>=len(self.dominoes):
                return self.validate_groups(board_values)
            a,b=self.dominoes[idx]
            for r in range(self.rows):
                for c in range(self.cols):
                    if board_values[r][c] is not None or not self.valid_tiles[r][c]:
                        continue
                    for dr, dc in [(0,1),(1,0)]:
                        r2, c2 = r+dr, c+dc
                        if not (0<=r2<self.rows and 0<=c2<self.cols):
                            continue
                        if board_values[r2][c2] is not None or not self.valid_tiles[r2][c2]:
                            continue
                        if not self.can_place_domino(r,c,r2,c2,self.valid_tiles):
                            continue
                        board_values[r][c]=a
                        board_values[r2][c2]=b
                        board_tiles[r][c].tile_number=a
                        board_tiles[r2][c2].tile_number=b
                        board_tiles[r][c].update()
                        board_tiles[r2][c2].update()
                        QApplication.processEvents()
                        #time.sleep(0.01)
                        if backtrack(idx+1):
                            return True
                        board_values[r][c]=None
                        board_values[r2][c2]=None
                        board_tiles[r][c].tile_number=None
                        board_tiles[r2][c2].tile_number=None
                        board_tiles[r][c].update()
                        board_tiles[r2][c2].update()
                        QApplication.processEvents()
            return False

        success=backtrack(0)
        if success:
            QMessageBox.information(self,"Solved","All dominos placed successfully!")
        else:
            QMessageBox.warning(self,"Failed","No valid placement found.")


if __name__=="__main__":
    app=QApplication(sys.argv)
    domino_window = DominoInputWindow()
    if domino_window.exec_() == QDialog.Accepted:
        dominoes = domino_window.dominoes
        rows, ok1 = QInputDialog.getInt(None,"Grid Rows","Enter number of rows:",5,1,20)
        cols, ok2 = QInputDialog.getInt(None,"Grid Columns","Enter number of cols:",5,1,20)
        if ok1 and ok2:
            window = GridApp(rows,cols,dominoes)
            window.show()
            sys.exit(app.exec_())
