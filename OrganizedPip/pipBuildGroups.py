from pipColorMatch import color_match
import numpy as np

WHITE = (255, 255, 255)
CREAM = (198, 204, 222)

def build_groups(grid_data):
    """
    Build groups of adjacent tiles with similar colors.
    Returns a list of dicts: {"tiles": [(r,c), ...], "rule": str, "rule_value": int/float}
    """
    rows = len(grid_data)
    cols = len(grid_data[0])
    visited = np.zeros((rows, cols), dtype=bool)
    groups = []
    

    for r in range(rows):
        for c in range(cols):
            if visited[r, c]:
                continue

            tile = grid_data[r][c]
            color = tile["color"]
            if color is None:
                continue

            # Skip white or cream tiles
            
            if color_match(color, WHITE):
                continue
            if color_match(color, CREAM):
                continue

            # Start new group
            group_tiles = [(r, c)]
            visited[r, c] = True

            # BFS queue for adjacent tiles
            queue = [(r, c)]
            while queue:
                cr, cc = queue.pop(0)
                for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:  # up, down, left, right
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < rows and 0 <= nc < cols and not visited[nr, nc]:
                        neighbor_tile = grid_data[nr][nc]
                        neighbor_color = neighbor_tile["color"]
                        if neighbor_color is None:
                            continue
                        if color_match(neighbor_color, color):
                            visited[nr, nc] = True
                            group_tiles.append((nr, nc))
                            queue.append((nr, nc))

            # --- After the group is collected, determine rule and rule_value ---
            rule = "sum"
            rule_value = 0
            for gr, gc in group_tiles:
                sym = grid_data[gr][gc]["symbol"]
                if sym is None or sym == "":
                    continue
                # Separate number and non-number parts
                non_numbers = "".join([ch for ch in sym if not ch.isdigit()])
                numbers = "".join([ch for ch in sym if ch.isdigit()])
                if non_numbers in ("=", "≠"):
                    rule = non_numbers
                    rule_value = 0
                else:
                    if non_numbers:
                        rule = non_numbers + "sum"
                    else:
                        rule = "sum"
                    rule_value = int(numbers) if numbers else 0
                break  # stop after finding the first non-None symbol

            groups.append({
                "tiles": group_tiles,
                "rule": rule,
                "rule_value": rule_value,
                "color": color
            })

    return groups