from pipColorMatch import color_match


WHITE = (255, 255, 255)
CREAM = (198, 204, 222)

def get_invalids(grid_data):
    rows = len(grid_data)
    cols = len(grid_data[0])
    invalids = []
    
    for r in range(rows):
        for c in range(cols):
            tile = grid_data[r][c]
            color = tile["color"]
            if color_match(color, WHITE):
                invalids.append((r, c))
    
    return invalids

