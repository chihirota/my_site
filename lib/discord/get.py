from flask import render_template, session
from zenora import User, exceptions, APIClient
from typing import List, Dict
from lib.db import role
from config import headers, BASE_URL
import requests


def guild(guild_id: int):
    with requests.get(f"{BASE_URL}guilds/{int(guild_id)}", headers=headers) as res:
        data = res.json()

        return data


def channel(channel_id: int):
    with requests.get(f"{BASE_URL}channels/{channel_id}", headers=headers) as res:
        data = res.json()

        return data


"""def guilds(user: User = None):
    with requests.get(
        "https://discord.com/api/v8/users/@me/guilds", headers=headers
    ) as res:
        guilds = res.json()
    
    return guilds"""


def guilds():
    token = session.get("access_token")
    print(token)

    if not token:
        return []

    with requests.get(
        "https://discord.com/api/v8/users/@me/guilds",
        headers={"Authorization": f"Bearer {token}"},
    ) as res:
        guilds = res.json()

    return guilds


def voice_channels(guild_id: int):

    with requests.get(
        f"{BASE_URL}guilds/{int(guild_id)}/channels", headers=headers
    ) as res:
        datas = res.json()

    channels = []

    for data in datas:
        if data["type"] != 2:
            continue

        channels.append(data)

    return channels


def text_channels(guild_id: int):

    with requests.get(
        f"{BASE_URL}guilds/{int(guild_id)}/channels", headers=headers
    ) as res:
        datas = res.json()

    channels = []

    for data in datas:
        if data["type"] != 0:
            continue

        channels.append(data)

    return channels


def share_guilds(guilds: List[Dict[str, str]], user: User):
    datas = []

    for guild in guilds:
        guild_id = guild["id"]
        member = members(guild_id, user.id)
        print(member)

        roles = role.fetch(guild_id)

        if not roles:
            continue

        if not roles.admin:
            continue

        if any(int(role) in roles.admin for role in member["roles"]):
            datas.append(guild)
            print("append")

    return datas


def members(guild_id: int):
    params = {"limit": 1000}

    with requests.get(
        f"{BASE_URL}guilds/{guild_id}/members", headers=headers, params=params
    ) as res:
        data = res.json()

        return data


def member(guild_id: int, member_id: int):
    with requests.get(
        f"{BASE_URL}guilds/{guild_id}/members/{member_id}", headers=headers
    ) as res:
        data = res.json()

        return data


def current_user(session, client: APIClient):
    try:
        access_token = session.get("access_token")

        bearer_client: APIClient = client(access_token, bearer=True)
        current_user = bearer_client.users.get_current_user()

        return current_user
    except exceptions.BadTokenError:
        from ..db import stats

        guilds = stats.server()
        members = stats.user()
        return render_template("index.html", member_count=members, guild_count=guilds)
