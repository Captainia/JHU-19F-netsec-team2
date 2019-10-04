"""
Escape Room Core
"""
import random, sys, asyncio
import time

def create_container_contents(*escape_room_objects):
    return {obj.name: obj for obj in escape_room_objects}
    
def listFormat(object_list):
    l = ["a "+object.name for object in object_list if object["visible"]]
    return ", ".join(l)
#@
class Trap: 
    def __init__(self, output):
        self.output = output
    def initialTrap(self,output):
        self.TRAP = 0
        self.ROAD = 1
        self.PEOPLE = 2
        self.EXIT = 3
        self.DEAD = 10
        self.LIVE = 11
        self.ESCAPED = 12
        self.maplist=[[0,0,0],
                      [0,0,0],
                      [0,0,0]]
        self.playerPosition = [random.choice([r for r in range(2)]),random.choice([c for c in range(3)])]
        self.exitPosition =[2,1]
        self.playerStatus = self.LIVE
        self.output = output
        
        
    def changeMap(self):
        self.generateMap()
        return self.drawMap()

    def getmap(self):
        return self.maplist
    

    def generateMap(self):
        for r in range(3):
            for c in range(3):
                if r == self.playerPosition[0] and c == self.playerPosition[1]:
                    self.maplist[r][c] = self.PEOPLE
                #self.maplist[r][c] != self.PEOPLE and self.maplist[r][c] != self.EXIT:
                elif r == self.exitPosition[0] and c == self.exitPosition[1]:
                    self.maplist[r][c] = self.EXIT
                else:
                    self.maplist[r][c] =  random.choice([self.TRAP,self.ROAD])

    

    def roomContent(self,content):
        if content == self.TRAP:
            return "X"
        elif content == self.PEOPLE:
            return "*"
        elif content == self.EXIT:
            return "@"
        else:
            return " "
        
    def drawMap(self):
        trapmap = "You are in trap room. If you want to go back, you need to move to EXIT.If you go into TRAP, you will die.\n"
        trapmap += "YOU--*  EXIT--@ TRAP--X\n"
        trapmap += "MOVE INPUT: up, down, left, right, wait.\n"
        trapmap += '-----------\n'
        trapmap +=' '+ self.roomContent(self.maplist[0][0]) + ' | ' + self.roomContent(self.maplist[0][1])+ ' | ' + self.roomContent(self.maplist[0][2])+"\n"
        trapmap += '-----------\n'
        trapmap +=' '+ self.roomContent(self.maplist[1][0]) + ' | ' + self.roomContent(self.maplist[1][1])+ ' | ' + self.roomContent(self.maplist[1][2])+"\n"
        trapmap += '-----------\n'
        trapmap +=' '+ self.roomContent(self.maplist[2][0]) + ' | ' + self.roomContent(self.maplist[2][1])+ ' | ' + self.roomContent(self.maplist[2][2])+"\n"
        trapmap += '-----------\n'
        return trapmap
    
    def isEscape(self):
        if self.playerPosition[0] == self.exitPosition[0] and self.playerPosition[1] == self.exitPosition[1]:
            self.playerStatus = self.ESCAPED
        elif self.maplist[self.playerPosition[0]][self.playerPosition[1]] == self.TRAP:
            self.playerStatus = self.DEAD
        else:
            pass
    def commandHandler(self,command):
        if command == "up":
            #print(command)
            nextY = self.playerPosition[0] -1
            if nextY >= 0 and nextY <= 2:
                self.maplist[self.playerPosition[0]][self.playerPosition[1]] = self.ROAD
                self.playerPosition[0] = nextY
            else:
                self.output("Can't go that way")
                
        elif command == "down":
            #print(command)
            nextY = self.playerPosition[0] + 1
            if nextY >= 0 and nextY <= 2:
                self.maplist[self.playerPosition[0]][self.playerPosition[1]] = self.ROAD
                self.playerPosition[0] = nextY

            else:
                self.output("Can't go that way")
                
        elif command == "left":
            #print(command)
            nextX = self.playerPosition[1] -1
            if nextX >= 0 and nextX <= 2:
                self.maplist[self.playerPosition[0]][self.playerPosition[1]] = self.ROAD
                self.playerPosition[1] = nextX
            else:
                self.output("Can't go that way")
                
        elif command == "right":
            #print(command)
            nextX = self.playerPosition[1] +1
            if nextX >= 0 and nextX <= 2:
                self.maplist[self.playerPosition[0]][self.playerPosition[1]] = self.ROAD
                self.playerPosition[1] = nextX
            else:
                self.output("Can't go that way")
                
        elif command == "wait":
            self.output("Waiting")
        else:
            self.output("what to do?")
        self.isEscape()
        self.output(self.changeMap())
        
    #def output(self,string0):
     #   print(string0)
#@
     
class EscapeRoomObject:
    def __init__(self, name, **attributes):
        self.name = name
        self.attributes = attributes
        self.triggers = []
        
    def do_trigger(self, *trigger_args):
        return [event for trigger in self.triggers for event in [trigger(self, *trigger_args)] if event]
        
    def __getitem__(self, object_attribute):
        return self.attributes.get(object_attribute, False)
        
    def __setitem__(self, object_attribute, value):
        self.attributes[object_attribute] = value
        
    def __repr__(self):
        return self.name
        
class EscapeRoomCommandHandler:
    def __init__(self, room, player, output=print):
        self.room = room
        self.player = player
        self.output = output
        
    def _run_triggers(self, object, *trigger_args):
        for event in object.do_trigger(*trigger_args):
            self.output(event)
        
    def _cmd_look(self, look_args):
        look_result = None
        if len(look_args) == 0:
            object = self.room
        else:
            object = self.room["container"].get(look_args[-1], self.player["container"].get(look_args[-1], None))
        
        if not object or not object["visible"]:
            look_result = "You don't see that here."
        elif object["container"] != False and look_args and "in" == look_args[0]:
            if not object["open"]:
                look_result = "You can't do that! It's closed!"
            else:
                look_result = "Inside the {} you see: {}".format(object.name, listFormat(object["container"].values()))
        else:
            self._run_triggers(object, "look")
            look_result = object.attributes.get("description","You see nothing special")
        self.output(look_result)
        
    def _cmd_unlock(self, unlock_args):
        unlock_result = None
        if len(unlock_args) == 0:
            unlock_result = "Unlock what?!"
        elif len(unlock_args) == 1:
            unlock_result = "Unlock {} with what?".format(unlock_args[0])
        
        else:
            object = self.room["container"].get(unlock_args[0], None)
            unlock = False
            
            if not object or not object["visible"]:
                unlock_result = "You don't see that here."
            elif not object["keyed"] and not object["keypad"]:
                unlock_result = "You can't unlock that!"
            elif not object["locked"]:
                unlock_result = "It's already unlocked"
            
            elif object["keyed"]:
                unlocker = self.player["container"].get(unlock_args[-1], None)
                if not unlocker:
                    unlock_result = "You don't have a {}".format(unlock_args[-1])                    
                elif unlocker not in object["unlockers"]:
                    unlock_result = "It doesn't unlock."
                else:
                    unlock = True
                    
            elif object["keypad"]:
                # TODO: For later Exercise
                pass
            
            if unlock:
                unlock_result = "You hear a click! It worked!"
                object["locked"] = False
                self._run_triggers(object, "unlock", unlocker)
        self.output(unlock_result)
        
    def _cmd_open(self, open_args):
        """
        Let's demonstrate using some ands instead of ifs"
        """
        if len(open_args) == 0:
            return self.output("Open what?")
        object = self.room["container"].get(open_args[-1], None)
        
        success_result = "You open the {}.".format(open_args[-1])
        open_result = (
            ((not object or not object["visible"]) and "You don't see that.") or
            ((object["open"])                      and "It's already open!") or
            ((object["locked"])                    and "It's locked") or
            ((not object["openable"])              and "You can't open that!") or
                                                       success_result)
        if open_result == success_result:
            object["open"] = True
            self._run_triggers(object, "open")
        self.output(open_result)

    def _cmd_get(self, get_args):
        if len(get_args) == 0:
            get_result = "Get what?"
        elif self.player["container"].get(get_args[0], None) != None:
            get_result = "You already have that"
        else:
            if len(get_args) > 1:
                container = self.room["container"].get(get_args[-1], None)
            else:
                container = self.room
            object = container["container"] and container["container"].get(get_args[0], None) or None
            
            success_result = "You got it"
            get_result = (
                ((not container or container["container"] == False)and "You can't get something out of that!") or
                ((container["openable"] and not container["open"]) and "It's not open.") or
                ((not object or not object["visible"])             and "You don't see that") or
                ((not object["gettable"])                          and "You can't get that.") or
                                                                   success_result)
            
            if get_result == success_result:
                container["container"].__delitem__(object.name)
                self.player["container"][object.name] = object
                self._run_triggers(object, "get",container)
        self.output(get_result)

    def _cmd_hit(self, hit_args):
        if not hit_args:
            return self.output("What do you want to hit?")
        target_name = hit_args[0]
        with_what_name = None
        if len(hit_args) != 1:
            with_what_name = hit_args[-1]
        
        target = self.room["container"].get(target_name, None)
        if not target or not target["visible"]:
            return self.output("You don't see a {} here.".format(target_name))
        if with_what_name:
            with_what = self.player["container"].get(with_what_name, None)
            if not with_what:
                return self.output("You don't have a {}".format(with_what_name))
        else:
            with_what = None
        
        if not target["hittable"]:
            return self.output("You can't hit that!")
        else:
            self.output("You hit the {} with the {}".format(target_name, with_what_name))
            self._run_triggers(target, "hit", with_what)
    
    def _cmd_enter(self, enter_args):
        if str(enter_args) == time.strftime("%H%M",time.localtime()):
            self.output('Great! The code matches! The chest is now open')
            object = self.room["container"].get("chest", None)
            self._run_triggers(object, "_code_correct_")
            
        else:
            object = self.room["container"].get("chest", self.player["container"].get("chest", None))
            self._run_triggers(object, "look")
            self.output("WRONG Answer! You have {} times remaining!".format(self.room["container"]["codedlock"]["chance"]))
            self.output("The message shines again: .-- .... .- - / - .. -- . / .. ... / .. - ..--.. ")
            self.output("Please enter the code (4 digits):")
            
            self._run_triggers(self.room, "_code_wrong_")
            
            
    def _cmd_press(self, press_args):
        if not press_args:
            return self.output("What do you want to press?")
        target_name = press_args[0]
        target = self.room["container"].get(target_name, None)
        if not target["pressable"]:
            return self.output("You can't press that!")
        else:
            if traget_name == "redbutton":
                self.output("You press the {}".format(target_name))
                
            elif traget_name == "bluebutton":#@
                target["pressable"] = False
                self.isintrap =True#@
            self._run_triggers(target, "press")
        

    def _cmd_inventory(self, inventory_args):
        """
        Use return statements to end function early
        """
        if len(inventory_args) != 0:
            self.output("What?!")
            return
            
        items = ", ".join(["a "+item for item in self.player["container"]])
        self._run_triggers(object, "inventory")
        self.output("You are carrying {}".format(items))
        
    def command(self, command_string):
        # no command
        if command_string.strip == "":
            return self.output("")
        
        if command_string.isdigit():
            self._cmd_enter(int(command_string))
            return
            
        command_args = command_string.split(" ")
        function = "_cmd_"+command_args[0]
        
        # unknown command
        if not hasattr(self, function):
            return self.output("You don't know how to do that.")
            
        # execute command dynamically
        getattr(self, function)(command_args[1:])
        self._run_triggers(self.room, "_post_command_", *command_args)
        
def create_room_description(room):
    room_data = {
        "mirror": room["container"]["mirror"].name,
        "clock_time": room["container"]["clock"]["time"],
        "interesting":"There are a bluebutton on the wall and a redbutton on the floor that seems pressable."#@
    }
    for item in room["container"].values():
        if item["interesting"]:
            room_data["interesting"]+= "\n\t"+short_description(item)
    if room_data["interesting"]:
        room_data["interesting"] = "\nIn the room you see:"+room_data["interesting"]
    return """You are in a locked room. There is only one door
and it is locked. Above the door is a clock that reads {clock_time}.
Across from the door is a large {mirror}. Below the mirror is an old chest.

The room is old and musty and the floor is creaky and warped.{interesting}""".format(**room_data)

def create_door_description(door):
    description = "The door is strong and highly secured."
    if door["locked"]: description += " The door is locked."
    return description
    
def create_mirror_description(mirror, room):
    description = "You look in the mirror and see yourself."
    if "hairpin" in room["container"]:
        description += ".. wait, there's a hairpin in your hair. Where did that come from?"
    return description
    
def create_chest_description(chest, room):
    description = """An old chest. It looks worn, 
    but it's still sturdy.
    """
    if chest["locked"]:
        description += """ And it appears to be locked by a coded lock. 
        You can see the description on the lock: 
        .-- .... .- - / - .. -- . / .. ... / .. - ..--.. 
        Please enter the code to the coded lock: ({} times remaining):""".format(room["container"]["codedlock"]["chance"])
    elif chest["open"]:
        description += " The chest is open."
    return description

def create_flyingkey_description(flyingkey):
    description = "A golden flying key with silver wings shimmering in the light"
    description += " is currently resting on the " + flyingkey["location"]
    return description
    
def create_flyingkey_short_description(flyingkey):
    return "A flying key on the " + flyingkey["location"]
    
def advance_time(room, clock):
    event = None
    clock["time"] = clock["time"] - clock["time_decr"]
    if clock["time"] <= 0:
        for object in room["container"].values():
            if object["alive"]:
                object["alive"] = False
        event = "Oh no! The clock reaches 0 and a deadly gas fills the room!"
    room["description"] = create_room_description(room)
    return event

def decrease_lock_chance(room, codedlock):
    event = None
    codedlock["chance"] = codedlock["chance"] - 1
    if codedlock["chance"] == 0:
        for object in room["container"].values():
            if object["alive"]:
                object["alive"] = False
        event = "Sadly the coded lock exploded, you are severely injured. You cannot move, waiting the clock to hit zero ..."

    room["description"] = create_room_description(room)
    return event
    
def flyingkey_hit_trigger(room, flyingkey, key, output):
    if flyingkey["location"] == "ceiling":
        output("You can't reach it up there!")
    elif flyingkey["location"] == "floor":
        output("It's too low to hit.")
    else:
        flyingkey["flying"] = False
        del room["container"][flyingkey.name]
        room["container"][key.name] = key
        output("The flying key falls off the wall. When it hits the ground, it's wings break off and you now see an ordinary key.")
        
        
def redbutton_trigger(clock, door, output):
    if clock["time_decr"] == 1:
        clock["time_decr"] += 1
        output("The time on the clock decreases faster.")
    elif clock["time_decr"] == 2:
        clock["time_decr"] += 3
        output("The time on the clock decreases even faster.")
    elif clock["time_decr"] == 5:
        clock["time_decr"] += 7
        output("The time on the clock decreases fast af now.")
        door["locked"] = False
        output("You hear a lock click.")
        
        
def short_description(object):
    if not object["short_description"]: return "a "+object.name
    return object["short_description"]
                
class EscapeRoomGame:
    def __init__(self, command_handler_class=EscapeRoomCommandHandler, output=print):
        self.room, self.player = None, None
        self.output = output
        self.command_handler_class = command_handler_class
        self.command_handler = None
        self.agents = []
        self.status = "void"
        self.trap = Trap(self.output)#@
        self.isintrap = False#@
        
    def create_game(self, cheat=False):
        clock =  EscapeRoomObject("clock",  visible=True, time=100, time_decr=1)
        codedlock = EscapeRoomObject('codedlock', visible=True, chance=5) #Define coded lock on the chest
        mirror = EscapeRoomObject("mirror", visible=True)
        hairpin= EscapeRoomObject("hairpin",visible=False, gettable=True)
        key    = EscapeRoomObject("key",    visible=True, gettable=True, interesting=True)
        door  =  EscapeRoomObject("door",   visible=True, openable=True, open=False, keyed=True, locked=True, unlockers=[key])
        chest  = EscapeRoomObject("chest",  visible=True, openable=True, open=False, keyed=True, locked=True, unlockers=[])
        room   = EscapeRoomObject("room",   visible=True)
        player = EscapeRoomObject("player", visible=False, alive=True)
        hammer = EscapeRoomObject("hammer", visible=True, gettable=True)
        redbutton = EscapeRoomObject("redbutton", visible=True, interesting=True, pressable=True)#tiger
        flyingkey = EscapeRoomObject("flyingkey", visible=True, flying=True, hittable=False, smashers=[hammer], interesting=True, location="ceiling")
        bluebutton = EscapeRoomObject("bluebutton", visible=True, pressable=True,trap = self.trap)#@ trap in here
        
        # setup containers
        player["container"]= {}
        chest["container"] = create_container_contents(hammer)
        room["container"]  = create_container_contents(codedlock, player, door, clock, mirror, hairpin, chest, flyingkey, redbutton,bluebutton)#@

        
        # set initial descriptions (functions)
        door["description"]    = create_door_description(door)
        mirror["description"]  = create_mirror_description(mirror, room)
        chest["description"]   = create_chest_description(chest, room)
        flyingkey["description"] = create_flyingkey_description(flyingkey)
        flyingkey["short_description"] = create_flyingkey_short_description(flyingkey)
        key["description"] = "a golden key, cruelly broken from its wings."
        
        # the room's description depends on other objects. so do it last
        room["description"]    = create_room_description(room)

        mirror.triggers.append(lambda obj, cmd, *args: (cmd == "look") and hairpin.__setitem__("visible",True))
        mirror.triggers.append(lambda obj, cmd, *args: (cmd == "look") and mirror.__setitem__("description", create_mirror_description(mirror, room)))
        door.triggers.append(lambda obj, cmd, *args: (cmd == "unlock") and door.__setitem__("description", create_door_description(door)))
        door.triggers.append(lambda obj, cmd, *args: (cmd == "open") and room["container"].__delitem__(player.name))
        room.triggers.append(lambda obj, cmd, *args: (cmd == "_post_command_") and advance_time(room, clock))
        room.triggers.append(lambda obj, cmd, *args: (cmd == "_code_wrong_") and decrease_lock_chance(room, codedlock))
        flyingkey.triggers.append((lambda obj, cmd, *args: (cmd == "hit" and args[0] in obj["smashers"]) and flyingkey_hit_trigger(room, flyingkey, key, self.output)))
        chest.triggers.append(lambda obj, cmd, *args: (cmd == "_code_correct_") and chest.__setitem__("locked",False))
        chest.triggers.append(lambda obj, cmd, *args: (cmd == "_code_correct_") and chest.__setitem__("description", create_chest_description(chest, room)))
        chest.triggers.append(lambda obj, cmd, *args: (cmd == "open") and chest.__setitem__("open",True))
        chest.triggers.append(lambda obj, cmd, *args: (cmd == "open") and chest.__setitem__("description", create_chest_description(chest, room)))
        chest.triggers.append(lambda obj, cmd, *args: (cmd == "look") and chest.__setitem__("description", create_chest_description(chest, room)))
        bluebutton.triggers.append(lambda obj, cmd, *args: (cmd == "press") and self.startTrap())#@
        redbutton.triggers.append((lambda obj, cmd, *args: (cmd == "press") and redbutton_trigger(clock, door, self.output)))

        
        # TODO, the chest needs some triggers. This is for a later exercise
        
        self.room, self.player = room, player
        self.command_handler = self.command_handler_class(room, player, self.output)
        self.agents.append(self.flyingkey_agent(flyingkey))
        self.status = "created"
        
    async def flyingkey_agent(self, flyingkey):
        random.seed(0) # this should make everyone's random behave the same.
        await asyncio.sleep(5) # sleep before starting the while loop
        while self.status == "playing" and flyingkey["flying"]:
            locations = ["ceiling","floor","wall"]
            locations.remove(flyingkey["location"])
            random.shuffle(locations)
            next_location = locations.pop(0)
            old_location = flyingkey["location"]
            flyingkey["location"] = next_location
            flyingkey["description"] = create_flyingkey_description(flyingkey)
            flyingkey["short_description"] = create_flyingkey_short_description(flyingkey)
            flyingkey["hittable"] = next_location == "wall"
            self.output("The {} flies from the {} to the {}".format(flyingkey.name, old_location, next_location))
            for event in self.room.do_trigger("_post_command_"):
                self.output(event)
            await asyncio.sleep(5)
    
    def start(self):
        self.status = "playing"
        self.output("Where are you? You don't know how you got here... Were you kidnapped? Better take a look around")
    #@
    def startTrap(self):
        self.isintrap = True
        self.trap.initialTrap(self.output)
        self.output(self.trap.changeMap())
        
    #@       
    def command(self, command_string):
        if self.status == "void":
            self.output("The world doesn't exist yet!")
        elif self.status == "created":
            self.output("The game hasn't started yet!")
        elif self.status == "dead":
            self.output("You already died! Sorry!")
        elif self.status == "escaped":
            self.output("You already escaped! The game is over!")
        else:
            if self.isintrap == True:#@
                if self.trap.playerStatus == self.trap.ESCAPED:
                    self.output('escaped from the trap!')
                    self.isintrap = False
                elif self.trap.playerStatus == self.trap.DEAD:
                    self.output('you die in the trap!')
                    self.isintrap = False
                    self.status = "dead"
                else:
                    self.trap.commandHandler(command_string)
            else:
                self.command_handler.command(command_string)
                if not self.player["alive"]:
                    self.output("You died. Game over!")
                    self.status = "dead"
                elif self.player.name not in self.room["container"]:
                    self.status = "escaped"
                    self.output("VICTORY! You escaped!")#@
                
def game_next_input(game):
    input = sys.stdin.readline().strip()
    game.command(input)
    if game.status != 'playing':
        asyncio.get_event_loop().stop()
    else:
        flush_output(">> ", end='')
        
def flush_output(*args, **kargs):
    print(*args, **kargs)
    sys.stdout.flush()
        
async def main(args):
    loop = asyncio.get_event_loop()
    game = EscapeRoomGame(output=flush_output)
    game.create_game(cheat=("--cheat" in args))
    game.start()
    flush_output(">> ", end='')
    loop.add_reader(sys.stdin, game_next_input, game)
    await asyncio.wait([asyncio.ensure_future(a) for a in game.agents])
        
if __name__=="__main__":
    asyncio.ensure_future(main(sys.argv[1:]))
    asyncio.get_event_loop().run_forever()
