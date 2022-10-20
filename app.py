from flask import Flask, render_template, request, redirect, session
from zenora import APIClient, exceptions

from datetime import datetime

from urllib.parse import quote
from colorama import Fore, Style, Back

from router import base_setting
from router.bot.counter import stats
from router.bot.back import back_recruit
from router.bot.back import back_two
from router.bot.event import event_panel
from router.bot.manage import server, module
from router.bot import paid
from router.docs import back

from lib import db, discord

import config

BASE_URL = config.BASE_URL
client_id = config.client_id
redirect_uri = str(config.redirect_uri)
token = config.manage_token
secret = config.secret

headers: str = config.headers

bheaders = config.bheaders

OAUTH_URL = (
    "https://discord.com/api/oauth2/authorize?"
    + f"client_id={client_id}&redirect_uri={quote(redirect_uri)}&"
    + "response_type=code&scope=guilds%20identify"
)

app = Flask(__name__)
client = APIClient(token, client_secret=secret)

app.config["SECRET_KEY"] = "dajhf09waf"

# router
app.register_blueprint(back_two.back_two_api)
app.register_blueprint(back_recruit.back_recruit_api)

app.register_blueprint(base_setting.base_seting_api)

app.register_blueprint(event_panel.api)

app.register_blueprint(stats.api)

app.register_blueprint(server.api)
app.register_blueprint(server.demo_api)
app.register_blueprint(module.api)

app.register_blueprint(paid.api)

# docs
app.register_blueprint(back.api)


@app.route("/")
def main():
    access_token = session.get("access_token")

    guilds = db.stats.server()
    members = db.stats.user()

    if not access_token:
        return render_template("index.html", member_count=members, guild_count=guilds)

    try:
        bearer_client = APIClient(access_token, bearer=True)
        current_user = bearer_client.users.get_current_user()
    except exceptions.AuthenticationError:
        return render_template("index.html", member_count=members, guild_count=guilds)
    except exceptions.ZenoraException:
        return render_template("index.html", member_count=members, guild_count=guilds)

    return render_template(
        "index.html",
        member_count=members,
        guild_count=guilds,
        current_user=current_user,
    )


@app.route("/login")
def login_with_discord():
    return redirect(OAUTH_URL)


@app.route("/callback")
def oauth_callback():
    code = request.args["code"]
    access_token = client.oauth.get_access_token(
        code, redirect_uri=redirect_uri
    ).access_token
    session["access_token"] = access_token

    return redirect("/guilds")


@app.route("/guilds")
def guilds():
    user = discord.get.current_user(session, APIClient)
    guilds = discord.get.guilds()

    now = datetime.now()

    print(
        f"{Back.WHITE}{Fore.MAGENTA}{user.username}がログインしました\nログイン時間(JST): {now}\n管理サーバ一覧: {guilds}{Style.RESET_ALL}"
    )

    datas = []

    for guild_data in guilds:
        name = guild_data.get("name")
        id = guild_data.get("id")
        user_permissions = int(guild_data.get("permissions"))
        icon_hash = guild_data.get("icon")

        channel_and_role_permission = (
            0x10 | 0x10000000
        )  # MANAGE_CHANNELS と MANAGE_ROLESの論理和

        result = (
            user_permissions & channel_and_role_permission
        ) == channel_and_role_permission

        if result:

            if not icon_hash:
                url = "https://cdn.discordapp.com/icons/845947995358232576/a2fdfb532379a48fa4b870f347140ac1.png?size=1024"
            else:
                animated = icon_hash.startswith("a_")

                format = "gif" if animated else "png"

                url = f"https://cdn.discordapp.com/icons/{id}/{icon_hash}.{format}?size=1024"

            _guilds = db.info.Guilds()
            in_me = _guilds.fetch(int(id))
            print(name, in_me)

            datas.append(
                {
                    "name": name,
                    "id": guild_data.get("id"),
                    "icon": url,
                    "in": False if in_me is None else True,
                }
            )

    return render_template("guilds.html", datas=datas)


@app.route("/docs")
def docs():
    return render_template("docs/index.html")


@app.route("/mypage")
def mypage():
    return render_template("mypage/menus.html")


@app.route("/dashboard/<guild_id>")
def dashboard(guild_id: int):
    data = discord.get.guild(guild_id.replace(" ", ""))

    current_user = discord.get.current_user(session, APIClient)

    if not current_user:
        return redirect("/login")

    _datas = db.module.fetchs(guild_id)

    datas = {}

    for _data in _datas:
        datas[_data.name] = _data.enable

    return render_template("menus.html", guild=data, datas=datas)


@app.get("/api/get_channels/<guild_id>/<channel_type>")
def get_channels(guild_id: int, channel_type: str):
    user = discord.get.current_user(session, APIClient)

    if not db.guild.fetch_admin(user.id, guild_id):
        datas = db.guild.fetchs_admin(user.id)

        return render_template("guilds.html", datas=datas)

    _datas = db.channel.type_fetchs(guild_id, channel_type)

    datas = []

    for data in _datas:
        datas.append({"name": data.channel_name, "id": str(data.channel_id)})

    return {"datas": datas}


@app.post("/api/save/module/<guild_id>")
def update_module(guild_id: int):
    data = request.json

    name = data.get("name")
    enable = data.get("enable")

    db.module.update(enable, name, guild_id)

    return {"status": "OK"}


if __name__ == "__main__":
    app.run(port="5000", debug=True, use_reloader=False)
