import json
from enum import IntFlag
from typing import Dict

from .device_properties import DeviceProperties


class DeviceCommunicationError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class EffectiveFlags(IntFlag):
    Update = 0
    Power = 1


class Device:
    """
    Represents an Ecodan Heat Pump device
    """
    def __init__(self, client: "Client", state: Dict):
        self._client = client
        self._state = state

    @property
    def name(self):
        return self._state[DeviceProperties.DeviceName]

    @property
    def flow_temperature(self):
        return self._device_properties[DeviceProperties.FlowTemperature]

    @property
    def _device_id(self):
        return self._state[DeviceProperties.DeviceID]

    @property
    def _building_id(self):
        return self._state[DeviceProperties.BuildingID]

    @property
    def _device_properties(self) -> Dict:
        return self._state["Device"]

    async def _request(self, effective_flags: EffectiveFlags, **kwargs) -> Dict:
        state = {
            DeviceProperties.BuildingID: self._building_id,
            DeviceProperties.DeviceID: self._device_id,
            DeviceProperties.EffectiveFlags: effective_flags
        }
        state.update(kwargs)
        return await self._client.device_request("SetAtw", state)

    async def power_on(self) -> None:
        """
        Turn on the Heat Pump. Performs the same task as the `On` switch in the MELCloud interface
        """
        response_state = await self._request(EffectiveFlags.Power, Power=True)
        if not response_state[DeviceProperties.Power]:
            raise DeviceCommunicationError("Power could not be set")

        self._device_properties.update(response_state)

    async def power_off(self) -> None:
        """
        Turn off the Heat Pump. Performs the same task as the `Off` switch in the MELCloud interface
        """
        response_state = await self._request(EffectiveFlags.Power, Power=False)
        if response_state[DeviceProperties.Power]:
            raise DeviceCommunicationError("Power could not be set")

        self._device_properties.update(response_state)

    async def update(self) -> None:
        """
        Update all the state properties of the device
        """
        device_response = await self._client.device_update(device_id=self._device_id)
        self._device_properties.update(device_response)

    def __repr__(self):
        return json.dumps(self._state, indent=2)