from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable

from conductor_demo.game.two_hand_mapping import MappingState, Section


LOGGER = logging.getLogger(__name__)

SECTION_CHANNELS = {
    # Derived from assets/audio/Symphony7_2.mid:
    # programs 73/68/71/70/69/69, 47, then 40/40/41/42/43.
    Section.STRINGS.value: [7, 8, 10, 11, 12],
    Section.WOODWINDS.value: [0, 1, 2, 3, 4, 5],
    Section.BRASS.value: [],
    Section.PERCUSSION.value: [6],
    Section.TUTTI.value: [],
}

MessageFactory = Callable[..., Any]
PortFactory = Callable[[str | None], Any]


def _load_mido() -> Any:
    try:
        import mido
    except ImportError as exc:
        raise RuntimeError(
            "MIDI output requires mido. Install with `pip install 'mido[ports-rtmidi]'`."
        ) from exc
    return mido


@dataclass(slots=True)
class MidiSectionOutput:
    enabled: bool = False
    port_name: str | None = None
    control_number: int = 11
    message_factory: MessageFactory | None = None
    port_factory: PortFactory | None = None
    _port: Any | None = None
    _last_values: dict[tuple[int, int], int] = field(default_factory=dict)

    def open(self) -> None:
        if not self.enabled or self._port is not None:
            return

        try:
            if self.port_factory is not None:
                self._port = self.port_factory(self.port_name)
            else:
                self._port = _load_mido().open_output(self.port_name)
        except Exception as exc:
            LOGGER.warning("MIDI output disabled: %s", exc)
            self.enabled = False
            self._port = None

    def close(self) -> None:
        if self._port is not None:
            self._port.close()
            self._port = None

    def apply(self, state: MappingState) -> None:
        if not self.enabled or self._port is None:
            return

        expression = int(state.section_expression.get(state.selected_section.value, 80))
        expression = max(0, min(127, expression))
        for channel in self._channels_for_section(state.selected_section):
            key = (channel, self.control_number)
            if self._last_values.get(key) == expression:
                continue

            self._port.send(self._message(channel=channel, value=expression))
            self._last_values[key] = expression

    def _message(self, *, channel: int, value: int) -> Any:
        factory = self.message_factory
        if factory is None:
            factory = _load_mido().Message
        return factory(
            "control_change",
            channel=channel,
            control=self.control_number,
            value=value,
        )

    def _channels_for_section(self, section: Section) -> list[int]:
        if section == Section.TUTTI:
            return sorted(
                {
                    channel
                    for section_name, channels in SECTION_CHANNELS.items()
                    if section_name != Section.TUTTI.value
                    for channel in channels
                }
            )
        return list(SECTION_CHANNELS.get(section.value, []))
