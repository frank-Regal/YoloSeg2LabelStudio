import json
import os
from pathlib import Path

# Parameters
image_width = 480
image_height = 640
class_map = {0: "egocentric_arm"}  # Map class IDs to label names

# Directory paths
base_dir = Path("/home/frank_regal/regal_docker_dev/HRI-Cacti/project/ws_dev/src/hri_cacti_xr/data/005_data/yolo")
image_dir = base_dir / "label-studio" / "images"
label_dir = base_dir / "label-studio" / "labels"

def convert_yolo_to_ls(image_path, label_path):
    # Read YOLO segmentation file
    results = []
    with open(label_path) as f:
        for line in f:
            parts = line.strip().split()
            class_id = int(parts[0])
            coords = list(map(float, parts[1:]))
            # Group coordinates into (x, y) pairs and convert to percentage
            points = []
            for i in range(0, len(coords), 2):
                x = coords[i] * 100  # percent
                y = coords[i+1] * 100
                points.append([x, y])
            results.append({
                "original_width": image_width,
                "original_height": image_height,
                "image_rotation": 0,
                "value": {
                    "points": points,
                    "polygonlabels": [class_map[class_id]]
                },
                "from_name": "label",
                "to_name": "image",
                "type": "polygonlabels",
                "readonly": False
            })

    # Create Label Studio task format
    image_name = os.path.basename(str(image_path))
    return {
        "data": {"image": f"/data/local-files/?d=images/{image_name}"},
        "annotations": [{"result": results}]
    }

def main():
    all_tasks = []
    
    # Get all image files
    image_files = list(image_dir.glob("*.jpg"))  # Adjust extension if needed
    
    for image_file in image_files:
        # Find corresponding label file
        label_file = label_dir / f"{image_file.stem}.txt"
        
        if label_file.exists():
            task = convert_yolo_to_ls(image_file, label_file)
            all_tasks.append(task)
        else:
            print(f"Warning: No label file found for {image_file}")

    # Save all tasks to a single JSON file
    output_file = base_dir / "label-studio" / "all_annotations.json"
    
    # Create the output directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w") as out_f:
        json.dump(all_tasks, out_f, indent=2)
    
    print(f"Processed {len(all_tasks)} images")
    print(f"Output saved to {output_file}")

if __name__ == "__main__":
    main()
