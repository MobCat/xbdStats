# xbdStats
Discord now playing info for og xbox<br>
<img src="https://raw.githubusercontent.com/MobCat/xbdStats/refs/heads/main/img/Discord.jpg" width="350">
> [!WARNING]  
> This project is a "PoC".<br>
> Just making sure this is even possible, let alone how to accomplish it in a sane and easy to use manor.<br>
> So this is not a complete ready to use project... yet.<br>
> Input and code is welcome though.

This project is a PoC for getting currently running title info from an og xbox into your discord client<br>
so your friends on discord can see the games you are playing on your og xbox, the same way they can see games you are playing on pc or current xbox.<br>
This project is Proof of Concept as we have the "Server" setup, the software that takes the title id and tells discord that you are playing xbox,<br>
but we don't have the "client" software setup yet, the how do we get the currently running title info out of your xbox done yet.

# How to test
(There is no how to use yet as this project is not "finished", but you can test it out though)<br>
0. If you don't have python 3 set up, do that now. also download the `requirements.txt` and run `pip install -r requirements.txt`<br>
to pip install `discord_rich_presence` and `websockets` for this project.<br>
1. Download the `server.py` and `testClient.py` from this repo to a folder on your computer, shouldn't matter where.
1. Make sure the discord app is running on your computer.
2. Now run `python server.py` from the folder where you downloaded the `server.py` to
3. When the server is running you should see a message like this<br>
```
Server started on ws://192.168.1.87:1102
Waiting for connection...
```
Note the `ws://192.168.1.87` this is the ip of our server, we need this for later.<br>
4. By later I mean now, open the `testClient.py` in a notepad or whatever IDE you like to use.<br>
we need to edit `serverIP = '192.168.1.87'` to the ip that was listed in your server screen. Then save and close.<br><br>
5. now run `python testClient.py` It will automatically try and connect to the server at the `serverIP` ip.<br><br>
6. once connected the server should say something like `('192.168.1.87', 54130) Xbox connected!`<br>
And will now ask you to enter a title id. You can see a list of title ids <a href="https://mobcat.zip/XboxIDs/">here</a><br>
<sup>(You can enter the title id in uppercase or lowercase it doesn't matter)</sup><br>
If you enter an id that's not in the database, your status will be set to `Playing Unknown Title`<br>
Once you have sent a title id to the server, the server will now say something like<br>
`Now Playing 4D530064 (MS10003W) - Halo 2`<br>
and you can see in discord when under your name it should say `Playing Xbox`<br>
If you click on your name, you can see more details about the "Playing Xbox" activity, in this case, playing halo 2.<br>
If you enter `q` as a title id to quit or otherwise disconnect from the server, your presence will be cleared on discord.<br><br>

<b>Side quest:</b><br>
You can download "WebSocket Tester" on android, set the ip to the one listed from your server, set the port to 1102 and click connect<br>
then you can enter a title id as a message from here. This will test to make sure this thing is working over your local network and you don't have firewall shenanigans to figure out.
