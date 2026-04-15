from __future__ import annotations


class FallbackControls:
    """Keyboard fallback controls for the live demo."""

    def __init__(self, keymap: dict[str, str]) -> None:
        self.keymap = keymap
        self._code_map = {self._normalize_key(key): action for key, action in keymap.items()}

    def describe(self) -> str:
        labels = []
        for key, action in self.keymap.items():
            labels.append(f"{key.upper()} {action}")
        return " | ".join(labels)

    def resolve(self, key: str) -> str | None:
        return self.keymap.get(key.lower())

    def resolve_keycode(self, key_code: int) -> str | None:
        return self._code_map.get(key_code)

    def _normalize_key(self, key: str) -> int:
        token = key.lower()
        if token == "space":
            return 32
        if token == "esc":
            return 27
        if len(token) == 1:
            return ord(token)
        raise ValueError(f"Unsupported key token: {key}")
