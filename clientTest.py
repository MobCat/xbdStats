#!/env/Python3.10.4
#/MobCat (2024)

# This is some very basic and shit code to send a basic message to the server for testing
# all we have to do to tell the server we are running a game is 
# open the web socket, send title id as text message, keep the socket open while we play
# if the socket closes, the presence data is cleared.
# I'm trying to handle, game changes, IGR and just turning off the console in the easiest way possible.
# if socket is open and connected, xbox is running.
# if message was sent, we are playing that game. And await a new message to change game.
# if socket is closed, xbox is missing or off. reset presence.

import asyncio, websockets

# Change this to whatever the server ws://ip is.
serverIP = '192.168.1.87'
#dataOut  = {}

async def sendMessages():
	try:
		async with websockets.connect(f'ws://{serverIP}:1102') as websocket:
			while True:
				message = await asyncio.get_event_loop().run_in_executor(None, input, "Enter TitleID (or 'q' to quit): ")
				#dataOut['id'] = message
				dataOut = '{"id": "'+message+'"}'
				if message.lower() == 'q':
					await websocket.close()
					break
				await websocket.send(dataOut)
	except ConnectionRefusedError:
		print("ERROR: The xbdStats server is missing or not ready.\nReboot the server and try again.")


asyncio.run(sendMessages())