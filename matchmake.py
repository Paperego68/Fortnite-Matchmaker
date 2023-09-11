import asyncio
import websockets
import requests
import json
import hashlib
import base64

def userAgent():
    url = "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token"

    payload='grant_type=client_credentials'
    headers = {
        'Authorization': 'Basic MzQ0NmNkNzI2OTRjNGE0NDg1ZDgxYjc3YWRiYjIxNDE6OTIwOWQ0YTVlMjVhNDU3ZmI5YjA3NDg5ZDMxM2I0MWE=',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    r = requests.request("POST", url, headers=headers, data=payload)
    
    url = "https://launcher-public-service-prod06.ol.epicgames.com/launcher/api/public/assets/v2/platform/Windows/namespace/fn/catalogItem/4fe75bbc5a674f4f9b356b5c90567da5/app/Fortnite/label/Live"

    payload={}
    headers = {
        'Authorization': 'Bearer {}'.format(r.json()["access_token"])
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    useragent = "Fortnite/{} Windows/10".format(response.json()["elements"][0]["buildVersion"][:-8])
    return useragent

def NetCL(bearer):
    url = "https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/matchmaking/session/matchMakingRequest"

    payload = json.dumps({
        "criteria": [],
        "openPlayersRequired": 1,
        "buildUniqueId": "",
        "maxResults": 1
    })
    headers = {
        'Authorization': f'Bearer {bearer}',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    try:
        Netcl = response.json()[0]["attributes"]["buildUniqueId_s"]
    except:
        print(response.text)
    return Netcl
    
debug = True
if debug is True:
    solo = "playlist_playgroundv2"
else:
    solo = input("Insert Playlist Here:")

exchange_code = input('Insert your Exchange Code here: ')

url = "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token"

payload = f'grant_type=exchange_code&exchange_code={exchange_code}'
headers = {
    'Authorization': 'Basic MzQ0NmNkNzI2OTRjNGE0NDg1ZDgxYjc3YWRiYjIxNDE6OTIwOWQ0YTVlMjVhNDU3ZmI5YjA3NDg5ZDMxM2I0MWE=',
    'Content-Type': 'application/x-www-form-urlencoded'
}
print("Grabbing token")
response = requests.request("POST", url, headers=headers, data=payload)
if response.status_code == 200:
    Bearer = response.json()["access_token"]
    accountid = response.json()['account_id']
    pass
else:
    raise RuntimeError("OAUTH FAILURE")

netcl = NetCL(bearer=Bearer)


url = f"https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/matchmakingservice/ticket/player/{accountid}?partyPlayerIds={accountid}&bucketId=FN:Stage:{netcl}:2:ME:{solo}:PC:private:0&player.platform=Windows&player.subregions=SAO&player.option.preserveSquad=false&player.option.crossplayOptOut=false&player.option.partyId=FooPartyId&player.option.splitScreen=false&party.WIN=true&input.KBM=true&player.input=KBM&player.option.microphoneEnabled=true&player.option.uiLanguage=pt-BR"

payload = {}
headers = {
    'User-Agent': userAgent(),
    'Authorization': 'Bearer ' + Bearer
}
print("Generating Ticket")
response = requests.request("GET", url, headers=headers, data=payload)
if response.status_code != 200:
    print(response.text)
else:
    pass
Payload = response.json()["payload"]
Signature = response.json()["signature"]


def calcchecksum(ticketpayload, signature):
    
    plaintext = ticketpayload[10:20] + "Don'tMessWithMMS" + signature[2:10]
    #print(f'Plaintext: "{plaintext}"')

    # Convert to UTF-16
    data = plaintext.encode('utf-16le')
    #print(f'Data UTF-16: "{data}"')

    # SHA1
    hash_object = hashlib.sha1(data)
    hash_digest = hash_object.digest()
    #print(f'Data SHA1: "{data}"')

    # Select 8 specific bytes and hex encode
    checksum = base64.b16encode(hash_digest[2:10]).decode().upper()
    #print(f'Checksum: "{checksum}"')
    return checksum


checksum = calcchecksum(ticketpayload=Payload, signature=Signature)

async def websocket(Payload, Signature, checksum):
    headers = {
        'Authorization': f'Epic-Signed mms-player {Payload} {Signature} {checksum}'
    }

    ws = await websockets.connect("wss://fortnite-matchmaking-public-service-live-me.ol.epicgames.com:443", extra_headers=headers)

    latest_data = None
    while True:
        try:
            latest_data = await ws.recv()
            print(f'Received: {latest_data}')

        except websockets.ConnectionClosed:
            print('### closed ###')
            break

        except Exception as e:
            print(f'Error: {e}')
            break

    data = json.loads(latest_data)
    session = data['payload']['sessionId']
    session

    url = f"https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/matchmaking/session/{session}"

    payload = {}
    headers = {
        'Authorization': 'Bearer ' + Bearer
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return response.text
print("Connecting to websocket")
resp = asyncio.run(main=websocket(Payload, Signature, checksum))
print(resp)

