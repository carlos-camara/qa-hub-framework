"""
Page object elements module.
Provides typed element classes for page object pattern.
"""
from qa_framework.core.elements.base_element import WebElement
from qa_framework.core.elements.button import Button
from qa_framework.core.elements.buttons import Buttons
from qa_framework.core.elements.input import Input
from qa_framework.core.elements.text import Text
from qa_framework.core.elements.texts import Texts

__all__ = [
    'WebElement',
    'Button',
    'Buttons',
    'Input',
    'Text',
    'Texts',
]
