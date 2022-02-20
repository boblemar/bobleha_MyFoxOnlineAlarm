from __future__ import annotations
from typing import Any, Final, final

import logging

from numpy import typename


from homeassistant.components.alarm_control_panel import (
    PLATFORM_SCHEMA_BASE,
    AlarmControlPanelEntity,
    SUPPORT_ALARM_ARM_HOME,
    SUPPORT_ALARM_ARM_AWAY,
    FORMAT_NUMBER,
)

from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_CODE,
    STATE_ALARM_DISARMING,
    STATE_ALARM_ARMING,
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_CUSTOM_BYPASS,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_ARMED_NIGHT,
    STATE_ALARM_ARMED_VACATION,
    STATE_ALARM_DISARMED,
    STATE_ALARM_TRIGGERED,
)


from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.config_entries import ConfigEntry

from homeassistant.helpers import config_validation as cv
from homeassistant.const import CONF_FRIENDLY_NAME, CONF_IP_ADDRESS, CONF_NAME

import voluptuous as vol

from .MyFoxOnline import MyFoxOnline, Status
from .const import *

DOMAIN = "bobleha_MyFoxOnlineAlarm"

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA_BASE = PLATFORM_SCHEMA_BASE.extend(
    {
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_CODE): cv.string,
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType = None,
) -> None:
    """Set up the bobleha_relaiswifi platform."""
    # Assign configuration variables.
    # The configuration check takes care they are present.
    username = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]
    code = config[CONF_CODE]

    entity = bobleha_MyFoxAlarm(username, password, code)
    add_entities([entity])


class bobleha_MyFoxAlarm(AlarmControlPanelEntity):

    _supported_features: int = SUPPORT_ALARM_ARM_HOME | SUPPORT_ALARM_ARM_AWAY
    _code_format: str = FORMAT_NUMBER

    def __init__(self, username: str, password: str, code: str) -> None:
        self.__myfox = MyFoxOnline(username, password)
        self._code: str = code

    @property
    def state(self) -> str:
        """Return the state of the alarm."""
        status = self.__myfox.get_state()

        if status == Status.DISARMING:
            return STATE_ALARM_DISARMING

        if status == Status.ARMING:
            return STATE_ALARM_ARMING

        if status == Status.DISARMED:
            return STATE_ALARM_DISARMED

        if status == Status.FULL:
            return STATE_ALARM_ARMED_AWAY

        if status == Status.PARTIAL:
            return STATE_ALARM_ARMED_NIGHT

    @property
    def code_format(self) -> str:
        """Regex for code format or None if no code is required."""
        return self._code_format

    @property
    def changed_by(self) -> str:
        """Last change triggered by."""
        return self._attr_changed_by

    @property
    def code_arm_required(self):
        """Whether the code is required for arm actions."""
        return True

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return self._supported_features

    def alarm_disarm(self, code: str | None = None) -> None:
        """Send disarm command."""
        if str(code) == str(self._code):
            self.__myfox.set_state(Status.DISARMED)
            self.schedule_update_ha_state()

    async def async_alarm_disarm(self, code: str | None = None) -> None:
        """Send disarm command."""
        await self.hass.async_add_executor_job(self.alarm_disarm, code)

    def alarm_arm_home(self, code: str | None = None) -> None:
        """Send arm home command."""
        if str(code) == str(self._code):
            self.__myfox.set_state(Status.PARTIAL)
            self.schedule_update_ha_state()

    async def async_alarm_arm_home(self, code: str | None = None) -> None:
        """Send arm home command."""
        await self.hass.async_add_executor_job(self.alarm_arm_home, code)

    def alarm_arm_away(self, code: str | None = None) -> None:
        """Send arm away command."""
        if str(code) == str(self._code):
            self.__myfox.set_state(Status.FULL)
            self.schedule_update_ha_state()

    async def async_alarm_arm_away(self, code: str | None = None) -> None:
        """Send arm away command."""
        await self.hass.async_add_executor_job(self.alarm_arm_away, code)

    def alarm_arm_night(self, code: str | None = None) -> None:
        """Send arm night command."""
        raise NotImplementedError()

    async def async_alarm_arm_night(self, code: str | None = None) -> None:
        """Send arm night command."""
        raise NotImplementedError()

    def alarm_arm_vacation(self, code: str | None = None) -> None:
        """Send arm vacation command."""
        raise NotImplementedError()

    async def async_alarm_arm_vacation(self, code: str | None = None) -> None:
        """Send arm vacation command."""
        raise NotImplementedError()

    def alarm_trigger(self, code: str | None = None) -> None:
        """Send alarm trigger command."""
        raise NotImplementedError()

    async def async_alarm_trigger(self, code: str | None = None) -> None:
        """Send alarm trigger command."""
        raise NotImplementedError()

    def alarm_arm_custom_bypass(self, code: str | None = None) -> None:
        """Send arm custom bypass command."""
        raise NotImplementedError()

    async def async_alarm_arm_custom_bypass(self, code: str | None = None) -> None:
        """Send arm custom bypass command."""
        raise NotImplementedError()
