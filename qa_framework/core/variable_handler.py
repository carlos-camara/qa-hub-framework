import re
import random
import string
import uuid
import json
import os
from datetime import datetime, timedelta
from typing import Any, Optional, Dict

class VariableHandler:
    """
    Handles variable transformation and dynamic data generation from string tokens.
    Usage: [UUID], [NOW + 2 DAYS], [INT:123], etc.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.dataset = self.config.get("dataset", {})

    def resolve(self, text: str) -> Any:
        """Resolve a tokenized string to its transformed value."""
        if not isinstance(text, str) or "[" not in text or "]" not in text:
            return text

        # Handle nested tokens recursively: [STR:[INT:123]]
        # We find the innermost [...] and resolve it first
        while "[" in str(text) and "]" in str(text):
            match = re.search(r"\[([^\[\]]+)\]", str(text))
            if not match:
                break
            
            full_match = match.group(0) # [TOKEN]
            inner_content = match.group(1) # TOKEN
            
            resolved_inner = self._resolve_single_token(inner_content)
            
            # If resolved_inner is not a string (e.g., None, True, int), 
            # and it was the ONLY thing in text, return it directly.
            if str(text) == full_match:
                return resolved_inner
            
            # Otherwise, replace and continue
            text = text.replace(full_match, str(resolved_inner))
            
        return text

    def _resolve_single_token(self, token: str) -> Any:
        """Internal method to resolve a single token without brackets."""
        # 1. Basic Constants
        constants = {
            "MISSING_PARAM": None,
            "NULL": None,
            "TRUE": True,
            "FALSE": False,
            "EMPTY": "",
            "B": " ",
            "SHARP": "#",
            "UUID": lambda: str(uuid.uuid4()),
            "RANDOM": lambda: str(random.randint(1000, 9999)),
            "TIMESTAMP": lambda: str(int(datetime.now().timestamp())),
            "DATETIME": lambda: datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

        if token in constants:
            val = constants[token]
            return val() if callable(val) else val

        # 2. String/Integer with length
        match = re.match(r"(STRING|INTEGER)_WITH_LENGTH_(\d+)", token)
        if match:
            type_name, length = match.groups()
            length = int(length)
            if type_name == "STRING":
                return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
            else:
                return ''.join(random.choices(string.digits, k=length))

        # 3. Arrays with length
        match = re.match(r"(STRING|INTEGER)_ARRAY_WITH_LENGTH_(\d+)", token)
        if match:
            type_name, length = match.groups()
            length = int(length)
            if type_name == "STRING":
                return [''.join(random.choices(string.ascii_letters, k=5)) for _ in range(length)]
            else:
                return [random.randint(0, 100) for _ in range(length)]

        # 4. JSON with length
        match = re.match(r"JSON_WITH_LENGTH_(\d+)", token)
        if match:
            length = int(match.group(1))
            data = {f"key_{i}": f"val_{i}" for i in range(length)}
            return json.dumps(data)

        # 5. Temporal (NOW/TODAY) with offsets and formats
        # Pattern: (NOW|TODAY)(\((.*?)\))?\s?([+-]\s?\d+\s?\w+)?
        # Example: [NOW(%Y-%m) + 2 DAYS]
        if token.startswith("NOW") or token.startswith("TODAY"):
            return self._resolve_temporal(token)

        # 6. Random Phone Number
        if token == "RANDOM_PHONE_NUMBER":
            lang = self.dataset.get("language", "en")
            country = self.dataset.get("country", "US")
            # Simple placeholder for now - could be expanded
            return f"+1{random.randint(200, 999)}{random.randint(200, 999)}{random.randint(1000, 9999)}"

        # 7. Functional Transformations (Wrappers)
        # Format: [TYPE:content] or [FUNCTION:content::args]
        if ":" in token:
            return self._resolve_functional(token)

        return text

    def _resolve_temporal(self, token: str) -> str:
        base_time = datetime.now()
        is_today = token.startswith("TODAY")
        
        # Default formats
        fmt = "%Y-%m-%d" if is_today else "%Y-%m-%dT%H:%M:%SZ"
        
        # Extract custom format if present: NOW(format)
        fmt_match = re.search(r"\((.*?)\)", token)
        if fmt_match:
            fmt = fmt_match.group(1)
            # Support %3f or %6f for microseconds
            if "%3f" in fmt:
                ms = base_time.strftime("%f")[:3]
                fmt = fmt.replace("%3f", ms)
            if "%6f" in fmt:
                ms = base_time.strftime("%f")
                fmt = fmt.replace("%6f", ms)

        # Extract offset: + 2 DAYS, - 1 MINUTES, etc.
        offset_match = re.search(r"([+-])\s?(\d+)\s?(\w+)", token)
        if offset_match:
            op, val, unit = offset_match.groups()
            val = int(val)
            unit = unit.lower()
            if not unit.endswith("s"): unit += "s"
            
            delta_kwargs = {unit: val if op == "+" else -val}
            try:
                base_time += timedelta(**delta_kwargs)
            except TypeError:
                pass # Invalid unit

        return base_time.strftime(fmt)

    def _resolve_functional(self, token: str) -> Any:
        parts = token.split(":", 1)
        func_name = parts[0].upper()
        content = parts[1]

        if func_name == "STR": return str(content)
        if func_name == "INT": return int(content)
        if func_name == "FLOAT": return float(content)
        if func_name == "LIST": 
            try: return json.loads(content.replace("'", '"'))
            except: return content.split(",")
        if func_name == "DICT": return json.loads(content.replace("'", '"'))
        if func_name == "UPPER": return content.upper()
        if func_name == "LOWER": return content.lower()
        if func_name == "TITLE": return content.title()
        
        # ROUND:xxxx::N
        if func_name == "ROUND":
            sub_parts = content.split("::")
            if len(sub_parts) == 2:
                return round(float(sub_parts[0]), int(sub_parts[1]))
            return round(float(content))

        # REPLACE:xxxx::OLD::NEW
        if func_name == "REPLACE":
            sub_parts = content.split("::")
            if len(sub_parts) == 3:
                return sub_parts[0].replace(sub_parts[1], sub_parts[2])
            return content

        return f"[{token}]"
