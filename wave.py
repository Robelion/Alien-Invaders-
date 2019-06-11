"""
Subcontroller module for Alien Invaders

This module contains the subcontroller to manage a single level or wave in the Alien
Invaders game.  Instances of Wave represent a single wave.  Whenever you move to a
new level, you are expected to make a new instance of the class.

The subcontroller Wave manages the ship, the aliens and any laser bolts on screen.
These are model objects.  Their classes are defined in models.py.

Most of your work on this assignment will be in either this module or models.py.
Whether a helper method belongs in this module or models.py is often a complicated
issue.  If you do not know, ask on Piazza and we will answer.

# Robel Ayalew(rsa83)
# 12/4/18
"""
from game2d import *
from consts import *
from models import *
import random

# PRIMARY RULE: Wave can only access attributes in models.py via getters/setters
# Wave is NOT allowed to access anything in app.py (Subcontrollers are not permitted
# to access anything in their parent. To see why, take CS 3152)


class Wave(object):
    """
    This class controls a single level or wave of Alien Invaders.

    This subcontroller has a reference to the ship, aliens, and any laser bolts on screen.
    It animates the laser bolts, removing any aliens as necessary. It also marches the
    aliens back and forth across the screen until they are all destroyed or they reach
    the defense line (at which point the player loses). When the wave is complete, you
    should create a NEW instance of Wave (in Invaders) if you want to make a new wave of
    aliens.

    If you want to pause the game, tell this controller to draw, but do not update.  See
    subcontrollers.py from Lecture 24 for an example.  This class will be similar to
    than one in how it interacts with the main class Invaders.

    #UPDATE ME LATER
    INSTANCE ATTRIBUTES:
        _ship:   the player ship to control [Ship]
        _aliens: the 2d list of aliens in the wave [rectangular 2d list of Alien or None]
        _bolts:  the laser bolts currently on screen [list of Bolt, possibly empty]
        _dline:  the defensive line being protected [GPath]
        _lives:  the number of lives left  [int >= 0]
        _time:   The amount of time since the last Alien "step" [number >= 0]

    As you can see, all of these attributes are hidden.  You may find that you want to
    access an attribute in class Invaders. It is okay if you do, but you MAY NOT ACCESS
    THE ATTRIBUTES DIRECTLY. You must use a getter and/or setter for any attribute that
    you need to access in Invaders.  Only add the getters and setters that you need for
    Invaders. You can keep everything else hidden.

    You may change any of the attributes above as you see fit. For example, may want to
    keep track of the score.  You also might want some label objects to display the score
    and number of lives. If you make changes, please list the changes with the invariants.

    LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
        _aliendownwards:    A bool type to specify when the aliens should move down [bool]
        _xdis:              The horizontal number of steps each alien is going to move [int >= 0]
        _ydis:              The vertical number of steps each alien is going to move [int >= 0]
        _speedofalien:      The speed of the aliens [0 < float <= 1]
        _numofsteps:        The number of steps taken since the last alien step [number >= 0]
        _shipboltalive:     Indicate if there is a ship's bolt on the screen [bool]
        _lastkey:           The number keys pressed in the last frames [int >= 0]
        _alienbolts:        The laser bolts of the alien currently on screen [list of Bolt, possibly empty]
        _alienboltalive:    Indicate if there is an alien's bolt on the screen [bool]
        _lost:              Indicate if the player lost the game [bool]
        _won:               Indicate if the player won the game[bool]
    """

    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    def getLost(self):
        """
        Returns _lost
        """
        return self._lost


    def getWon(self):
        """
        Returns _won
        """
        return self._won


    def getLives(self):
        """
        Return _lives
        """
        return self._lives


    def allnone(self):
        """
        Returns true of all the aliens in self._aliens have been set to None
        """
        for row in range(ALIEN_ROWS):
            for col in range(ALIENS_IN_ROW):
                if self._aliens[col][row] != None:
                    return False
        return True


    # INITIALIZER (standard form) TO CREATE SHIP AND ALIENS
    def __init__(self):
        self.waveofaliens()
        self._lives = 3
        self._dline = GPath(points=[0,DEFENSE_LINE,GAME_WIDTH,DEFENSE_LINE],linewidth=5, linecolor='black')
        self._life = GLabel(text="Lives: " + str(self._lives),
        halign='center', valign='top', x=(GAME_WIDTH-110), y=(GAME_HEIGHT-40),
        fillcolor='black', linecolor='white', font_size=WelcomeFontSize, font_name='RetroGame.ttf')
        self._ship = Ship()
        self._time = 0
        self._bolts = []
        self._alienbolts = []
        self._aliendownwards = False
        self._xdis = ALIEN_H_WALK
        self._ydis = ALIEN_V_WALK
        self._speedofalien = ALIEN_SPEED
        self._numofsteps = 0
        self._shipboltalive = False
        self._lastkey = 1
        self._alienboltalive = False
        self._lost = False
        self._won = False


    def waveofaliens(self):
        """
        This method fills _aliens with aliens

        _aliens will have ALIEN_ROWS rows and ALIENS_IN_ROW colums
        """
        self._aliens = []
        x = 0
        y = GAME_HEIGHT - ALIEN_CEILING
        for colums in range(ALIENS_IN_ROW):
            x = x + ALIEN_H_SEP + ALIEN_WIDTH
            newlist = []
            y = GAME_HEIGHT - ALIEN_CEILING - (ALIEN_HEIGHT/2)
            for rows in range(ALIEN_ROWS):
                y = y - (ALIEN_V_SEP + ALIEN_HEIGHT)
                if rows == 0:
                    y = GAME_HEIGHT - ALIEN_CEILING - (ALIEN_HEIGHT/2)
                ans = rows%HalfofColums
                source = ''
                if ans == 0 or ans == 5:
                    source = ALIEN_IMAGES[2]
                elif ans == 1 or ans == 2:
                    source = ALIEN_IMAGES[1]
                elif ans == 3 or ans ==4:
                    source = ALIEN_IMAGES[0]
                newlist.append(Alien(x = x , y = y, source=source))
            self._aliens.append(newlist)


    # UPDATE METHOD TO MOVE THE SHIP, ALIENS, AND LASER BOLTS
    def _update(self, input, dt):
        if self.alienscross() != True and self._ship != None:
            self.aliendead()
            self.shipdead()
            self.firealienbolt()
            if self._ship != None:
                self._ship.moveship(input)
            self.fireshipbolt(input)
            self._time += dt
            if self._time > self._speedofalien:
                self._numofsteps += 1
                self.movealiens()
            if self.allnone() == True:
                self._won = True
            if self._lives == 0 or self.alienscross() == True:
                self._lost = True
            else:
                self._lives = self._lives


    def xcooralien(self):
        """
        Creates a list of all the x coordinates of the aliens in self._aliens
        """
        listofx = []
        for rows in range(ALIEN_ROWS):
            for colums in range(ALIENS_IN_ROW):
                if self._aliens[colums][rows] != None:
                    listofx.append(self._aliens[colums][rows].getXPos())
        return listofx


    def ycooralien(self):
        """
        Creates a list of all the y coordinates of the aliens in self._aliens
        """
        listofy = []
        for rows in range(ALIEN_ROWS):
            for colums in range(ALIENS_IN_ROW):
                if self._aliens[colums][rows] != None:
                    listofy.append(self._aliens[colums][rows].getYPos())
        return listofy


    def movealiens(self):
        """
        Moves aliens across the screen
        """
        self.boundcheck(self.xcooralien())
        for rows in range(ALIEN_ROWS):
            for colums in range(ALIENS_IN_ROW):
                if self._aliens[colums][rows] != None:
                        self._aliens[colums][rows].x += self._xdis
                        self._aliens[colums][rows].y += self._ydis
        self._time = 0


    def boundcheck(self, listofx):
        """
        This helpermethod checks the boundaries of the screen for alien movement

        Parameter listofx - the list of alien x-values
        Precondition - listofx is a non-empty list of floats(alien x coordinates)
        """
        if listofx != []:
            rightmostalien = max(listofx)
            leftmostalien = min(listofx)
            if self._aliendownwards == True:
                if rightmostalien > rightborder:
                    self._xdis = -ALIEN_H_WALK
                elif leftmostalien < leftborder:
                    self._xdis = ALIEN_H_WALK
                self._ydis = 0
                self._aliendownwards = False
            elif rightmostalien > rightborder:
                self._xdis = 0
                self._ydis = -ALIEN_V_WALK
                self._aliendownwards = True
            elif leftmostalien < leftborder:
                self._xdis = 0
                self._ydis = -ALIEN_V_WALK
                self._aliendownwards = True
            else:
                self._xdis = self._xdis
                self._ydis = 0


    def alienscross(self):
        """
        This method checks if the aliens have reached the DEFENSE_LINE
        """
        if self.ycooralien() != [] and min(self.ycooralien()) < DEFENSE_LINE:
            return True
        else:
            return False


    def fireshipbolt(self, input):
        """
        Creates a bolt above the ship when the 'up-arrow' is pressed and appends the bolt to _bolts

        Parameter input - the keyboard input
        Precondition - input is a GInput
        """
        numofkey = input.key_count
        if numofkey > 0 and self._lastkey == 1 and input.is_key_down('spacebar') and self._shipboltalive == False:
            Sound('blast1.wav').play()
            x = self._ship.getXPos()
            y = self._ship.getYPos() + BOLT_HEIGHT/2 + SHIP_HEIGHT/2
            shipbolt = Bolt(x, y)
            self._bolts.append(shipbolt)
            self._shipboltalive = True
        self._lastkey = numofkey
        for bolt in self._bolts:
            if bolt.y <= GAME_HEIGHT:
                bolt.y += BOLT_SPEED
            else:
                del self._bolts[self._bolts.index(bolt)]
                self._shipboltalive = False


    def firealienbolt(self):
        """
        Creates a bolt under a random alien and appends the bolt to _alienbolts
        """
        if self._numofsteps == random.randint(1, BOLT_RATE):
            if self._alienboltalive == False:
                randcolum = random.randint(0, ALIENS_IN_ROW-1)
                randrow = ALIEN_ROWS-1
                while self._aliens[randcolum][randrow] == None and randrow > 0:
                    randrow -= 1
                if self._aliens[randcolum][randrow] != None:
                    x = self._aliens[randcolum][randrow].getXPos()
                    y = self._aliens[randcolum][randrow].getYPos() - (BOLT_HEIGHT/2 + ALIEN_HEIGHT/2)
                    alienbolt = Bolt(x, y)
                    Sound('pew2.wav').play()
                    self._alienbolts.append(alienbolt)
                    self._alienboltalive = True
            self._numofsteps = 0

        for bolt in self._alienbolts:
            if bolt.y >= 0:
                bolt.y -= BOLT_SPEED
            else:
                del self._alienbolts[self._alienbolts.index(bolt)]
                self._alienboltalive = False


    # DRAW METHOD TO DRAW THE SHIP, ALIENS, DEFENSIVE LINE AND BOLTS
    def draws(self, view):
        """
        Draws the ship, aliens, and Defensive line

        Parameter view - the view window
        Precondition - view is a GView
        """
        for row in self._aliens:
            for alien in row:
                if alien != None:
                    alien.draw(view)
        if self._ship != None:
            self._ship.draw(view)
        self._dline.draw(view)
        for shipbolts in self._bolts:
            shipbolts.draw(view)
        for alienbolts in self._alienbolts:
            alienbolts.draw(view)
        self._life.text = ('Lives: ' + (str(self._lives)))
        self._life.draw(view)


    # HELPER METHODS FOR COLLISION DETECTION
    def aliendead(self):
        """
        Removes alien that is shot by a ship bolt
        """
        for row in range(len(self._aliens)):
            for col in range(len(self._aliens[row])):
                for bolt in self._bolts:
                    if self._aliens[row][col] != None and self._aliens[row][col].aliencollides(bolt) == True:
                        Sound('pop1.wav').play()
                        self._aliens[row][col] = None
                        del self._bolts[self._bolts.index(bolt)]
                        self._shipboltalive = False


    def shipdead(self):
        """
        Removes ship when shot by a alien bolt
        """
        for bolt in self._alienbolts:
            if self._ship != None and self._ship.shipcollides(bolt) == True:
                if self._lives > 0:
                    self._lives -= 1
                else:
                    self._ship = None
                del self._alienbolts[self._alienbolts.index(bolt)]
                self._alienboltalive = False
