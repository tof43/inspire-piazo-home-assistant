"""Inspire Piazo RF protocol helpers."""

import re
from enum import StrEnum

_REMOTE_CODE_PATTERN = re.compile(r"^[0-9A-F]{4}$")


class PiazoCommand(StrEnum):
    """Known command bytes from the Inspire Piazo remote."""

    ON = "01"
    OFF = "03"
    DIM_UP = "05"
    DIM_DOWN = "0B"
    BRIGHTNESS_30 = "0F"
    BRIGHTNESS_50 = "0E"
    BRIGHTNESS_75 = "10"
    BRIGHTNESS_100 = "12"
    KELVIN_UP = "09"
    KELVIN_DOWN = "04"


_BRIGHTNESS_COMMANDS = (
    (40, 30, PiazoCommand.BRIGHTNESS_30),
    (62, 50, PiazoCommand.BRIGHTNESS_50),
    (87, 75, PiazoCommand.BRIGHTNESS_75),
    (100, 100, PiazoCommand.BRIGHTNESS_100),
)


def normalize_remote_code(value: str) -> str:
    """Normalize and validate the 16-bit remote identifier."""
    remote_code = value.strip().upper()
    if remote_code.startswith("0X"):
        remote_code = remote_code[2:]

    if not _REMOTE_CODE_PATTERN.fullmatch(remote_code):
        raise ValueError("remote code must contain exactly four hexadecimal digits")

    return remote_code


def build_rfxtrx_event(remote_code: str, command: PiazoCommand) -> str:
    """Build a Lighting4/PT2262 RFXtrx packet with a 390 us pulse."""
    normalized_code = normalize_remote_code(remote_code)
    return f"09130000{normalized_code}{command.value}018600"


def quantize_brightness(brightness: int) -> tuple[PiazoCommand, int]:
    """Map Home Assistant brightness to a supported Piazo preset.

    Return the RF command and the effective Home Assistant brightness.
    """
    if not 1 <= brightness <= 255:
        raise ValueError("brightness must be between 1 and 255")

    requested_percent = round(brightness * 100 / 255)
    for upper_bound, preset_percent, command in _BRIGHTNESS_COMMANDS:
        if requested_percent <= upper_bound:
            effective_brightness = round(preset_percent * 255 / 100)
            return command, effective_brightness

    raise AssertionError("brightness mapping is incomplete")
