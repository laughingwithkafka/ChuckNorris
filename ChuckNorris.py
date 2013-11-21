#!/usr/bin/env python

##############################################################################
##  ChuckNorris the IRC bot  ##  created by: persistence                    ##
##############################################################################

##############################################################################
##  USER SETTINGS GO HERE                                                   ##
##############################################################################

# The server and port the bot should connect to.
SERVER = "irc.zempirians.com"
PORT = 6667

# The bot's name on the server.
HANDLE = ""

# The password for the bot to identify itself.
# This should be "" if the bot's nick is not registered
HANDLE_PASSWORD = ""

# The nick of the bot's owner. This user will be able to send the bot commands.
# This user will also receive a private message from the bot once the bot
# connects to the server.
MASTER_NICK = "" # Your real nick goes here to control the bot.

# Auto-join these rooms on connect. It's ok to leave empty.
ROOMS = [ ] 

# File containing one Chuck Norris fact per line.
# These are read when users address the bot in a room.
# The file should probably be unix-formatted (\n line-endings).
CHUCK_NORRIS_FACTS_FILE = "chuck_norris_facts.txt"

##############################################################################
## END OF USER SETTINGS                                                     ##
##############################################################################

import socket       # To build the connection.
import threading    # For the listening thread.
import time         # For delays between commands on connect.
import sys          # For sys.exit().
import random       # For Chuck Norris fact selection.
import lxml.html    # For imgur image titles.


# Global variables that should not be changed by the user. (Not settings.)
ENABLE_IRC_COMMANDS = True
CHUCK_NORRIS_FACTS = []


# Kills all threads
def really_quit():
    # Terminate running threads
    for thread in threading.enumerate():
        if thread.isAlive():
            try:
                thread._Thread__stop()
            except:
                print(str(thread.getName()) + ' could not be terminated')
    sys.exit()


# Logs messages that are sent directly to the bot (as opposed to
# the room/channel) to a file. I did this to examine hack attempts.
def log_message(message):
    log_filename = sys.argv[0] + ".txt"
    log_file = open(log_filename, 'a')
    log_file.write(message + "\n")
    log_file.close()


# Loads the Chuck Norris facts into memory to prevent constant disk access.
def load_chuck_norris_facts():
    f = open(CHUCK_NORRIS_FACTS_FILE, 'r')
    global CHUCK_NORRIS_FACTS
    CHUCK_NORRIS_FACTS = f.readlines()
    f.close()


# Returns a random fact about Chuck Norris.
def random_chuck_norris_fact():
    return random.choice(CHUCK_NORRIS_FACTS)


# Returns the title of a linked imgur image.
def get_imgur_image_title(url):
    original_url = url

    # Modify the url to find the title if it is just a linked image.
    if url.lower()[-4] == ".":
        image_link = url.split("/")[-1]
        image_link = image_link[0:-4]
        url = "http://imgur.com/gallery/" + image_link
    
    t = lxml.html.parse(url)
    image_title = t.find(".//title").text.strip() # .strip() just removes leading and trailing whitespace
    image_title = image_title.replace(" - Imgur", "")
    return image_title


# Takes a IRC message as input.
# Returns a tuple containing sender_nick and room if a user joins the room.
# Returns False if the message was not a JOIN notification.
def is_join(data):
    # :fas!b@FFEB8179.999AE7B1.9E737E40.IP JOIN :#HowToHack
    header = data.split(":")[1]
    room = data.split(":")[2].rstrip()

    command = header.split(" ")[1]
    sender_nick = header.split("!")[0]

    if command.lower() == "join":
        return (sender_nick, room)
    else:
        return False


# Returns sender_nick, recipient, and message from message strings received
# in the regular IRC format.
def parse_message(data):
    header = data.split(":")[1]
    message = data[len(header)+2:].rstrip()
    (sender, msg_type, recipient) = header.split(" ")[0:3]
    sender_nick = sender.split("!")[0]

    #print sender_nick + " -> " + recipient + ": " + message

    return (sender_nick, recipient, message)


# Returns a PRIVMSG command complete with \r\n that you can just s.send()
def build_message(recipient, message):
    return "PRIVMSG %s :%s\r\n" % (recipient, message)


# Listens for incoming data and automatically responds where appropriate.
def listen(s):
    global ENABLE_IRC_COMMANDS

    # Create banned words list for use further down.
    banned_words = ["the", "tickle", "pet", "hug", "creepy", "girl",
                    "depress", "sad", "hate", "hating", "tit",
                    "show me", "kill", "sex", "cry", "troll"]
    
    targeted_nicks = []

    while s:
        try:
            data = s.recv(1024)
            if data != "":
                print data ,

                # Put automatic responses here
                if "PING" in data:
                    n = data.split(" ")[1]
                    response = "PONG " + n 
                    s.send(response + "\r\n")
                    #print response

                # I don't know what to do with server messages yet...
                if data[0] == ":" and ":"+SERVER not in data:
                    (sender_nick, recipient, message) = parse_message(data)

                    # Reply to the whole room if a message was sent to the whole room.
                    # Otherwise reply to the sender via PM.
                    if "#" in recipient:
                        new_recipient = recipient
                    else:
                        log_message(data) # Log PM's from all users
                        new_recipient = sender_nick

                    # Greet people as they join the room.
                    if is_join(data):
                        print 
                        print is_join(data)
                        (sender_nick, new_recipient) = is_join(data)
                        print build_message(new_recipient, "sup %s" % sender_nick)
                        s.send(build_message(new_recipient, "sup %s" % sender_nick))
                        print

                    # Respond to direct messages with Chuck Norris facts.
                    if message[0:len(HANDLE)+1] == (HANDLE + ":") or \
                       message[0:len(HANDLE)+1] == (HANDLE + ",") or \
                       ("sup "+HANDLE).lower() in message.lower() or \
                       ("hello "+HANDLE).lower() in message.lower() or \
                       ("hi "+HANDLE).lower() in message.lower() or \
                       (HANDLE+" is").lower() in message.lower():
                        new_message = random_chuck_norris_fact()
                        s.send(build_message(new_recipient, new_message))

                    # Commands that can only be run by the master nick.
                    if sender_nick == MASTER_NICK and ENABLE_IRC_COMMANDS:
                        # Quit. Obviously.
                        if "!QUIT" == message[0:5]:
                            s.send("QUIT\r\n")
                            s.close()
                            really_quit()

                        # Join a room: !JOIN #RoomName
                        elif "!JOIN" == message[0:5]:
                            room = message.split(" ")[1]
                            s.send("JOIN %s\r\n" % room)

                        # Leave a room. Including room name is optional. 
                        # !PART #RoomName
                        elif "!PART" == message[0:5]:
                            if len(message.split()) > 1:
                                room = message.split(" ")[1]
                            else:
                                room = new_recipient
                            s.send("PART %s\r\n" % room)

                        # Add a word to the list of banned words (saying these
                        # will kick a targeted nick).
                        # !ADDWORD word
                        # Leave off the word to just display current words.
                        elif "!ADDWORD" in message:
                            if len(message.split()) > 1:
                                banned_words.append(message.split(" ")[1].lower())

                            new_message = "banned_words=%s" % banned_words
                            s.send(build_message(new_recipient, new_message))
                            print new_message

                        # Remove a word from the list of banned words.
                        # !DELWORD word
                        elif "!DELWORD" in message:
                            if len(message.split()) > 1:
                                banned_words.remove(message.split(" ")[1].lower())

                            new_message = "banned_words=%s" % banned_words
                            s.send(build_message(new_recipient, new_message))
                            print new_message

                        # Add a targeted nick. !TARGET nick
                        # Leave off the nick to just display current targets.
                        elif "!TARGET" in message:
                            if len(message.split()) > 1:
                                targeted_nicks.append(message.split(" ")[1].lower())
                            
                            new_message = "targeted_nicks=%s" % targeted_nicks
                            s.send(build_message(new_recipient, new_message))
                            print new_message

                        # Remove a nick from the targeted nicks. !UNTARGET nick
                        elif "!UNTARGET" in message:
                            if len(message.split()) > 1:
                                targeted_nicks.remove(message.split(" ")[1].lower())
                            
                            new_message = "targeted_nicks=%s" % targeted_nicks
                            s.send(build_message(new_recipient, new_message))
                            print new_message

                        # Disable IRC commands. This is good for when you go
                        # AFK in case someone gets the brilliant idea to 
                        # kick you and take over your nick. !DISABLE 
                        #
                        # Re-enable commands by typing !ENABLE into the running
                        # console.
                        elif "!DISABLE" in message:
                            ENABLE_IRC_COMMANDS = False
                            s.send(build_message(new_recipient, "IRC commands have been disabled."))


                    # Kick targeted_nicks if they use banned words
                    if sender_nick.lower() in targeted_nicks:
                        word_counter = 0
                        for word in banned_words:
                            if word in message.lower() and "#" in recipient:
                                #reason = "Roundhouse kicked for saying %s!" % word
                                reason = "Roundhouse KICKed by ChuckNorris. You're lucky you're not dead."
                                command = "KICK %s %s %s\r\n" % (recipient, sender_nick, reason)
                                print "\n" + command + "\n"
                                s.send(command)
                                break

                    # If someone says a imgur image, post the title so people know what it is.
                    if "http://i.imgur.com/" in message.lower() or "http://imgur.com/" in message.lower():
                        message_parts = message.split(" ")
                        for part in message_parts:
                            if "imgur.com" in part.lower():
                                image_title = get_imgur_image_title(part)
                                new_message = "[%s] \"%s\"" % (part, image_title)
                                s.send(build_message(new_recipient, new_message))
                                

                else:
                    print data,

                data = ""

        except Exception, e:
            print "-----\nERROR in the receiving thread:"
            print e

    return


def main():
    global ENABLE_IRC_COMMANDS

    load_chuck_norris_facts()
    log_message("====== LOGGING BEGINS ======")

    try:
        ip = socket.gethostbyname(SERVER)
        s = socket.socket()
        s.connect((ip, PORT))

        print "CONNECTED TO %s" % SERVER

        t = threading.Thread(target=listen, args=(s,))
        t.start()

        # Stuff to do after connecting...
        startup_commands = ["NICK %s" % HANDLE,
                            "USER %(handle)s 8 * : %(handle)s" % {"handle": HANDLE}, ]        

        if HANDLE_PASSWORD != "":
            startup_commands.append("PRIVMSG NickServ identify %s" % HANDLE_PASSWORD)

        for room in ROOMS:
            startup_commands.append("JOIN %s" % room)

        startup_commands.append("PRIVMSG %s :I'm here." % MASTER_NICK)

        for cmd in startup_commands:
            s.send(cmd + "\r\n")
            time.sleep(2)
            print cmd

        # Wait for user input on the console
        while True:
            user_in = raw_input("")

            # User defined commands
            if user_in == "!ENABLE":
                ENABLE_IRC_COMMANDS = True
                print "<<< IRC commands have been ENABLED. >>>"
            elif user_in == "!DISABLE":
                ENABLE_IRC_COMMANDS = False
                print "<<< IRC commands have been DISABLED. >>>"

            # Commands that should be passed on to the server.
            else:    
                s.send(user_in + "\r\n")

                # Handle manually entered QUIT command
                if user_in[0:4] == "QUIT":
                    really_quit()

    except Exception, e:
        print "-----\nERROR in the main function:"
        print e
    finally:
        try:
            s.send("QUIT")
        except:
            pass
        s.close()

        exit()


if __name__ == "__main__":
    main()