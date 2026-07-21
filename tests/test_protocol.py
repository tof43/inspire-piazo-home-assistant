"""Tests for the RF protocol helpers without requiring Home Assistant."""

import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = (
    Path(__file__).parents[1] / "custom_components" / "inspire_piazo" / "protocol.py"
)
SPEC = importlib.util.spec_from_file_location("inspire_piazo_protocol", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
PROTOCOL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROTOCOL)


class ProtocolTest(unittest.TestCase):
    """Verify packet generation and brightness mapping."""

    def test_normalize_remote_code(self) -> None:
        self.assertEqual(PROTOCOL.normalize_remote_code(" f120 "), "F120")
        self.assertEqual(PROTOCOL.normalize_remote_code("0xF120"), "F120")

    def test_reject_invalid_remote_code(self) -> None:
        for value in ("", "F12", "F12001", "ZZZZ"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                PROTOCOL.normalize_remote_code(value)

    def test_build_known_packets(self) -> None:
        expected_packets = {
            PROTOCOL.PiazoCommand.ON: "09130000F12001018600",
            PROTOCOL.PiazoCommand.OFF: "09130000F12003018600",
            PROTOCOL.PiazoCommand.BRIGHTNESS_30: "09130000F1200F018600",
            PROTOCOL.PiazoCommand.BRIGHTNESS_50: "09130000F1200E018600",
            PROTOCOL.PiazoCommand.BRIGHTNESS_75: "09130000F12010018600",
            PROTOCOL.PiazoCommand.BRIGHTNESS_100: "09130000F12012018600",
        }
        for command, expected in expected_packets.items():
            with self.subTest(command=command):
                self.assertEqual(PROTOCOL.build_rfxtrx_event("F120", command), expected)

    def test_quantize_brightness(self) -> None:
        cases = {
            1: (PROTOCOL.PiazoCommand.BRIGHTNESS_30, 76),
            102: (PROTOCOL.PiazoCommand.BRIGHTNESS_30, 76),
            103: (PROTOCOL.PiazoCommand.BRIGHTNESS_30, 76),
            104: (PROTOCOL.PiazoCommand.BRIGHTNESS_50, 128),
            159: (PROTOCOL.PiazoCommand.BRIGHTNESS_50, 128),
            160: (PROTOCOL.PiazoCommand.BRIGHTNESS_75, 191),
            223: (PROTOCOL.PiazoCommand.BRIGHTNESS_75, 191),
            224: (PROTOCOL.PiazoCommand.BRIGHTNESS_100, 255),
            255: (PROTOCOL.PiazoCommand.BRIGHTNESS_100, 255),
        }
        for brightness, expected in cases.items():
            with self.subTest(brightness=brightness):
                self.assertEqual(PROTOCOL.quantize_brightness(brightness), expected)

    def test_reject_invalid_brightness(self) -> None:
        for value in (0, 256):
            with self.subTest(value=value), self.assertRaises(ValueError):
                PROTOCOL.quantize_brightness(value)


if __name__ == "__main__":
    unittest.main()
