def validate_pos(grid, x, y, val):
    if val in grid[x][y]['badNums']:
        return False
    else:
        return True