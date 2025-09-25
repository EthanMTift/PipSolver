
from pipEmptySpot import find_empty
from pipValidateGroups import validate_groups
from pipValidatePos import validate_pos

def solve_domino(grid, unused_dominos, groups, solver_viewer, solve_visual):
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
                solver_viewer.highlight_domino((r, c), (r2, c2))
                if(solve_visual):
                    solver_viewer.draw_board()
                
                if validate_groups(grid, groups) and validate_pos(grid, r, c, x) and validate_pos(grid, r2, c2, y):
                    
                    unused_dominos.remove((a, b))

                    if solve_domino(grid, unused_dominos, groups, solver_viewer, solve_visual):
                        return True

                    unused_dominos.add((a, b))

                # Backtrack
                grid[r][c]['value'] = None
                grid[r2][c2]['value'] = None
                solver_viewer.clear_domino_highlight((r, c), (r2, c2))
                if(solve_visual):
                    solver_viewer.draw_board()

                
                
                
    return False
