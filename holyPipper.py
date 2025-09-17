import sys
import random
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QGridLayout, QPushButton, QVBoxLayout,
    QInputDialog, QMessageBox, QDialog, QLineEdit, QLabel
)
from PyQt5.QtGui import QColor, QPainter, QFont
from PyQt5.QtCore import Qt

grid_rows = 3
grid_columns = 4
grid = [[{"value": None, "valid": True, "badNums": []} for _ in range(grid_columns)] for _ in range(grid_rows)]


for row in grid:
    print(row)
#manually make the empty ones false
grid[0][3]["valid"] = False
grid[2][0]["valid"] = False
grid[2][2]["valid"] = False
grid[2][3]["valid"] = False
print()

for row in grid:
    print([col["valid"] for col in row])

groups = []

for i in range(4):
    groups.append({"tiles": [], "rule": None, "rule_value": None})

groups[0]["tiles"] = [[0, 0], [0, 1]]
groups[0]["rule"] = '='
groups[0]["rule_value"] = None
groups[1]["tiles"] = [[1, 0], [1, 1], [1, 2]]
groups[1]["rule"] = 'sum'
groups[1]["rule_value"] = 9
groups[2]["tiles"] = [[2, 1]]
groups[2]["rule"] = 'constant'
groups[2]["rule_value"] = 0
groups[3]["tiles"] = [[1, 3]]
groups[3]["rule"] = 'constant'
groups[3]["rule_value"] = 1


grid[1][0]["value"] = 1
grid[1][1]["value"] = 3
grid[1][2]["value"] = 5




def validate_groups(grid, groups):
    for group in groups:
        match group["rule"]:
            case 'sum':
                temp_sum = 0
                for tile in group["tiles"]:
                    if grid[tile[0]][tile[1]]['value'] is None:
                        continue
                    else:
                        temp_sum += int(grid[tile[0]][tile[1]]['value'])
                if int(group["rule_value"]) is not temp_sum:
                    return False
                else:
                    continue
            

            case '=':
                temp_equal_set = {}
                for tile in group["tiles"]:
                    if grid[tile[0]][tile[1]]['value'] is None:
                        continue
                    temp_equal_set.append(grid[tile[0]][tile[1]]['value'])
                if len(temp_equal_set) > 1:
                    return False
                else:
                    continue


            case '!=':
                temp_equal_set = {}
                temp_none_count = 0
                for tile in group["tiles"]:
                    if grid[tile[0]][tile[1]]['value'] is None:
                        temp_none_count += 1
                    else:    
                        temp_equal_set.append(grid[tile[0]][tile[1]]['value'])
                if (len(temp_equal_set) + temp_none_count) is not len(group['tiles']):
                    return False
                else:
                    continue


            case 'constant':
                for tile in group['tiles']:
                    if grid[tile[0]][tile[1]]['value'] is None:
                        continue
                    if grid[tile[0]][tile[1]]['value'] is not group['rule_value']:
                        return False
                    else:
                        continue

            case '<constant':
                for tile in group['tiles']:
                    if grid[tile[0]][tile[1]]['value'] is None:
                        continue
                    if grid[tile[0]][tile[1]]['value'] > group['rule_value']:
                        return False
                    else:
                        continue

            case '>constant':
                for tile in group['tiles']:
                    if grid[tile[0]][tile[1]]['value'] is None:
                        continue
                    if grid[tile[0]][tile[1]]['value'] < group['rule_value']:
                        return False
                    else:
                        continue

            case '!constant':
                for tile in group['tiles']:
                    if grid[tile[0]][tile[1]]['value'] is None:
                        continue
                    if grid[tile[0]][tile[1]]['value'] is group['rule_value']:
                        return False
                    else:
                        continue

            case _:
                print("hi")

            
 
        
if validate_groups(grid, groups):
    print ("So true king")
else:
    print ("WRONG")










