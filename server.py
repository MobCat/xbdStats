
#!/env/Python3.10.4
#/MobCat (2024)
#/Modified by Rocky5 (2025)

# Install dependencies
# import sys, subprocess, importlib, os
# dependencies = {"discord_rich_presence": "discord_rich_presence==1.1.0", "websockets": "websockets==10.3"}
# for module, package in dependencies.items():
	# try: importlib.import_module(module)
	# except ImportError:
		# with open(os.devnull, "w") as devnull:
			# subprocess.check_call([sys.executable, "-m", "pip", "install", package], stdout=devnull, stderr=devnull)

import asyncio, configparser, json, os, socket, threading, time, urllib.request, websockets
from discordrp import Presence
from websockets.server import WebSocketServerProtocol as wetSocks

clientID = "1304454011503513600" # Discord client ID
presence = Presence(clientID)
smallimage = "https://cdn.discordapp.com/avatars/1304454011503513600/6be191f921ebffb2f9a52c1b6fc26dfa"
showadditionalinfo = 0

APIURL = "https://mobcat.zip/XboxIDs"
CDNURL = "https://raw.githubusercontent.com/MobCat/MobCats-original-xbox-game-list/main/icon"
CONFIG = "Server Settings.ini"

def get_server_config():
	base_path = os.path.dirname(os.path.abspath(__file__))
	config_path = os.path.join(base_path, CONFIG)
	if not os.path.exists(config_path):
		config_path = os.path.join(base_path, '../../../', CONFIG)
	config = configparser.ConfigParser()
	config.read(config_path)
	try:
		server_port = config.getint('server', 'port')
		if 1024 <= server_port <= 65535:
			return server_port
		else:
			print(f"  ERROR: Invalid port {server_port} in config. Using default 1102.")
			return 1102
	except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
		print(f"  ERROR: Unable to retrieve port from {config_path}. Using default 1102.")
		return 1102

# Placed here so above can populate the port
UDP_PORT = get_server_config()
TCP_PORT = UDP_PORT + 1

def getIP():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		s.connect(('10.255.255.255', 1))
		IP = s.getsockname()[0]
	except:
		IP = '127.0.0.1'
	finally:
		s.close()
	return '.'.join(IP.split('.'))

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
		XMID = '00000000'
		TitleName = 'Unknown Title'
	return XMID, TitleName

async def clientHandler(websocket: wetSocks):
	try:
		print(f"  {int(time.time())} {websocket.remote_address} Xbox connected!")
		async for message in websocket:
			print(f"  {int(time.time())} {websocket.remote_address} {message}")
			dataIn = json.loads(message)
			XMID, TitleName = lookupID(dataIn['id'])
			inTitleID = dataIn['id'].upper()

			large_image = f"{CDNURL}/{inTitleID[:4]}/{inTitleID}.png"
			
			try:
				with urllib.request.urlopen(large_image) as response:
					if response.status != 200:
						large_image = smallimage
			except:
				large_image = smallimage

			presenceData = {
				"type": 0,
				"details": TitleName,
				"timestamps": {"start": int(time.time())},
				"assets": {
					"large_image": large_image,
					"large_text": f"TitleID: {dataIn['id']}",
					"small_image": smallimage
				},
				"instance": True,
			}

			if "name" in dataIn and dataIn["name"] and dataIn["name"].strip() and dataIn["name"].lower() != "default.xbe":
				presenceData["details"] = dataIn["name"]
				TitleName = dataIn["name"]
			elif XMID != "00000000":
				presenceData["buttons"] = [{"label": "Title Info", "url": f"{APIURL}/title.php?{XMID}"}]

			presence.set(presenceData)
			print(f"  {int(time.time())} Playing: {TitleName}\n             TitleID: {dataIn['id']} ({XMID})")
	except websockets.ConnectionClosedOK:
		print(f"  {int(time.time())} {websocket.remote_address} Client disconnected normally")
	except websockets.ConnectionClosedError as e:
		print(f"  {int(time.time())} {websocket.remote_address} Client disconnected with error: {e}")
	finally:
		if websocket.closed:
			print(f"  {int(time.time())} {websocket.remote_address} Connection closed. Presence cleared.")
			presence.clear()

# === UDP listener added here ===
def listen_udp():
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind(('0.0.0.0', UDP_PORT))  # Same port as WebSocket
	print(f"  [UDP] Listening for raw relay packets on port {UDP_PORT}...")

	while True:
		data, addr = sock.recvfrom(1024)
		try:
			message = data.decode("utf-8").strip()
			if showadditionalinfo: print(f"  [DEBUG] From {addr}: {message}")
			dataIn = json.loads(message)

			XMID, TitleName = lookupID(dataIn['id'])
			inTitleID = dataIn['id'].upper()

			large_image = f"{CDNURL}/{inTitleID[:4]}/{inTitleID}.png"
			
			try:
				with urllib.request.urlopen(large_image) as response:
					if response.status != 200:
						large_image = smallimage
			except:
				large_image = smallimage

			presenceData = {
				"type": 0,
				"details": TitleName,
				"timestamps": {"start": int(time.time())},
				"assets": {
					"large_image": large_image,
					"large_text": f"TitleID: {dataIn['id']}",
					"small_image": smallimage
				},
				"instance": True,
			}

			if "name" in dataIn and dataIn["name"] and dataIn["name"].strip() and dataIn["name"].lower() != "default.xbe":
				presenceData["details"] = dataIn["name"]
				TitleName = dataIn["name"]
			elif XMID != "00000000":
				presenceData["buttons"] = [{"label": "Title Info", "url": f"{APIURL}/title.php?{XMID}"}]

			presence.set(presenceData)
			print(f"  [UDP-INFO] Playing: {TitleName}\n             TitleID: {dataIn['id']} ({XMID})")

		except Exception as e:
			print(f"  [UDP ERROR] {e}")

def listen_tcp():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind(('0.0.0.0', TCP_PORT))  # WebSocket Port + 1  
	sock.listen(5)
	print(f"  [TCP] Listening for connections on port {TCP_PORT}...\n")

	while True:
		conn, addr = sock.accept()
		try:
			message = conn.recv(1024).decode("utf-8").strip()
			if showadditionalinfo:
				print(f"  [DEBUG] From {addr}: {message}")

			dataIn = json.loads(message)

			XMID, TitleName = lookupID(dataIn['id'])
			inTitleID = dataIn['id'].upper()

			large_image = f"{CDNURL}/{inTitleID[:4]}/{inTitleID}.png"
			try:
				with urllib.request.urlopen(large_image) as response:
					if response.status != 200:
						large_image = smallimage
			except:
				large_image = smallimage

			presenceData = {
				"type": 0,
				"details": TitleName,
				"timestamps": {"start": int(time.time())},
				"assets": {
					"large_image": large_image,
					"large_text": f"TitleID: {dataIn['id']}",
					"small_image": smallimage
				},
				"instance": True,
			}

			if "name" in dataIn and dataIn["name"] and dataIn["name"].strip() and dataIn["name"].lower() != "default.xbe":
				presenceData["details"] = dataIn["name"]
				TitleName = dataIn["name"]
			elif XMID != "00000000":
				presenceData["buttons"] = [{"label": "Title Info", "url": f"{APIURL}/title.php?{XMID}"}]

			presence.set(presenceData)
			print(f"  [TCP-INFO] Playing: {TitleName}\n             TitleID: {dataIn['id']} ({XMID})")

		except Exception as e:
			print(f"  [TCP ERROR] {e}")

		finally:
			conn.close()

# === Main async WebSocket server entry point ===
async def main():
	serverIP = getIP()
	server = await websockets.serve(clientHandler, serverIP, UDP_PORT)
	print(f"  Server started on ws://{serverIP}:{UDP_PORT}\n  Waiting for connection...")

	threading.Thread(target=listen_udp, daemon=True).start()
	threading.Thread(target=listen_tcp, daemon=True).start()

	try:
		await asyncio.Future()
	except KeyboardInterrupt:
		print("\n  Shutting down server...")
	finally:
		presence.close()
		server.close()
		await server.wait_closed()
		print("  Server closed")
		exit()

# Banner + launch
print(r'''
        _         _ __ _         _       
  __  _| |__   __| / _\ |_  __ _| |_ ___ 
  \ \/ / '_ \ / _` \ \| __|/ _` | __/ __|
   >  <| |_) | (_| |\ \ |_  (_| | |_\__ \
  /_/\_\_.__/ \__,_\__/\__|\__,_|\__|___/
  xbdStats Server 20250523
''')

asyncio.run(main())