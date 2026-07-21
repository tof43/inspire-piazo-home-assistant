"""Light platform for Inspire Piazo."""

from typing import Any

from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
from homeassistant.const import STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from . import InspirePiazoConfigEntry
from .const import DOMAIN
from .controller import InspirePiazoController
from .protocol import PiazoCommand, quantize_brightness

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: InspirePiazoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Inspire Piazo light platform."""
    async_add_entities([InspirePiazoLight(entry, entry.runtime_data)])


class InspirePiazoLight(RestoreEntity, LightEntity):
    """Representation of an Inspire Piazo ceiling light."""

    _attr_assumed_state = True
    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_has_entity_name = True
    _attr_icon = "mdi:ceiling-light"
    _attr_name = None
    _attr_should_poll = False
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}

    def __init__(
        self,
        entry: InspirePiazoConfigEntry,
        controller: InspirePiazoController,
    ) -> None:
        """Initialize the light."""
        self._controller = controller
        self._attr_unique_id = f"{controller.remote_code.lower()}_light"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, controller.remote_code)},
            manufacturer="Inspire",
            model="Piazo",
            name=entry.title,
        )
        self._attr_is_on = False
        self._attr_brightness = 255

    async def async_added_to_hass(self) -> None:
        """Restore the optimistic state after a Home Assistant restart."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state is None:
            return

        self._attr_is_on = last_state.state == STATE_ON
        restored_brightness = last_state.attributes.get(ATTR_BRIGHTNESS)
        if isinstance(restored_brightness, int) and 1 <= restored_brightness <= 255:
            self._attr_brightness = restored_brightness

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light or select the nearest brightness preset."""
        requested_brightness = kwargs.get(ATTR_BRIGHTNESS)

        if requested_brightness is not None:
            if requested_brightness <= 0:
                await self.async_turn_off()
                return

            command, effective_brightness = quantize_brightness(requested_brightness)
            await self._controller.async_send(command)
            self._attr_brightness = effective_brightness
        else:
            await self._controller.async_send(PiazoCommand.ON)

        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        await self._controller.async_send(PiazoCommand.OFF)
        self._attr_is_on = False
        self.async_write_ha_state()
