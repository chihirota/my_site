from flask import Blueprint, render_template, session, request
from zenora import APIClient
from lib.db import guild, server, channel
from lib.discord import get, check
from dataclasses import dataclass


api = Blueprint("log", __name__)

demo_api = Blueprint("demo_log", __name__)

log = server.Log()

log_data = {
    "VC入室": {"desc": "VCに入室したらログを表示", "channel_id": "0", "enable": False},
    "VC退室": {"desc": "VCに退室したらログを表示", "channel_id": "0", "enable": False},
    "VC移動": {"desc": "VCを移動したらログを表示", "channel_id": "0", "enable": False},
    "サーバー入室": {"desc": "サーバーに入室したらログを表示", "channel_id": "0", "enable": False},
    "サーバー退室": {"desc": "サーバーに入室したらログを表示", "channel_id": "0", "enable": False},
    "メッセージ削除": {"desc": "メッセージを削除したらログを表示", "channel_id": "0", "enable": False},
    "メッセージ編集": {"desc": "メッセージが編集されたらログを表示", "channel_id": "0", "enable": False},
    "チャンネル作成": {"desc": "チャンネルを作成したらログを表示", "channel_id": "0", "enable": False},
    "チャンネル削除": {"desc": "チャンネルが削除されたらログを表示", "channel_id": "0", "enable": False},
    "ユーザーBAN": {"desc": "ユーザーをBANしたらログを表示", "channel_id": "0", "enable": False},
    "BOTINFO": {"desc": "Same BOTのログを表示", "channel_id": "0", "enable": False},
}


@dataclass
class Guild:
    id: int = None


@demo_api.get("/dashboard/demo/log")
def demo_log_index():
    tcs = [name for name in log_data.keys()]

    return render_template("contents/demo/log.html", 
    datas=log_data, 
    tcs=tcs, 
    guilds=[],
    guild_id=000000,
    guild=Guild(id=0000))


@api.get("/dashboard/<guild_id>/log")
def log_index(guild_id: int):

    user = get.current_user(session, APIClient)
    guilds = guild.fetchs_admin(user.id) or []

    if not check.admin(guild_id, user.id):
        return render_template("guilds.html", datas=guilds)

    datas = log.guild_fetchs(guild_id)

    voice_channels = {}
    text_channels = {}
    category_channels = []

    channel_datas = channel.fetchs(guild_id)

    for channel_data in channel_datas:
        if channel_data.channel_type == "voice":
            if not voice_channels.get(channel_data.category_name):
                voice_channels[channel_data.category_name] = []
            voice_channels[channel_data.category_name].append(channel_data)

        elif channel_data.channel_type == "text":
            if not text_channels.get(channel_data.category_name):
                text_channels[channel_data.category_name] = []
            text_channels[channel_data.category_name].append(channel_data)

        elif channel_data.channel_type == "category":
            category_channels.append(channel_data)

    for data in datas:
        log_data[data.type]["enable"] = data.enable
        log_data[data.type]["channel_id"] = data.channel_id

    return render_template(
        "contents/server/log.html",
        guilds=guilds,
        guild_id=guild_id,
        guild=Guild(id=guild_id),
        datas=log_data,
        voice_channels=voice_channels,
        category_channels=category_channels,
        text_channels=text_channels,
    )


@api.post("/api/save/log/<guild_id>")
def log_save(guild_id):
    name = request.json.get("name")
    enable = request.json.get("enable")
    if not (log.fetch(guild_id, name)):
        log.insert(guild_id, name)

    log.update(enable, guild_id, name)

    return {"status": "OK"}


@api.post("/api/save/log/channel_id/<guild_id>")
def log_save_channel_id(guild_id):
    name = request.json.get("name")
    channel_id = request.json.get("channel_id")
    if not (log.fetch(guild_id, name)):
        log.insert(guild_id, name)

    log.update_channel_id(channel_id, guild_id, name)

    return {"status": "OK"}
