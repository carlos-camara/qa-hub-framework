"""
Page object elements module.
Provides typed element classes for the Page Object pattern.

Includes:
- WebElement: Base class with common methods
- Button/Buttons: Click-able button elements
- Input: Text input fields
- Checkbox: Checkable elements with check/uncheck/toggle
- RadioButton/RadioGroup: Radio button selection
- Link: Anchor elements with href inspection
- Select: Dropdown elements with option selection
- Text/Texts: Read-only text elements
"""
from qa_framework.core.elements.base_element import WebElement
from qa_framework.core.elements.button import Button
from qa_framework.core.elements.buttons import Buttons
from qa_framework.core.elements.input import Input
from qa_framework.core.elements.checkbox import Checkbox
from qa_framework.core.elements.radio import RadioButton, RadioGroup
from qa_framework.core.elements.link import Link
from qa_framework.core.elements.select import Select
from qa_framework.core.elements.text import Text
from qa_framework.core.elements.texts import Texts

__all__ = [
    # Base
    'WebElement',
    # Interactive
    'Button',
    'Buttons',
    'Input',
    'Checkbox',
    'RadioButton',
    'RadioGroup',
    'Link',
    'Select',
    # Read-only
    'Text',
    'Texts',
]
