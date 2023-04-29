#The Legend of Zelda: Link's Dream
#Arfaa Rashid
#June 8,2020
#This program is a game in the style of The Legend of Zelda using sprites from The Minish Cap. It allows the user to take control of the player character with the mouse; use items like a sword, shield, and boomerang; talk to NPCS; collect and find various collectibles; and make their way to the boss of the game.
# The program uses object oriented programming to organize different types of data into classes and make it easier to work with functions.
# The plot of the game follows a similar style to Zelda games: in times of evil, a hero is chosen to fight it. It takes a different spin on it by playing as someone who desperately wants to be a hero but can't, rather than the hero himself. To gain experience, the characters goes on the adventures of all the past Links. However, the power is too much for him and he falls to evil in the end too.

from pygame import *
from pprint import *
from random import *
from math import *

screen = display.set_mode((800,600))

font.init()
mixer.init()

#---------------------------------------------------------------------------------
#Magic Numbers          #varibles with assigned values used to index lists with less confusion as to where the index came from
#Indices of Player.pics 2D-List of sprites. These are the first indices, used to access individual lists in the 2D list.
RIGHT = 0               #used for running moves as well as accessing different direction variations of other moves
DOWN = 1
UP = 2
LEFT = 3
ROLL = 4
DROWN = 8
GOT_ITEM = 9
LINK_DAMAGE = 10        #has 4 directions. Adding direction gives animation in that direction
LINK_DEATH = 14
SWORD = 15              #4 directions
SHIELD = 19             #4 directions
BOOMERANG =  23         #4 directions
#NEXTTHING = 24

#Indices of Enemy pics
ENEMY_DAMAGE = 0        #effect blitted on top of enemy
ENEMY_DEATH = 1         #effect blitted where enemy died

#Indices of Octorok pics
OCTOROK = 0             #4 directions
OCTOROK_ATTACK = ATTACK = 4      #4 directions

#Indicies of Chuchu pics
CHUCHU_RUN = 0          #Chuchu uses same move for all 4 directions
CHUCHU_DAMAGE = 1

#Indices of Boss pics
WALK = 0                #4 directions
DAMAGE = 4              #4 directions

#Indices of Projectile pics
ROCK = 0 
BOOMERANG_SPIN = 1
BOSS_ROCK = 2

#Indices of 2D list of collectible sprites
GREEN_RP = 0            #some are still images, not animations, but are stored as lists for consistency
BLUE_RP = 1
RED_RP = 2
BIG_RP = 3
HEART = 4
PIECE = 5
CONTAINER = 6

#Indices of 2D list of NPC sprites
SMITH = 0
SIGN = 1
CHEST = 2   
BIG_CHEST = 3

#Indices of Game pics - miscellaneous images
BOXES = 0               #images of text/dialogue/prompt boxes
PLATFORMS = 1           
BUTTONS = 2
HEARTS = 3
PIECES = 4
BIG_BLUE_RUPEE = 5
GATES = 6       
SWITCHES = 7
WARP = 8
CURSOR = 9

#Indices of Game page pics - 1D list
TITLE = 0
STORY = 1
ENTER_NAME = 2
PAUSE = 3
GAMEOVER = 4
CREDITS = 5

#Indices of switch list
COL = 0
RECT = 1
TIME = 2
#Magic numbers for COL in switch list
GREEN = 0
BLUE = 1
RED = 2

#Indices of gates
STAIRS = 0                  #blocks stairs -> False when switch activated
SWITCH_ROOM = 1             #blocks entrance to room with switch in it -> True when switch activated

#Indices of track list - 1D list
T_TITLE = 0
T_ENTER_NAME = 1
T_PAUSE = 2
T_STORY = 3
T_SOUTHFIELD = 4
T_WOODS = 5
T_DUNGEON = 6
T_END = 7
T_GAMEOVER = 8
T_SFX_SECRET = 9
T_SFX_TREASURE = 10
T_SFX_GAMEOVER = 11



#Partially transparent Surface on which dialogue,text, and prompts are blitted
trans_Surf = Surface((800,600))
trans_Surf.fill((0,0,255))                #fills surface with a colour that won't be used in anything blitted on the surface
trans_Surf.set_colorkey((0,0,255))        # and sets that colour to transparent so only what's blitted on the surface appears and the rest is clear

trans_Surf.set_alpha(200)                 #surface is semi transparent

#---------------------------------------------------------------------------------
#Classes
class Player:               
    pics = []                                                   #2d list of sprites for Player animations
    knockback = 2                                               #distance knocked back per loop while being blocked or taking damage

    def __init__(self):                                         
        """Creates player object and sets his default attributes.
        There's only 1 Player, so all his attributes can just be set directly here instead of being passed in as parameters.
        Also,as there's only 1 object of the class it doesn't make a big difference whether variables are class attributes or object attributes.
             Which type each variable is is decided assuming there were several Players, and which variables would be consistent with all and which would be specific to each object.
        """
        
        self.x,self.y = 1100,750                                #world x/y position - position of player on map
        self.name = "Link"                                      #if no name is chosen to overwrite this one, name remains default name Link
        self.respawn_location = (1100,750)                      #position Player respawns at if they die. Changes every time an area is entered/exited
        self.speed = 3                                          #amount of pixels Player can move in any direction each loop
        self.max_health,self.health = 12,12                     #max health is total amount of health Player could possibly have, health is amount of health Player currently has after taking damage
        self.rupees = 0                                         #collectible currency                                     
        self.heart_pieces = 0                                   #collectible. Find 3 to have another heart added to max health
        self.equipped1,self.equipped2 = sword,shield            #Item mapped to left and right mouse buttons
        self.using_item1,using_item2 = False,False              #bool indicating whether item is being used
        self.collision,self.collision_object = None,None        #action player is performing, usually result of collision (ex: "getting_hit"; object being collided with                                     
        self.invincible,self.count_invincibility = False,3      #bool indicating whether invincible, counter indicates how many loops Player is invincible for
        self.move = 0                                           #first index of 2D list of sprites. Indicates action Player is performing
        self.direction = self.move                              #indicates direction being faced
        self.frame = 0                                          #second index of 2D list. Indicates frame of animation
        self.animate_speed = 0.3                                #indicates rate at which animation frames will be increased by
        self.interact_object = None                             #NPC Player is interacting with
        self.follow_cursor = True                               #Player can either follow the mouse cursor, or walk to a location set by clicking the mouse cursor. Which he will do is decided by this flag
        Game.make_Rect(self)                                    #Rect is created around Player sprite, and is used to check for collisions                      


    def move_link(self,dest_x,dest_y):
        "Sets direction, position, and move of Player based on location relative to destination--a position on the map, equal to or earlier set by mouse input."
        
        if self.rect.collidepoint(dest_x,dest_y) == False:                      #when Player is at destination, doesn't move
            self.move = None                                                    #prevents move from last loop from interfering with current                                                                                 

            if dest_x >= self.rect[0] + self.rect[2]:               #checks if mouse is right/left of Player rect 
                self.move = RIGHT                                                                          
                new_x = self.x+self.speed
            elif dest_x <= self.rect[0]:
                self.move = LEFT
                new_x = self.x-self.speed
            else:
                new_x = self.x
                        
            if dest_y >= self.rect[1] + self.rect[3]:               #does the same for up/down as for right left
                self.move = DOWN                                                #vertical movement is checked in seperate if structure than horizontal to allow diagonal movement.
                new_y = self.y+self.speed
            elif dest_y <= self.rect[1]:
                self.move = UP
                new_y = self.y-self.speed
            else:
                new_y = self.y

            if maps[game.map].read_map(new_x,new_y,link) != "WALL":         #makes sure new position is 'safe' to be in: not inside a wall or an object Rect where Player shouldn't be able to stand
                collide = False
                for rec in Game.rects:                                      #Game.rects is a list containing all the Rects on the screen where line is not allowed to walk: for ex, through an NPC
                    if rec.collidepoint(new_x,new_y):   
                        collide = True
                        break                                               #if player collides with at least one rect, won't move, so no need to check the rest
                if collide == False:
                    self.x,self.y = new_x,new_y
                      
            self.direction = self.move
        else:                                                                   #if mouse is over Player rect, no movement
            self.frame = self.frame - self.animate_speed                        #cancels out frame increase in animate() method
            self.move = self.direction
            self.frame = 10                                                     #standing frame is at index 10 in the running moves

        if link.rect.collidepoint(dest_x,dest_y):
            if link.follow_cursor == False:                                     #link starts following cursor again once he reaches the dest_x,dest_y, if he wasn't following it already
                    link.follow_cursor = True       


    def roll(self):
        if self.move < ROLL or self.move > ROLL+3:              #If not roll move yet
            self.move = ROLL + self.direction                   # becomes roll move
            self.frame = 0
            self.speed = 4                                      #rolling is faster than walking
            self.collision = "rolling"                          #can't use items or move normally while rolling
            
        if self.direction == RIGHT:                             #all directions are called within the same if structure because you can't roll diagonally
            new_x,new_y = self.x + self.speed,self.y
        elif self.direction == LEFT:
            new_x,new_y = self.x - self.speed,self.y
        elif self.direction == DOWN:
            new_x,new_y = self.x,self.y + self.speed
        elif self.direction == UP:
            new_x,new_y = self.x,self.y - self.speed

        if maps[game.map].read_map(new_x,new_y,link) != "WALL":         #only roll to new location if new location is 'safe' to be in -> not colliding with any Rects or inside a wall
                collide = False
                for rec in Game.rects:
                    if rec.collidepoint(new_x,new_y):   
                        collide = True
                        break                                           #if player collides with at least one rect, won't move, so no need to check the rest
                if collide == False:
                    self.x,self.y = new_x,new_y
        
        if self.frame + self.animate_speed >= len(self.pics[self.move]):        #if done animation,reset all attributes and resume normal movement
            self.move = self.direction
            self.frame = 0
            self.speed = 3                                                      #normal running speed
            self.collision = None


    def use_item(self,item):
        "Selects attributes for using an item, like move, frame, animate_speed."

        if self.move < SWORD:                           #SWORD is the first item move. If move is less than that, move has not been changed to item move yet
            self.move = item.num + self.direction       #num is index of Player pics where Item's moves begin
            item.being_used = True
            self.frame = 0
            self.animate_speed = item.animate_speed     #each kind of move animates at a different speed. speed that Player should animate with while using item is an attribute of the item
            if item == boomerang:                       #boomerang item not only has Player do a move, but also creates a boomerang projectile that damages enemies and then returns to the Player
                boomerang.loops = 0                     #increases every time frame reset to 0. used to decide when boomerang switches direction and returns to link
                boomerang.come_back = False             #projectile follows slightly different rules on the way back to Player than when first thrown
                boomerang_projectile = Projectile(link.x,link.y,4,link.direction,"enemy",item.damage,0,0.75,BOOMERANG_SPIN)

        else:
            if item.button_type == "click":                                                 
                if self.frame + self.animate_speed >= len(self.pics[self.move]):            #if once animate() is called, frame will reset and animation will repeat, 
                    self.move = self.direction                                              # move is over and everything is reset -> click items are only used for the duration of their animation
                    self.animate_speed = 0.3
                    if item != boomerang:                                                   #boomerang being used is only set to False when it returns to link, not when link is done throwing it, 
                        item.being_used = False                                             # so that it can't be thrown again until then. however link can run around and use other items in the meantime
                    if self.using_item1:
                        self.using_item1 = False
                    elif self.using_item2:
                        self.using_item2 = False
                    
            elif item.button_type == "hold":
                if self.frame + self.animate_speed >= len(self.pics[self.move]):            #if once animate() is called, frame will reset and animation will repeat,
                    self.frame = item.repeat_frame                                          # sets to repeated frame so entire animation isn't played again -> hold items are used until the mouse button is released

    
    def game_over(self):
        "If Player health is 0, dies,coordinates and health are reset, and page is switched to Gameover."

        if self.frame + self.animate_speed >= len(self.pics[self.move]):                         
            self.x = self.respawn_location[0]
            self.y = self.respawn_location[1]
            self.move = self.direction                  
            self.frame = 10
            self.animate_speed = 0.3
            game.offset()                                               #Player position has changed so offset must be recalculated
            mouse.set_pos(self.x+game.offset_x,self.y+game.offset_y)    #mouse is set over Player position when he respawns
            self.health = int(self.max_health)
            self.collision = None
            self.collision_object = None
            time.wait(10000)                            #waits so that dying sound effect can finish
            return "Gameover"                           #switches to gameover page once animation over -> this is a function being called from the function that actually needs to return this. This function will return it, and then the original function will return it too



Player.items = []       #list of all Item objects
class Item:
    pics = []           #2D list of images of items
    
    def __init__(self,damage,button_type,animate_speed,num,name):          
        "Item object attributes are set according to parameters passed in."

        self.damage = damage                    #damage dealt by item
        self.button_type = button_type          #indicates if mb needs to be clicked or held to use item
        self.num = num                          #index of Player sprite 2D-list where Item's moves begin
        self.name = name                        #name of item
        self.pos = len(Player.items)            #position in list of items
        if self.button_type == "hold":
            if self.num == SHIELD:
                self.repeat_frame = 4               #if mb needs to be held, frame where its animation repeats from is set
        self.shortcut_key = 49 + len(Player.items)  #shortcut key is number from 1-9 on keyboard that can be held to switch to that item. 49 is the index for the key K_1 in the list of of keys. adding the length of the list gives the value the key for that item corresponds to
        self.animate_speed = animate_speed      #will change Player animate speed when he uses the item
        self.being_used = False    
        self.unlocked = False                   #not all items are available to use from the very beginning. If it's not unlocked, it can't be used
        Player.items.append(self)
        if self.num == BOOMERANG:
            self.come_back = False              #True when on its way back to Player
            self.loops = 0                      #Increases every time its animation ends. Used to decide when boomerang switches direction and returns to Player


    def switch_item(self,mb):
        "Equipped items can be switched by holding a number key and pressing the mouse button you want to map it to."
        
        if self.unlocked == True:                       #can only be equipped if unlocked
            if mb == "left":                            #mb is a string indicating the mousebutton that was pressed while the key was pressed
                if link.equipped2 == self:
                    link.equipped2 = link.equipped1
                link.equipped1 = self
            elif mb == "right":
                if link.equipped1 == self:
                    link.equipped1 = link.equipped2
                link.equipped2 = self
            


enemies = []
class Enemy:
    pics = []       #contains general sprites used for all enemies, like the hit and death animations

    def __init__(self,x,y): 
        "Sets general attributes for enemies that are same across all types of enemies. Enemy is a parent class but has no objects of its own."
    
        self.x,self.y = x,y                                         #Enemy has the some of the same attributes as Player
        self.collision,self.collision_object = None,None
        self.invincible,self.count_invincibility = False,15
        self.direction = self.move = RIGHT
        self.frame = 0
        Game.make_Rect(self)
        enemies.append(self)                                        #enemies is list of enemy objects currently in the game

        
    def move_enemy(self):
        "Random movement. Continues in the same direction, chooses a new direction, or attacks."

        if self.move >= self.attack_move and self.frame == 0:                           #if done attacking,returns from attacking move to walking move
            self.move = self.direction      

        if self.move < self.attack_move:                                                #if not attacking, will move
            moves = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1]                                   #1/16 chance of changing direction. 0 -> continue old move. 1 -> select new move  
            if choice(moves) == 1:              
                new_moves = [RIGHT,RIGHT,RIGHT,DOWN,DOWN,DOWN,UP,UP,UP,LEFT,LEFT,LEFT,ATTACK]   #Options for new move. Attacking is less likely than normal running
                for i in range(2):                                                              #removes current move from new move options
                    new_moves.remove(self.move)
                self.move = choice(new_moves)
                self.frame = 0
        
            if self.move < self.attack_move:
                self.direction = self.move                                  #if new move selected wasn't an attack, direction is updated
                        
                if self.move == RIGHT:
                    new_x,new_y = self.x+self.speed,self.y
                elif self.move == DOWN:
                    new_x,new_y = self.x,self.y+self.speed
                elif self.move == UP:
                    new_x,new_y = self.x,self.y-self.speed
                else:
                    new_x,new_y = self.x-self.speed,self.y

                if maps[game.map].read_map(new_x,new_y,self) != "WALL" and maps[game.map].rect.collidepoint(new_x,new_y):   #makes sure new position is 'safe' to be in: not inside a wall or another object Rect or off the map          
                    collide = False
                    for rec in Game.rects:                                      
                        if rec.collidepoint(new_x,new_y):   
                            collide = True
                            break                                               
                    if collide == False:
                        self.x,self.y = new_x,new_y
                            
            elif self.move == self.attack_move:
                self.move = 4 + self.direction                      #type doubles as index where its moves start. + 4 gives where its attacks start. + direction gives attack move in the right direction     
                self.enemy_attack()                                 #attacking has its own seperate method 



class Octorok(Enemy):       #"Octorok" is the name of a type of enemy
    pics = []               #2D list with indices move,frame which contains only Octorok sprites

    def __init__(self,x,y):
        "Sets attributes specific to Octoroks."

        super().__init__(x,y)
        self.attack_move = OCTOROK_ATTACK                           #index where its attack moves start
        self.animate_speed = 0.1
        self.health = 3
        self.damage = 1
        self.speed = 1                                                                                  #knockback counter is 30 because sword swing takes 27 loops, so sword will definitely not still be colliding when collision is reset
        self.knockback,self.count_knockback = 1,30                                                      #Octorok has no sprites for taking damage, so can't end its knockback when frame == 0. Instead, ended when its counter = 0
        self.move_choices = [RIGHT,RIGHT,RIGHT,DOWN,DOWN,DOWN,UP,UP,UP,LEFT,LEFT,LEFT,OCTOROK_ATTACK]   #if a new move is being chosen, it will choose between these
        self.drop = choice([None,GREEN_RP,HEART])                                                       #octorok has chance of dropping a green rupee or a heart when it dies


    def enemy_attack(self):
        "Attack specific to Octorok."
        
        rock = Projectile(self.x,self.y,2,self.direction,"player",1,2,0.4,ROCK)         #shoots a rock - Projectile object does the rest of the work



class Chuchu(Enemy):    #"Chuchu" is the name of another type of enemy
    pics = []           #2D list with indices move,frame which contains only Chuchu sprites

    def __init__(self,x,y):
        "Sets attributes specific to Chuchus."

        super().__init__(x,y)
        self.attack_move = CHUCHU_RUN                               #chuchu doesnt have a special move for attacking
        self.animate_speed = 0.2
        self.health = 5
        self.damage = 2
        self.speed = 4
        self.knockback = 15                                         #chuchu has a move for getting hit, so doesnt need a counter. It's basically a big bouncy blob so it gets knocked back a lot
        self.move_choices = [RIGHT,DOWN,UP,LEFT]                    #if a new move is being chosen, it will choose between these
        self.drop = choice([BLUE_RP,BLUE_RP,RED_RP,HEART])          #chuchu could drop a heart, a blue rupee, or a red rupee


    def move_enemy(self):
        "Chuchu doesnt have 4 different direction moves for walking, nor an attack move, so its movement is unique and has its own method."

        if self.frame < 8 or self.frame > 25:                       #can only move around while on the ground. at frame 8, chuchu jumps up, and at 25, it squishes down
            self.direction = choice(self.move_choices)

            if self.direction == RIGHT:                             #chuchu moves quickly and randomly, discouraging Player from approaching when it's on the ground and instead approaching when it jumps up
                new_x,new_y = self.x+self.speed,self.y
            elif self.direction == DOWN:
                new_x,new_y = self.x,self.y+self.speed
            elif self.direction == UP:
                new_x,new_y = self.x,self.y-self.speed
            else:
                new_x,new_y = self.x-self.speed,self.y

            if maps[game.map].read_map(new_x,new_y,self) != "WALL" and maps[game.map].rect.collidepoint(new_x,new_y):           #as usual, only updates location if new location is safe
                    collide = False
                    for rec in Game.rects:                                      
                        if rec.collidepoint(new_x,new_y):   
                            collide = True
                            break                                               
                    if collide == False:
                        self.x,self.y = new_x,new_y



class Boss():                   #would make it a subclass of enemy, but doesn't act like a normal enemy so is its own class
    pics = []

    def __init__(self):
        "There is only 1 Boss, so its attributes don't need to passed in as parameters. Instead, they are set directly here."

        self.x,self.y = 370,785       
        self.health = 12                
        self.damage = 2
        self.type = WALK                    #like Enemy object attribute type, is starting index for its moves in its list. needed for collision code where boss acts like an enemy
        self.move_type = None               #boss has 4 possible moves. if None, move is over and choose_move() is called so a new move is chosen
        self.old_move = None                #old move is what the last move was. Used to decide what next move will be
        self.speed = 1                      #speed x/y increases by - if move type is "move"
        self.move_direction = None          #moves back and forth in either x or y direction - if move type is "move"
        self.current_rotation = 0           #measure in degrees of how much image has already been rotated - if move type is "rotate"
        self.max_rotation = 0               #measure in degrees of how much image needs to be rotated (could be 90,180,270,360) - if move type is "rotate"
        self.move = self.direction = LEFT
        self.frame = 0
        self.animate_speed = 0.1
        self.collision = self.collision_object = None
        self.count_hit_wait = 30            #boss freezes until counter reaches 0 after it gets hit to avoid multiple consecutive collisions
        Game.make_Rect(self)
        self.make_hitbox()                  #boss uses a hitbox instead of its normal Rect for collisions unlike other objects because it has a large amount of empty transparent space
                                            # surrounding it so it can rotate without part of its image being cut off, and between its legs, which count as part of its Rect and could damage and be damaged if its Rect was used
                                            # The hitbox is only around the body of the Boss


    def make_hitbox(self):
        "Creates 192x192 Rect centered at the boss's centre. Hitbox is used in place of its normal Rect for collisions to avoid unfair collisions."

        box = (self.x-96,self.y-96,192,192)     #Creates rect around middle area of boss. Values 96 and 192 were decided by looking at the sprite image 
        self.hitbox = Rect(box)


    def choose_move(self):
        "Randomly chooses a new move type based on last move type."

        if self.old_move == "rotate":                                   #4 possible moves are rotate,shoot,rest,and move
            moves = ["shoot","shoot","move"]                            #likelihood of each move being selected as new move type depends on last move
        elif self.old_move == "shoot":                                  # this makes it easier for Player to predict what the boss will do next and prepare for it
            moves = ["move","rest"]
        elif self.old_move == "rest":
            moves = ["rotate","rotate","shoot","shoot","move"]
        else:
            moves = ["rotate","shoot","move","rest"]

        self.move_type = self.old_move = choice(moves)

        if self.move_type == "rotate":          #rotate - boss spins 90,180,270,or 360 degrees on the spot
            self.animate_speed = 0.15
            self.current_rotation = 0
            rand_ang = randint(1,4)                 #decides whether rotation will be 1/4,2/4,3/4,or 4/4 of a circle
            self.max_rotation = 90*rand_ang         #multiplies by 90 for the actual angle value

            count_direction = rand_ang              #sets new direction by setting direction to the next direction in counter clockwise order 
            while count_direction >0:               # for each 1/4 circle rotation
                if self.direction == RIGHT:
                    self.direction = UP
                elif self.direction == UP:
                    self.direction = LEFT   
                elif self.direction == LEFT:
                    self.direction = DOWN
                else:
                    self.direction = RIGHT
                count_direction -= 1
 
        elif self.move_type == "shoot":         #shoot - shoots rock projectile(like Octorok)
            self.animate_speed = 0.1
            x,y = self.x,self.y
            if self.direction == RIGHT:                 #makes the projectile appear at the boss's mouth/nose instead of at its centre
                x += self.pics[self.move][int(self.frame)].get_width()//2
            elif self.direction == DOWN:
                y += self.pics[self.move][int(self.frame)].get_height()//2
            elif self.direction == UP:
                y -= self.pics[self.move][int(self.frame)].get_height()//2
            else:
                x -= self.pics[self.move][int(self.frame)].get_width()//2
            big_rock = Projectile(x,y,3,self.direction,"player",2,3,0.5,BOSS_ROCK)        
            self.count_move = 3

        elif self.move_type == "rest":          #rest - enemy slows down (makes it easier for player to attack)
            self.animate_speed = 0.07
            self.count_move = 5        
        else:                                   #move - normal back and forth movement in x or y direction 
            self.animate_speed = 0.2
            self.count_move = 5
            

    def move_boss(self):        #move has its own method while the other moves don't because their information (rotations, direction) only need to be set once, while location must be checked each loop
        "Controls x and y movement if move_type is 'move'."
        
        if self.move_direction == None:
            self.move_direction = choice(["x","y"])     #can only move in 1 direction at a time
    
        elif self.move_direction == "x":                #if boss moves 30 px in any direction, changes direction so it doesn't go too far in any direction
            self.x += self.speed
            if self.x >= 400:                       #30 px greater than normal x position(370)
                self.speed *= -1
            elif self.x <= 340:                     #30 px less than normal x position(370)
                self.speed *= -1

        elif self.move_direction == "y":
            self.y += self.speed
            if self.y >= 815:                       #30 px greater than normal y position(784)
                self.speed *= -1
            elif self.y <= 755:                     #30 px less than normal y position(784)
                self.speed *= -1
    

    def boss_get_blocked(self):             #boss reacts differently to block and hit collisions so it has its own methods for each
        "Stops the boss from moving if it's being blocked."

        self.move_type = None       #boss stops moving while being blocked
        self.animate_speed = 0
        if (link.equipped1 == shield and Game.mb[0] == 0) or (link.equipped2 == shield and Game.mb[2] == 0):
            self.collision = self.collision_object = None


    def boss_get_hit(self):
        "Controls what happens if boss is hit or dies."

        if sword.being_used == False and boomerang.being_used == False:     #boss is so big it doesn't get knocked back, instead its collisions are set to False when the item is done being used
            self.collision = self.collision_object = None

        if self.health <= 0:                                        #if boss dies, boss fight is over
            container = Collectible(self.x,self.y,CONTAINER,False)  #drops a heart container
            Game.boss = None
            del self
            Game.boss_fight = "over"                                #"over" instead of False, so it doesn't trigger again
            game.sfx_treasure = True                                #sound effect plays when boss defeated
            game.play_music("sfx")
            Game.warp = True                                        #stepping on warp tile ends game
            


projectiles = []            #list of all projectile objects in game currently
class Projectile():
    pics = []               #2D list of projectile sprites organized by move,frame

    def __init__(self,x,y,speed,direction,target,damage,knockback,animate_speed,move):
        "Sets attributes for Projectile object based on parameters."
        
        self.x,self.y = x,y                                 #mostly same as Player attributes
        self.speed = speed
        self.direction = direction
        self.target = target                                #prevents friendly fire (enemy's projectiles can't damage another enemy)
        self.damage = damage
        self.collision,self.collision_object = None,None
        self.knockback = knockback
        self.animate_speed = animate_speed
        self.move = move
        self.frame = 0
        Game.make_Rect(self)
        projectiles.append(self)


    def move_projectile(self):
        "Updates Projectile's x,y coordinates."

        if boomerang.loops >= 6 and boomerang.come_back == False:      #boomerang loop increases every time it finishes its animation. Once it does that 6 times, it will start returning to link
            boomerang.come_back = True

        if self.move == BOOMERANG_SPIN and boomerang.come_back:         #boomerang moves differently when it's coming back
            if link.x > self.x:                 # checks if player is to the right/left of boomerang and moves in that direction                                                                   
                self.x += self.speed
                self.direction = RIGHT
            elif link.x < self.x:
                self.x -= self.speed
                self.direction = LEFT
                 
            if link.y > self.y:                 # does the same for up/down as for right left. checking in different if structures allows it to move diagonally  
                self.y += self.speed
                self.direction = DOWN
            elif link.y < self.y:
                self.y -= self.speed        #no need to check for walls/npcs -> boomerang is loyal--people,houses,walls:nothing can stop it from returning to its master
                self.direction = UP
        else:
            if self.direction == RIGHT:                                 #normal projectile movement -> constant speed added to x or y in the same direction
                new_x,new_y = self.x+self.speed,self.y
            elif self.direction == DOWN:
                new_x,new_y = self.x,self.y+self.speed
            elif self.direction == UP:
                new_x,new_y = self.x,self.y-self.speed
            elif self.direction == LEFT:
                new_x,new_y = self.x-self.speed,self.y

            if maps[game.map].read_map(new_x,new_y,self) == "WALL":
                if self.move == BOOMERANG_SPIN:                         #if boomerang hits a wall before starting to return, acts as though it has completed 6 loops and returns anyway
                    boomerang.come_back = True
                    boomerang.loops = 6
                else:                                                   #if normal projectile hits a wall, acts as though blocked. collision is set to "getting_blocked" so method for getting blocked is called
                    self.frame = 0.1
                    self.collision = "getting_blocked"                
            else:
                self.x,self.y = new_x,new_y

            if maps[game.map].rect.collidepoint(self.x,self.y) == False:    #if goes off the map, removed (normal projectile) or returns to player (boomerang)
                if self.move == BOOMERANG_SPIN:
                    boomerang.come_back = True
                    boomerang.loops = 6
                else:
                    projectiles.remove(self)
                    del self
                    


animations = []
class Animation():

    def __init__(self,x,y,animate_speed,cls,obj,move,moves,name,frame=0):
        "For animations with no related class or associated object, or happening simultaneous to another animation of the same object."
        
        self.x,self.y = x,y
        self.animate_speed = animate_speed
        self.pics = cls.pics        #class is passed in as a parameter so animation can seek for its pictures in there
        self.object = obj           #object on which animation takes place. in case object moves and animation x,y must also move. can be None
        self.move = move
        self.moves = moves          #bool indicating whether x/y position changes and move_animation needs to be called
        self.name = name
        self.frame = frame          #default 0, but a value could be passed in 
        Game.make_Rect(self)
        Game.rects.append(self.rect)
        animations.append(self)


    def move_animation(self):
        "Some animations move in x or y direction to stay on top of an object. Sets animaition x,y equal to object's x,y."
        
        self.x,self.y = self.object.x,self.object.y



collectibles = []
class Collectible():
    pics = []       #pics will be a 2D-List for consistency even though not all collectibles have animations

    def __init__(self,x,y,tp,temp):        
        "Objects that can be dropped by enemies or are found on the map."
        
        self.x,self.y = x,y
        self.type = self.move = tp          #type is also index of pics 2D-list
        self.frame = 0
        self.call_animate = False           #default is False. animate method will be called to increase frames if True. Some collectibles have animations but others don't
        self.temp = temp                    #bool indicates whether collectible will disappear if not collected
        self.count_down = 500
        
        if self.type == GREEN_RP:           #each type has an associated value that increases something different
            self.amount = 1
        elif self.type == BLUE_RP:
            self.amount = 5
        elif self.type == RED_RP:
            self.amount = 20
        elif self.type == BIG_RP:
            self.amount = 50
            self.call_animate = True        
            self.animate_speed = 0.1
        elif self.type == HEART:
            self.amount = 1
        elif self.type == PIECE:           
            self.amount = 1/3
        elif self.type == CONTAINER:
            self.amount = 1
            self.call_animate = True
            self.animate_speed = 0.3
        
        Game.make_Rect(self)
        collectibles.append(self)


    def collect(self):
        "Method for adding the collectible's amount to the appropriate variable."

        if self.type <= BIG_RP:
            link.rupees += self.amount
            game.rupee_text = Game.render_text(str(link.rupees),100,50,1,(0,0,255))                 #rupee number text is only rerendered if it changes
        elif self.type == HEART:
            if link.health + self.amount <= link.max_health:
                link.health += self.amount
        elif self.type >= PIECE:
            link.max_health += self.amount
            link.heart_pieces += 1
            game.heart_piece_text = Game.render_text(str(link.heart_pieces),100,50,1,(0,0,255))     #heart piece number text is only rerendered if it changes    

        if (self.x,self.y,self.move) in maps[game.map].collectibles:                                #once picked up, deleted. if collectible was spawned from map list, removed from there too so it doesnt respawn
            maps[game.map].collectibles.remove((self.x,self.y,self.move))
        collectibles.remove(self)                
        del self


    def disappear(self):
        "Some collectibles, like ones that drop when enemies die, disappear if they're not collected in a period of time. Method decreases count_down and removes collectible if it reaches 0."

        self.count_down -= 1                #When count_down reaches 0, collectible is deleted
        if self.count_down == 0:
            Game.rects.remove(self.rect)
            collectibles.remove(self)
            del self



npcs = []           
class NPC():
    pics = []

    def __init__(self,x,y,move,animate_speed,item,rect,name,dialogue,pos):           
        "Interactable character that has dialogue and may give an item."

        self.x,self.y = x,y
        self.move,self.frame = move,0
        self.speaking = False               #characters speak,signs are read,and chests are opened, but all are functionally the same, and are similar enough
        self.pos = pos                      #index of npcs list 
        self.name = name        
        if self.move < SIGN:                #characters start off animating, while chests only animate later, and signs never do. Character moves are all before sign and chest moves are all after
            self.animate = True
        else:
            self.animate = False
        self.animate_speed = animate_speed
        self.item = item                    #If npc gives item, included here. otherwise, None
        self.inteRect = rect                #Interact Rect (haha interect)-> area where link has to be standing to interact with NPC 
        self.count_dialogue = -1            #dialogue is list of strings of the lines NPC says. Counter keeps track of which line NPC is at 
        self.dialogue = []
        for line in dialogue:
            self.dialogue.append(Game.render_text(line,760,180,20,(255,255,255)))
        Game.make_Rect(self)
        Game.rects.append(self.rect)
        npcs.append(self)


    def speak(self):
        "Increases index of list of NPC's dialogue."

        if self.count_dialogue+1 >= len(self.dialogue):     #if last line of dialogue has been said - if npc gives an item, this line is about the item.
            if self.item != None:                           #if npc gives an item, link move becomes get item move and give_item() called
                link.move = GOT_ITEM
                link.animate_speed = 0.2 
                link.frame = 0
                self.give_item()
            else:
                if link.frame + link.animate_speed >= len(link.pics[link.move]):        #if animation will reset frame to 0 after animate is called, cancels frame increase
                    link.frame -= link.animate_speed                                    # and freezes at last frame until done speaking
                if Game.space_click:                                    #space is how dialogue is progressed through
                    self.speaking = False                               #resets everything when dialogue is finished
                    if game.item_animation != None:                     #removes item animation that was created in give_item()
                        Game.rects.remove(game.item_animation.rect)
                        animations.remove(game.item_animation)
                        del game.item_animation
                        game.item_animation = None
                    trans_surf.fill((0,0,255))                      #removes textbox from surface
                    self.count_dialogue = -1                        #begins at -1 because dialogue counter increases before line is actually shown

                    if self.move < SIGN:                            #characters moves are less than sign move
                        self.animate = True
                        if self.name == "smith":                    #can't talk to smith again after speaking to him once -> since he can't be interacted with, he's essentially just an animation
                            smith_animation = Animation(self.x,self.y,self.animate_speed,NPC,None,SMITH,False,"smith_animation")
                            maps[game.map].animations.append((self.x,self.y,self.animate_speed,NPC.pics,None,SMITH,False,"smith_animation"))
                            del maps[game.map].npcs[self.pos]       #removes smith from map's list of npcs, so he won't respawn
                            self.inteRect = None    
                            npcs.remove(self)
                            del self

                    elif self.move > SIGN:                          #chest moves are greater than sign move. chests disappear after being interacted with
                        if len(maps[game.map].npcs) == 1:
                            del maps[game.map].npcs[-1]             #removes chest from map list of npcs, so it doesn't get respawned. If len of list is 1, deleting from the end will delete the right chest
                        else:
                            del maps[game.map].npcs[self.pos]       #Note: only reason this works is that the only map with more than 1 chest is shrine, which has 2. with 2, first one can remove at self.position, but for the other, the position is now changed. since there are only 2, the other can be removed from the end of the list. if there were more, a more complicated solution would be needed, but there aren't so i'll pass on thinking up the best way to do this one.
                        self.inteRect = None
                        npcs.remove(self)
                        del self
                    link.collision = None                           #resets link's attributes now that interaction is over
                    link.interact_object = None
                    link.animate_speed = 0.3
        else:
            if Game.space_click:                #dialogue is progressed when space bar is clicked
                self.count_dialogue += 1       


    def give_item(self):    
        "NPC could give an Item or a Collectible. Method either unlocks an Item or creates a Collectible for Player to collect."

        game.sfx_treasure = True
        game.play_music("sfx")
        if isinstance(self.item,Item):      #can get Items or Collectibles through chests
            self.item.unlocked = True
            game.item_animation = Animation(link.x,link.y-50,0,Item,None,0,False,"item",self.item.pos)      #image of item appears over player
        else:                                           
            got_item = Collectible(link.x,link.y,self.item,True)                                            #collectible is created at player position so link automatically collects it
            game.item_animation = Animation(link.x,link.y-50,0,Collectible,None,got_item.move,False,"item") #image of item appears over player
        self.item = None    



maps = []
class Map():

    def __init__(self,name,img,mask,width,height,track,enemies=None,npcs=None,collectibles=None,animations=None,mask2=None):
        "Creates Map object with parameters passed in. Last 5 parameters are optional: not every map has enemies,npcs,collectibles,animations,and a second floor."

        self.name = name                        #name of area map is of
        self.num = len(maps)                    #index of maps
        self.width,self.height = width,height   #size map images are scaled to 
        self.rect = Rect(0,0,width,height)
        self.track = track                      #music track that plays on that map
        self.exits = []                         #list of exits from map
        
        if enemies == None:
            self.enemies = []                   
        else:
            self.enemies = enemies              #list of tups containing type of enemy and number on map used to create their objects
        if npcs == None:
            self.npcs = []                      
        else:
            self.npcs = npcs                    #list of tups of info for attributes of NPCs on map used to create their objects
        if collectibles == None:
            self.collectibles = []
        else:
            self.collectibles = collectibles    #list of tups of info for attributes of Collectibless on map used to create their objects
        if animations == None:
            self.animations = []
        else:
            self.animations = animations        #list of tups of info for attributes of Animations on map used to create their objects

        map_img = image.load("imgs/maps/%s.png" % (img))                #each map has a map image and a mask image. The map is what's blitted on the screen and is actually visible 
        scaled_map_img = transform.scale(map_img,(width,height))
        self.image = scaled_map_img

        mask_img = image.load("imgs/maps/%s.png" % (mask))              #the mask is colour coded to show if something special is at that spot of the map, like a wall or water. The mask is checked in read_map()
        scaled_mask_img = transform.scale(mask_img,(width,height))
        self.mask = scaled_mask_img

        if mask2 == None:                       #mask2 is used for a second floor, if there is one
            self.mask2 = None
        else:
            mask_img2 = image.load("imgs/maps/%s.png" % (mask2))
            scaled_mask_img2 = transform.scale(mask_img2,(width,height))
            self.mask2 = scaled_mask_img2

        if self.num == 0:                       #only want to spawn everything when initialized for the first map, otherwise objects that should appear on other maps would be created while on the first map as well
            self.create_objects()

        maps.append(self)


    def create_objects(self):   
        "Creates objects that belong on that map using information in tuples. Tuples contain parameters/types/etc for object to be created."

        for tup in self.enemies:                    #enemy list of tups contains tups with 2 pieces of info: the class, so the type of enemy; and the number that are on the map                          
            for i in range(tup[1]):                 #loops for the amount of that type of enemy on the map. Note: it's entertaining to make this a really high number, like 200ish
                while True:                         #enemies spawn at random locations. positions are checked to make sure they're not over walls/water/any other place where enemy can't normally go or is unfair to spawn(inside player or other rects)
                    rand_x = randint(0,self.width)
                    rand_y = randint(0,self.height)
                    if link.rect.collidepoint(rand_x,rand_y) == False and self.read_map(rand_x,rand_y,None) == "CLEAR" or self.read_map(rand_x,rand_y,None) == "DOORWAY": #if clear is returned, position is safe to walk on(not water,wall,hidden,etc)
                        safe = True
                        for r in Game.rects:                        #loops through rects to check for collisions. breaks for loop if one is encountered
                            if r.collidepoint(rand_x,rand_y):       # because if it even collides with one, area is not safe
                                safe = False
                                break
                        if safe:
                            break
                enemy = tup[0](rand_x,rand_y)
                
        for tup in self.npcs:
            npc = NPC(tup[0],tup[1],tup[2],tup[3],tup[4],tup[5],tup[6],tup[7],len(npcs))

        for tup in self.collectibles:
            collectible = Collectible(tup[0],tup[1],tup[2],False)           #if collectible is spawned onto map, it won't disappear after a period of time
            
        for tup in self.animations:
            animation = Animation(tup[0],tup[1],tup[2],tup[3],tup[4],tup[5],tup[6],tup[7])



    def set_exit(self,rect,new_map,new_x,new_y):
        "Creates tup of Rect of exit, the map it leads to, and the x/y Player starts at on that map."
        
        ex = (rect,new_map,new_x,new_y)             #rect can be collided with to go to the new_map and start there at new_x,new_y
        self.exits.append(ex)


    def read_map(self,x,y,obj):
        "Gets colour at position of map mask. Returns meaning of colour at position."
        
        if x>0 and y>0 and x<self.width and y<self.height:
            map_x,map_y = int(x),int(y)
            col = self.mask.get_at((map_x,map_y))

            if col == (0,0,0):
                return "WALL"

            elif col == (0,255,255):                                                #player drowns in water unless colliding with platforms in the shrine      
                if isinstance(obj,Player):
                    if maps[game.map].name == "shrine":
                        if Game.shrine_platform == 1:
                            for r in Game.platform1_Rects:                          #list of the first three platforms that appear together when platform1 is True
                                if link.rect.colliderect(r):
                                    return                                          #ends function before returning WATER so Player doesnt drown
                        else:   
                            for r in Game.platform2_Rects:                          #list of other three platforms that appear together when platform2 is True
                                if link.rect.colliderect(r):
                                    return
                    if link.move != DROWN:                                          #if not already drowning, move is set to drown and frame to 0
                        link.frame = 0
                        link.move = DROWN
                    link.collision = "drowning"             
                    link.animate_speed = 0.2
                    if link.frame + link.animate_speed >= len(link.pics[link.move]):    #if drowning animation is over, dies
                        link.game_over()

                elif isinstance(obj,Enemy):
                    enemies.remove(obj)
                    del obj
                return "WATER"

            elif col == (0,255,0):
                return "DOORWAY"

            elif col == (255,255,0):
                return "SWITCH_FLOOR"            #shrine masks are yellow where other floor is to indicate that other mask should be used

            else:
                return "CLEAR"


    def switch_map(self,new_map,new_x,new_y):
        "Game map is switched so old objects must be removed, new objects must be created, and some attributes must be reset."

        game.map = new_map                      
        link.x,link.y = new_x,new_y
        link.respawn_location = (new_x,new_y)
        game.offset()                                               #link's x/y and game map have changed since .offset() was called, so must be called again to update
        mouse.set_pos([link.x+game.offset_x,link.y+game.offset_y])  #sets mouse over Player when entering an area. Prevents player from getting trapped in a loop of being forced through exits because of the mouse's last position

        for i in range(len(projectiles)):       #all old enemies, projectiles, and npcs are deleted when maps are switched
            del projectiles[-1]
        for i in range(len(enemies)):             
            del enemies[-1]
        for i in range(len(npcs)):              
            del npcs[-1]
        for i in range(len(collectibles)):
            del collectibles[-1]
        for i in range(len(animations)):
            del animations[-1]

        Game.rects = []                             #list is reset when maps switches so rects on another map dont interfere with this one
        if maps[game.map].name == "shrine":         #these rects are only in the shrine map, and since the objects the rects are for aren't created in a class with an 
            Game.rects.append(Game.switch[RECT])    # init method, they exist all the time so their rects can't just be appended then. instead they are appended when the map is switched
            Game.rects.append(Game.stair_gate_rect)
        maps[game.map].create_objects()             #objects that belong on the new map are created when the map is switched

        if game.track != maps[game.map].track:      #only change the track and play music if it's a new track. otherwise same track will restart from the beginning
            game.track = maps[game.map].track
            game.play_music("play")

        boomerang.come_back = True
        boomerang.being_used = False

            
class Game():   #for variables and functions either unassociated with any other class/referenced by multiple. 
    pics = []                                   #for miscellaneous pics
    page_pics = []                              #contains images of title screen,enter name screen, story image, etc
    rects = []                                  #list of rects that can't be walked through, like npc rects, switch rect, gate rects
    pressing_shortcut = False                   #True if any of the number keys used to switch items are pressed. Used to make sure item isn't used while switching item    
    dialogue_font = font.Font("MyMCFont.otf",16)#font used for dialogue text  
    clock = time.Clock()                        #used to set fps program runs at
    loops = 0                                   #loops increase with each frame of the game, so 50 times/second. Used to calculate time between events
    dest_x,dest_y = 0,0                         #coordinate link runs to if not following mouse
    warp_rect = Rect(255,785,20,20)             #Rect to collide with to end game

    #Shrine variables - variables that will exclusively be used in the shrine
    shrine_platform = 1                         #Can either be 1 or 2. Each has 3 Rects. Used to allow Player to cross water in shrine
    platform1_Rects = [Rect(900,1165,77,68),Rect(1017,1226,74,67),Rect(833,1393,129,64)]            #platforms and switches are Game attributes because they'll only be used once and aren't important enough to have their own classes
    platform2_Rects = [Rect(835,1236,88,66),Rect(955,1329,74,29),Rect(1114,1282,74,119)]
    switch = [0,Rect(1010,84,45,45),0]          #list contains all info about switch
    gates = [True,False]                        #there are 3 gates: bool indicates whether gate is True - up(can't pass) or False - down(can pass)
    stair_gate_rect = Rect(1102,640,45,28)
    switch_gate_rect = Rect(1007,368,53,32)
    boss = None        #this will be the boss when the object is created
    forced_fight = False                        #some things only happen during the forced fight or boss fight. 
    boss_fight = False
    floor = 1                                   #shows which floor of shrine player is at. floor decides which mask will be used
    warp = False                                #after boss is defeated, warp appears to take player back to southfield

    def __init__(self):                 
        "Contains all methods either unrelated to any class or called by several classes"
        
        self.map = 0                                        #index of maps. Indicates current map
        self.offset_x,self.offset_y = 0,0                   #offset is used to convert world coordinates to screen coordinates for when something must be blitted on the screen
        self.call_pixelize,self.count_pixelize = False,0
        self.prompt = None
        self.rupee_text = self.render_text("0",100,50,1,(0,0,255))      #text of number to be blitted on screen showing number of rupees link has
        self.heart_piece_text = self.render_text("0",100,50,1,(0,0,255))#text of number to be blitted on screen showing number of heart pieces link has collected
        self.load_save_file = False                                     #if continue option chosen from title screen, save file is loaded and player continues game from where they saved it
        self.page = "Title"                                             #page indicates which page game is at and is used to call the corresponding function
        self.item_animation = None                                      #if player gets an item, its image appears until space bar clicked
        self.tracks = []                            #list of music tracks that will play
        self.track = T_TITLE                        #Index of list of tracks that is currently playing
        self.sfx_secret = False                     #when True, sound effect will play. sound effect for something appearing
        self.sfx_treasure = False                   #when True, sound effect will play. sound effect for victory
        self.sfx_gameover = False                   #when True, sound effect will play. sound effect for death
        self.bomb_wall = True                       #blowing up wall reveals entrance to fairy fountain. can't enter unless wall is blown up. Bool tells whether blown up
        self.cursor_angle = 0                                           #angle cursor image is rotated to

        
    #Page functions - depending on page the game is at, a page function will be called
    def title_screen(self):
        "Method for running title screen. Called if game page is 'Title'. Runs repeatedly until program exited or Continue or New Game chosen."

        self.title_y = 0                        #y position at which title screen image is blitted
        newgame_rect = Rect(324,344,152,32)     #buttons to select New Game or Continue
        continue_rect = Rect(324,396,152,32)
        self.track = T_TITLE
        self.play_music("play")
        
        running = True
        while running:
            for e in event.get():
                if e.type == QUIT:
                    return "Exit"

            Game.mx,Game.my = mouse.get_pos()
            Game.mb = mouse.get_pressed()
            mouse.set_visible(True)

            #scroll title screen
            if self.title_y > -600:             #makes the title screen image scroll up slowly until the bottom of the image shows.
                self.title_y -= 3               # screen height is 600 and image heigt is 1200, so blitting at -600 shows bottom

            #check collisions with buttons
            if Game.mb[0] == 1 and self.title_y == -600:
                if newgame_rect.collidepoint(Game.mx,Game.my):        #selecting New Game takes you to screen where you enter your name
                    return "Story"
                elif continue_rect.collidepoint(Game.mx,Game.my):     #selecting Continue takes you straight to the actual game
                    self.load_save_file = True
                    return "Play"

            game.draw_scene()
            Game.loops += 1             #loops increases with every frame of the game, so 50 times per second
            Game.clock.tick(50) 


    def story(self):
        "Method for scrolling through story image."

        self.story_y = 0                        #y position at which story image is blitted
        self.track = T_END
        self.play_music("play")
        
        running = True
        while running:
            for e in event.get():
                if e.type == QUIT:
                    return "Exit"

            #scroll image
            if self.story_y > -3000:             #blits the image higher and higher until you see the bottom
                if self.story_y%600 == 0:
                    time.wait(3000)              #waits a little bit every 600 pixels (height of screen) so there's more time to read
                self.story_y -= 2               # screen height is 600 and image height is 3600, so blitting at -3000 shows bottom
            else:
                time.wait(300)
                return "Name Entry"

            game.draw_scene()
            Game.loops += 1             #loops increases with every frame of the game, so 50 times per second
            Game.clock.tick(50) 


    def enter_name(self):
        "Method called if New Game selected from title screen and page is 'Name Entry'. Allows player to enter name for their character. Runs until player hits escape or enter keys."

        self.track = T_ENTER_NAME
        self.play_music("play")

        running = True
        while running:
            for e in event.get():
                if e.type == QUIT:
                    return "Exit"

            game.draw_scene()
            
            link.name = game.getName()
            maps[4].npcs[0][7][0] = "Ah "+link.name+", where have you been?"        #npc has a line where he says Player name. npc tup containing his lines has already been created, so it is updated
                                                                                    # with the new name inputted by the player, so that when the npc object is created, his line contains the new name
                                                                                    # maps[4] is the map the npc appears on, he is the first npc in the list, his lines are at the 7th position in the tup, and
            Game.mx,Game.my = link.x,link.y                                         # the line that needs to be updated is the first one
            return "Play"               #once name has been entered, game begins

            Game.loops += 1             #loops increases with every frame of the game, so 50 times per second
            Game.clock.tick(50)   


    def pause_game(self):
        "Method runs if escape key pressed while playing and page becomes'Pause'. Can either save or exit game from this page."

        save_rect = Rect(295,168,214,98)
        exit_rect = Rect(295,326,214,98)

        self.track = T_PAUSE
        self.play_music("play")

        running = True
        while running:
            click = False
            for e in event.get():
                if e.type == QUIT:
                    return "Exit"
                if e.type == MOUSEBUTTONDOWN:
                    if e.button == 1:
                        click = True                #pressing mouse button will only be True for one frame of game so save function isnt called repeatedly
                if Game.check_keys(e) == "Play":    #if escape key was pressed, check_keys() returns Pause or Play depending on what the current page is
                    return "Play"

            Game.mx,Game.my = mouse.get_pos()
            Game.mb = mouse.get_pressed()
            mouse.set_visible(True)

            #check collisions with buttons
            if click and save_rect.collidepoint(Game.mx,Game.my):
                self.save_game()
            elif Game.mb[0] == 1 and exit_rect.collidepoint(Game.mx,Game.my):
                return "Exit"

            game.draw_scene()
            Game.loops += 1             #loops increases with every frame of the game, so 50 times per second
            Game.clock.tick(50) 


    def gameover_screen(self):
        "Method runs if player dies. Player can chose to exit or retry."

        retry_rect = Rect(295,101,214,98)       #retrying will respawn player
        exit_rect = Rect(295,355,214,98)

        self.track = T_GAMEOVER
        self.play_music("play")

        running = True
        while running:
            click = False
            for e in event.get():
                if e.type == QUIT:
                    return "Exit"

            Game.mx,Game.my = mouse.get_pos()
            Game.mb = mouse.get_pressed()
            mouse.set_visible(True)

            #check collisions with buttons
            if Game.mb[0] == 1:
                if retry_rect.collidepoint(Game.mx,Game.my):
                    return "Play"
                elif exit_rect.collidepoint(Game.mx,Game.my):
                    return "Exit"

            game.draw_scene()
            Game.loops += 1             #loops increases with every frame of the game, so 50 times per second
            Game.clock.tick(50) 


    def roll_credits(self):
        "Not exactly credits as there aren't a lot of people to credit, but close enough as it runs when the game ends. Method scrolls credit image."

        self.credits_y = 0                          #y position at which credits image is blitted
        self.track = T_END
        self.play_music("play")
        
        running = True
        while running:
            for e in event.get():
                if e.type == QUIT:
                    return "Exit"

            #scroll image
            time.wait(1000)
            if self.credits_y > -3600:             #blits the image higher and higher until you see the bottom
                if self.story_y%600 == 0:
                        time.wait(3000)           #waits a little bit every 600 pixels (height of screen) so there's more time to read
                self.credits_y -= 1               # screen height is 600 and image height is 4200, so blitting at -3600 shows bottom
            else:
                time.wait(1000)
                return "Title"

            game.draw_scene()
            Game.loops += 1             #loops increases with every frame of the game, so 50 times per second
            Game.clock.tick(50) 


    def play_game(self):    
        "Method contains while running loop for main game. Runs repeatedly while actual game is being played. Stops running if game is exited or pause menu is opened."        

        self.track = maps[self.map].track
        self.play_music("play")

        running = True
        while running:
            Game.space_click = Game.left_click = Game.right_click = False       #set to True when pressed. This makes it so they only stay True for 1 loop
            
            for e in event.get():
                if e.type == QUIT:
                    return "Exit"

                elif e.type == USEREVENT+1:             #event sent from play_music() that sound effect has ended
                    self.play_music("play")             #normal track is played again                    

                elif e.type == MOUSEBUTTONDOWN:

                    if e.button == 1:
                        Game.left_click = True
                    elif e.button == 2:                 #if scroll wheel is clicked, sets a destination at the mx,my position mouse was at. Intead of following the mouse, player runs to the destination          
                        Game.dest_x,Game.dest_y = Game.mx-self.offset_x,Game.my-self.offset_y       #destination is wherever mouse was at the time button was clicked
                        link.follow_cursor = False
                    elif e.button == 3:
                        Game.right_click = True
                    elif e.button == 4 or e.button == 5:    #roll by scrolling the mouse
                        link.roll()

                    if link.collision == None and Game.pressing_shortcut == False:  #item can only be used if Player isn't colliding and not trying to change item
                        if Game.left_click:
                            if link.equipped1.button_type == "click":                               #only items that are used when mouse button is clicked are set to True here
                                if link.equipped1 != boomerang or boomerang.being_used == False:    #can't use the boomerang again if it hasnt returned to link yet
                                    link.using_item1 = True
                        elif Game.right_click:
                            if link.equipped2.button_type == "click":
                                if link.equipped2 != boomerang or boomerang.being_used == False:
                                    link.using_item2 = True

                if Game.check_keys(e) == "Pause":   #if escape key was pressed, check_keys() returns Pause or Play depending on what the current page is
                    return "Pause"
            
            Game.mx,Game.my = mouse.get_pos()     
            Game.mb = mouse.get_pressed()
            mouse.set_visible(False)

            if link.collision == None and Game.pressing_shortcut == False:
                if link.equipped1.button_type == "hold":            #Only items that are used while mouse button is being held are set to True from here
                    if Game.mb[0] == 1:                             #Using item while mb down, done using item once mb released
                        link.using_item1 = True
                    else:
                        link.using_item1 = False
                        link.equipped1.being_used = False
                        link.animate_speed = 0.3
                elif link.equipped2.button_type == "hold":
                    if Game.mb[2] == 1:
                        link.using_item2 = True
                    else:
                        link.using_item2 = False
                        link.equipped2.being_used = False
                        link.animate_speed = 0.3
            elif link.collision:
                link.using_item1 = link.using_item2 = False

            #Calling Link methods - methods to move,update,animate,etc the Player object. Called according to attributes
            if link.using_item1:
                link.use_item(link.equipped1)
            elif link.using_item2:
                link.use_item(link.equipped2)
            else:                                                   #if not using item and not collding, move
                if link.collision == None and link.follow_cursor:
                    link.move_link(Game.mx-self.offset_x,Game.my-self.offset_y)              #link moves in the direction of the mouse. subtracting offsets converts mouse screen coords to world coords
                elif link.follow_cursor == False:
                    link.move_link(Game.dest_x,Game.dest_y)

            maps[self.map].read_map(link.x,link.y,link) 
            
            Game.animate(link)

            if link.collision == "getting_blocked":         #method called based on what object collision is
                self.get_blocked(link)
            elif link.collision == "getting_hit":
                self.get_hit(link)
            elif link.collision == "rolling":
                link.roll()
            elif link.collision == "dying":
                if link.game_over() == "Gameover":      #game_over function returns game over to switch to gameover page when player dies
                    return "Gameover"
            if link.invincible:
                self.invincibility(link)

            #Calling enemy methods - methods to move,update,etc the enemy object. Called according to attributes
            for enemy in enemies:               
                if enemy.collision == None:
                    enemy.move_enemy()
                if enemy.collision == "getting_blocked":
                    self.get_blocked(enemy)
                elif enemy.collision == "getting_hit":
                    self.get_hit(enemy)
                if enemy.invincible:
                    self.invincibility(enemy)
                Game.animate(enemy)

            #Calling projectile methods - methods to move,update,etc the projectile object. Called according to attributes
            for projectile in projectiles:
                if projectile.collision == None:
                    projectile.move_projectile()
                if projectile.collision == "getting_blocked":
                    self.get_blocked(projectile)
                Game.animate(projectile)

            #Calling animation methods - methods to move,update,etc the animation object. Called according to attributes
            for animation in animations:
                if animation.moves:                 #some animation's x/y positions move and others' don't. move_animation() only called if animation's x/y should change
                    animation.move_animation()
                Game.animate(animation)

            #Calling collectible methods - methods to move,update,etc the collectible object. Called according to attributes
            for collectible in collectibles:
                if collectible.call_animate:        #some collectibles have animations, others don't
                    Game.animate(collectible)
                if collectible.temp:                #some collectibles disappear, others don't
                    collectible.disappear()

            #Calling npc methods - methods to move,update,etc the npc object. Called according to attributes
            for npc in npcs:
                if npc.animate:
                    Game.animate(npc)  
                if npc.speaking:
                    npc.speak()

            #Calling boss methods - methods to move,update,etc the boss object. Called according to attributes
            if Game.boss != None:
                if Game.boss.move_type == Game.boss.collision == None:      #new move is chosen if old move has ended(move_type None)
                    Game.boss.choose_move()
                elif Game.boss.move_type == "move":                         #"move" type move has its own method
                    Game.boss.move_boss()

                Game.animate(Game.boss)
                Game.make_Rect(Game.boss)
                Game.boss.make_hitbox()

                if Game.boss.collision == "getting_blocked":
                    Game.boss.boss_get_blocked()
                elif Game.boss.collision == "getting_hit":
                    self.boss.boss_get_hit()

            if maps[self.map].name == "shrine":
                Game.shrine()
                Game.switch_floor()             #the only map with 2 floors is the shrine, so switch floor is only called if that's the current map

            if self.check_collisions() == "Credits":           #objects are checked for collisions. if collide with warp, game ends
                return "Credits"
            if self.load_save_file:                             #load game is called to overwrite default starting attributes and variables with the ones
                self.load_game()                                # from when the game was last saved
            game.draw_scene()                                   #everything is blitted on screen. 
            Game.loops += 1                                     #loops increases with every frame of the game, so 50 times per second
            Game.clock.tick(50) 



    #Load and Save functions
    def save_game(self):
        "Writes certain variables and attributes to a text file that can be read later to update those variables when the save is loaded."

        file = open("savefile.txt","w")
        
        info = [                                            #info is a 2D list containing strings of all the variables/attributes/etc that must be written to file. 1D lists are mostly sorted by type of info, but it's a 2D list more to ensure that the order the info is written in is consistent with how it's read.
        [str(link.respawn_location[0]),                     #Player will start at location current respawn location is at
        str(link.respawn_location[1]),
        str(link.max_health),
        str(link.rupees),
        str(link.heart_pieces),
        link.name],
        [str(int(item.unlocked)) for item in Player.items], #player will be able to use all the items currently unlocked upon loading the save
        ]

                                                    #map lists for animations,collectibles,and npcs can be changed,so every list is written into the text file and loaded and updated again
        all_objects = []                            #will contain 3 strings: one with all info for animations, one for collectibles, one for npcs
        #animation objects
        all_animations = ""                         #string will contain all info for creating tuples for creating every animation object for every map
        for gamemap in maps:
            map_animations = ""                     #string will contain all info for creating tup for creating every animation on current gamemap                     

            if len(gamemap.animations) == 0:        #if there are no animations, None will be added to the string as a placeholder so the order doesnt get messed up
                map_animations += "None"
            else:
                for animation in gamemap.animations:            #string will contain all info for creating tup for creating a single animation
                    animation_string = "{}&{}&{}&{}&{}&{}&{}&{}".format(str(animation[0]),str(animation[1]),str(animation[2]),animation.__class__.__name__,str(animation[4]),str(animation[5]),str(int(animation[6])),animation[7])

                    if gamemap.animations[-1] != animation:     #each animation's info is seperated from the other animations by a star
                        animation_string += "*"
                    map_animations += animation_string          #animation info is dumped into map string 

            if maps[-1] != gamemap:
                map_animations += ";"                   #each map's animations are seperated from other maps by a semicolon
            all_animations += map_animations            #map animations info is dumped into string for all animations
        all_objects.append(all_animations)              #once animations for all maps have been added, string appended to list

        #collectible objects
        all_collectibles = ""                           #string will contain all info for creating tuples for creating every collectible object for every map
        for gamemap in maps:
            map_collectibles = ""                       #string will contain all info for creating tup for creating every collectible on current gamemap                     

            if len(gamemap.collectibles) == 0:
                map_collectibles += "None"
            else:
                for collectible in gamemap.collectibles:            #string will contain all info for creating tup for creating a single collectible
                    collectible_string = "{}&{}&{}".format(str(collectible[0]),str(collectible[1]),str(collectible[2]))

                    if gamemap.collectibles[-1] != collectible:     #each collectible's info is seperated from the other collectibles by a star
                        collectible_string += "*"
                    map_collectibles += collectible_string          #collectible info is dumped into map string 

            if maps[-1] != gamemap:
                map_collectibles += ";"                 #each map's collectibles are seperated from other maps by a semicolon
            all_collectibles += map_collectibles        #map collectibles info is dumped into string for all collectibles
        all_objects.append(all_collectibles)            #once collectibles for all maps have been added, string appended to list

        #npc objects
        all_npcs = ""                                   #string will contain all info for creating tup for creating every npc on current gamemap                     
        for gamemap in maps:
            map_npcs = ""                               #string will contain all info for creating tup for creating every npc on current gamemap                     

            if len(gamemap.npcs) == 0:
                map_npcs += "None"
            else:
                for npc in gamemap.npcs:                #string will contain all info for creating tup for creating a single npc

                    if npc[4] == None:                  #some enemies give something while others dont
                        name = "None"
                    elif isinstance(npc[4],Item):
                        name = npc[4].name
                    elif isinstance(npc[4],Collectible):
                        name = npc[4].move
                    npc_string = "{}&{}&{}&{}&{}&{}&{}&{}&{}&{}&".format(str(npc[0]),str(npc[1]),str(npc[2]),str(npc[3]),name,str(npc[5][0]),str(npc[5][1]),str(npc[5][2]),str(npc[5][3]),npc[6])
                    for line in npc[7]:                 #npc dialogue is all added on at the end
                        npc_string += line
                        if line != npc[7][-1]:
                            npc_string += "&"           #amperand added on to all but last line

                    if gamemap.npcs[-1] != npc:         #each npc's info is seperated from the other npcs by a star
                        npc_string += "*"
                    map_npcs += npc_string              #npc info is dumped into map string 

            if maps[-1] != gamemap:
                map_npcs += ";"                         #each map's npcs are seperated from other maps by a semicolon
            all_npcs += map_npcs                        #map npcs info is dumped into string for all npcs
        all_objects.append(all_npcs)                    #once npcs for all maps have been added, string appended to list

        info.append(all_objects)

        other_variables = []
        other_variables.append(str(self.map))
        other_variables.append(str(self.loops))
        info.append(other_variables)

        shrine_variables = []
        shrine_variables.append(str(Game.switch[COL]))
        shrine_variables.append(str(int(Game.forced_fight)))
        shrine_variables.append(str(int(Game.boss_fight)))
        shrine_variables.append(str(Game.floor))
        shrine_variables.append(str(int(Game.warp)))
        info.append(shrine_variables)


        for lines in info:
            for line in lines:
                file.write(line+"\n")

        file.close()

            
    def load_game(self):
        "When game is loaded, certain variables and attributes carry over, while others are set again. This is called after everything has been set, so anything that should carry over overwrites the default. Method reads info from text file and overwrites attributes."

        info = open("savefile.txt").read().strip().split("\n")  #reads the file as a giant string, strips any extra new lines, and splits it at each new line to make it a list
                                                                #savefile contains all attributes that need to be updated. Each attribute is on its own line, so once split, each attribute is an index of the created list
                                                                #attributes are set in same order they were written. Order is pretty much arbitrary but is roughly in order of appearance in the code. Writing and calling in the same order is all that matter though
        link.x,link.y = int(info[0]),int(info[1])               #file is read as a string, so integers must be converted before being set       
        link.respawn_location = (link.x,link.y)
        link.health = link.max_health = int(info[2])
        link.rupees = int(info[3])
        self.rupee_text = self.render_text(str(link.rupees),100,50,1,(0,0,255)) #since rupees are updated, new text must also be rendered for the number
        link.heart_pieces = int(info[4])
        link.name = info[5]
        maps[4].npcs[0][7][0] = "Ah "+link.name+", where have you been?"        #npc has a line where he says Player name. npc tup containing his lines has already been created with the default name, so it is replaced with line with selected name
        for i,item in enumerate(Player.items):
            item.unlocked = bool(info[6+i])                     #unlocked is a bool, but "True" and "False" converted to bools both return True. So False is written as "0" and True as "1", then they are converted to integers and then to bools to make sure the right bool is returned
                                                                #map lists of tuples for spawning animations,collectibles,and npcs can change, so all these lists for all the maps are rewritten
        all_animations = info[9].split(";")                     #each map's info is seperated from other maps with a semicolon. splitting at the semicolon returns a list with each element being a string containing all its animations
        for i,gamemap in enumerate(maps):                       #each maps animation list is cleared so it can be rewritten
            gamemap.animations = []

            map_animations = all_animations[i].split("*")      #each animation on the map is seperated from the next by a star. splitting at the space returns a list with each element being a string containing all the information for a single animation
            for parameter_set in map_animations:            #each set of info is seperated by ampersands, so splitting each at the commas returns a list with each element being a string of a parameter
                parameters = parameter_set.split("&")
                tup = (int(parameters[0]),int(parameters[1]),float(parameters[2]),Game.dict[parameters[3]].pics,None,int(parameters[5]),bool(int(parameters[6])),parameters[7])       #here, each string is converted to the data type required. the magic number for the move and the class used to access the list of pics are in a dictionary in order to convert them from strings to variables with assigned meaning
                gamemap.animations.append(tup)

        all_collectibles = info[10].split(";")                   #the exact same thing as for animations is done for collectibles
        for i,gamemap in enumerate(maps):
            gamemap.collectibles = []
            map_collectibles = all_collectibles[i].split("*")
            for parameter_set in map_collectibles:
                parameters = parameter_set.split("&")
                tup = (int(parameters[0]),int(parameters[1]),int(parameters[2]))
                gamemap.collectibles.append(tup)

        all_npcs = info[11].split(";")                          #same thing is done for npcs as for animations and collectibles
        for i,gamemap in enumerate(maps):
            gamemap.npcs = []
            map_npcs = all_npcs[i].split("*")
            for parameter_set in map_npcs:
                parameters = parameter_set.split("&")

                if parameters[4] == "None":             #some npcs give items while others dont
                    item = None
                else:
                    item = Game.dict[parameters[4]]

                tup = (int(parameters[0]),int(parameters[1]),int(parameters[2]),float(parameters[3]),item,Rect(int(parameters[5]),int(parameters[6]),int(parameters[7]),int(parameters[8])),parameters[9],parameters[10:])
                gamemap.npcs.append(tup)

        maps[self.map].switch_map(int(info[12]),link.x,link.y)  #map is switched to map from when last saved. Since default starting map was selected momentarily, it's the same as switching the map
        Game.loops = int(info[13])
        Game.switch[COL] = int(info[14])                       #switch colour could start off as green,unactivated; or blue, off

        forced_fight = info[15]
        if forced_fight == "0":        #Can't just do bool(int("num")) here because variables could be True, False, or "over". bool("over") returns True, so instead they must be checked with ifs and set accordingly
            Game.forced_fight = False
        elif forced_fight == "1":
            Game.forced_fight = True
        else:
            Game.forced_fight = "over"

        boss_fight = info[16]
        if boss_fight == "0":
            Game.boss_fight = False
        elif boss_fight == "1":
            Game.boss_fight = True
            Game.boss = Boss()
        else:
            Game.boss_fight = "over"

        Game.floor = int(info[17])
        Game.warp = bool(int(info[18]))

        
        self.load_save_file = False
        
        
    #General useful functions called from various places and by several classes
    def play_music(self,action):
        "Loads the track specified by game.track."

        if action == "play":
            mixer.music.load(self.tracks[self.track])
            mixer.music.play(-1)                            #track will repeat until a new track is selected

        elif action == "sfx":                               #track will only play once
            if self.sfx_secret:                             #track is chosen based on variables
                sfx = T_SFX_SECRET
                self.sfx_secret = False
            elif self.sfx_treasure:
                sfx = T_SFX_TREASURE
                self.sfx_treasure = False
            elif self.sfx_gameover:
                sfx = T_SFX_GAMEOVER
            mixer.music.pause()
            mixer.music.set_endevent(USEREVENT+1)           #sends an event to the event queue when the sound effect ends so the normal track can continue playing.
            mixer.music.load(self.tracks[sfx])              #pygame events are integers, so to ensure a different event isnt accidentally triggered by using the same integer for
            mixer.music.play()                              # the event, making it greater than USEREVENT ensures that it is unique 

        elif action == "stop":
            mixer.music.stop()

   
    def offset(self):
        "Calculates offset to convert world coordinates to screen coordinates when drawing. calculates offset by subtracting player position from centre of screen"

        offset_x = 400-link.x                               #400,300 is middle of screen. offset is found by subtracting position from middle of screen. 
        if offset_x > 0:                                    #map will be blitted at offset. If player is at the left or top of the screen, offset is positive. map will be blitted farther right/down from 0,0 instead of staying at the corner of the screen
            offset_x = 0                                    # so if it's greater than 0, it's set to 0 so it stays at the corner. The max offset can be is 0
        elif offset_x < 400-(maps[self.map].width-400):     #if the player position is greater than the width or height of the map - half the screen, this means the player is at the very right/bottom of the screen 
            offset_x = 400-(maps[self.map].width-400)       # and there isnt enough space on the map for the player to remain in the middle of the screen while also keeping the edge of the map from going past the edge of the screen                                                                  
                                                            # so the offset is set to the middle of the screen - (width-middle of screen) so the edge of the map stays at the edge of the screen. So, the min offset is middle of the screen - (width-middle of screen)
        offset_y = 300-link.y
        if offset_y > 0:
            offset_y = 0
        elif offset_y < 300-(maps[self.map].height-300):
            offset_y = 300-(maps[self.map].height-300)

        self.offset_x,self.offset_y = offset_x,offset_y


    @classmethod
    def time(cls,tp):
        "Returns current time in frames or seconds."
        
        if tp == "sec":                 #can return in seconds for more intuitive and simpler measure, or in frames for more exact and specific measure
            sec = cls.loops // 50       #game is set to looping 50 times per second. loops increases every loop. dividing gives the number of seconds that have passed
            return sec                  
        else:
            return cls.loops


    def getName(self):                  #-code from split2.py
        "Allows user to input text with a keyboard"               
        
        ans = ""                    # final answer will be built one letter at a time.
        back = screen.copy()        # copy screen so we can replace it when done
        textArea = Rect(5,5,200,25) # make changes here.
        
        typing = True
        while typing:
            
            for e in event.get():
                if e.type == QUIT:
                    event.post(e)   # puts QUIT back in event list so main quits
                    return ""
                if e.type == KEYDOWN:
                    if e.key == K_BACKSPACE:    # remove last letter
                        if len(ans)>0:
                            ans = ans[:-1]
                    elif e.key == K_KP_ENTER or e.key == K_RETURN : 
                        typing = False
                        if ans == "":                           #if no name was inputted, default name is Link
                            ans = "Link"
                    elif e.key < 256 and len(ans) < 18:         #max length is 25
                        ans += e.unicode       # add character to ans

            text_surf = Game.render_text(ans,300,65,5,(255,255,255))    #only thing ever drawn outside of draw_scene().
            screen.blit(back,(0,0))                                     # needs to be drawn here to show the letters as they appear,
            screen.blit(text_surf,(260,135))                            # not just the final word at the end
            display.flip()
            
        return ans


    @classmethod       
    def render_text(cls,text,surf_x,surf_y,extrasp,col):           
        "Returns a surface with rendered text blitted on it."

        words = text.split()                        #returns a list with each word in the string separated into its own string
        for i in range(len(words)-1):
            words[i] += " "                         #adds a space to the end of each word except the last
        start = 0                                   #indices for words. used to decide which words will be on the same line so the line's width doesn't exceed the width of the box it's in
        end = len(words)
        rendered_text = []                          #rendered line in pieces that fit in the dialogue box
        while True:                 
            new_line = words[start:end]
            string = ""                             #converts list back to string so it can be rendered
            for word in new_line:
                string += word
                
            text = Game.dialogue_font.render(string,True,(col))

            if text.get_width() > surf_x-2*extrasp:             #x is width of surface, extrasp is the distance from the sides that text will be blitted at so text isnt right up against sides of text box
                end -= 1                                        #if width of text exceeds length, removes words from end until it fits
            else:                                               #when it fits, the start of the next line is the end of the previous, and the end of the line is reset to the end of the list again
                rendered_text.append(text)
                start = end
                end = len(words)   
            if start == len(words):                             #loops until the entire line has been rendered
                break
            
        text_surface = Surface((surf_x,surf_y))     #surface is size of text box that text will be blitted in
        text_surface.set_colorkey((0,0,0))          #only the white text will be visible on the surface so it can be blitted onto the textbox

        if len(rendered_text) > 1:                  #if there are several lines, they will be blitted beneath each other
            surf_y = 5
            for line in rendered_text:              #blits lines under each other on the surface
                text_surface.blit(line,(extrasp,surf_y))
                surf_y += line.get_height() + 5
        else:
            text_surface.blit(rendered_text[0],(extrasp,5))

        return text_surface


    @classmethod
    def check_keys(cls,e):              #e is event in event.get()
        "checks key events"
        
        if e.type == KEYDOWN:
            if e.key == K_SPACE:
                cls.space_click = True
                if game.prompt == "interact":       
                    link.collision = "interacting"     
                    link.animate_speed = 0
                    link.move = link.direction
                    link.frame = 10
                    game.prompt = None
                    trans_surf.fill((0,0,255))
                    link.interact_object.speaking = True

                    if link.interact_object.move < SIGN:            #character sprites are all before sign. Characters stop animating while 'talking'
                        link.interact_object.animate = False
                    elif link.interact_object.move > SIGN:          #chest sprites are all after sign. Chests animate when 'talking'
                        link.interact_object.animate = True

            elif e.key == K_ESCAPE:             #escape key is used to pause and unpause the game
                if game.page == "Play":
                    return "Pause"
                elif game.page == "Pause":
                    return "Play"

        Game.pressing_shortcut = False
        for item in Player.items:
            if key.get_pressed()[item.shortcut_key] == 1:
                Game.pressing_shortcut = True
                if cls.left_click:
                    item.switch_item("left")
                elif cls.right_click:
                    item.switch_item("right") 
    

    @classmethod       
    def animate(cls,obj):       
        "Increases frame of animation."

        reappend = False                #An object's rect changes when it animates, so it needs to be removed from the list and appended again so that the right rect is in the list
        if obj.rect in Game.rects:
            Game.rects.remove(obj.rect)
            reappend = True             #rect will be appended again once frame has changed           

        obj.frame += obj.animate_speed
        if obj.frame >= len(obj.pics[obj.move]):    

            if isinstance(obj,Projectile) and obj.move == BOOMERANG_SPIN and boomerang.loops < 8:
                boomerang.loops += 1

            if isinstance(obj,Boss):
                if obj.move_type != "rotate":               #rotate move ends once current_rotation = max_rotation, but the other moves end once count_move = 0
                    obj.count_move -= 1                     #count_move is decreased every time the animation finishes
                    if obj.move_type == "move":             #the direction of movement is also reset when the animation ends so the boss doesn't keep moving just horizontally or vertically
                        obj.move_direction = None
                    if obj.count_move == 0:       
                        obj.move_type = None

            if isinstance(obj,Animation) and obj.name != "smith_animation":     #most animations are removed once they end
                animations.remove(obj)
                del obj
            elif isinstance(obj,NPC) and obj.move > SIGN:       #chests stop animating once their animation loops once
                obj.animate = False
                obj.frame -= obj.animate_speed
                obj.animate_speed = 0
            else:
                obj.frame = 0
                if reappend == True:            #if frame exceeded list but object was not removed, Rect reappended
                    Game.make_Rect(obj)
                    Game.rects.append(obj.rect)

        elif reappend == True:                  #only happens if frame is not greater than list because
            Game.make_Rect(obj)                 # otherwise returns out of range error
            Game.rects.append(obj.rect)

            
    @classmethod
    def make_move(cls,folder,name,start,end,scale=None):           #[-Code from sprite2 example]
        "Creates list of all sprites for a move."
        
        move = []
        for i in range(start,end+1):            #all images pertaining to one move are named the same and numbered. loops through and loads each and appends them to move list
            if scale == None:
                move.append(transform.scale2x(image.load("imgs/{}/{}{}.png".format(folder,name,i))))
            else:
                move.append(transform.scale(image.load("imgs/{}/{}{}.png".format(folder,name,i)),scale))    #if scale is passed in, images are scaled before being appended to the list
        return move


    @classmethod    #static **
    def make_Rect(cls,obj):
        "Creates Rect object at another object's position."

        move = obj.move
        frame = int(obj.frame)
        pic = obj.pics[move][frame]
        obj.rect = Rect(obj.x-pic.get_width()//2,obj.y-pic.get_height()//2,pic.get_width(),pic.get_height())


    #Collision methods
    def check_collisions(self): 
        "Checks if 2 object's Rects collide, and decides type of collision based on object attributes."

        self.make_Rect(link)                    #Rects created for all objects using their sprites so they can be checked if they collide
        for enemy in enemies:
            self.make_Rect(enemy)
        for projectile in projectiles:
            self.make_Rect(projectile)
        for collectible in collectibles:
            self.make_Rect(collectible)
        for npc in npcs:
            self.make_Rect(npc)

        #enemy collisions
        for enemy in enemies:
            if enemy.rect.colliderect(link.rect) and enemy.collision == link.collision == None:    
                if link.invincible or (shield.being_used and link.direction == 3-enemy.direction):     
                    self.block_collision(enemy,link)                    #link blocks enemy
                elif sword.being_used:                                                  
                    self.hit_collision(enemy,link,sword)                #link hits enemy
                else:
                    self.hit_collision(link,enemy)                      #enemy hits link

        #boss collisions
        if Game.boss != None:
            if link.rect.colliderect(Game.boss.hitbox) and link.collision == Game.boss.collision == None:
                if link.invincible or shield.being_used:
                    self.block_collision(Game.boss,link)                    #link blocks boss
                elif sword.being_used:
                    self.hit_collision(Game.boss,link,sword)                #link hits boss
                else:
                    self.hit_collision(link,Game.boss)                      #boss hits link

        #projectile collisions    
        for projectile in projectiles:
            if projectile.rect.colliderect(link.rect):
                if projectile.target == "player":
                    if link.invincible or ((shield.being_used or sword.being_used) and link.direction == 3-projectile.direction) or link.collision == "interacting":  #3-projectile.direction is opposite to projectile direction. So, facing projectile   
                        self.block_collision(projectile,link)           #link blocks projectile 
                    else:
                        self.hit_collision(link,projectile)             #projectile hits link  
                else:
                    if projectile.move == BOOMERANG_SPIN and boomerang.come_back:   #boomerang returns to link
                        projectiles.remove(projectile)
                        del projectile
                        boomerang.being_used = False
                        boomerang.come_back = False

            else:
                if projectile.target == "enemy":      
                    for enemy in enemies:
                        if projectile.rect.colliderect(enemy.rect) and enemy.collision == None:
                            self.hit_collision(enemy,projectile)        #projectile hits enemy

                    if Game.boss != None:
                        if projectile.rect.colliderect(Game.boss.hitbox) and Game.boss.collision == None:
                            self.hit_collision(Game.boss,projectile)        #projectile hits boss

                    for collectible in collectibles:
                        if projectile.rect.colliderect(collectible.rect):
                            collectible.collect()

                    if projectile.rect.colliderect(Game.switch[RECT]) and Game.switch[COL] == BLUE:
                        Game.switch[COL] = RED
                        Game.switch[TIME] = Game.time("sec")

        #switch collisions
        if link.rect.colliderect(Game.switch[RECT]) and sword.being_used and Game.switch[COL] == BLUE:
            Game.switch[COL] = RED
            Game.switch[TIME] = Game.time("sec")

        #warp collision
        if Game.warp and link.rect.colliderect(Game.warp_rect):
            return "Credits"

        #collectible collisions
        for collectible in collectibles:
            if link.rect.colliderect(collectible.rect) and sword.being_used == shield.being_used == False:      #collectible picked up by running into it or throwing boomerang at it
                collectible.collect()

        #npc interaction rect collision
        for npc in npcs:
            if npc.inteRect != None:       #if not already talking
                if link.rect.colliderect(npc.inteRect) and npc.speaking == False:      #checks if link is near enough to an NPC (colliding with its interact Rect) to interact with it
                    game.prompt = "interact"    
                    link.interact_object = npc              #Not interacting with it yet, but it is the object link is being asked to interact with
                    break                                   #if link is close enough to one NPC to interact, when the loop continues and he isn't close enough
                elif link.rect.colliderect(npc.inteRect) == False or npc.speaking:                                       # to another, it will reset to None. break allows it to stop as soon as link is able to interact with one
                    game.prompt = None                      #if link isnt close enough to an NPC, these will be set to None
                elif link.rect.colliderect(npc.inteRect) == False:
                    link.interact_object = None

        #exit rect collisions
        for ex in maps[self.map].exits:             #check exits of map
            if ex[0].colliderect(link.rect):       
                if ex[1].name != "fairy_fountain" or (ex[1].name == "fairy_fountain" and game.bomb_wall == False):           #if trying to enter fountain, wall must have been blown up first
                    maps[game.map].switch_map(ex[1].num,ex[2],ex[3])



    def block_collision(self,obj1,obj2):       
        """ Method is called once when the collision happens to set attributes for the objects involved in the collision.
            obj1 is the object getting blocked; obj2 is the object doing the blocking.
        """

        obj1.collision = "getting_blocked"  #collision is "getting_blocked", so get_blocked() will be called
        obj1.collision_object = obj2
        obj1.frame = 0.1                    #getting blocked collision is over when frame = 0, so frame starts just above 0
        if isinstance(obj1,Projectile):     #if the object getting blocked is a projectile, once it gets blocked it will hurt enemies if they collide with it
            obj1.target = "enemy"       


    def hit_collision(self,obj1,obj2,weapon=None):
        """ Method is called once when the collision happens to set attributes for the objects involved in the collision.
        obj1 is object getting hit; obj2 is object hitting; weapon, if there is one, can be used to determine damage instead of obj2 in case obj2 itself doesn't have damage.
        """

        if weapon == None:
            weapon = obj2       #if there's no weapon, the one damaging is obj2, so it can be used to determine damage instead
        obj1.collision = "getting_hit"
        obj1.collision_object = obj2
        obj1.health -= weapon.damage
        obj1.frame = 0
        
        if obj1.health > 0:                 #obj1 gets hit but doesn't die
            if isinstance(obj1,Enemy) or isinstance(obj1,Boss):                             #Enemies and the Boss both have an animation of getting hit appear over their objects
                hit_animation = Animation(obj1.x,obj1.y,0.3,Enemy,obj1,ENEMY_DAMAGE,True,"enemy_hit")
                if isinstance(obj1,Octorok):                                                  #Enemies will turn to face the object that hit them when hit, but the Boss is so big that besides damaging it, it doesn't take notice of hits
                    obj1.move = 3-obj2.direction
                    obj1.direction = obj2.direction
                elif isinstance(obj1,Chuchu):
                    obj1.move = CHUCHU_DAMAGE
                    obj1.animate_speed = 0.1
                    obj1.direction = obj2.direction
                
            elif isinstance(obj1,Player):
                obj1.follow_cursor = True           #player returns to normal movement if hit
                obj1.animate_speed = 0.2
                self.call_pixelize = True           #screen will pixelize if Player takes damage
                self.count_pixelize = 5
                if (obj2.direction == RIGHT and obj1.x > obj2.x) or (obj2.direction == DOWN and obj1.y > obj2.y) or (obj2.direction == UP and obj1.y < obj2.y) or (obj2.direction == LEFT and obj1.x < obj2.x):
                    obj1.move = LINK_DAMAGE + (3-obj2.direction)    #if obj2 runs into link, his knockback animation direction is opposite to obj2's direction 
                    obj1.direction = obj2.direction                 # and his knockback direction is the same as obj2's direction
                else:
                    obj1.move = LINK_DAMAGE+obj1.direction          #if player runs into obj2, knockback animation direction will be same as own direction
                    obj1.direction = 3-obj1.direction               # and knockback direction will be opposite to own direction

        else:                               #obj1 dies
            if isinstance(obj1,Enemy) or isinstance(obj1,Boss):                             #Enemies and Boss both have death animation appear over their object position
                death_animation = Animation(obj1.x,obj1.y,0.3,Enemy,obj1,ENEMY_DEATH,True,"enemy_death")

            elif isinstance(obj1,Player):
                obj1.follow_cursor = True           #player returns to normal (lack of?) movement if dead
                obj1.collision = "dying"
                game.sfx_gameover = True
                game.play_music("sfx")
                obj1.move = LINK_DEATH
                self.call_pixelize = True
                self.count_pixelize = 5

        if isinstance(obj2,Projectile) and obj2.move != BOOMERANG_SPIN:                     #If a normal projectile hits an enemy, it will deal damage and disappear
            projectiles.remove(obj2)                                                        # but a boomerang will keep going and can hit multiple enemies
            del obj2


    def get_blocked(self,obj):
        "Method called every loop to knock back object being blocked until knockback is over."
           
        if obj.direction == RIGHT:                                 #knockback when blocked is always opposite to object's own direction
            new_x,new_y = obj.x-obj.knockback,obj.y
        elif obj.direction == DOWN:
            new_x,new_y = obj.x,obj.y-obj.knockback
        elif obj.direction == UP:
            new_x,new_y = obj.x,obj.y+obj.knockback
        elif obj.direction == LEFT:
            new_x,new_y = obj.x+obj.knockback,obj.y

        if isinstance(obj,Projectile) or maps[self.map].read_map(new_x,new_y,obj) != "WALL":    #if object is an enemy or link, only move x,y position if new position is not a wall 
            obj.x,obj.y = new_x,new_y                                                           # if Projectile, doesn't matter as it will disappear after getting blocked anyway
            
        if obj.frame == 0:                                                                      #knockback ends when frame is 0, attributes are reset
            obj.collision = None
            obj.collision_object = None          
            if isinstance(obj,Projectile) and obj.move != BOOMERANG_SPIN:                       #normal Projectiles will be deleted after knockback is over               
                projectiles.remove(obj)         
                del obj


    def get_hit(self,obj):
        "Method called every loop to knock back object getting hit until knockback is over."
        
        if obj.direction == RIGHT:                          
            new_x,new_y = obj.x+obj.knockback,obj.y                     #If object is getting hit, its direction was already set in hit_collision() so it                                                             
        elif obj.direction == DOWN:                                     # gets knocked back in its own direction
            new_x,new_y = obj.x,obj.y+obj.knockback
        elif obj.direction == UP:
            new_x,new_y = obj.x,obj.y-obj.knockback
        elif obj.direction == LEFT:
            new_x,new_y = obj.x-obj.knockback,obj.y
        if maps[self.map].read_map(new_x,new_y,obj) != "WALL":          #checks to make sure that area object knocked back into isnt a wall
            obj.x,obj.y = new_x,new_y

        if isinstance(obj,Octorok):         #Octorok doesnt have a seperate move for taking damage, so it has a counter instead that ends getting hit when it reaches 0 instead
            obj.count_knockback -= 1
            
        if (isinstance(obj,Octorok) == False and obj.frame == 0) or (isinstance(obj,Octorok) and obj.count_knockback <= 0):     #object is done getting hit when its animation ends, or if it doesn't have one, once its counter is 0
            obj.move = obj.direction
            obj.invincible = True  
            obj.collision = obj.collision_object.collision = obj.collision_object = None           

            if isinstance(obj,Octorok):                                                                                         #attributes are reset
                obj.count_knockback = 30                                                               
            if isinstance(obj,Player):
                obj.animate_speed = 0.3
            elif isinstance(obj,Chuchu):
                obj.move = CHUCHU_RUN
                self.animate_speed = 0.2
            
        if isinstance(obj,Enemy):           #enemy death                        #if Enemy health is 0, it's deleted and its drop collectible, if there is one, appears at its position
            if obj.health == 0:
                if obj.drop != None:
                    drop = Collectible(obj.x,obj.y,obj.drop,True)
                enemies.remove(obj)
                del obj


    def invincibility(self,obj):    
        "Object is temporarily unable to be hit again after getting hit to prevent getting trapped in an unescapable cycle of getting hit and knocked back."
        
        obj.count_invincibility -= 1            #object is invincible while counter is greater than 0. When it reaches 0, counter resets and object is no longer invincible               
        if obj.count_invincibility == 0:
            obj.invincible = False
            obj.count_invincibility = 5


    #Drawing methods - there are several to keep code organized, but all other drawing methods are called from draw_scene()
    def draw_scene(self):
        "Calls methods,draws and blits images based on page, map, and objects in game."

        #Draws background image based on page
        if self.page == "Title": 
            screen.blit(self.page_pics[TITLE],(0,self.title_y))

        elif self.page == "Story":
            screen.blit(self.page_pics[STORY],(0,self.story_y))

        elif self.page == "Name Entry":
            screen.blit(self.page_pics[ENTER_NAME],(0,0))

        elif self.page == "Pause":
            screen.blit(self.page_pics[PAUSE],(0,0))

        elif self.page == "Gameover":
            screen.blit(self.page_pics[GAMEOVER],(0,0))

        elif self.page == "Credits":
            screen.blit(self.page_pics[CREDITS],(0,self.credits_y))

        elif self.page == "Play": 
            self.offset()                                                       #calculates offset in relation to player x,y 
            screen.blit(maps[self.map].image,(self.offset_x,self.offset_y))     #blits map at offset so player remains in middle of screen

            #Anything specific to shrine, like platforms, gates
            if maps[self.map].name == "shrine":             
                Game.draw_shrine()

            #warp tiles
            if Game.warp:
                if maps[self.map].name == "southfield":
                    screen.blit(Game.pics[WARP][0],(1090+game.offset_x,690+game.offset_y))
                elif maps[self.map].name == "shrine":
                    screen.blit(Game.pics[WARP][0],(255+game.offset_x,780+game.offset_y))

            #All objects are blitted
            if Game.boss != None: 
                self.draw_objects([Game.boss]) 
            self.draw_objects(enemies)
            self.draw_objects(animations)
            self.draw_objects(collectibles)
            self.draw_objects(npcs)                                                                     
            self.draw_objects(projectiles)  
            self.draw_objects([link])                     

            #If Player took damage, screen will pixelize
            if self.call_pixelize:
                self.pixelize()

            #HUD is blitted after pixelization so it doesn't get pixelized if Player takes damage
            self.draw_hud()

            #Inventory is extra info similar to HUD only blitted if Player is standing still
            if link.rect.collidepoint(Game.mx-game.offset_x,Game.my-game.offset_y):
                self.draw_inventory()

            #Interact prompt/dialogue and dialogue box
            if game.prompt == "interact":
                trans_surf.blit(Game.pics[BOXES][1],(215,480))        #interact prompt image is blitted onto semi-transparent surface
                screen.blit(trans_surf,(0,0))                         #surface is blitted onto screen
            if link.interact_object != None:
                if link.interact_object.speaking:
                    trans_surf.blit(Game.pics[BOXES][0],(20,400))     #dialogue box image is blitted onto semi-transparent surface
                    screen.blit(trans_surf,(0,0))                     #surface is blitted onto screen
                    screen.blit(link.interact_object.dialogue[link.interact_object.count_dialogue],(40,420)) #text for correct line of dialogue in npc's dialogue list is blitted directly onto the screen so it isn't also semi-transparent            

            #draw cursor
            cursor_pic = Game.pics[CURSOR][0]
            rot_cursor_pic = Game.rot_center(cursor_pic,self.cursor_angle)  #rotate curor img
            self.cursor_angle += 3      
            if self.cursor_angle == 360:
                self.cursor_angle = 0
            if link.follow_cursor:
                screen.blit(rot_cursor_pic,(Game.mx-rot_cursor_pic.get_width()//2,Game.my-rot_cursor_pic.get_height()//2))
            else:
                screen.blit(rot_cursor_pic,(Game.dest_x-rot_cursor_pic.get_width()//2+self.offset_x,Game.dest_y-rot_cursor_pic.get_height()//2+self.offset_y))

        display.flip()


    def draw_objects(self,objs):
        "Selects sprite from object's 2D list using its move and frame and blits it so its centre is over the object's centre."

        if isinstance(objs,list):
            for element in objs:
                if maps[self.map].read_map(element.x,element.y,element) != "DOORWAY":       #if colour on mask returns doorway, object is not drawn.
                    move = element.move                     #selects correct sprite from object's 2D list of sprites using move and frame
                    frame = int(element.frame)
                    pic = element.pics[move][frame]

                    if isinstance(element,Boss):
                        if element.collision == "getting_hit":                      
                            pic = element.pics[move+4][frame]                       #adding 4 to move gives damage sprite in correct direction
                        if element.move_type == "rotate":
                            pic = Game.rot_center(pic,element.current_rotation)     #returns sprite rotated to current rotation angle
                            element.current_rotation += 3                           #rotation angle increases each loop
                            if element.current_rotation >= element.max_rotation:    #when current angle = max angle, rotation move is over and attributes are reset
                                element.current_rotation = element.max_rotation = 0
                                element.move_type = None
                                element.move = WALK + element.direction

                    screen.blit(pic,(element.x+self.offset_x-pic.get_width()//2,element.y+self.offset_y-pic.get_height()//2))


    @classmethod    #class method because shrine related variables are class variables
    def draw_shrine(cls):
        "For drawing things that only happen in the shrine."

        platform_pic = cls.pics[PLATFORMS][cls.shrine_platform-1]           #platform image
        screen.blit(platform_pic,(game.offset_x,game.offset_y))             #image is scaled to map size to it's blitted at same pos as map  

        switch_pic = cls.pics[SWITCHES][cls.switch[COL]]                    #switch image
        screen.blit(switch_pic,(1032+game.offset_x-switch_pic.get_width()//2,101+game.offset_y-switch_pic.get_height()//2)) #1032,101 is pos of switch on map

        for i in range(2):
            if cls.gates[i]:                                               #gate pic is blitted if True - if gate is up
                screen.blit(cls.pics[GATES][i],(game.offset_x,game.offset_y))


    def draw_hud(self):
        "HUD is constantly visible while game is being played. Method blits info like hearts, items being used, on the screen."
            
        screen.blit(self.pics[BUTTONS][0],(690,10))                         #Image of left and right mouse buttons
        screen.blit(Item.pics[0][link.equipped1.pos],(690,35))              #Image of items assigned to left and right buttons are blitted at their button
        screen.blit(Item.pics[0][link.equipped2.pos],(735,35))

        for i in range(int(link.max_health)//4):                            #each heart has 4 quarters. health attributes are measured in quarters to make it easier to deal quarter hearts of damage without decimals
            screen.blit(self.pics[HEARTS][0],(20+i*16,20))                  #empty hearts (like mine) - correct number of full max hearts blitted on screen
        for i in range(link.health//4):
            screen.blit(self.pics[HEARTS][4],(20+i*16,20))                  #full hearts - correct number of current hearts blitted on top of empty hearts so only the hearts missing from having taken damage appear empty
        rem = link.health%4
        if rem > 0:
            screen.blit(self.pics[HEARTS][rem],(20+(link.health//4*16),20)) #part hearts - if current hearts leaves a remainder, the last heart is only part of a heart


    def draw_inventory(self):
        "Inventory is similar to HUD, but is extra information only blitted when mouse is over player Rect, so player is standing still. Method blits info like heartpieces, rupees, and items."

        screen.blit(self.rupee_text,(750,550))                              #Text showing number of rupees Player has and image of rupee
        screen.blit(self.pics[BIG_BLUE_RUPEE][0],(720,550))
        screen.blit(self.heart_piece_text,(750,525))                        #Text showing number of heart pieces Player has and image of heart piece
        screen.blit(self.pics[PIECES][link.heart_pieces%3],(715,525))
        for i in range(len(Player.items)):                                  #images of unlocked items are blitted on screen
            if Player.items[i].unlocked:
                screen.blit(Item.pics[0][i],(20+i*50,550))
        

    def pixelize(self):
        "Pixelizes the screen when Link takes damage. Exists because it looks cool."
        
        num = randint(0,9)                                              #randint used to slightly change position of pixelized boxes every loop so it looks cooler
        for x in range(0-num,800+num,10):                               #gives top left corner positions of each box in 10x10 grid made across screen
            for y in range(0-num,600+num,10):
                avg_col = transform.average_color(screen,(x,y,10,10))   #finds average colour of box in grid
                draw.rect(screen,avg_col,(x,y,10,10))                   #blits rect of average colour over box
        self.count_pixelize -= 1                                        #when pixelize counter reaches 0, pixelize effect is over
        if self.count_pixelize== 0:
            self.call_pixelize = False

    @classmethod   
    def rot_center(cls,image,angle):                                #-Code from https://www.pygame.org/wiki/RotateCenter?parent=CookBook     
        """rotate an image while keeping its center and size"""
                                                                     
        orig_rect = image.get_rect()                             
        rot_image = transform.rotate(image, angle)                
        rot_rect = orig_rect.copy()                            
        rot_rect.center = rot_image.get_rect().center            
        rot_image = rot_image.subsurface(rot_rect).copy()         
        return rot_image
        

    @classmethod    #class method because shrine related variables are all class variables
    def shrine(cls):   
        "Lots of specific things only happen in the shrine, so it has its own method."
        
        #platforms
        if Game.time("frames")%100 == 0:            #which set of platforms is visible switches every 100 frames(2 seconds)
            if cls.shrine_platform == 1:
                cls.shrine_platform = 2
            else:
                cls.shrine_platform = 1

        #switch
        if cls.switch[COL] == RED:                             #if switch is on(red), stairs are open but entrance to room is blocked
            cls.gates[STAIRS] = False                          
            if cls.stair_gate_rect in cls.rects:
                game.sfx_secret = True                          #secret sound effect plays when gate opens
                game.play_music("sfx")
                cls.rects.remove(cls.stair_gate_rect)

            if cls.switch_gate_rect.colliderect(link.rect) == False:   #gate only rises if player isn't on it, so player doesnt get stuck
                cls.gates[SWITCH_ROOM] = True
                if cls.switch_gate_rect not in cls.rects:
                    cls.rects.append(cls.switch_gate_rect)
                
            if Game.time("sec") >= cls.switch[TIME]+3:             #if switch is red(on), returns to blue(off) after 3 seconds
                cls.switch[COL] = BLUE

        elif cls.switch[COL] == BLUE:                          #if switch is blue(off), stairs are blocked but the room is open
            if cls.stair_gate_rect.colliderect(link.rect) == False:
                cls.gates[STAIRS] = True                                
                if cls.stair_gate_rect not in cls.rects:
                    cls.rects.append(cls.stair_gate_rect)

            cls.gates[SWITCH_ROOM] = False
            if cls.switch_gate_rect in cls.rects:
                cls.rects.remove(cls.switch_gate_rect)
    
        #forced fight -> when room at top right of shrine entered, exit closed off and must defeat all enemies to leave
        if cls.forced_fight == False:  
            if link.y < 343:                        #because of how the map is laid out, if link is higher than 343, he must be in the room where the forced fight happens
                cls.forced_fight = True        
                game.sfx_secret = True                       #secret sound effect plays when fight begins
                game.play_music("sfx")
                link.respawn_location = (link.x,link.y)     #if player dies during fight, will respawn in the same room
                
                enemy1 = Octorok(675,103)
                enemy2 = Octorok(1166,103)
                enemy3 = Octorok(1166,340)
                enemy4 = Octorok(675,340)
                cls.forced_fight_enemies = [enemy1,enemy2,enemy3,enemy4]
                
                cls.gates[SWITCH_ROOM] = True               #gate is up blocking exit while fighting
                cls.rects.append(cls.switch_gate_rect)

        elif cls.forced_fight == True:         
            dead = True
            for enemy in cls.forced_fight_enemies:
                if enemy in enemies:                    #if none of the enemies are in enemies list, all have died and fight is over
                    dead = False
            if dead:
                cls.switch[COL] = BLUE         #when all enemies die, switch goes from green to blue and can now be activated to open the stair gate
                cls.forced_fight = "over"      #forced fight won't happen again even if Player reenters room
                game.sfx_secret = True        #secret sound effect plays when fight ends
                game.play_music("sfx")
                
        #boss fight
        if cls.boss_fight == False:
            if cls.stair_gate_rect.colliderect(link.rect) and cls.gates[STAIRS] == False:   #if link goes up the stairs, the boss spawns and fight begins
                cls.switch[COL] = GREEN                                                     #switch is deactivated and can't be reactivated once fight begins
                link.respawn_location = (1111,770)
                cls.boss_fight = "start"
                cls.boss = Boss()                                                           #Boss spawns when link passes through stair gate    
                game.sfx_secret = True        #secret sound effect plays when boss spawns
                game.play_music("sfx")

    @classmethod
    def switch_floor(cls):
        "When on the second floor or boss area, a different mask is used than when on the first floor. Function checks and switches mask accordingly."

        if maps[game.map].read_map(link.x,link.y,link) == "SWITCH_FLOOR":       #if mask at position is yellow, floor is switched
            if cls.floor == 1:
                cls.floor = 2
            else:
                cls.floor = 1

        mask1 = maps[game.map].mask
        mask2 = maps[game.map].mask2
        if cls.floor == 1:                                                      #depending on floor, mask is set
            maps[game.map].mask = mask1
        else:
            maps[game.map].mask = mask2


#---------------------------------------------------------------------------------
#Sprites
directions = ["right","down","up","left"]       #some moves have 4 versions, one in each direction. can loop through directions to make it easier to append all version of move to list

#Player sprites
for direction in directions:
    Player.pics.append(Game.make_move("link/run","run_"+direction,0,10))
for direction in directions:
    Player.pics.append(Game.make_move("link/roll","roll_"+direction,0,6))
Player.pics.append(Game.make_move("link/drown","drown",0,11))
Player.pics.append(Game.make_move("link/got_item","got_item",0,2))
for direction in directions:
    Player.pics.append(Game.make_move("link/link_damage","link_damage_"+direction,0,2))     
Player.pics.append(Game.make_move("link/link_death","link_death",0,12))
for direction in directions:
    Player.pics.append(Game.make_move("items/sword","sword_"+direction,0,7))     
for direction in directions:
    Player.pics.append(Game.make_move("items/shield","shield_"+direction,0,11))
for direction in directions:
    Player.pics.append(Game.make_move("items/boomerang","boomerang_"+direction,0,4))

#Item sprites
Item.pics.append(Game.make_move("items/stills","still",0,2))

#Octorok sprites
for direction in directions:
    Octorok.pics.append(Game.make_move("enemies/octorok","run_"+direction,0,1))    
for direction in directions:
    Octorok.pics.append(Game.make_move("enemies/octorok","attack_"+direction,0,1))

#Chuchu sprites
Chuchu.pics.append(Game.make_move("enemies/chuchu","chuchu_walk",0,33))
Chuchu.pics.append(Game.make_move("enemies/chuchu","chuchu_damage",0,18))

#Boss sprites
for direction in directions:
    Boss.pics.append(Game.make_move("enemies/boss/walk","walk_"+direction,0,1,(305,305)))       
for direction in directions:
    Boss.pics.append(Game.make_move("enemies/boss/damage","damage_"+direction,0,1,(305,305)))

#Enemy sprites
Enemy.pics.append(Game.make_move("enemies/damage","damage",0,3))
Enemy.pics.append(Game.make_move("enemies/enemy_death","enemy_death",0,8))

#Projectile sprites
Projectile.pics.append(Game.make_move("enemies/octorok","rok",0,2))
Projectile.pics.append(Game.make_move("items/boomerang","boomerang_spin",0,7))
Projectile.pics.append(Game.make_move("enemies/boss","boss_rock",0,3))

#Collectible sprites
Collectible.pics.append([transform.scale2x(image.load("imgs/collectibles/rps1.png"))])  #added as a list so 2D list stays organized, since some collectibles have several frames but others dont
Collectible.pics.append([transform.scale2x(image.load("imgs/collectibles/rps5.png"))])
Collectible.pics.append([transform.scale2x(image.load("imgs/collectibles/rps20.png"))])
Collectible.pics.append(Game.make_move("collectibles","big_rupee",0,7))
Collectible.pics.append([transform.scale2x(image.load("imgs/collectibles/heart.png"))])
Collectible.pics.append([transform.scale2x(image.load("imgs/collectibles/heart_piece.png"))])
Collectible.pics.append(Game.make_move("collectibles","heart_container",0,6))

#NPC sprites
NPC.pics.append(Game.make_move("NPC","smith",0,11))
NPC.pics.append([transform.scale2x(image.load("imgs/NPC/sign_down.png"))])
NPC.pics.append(Game.make_move("NPC","chest",0,1))
NPC.pics.append(Game.make_move("NPC","big_chest",0,3))

#Other miscellaneous pics
Game.pics.append([image.load("imgs/dialoguebox.png"),image.load("imgs/interact_prompt.png")])
Game.pics.append(Game.make_move("","platform",1,2,(1277,1600)))
Game.pics.append([transform.scale(image.load("imgs/screen/buttons.png"),(100,50))])
Game.pics.append(Game.make_move("screen","heart",0,4))
Game.pics.append(Game.make_move("inventory","heart",0,2))
Game.pics.append([transform.scale(image.load("imgs/screen/big_blue_rupee.png"),(25,40))])
Game.pics.append(Game.make_move("","gate",0,1,(1277,1600)))
Game.pics.append(Game.make_move("","switch",0,2))
Game.pics.append([transform.scale2x(image.load("imgs/warp_tile.png"))])
Game.pics.append([transform.scale2x(image.load("imgs/screen/triforce.png"))])

#Screen pics
Game.page_pics.append(image.load("imgs/screens/titlescreen.png"))
Game.page_pics.append(image.load("imgs/screens/story.png"))
Game.page_pics.append(image.load("imgs/screens/enter_name.png"))
Game.page_pics.append(image.load("imgs/screens/pause.png"))
Game.page_pics.append(image.load("imgs/screens/gameover.png"))
Game.page_pics.append(image.load("imgs/screens/credits.png"))

#---------------------------------------------------------------------------------
#Objects

# items
sword = Item(1,"click",0.35,SWORD,"sword")
shield = Item(0,"hold",0.2,SHIELD,"shield")
boomerang = Item(1,"click",0.25,BOOMERANG,"boomerang")

sword.unlocked = True #sword and shield start off unlocked
shield.unlocked = True

link = Player() 

# npcs
smith = (555,350,SMITH,0.25,None,Rect(497,319,105,76),"smith",["Ah "+link.name+", where have you been?","If you're heading into the forest, be careful. There have been more monsters around lately.","Take your boomerang, it should be just southeast of here.","I'm working now, so we'll talk more later."])

#chests are technically not NPC's, but you must interact with them, and they give items that have accompanying text similar to dialogue. Functionally similar enough to belong to same class
chest0 = (191,618,CHEST,1,BLUE_RP,Rect(179,630,15,8),"chest0",["-You got 5 rupees! You might be able to buy something someday!"])
chest1 = (184,175,CHEST,1,None,Rect(175,165,20,30),"chest0",["-You got...nothing? The chest was empty."])
chest2 = (184,175,CHEST,1,GREEN_RP,Rect(175,165,20,30),"chest0",["-You got 1 rupee! ...That's kinda sad."])
chest3 = (275,179,CHEST,1,RED_RP,Rect(260,160,30,40),"chest0",["-You got 20 rupees! 20! 20 whole rupees! Aw yeah!"])
chest4 = (1164,1065,CHEST,1,BLUE_RP,Rect(1150,1050,30,30),"chest0",["-You got 5 rupees! That's exciting, I guess?"])
chest5 = (1222,776,CHEST,1,BLUE_RP,Rect(1200,760,40,40),"chest0",["-You got 20 rupees! It's...not as cool the second time."])
big_chest0 = (406,295,BIG_CHEST,0.4,boomerang,Rect(383,346,52,15),"big_chest0",["-You got a boomerang! Now you can kill enemies while social distancing!"])

#A sign is essentially an NPC: the text on it is "dialogue", and you must interact with it
sign0 = (322,188,SIGN,0,None,Rect(294,178,54,40),"sign0",["~Use the mouse to lead the character around.","Click or hold the mouse buttons to use items.","Click the scroll wheel to have your character walk somewhere instead of following the mouse.","Roll the scroll wheel to roll.","Good luck on your adventure!"])       
sign1 = (648,396,SIGN,0,None,Rect(633,405,25,15),"sign1",["Bombs strictly prohibited"])
sign2 = (984,180,SIGN,0,None,Rect(965,186,30,21),"sign2",["Welcome to the South Hyrule Field!","CAUTION! Minish Woods ahead.","Visit Smith the Blacksmith for a strong,durable,shiny,new sword!"])
sign3 = (433,230,SIGN,0,None,Rect(401,215,44,54),"sign3",["No swimming! Seriously."])
sign4 = (133,888,SIGN,0,None,Rect(1096,860,76,20),"sign3",["Danger! Deepwood Shrine ahead.","Take the heart piece and enter well-prepared."])

#some collectibles start off on map. once collected, removed from map so they dont respawn
hpc0 = (403,320,PIECE)
hpc1 = (887,885,PIECE)
hpc2 = (432,130,PIECE)
bigrp = (2082,592,BIG_RP)       #get up to this platform by throwing bomb in hole and standing on it. Note: originally planned to have bombs but didn't end up implementing them. The giant rupee can just taunt players from afar instead as they struggle to figure out how to get up there.

# maps - enemies, npcs, collectibles, animations, and mask2 will automatically be set to None if nothing is passed in for them, because they are optional.
map1000 = Map("southfield","map1000","mask1000",2200,1500,T_SOUTHFIELD,[(Octorok,5),(Chuchu,5)],[sign0,sign1,sign2,chest0],[bigrp])            
map1010 = Map("fairy_fountain","map1010","mask1010",800,600,T_ENTER_NAME)
map1020 = Map("house1","map1020","mask1020",800,600,T_SOUTHFIELD,None,[chest1])
map1021 = Map("house2","map1021","mask1021",800,600,T_SOUTHFIELD,None,[chest2])
map1022 = Map("house3","map1022","mask1022",800,600,T_SOUTHFIELD,None,[smith,chest3])      
map1030 = Map("treehouse1","map1030","mask1030",800,600,T_SOUTHFIELD,[(Chuchu,2)],None,[hpc0])                     
map1040 = Map("treehouse2","map1030","mask1030",800,600,T_SOUTHFIELD,None,[big_chest0])                 
map1100 = Map("minishwood","map1100","mask1100",2200,1500,T_WOODS,[(Octorok,3),(Chuchu,2)],[sign3,sign4],[hpc1,hpc2])
map1200 = Map("shrine","map1200","mask1200_floor1",1277,1600,T_DUNGEON,[(Chuchu,2)],[chest4,chest5],None,None,"mask1200_floor2")

map1000.set_exit(Rect(593,354,27,20),map1010,403,450)       #southfield to fountain
map1010.set_exit(Rect(391,483,36,24),map1000,615,405)       #fountain to southfield
map1000.set_exit(Rect(1403,830,66,30),map1020,400,415)      #southfield to house
map1020.set_exit(Rect(385,451,42,25),map1000,1433,915)      #house to southfield
map1020.set_exit(Rect(301,112,36,21),map1021,314,190)       #house room 1 to 2
map1020.set_exit(Rect(640,304,33,26),map1022,212,316)       #house room 1 to 3
map1021.set_exit(Rect(302,109,27,27),map1020,320,170)       #house room 2 to 1
map1022.set_exit(Rect(125,304,17,42),map1020,600,313)       #house room 3 to 1
map1000.set_exit(Rect(176,1191,33,15),map1030,403,441)      #southfield to treehouse1
map1030.set_exit(Rect(382,477,45,48),map1000,213,1250)      #treehouse1 to southfield
map1000.set_exit(Rect(2007,1190,42,12),map1040,403,441)     #southfield to treehouse2
map1040.set_exit(Rect(382,477,45,48),map1000,2028,1238)     #treehouse2 to southfield
map1000.set_exit(Rect(2165,213,20,93),map1100,144,333)      #southfield to woods
map1100.set_exit(Rect(18,324,30,45),map1000,2111,252)       #woods to southfield
map1100.set_exit(Rect(954,871,66,15),map1200,362,1378)      #woods to shrine
map1200.set_exit(Rect(310,1422,102,20),map1100,960,940)     #shrine to woods

game = Game()

#dictionary - used for load_game(), so varibles read from the save file as strings can be converted to variables. Includes some magic numbers, some classes
Game.dict = { 
    "Player": Player,                   #classes
    "Octorok": Octorok,
    "Boss": Boss,
    "Enemy": Enemy,
    "Projectile": Projectile,
    "Collectible": Collectible,
    "NPC": NPC,
    "Game": Game,
    "sword": sword,                     #items
    "shield": shield,
    "boomerang": boomerang,
    "GREEN_RP": GREEN_RP,               #collectible pics magic numbers
    "BLUE_RP": BLUE_RP,
    "RED_RP": RED_RP,
    "BIG_RP": BIG_RP,
    "HEART": HEART,
    "PIECE": PIECE,
    "CONTAINER": CONTAINER,
    "SMITH": SMITH,                     #npc pics magic numbers
    "SIGN": SIGN,
    "CHEST": CHEST,
    "BIG_CHEST": BIG_CHEST,
    "GREEN": GREEN,                     #switch list magic numbers
    "BLUE": BLUE,
    "RED": RED
}                                       

#---------------------------------------------------------------------------------
#Music

game.tracks.append("music/title.mp3")       #path for each track is appended to list so they can be loaded in the method
game.tracks.append("music/enter_name.mp3")
game.tracks.append("music/pause.mp3")
game.tracks.append("music/story.mp3")
game.tracks.append("music/southfield.mp3")
game.tracks.append("music/woods.mp3")
game.tracks.append("music/dungeon.mp3")
game.tracks.append("music/end.mp3")
game.tracks.append("music/gameover.mp3")
game.tracks.append("music/sound_effect_secret.mp3")
game.tracks.append("music/sound_effect_treasure.mp3")
game.tracks.append("music/sound_effect_gameover.mp3")

#---------------------------------------------------------------------------------

while game.page != "Exit":                  #-code from menu example
    if game.page == "Title":
        game.page = game.title_screen()

    elif game.page == "Story":
        game.page = game.story()

    elif game.page == "Name Entry":
        game.page = game.enter_name()

    elif game.page == "Pause":
        game.page = game.pause_game()

    elif game.page == "Gameover":
        game.page = game.gameover_screen()

    elif game.page == "Play":
        game.page = game.play_game()

    elif game.page == "Credits":
        game.page = game.roll_credits()

    

quit()

    
