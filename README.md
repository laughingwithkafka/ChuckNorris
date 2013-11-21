ChuckNorris (the IRC bot)
-------------------------

**Basic instructions:**

1. Edit ChuckNorris.py and set the appropriate settings at the top.
2. Run like "python ChuckNorris.py"
3. You can interact with the bot either through IRC (!COMMAND) or through the
console. Anything typed into the console that does not begin with a ! will be
passed directly to the server, so you can do pretty much whatever you want.

**Known bugs:**

* Right now when you !QUIT from IRC, the bot doesn't exit cleanly. I think this 
is because the thread closes and closes the socket connection before the main 
function closes. QUIT from the command line works just fine though. Pressing
ENTER in the command line after a funky !QUIT closes the program with an error. 

**Features to add:**

* Voicemail/leaving messages for users (that was the point all along).
* PM logs need timestamps.
* Need to add a !DELWORD command to complement !ADDWORD.
* Random kick messages (the eyes of the ranger are upon you...)
* Random quit messages
* After two kicks, should start kills