import requests
from config import BASE_URL


def edit(channel_id: int, message_id: int, headers, **kwargs):
    with requests.patch(
        f"{BASE_URL}channels/{channel_id}/messages/{message_id}",
        headers=headers,
        json=kwargs,
    ) as res:
        data = res.json()

        if data.get("code") == 30046:
            import time

            reset_after = res.headers.get("x-ratelimit-reset-after", 5)

            time.sleep(int(reset_after) / 1000)
            return edit(channel_id, message_id, headers, **kwargs)

        if data.get("code") == 50001:
            return 50001

        return data


def delete(channel_id: int, message_id: int, headers):
    with requests.delete(
        f"{BASE_URL}channels/{channel_id}/messages/{message_id}", headers=headers
    ) as res:
        try:
            data = res.json()
        except:
            print(res.text)
            return

        if data.get("code") == 30046:
            import time

            reset_after = res.headers.get("x-ratelimit-reset-after", 5)

            time.sleep(int(reset_after) / 1000)
            return delete(channel_id, message_id, headers)

        if data.get("code") == 50001:
            return 50001


def send(channel_id: int, headers, **kwargs):
    with requests.post(
        f"{BASE_URL}channels/{channel_id}/messages",
        headers=headers,
        json=kwargs,
    ) as res:
        data = res.json()

        if data.get("code") == 30046:
            import time

            print(res.headers)

            reset_after = res.headers.get("x-ratelimit-reset-after", 5)
            print("reset after", reset_after)
            time.sleep(int(reset_after) / 1000)
            return send(channel_id, headers, **kwargs)

        if data.get("code") == 50001:
            return 50001

        if res.status_code != 200:
            print(data)
            return data

        return data
