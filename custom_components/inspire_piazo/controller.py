"""RFXtrx controller for an Inspire Piazo ceiling light."""

from dataclasses import dataclass

from homeassistant.core import HomeAssistant

from .const import RFXTRX_DOMAIN, RFXTRX_SEND_ACTION
from .protocol import PiazoCommand, build_rfxtrx_event


@dataclass(slots=True)
class InspirePiazoController:
    """Send commands for one paired Inspire Piazo remote code."""

    hass: HomeAssistant
    remote_code: str

    async def async_send(self, command: PiazoCommand) -> None:
        """Send one command through the configured RFXtrx integration."""
        await self.hass.services.async_call(
            RFXTRX_DOMAIN,
            RFXTRX_SEND_ACTION,
            {"event": build_rfxtrx_event(self.remote_code, command)},
            blocking=True,
        )
