"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           QA Hub Framework                                    ║
║                          Element Unit Tests                                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Comprehensive test suite for all element classes:                           ║
║  • WebElement (base)    • Button     • Input     • Text                      ║
║  • Checkbox             • RadioButton/RadioGroup  • Link     • Select        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import pytest
from unittest.mock import MagicMock, patch
from selenium.webdriver.common.by import By


# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES - Shared test setup
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def mock_driver():
    """Create a mock Selenium WebDriver."""
    driver = MagicMock()
    mock_element = MagicMock()
    driver.find_element.return_value = mock_element
    driver.find_elements.return_value = [mock_element]
    return driver


@pytest.fixture
def mock_element():
    """Create a mock WebElement returned by find_element."""
    element = MagicMock()
    element.text = "Sample Text"
    element.is_displayed.return_value = True
    element.is_enabled.return_value = True
    element.is_selected.return_value = False
    element.get_attribute.return_value = "attribute_value"
    return element


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: BASE WEBELEMENT TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestWebElement:
    """Tests for the base WebElement class."""

    def test_initialization(self, mock_driver):
        """✓ WebElement initializes with driver, locator, and name."""
        from qa_framework.core.elements.base_element import WebElement
        
        locator = (By.ID, "test-element")
        element = WebElement(mock_driver, locator, "Test Element")
        
        assert element.driver == mock_driver
        assert element.locator == locator
        assert element.name == "Test Element"

    def test_click(self, mock_driver, mock_element):
        """✓ click() triggers click on the found element."""
        from qa_framework.core.elements.base_element import WebElement
        
        mock_driver.find_element.return_value = mock_element
        locator = (By.ID, "btn")
        element = WebElement(mock_driver, locator)
        
        with patch.object(element, '_find_element', return_value=mock_element):
            element.click()
        
        mock_element.click.assert_called_once()

    def test_get_text(self, mock_driver, mock_element):
        """✓ get_text() returns the element's text content."""
        from qa_framework.core.elements.base_element import WebElement
        
        mock_element.text = "Hello World"
        locator = (By.ID, "label")
        element = WebElement(mock_driver, locator)
        
        with patch.object(element, '_find_element', return_value=mock_element):
            text = element.get_text()
        
        assert text == "Hello World"

    def test_is_displayed(self, mock_driver, mock_element):
        """✓ is_displayed() returns element visibility status."""
        from qa_framework.core.elements.base_element import WebElement
        
        mock_element.is_displayed.return_value = True
        locator = (By.ID, "visible-el")
        element = WebElement(mock_driver, locator)
        
        with patch.object(element, '_find_element', return_value=mock_element):
            assert element.is_displayed() is True

    def test_get_attribute(self, mock_driver, mock_element):
        """✓ get_attribute() returns the specified attribute value."""
        from qa_framework.core.elements.base_element import WebElement
        
        mock_element.get_attribute.return_value = "https://example.com"
        locator = (By.ID, "link")
        element = WebElement(mock_driver, locator)
        
        with patch.object(element, '_find_element', return_value=mock_element):
            href = element.get_attribute("href")
        
        assert href == "https://example.com"
        mock_element.get_attribute.assert_called_with("href")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: BUTTON ELEMENT TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestButton:
    """Tests for the Button element class."""

    def test_button_inherits_webelement(self, mock_driver):
        """✓ Button inherits from WebElement."""
        from qa_framework.core.elements.button import Button
        from qa_framework.core.elements.base_element import WebElement
        
        btn = Button(mock_driver, (By.ID, "submit-btn"))
        assert isinstance(btn, WebElement)

    def test_is_enabled(self, mock_driver, mock_element):
        """✓ is_enabled() returns button's enabled state."""
        from qa_framework.core.elements.button import Button
        
        mock_element.is_enabled.return_value = True
        btn = Button(mock_driver, (By.ID, "submit"))
        
        with patch.object(btn, '_find_element', return_value=mock_element):
            assert btn.is_enabled() is True

    def test_get_text(self, mock_driver, mock_element):
        """✓ get_text() returns button label."""
        from qa_framework.core.elements.button import Button
        
        mock_element.text = "Submit Form"
        btn = Button(mock_driver, (By.ID, "submit"))
        
        with patch.object(btn, '_find_element', return_value=mock_element):
            assert btn.get_text() == "Submit Form"


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: INPUT ELEMENT TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestInput:
    """Tests for the Input element class."""

    def test_type_text(self, mock_driver, mock_element):
        """✓ type() sends keys to the input element."""
        from qa_framework.core.elements.input import Input
        
        inp = Input(mock_driver, (By.ID, "username"))
        
        with patch.object(inp, '_find_element', return_value=mock_element):
            inp.type("test_user")
        
        mock_element.send_keys.assert_called_with("test_user")

    def test_clear(self, mock_driver, mock_element):
        """✓ clear() clears the input content."""
        from qa_framework.core.elements.input import Input
        
        inp = Input(mock_driver, (By.ID, "email"))
        
        with patch.object(inp, '_find_element', return_value=mock_element):
            inp.clear()
        
        mock_element.clear.assert_called_once()

    def test_clear_and_type(self, mock_driver, mock_element):
        """✓ clear_and_type() clears then types new content."""
        from qa_framework.core.elements.input import Input
        
        inp = Input(mock_driver, (By.ID, "search"))
        
        with patch.object(inp, '_find_element', return_value=mock_element):
            inp.clear_and_type("new value")
        
        mock_element.clear.assert_called_once()
        mock_element.send_keys.assert_called_with("new value")

    def test_get_value(self, mock_driver, mock_element):
        """✓ get_value() returns the input's value attribute."""
        from qa_framework.core.elements.input import Input
        
        mock_element.get_attribute.return_value = "current_value"
        inp = Input(mock_driver, (By.ID, "field"))
        
        with patch.object(inp, '_find_element', return_value=mock_element):
            value = inp.get_value()
        
        assert value == "current_value"
        mock_element.get_attribute.assert_called_with("value")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: CHECKBOX ELEMENT TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestCheckbox:
    """Tests for the Checkbox element class."""

    def test_is_checked_when_selected(self, mock_driver, mock_element):
        """✓ is_checked() returns True when checkbox is selected."""
        from qa_framework.core.elements.checkbox import Checkbox
        
        mock_element.is_selected.return_value = True
        chk = Checkbox(mock_driver, (By.ID, "agree"))
        
        with patch.object(chk, '_find_element', return_value=mock_element):
            assert chk.is_checked() is True

    def test_is_checked_when_not_selected(self, mock_driver, mock_element):
        """✓ is_checked() returns False when checkbox is not selected."""
        from qa_framework.core.elements.checkbox import Checkbox
        
        mock_element.is_selected.return_value = False
        chk = Checkbox(mock_driver, (By.ID, "terms"))
        
        with patch.object(chk, '_find_element', return_value=mock_element):
            assert chk.is_checked() is False

    def test_check_when_unchecked(self, mock_driver, mock_element):
        """✓ check() clicks the checkbox when it's unchecked."""
        from qa_framework.core.elements.checkbox import Checkbox
        
        mock_element.is_selected.return_value = False
        chk = Checkbox(mock_driver, (By.ID, "newsletter"))
        
        with patch.object(chk, '_find_element', return_value=mock_element):
            with patch.object(chk, 'click') as mock_click:
                chk.check()
                mock_click.assert_called_once()

    def test_check_when_already_checked(self, mock_driver, mock_element):
        """✓ check() does nothing when checkbox is already checked."""
        from qa_framework.core.elements.checkbox import Checkbox
        
        mock_element.is_selected.return_value = True
        chk = Checkbox(mock_driver, (By.ID, "newsletter"))
        
        with patch.object(chk, '_find_element', return_value=mock_element):
            with patch.object(chk, 'click') as mock_click:
                chk.check()
                mock_click.assert_not_called()

    def test_uncheck_when_checked(self, mock_driver, mock_element):
        """✓ uncheck() clicks the checkbox when it's checked."""
        from qa_framework.core.elements.checkbox import Checkbox
        
        mock_element.is_selected.return_value = True
        chk = Checkbox(mock_driver, (By.ID, "marketing"))
        
        with patch.object(chk, '_find_element', return_value=mock_element):
            with patch.object(chk, 'click') as mock_click:
                chk.uncheck()
                mock_click.assert_called_once()

    def test_toggle(self, mock_driver, mock_element):
        """✓ toggle() always clicks the checkbox."""
        from qa_framework.core.elements.checkbox import Checkbox
        
        chk = Checkbox(mock_driver, (By.ID, "option"))
        
        with patch.object(chk, 'click') as mock_click:
            chk.toggle()
            mock_click.assert_called_once()

    def test_set_state_to_checked(self, mock_driver, mock_element):
        """✓ set_state(True) ensures checkbox is checked."""
        from qa_framework.core.elements.checkbox import Checkbox
        
        chk = Checkbox(mock_driver, (By.ID, "pref"))
        
        with patch.object(chk, 'check') as mock_check:
            chk.set_state(True)
            mock_check.assert_called_once()

    def test_set_state_to_unchecked(self, mock_driver, mock_element):
        """✓ set_state(False) ensures checkbox is unchecked."""
        from qa_framework.core.elements.checkbox import Checkbox
        
        chk = Checkbox(mock_driver, (By.ID, "pref"))
        
        with patch.object(chk, 'uncheck') as mock_uncheck:
            chk.set_state(False)
            mock_uncheck.assert_called_once()


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5: RADIO BUTTON ELEMENT TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestRadioButton:
    """Tests for the RadioButton element class."""

    def test_is_selected(self, mock_driver, mock_element):
        """✓ is_selected() returns selection state."""
        from qa_framework.core.elements.radio import RadioButton
        
        mock_element.is_selected.return_value = True
        radio = RadioButton(mock_driver, (By.ID, "gender-male"))
        
        with patch.object(radio, '_find_element', return_value=mock_element):
            assert radio.is_selected() is True

    def test_select_when_not_selected(self, mock_driver, mock_element):
        """✓ select() clicks radio when not already selected."""
        from qa_framework.core.elements.radio import RadioButton
        
        mock_element.is_selected.return_value = False
        radio = RadioButton(mock_driver, (By.ID, "payment-card"))
        
        with patch.object(radio, '_find_element', return_value=mock_element):
            with patch.object(radio, 'click') as mock_click:
                radio.select()
                mock_click.assert_called_once()

    def test_select_when_already_selected(self, mock_driver, mock_element):
        """✓ select() does nothing when already selected."""
        from qa_framework.core.elements.radio import RadioButton
        
        mock_element.is_selected.return_value = True
        radio = RadioButton(mock_driver, (By.ID, "payment-cash"))
        
        with patch.object(radio, '_find_element', return_value=mock_element):
            with patch.object(radio, 'click') as mock_click:
                radio.select()
                mock_click.assert_not_called()


class TestRadioGroup:
    """Tests for the RadioGroup utility class."""

    def test_get_options(self, mock_driver):
        """✓ get_options() returns all option values in the group."""
        from qa_framework.core.elements.radio import RadioGroup
        
        mock_radios = [MagicMock(), MagicMock(), MagicMock()]
        mock_radios[0].get_attribute.return_value = "option1"
        mock_radios[1].get_attribute.return_value = "option2"
        mock_radios[2].get_attribute.return_value = "option3"
        mock_driver.find_elements.return_value = mock_radios
        
        group = RadioGroup(mock_driver, "payment_method")
        options = group.get_options()
        
        assert options == ["option1", "option2", "option3"]

    def test_get_selected_value(self, mock_driver):
        """✓ get_selected_value() returns the selected option's value."""
        from qa_framework.core.elements.radio import RadioGroup
        
        mock_radios = [MagicMock(), MagicMock()]
        mock_radios[0].is_selected.return_value = False
        mock_radios[1].is_selected.return_value = True
        mock_radios[1].get_attribute.return_value = "selected_option"
        mock_driver.find_elements.return_value = mock_radios
        
        group = RadioGroup(mock_driver, "size")
        assert group.get_selected_value() == "selected_option"

    def test_get_selected_value_none_selected(self, mock_driver):
        """✓ get_selected_value() returns None when nothing is selected."""
        from qa_framework.core.elements.radio import RadioGroup
        
        mock_radios = [MagicMock(), MagicMock()]
        mock_radios[0].is_selected.return_value = False
        mock_radios[1].is_selected.return_value = False
        mock_driver.find_elements.return_value = mock_radios
        
        group = RadioGroup(mock_driver, "color")
        assert group.get_selected_value() is None


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6: LINK ELEMENT TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestLink:
    """Tests for the Link element class."""

    def test_get_href(self, mock_driver, mock_element):
        """✓ get_href() returns the link's href attribute."""
        from qa_framework.core.elements.link import Link
        
        mock_element.get_attribute.return_value = "https://example.com/page"
        link = Link(mock_driver, (By.ID, "nav-link"))
        
        with patch.object(link, '_find_element', return_value=mock_element):
            with patch.object(link, 'get_attribute', return_value="https://example.com/page"):
                href = link.get_href()
        
        assert href == "https://example.com/page"

    def test_get_target(self, mock_driver, mock_element):
        """✓ get_target() returns the link's target attribute."""
        from qa_framework.core.elements.link import Link
        
        link = Link(mock_driver, (By.ID, "external-link"))
        
        with patch.object(link, 'get_attribute', return_value="_blank"):
            target = link.get_target()
        
        assert target == "_blank"

    def test_opens_in_new_tab(self, mock_driver, mock_element):
        """✓ opens_in_new_tab() returns True when target is _blank."""
        from qa_framework.core.elements.link import Link
        
        link = Link(mock_driver, (By.ID, "ext"))
        
        with patch.object(link, 'get_target', return_value="_blank"):
            assert link.opens_in_new_tab() is True

    def test_is_download_link(self, mock_driver, mock_element):
        """✓ is_download_link() returns True when download attribute exists."""
        from qa_framework.core.elements.link import Link
        
        mock_element.get_attribute.return_value = "file.pdf"
        link = Link(mock_driver, (By.ID, "download-link"))
        
        with patch.object(link, '_find_element', return_value=mock_element):
            result = link.is_download_link()
        
        assert result is True


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7: SELECT ELEMENT TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestSelect:
    """Tests for the Select element class."""

    def test_inherits_webelement(self, mock_driver):
        """✓ Select inherits from WebElement."""
        from qa_framework.core.elements.select import Select
        from qa_framework.core.elements.base_element import WebElement
        
        select = Select(mock_driver, (By.ID, "country"))
        assert isinstance(select, WebElement)

    @patch("qa_framework.core.elements.select.SeleniumSelect")
    def test_select_by_visible_text(self, mock_selenium_select, mock_driver, mock_element):
        """✓ select_by_visible_text() delegates to Selenium Select."""
        from qa_framework.core.elements.select import Select
        
        mock_select_instance = MagicMock()
        mock_selenium_select.return_value = mock_select_instance
        
        select = Select(mock_driver, (By.ID, "state"))
        
        with patch.object(select, '_find_element', return_value=mock_element):
            with patch.object(select, 'wait_until_visible'):
                select.select_by_visible_text("California")
        
        mock_select_instance.select_by_visible_text.assert_called_with("California")

    @patch("qa_framework.core.elements.select.SeleniumSelect")
    def test_select_by_value(self, mock_selenium_select, mock_driver, mock_element):
        """✓ select_by_value() delegates to Selenium Select."""
        from qa_framework.core.elements.select import Select
        
        mock_select_instance = MagicMock()
        mock_selenium_select.return_value = mock_select_instance
        
        select = Select(mock_driver, (By.ID, "priority"))
        
        with patch.object(select, '_find_element', return_value=mock_element):
            with patch.object(select, 'wait_until_visible'):
                select.select_by_value("high")
        
        mock_select_instance.select_by_value.assert_called_with("high")

    @patch("qa_framework.core.elements.select.SeleniumSelect")
    def test_get_selected_text(self, mock_selenium_select, mock_driver, mock_element):
        """✓ get_selected_text() returns first selected option text."""
        from qa_framework.core.elements.select import Select
        
        mock_option = MagicMock()
        mock_option.text = "United States"
        mock_select_instance = MagicMock()
        mock_select_instance.first_selected_option = mock_option
        mock_selenium_select.return_value = mock_select_instance
        
        select = Select(mock_driver, (By.ID, "country"))
        
        with patch.object(select, '_find_element', return_value=mock_element):
            result = select.get_selected_text()
        
        assert result == "United States"

    @patch("qa_framework.core.elements.select.SeleniumSelect")
    def test_get_all_options_text(self, mock_selenium_select, mock_driver, mock_element):
        """✓ get_all_options_text() returns list of option texts."""
        from qa_framework.core.elements.select import Select
        
        mock_opts = [MagicMock(), MagicMock()]
        mock_opts[0].text = "Option A"
        mock_opts[1].text = "Option B"
        mock_select_instance = MagicMock()
        mock_select_instance.options = mock_opts
        mock_selenium_select.return_value = mock_select_instance
        
        select = Select(mock_driver, (By.ID, "choices"))
        
        with patch.object(select, '_find_element', return_value=mock_element):
            options = select.get_all_options_text()
        
        assert options == ["Option A", "Option B"]


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8: ELEMENT FACTORY TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestElementFactory:
    """Tests for the ElementFactory class."""

    def test_create_button(self, mock_driver):
        """✓ ElementFactory creates Button for type='button'."""
        from qa_framework.core.element_factory import ElementFactory
        from qa_framework.core.elements.button import Button
        
        element = ElementFactory.create(
            driver=mock_driver,
            element_type='button',
            locator_data={'by': 'id', 'value': 'submit-btn'},
            element_name='Submit'
        )
        
        assert isinstance(element, Button)

    def test_create_input(self, mock_driver):
        """✓ ElementFactory creates Input for type='input'."""
        from qa_framework.core.element_factory import ElementFactory
        from qa_framework.core.elements.input import Input
        
        element = ElementFactory.create(
            driver=mock_driver,
            element_type='input',
            locator_data={'by': 'css', 'value': '#email'},
            element_name='Email Field'
        )
        
        assert isinstance(element, Input)

    def test_create_checkbox(self, mock_driver):
        """✓ ElementFactory creates Checkbox for type='checkbox'."""
        from qa_framework.core.element_factory import ElementFactory
        from qa_framework.core.elements.checkbox import Checkbox
        
        element = ElementFactory.create(
            driver=mock_driver,
            element_type='checkbox',
            locator_data={'by': 'id', 'value': 'agree'},
            element_name='Agreement'
        )
        
        assert isinstance(element, Checkbox)

    def test_create_radio(self, mock_driver):
        """✓ ElementFactory creates RadioButton for type='radio'."""
        from qa_framework.core.element_factory import ElementFactory
        from qa_framework.core.elements.radio import RadioButton
        
        element = ElementFactory.create(
            driver=mock_driver,
            element_type='radio',
            locator_data={'by': 'id', 'value': 'option-a'},
            element_name='Option A'
        )
        
        assert isinstance(element, RadioButton)

    def test_create_link(self, mock_driver):
        """✓ ElementFactory creates Link for type='link'."""
        from qa_framework.core.element_factory import ElementFactory
        from qa_framework.core.elements.link import Link
        
        element = ElementFactory.create(
            driver=mock_driver,
            element_type='link',
            locator_data={'by': 'css', 'value': 'a.nav-item'},
            element_name='Navigation Link'
        )
        
        assert isinstance(element, Link)

    def test_create_select(self, mock_driver):
        """✓ ElementFactory creates Select for type='select'."""
        from qa_framework.core.element_factory import ElementFactory
        from qa_framework.core.elements.select import Select
        
        element = ElementFactory.create(
            driver=mock_driver,
            element_type='select',
            locator_data={'by': 'id', 'value': 'country-dropdown'},
            element_name='Country'
        )
        
        assert isinstance(element, Select)

    def test_unknown_element_type_raises_error(self, mock_driver):
        """✓ ElementFactory raises ValueError for unknown types."""
        from qa_framework.core.element_factory import ElementFactory
        
        with pytest.raises(ValueError, match="Unknown element type"):
            ElementFactory.create(
                driver=mock_driver,
                element_type='unknown_type',
                locator_data={'by': 'id', 'value': 'test'}
            )

    def test_unknown_locator_type_raises_error(self, mock_driver):
        """✓ ElementFactory raises ValueError for unknown locator types."""
        from qa_framework.core.element_factory import ElementFactory
        
        with pytest.raises(ValueError, match="Unknown locator type"):
            ElementFactory.create(
                driver=mock_driver,
                element_type='button',
                locator_data={'by': 'invalid_by', 'value': 'test'}
            )

    def test_register_custom_element(self, mock_driver):
        """✓ register_custom_element() allows adding custom types."""
        from qa_framework.core.element_factory import ElementFactory
        from qa_framework.core.elements.base_element import WebElement
        
        class CustomElement(WebElement):
            pass
        
        ElementFactory.register_custom_element('custom', CustomElement)
        
        element = ElementFactory.create(
            driver=mock_driver,
            element_type='custom',
            locator_data={'by': 'id', 'value': 'test'}
        )
        
        assert isinstance(element, CustomElement)
        
        # Cleanup: Remove custom element from registry
        del ElementFactory.ELEMENT_TYPE_MAP['custom']


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 9: TEXT ELEMENT TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestText:
    """Tests for the Text element class."""

    def test_get_text(self, mock_driver, mock_element):
        """✓ get_text() returns the element's text content."""
        from qa_framework.core.elements.text import Text
        
        mock_element.text = "Important Message"
        text_el = Text(mock_driver, (By.ID, "message"))
        
        with patch.object(text_el, '_find_element', return_value=mock_element):
            assert text_el.get_text() == "Important Message"


# ═══════════════════════════════════════════════════════════════════════════════
# RUN CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
