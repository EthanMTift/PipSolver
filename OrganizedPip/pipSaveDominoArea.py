import json

def save_domino_area_json(top_left, bottom_right, domino_json_path):
    area_data = {
        "top_left": top_left,
        "bottom_right": bottom_right
    }
    with open(domino_json_path, "w") as f:
        json.dump(area_data, f, indent=4)
    print(f"Saved domino area to {domino_json_path}")