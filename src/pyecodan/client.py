import os
from typing import Dict

from aiohttp import ClientSession


class Client():
    def __init__(self, username=os.getenv("ECODAN_USERNAME"), password=os.getenv("ECODAN_PASSWORD")):
        self._session = ClientSession()
        self._username = username
        self._password = password
        self._context_key = None

    async def _user_request(self, endpoint) -> Dict:
        if self._context_key is None:
            await self.login()

        base_url = "https://app.melcloud.com/Mitsubishi.Wifi.Client/User"
        client_url = f"{base_url}/{endpoint}"
        auth_header = {"X-MitsContextKey": self._context_key}
        async with self._session.get(client_url, headers=auth_header) as response:
            return await response.json()

    async def login(self) -> None:
        login_url = "https://app.melcloud.com/Mitsubishi.Wifi.Client/Login/ClientLogin"
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

    async def list_devices(self) -> Dict:
        return await self._user_request("ListDevices")

    async def __aenter__(self) -> "Client":
        return self

    async def __aexit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
    ) -> None:
        await self._session.__aexit__(exc_type, exc_val, exc_tb)
