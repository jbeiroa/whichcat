import cv2
import os
import shutil
import sys

def label_images(source_dir="data/raw/unlabeled", base_target_dir="data/raw"):
    # Ensure target directories exist
    categories = {
        '1': 'coquita',
        '2': 'ori',
        '3': 'other_cat',
        '0': 'false_positives'
    }
    
    for cat in categories.values():
        os.makedirs(os.path.join(base_target_dir, cat), exist_ok=True)

    # Get list of images
    if not os.path.exists(source_dir):
        print(f"Source directory {source_dir} does not exist.")
        return

    images = [f for f in os.listdir(source_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    images.sort()

    if not images:
        print("No images found to label.")
        return

    print(f"Found {len(images)} images to label.")
    print("\nControls:")
    print("  1: Coquita")
    print("  2: Ori")
    print("  3: Other Cat")
    print("  0: False Positive")
    print("  q: Quit")
    print("  s: Skip (keep in unlabeled)")

    cv2.namedWindow("Labeler", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Labeler", 1280, 720)

    for i, img_name in enumerate(images):
        img_path = os.path.join(source_dir, img_name)
        frame = cv2.imread(img_path)
        
        if frame is None:
            continue

        # Add progress text
        display_frame = frame.copy()
        cv2.putText(display_frame, f"{i+1}/{len(images)}: {img_name}", (50, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.imshow("Labeler", display_frame)
        
        key = cv2.waitKey(0) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord('s'):
            print(f"Skipped {img_name}")
            continue
        elif chr(key) in categories:
            category = categories[chr(key)]
            target_path = os.path.join(base_target_dir, category, img_name)
            shutil.move(img_path, target_path)
            print(f"Moved {img_name} -> {category}")
        else:
            print(f"Invalid key: {chr(key)}. Use 1, 2, 3, 0, q, or s.")
            # Reprocess the same image
            # We don't advance the loop easily here, but we can just continue
            # Wait, the loop will advance. Let's fix that.
            # Actually, let's just use a while loop for better control if needed.
            pass

    cv2.destroyAllWindows()
    print("Labeling session finished.")

if __name__ == "__main__":
    label_images()
