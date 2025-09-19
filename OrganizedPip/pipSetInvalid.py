def set_invalid(grid, invalids):
    for x, y in invalids:
        grid[x][y]['valid'] = False
    return grid
        
            
