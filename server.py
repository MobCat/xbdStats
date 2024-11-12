#!/env/Python3.10.4
#/MobCat (2024)

import asyncio
import websockets, socket, time, urllib.request, json
from discordrp import Presence
from websockets.server import WebSocketServerProtocol as wetSocks # Yes, I thought it was funny.

# Login and tell discord app we are a game and we are running.
clientID = "1304454011503513600" # 'Playing Xbox' id. I wish we could set 'Playing Game Name' but we can't without API abuse.
presence = Presence(clientID)

# If you host your own ver of the DB, then you can point to it here
# However I haven't made all the code of this public yet sooo...
APIURL = "https://mobcat.zip/XboxIDs"
CDNURL = "https://raw.githubusercontent.com/MobCat/MobCats-original-xbox-game-list/main/icon"

# Get server ip because I'm to lazy to type it. It should only be manually set on the clients side anyways.
def getIP():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		# doesn't even have to be reachable
		s.connect(('10.255.255.255', 1))
		IP = s.getsockname()[0]
	except:
		IP = '127.0.0.1'
	finally:
		s.close()

	return '.'.join(IP.split('.'))

# Helper func to lookup title ids
def lookupID(titleID):
	try:
		with urllib.request.urlopen(f"{APIURL}/api.php?id={titleID}") as url:
			apiData = json.load(url)
			if 'error' not in apiData:
				XMID = apiData[0]['XMID']
				TitleName = apiData[0]['Full_Name']
			else:
				XMID = '00000000'
				TitleName = 'Unknown Title'
			
	except Exception as e:
		print(e)
		# Lol so yeah, I forgot. If you enter bad data into the api, it just re-directs to the docs page
		# json.load() is trying to load this html docs page as json...
		# also if we dump bad not "URL safe" data into urlopen like 'Hello world' that will crash too, soo cheap catch all hack go burr.
		XMID = '00000000'
		TitleName = 'Unknown Title'

	return XMID, TitleName

########################################################################################################################
async def clientHandler(websocket: wetSocks):
	try:
		# The websocket is already open when this handler is called
		print(f"{int(time.time())} {websocket.remote_address} Xbox connected!")
		
		# Handle messages until xbox disconnects
		async for message in websocket:
			#Debug message
			print(f"{int(time.time())} {websocket.remote_address} {message}")
			#TODO: We should filter user input, but for now fuck it we ball. API already filters input, so it would be just to protect server from bad input.
			dataIn = json.loads(message)
			#PLEASE NOTE: We are doing a XMID lookup based on a title id. this has a 50/50/90 % chance of working. a lot of the time PAL and NTSC have the same title id.
			XMID, TitleName = lookupID(dataIn['id'])
			inTitleID = dataIn['id'].upper()

			# Default presence data
			presenceData = {
				"type": 0, #TODO: Figure out Competing, parties, and the "secret" join match. the latter cant be used with Title info button.
				"details": TitleName,
				"timestamps": {
					"start": int(time.time()),
				},
				"assets": {
					"large_image": f"{CDNURL}/{inTitleID[:4]}/{inTitleID}.png",
					"large_text":  f"TitleID: {dataIn['id']}",
					"small_image": "https://cdn.discordapp.com/avatars/1304454011503513600/6be191f921ebffb2f9a52c1b6fc26dfa",
				},
				"instance": True,
			}

			# Only append the title info button if that title is indeed in the database
			if XMID != "00000000":
				presenceData["buttons"] = [{"label": "Title Info", "url": f"{APIURL}/title.php?{XMID}",}]
			else:
				# Only append custom title name if title is not in db, and we supply a custom name in the first place
				if 'name' in dataIn.keys() and dataIn['name'] != '':
					presenceData['details'] = dataIn['name']
					TitleName = dataIn['name']

			# Now we have some game info.. hopefully.. we can set our discord presence
			presence.set(presenceData)
			print(f"{int(time.time())} Now Playing {dataIn['id']} ({XMID}) - {TitleName}")

			#TODO: Maybe do a check / echo back to xbox for yes, the server got your message, we have set discord presence. or no something went wrong.
			#await websocket.send(f"OK")
			
	except websockets.ConnectionClosedOK:
		print(f"{int(time.time())} {websocket.remote_address} Client disconnected normally")
	except websockets.ConnectionClosedError as e:
		print(f"{int(time.time())} {websocket.remote_address} Client disconnected with error: {e}")
	finally:
		if websocket.closed:
			print(f"{int(time.time())} {websocket.remote_address} Connection closed. Presence cleared.")
			presence.clear() # This kinda does work, just slow for some reason, like 5 secs slow.
			#TODO: If no xbox connection in 10 mins, shutdown the server and clear presence.
            # So you don't get stuck "playing halo" for 2 weeks even know your xbox is off.

########################################################################################################################
async def main():
	# Get server IP
	serverIP = getIP()
	# Create the websocket server
	server = await websockets.serve(clientHandler, serverIP, 1102)
	print(f"Server started on ws://{serverIP}:1102\nWaiting for connection...")
	
	try:
		# run forever
		await asyncio.Future()  
	except KeyboardInterrupt: #BUGBUG: This shit doesn't work, but its the thought that counts... right?
		print("\nShutting down server...")
	finally:
		# Clean shutdown
		presence.close()
		server.close()
		await server.wait_closed()
		print("Server closed")
		exit()

########################################################################################################################
# Server starts here.
print(r'''
      _         _ __ _         _       
__  _| |__   __| / _\ |_  __ _| |_ ___ 
\ \/ / '_ \ / _` \ \| __|/ _` | __/ __|
 >  <| |_) | (_| |\ \ |_  (_| | |_\__ \
/_/\_\_.__/ \__,_\__/\__|\__,_|\__|___/
xbStats Server 20241111
''')
asyncio.run(main())