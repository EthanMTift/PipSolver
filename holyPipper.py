import sys
import random
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QGridLayout, QPushButton, QVBoxLayout,
    QInputDialog, QMessageBox, QDialog, QLineEdit, QLabel
)
from PyQt5.QtGui import QColor, QPainter, QFont
from PyQt5.QtCore import Qt

grid_rows = 8
grid_columns = 4
grid = [[{"value": None, "valid": True, "badNums": []} for _ in range(grid_columns)] for _ in range(grid_rows)]
dominos = {(0, 1), (0, 4), (4, 2), (0, 3), (3, 2), (3, 3), (1, 1), (0, 0), (0, 2)}


for row in grid:
    print(row)
#manually make the empty ones false
grid[1][1]["valid"] = False
grid[1][2]["valid"] = False
grid[2][1]["valid"] = False
grid[2][2]["valid"] = False
grid[4][0]["valid"] = False
grid[4][1]["valid"] = False
grid[4][3]["valid"] = False
grid[5][1]["valid"] = False
grid[5][3]["valid"] = False
grid[6][2]["valid"] = False
grid[6][3]["valid"] = False
grid[7][0]["valid"] = False
grid[7][2]["valid"] = False
grid[7][3]["valid"] = False
print()

for row in grid:
    print([col["valid"] for col in row])

groups = []

for i in range(8):
    groups.append({"tiles": [], "rule": None, "rule_value": None})

groups[0]["tiles"] = [[0, 0]]
groups[0]["rule"] = 'constant'
groups[0]["rule_value"] = 0
groups[1]["tiles"] = [[0, 2], [0, 3], [1, 3], [2, 3]]
groups[1]["rule"] = '!='
groups[1]["rule_value"] = None
groups[2]["tiles"] = [[2, 0]]
groups[2]["rule"] = 'constant'
groups[2]["rule_value"] = 0
groups[3]["tiles"] = [[3, 0], [3, 1], [3, 2], [3, 3], [4, 2]]
groups[3]["rule"] = '!='
groups[3]["rule_value"] = None
groups[4]["tiles"] = [[5, 2]]
groups[4]["rule"] = 'constant'
groups[4]["rule_value"] = 0
groups[5]["tiles"] = [[5, 0]]
groups[5]["rule"] = 'constant'
groups[5]["rule_value"] = 0
groups[6]["tiles"] = [[6, 0], [6, 1]]
groups[6]["rule"] = '!='
groups[6]["rule_value"] = None
groups[7]["tiles"] = [[7, 1]]
groups[7]["rule"] = 'constant'
groups[7]["rule_value"] = 0





digitDict = {i: 0 for i in range(7)}

def countDigits(dominos, digitDict):
    # Reset counts first
    for key in digitDict:
        digitDict[key] = 0

    # Count digits
    for a, b in dominos:
        if 0 <= a <= 6:
            digitDict[a] += 1
        if 0 <= b <= 6:
            digitDict[b] += 1

def validate_groups(grid, groups):
    for group in groups:
        match group["rule"]:
            case 'sum':
                temp_sum = 0
                noneTiles = 0
                for tile in group["tiles"]:
                    if grid[tile[0]][tile[1]]['value'] == None:
                        noneTiles += 1
                        continue
                    else:
                        temp_sum += int(grid[tile[0]][tile[1]]['value'])
                if int(group["rule_value"]) != temp_sum and noneTiles == 0:
                    return False
                else:
                    continue
            

            case '=':
                temp_equal_set = set()
                for tile in group["tiles"]:
                    if grid[tile[0]][tile[1]]['value'] == None:
                        continue
                    temp_equal_set.add(grid[tile[0]][tile[1]]['value'])
                if len(temp_equal_set) > 1:
                    return False
                else:
                    continue


            case '!=':
                temp_equal_set = set()
                temp_none_count = 0
                for tile in group["tiles"]:
                    if grid[tile[0]][tile[1]]['value'] == None:
                        temp_none_count += 1
                    else:    
                        temp_equal_set.add(grid[tile[0]][tile[1]]['value'])
                if (len(temp_equal_set) + temp_none_count) != len(group['tiles']):
                    return False
                else:
                    continue


            case 'constant':
                for tile in group['tiles']:
                    if grid[tile[0]][tile[1]]['value'] == None:
                        continue
                    if grid[tile[0]][tile[1]]['value'] != group['rule_value']:
                        return False
                    else:
                        continue

            case '<constant':
                for tile in group['tiles']:
                    if grid[tile[0]][tile[1]]['value'] == None:
                        continue
                    if grid[tile[0]][tile[1]]['value'] > group['rule_value']:
                        return False
                    else:
                        continue

            case '>constant':
                for tile in group['tiles']:
                    if grid[tile[0]][tile[1]]['value'] == None:
                        continue
                    if grid[tile[0]][tile[1]]['value'] < group['rule_value']:
                        return False
                    else:
                        continue

            case '!constant':
                for tile in group['tiles']:
                    if grid[tile[0]][tile[1]]['value'] == None:
                        continue
                    if grid[tile[0]][tile[1]]['value'] is group['rule_value']:
                        return False
                    else:
                        continue

            case _:
                print("hi")
    return True
def badNumPicker(grid, groups, digitDict):
    for group in groups:
        match group['rule']:
            
            case 'sum':
                nums = [0, 1, 2, 3, 4, 5, 6]
                tileMinimum = group['rule_value'] - (6 * (len(group['tiles']) - 1))
                tileMaximum = group['rule_value']
                for tile in group['tiles']:
                    if tileMinimum > 0:
                        badMin = [x for x in nums if x<tileMinimum]
                        grid[tile[0]][tile[1]]['badNums'].append(badMin)
                    if tileMaximum < 6:
                        badMax = [x for x in nums if x>tileMaximum]
                        grid[tile[0]][tile[1]]['badNums'].append(badMax)

            case '=':
                badDigits = [digit for digit, count in digitDict.items() if count < len(group['tiles'])]
                for digits in badDigits:
                    for tile in group['tiles']:
                        grid[tile[0]][tile[1]]['badNums'].append(digits)


            
            case _:
                print("hello")
    
  
def find_empty(grid):
   
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j]['value'] == None and grid[i][j]['valid'] == True:
                return i, j
    return None

def validate_pos(grid, x, y, val):
    if val in grid[x][y]['badNums']:
        return False
    else:
        return True




def solve_domino(grid, unused_dominos, groups):
    empty = find_empty(grid)
    if not empty:
        return True  # solved
    
    r, c = empty
    rows, cols = len(grid), len(grid[0])

    # Try all 4 adjacency directions
    for dr, dc in [(0,1), (1,0), (0,-1), (-1,0)]:
        r2, c2 = r+dr, c+dc
        if not (0 <= r2 < rows and 0 <= c2 < cols):
            continue
        if ((grid[r2][c2]['value'] != None) or (grid[r2][c2]['valid'] == False)):
            continue

        # Try each unused domino
        for (a, b) in list(unused_dominos):

            # Orientations: both orders if a≠b, only one if a==b
            orientations = [(a, b), (b, a)] if a != b else [(a, b)]

            for x, y in orientations:
            
                grid[r][c]['value'] = x
                grid[r2][c2]['value'] = y
                if validate_groups(grid, groups) and validate_pos(grid, r, c, x) and validate_pos(grid, r2, c2, y):
                    
                    unused_dominos.remove((a, b))

                    if solve_domino(grid, unused_dominos, groups):
                        return True

                    unused_dominos.add((a, b))

                # Backtrack
                grid[r][c]['value'] = None
                grid[r2][c2]['value'] = None
                
    return False



countDigits(dominos, digitDict)
badNumPicker(grid, groups, digitDict)

if solve_domino(grid, dominos, groups):
    print("Solved board:")
    for row in grid:
        print([col["value"] for col in row])
else:
    print("No solution found.")
 











