def find_empty(grid):
   
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j]['value'] == None and grid[i][j]['valid'] == True:
                return i, j
    return None