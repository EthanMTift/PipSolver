from pipRemoveBackground import remove_white_background
from pipExtractTile import extract_tile_data
from pipBuildGroups import build_groups
from pipGetInvalid import get_invalids
import json

def make_groups(img, JSON_PATH, SYMBOL_CONF_THRESHOLD, DEBUG_FOLDER):
    with open(JSON_PATH, "r") as f:
        grid_data = json.load(f)

    
    tile_w = int(grid_data["tile_width"])
    tile_h = int(grid_data["tile_height"])
    

    no_background = remove_white_background(img, tile_w, tile_h)
    grid_data = extract_tile_data(
        img, no_background, JSON_PATH, SYMBOL_CONF_THRESHOLD, debug=False, debug_folder=DEBUG_FOLDER
    )
    groups = build_groups(grid_data)
    invalids = get_invalids(grid_data)
    return groups, invalids

