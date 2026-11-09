


import ctypes, time, sys, pydirectinput
from random import randrange
import pyautogui as pg
from Tower import Tower
from Hero import Hero
from Map import Map
from KeyboardInput import PressKey, ReleaseKey
from ImageGrabTest import locate

TOP_LEFT = ( 701, 283, "Top left" )
TOP_MIDDLE = ( 1124, 283, "Top middle" )
TOP_RIGHT = ( 1548, 283, "Top right" )

BOTTOM_LEFT = ( 701, 597, "Bottom left" )
BOTTOM_MIDDLE = ( 1124, 597, "Bottom middle" )
BOTTOM_RIGHT = ( 1548, 597, "Bottom right" )

HEROES = [Hero('Quincy', [111,970], 0),
          Hero('Gwendolin', [325,970], 1),
          Hero('Striker Jones', [538,970], 2),
          Hero('Obyn', [746,970], 3),
          Hero('Psi', [971,970], 4),
          Hero('Captain Churchill', [1177,970], 5),
          Hero('Benjamin', [1385, 970], 6),
          Hero('Ezili', [1600, 970], 7),
          Hero('Pat Fusty', [1815, 970], 8),
          Hero('Adora', [1094, 970], 9),
          Hero('Admiral Brickell', [1304, 970], 10),
          Hero('Etienne', [1519, 970], 11),
          Hero('Sauda', [1733, 970], 12)]
        
MAPS = [Map('Sanctuary', 3, 0, TOP_LEFT, 309, 
            [ Tower('Hero', [834,177], [0,0,0], 3),
              Tower('Boomerang Monkey', [838,287], [4,0,2], 0),
              Tower('Sniper Monkey', [754,926], [0,2,4], 0),
              Tower('Alchemist', [753,1007], [4,2,0], 0) ] ),
        Map('Ravine', 3, 0, TOP_MIDDLE, 292, 
            [ Tower('Monkey Village', [273,928], [2,2,0], 0),
              Tower('Monkey Ace', [258,826], [2,0,3], 0),
              Tower('Monkey Ace', [413,897], [2,0,3], 0),
              Tower('Alchemist', [393,805], [4,0,1], 0) ] ),
        Map('Flooded Valley',3,0,TOP_RIGHT, 300, []),
        Map('Infernal',3,0,BOTTOM_LEFT, 300, []),
        Map('Bloody Puddles',3,0,BOTTOM_MIDDLE, 300, []),
        Map('Workshop',3,0,BOTTOM_RIGHT, 300, []),
        Map('Quad',3,1,TOP_LEFT, 300, []),
        Map('Dark Castle',3,1,TOP_MIDDLE, 300, []),
        Map('Muddy Puddles',3,1,TOP_RIGHT, 300, []),
        Map('Ouch',3,1,BOTTOM_LEFT, 300, [])]

def getMap(mapName):
    for m in MAPS:
        if m.name == mapName:
            return m

def getMapFromLocation(pageNum, position):
    for m in MAPS:
        if m.subpage == pageNum:
            if m.position[2] == position[2]:
                return m

def getHero(heroName):
    for h in HEROES:
        if h.name == heroName:
            return h


getMap('Sanctuary').hero = getHero('Psi')
getMap('Ravine').hero = getHero('Quincy')

getMap('Flooded Valley').delayTime = 300
getMap('Flooded Valley').towers = [ Tower('Hero', [717,404], [0,0,0], 0),
                               Tower('Monkey Sub', [1002,214], [4,0,0], 0),
                               Tower('Monkey Sub', [1011,834], [4,0,0], 0),
                               Tower('Monkey Buccaneer', [1033,762], [3,2,0], 0),
                               Tower('Monkey Buccaneer', [1088,263], [3,2,0], 0),
                               Tower('Monkey Sub', [1111,502], [2,0,3], 0) ]
getMap('Flooded Valley').hero = getHero('Etienne')


getMap('Infernal').delayTime = 325
getMap('Infernal').towers = [ Tower('Ninja Monkey', [838,698], [4,0,2], 0),
                               Tower('Ninja Monkey', [838,386], [4,0,2], 0),
                               Tower('Alchemist', [838,322], [4,0,0], 0),
                               Tower('Alchemist', [838,755], [4,0,0], 0) ]
getMap('Infernal').hero = getHero('Quincy')


getMap('Bloody Puddles').delayTime = 292
getMap('Bloody Puddles').towers = [ Tower('Monkey Village', [979,459], [0,0,2], 0),
                               Tower('Monkey Ace', [1000,556], [2,0,3], 0),
                               Tower('Alchemist', [1099,488], [4,0,0], 0),
                               Tower('Monkey Ace', [1047,359], [2,0,3], 0),
                               Tower('Monkey Ace', [965,273], [2,0,3], 0),
                               Tower('sell', [979,459], [0,0,0], 0),
                               Tower('Monkey Village', [979,459], [2,2,0], 0) ]
getMap('Bloody Puddles').hero = getHero('Quincy')


getMap('Workshop').delayTime = 335
getMap('Workshop').towers = [ Tower('Monkey Village', [897,427], [0,0,2], 0),
                               Tower('Monkey Village', [1001,377], [0,0,2], 0),
                               Tower('Super Monkey', [1003,482], [2,0,3], 0),
                               Tower('sell', [1001,377], [0,0,0], 0),
                               Tower('Hero', [1020,397], [0,0,0], 0),
                               Tower('sell', [897,427], [0,0,0], 0),
                               Tower('Spike Factory', [1578,703], [3,2,0], 0) ]
getMap('Workshop').hero = getHero('Quincy')


getMap('Quad').delayTime = 305
getMap('Quad').towers = [ Tower('Monkey Village', [1175,797], [0,0,2], 0),
                               Tower('Monkey Village', [1294,792], [0,0,2], 0),
                               Tower('Monkey Ace', [1112,892], [2,0,3], 0),
                               Tower('Monkey Ace', [1265,890], [2,0,3], 0),
                               Tower('Monkey Ace', [1193,977], [2,0,3], 0),
                               Tower('Alchemist', [1307,963], [4,0,1], 0),
                               Tower('sell', [1175,797], [0,0,0], 0),
                               Tower('Monkey Village', [1175,797], [0,2,0], 0),
                               Tower('sell', [1294,792], [0,0,0], 0),
                               Tower('upgrade', [1175,797], [2,0,0], 0) ]
getMap('Quad').hero = getHero('Quincy')


getMap('Dark Castle').delayTime = 310
getMap('Dark Castle').towers = [ Tower('Hero', [532,480], [0,0,0], 0),
                               Tower('Ninja Monkey', [489,734], [0,0,0], 0),
                               Tower('Ninja Monkey', [466,343], [0,0,0], 0),
                               Tower('Monkey Sub', [1084,433], [2,0,4], 0),
                               Tower('Monkey Sub', [1084,367], [2,0,4], 0),
                               Tower('Alchemist', [1008,447], [4,0,1], 0) ]
getMap('Dark Castle').hero = getHero('Captain Churchill')


getMap('Muddy Puddles').delayTime = 286
getMap('Muddy Puddles').towers = [ Tower('Hero', [783,208], [0,0,0], 0),
                               Tower('Ninja Monkey', [416,192], [0,0,0], 0),
                               Tower('Ninja Monkey', [1104,189], [0,0,0], 0),
                               Tower('Monkey Sub', [729,596], [2,0,4], 0),
                               Tower('Monkey Sub', [641,647], [2,0,4], 0),
                               Tower('Alchemist', [615,504], [4,0,2], 0) ]
getMap('Muddy Puddles').hero = getHero('Captain Churchill')


getMap('Ouch').delayTime = 306
getMap('Ouch').towers = [ Tower('Hero', [694,660], [0,0,0], 0),
                               Tower('Monkey Buccaneer', [847,562], [4,0,2], 0),
                               Tower('Alchemist', [665,464], [4,0,2], 0),
                               Tower('Wizard Monkey', [1006,430], [0,2,2], 0),
                               Tower('Ninja Monkey', [1021,765], [2,0,2], 0) ]
getMap('Ouch').hero = getHero('Captain Churchill')

def keyPush(c):
    if(c == 'esc'):
        pydirectinput.press('esc')
        return
    
    code = 0x00
    if(c == 'u'):
        code = 0x16
    elif(c == 'q'):
        code = 0x10
    elif(c == 'w'):
        code = 0x11
    elif(c == 'f'):
        code = 0x21
    elif(c == 'z'):
        code = 0x2C
    elif(c == ','):
        code = 0x33
    elif(c == '.'):
        code = 0x34
    elif(c == '/'):
        code = 0x35
    elif(c == 'tab'):
        code = 0x0F
    elif(c == ' '):
        code = 0x39
    elif(c == 'a'):
        code = 0x1E
    elif(c == 's'):
        code = 0x1F
    elif(c == 'd'):
        code = 0x20
    elif(c == 'x'):
        code = 0x2D
    elif(c == 'c'):
        code = 0x2E
    elif(c == 'v'):
        code = 0x2F
    elif(c == 'j'):
        code = 0x24
    elif(c == 'k'):
        code = 0x25
    elif(c == 'bksp'):
        code = 0x0E
    elif(c == 'esc'):
        pass
    else:
        code = 0x10
    
    PressKey(code)
    ReleaseKey(code)

def waitClick(t, x, y):
    time.sleep(t)
    pg.click(x, y)

def acceptFreeMonkeys():
    waitClick(2, 957, 674) # Continue
    for i in range(2):
        waitClick(0.4, 810, 532)
    time.sleep(1)
    for i in range(2):
        waitClick(0.4, 1106, 532)
    time.sleep(1)
    for i in range(2):
        waitClick(0.4, 661, 532)
    time.sleep(1)
    for i in range(2):
        waitClick(0.4, 960, 532)
    time.sleep(1)
    for i in range(2):
        waitClick(0.4, 1261, 532)
    waitClick(0.4, 958, 997) #cont
    time.sleep(0.2)
    keyPush('esc')
    waitClick(0.1, 796, 727)

def selectDeflation():
    LOADING_TIME = 6
    
    waitClick(0.5, 618, 417) #easy
    waitClick(0.5, 1293, 475) #deflation
    waitClick(0.3, 1137, 729) #Overwrite Save
    waitClick(LOADING_TIME, 969, 758) #okay
    time.sleep(0.8)

def placeTowerAdv(t):
    thisHotkey = t.getHotkey()
    x,y = t.getPosition()
    a,b,c = t.getUpgrades()

    # Tower sell
    if(thisHotkey == 'bksp'):
        waitClick(0.2, x, y)
        keyPush(thisHotkey)
        return

    # Place tower
    if(thisHotkey != '0'):
        keyPush(thisHotkey)
        pg.moveTo(x, y, duration = 0.1)
        pg.click(x,y)

    # Reselect tower
    if( t.upgrades == [0,0,0] and t.targeting == 0 ):
        return
    else:
        pg.click(x, y)

    # Upgrade tower
    for n in range(a):
        time.sleep(0.08)
        keyPush(",")
    for n in range(b):
        time.sleep(0.08)
        keyPush(".")
    for n in range(c):
        time.sleep(0.08)
        keyPush("/")

    # Set targeting priority
    for n in range(t.targeting):
        time.sleep(0.08)
        keyPush("tab")

    # De-select tower
    time.sleep(0.1)
    keyPush("esc")

def beatThisMap(m):
    selectMap(m)
    selectHero(m.hero)
    selectDeflation()

    pg.moveTo(1519, 309)
    for t in m.towers:
        placeTowerAdv(t)
    delayFxn(m.delayTime)
        

def delayFxn(totalDelay):
    # Start round
    for x in range(2):
        time.sleep(0.1)
        keyPush(' ')

    pg.moveTo(960, 540)

    # Wait for game to end
    for t in range(totalDelay):
        time.sleep(1)
        #print(str(t)+' ', end = '')

    #Return to main menu
    waitClick(0.5, 961, 898) #okay
    waitClick(0.8, 690, 836) #home

def selectHero(h): 
    waitClick(0.5, 104, 990) # ChangeHero
    time.sleep(0.5)
    if h.position > 8:
        time.sleep(0.5)
        pg.moveTo(1712, 960)
        pg.dragTo(557, 960, 0.5, button='left')


    waitClick(0.5, h.buttonCoords[0], h.buttonCoords[1])
    
    waitClick(0.2, 643, 663) # Select
    waitClick(0.2, 80, 50) # BackArrow

def selectMap(m):
    difficulty = 0
    pageNum = 0
    location = TOP_LEFT

    difficulty = m.difficulty
    pageNum = m.subpage
    location = m.position

    # Scroll to page
    #if(difficulty == 3):
    #    for i in range(pageNum + 1):
    #        waitClick(0.5, 1333, 966) #Expert
    #else:
    #    print("ERROR: diffulty != 3")
    #    sys.exit()

    # Click on map
    X_LEFT_SHIFT = 150
    x = location[0]
    y = location[1]
    waitClick(0.8, x - X_LEFT_SHIFT, y)


### Start of Main ###

#Click into top right corner of screen
            # to refocus window on BTD6
pg.click(1900,0)

iteration = 0
while(iteration >= 0):
    waitClick(2, 833, 936) #play
    matchFound = False
    pageNum = -1

    while (not matchFound) and pageNum <= 2:
        waitClick(0.5, 1333, 966) #Expert
        pageNum += 1
        time.sleep(0.5)
        matchLocation = locate()
        matchFound = (matchLocation != -1)

    m = getMapFromLocation(pageNum, matchLocation)
    
    if m:
        beatThisMap(m)
    else:
        print('no match')
        beatThisMap(getMap('Muddy Puddles'))

    acceptFreeMonkeys()

    iteration += 1
    
