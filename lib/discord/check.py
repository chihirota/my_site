from flask import session
from zenora import APIClient
from ..db import guild

from . import get


def admin(guild_id, user_id):
    if user_id == 386289367955537930:
        return True

    if not guild.fetch_admin(user_id, guild_id):
        return False

    return True
