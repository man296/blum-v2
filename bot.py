import os
import re
import sys
import json
import anyio
from payload import get_payload
import httpx
import random
import uuid
import requests
import asyncio
import argparse
import aiofiles
import aiofiles.os
from base64 import b64decode
import aiofiles.ospath
from colorama import init, Fore, Style
from urllib.parse import parse_qs
from datetime import datetime
from models import (
    get_by_id,
    update_useragent,
    insert,
    update_balance,
    update_token,
    init as init_db,
)
import python_socks
from httpx_socks import AsyncProxyTransport
from fake_useragent import UserAgent
# Initialize logging


init(autoreset=True)
red = Fore.LIGHTRED_EX
blue = Fore.LIGHTBLUE_EX
green = Fore.LIGHTGREEN_EX
yellow = Fore.LIGHTYELLOW_EX
black = Fore.LIGHTBLACK_EX
white = Fore.LIGHTWHITE_EX
reset = Style.RESET_ALL
magenta = Fore.LIGHTMAGENTA_EX
line = white + "~" * 50
log_file = "http.log"
proxy_file = "proxies.txt"
data_file = "data.txt"
config_file = "config.json"


class Config:
    def __init__(self, auto_task, auto_game, auto_claim, low, high, clow, chigh):
        self.auto_task = auto_task
        self.auto_game = auto_game
        self.auto_claim = auto_claim
        self.low = low
        self.high = high
        self.clow = clow
        self.chigh = chigh


class BlumTod:
    def __init__(self, id, query, proxies, config: Config):
        self.p = id
        self.query = query
        self.proxies = proxies
        self.cfg = config
        self.valid = True
        parser = {key: value[0] for key, value in parse_qs(query).items()}
        user = parser.get("user")
        if user is None:
            self.valid = False
            self.log(f"{red}this account data has the wrong format.")
            return None
        self.user = json.loads(user)
        if len(self.proxies) > 0:
            proxy = self.get_random_proxy(id, False)
            transport = AsyncProxyTransport.from_url(proxy)
            self.ses = httpx.AsyncClient(transport=transport, timeout=httpx.Timeout(10.0))
        else:
            self.ses = httpx.AsyncClient(timeout=httpx.Timeout(10.0))
        self.headers = {
            "accept": "application/json, text/plain, */*",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
            "content-type": "application/json",
            "origin": "https://telegram.blum.codes",
            "x-requested-with": "org.telegram.messenger",
            "sec-fetch-site": "same-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://telegram.blum.codes/",
            "accept-encoding": "gzip, deflate",
            "accept-language": "en,en-US;q=0.9",
        }

    def log(self, msg):
        now = datetime.now().isoformat().split("T")[1].split(".")[0]
        print(
            f"{black}[{now}]{white}-{blue}[{white}acc {self.p + 1}{blue}]{white} {msg}{reset}"
        )

    async def ipinfo(self):
        ipinfo1_url = "https://ipapi.co/json/"
        ipinfo2_url = "https://ipwho.is/"
        ipinfo3_url = "https://freeipapi.com/api/json"
        headers = {"user-agent": "marin kitagawa"}
        try:
            res = await self.http(ipinfo1_url, headers)
            ip = res.json().get("ip")
            country = res.json().get("country")
            if not ip:
                res = await self.http(ipinfo2_url, headers)
                ip = res.json().get("ip")
                country = res.json().get("country_code")
                if not ip:
                    res = await self.http(ipinfo3_url, headers)
                    ip = res.json().get("ipAddress")
                    country = res.json().get("countryCode")
            self.log(f"{green}ip : {white}{ip} {green}country : {white}{country}")
        except json.decoder.JSONDecodeError:
            self.log(f"{green}ip : {white}None {green}country : {white}None")

    def get_random_proxy(self, isself, israndom=False):
        if israndom:
            return random.choice(self.proxies)
        return self.proxies[isself % len(self.proxies)]

    async def http(self, url, headers, data=None):
        while True:
            try:
                if not await aiofiles.ospath.exists(log_file):
                    async with aiofiles.open(log_file, "w") as w:
                        await w.write("")

                logsize = await aiofiles.ospath.getsize(log_file)

                if logsize / 1024 / 1024 > 1:
                    async with aiofiles.open(log_file, "w") as w:
                        await w.write("")

                if data is None:
                    res = await self.ses.get(url, headers=headers)
                elif data == "":
                    res = await self.ses.post(url, headers=headers)
                else:
                    res = await self.ses.post(url, headers=headers, data=data)
                async with aiofiles.open(log_file, "a", encoding="utf-8") as hw:
                    await hw.write(f"{res.status_code} {res.text}\n")
                # print(res.status_code)
                # print(res.text)
                if "<title>" in res.text:
                    self.log(f"{yellow}failed get json response !")
                    return None

                return res
            except (
                    httpx.ProxyError,
                    python_socks._errors.ProxyTimeoutError,
                    python_socks._errors.ProxyError,
            ):
                proxy = self.get_random_proxy(0, israndom=True)
                transport = AsyncProxyTransport.from_url(proxy)
                self.ses = httpx.AsyncClient(transport=transport)
                self.log(f"{yellow}proxy error,selecting random proxy !")
                await asyncio.sleep(3)
                continue
            except httpx.NetworkError:
                self.log(f"{yellow}network error !")
                await asyncio.sleep(3)
                continue
            except httpx.TimeoutException:
                self.log(f"{yellow}connection timeout !")
                await asyncio.sleep(3)
                continue
            except (httpx.RemoteProtocolError, anyio.EndOfStream):
                self.log(f"{yellow}connection close without response !")
                await asyncio.sleep(3)
                continue

    def is_expired(self, token):
        if token is None or isinstance(token, bool):
            return True
        header, payload, sign = token.split(".")
        payload = b64decode(payload + "==").decode()
        jload = json.loads(payload)
        now = round(datetime.now().timestamp()) + 300
        exp = jload["exp"]
        if now > exp:
            return True

        return False

    async def login(self):
        auth_url = "https://user-domain.blum.codes/api/v1/auth/provider/PROVIDER_TELEGRAM_MINI_APP"
        data = {
            "query": self.query,
        }
        res = await self.http(auth_url, self.headers, json.dumps(data))
        token = res.json().get("token")
        if not token:
            message = res.json().get("message", "")
            if "signature is invalid" in message:
                self.log(f"{red}data has the wrong format or data is outdated.")
                return False
            self.log(f"{red}{message}, check log file http.log !")
            return False
        token = token.get("access")
        uid = self.user.get("id")
        await update_token(uid, token)
        self.log(f"{green}success get access token !")
        self.headers["authorization"] = f"Bearer {token}"
        return True

    # async def get_data_payload(self):
    #     url = 'https://raw.githubusercontent.com/zuydd/database/main/blum.json'
    #     data = requests.get(url=url)
    #     return data.json()


    async def create_payload(self, game_id, points, dogs):
        # data = await self.get_data_payload()
        # payload_server = data.get('payloadServer', [])
        # filtered_data = [item for item in payload_server if item['status'] == 1]
        # random_id = random.choice([item['id'] for item in filtered_data])
        payload_data = {'gameId': game_id,
                'points': str(points),
                "dogs": dogs}

        PAYLOAD_SERVER_URL = "https://server2.ggtog.live/api/game"
        resp = requests.post(PAYLOAD_SERVER_URL, json=payload_data)

        if resp is not None:
            try:
                data = resp.json()
                if "payload" in data:
                    return json.dumps({"payload": data["payload"]})
            except Exception as e:
                self.log(e)
                return None

    async def start(self):
        rtime = random.randint(self.cfg.clow, self.cfg.chigh)
        await countdown(rtime)
        if not self.valid:
            return int(datetime.now().timestamp()) + (3600 * 8)
        balance_url = "https://game-domain.blum.codes/api/v1/user/balance"
        friend_balance_url = "https://user-domain.blum.codes/api/v1/friends/balance"
        farming_claim_url = "https://game-domain.blum.codes/api/v1/farming/claim"
        farming_start_url = "https://game-domain.blum.codes/api/v1/farming/start"
        checkin_url = "https://game-domain.blum.codes/api/v1/daily-reward?offset=-420"
        if len(self.proxies) > 0:
            await self.ipinfo()
        uid = self.user.get("id")
        first_name = self.user.get("first_name")
        self.log(f"{green}login as {white}{first_name}")
        result = await get_by_id(uid)
        if not result:
            await insert(uid, first_name)
            result = await get_by_id(uid)
        useragent = result.get("useragent")
        if useragent is None:
            useragent = UserAgent(os=["android", "ios", "windows"]).random
            await update_useragent(uid, useragent)
        self.headers["user-agent"] = useragent
        token = result.get("token")
        expired = self.is_expired(token=token)
        if expired:
            result = await self.login()
            if not result:
                return int(datetime.now().timestamp()) + 300
        else:
            self.headers["authorization"] = f"Bearer {token}"
        res = await self.http(checkin_url, self.headers)
        if res.status_code == 404:
            self.log(f"{yellow}already check in today !")
        else:
            res = await self.http(checkin_url, self.headers, "")
            self.log(f"{green}success check in today !")
        while True:
            res = await self.http(balance_url, self.headers)
            timestamp = res.json().get("timestamp")
            if timestamp == 0:
                timestamp = int(datetime.now().timestamp() * 1000)
            if not timestamp:
                continue
            timestamp = timestamp / 1000
            break
        balance = res.json().get("availableBalance", 0)
        await update_balance(uid, balance)
        farming = res.json().get("farming")
        end_iso = datetime.now().isoformat(" ")
        end_farming = int(datetime.now().timestamp() * 1000) + random.randint(
            3600000, 7200000
        )
        self.log(f"{green}balance : {white}{balance}")
        refres = await self.http(friend_balance_url, self.headers)
        amount_claim = refres.json().get("amountForClaim")
        can_claim = refres.json().get("canClaim", False)
        self.log(f"{green}referral balance : {white}{amount_claim}")
        if can_claim:
            friend_claim_url = "https://user-domain.blum.codes/api/v1/friends/claim"
            clres = await self.http(friend_claim_url, self.headers, "")
            if clres.json().get("claimBalance") is not None:
                self.log(f"{green}success claim referral reward !")
            else:
                self.log(f"{red}failed claim referral reward !")
        if self.cfg.auto_claim:
            while True:
                if farming is None:
                    _res = await self.http(farming_start_url, self.headers, "")
                    if _res.status_code != 200:
                        self.log(f"{red}failed start farming !")
                    else:
                        self.log(f"{green}success start farming !")
                        farming = _res.json()
                if farming is None:
                    res = await self.http(balance_url, self.headers)
                    farming = res.json().get("farming")
                    if farming is None:
                        continue
                end_farming = farming.get("endTime")
                if timestamp > (end_farming / 1000):
                    res_ = await self.http(farming_claim_url, self.headers, "")
                    if res_ and res_.status_code != 200:
                        self.log(f"{red}failed claim farming !")
                    else:
                        self.log(f"{green}success claim farming !")
                        farming = None
                        continue
                else:
                    self.log(f"{yellow}not time to claim farming !")
                end_iso = (
                    datetime.fromtimestamp(end_farming / 1000)
                    .isoformat(" ")
                    .split(".")[0]
                )
                break
            self.log(f"{green}end farming : {white}{end_iso}")
        if self.cfg.auto_task:
            task_url = "https://earn-domain.blum.codes/api/v1/tasks"
            res = await self.http(task_url, self.headers)
            if res:
                for tasks in res.json():
                    if isinstance(tasks, str):
                        self.log(f"{yellow}failed get task list !")
                        break
                    for k in list(tasks.keys()):
                        if k != "tasks" and k != "subSections":
                            continue
                        for t in tasks.get(k):
                            if isinstance(t, dict):
                                subtasks = t.get("subTasks")
                                if subtasks is not None:
                                    for task in subtasks:
                                        await self.solve(task)
                                    await self.solve(t)
                                    continue
                            _tasks = t.get("tasks")
                            if not _tasks:
                                continue
                            for task in _tasks:
                                await self.solve(task)
        if self.cfg.auto_game:
            play_url = "https://game-domain.blum.codes/api/v2/game/play"
            claim_url = "https://game-domain.blum.codes/api/v2/game/claim"
            dogs_url = 'https://game-domain.blum.codes/api/v2/game/eligibility/dogs_drop'

            game = True
            # try:
            #     random_uuid = str(uuid.uuid4())
            #     point = random.randint(self.cfg.low, self.cfg.high)
            #     data = await get_payload(gameId=random_uuid, points=point, freeze=None)
            #
            #     if "payload" in data:
            #         self.log(f"{green}Games available right now!")
            #         game = True
            #
            #     else:
            #         self.log(f"{red}Failed start games - {e}")
            #         self.log(f"{red}Install node.js!")
            #         game = False
            # except Exception as e:
            #     self.log(f"{red}Failed start games - {e}")
            #     self.log(f"{red}Install node.js!")
            #     game = False



            while game:
                res = await self.http(balance_url, self.headers)

                #количество игр
                play = res.json().get("playPasses")
                if play is None:
                    self.log(f"{yellow}failed get game ticket !")
                    break
                self.log(f"{green}you have {white}{play}{green} game ticket")
                if play <= 0:
                    break

                #основной цикл игр
                for i in range(play):
                    if self.is_expired(self.headers.get("authorization").split(" ")[1]):
                        result = await self.login()
                        if not result:
                            break
                        continue

                    #старт игры
                    res = await self.http(play_url, self.headers, "")
                    game_id = res.json().get("gameId")

                    if game_id is None:
                        message = res.json().get("message", "")
                        if message == "cannot start game":
                            self.log(f"{yellow}{message}")
                            game = False
                            break
                        self.log(f"{yellow}{message}")
                        continue


                    while True:

                        # количество очков
                        point = random.randint(self.cfg.low, self.cfg.high)

                        # проверяем догс
                        try:
                            res = await self.http(dogs_url, self.headers)
                            if res is not None:
                                eligible = res.json().get('eligible', False)

                        except Exception as e:
                            self.error(f"Failed elif dogs, error: {e}")
                            eligible = None

                        freeze_count = random.randint(*[4, 8])
                        #создаем payload
                        if eligible:
                            dogs = random.randint(25, 30) * 5
                            self.log(f'dogs = {dogs}')
                            # payload = await self.create_payload(game_id=game_id, points=point,dogs=dogs)
                            payload = await get_payload(gameId=game_id, points=point, freeze=freeze_count)
                        else:
                            # payload = await self.create_payload(game_id=game_id, points=point,dogs=0)
                            payload = await get_payload(gameId=game_id, points=point,freeze=freeze_count)

                        await countdown(30 + freeze_count * 5)

                        res = await self.http(claim_url, self.headers, payload)
                        if res and "OK" in res.text:
                            self.log(
                                f"{green}success earn {white}{point}{green} from game !"
                            )
                            break
                        else:
                            self.log(f"{red}failed earn {white}{point}{red} from game !")
                        break
        res = await self.http(balance_url, self.headers)
        balance = res.json().get("availableBalance", 0)
        self.log(f"{green}balance :{white}{balance}")
        now = datetime.now().strftime("%Yx%mx%d %H:%M")
        open("balance.log", "a", encoding="utf-8").write(
            f"{now} - {self.p} - {balance} - {first_name}\n")
        await update_balance(uid, balance)
        return round(end_farming / 1000)

    async def solve(self, task: dict):
        task_id = task.get("id")
        answers_local = json.loads(open("answers.json").read())
        task_title = task.get("title")
        task_status = task.get("status")
        task_type = task.get("type")
        validation_type = task.get("validationType")
        start_task_url = f"https://earn-domain.blum.codes/api/v1/tasks/{task_id}/start"
        claim_task_url = f"https://earn-domain.blum.codes/api/v1/tasks/{task_id}/claim"
        while True:
            if task_status == "FINISHED":
                self.log(f"{yellow}already complete task id {white}{task_title} !")
                return
            if task_status == "READY_FOR_CLAIM" or task_status == "STARTED":
                _res = await self.http(claim_task_url, self.headers, "")
                message = _res.json().ge
