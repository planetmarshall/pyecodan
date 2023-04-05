import os
from typing import Dict, List

from aiohttp import ClientSession

from .device import Device

class Client():
    """
    A client for communicating with an Ecodan Heatpump via MELCloud
    """

    base_url = "https://app.melcloud.com/Mitsubishi.Wifi.Client"

    def __init__(self, username=os.getenv("ECODAN_USERNAME"), password=os.getenv("ECODAN_PASSWORD")):
        """
        :param username: MELCloud username. Default is taken from the environment variable `ECODAN_USERNAME`
        :param password: MELCloud password. Default is taken from the environment variable `ECODAN_PASSWORD`
        """
        self._session = ClientSession()
        self._username = username
        self._password = password
        self._context_key = None

    async def device_request(self, endpoint: str, state: Dict):
        if self._context_key is None:
            await self.login()

        auth_header = {"X-MitsContextKey": self._context_key}
        url = f"{Client.base_url}/Device/{endpoint}"
        async with self._session.post(url, headers=auth_header, json=state) as response:
            return await response.json()

    async def device_update(self, device_id) -> Dict:
        for location in await self._user_request("ListDevices"):
            structure = location["Structure"]
            device_state = [state["Device"] for state in structure["Devices"] if state["DeviceID"] == device_id]
            if len(device_state) > 0:
                return device_state[0]

        raise ValueError(f"Device with id={device_id} not found")

    async def _user_request(self, endpoint) -> Dict:
        if self._context_key is None:
            await self.login()

        auth_header = {"X-MitsContextKey": self._context_key}
        url = f"{Client.base_url}/User/{endpoint}"
        async with self._session.get(url, headers=auth_header) as response:
            return await response.json()

    async def login(self) -> None:
        login_url = f"{Client.base_url}/Login/ClientLogin"
        login_data = {
            "Email": self._username,
            "Password": self._password,
            "Language": 0,
            "AppVersion": "1.26.2.0",
            "Persist": True,
            "CaptchaResponse": None
        }
        async with self._session.post(login_url, json=login_data) as response:
            response_data = await response.json()
            if response_data["ErrorId"] is not None:
                raise ConnectionError("login error")
            self._context_key = response_data["LoginData"]["ContextKey"]

    async def list_devices(self) -> List[Device]:
        for location in await self._user_request("ListDevices"):
            structure = location["Structure"]
            return [Device(self, device_state) for device_state in structure["Devices"]]

        return []

    async def __aenter__(self) -> "Client":
        return self

    async def __aexit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
    ) -> None:
        await self._session.__aexit__(exc_type, exc_val, exc_tb)
