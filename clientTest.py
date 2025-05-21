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

async def sendMessages():
	serverIP = get_server_ip()
	if not serverIP:
		return
	is_ready = await server_connect(serverIP)
	if not is_ready:
		return
	try:
		clear_screen()
		async with connect(f'ws://{serverIP}:1102') as websocket:
			while True:
				message = await asyncio.get_event_loop().run_in_executor(None, input, "Enter TitleID (or 'q' to quit): ")
				dataOut = '{"id": "'+message+'"}'
				if message.lower() == 'q':
					await websocket.close()
					break
				await websocket.send(dataOut)
	except ConnectionRefusedError:
		print("ERROR: The xbdStats server is missing or not ready.\nReboot the server and try again.")

def clear_screen():
	if os.name == 'nt':
		os.system('cls')
	else:
		os.system('clear')

def get_server_ip():
	base_path = os.path.dirname(os.path.abspath(__file__))
	config_path = os.path.join(base_path, 'clientTest_IP.ini')
	if not os.path.exists(config_path):
		config_path = os.path.join(base_path, '../../../', 'clientTest_IP.ini')
	config = configparser.ConfigParser()
	config.read(config_path)
	try:
		return config.get('server', 'ip')
	except (configparser.NoSectionError, configparser.NoOptionError):
		print(f"ERROR: Unable to retrieve server IP from {config_path}")
		return None

async def server_connect(serverIP, retries=10, delay=2):
	for attempt in range(retries):
		try:
			async with connect(f'ws://{serverIP}:1102'):
				return True
		except:
			print(f"Retrying: {attempt + 1}/{retries}")
			await asyncio.sleep(delay)
	print("ERROR: Server is not running?")
	return False

asyncio.run(sendMessages())