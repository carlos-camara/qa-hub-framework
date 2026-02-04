"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           QA Hub Framework                                    ║
║                       Visual Handler Unit Tests                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Tests for visual regression testing engine including:                       ║
║  • Baseline management       • Image comparison                              ║
║  • Threshold validation      • Configuration                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import pytest
import os
from unittest.mock import MagicMock, patch
from qa_framework.utils.visual import VisualHandler


# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def mock_context():
    """Create a mock Behave context for visual tests."""
    context = MagicMock()
    context.visual_config = {
        "enabled": True,
        "fail": True,
        "save": False,
        "baseline_name": None
    }
    return context


@pytest.fixture
def temp_images(tmp_path):
    """Create temporary test images."""
    baselines = tmp_path / "baselines"
    baselines.mkdir()
    
    screenshots = tmp_path / "screenshots"
    screenshots.mkdir()
    
    return {
        "baselines": baselines,
        "screenshots": screenshots
    }


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: BASELINE DIRECTORY MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

class TestBaselineDirectory:
    """Tests for baseline directory management."""

    @patch("os.getcwd")
    @patch("os.path.exists", return_value=True)
    def test_get_baseline_dir_returns_path(self, mock_exists, mock_cwd):
        """✓ Returns correct baseline directory path."""
        mock_cwd.return_value = "/project"
        
        path = VisualHandler.get_baseline_dir()
        
        assert "baselines" in path

    @patch("os.getcwd")
    @patch("os.path.exists", return_value=False)
    @patch("os.makedirs")
    def test_get_baseline_dir_creates_if_missing(self, mock_mkdir, mock_exists, mock_cwd):
        """✓ Creates baseline directory if it doesn't exist."""
        mock_cwd.return_value = "/project"
        
        VisualHandler.get_baseline_dir()
        
        mock_mkdir.assert_called_once()


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: BASELINE PATH CONSTRUCTION
# ═══════════════════════════════════════════════════════════════════════════════

class TestBaselinePath:
    """Tests for baseline path construction."""

    @patch.object(VisualHandler, 'get_baseline_dir', return_value="/baselines")
    def test_get_baseline_path_simple(self, mock_dir):
        """✓ Returns correct path for simple screenshot name."""
        path = VisualHandler.get_baseline_path("login_page")
        
        assert "login_page.png" in path
        assert path.endswith(".png")

    @patch.object(VisualHandler, 'get_baseline_dir', return_value="/baselines")
    def test_get_baseline_path_with_prefix(self, mock_dir):
        """✓ Includes prefix in baseline filename."""
        path = VisualHandler.get_baseline_path("header", baseline_prefix="desktop")
        
        assert "desktop_header.png" in path

    @patch.object(VisualHandler, 'get_baseline_dir', return_value="/baselines")
    def test_get_baseline_path_no_prefix(self, mock_dir):
        """✓ Works without prefix."""
        path = VisualHandler.get_baseline_path("footer", baseline_prefix=None)
        
        assert "footer.png" in path
        assert "None" not in path


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: IMAGE COMPARISON
# ═══════════════════════════════════════════════════════════════════════════════

class TestImageComparison:
    """Tests for image comparison functionality."""

    @patch("qa_framework.utils.visual.Image")
    @patch("qa_framework.utils.visual.ImageChops")
    @patch("qa_framework.utils.visual.ImageStat")
    def test_compare_images_identical(self, mock_stat, mock_chops, mock_image):
        """✓ Returns high similarity for identical images."""
        # Mock identical images
        mock_img = MagicMock()
        mock_img.size = (800, 600)
        mock_image.open.return_value.convert.return_value = mock_img
        
        # Mock RMS calculation (0 = identical)
        mock_stat_instance = MagicMock()
        mock_stat_instance.rms = [0, 0, 0]  # Perfect match
        mock_stat.Stat.return_value = mock_stat_instance
        
        similarity, is_match = VisualHandler.compare_images(
            "/current.png", "/baseline.png", threshold=5.0
        )
        
        assert similarity == 100.0
        assert is_match is True

    @patch("qa_framework.utils.visual.Image")
    @patch("qa_framework.utils.visual.ImageChops")
    @patch("qa_framework.utils.visual.ImageStat")
    def test_compare_images_with_differences(self, mock_stat, mock_chops, mock_image):
        """✓ Returns lower similarity for different images."""
        mock_img = MagicMock()
        mock_img.size = (800, 600)
        mock_image.open.return_value.convert.return_value = mock_img
        
        # Mock RMS with some difference
        mock_stat_instance = MagicMock()
        mock_stat_instance.rms = [25.5, 25.5, 25.5]  # ~10% difference
        mock_stat.Stat.return_value = mock_stat_instance
        
        similarity, is_match = VisualHandler.compare_images(
            "/current.png", "/baseline.png", threshold=5.0
        )
        
        assert similarity < 100.0
        assert is_match is False

    @patch("qa_framework.utils.visual.Image")
    @patch("qa_framework.utils.visual.ImageChops")
    @patch("qa_framework.utils.visual.ImageStat")
    def test_compare_images_within_threshold(self, mock_stat, mock_chops, mock_image):
        """✓ Returns match when within threshold."""
        mock_img = MagicMock()
        mock_img.size = (800, 600)
        mock_image.open.return_value.convert.return_value = mock_img
        
        # Small difference
        mock_stat_instance = MagicMock()
        mock_stat_instance.rms = [5, 5, 5]  # ~2% difference
        mock_stat.Stat.return_value = mock_stat_instance
        
        similarity, is_match = VisualHandler.compare_images(
            "/current.png", "/baseline.png", threshold=5.0
        )
        
        assert is_match is True


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: FULL VALIDATION WORKFLOW
# ═══════════════════════════════════════════════════════════════════════════════

class TestValidateVisual:
    """Tests for the complete validation workflow."""

    def test_validate_visual_disabled(self, mock_context):
        """✓ Skips validation when disabled."""
        mock_context.visual_config["enabled"] = False
        
        similarity, is_match = VisualHandler.validate_visual(
            mock_context, "test", "/current.png", threshold=5.0
        )
        
        assert similarity == 100.0
        assert is_match is True

    @patch.object(VisualHandler, 'get_baseline_path')
    @patch("os.path.exists", return_value=False)
    @patch("shutil.copy")
    def test_validate_visual_seeds_baseline(
        self, mock_copy, mock_exists, mock_path, mock_context
    ):
        """✓ Creates baseline when none exists."""
        mock_path.return_value = "/baselines/test.png"
        
        similarity, is_match = VisualHandler.validate_visual(
            mock_context, "test", "/current.png", threshold=5.0
        )
        
        mock_copy.assert_called_once()
        assert similarity == 100.0
        assert is_match is True

    @patch.object(VisualHandler, 'get_baseline_path')
    @patch.object(VisualHandler, 'compare_images')
    @patch("os.path.exists", return_value=True)
    def test_validate_visual_compares(
        self, mock_exists, mock_compare, mock_path, mock_context
    ):
        """✓ Compares images when baseline exists."""
        mock_path.return_value = "/baselines/test.png"
        mock_compare.return_value = (98.5, True)
        
        similarity, is_match = VisualHandler.validate_visual(
            mock_context, "test", "/current.png", threshold=5.0
        )
        
        assert similarity == 98.5
        assert is_match is True

    @patch.object(VisualHandler, 'get_baseline_path')
    @patch("os.path.exists", return_value=True)
    @patch("shutil.copy")
    def test_validate_visual_save_mode_updates(
        self, mock_copy, mock_exists, mock_path, mock_context
    ):
        """✓ Updates baseline when save mode is enabled."""
        mock_context.visual_config["save"] = True
        mock_path.return_value = "/baselines/test.png"
        
        similarity, is_match = VisualHandler.validate_visual(
            mock_context, "test", "/current.png", threshold=5.0
        )
        
        mock_copy.assert_called_once()
        assert similarity == 100.0


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5: CONFIGURATION OPTIONS
# ═══════════════════════════════════════════════════════════════════════════════

class TestConfiguration:
    """Tests for visual testing configuration options."""

    @patch.object(VisualHandler, 'get_baseline_path')
    @patch("os.path.exists", return_value=False)
    @patch("shutil.copy")
    def test_baseline_prefix_applied(
        self, mock_copy, mock_exists, mock_path, mock_context
    ):
        """✓ Uses baseline_name prefix from config."""
        mock_context.visual_config["baseline_name"] = "desktop"
        mock_path.return_value = "/baselines/desktop_test.png"
        
        VisualHandler.validate_visual(
            mock_context, "test", "/current.png", threshold=5.0
        )
        
        mock_path.assert_called_with("test", "desktop")


# ═══════════════════════════════════════════════════════════════════════════════
# RUN CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
