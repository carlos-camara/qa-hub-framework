import os
import shutil
from PIL import Image, ImageChops, ImageStat

class VisualHandler:
    """
    Handles visual testing operations: baseline management and image comparison.
    """
    
    @staticmethod
    def get_baseline_dir():
        """Returns the directory where baseline images are stored."""
        # Typically features/resources/screenshots/baselines
        base_path = os.path.join(os.getcwd(), 'features', 'resources', 'screenshots')
        baseline_dir = os.path.join(base_path, 'baselines')
        if not os.path.exists(baseline_dir):
            os.makedirs(baseline_dir)
        return baseline_dir

    @staticmethod
    def get_baseline_path(screenshot_name, baseline_prefix=None):
        """Returns the full path for a baseline image."""
        directory = VisualHandler.get_baseline_dir()
        filename = f"{screenshot_name}.png"
        if baseline_prefix:
            filename = f"{baseline_prefix}_{screenshot_name}.png"
        return os.path.join(directory, filename)

    @staticmethod
    def compare_images(current_path, baseline_path, threshold=0.0):
        """
        Compare two images and return (similarity_percentage, is_match).
        Similarity is 0-100%. threshold is allowed difference percentage (0-100%).
        """
        img_current = Image.open(current_path).convert('RGB')
        img_baseline = Image.open(baseline_path).convert('RGB')

        # Sizes must match for pixel-by-pixel comparison
        if img_current.size != img_baseline.size:
            # Resize current to match baseline for comparison if they differ
            img_current = img_current.resize(img_baseline.size, Image.Resampling.LANCZOS)

        diff = ImageChops.difference(img_current, img_baseline)
        stat = ImageStat.Stat(diff)
        
        # Calculate RMS (Root Mean Square) error across R, G, B channels
        # Sum of RMS divided by (3 channels * 255 max value) gives normalized error (0.0 to 1.0)
        rms = sum(stat.rms) / (3.0 * 255.0)
        
        error_percentage = rms * 100.0
        similarity = 100.0 - error_percentage
        is_match = error_percentage <= threshold
        
        return similarity, is_match

    @staticmethod
    def validate_visual(context, screenshot_name, current_path, threshold=0.0):
        """
        High-level validation logic integrated with framework context.
        """
        visual_config = getattr(context, 'visual_config', {})
        
        if not visual_config.get('enabled', True):
            print(f"[Visual] Skipping visual validation for '{screenshot_name}' (Disabled in config)")
            return 100.0, True

        save_mode = visual_config.get('save', False)
        baseline_prefix = visual_config.get('baseline_name')
        
        baseline_path = VisualHandler.get_baseline_path(screenshot_name, baseline_prefix)
        
        # 1. Check if baseline exists or if we are in 'save' mode (seeding/overwriting)
        if not os.path.exists(baseline_path) or save_mode:
            print(f"[Visual] {'Seeding' if not os.path.exists(baseline_path) else 'Updating'} baseline: {baseline_path}")
            shutil.copy(current_path, baseline_path)
            return 100.0, True

        # 2. Perform comparison
        similarity, is_match = VisualHandler.compare_images(current_path, baseline_path, threshold)
        
        # 3. Handle results
        if not is_match:
            error_msg = f"Visual mismatch for '{screenshot_name}': Similarity={similarity:.2f}%, Allowed Error={threshold}%"
            print(f"[Visual] ❌ {error_msg}")
            
            # Create a simplified diff image for visual inspection in reports later?
            # For now, just return the result.
        else:
            print(f"[Visual] ✅ Match for '{screenshot_name}': Similarity={similarity:.2f}%")
            
        return similarity, is_match
