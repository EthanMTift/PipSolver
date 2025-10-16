def find_empty(grid):
    maxBad = -1
    maxBadCoords = []
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if (len(grid[i][j]['badNums']) > maxBad) and grid[i][j]['value'] == None and grid[i][j]['valid'] == True:
                maxBad = len(grid[i][j]['badNums'])
                maxBadCoords = [i, j]

    if maxBadCoords:        
        return maxBadCoords[0], maxBadCoords[1]
    else:
        return None