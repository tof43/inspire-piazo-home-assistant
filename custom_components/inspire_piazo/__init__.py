"""The Inspire Piazo integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import CONF_REMOTE_CODE, RFXTRX_DOMAIN, RFXTRX_SEND_ACTION
from .controller import InspirePiazoController

PLATFORMS: list[Platform] = [Platform.LIGHT]

type InspirePiazoConfigEntry = ConfigEntry[InspirePiazoController]


async def async_setup_entry(
    hass: HomeAssistant, entry: InspirePiazoConfigEntry
) -> bool:
    """Set up Inspire Piazo from a config entry."""
    if not hass.services.has_service(RFXTRX_DOMAIN, RFXTRX_SEND_ACTION):
        raise ConfigEntryNotReady("The RFXtrx send action is not available")

    entry.runtime_data = InspirePiazoController(
        hass=hass,
        remote_code=entry.data[CONF_REMOTE_CODE],
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: InspirePiazoConfigEntry
) -> bool:
    """Unload an Inspire Piazo config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
