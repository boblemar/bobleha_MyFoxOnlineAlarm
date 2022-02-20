import threading
from time import sleep
from threading import Timer
import requests

# from grequests import async

from urllib import response
from urllib.request import Request
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup


class Status:
    """MyFoxOnline status enum"""

    DISARMED = 1
    PARTIAL = 2
    FULL = 3
    ARMING = 4
    DISARMING = 5

class MyFoxOnline:
    """Class to access MyFox alarms using the myfoxonline web site."""

    def __init__(self, username: str, password: str, isOffline: bool = False) -> None:
        self.__is_offline = isOffline

        self.__state_cache: Status = Status.DISARMED

        self.__connection_payload = {
            "nom": username,
            "mdp": password,
            "act": "client",
            "provenance": "https://www.myfox-online.com",
        }

        if self.__is_offline:
            return

        self.__session = requests.Session()

        self.__refresh_state_cache()

    def __refresh_state_cache(self) -> None:
        self.__connect()
        html = self.__get_homepage()

        if not self.__is_offline:
            self.__session.close()

        bs = BeautifulSoup(html, "html.parser")
        div_myprotection = bs.find("div", {"id": "my-protection"})
        status_id = div_myprotection.find("div", {"class": "active"})["id"]

        if status_id == "desarm":
            self.__state_cache = Status.DISARMED
        elif status_id == "full":
            self.__state_cache = Status.FULL
        else:
            self.__state_cache = Status.PARTIAL

        threading.Timer(60, self.__refresh_state_cache).start()

    def __connect(self) -> None:
        if self.__is_offline:
            return

        self.__session.post(
            "https://www.myfox-online.com/newIG/bat_identif_clt.php",
            data=self.__connection_payload,
            verify=False,
        )

    def __get_homepage(self) -> None:
        if self.__is_offline:
            with open(
                "/workspaces/home-assistant-core/config/custom_components/bobleha_MyFoxOnlineAlarm/getHomepage.html",
                "r",
                encoding="utf-8",
            ) as f:
                return f.read()

        resp = self.__session.get(
            "https://www.myfox-online.com/newIG/myfox/", verify=True
        )

        with open("getHomepage.html", "w", encoding="utf-8") as f:
            f.write(resp.text)

        return resp.text

    def get_state(self) -> Status:
        return self.__state_cache

    def set_state(self, status: Status):
        if self.__is_offline:
            return

        self.__connect()

        if status == Status.FULL:
            self.__state_cache = Status.ARMING
            status_param = "total"
        elif status == Status.DISARMED:
            self.__state_cache = Status.DISARMING
            status_param = "desarmement"
        else:
            self.__state_cache = Status.ARMING
            status_param = "partiel"

        payload = {"question": status_param}

        self.__session.get(
            "https://www.myfox-online.com/newIG/myfox/ajax/Traitement_Etat_Centrale.php",
            params=payload,
            verify=False,
        )

        self.__refresh_state_cache()
        # self.__session.close()
