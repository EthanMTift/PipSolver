def create_grid(row, col):
    grid = [[{"value": None, "valid": True, "badNums": []} for _ in range(col)] for _ in range(row)]
    return grid