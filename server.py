
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

# Show additional info
showadditionalinfo = 0

CLIENTID = "1304454011503513600" # Discord client ID
APIURL = "https://mobcat.zip/XboxIDs"
CDNURL = "https://raw.githubusercontent.com/MobCat/MobCats-original-xbox-game-list/main/icon"
SMALLIMAGE = "https://cdn.discordapp.com/avatars/1304454011503513600/6be191f921ebffb2f9a52c1b6fc26dfa"
CONFIG = "Server Settings.ini"

# Only start discord on windows, I'm not sure how to do it on Linux/Mac as don't know where stuff is installed.
if os.name == 'nt':
	try:
		presence = Presence(CLIENTID)
	except FileNotFoundError:
		# Start Discord
		local = os.getenv("LOCALAPPDATA")
		discord_path = fr"{local}\Discord\Update.exe"
		
		# Check for Discord
		while os.system('tasklist | findstr Discord.exe > nul 2>&1') != 0:
			if os.path.exists(discord_path):
				os.system(f'start "" "{discord_path}" --processStart Discord.exe')
				print("Starting Discord...")
				time.sleep(5)
			else:
				print(f"Error: Discord not found at:\n{discord_path}")
				exit()
			time.sleep(1)

		# Loop
		while True:
			try:
				presence = Presence(CLIENTID)
				os.system('cls')
				break
			except FileNotFoundError:
				print("Error: Waiting for Discord to fully start.")
				time.sleep(5)
else:
	presence = Presence(CLIENTID)

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
		infolabel = int(time.time())
		print(f"  {int(time.time())} {websocket.remote_address} Xbox connected!")
		async for message in websocket:
			print(f"  {int(time.time())} {websocket.remote_address} {message}")
			dataIn = json.loads(message)
			if not dataIn.get('id'):
				print(f"  {infolabel} Presence cleared.")
				presence.clear()
				continue
			process_message(dataIn, int(time.time()))
	except websockets.ConnectionClosedOK:
		print(f"  {int(time.time())} {websocket.remote_address} Client disconnected normally")
	except websockets.ConnectionClosedError as e:
		print(f"  {int(time.time())} {websocket.remote_address} Client disconnected with error: {e}")
	finally:
		if websocket.closed:
			print(f"  {int(time.time())} {websocket.remote_address} Connection closed. Presence cleared.")
			presence.clear()

# === UDP listener ===
def listen_udp():
	infolabel = '[UDP-INFO]'
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind(('0.0.0.0', UDP_PORT))
	print(f"  [UDP] Listening for raw relay packets on port {UDP_PORT}...")

	while True:
		data, addr = sock.recvfrom(1024)
		try:
			message = data.decode("utf-8").strip()
			if showadditionalinfo: print(f"  [DEBUG] From {addr}: {message}")
			dataIn = json.loads(message)
			if not dataIn.get('id'):
				print(f"  {infolabel} Presence cleared.")
				presence.clear()
				continue
			process_message(dataIn, '[UDP-INFO]')
		except Exception as e:
			print(f"  [UDP ERROR] {e}")

# === TCP listener ===
def listen_tcp():
	infolabel = '[TCP-INFO]'
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind(('0.0.0.0', TCP_PORT))
	sock.listen(5)
	print(f"  [TCP] Listening for connections on port {TCP_PORT}...")

	while True:
		conn, addr = sock.accept()
		try:
			message = conn.recv(1024).decode("utf-8").strip()
			if showadditionalinfo: print(f"  [DEBUG] From {addr}: {message}")
			dataIn = json.loads(message)
			if not dataIn.get('id'):
				print(f"  {infolabel} Presence cleared.")
				presence.clear()
				continue
			process_message(dataIn, infolabel)
		except Exception as e:
			print(f"  [TCP ERROR] {e}")
		finally:
			conn.close()

def process_message(dataIn, variable):
	XMID, TitleName = lookupID(dataIn['id'])
	inTitleID = dataIn['id'].upper()

	large_image = f"{CDNURL}/{inTitleID[:4]}/{inTitleID}.png"
	
	try:
		with urllib.request.urlopen(large_image) as response:
			if response.status != 200:
				large_image = SMALLIMAGE
	except:
		large_image = SMALLIMAGE

	presenceData = {
		"type": 0,
		"details": TitleName,
		"timestamps": {"start": int(time.time())},
		"assets": {
			"large_image": large_image,
			"large_text": f"TitleID: {dataIn['id']}",
			"small_image": SMALLIMAGE
		},
		"instance": True,
	}

	if "name" in dataIn and dataIn["name"] and dataIn["name"].strip() and dataIn["name"].lower() != "default.xbe":
		presenceData["details"] = dataIn["name"]
		TitleName = dataIn["name"]
	elif XMID != "00000000":
		presenceData["buttons"] = [{"label": "Title Info", "url": f"{APIURL}/title.php?{XMID}"}]

	presence.set(presenceData)
	print(f"  {variable} Playing: {TitleName}\n             TitleID: {dataIn['id']} ({XMID})")

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
  xbdStats Server 20250524
''')

asyncio.run(main())