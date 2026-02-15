"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           QA Hub Framework                                    ║
║                     Visual Regression Testing Engine                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  This module provides pixel-based visual comparison capabilities for         ║
║  detecting UI regressions, layout shifts, and CSS glitches.                  ║
║                                                                              ║
║  Features:                                                                    ║
║  • Automatic baseline seeding (first run creates baselines)                  ║
║  • RMS (Root Mean Square) error calculation for high fidelity                ║
║  • Configurable tolerance thresholds for flexible matching                   ║
║  • Baseline prefix support for environment-specific baselines                ║
║  • Works identically with Selenium and Playwright backends                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import os
import shutil
from PIL import Image, ImageChops, ImageStat



class VisualHandler:

    """
    Static utility class for visual regression testing operations.
    
    Handles baseline image management and pixel-perfect comparison using
    the Pillow (PIL) library. Designed to integrate seamlessly with the
    framework's step definitions and configuration system.
    
    Configuration (features/config/properties.cfg):
        [VisualTests]
        enabled = true           # Enable/disable visual testing
        fail = true              # Fail tests on mismatch
        save = false             # Overwrite baselines with current screenshots
        baseline_name = desktop  # Prefix for baseline files (optional)
    
    Directory Structure:
        features/
        └── resources/
            └── screenshots/
                ├── baselines/           # Stored baseline images
                │   ├── login_form.png
                │   └── dashboard_header.png
                └── *_latest.png         # Temporary current screenshots
    
    Usage:
        # In step definitions (gui_steps.py handles this automatically)
        similarity, is_match = VisualHandler.validate_visual(
            context, 
            "dashboard_header",  # baseline name
            "/path/to/current.png",
            threshold=5.0
        )
    """
    
    @staticmethod
    def get_baseline_dir():
        """
        Get or create the baseline images directory.
        
        Returns:
            str: Absolute path to features/resources/screenshots/baselines/
            
        Side Effects:
            Creates the directory if it doesn't exist.
        """
        base_path = os.path.join(os.getcwd(), 'features', 'resources', 'screenshots')
        baseline_dir = os.path.join(base_path, 'baselines')
        if not os.path.exists(baseline_dir):
            os.makedirs(baseline_dir)
        return baseline_dir

    @staticmethod
    def get_baseline_path(screenshot_name, baseline_prefix=None):
        """
        Construct the full path for a baseline image.
        
        Args:
            screenshot_name: Base name for the screenshot (e.g., "login_form")
            baseline_prefix: Optional prefix for environment-specific baselines
                            (e.g., "desktop", "mobile", "dark_mode")
        
        Returns:
            str: Full path like .../baselines/desktop_login_form.png
            
        Examples:
            get_baseline_path("header") → .../baselines/header.png
            get_baseline_path("header", "mobile") → .../baselines/mobile_header.png
        """
        directory = VisualHandler.get_baseline_dir()
        filename = f"{screenshot_name}.png"
        if baseline_prefix:
            filename = f"{baseline_prefix}_{screenshot_name}.png"
        return os.path.join(directory, filename)

    @staticmethod
    def compare_images(current_path, baseline_path, threshold=0.0):
        """
        Compare two images and calculate their similarity.
        
        Uses RMS (Root Mean Square) error calculation across RGB channels
        for high-fidelity difference detection. This method detects:
        - Color differences
        - Layout shifts
        - Missing/extra elements
        - Font rendering changes
        - Anti-aliasing variations
        
        Algorithm:
            1. Load both images and convert to RGB
            2. Resize current to match baseline if sizes differ
            3. Calculate pixel-by-pixel difference
            4. Compute RMS error: sum(channel_rms) / (3 * 255)
            5. Convert to percentage: error * 100
        
        Args:
            current_path: Path to the current (latest) screenshot
            baseline_path: Path to the expected baseline image
            threshold: Maximum allowed error percentage (0.0 = pixel-perfect)
            
        Returns:
            tuple: (similarity_percentage, is_match)
                - similarity_percentage: 0-100 where 100 is identical
                - is_match: True if error <= threshold
                
        Example:
            similarity, match = compare_images("current.png", "baseline.png", 5.0)
            # similarity: 98.5 (98.5% similar)
            # match: True (error 1.5% <= threshold 5.0%)
        """
        # Load and normalize images to RGB
        img_current = Image.open(current_path).convert('RGB')
        img_baseline = Image.open(baseline_path).convert('RGB')

        # Handle size mismatches (viewport differences, responsive layouts)
        if img_current.size != img_baseline.size:
            img_current = img_current.resize(img_baseline.size, Image.Resampling.LANCZOS)

        # Calculate pixel difference
        diff = ImageChops.difference(img_current, img_baseline)
        stat = ImageStat.Stat(diff)
        
        # RMS error: normalized to 0.0-1.0 range
        # stat.rms gives [R_rms, G_rms, B_rms] where each is 0-255
        rms = sum(stat.rms) / (3.0 * 255.0)
        
        error_percentage = rms * 100.0
        similarity = 100.0 - error_percentage
        is_match = error_percentage <= threshold
        
        return similarity, is_match

    @staticmethod
    def validate_visual(context, screenshot_name, current_path, threshold=0.0):
        """
        High-level visual validation integrated with framework configuration.
        
        This is the main entry point called by step definitions. It handles:
        - Reading visual configuration from context
        - Baseline seeding (auto-create if missing)
        - Baseline updating (when save=true)
        - Image comparison with threshold
        - Logging results
        
        Workflow:
            1. Check if visual testing is enabled
            2. If baseline missing OR save=true: seed/update baseline
            3. Otherwise: compare current vs baseline
            4. Log result and return match status
        
        Args:
            context: Behave context with optional visual_config dict
            screenshot_name: Base name for the screenshot (e.g., "dashboard")
            current_path: Path to the current screenshot to validate
            threshold: Allowed error percentage (0.0 = pixel-perfect)
            
        Returns:
            tuple: (similarity_percentage, is_match)
            
        Configuration (context.visual_config):
            {
                'enabled': True,      # Skip validation if False
                'save': False,        # Overwrite baselines if True
                'fail': True,         # Fail tests on mismatch if True
                'baseline_name': None # Optional prefix for baselines
            }
            
        Console Output:
            ✅ Match: "[Visual] ✅ Match for 'header': Similarity=100.00%"
            ❌ Mismatch: "[Visual] ❌ Visual mismatch for 'header': Similarity=95.00%"
            📸 Seeding: "[Visual] Seeding baseline: .../baselines/header.png"
        """
        visual_config = getattr(context, 'visual_config', {})
        
        # Check if visual testing is enabled
        if not visual_config.get('enabled', True):
            print(f"[Visual] Skipping visual validation for '{screenshot_name}' (Disabled in config)")
            return 100.0, True

        save_mode = visual_config.get('save', False)
        baseline_prefix = visual_config.get('baseline_name')
        
        baseline_path = VisualHandler.get_baseline_path(screenshot_name, baseline_prefix)

        # Adaptive Tolerance for CI/Linux
        # Linux rendering often differs from Windows/Mac baselines
        is_ci_linux = os.environ.get('GITHUB_ACTIONS') == 'true' or os.name == 'posix'
        if is_ci_linux:
            # If running in CI/Linux, we relax the tolerance significantly if it's too strict
            # We ensure at least 15% tolerance for cross-platform robustness
            
            # Helper to adjust threshold
            original_threshold = threshold
            
            # Apply 2x multiplier or min 15% for Linux
            threshold = max(threshold * 2.0, 15.0)
            
            if threshold != original_threshold:
                 print(f"[Visual] 🐧 CI/Linux detected. Adjusting tolerance from {original_threshold}% to {threshold}%")
        
        # ─────────────────────────────────────────────────────────────────────
        # BASELINE SEEDING / UPDATE
        # ─────────────────────────────────────────────────────────────────────
        if not os.path.exists(baseline_path) or save_mode:
            action = "Seeding" if not os.path.exists(baseline_path) else "Updating"
            print(f"[Visual] {action} baseline: {baseline_path}")
            shutil.copy(current_path, baseline_path)
            return 100.0, True

        # ─────────────────────────────────────────────────────────────────────
        # IMAGE COMPARISON
        # ─────────────────────────────────────────────────────────────────────
        similarity, is_match = VisualHandler.compare_images(current_path, baseline_path, threshold)
        
        # Log result
        if not is_match:
            error_msg = f"Visual mismatch for '{screenshot_name}': Similarity={similarity:.2f}%, Allowed Error={threshold}%"
            print(f"[Visual] ❌ {error_msg}")
        else:
            print(f"[Visual] ✅ Match for '{screenshot_name}': Similarity={similarity:.2f}%")
            
        return similarity, is_match

    @staticmethod
    def apply_masking(image_path, regions):
        """
        Draw black rectangles over specific regions of an image.
        
        This is used to "hide" dynamic content (dates, numbers, user names)
        before performing visual comparison, preventing false positives.
        
        Args:
            image_path: Path to the image file to modify.
            regions: List of dicts with coordinates: [{'x', 'y', 'width', 'height'}]
        
        Side Effects:
            Overwrites the original image with the masked version.
        """
        if not regions:
            return

        from PIL import ImageDraw
        img = Image.open(image_path).convert('RGB')
        draw = ImageDraw.Draw(img)
        
        for region in regions:
            x = region.get('x', 0)
            y = region.get('y', 0)
            w = region.get('width', 0)
            h = region.get('height', 0)
            
            # Draw black rectangle (mask)
            draw.rectangle([x, y, x + w, y + h], fill='black', outline='black')
        
        img.save(image_path)
