import websocket
import _thread
import time
import requests
import json


url = "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token"

payload = 'grant_type=device_auth&account_id=c7d7fd6f47f54239b345c9b5f5e5d680&device_id=5d40a5f834df4de0afd83862c064b84e&secret=UYDZK7IIFIREM4UYGUIAHB4RJ3ZWB3KO'
headers = {
    'Authorization': 'Basic MzQ0NmNkNzI2OTRjNGE0NDg1ZDgxYjc3YWRiYjIxNDE6OTIwOWQ0YTVlMjVhNDU3ZmI5YjA3NDg5ZDMxM2I0MWE=',
    'Content-Type': 'application/x-www-form-urlencoded'
}

response = requests.request("POST", url, headers=headers, data=payload)

Bearer = response.json()["access_token"]

url = "https://party-service-prod.ol.epicgames.com/party/api/v1/Fortnite/user/c7d7fd6f47f54239b345c9b5f5e5d680"

payload = {}
headers = {
    'Authorization': 'Bearer ' + Bearer
}

response = requests.request("GET", url, headers=headers, data=payload)

Id = response.json()["current"][0]["id"]

url = f"https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/matchmakingservice/ticket/player/c7d7fd6f47f54239b345c9b5f5e5d680?partyPlayerIds=c7d7fd6f47f54239b345c9b5f5e5d680&bucketId=FN:Stage:17227462:2:ME:playlist_playgroundv2:PC:private:0&player.platform=Windows&player.subregions=SAO&player.option.preserveSquad=false&player.option.crossplayOptOut=false&player.option.partyId=70da6a5278464ed7934624863c2d45cc&player.option.splitScreen=false&party.WIN=true&input.KBM=true&player.input=KBM&player.option.microphoneEnabled=true&player.option.uiLanguage=pt-BR"

payload = {}
headers = {
    'User-Agent': 'Fortnite/++Fortnite+Release-21.00-CL-20463113 Windows/10',
    'Authorization': 'Bearer ' + Bearer
}

response = requests.request("GET", url, headers=headers, data=payload)
if response.status_code != 200:
    print(response.text)
else:
    pass
Payload = response.json()["payload"]
Signature = response.json()["signature"]

url = "https://plebs.polynite.net/api/checksum"

payload = json.dumps({
    "payload": Payload,
    "signature": Signature
})
headers = {
    'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

checksum = response.json()["checksum"]

def on_message(ws, message):
    print(message)
    global r
    r = message

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    def run(*args):
        for i in range(3):
            time.sleep(1)
        time.sleep(1)

    _thread.start_new_thread(run, ())

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://fortnite-matchmaking-public-service-live-me.ol.epicgames.com:443",
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close,
                                header=[
                                    f"Authorization:Epic-Signed mms-player {Payload} {Signature} {checksum}"])

    ws.run_forever()
a = json.loads(r)
session = a["payload"]["sessionId"]

url = f"https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/matchmaking/session/{session}"

payload = {}
headers = {
    'Authorization': 'Bearer ' + Bearer
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)


