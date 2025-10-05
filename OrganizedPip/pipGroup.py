from pipRemoveBackground import remove_white_background
from pipExtractTile import extract_tile_data
from pipBuildGroups import build_groups
from pipGetInvalid import get_invalids

def make_groups(img, JSON_PATH, SYMBOL_CONF_THRESHOLD, DEBUG_FOLDER):
    no_background = remove_white_background(img)
    grid_data = extract_tile_data(
        img, no_background, JSON_PATH, SYMBOL_CONF_THRESHOLD, debug=False, debug_folder=DEBUG_FOLDER
    )
    groups = build_groups(grid_data)
    invalids = get_invalids(grid_data)
    return groups, invalids

