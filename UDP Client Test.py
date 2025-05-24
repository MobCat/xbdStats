#!/env/Python3.10.4
#/MobCat (2024)
#/Modified by Rocky5 (2025)

# This is some very basic and shit code to send a basic message to the server for testing
# all we have to do to tell the server we are running a game is 
# open the web socket, send title id as text message, keep the socket open while we play
# if the socket closes, the presence data is cleared.
# I'm trying to handle, game changes, IGR and just turning off the console in the easiest way possible.
# if socket is open and connected, xbox is running.
# if message was sent, we are playing that game. And await a new message to change game.
# if socket is closed, xbox is missing or off. reset presence.

import asyncio
import configparser
import os
from websockets.client import connect

CONFIG = "Client Test Settings.ini"

def get_server_config():
	base_path = os.path.dirname(os.path.abspath(__file__))
	config_path = os.path.join(base_path, CONFIG)
	if not os.path.exists(config_path):
		config_path = os.path.join(base_path, '../../../', CONFIG)
	config = configparser.ConfigParser()
	config.read(config_path)
	try:
		server_ip = config.get('server', 'ip')
		server_port = config.getint('server', 'port')
		if 1024 <= server_port <= 65535:
			return server_ip, server_port
		else:
			print(f"  ERROR: Invalid port {server_port} in config. Using default 1102.")
			return server_ip, 1102
		return server_ip, server_port
	except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
		print(f"  ERROR: Unable to retrieve server configuration from {config_path}")
		return None, None

async def sendMessages():
	serverIP, UDP_PORT = get_server_config()
	if not serverIP or not UDP_PORT:
		return
	is_ready = await server_connect(serverIP, UDP_PORT)
	if not is_ready:
		return
	try:
		clear_screen()
		async with connect(f'ws://{serverIP}:{UDP_PORT}') as websocket:
			while True:
				message = await asyncio.get_event_loop().run_in_executor(None, input, "  Enter TitleID (or 'q' to quit): ")
				dataOut = '{"id": "'+message+'"}'
				if message.lower() == 'q':
					await websocket.close()
					break
				await websocket.send(dataOut)
	except ConnectionRefusedError:
		print("  ERROR: The xbdStats server is missing or not ready.\nReboot the server and try again.")

def clear_screen():
	if os.name == 'nt':
		os.system('cls')
	else:
		os.system('clear')

async def server_connect(serverIP, UDP_PORT, retries=10, delay=2):
	for attempt in range(retries):
		try:
			async with connect(f'ws://{serverIP}:{UDP_PORT}'):
				return True
		except:
			print(f"  Retrying: {attempt + 1}/{retries}")
			await asyncio.sleep(delay)
	print("  ERROR: Server is not running?")
	return False

asyncio.run(sendMessages())