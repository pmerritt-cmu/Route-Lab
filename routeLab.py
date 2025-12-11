'''
Welcome to Route Lab, where users create football plays
and use their own plays live in game.

Features:
    4 Formation Options
    12 Route Options (mirrored on each side)
    Play against a live man-defense
    Throw football to target on mouse press
    A live defense
    WR and Defense adjust to ball after reaction time in air
    Indicates Complete/Incomplete (factoring in defensive positions)
    Tracks yards, completions
    Import/Export play data in json format

I focused on making the app user-friendly with a clean UI.
Just follow the instructions on screen to run the app.

Note this was originally a group project, so if there's:
#James wrote this function before a function, I did not write it.

Enjoy! 
'''
from cmu_graphics import *
import random
import math
import copy
import json

#---------------------#
#------ Classes ------#
#---------------------#

class Player:
    def __init__(self, cx, cy, dx=0, dy=0):
        self.cx = cx
        self.cy = cy
        self.dx = dx
        self.dy = dy
   
    def __repr__(self):
        return f"cx = {self.cx}, cy = {self.cy}"
       
    def __eq__(self, other):
        return (isinstance(other, Player) and
                self.cx==other.cx and
                self.cy==other.cy)
               
    def __hash__(self):
        return hash(str(self))

class WideReceiver(Player):
    def __init__(self,  cx, cy, dx=0, dy=0, route=None):
        super().__init__(cx, cy, dx, dy)
        self.route = route

class RunningBack(Player):
    def __init__(self,  cx, cy, dx=0, dy=0, route=None):
        super().__init__(cx, cy, dx, dy)
        self.route = route

class TightEnd(Player):
    def __init__(self,  cx, cy, dx=0, dy=0, route=None):
        super().__init__(cx, cy, dx, dy)
        self.route = route

class Quarterback(Player):
    def __init__(self,  cx, cy, dx=0, dy=0):
        super().__init__(cx, cy, dx, dy)

class Lineman(Player):
    def __init__(self,  cx, cy, dx=0, dy=0):
        super().__init__(cx, cy, dx, dy)

class CornerBack(Player):
    def __init__(self,  cx, cy, dx=0, dy=0, man=None):
        super().__init__(cx, cy, dx, dy)
        self.man = man

class LineBacker(Player):
    def __init__(self,  cx, cy, dx=0, dy=0, man=None):
        super().__init__(cx, cy, dx, dy)
        self.man = man

class DefensiveTackle(Player):
    def __init__(self,  cx, cy, dx=0, dy=0):
        super().__init__(cx, cy, dx, dy)

class DefensiveEnd(Player):
    def __init__(self,  cx, cy, dx=0, dy=0):
        super().__init__( cx, cy, dx, dy)

class Safety(Player):
    def __init__(self,  cx, cy, dx=0, dy=0, man=None):
        super().__init__( cx, cy, dx, dy)
        self.man = man

class Route:
    def __init__(self, step1, step2):
        self.x1 = step1[0]
        self.y1 = step1[1] 
        self.x2 = step2[0]
        self.y2 = step2[1]
    
    def __repr__(self):
        return f"({self.x1}, {self.y1}), ({self.x2}, {self.y2})"

class Football:
    armOffset = 7
    brownColor = rgb(135, 75, 1)
    def __init__(self, app):
        self.cx = app.oFormation['QB'].cx + Football.armOffset
        self.cy = app.oFormation['QB'].cy
        self.dx = 0
        self.dy = 0
        self.targetCX = None
        self.targetCY = None
        self.sizeW = 10
        self.sizeH = 20
        self.angle = 0

    def draw(self):
        drawOval(self.cx, self.cy, self.sizeW, self.sizeH, 
                fill=Football.brownColor, rotateAngle = self.angle)
        angle1 = (270+self.angle) % 360
        angle2 = angle1 + 180
        r = self.sizeH//2
        endX1 = self.cx + r*math.cos(math.radians(angle1))
        endY1 = self.cy + r*math.sin(math.radians(angle1))
        endX2 = self.cx + r*math.cos(math.radians(angle2))
        endY2 = self.cy + r*math.sin(math.radians(angle2))
        drawLine(endX1, endY1, endX2, endY2, fill='white', lineWidth = 0.6)

        laceR = 2
        laceCX1 = self.cx + (r//2)*math.cos(math.radians(angle1))
        laceCY1 = self.cy + (r//2)*math.sin(math.radians(angle1))
        laceX1 = laceCX1 + laceR*math.cos(math.radians(angle1+90))
        laceY1 = laceCY1 + laceR*math.sin(math.radians(angle1+90))
        laceX2 = laceCX1 + laceR*math.cos(math.radians(angle1-90))
        laceY2 = laceCY1 + laceR*math.sin(math.radians(angle1-90))
        drawLine(laceX1, laceY1, laceX2, laceY2, fill='white', lineWidth = 0.5)

        laceCX2 = self.cx + (r//2)*math.cos(math.radians(angle2))
        laceCY2 = self.cy + (r//2)*math.sin(math.radians(angle2))
        laceX3 = laceCX2 + laceR*math.cos(math.radians(angle2+90))
        laceY3 = laceCY2 + laceR*math.sin(math.radians(angle2+90))
        laceX4 = laceCX2 + laceR*math.cos(math.radians(angle2-90))
        laceY4 = laceCY2 + laceR*math.sin(math.radians(angle2-90))
        drawLine(laceX3, laceY3, laceX4, laceY4, fill='white', lineWidth = 0.5)

        laceX5 = self.cx + laceR*math.cos(math.radians(angle2+90))
        laceY5 = self.cy + laceR*math.sin(math.radians(angle2+90))
        laceX6 = self.cx + laceR*math.cos(math.radians(angle2-90))
        laceY6 = self.cy + laceR*math.sin(math.radians(angle2-90))
        drawLine(laceX5, laceY5, laceX6, laceY6, fill='white', lineWidth = 0.5)

    def setAngle(self):
        if self.targetCX==None: return
        _, angle = getRadiusAndAngleToEndpoint(self.cx, self.cy, 
                    self.targetCX, self.targetCY)
        self.angle = angle

    def setTarget(self, mx, my):
        self.targetCX = mx
        self.targetCY = my

class Button:
    customGreen1 = rgb(19, 130, 60)
    def __init__(self, cx, cy, w, h, text):
        self.cx = cx
        self.cy = cy
        self.w = w
        self.h = h
        self.text = text
        self.bolded = False
    
    def isClicked(self, mx, my):
        return ((self.cx-self.w//2)<=mx<=(self.cx+self.w//2) and 
                (self.cy-self.h//2)<=my<=(self.cy+self.h/2))

    def checkBold(self, mx, my):
        if self.isClicked(mx, my):
            self.bolded = True
        else:
            self.bolded = False

    def draw(self):
        drawRect(self.cx, self.cy, self.w+7, self.h+4.4,
                fill='black', align='center')
        drawRect(self.cx, self.cy, self.w, self.h,
                fill=Button.customGreen1, align='center')
        drawLabel(self.text, self.cx, self.cy, size=18, 
                    bold = self.bolded, align='center')

class FormationButton(Button):
    def __init__(self, cx, cy, w, h, text, formation):
        super().__init__(cx, cy, w, h, text)
        self.formation = formation

class RouteButton(Button):
    def __init__(self, cx, cy, w, h, text, routes):
        super().__init__(cx, cy, w, h, text)
        self.leftRoute = routes[0]
        self.rightRoute = routes[1]

class StartButton(Button):
    customComplimentRed = rgb(215, 80, 75)
    def __init__(self, cx, cy, w, h, text):
        super().__init__(cx, cy, w, h, text)

    def draw(self):
        drawRect(self.cx, self.cy, self.w+7, self.h+4.4,
                fill='black', align='center')
        drawRect(self.cx, self.cy, self.w, self.h,
                fill=StartButton.customComplimentRed, align='center')
        drawLabel(self.text, self.cx, self.cy, size=48, 
                    bold = self.bolded, align='center')

class exportImportButton(Button):
    def __init__(self, cx, cy, w, h, text, data):
        super().__init__(cx, cy, w, h, text)
        self.data = data

#----------------------------#
#------ Initialize App ------#
#----------------------------#

def onAppStart(app):
    app.isField = False
    app.isMainMenu = True
    app.isDefensiveMenu = False
    app.isOffensiveMenu = False
    app.isPlayActive = False
    app.isMainMenuLabelHovering = False
    app.isPaused = True
    app.isWRMenu = True
    app.isComplete = False

    app.width = 1000
    app.height = 750
    app.yardStep = 20 #pixels per yard
    app.lineOfScrimmage = app.height-(app.yardStep*14)
    app.sideLineOffset = 194
    app.steps = 0
    app.stepsSinceBallThrown = 0
    app.yardsRan = 0
    app.score = 0
    app.stepsPerSecond = 40

    yardsPerSecond = 3
    app.velocity = yardsPerSecond * (app.yardStep/app.stepsPerSecond)
    app.selectedPlayer = None

    app.score = 0
    app.totalYards = 0
    app.isWinScreen = False
    app.isComplete = False
    app.indexExport = 0
    app.dataPath = ''

    loadOffensiveRoutes(app)
    loadOffensiveFormations(app)
    loadOffensivePlayerRoutes(app)
    loadDefensiveFormations(app)
    loadOffensiveMenuButtons(app)
    loadFieldButtons(app)

def loadOffensiveRoutes(app):
    #Routes are in (dx, dy) format where yards are steps.
    #'Left/Right' is the starting location relative to center of field
    #RB routes start with 'rb'
    crossingLeft = Route((10,-10), (10, -10))
    crossingRight = Route((-10,-10), (-10, -10))

    slantLeft = Route((0, -5), (15,-15))
    slantRight = Route(( 0, -5), (-15, -15))
   
    quickOutLeft = Route((0, -3), (-8, 0))
    quickOutRight = Route((0, -3), (8, 0)) #((3, 0, -3), (8, 3, 0))
   
    shallowDigLeft = Route((0, -5), (15, 0))
    shallowDigRight = Route((0, -5), (-15, 0))

    deepDigLeft = Route((0, -10), (15, 0))
    deepDigRight = Route(( 0, -10), (-15,  0))
   
    shallowOutLeft = Route((0, -5), ( -8, 0))
    shallowOutRight = Route(( 0, -5), (8,  0))
    deepOutLeft = Route((0, -10), ( -8, 0))
    deepOutRight = Route(( 0, -10), (8,  0))
   
    shallowHitchLeft = Route((0, -8), (2, 2))
    shallowHitchRight = Route(( 0,-8), (-2, 2))
    deepHitchLeft = Route(( 0, -12), (2,3))
    deepHitchRight = Route(( 0, -12), (-2, 3))
   
    postLeft = Route(( 0, -12), (5, -10))
    postRight = Route(( 0, -12), (-5, -10))
    cornerLeft = Route(( 0, -12), ( -5, -10))
    cornerRight = Route((0, -12), ( 5, -10))
   
    go = Route((0, -10), (0,-10))
   
    app.wrRouteList= (crossingLeft, crossingRight, slantLeft, slantRight,
                    quickOutLeft, quickOutRight, shallowDigLeft,
                    shallowDigRight, deepDigLeft, deepDigRight,
                    shallowOutLeft, shallowOutRight, deepOutLeft,  
                    deepOutRight, shallowHitchLeft, shallowHitchRight,
                    deepHitchLeft, deepHitchRight, postLeft, postRight,
                    cornerLeft, cornerRight, go)

    rbOutLeft = Route(( 8, -4), ( 5, -2.5)) 
    rbOutRight = Route((-8, -4), (-5, -2.5))
    rbZoneSit = Route((1.5, -10), (0, 1.5))
    app.rbRouteList = (rbOutRight, rbOutLeft, rbZoneSit)

    app.route = go

#Initialize Offense
def loadOffensiveFormations(app):
    dx = dy = 0
    app.singleBack = {'WR1' : WideReceiver(310, app.lineOfScrimmage+13, 
                                dx, dy, app.route),
                  'WR2': WideReceiver(370, app.lineOfScrimmage+33, 
                                dx, dy, app.route),
                  'LT': Lineman(450, app.lineOfScrimmage+18, dx, dy),
                  'LG': Lineman(475, app.lineOfScrimmage+13, dx, dy),
                  'C': Lineman(app.width//2, app.lineOfScrimmage+13, dx, dy),
                  'RG': Lineman(525, app.lineOfScrimmage+13, dx, dy),
                  'RT': Lineman(550, app.lineOfScrimmage+13, dx, dy),
                  'TE': TightEnd(575, app.lineOfScrimmage+28, 
                                dx, dy, app.route),
                  'WR3': WideReceiver(660, app.lineOfScrimmage+13, 
                                dx, dy, app.route),
                  'QB': Quarterback(app.width//2, app.lineOfScrimmage+40, 
                                dx, dy),
                  'RB': RunningBack(app.width//2, app.lineOfScrimmage+70, 
                                dx, dy, app.rbRouteList[2]),
                 }
    app.shotgun = {'WR1' : WideReceiver(310, app.lineOfScrimmage+13, 
                                dx, dy, app.route),
                  'WR2': WideReceiver(370, app.lineOfScrimmage+33, 
                                dx, dy, app.route),
                  'LT': Lineman(450, app.lineOfScrimmage+18, dx, dy),
                  'LG': Lineman(475, app.lineOfScrimmage+13, dx, dy),
                  'C': Lineman(app.width//2, app.lineOfScrimmage+13, dx, dy),
                  'RG': Lineman(525, app.lineOfScrimmage+13, dx, dy),
                  'RT': Lineman(550, app.lineOfScrimmage+13, dx, dy),
                  'TE': TightEnd(575, app.lineOfScrimmage+28, 
                                dx, dy, app.route),
                  'WR3': WideReceiver(660, app.lineOfScrimmage+13, 
                                dx, dy, app.route),
                  'QB': Quarterback(app.width//2, app.lineOfScrimmage+70, 
                                dx, dy),
                  'RB': RunningBack(app.width//2 + 35, app.lineOfScrimmage+70, 
                                dx, dy, app.rbRouteList[2]),
                 }
    app.spread = {'WR1' : WideReceiver(300, app.lineOfScrimmage+13, 
                                dx, dy, app.route),
                  'WR2': WideReceiver(340, app.lineOfScrimmage+33, 
                                dx, dy, app.route),
                  'LT': Lineman(450, app.lineOfScrimmage+18, dx, dy),
                  'LG': Lineman(475, app.lineOfScrimmage+13, dx, dy),
                  'C': Lineman(app.width//2, app.lineOfScrimmage+13, dx, dy),
                  'RG': Lineman(525, app.lineOfScrimmage+13, dx, dy),
                  'RT': Lineman(550, app.lineOfScrimmage+18, dx, dy),
                  'WR3': WideReceiver(660, app.lineOfScrimmage+33, 
                                dx, dy, app.route),
                  'WR4': WideReceiver(725, app.lineOfScrimmage+13, 
                                dx, dy, app.route),
                  'QB': Quarterback(app.width//2, app.lineOfScrimmage+70, 
                                dx, dy),
                  'RB': RunningBack(app.width//2 + 35, app.lineOfScrimmage+70,
                                dx, dy, app.rbRouteList[2]),
                 }
    app.bunch = {'WR1' : WideReceiver(310, app.lineOfScrimmage+13, 
                                dx, dy, app.route),
                  'WR2': WideReceiver(340, app.lineOfScrimmage+27, 
                                dx, dy, app.route),
                  'WR3': WideReceiver(380, app.lineOfScrimmage+15, 
                                dx, dy, app.route),
                  'LT': Lineman(450, app.lineOfScrimmage+18, dx, dy),
                  'LG': Lineman(475, app.lineOfScrimmage+13, dx, dy),
                  'C': Lineman(app.width//2, app.lineOfScrimmage+13, dx, dy),
                  'RG': Lineman(525, app.lineOfScrimmage+13, dx, dy),
                  'RT': Lineman(550, app.lineOfScrimmage+18, dx, dy),
                  'WR4': WideReceiver(725, app.lineOfScrimmage+13, 
                                dx, dy, app.route),
                  'QB': Quarterback(app.width//2, app.lineOfScrimmage+70, 
                                dx, dy),
                  'RB': RunningBack(app.width//2 + 35, app.lineOfScrimmage+70,
                                dx, dy, app.rbRouteList[2]),
                 }
    app.singleBackOriginalLocations = copy.deepcopy(app.singleBack)
    app.shotgunOriginalLocations = copy.deepcopy(app.shotgun)
    app.spreadOriginalLocations = copy.deepcopy(app.spread)
    app.bunchOriginalLocations = copy.deepcopy(app.bunch)
    app.oFormation = app.singleBack
    app.isFootballThrown = False

def loadOffensivePlayerRoutes(app):
    for position in app.oFormation:
        player = app.oFormation[position]
        if isinstance(player, WideReceiver) or isinstance(player, TightEnd):
            randomRoute = random.randrange(len(app.wrRouteList))
            player.route = app.route #app.wrRouteList[randomRoute]
            targetX = player.cx + player.route.x1*app.yardStep
            targetY = player.cy + player.route.y1*app.yardStep
            player.dx, player.dy = goToPoint(app,player,targetX, targetY)
        elif isinstance(player, RunningBack):
            randomRoute = random.randrange(len(app.rbRouteList))
            player.route = app.rbRouteList[2] #app.rbRouteList[randomRoute]
            targetX = player.cx + player.route.x1*app.yardStep
            targetY = player.cy + player.route.y1*app.yardStep
            player.dx, player.dy = goToPoint(app,player,targetX, targetY)

#Initialize Defense  
def loadDefensiveFormations(app):
    coverOne = initializeCoverOne(app)
    coverTwo = dict()
    coverThree = dict()
    coverFour = dict()
    coverTwoBuzz = dict()
    coverOneRobber = dict()
    app.dFormation = coverOne

def initializeCoverOne(app):
    dx = dy = 0
    wrLocations = getWRLocations(app)
    teLocations = getTELocations(app)
    coverOne = dict()
    #Map a CB/LB to a WR/TE
    for i in range(len(wrLocations)):
        wr = wrLocations[i]
        cornerBack = f"CB{i+1}"
        coverOne[cornerBack] = CornerBack(wr.cx,
                    app.lineOfScrimmage-(wr.cy-app.lineOfScrimmage),
                    dx, dy, wr)
    numCB = len(coverOne)
    for i in range(len(teLocations)):
        te = teLocations[i]
        cornerBack = f"CB{numCB+i+1}"
        coverOne[cornerBack] = CornerBack(te.cx,
                app.lineOfScrimmage-(te.cy-app.lineOfScrimmage+10),
                dx, dy, te)
    numCB = len(coverOne)
    numLB = 6-numCB
    for i in range(numLB):
        linebacker = f"LB{i+1}"
        #Evenly distribute remaining LB between hash marks
        xCord = 2*app.width//5 + (i+1)*(app.width//5)//(numLB+1)
        coverOne[linebacker] = LineBacker(xCord, 
                                app.lineOfScrimmage - app.yardStep*4)
    toUnionCoverOne = {'DE1': DefensiveEnd(435, app.lineOfScrimmage-13, 
                                        dx, dy),
                       'DE2': DefensiveEnd(475, app.lineOfScrimmage-13, 
                                        dx, dy),
                       'DT1': DefensiveTackle(510, app.lineOfScrimmage-13, 
                                        dx, dy),
                       'DT2': DefensiveTackle(540, app.lineOfScrimmage-13, 
                                        dx, dy),
                       'S': Safety(app.width//2, 
                                    app.lineOfScrimmage-app.yardStep*12)
                       }
    coverOne |= toUnionCoverOne
    return coverOne

def loadOffensiveMenuButtons(app):
    app.offensiveFormationButtons = []
    app.offensiveWRRouteButtons = []
    app.offensiveRBRouteButtons = []
    singleBack = FormationButton(95, 60, 
                    130, 65, "Single Back", app.singleBack)
    shotgunButton = FormationButton(95, 160, 
                    130, 65, "Shotgun", app.shotgun)
    spreadButton = FormationButton(95, 260, 
                    130, 65, "Spread", app.spread)
    bunchButton = FormationButton(95, 360, 
                    130, 65, "Bunch", app.bunch)
    app.offensiveFormationButtons.append(singleBack)
    app.offensiveFormationButtons.append(shotgunButton)
    app.offensiveFormationButtons.append(spreadButton)
    app.offensiveFormationButtons.append(bunchButton)

    #splices app.WR routes to get left and right route
    crossingButton = RouteButton(app.width-95, 50, 
                            130, 35, "Crossing", app.wrRouteList[0:2]) 
    slantButton = RouteButton(app.width-95, 110, 
                            130, 35, "Slant", app.wrRouteList[2:4])
    quickOutButton = RouteButton(app.width-95, 170, 
                            130, 35, "Quick Out", app.wrRouteList[4:6])
    shallowDigButton = RouteButton(app.width-95, 230, 
                            130, 35, "Shallow Dig", app.wrRouteList[6:8])
    deepDigButton = RouteButton(app.width-95, 290, 
                            130, 35, "Deep Dig", app.wrRouteList[8:10])
    shallowOutButton = RouteButton(app.width-95, 350, 
                            130, 35, "Shallow Out", app.wrRouteList[10:12])
    deepOutButton = RouteButton(app.width-95, 410, 
                            130, 35, "Deep Out", app.wrRouteList[12:14])
    shallowHitchButton = RouteButton(app.width-95, 470, 
                            130, 35, "Shallow Hitch", app.wrRouteList[14:16])
    deepHitchButton = RouteButton(app.width-95, 530, 
                            130, 35, "Deep Hitch", app.wrRouteList[16:18])
    postButton = RouteButton(app.width-95, 590, 
                            130, 35, "Post", app.wrRouteList[18:20])
    cornerButton = RouteButton(app.width-95, 650, 
                            130, 35, "Corner", app.wrRouteList[20:22])
    goButton = RouteButton(app.width-95, 710, 
                            130, 35, "Go", [app.wrRouteList[22], 
                                            app.wrRouteList[22]])
    app.offensiveWRRouteButtons.append(crossingButton)
    app.offensiveWRRouteButtons.append(slantButton)
    app.offensiveWRRouteButtons.append(quickOutButton)
    app.offensiveWRRouteButtons.append(shallowDigButton)
    app.offensiveWRRouteButtons.append(deepDigButton)
    app.offensiveWRRouteButtons.append(shallowOutButton)
    app.offensiveWRRouteButtons.append(deepOutButton)
    app.offensiveWRRouteButtons.append(shallowHitchButton)
    app.offensiveWRRouteButtons.append(deepHitchButton)
    app.offensiveWRRouteButtons.append(postButton)
    app.offensiveWRRouteButtons.append(cornerButton)
    app.offensiveWRRouteButtons.append(goButton)
    app.startGameButton = StartButton(app.width//2, 650, 300, 
                                        150 , "Start Game")

    rbOutButton = RouteButton(app.width-95, 50, 
                        130, 35, "RB Out", app.rbRouteList[0:2]) 
    rbZoneSitButton = RouteButton(app.width-95, 110, 
                        130, 35, "RB Zone Sit", [app.rbRouteList[2], 
                                                app.rbRouteList[2]])
    app.offensiveRBRouteButtons.append(rbOutButton)
    app.offensiveRBRouteButtons.append(rbZoneSitButton)
    app.importButton = exportImportButton(app.sideLineOffset//2, 
                    app.height-45, 150, 50, "Import Play", dict())
    app.exportButton = exportImportButton(app.sideLineOffset//2, 
                app.height-45, 150, 50, "Export Play", dict())

def loadFieldButtons(app):
    resetButton = Button(app.sideLineOffset//2, 40, 100, 50, "Reset")
    menuButton = Button(app.sideLineOffset//2, 110, 100, 50, "Menu")
    app.fieldButtons = [resetButton, menuButton]

#-------------------------------------------------#
#------ Location/Resetting Helper Functions ------#
#-------------------------------------------------#
 
def getWRLocations(app):
    wrLocations = []
    for position in app.oFormation:
        player = app.oFormation[position]
        if isinstance(player, WideReceiver):
            wrLocations.append(player)
    return wrLocations

def getTELocations(app):
    teLocations = []
    for position in app.oFormation:
        player = app.oFormation[position]
        if isinstance(player, TightEnd):
            teLocations.append(player)
    return teLocations

def getRBLocation(app):
    for position in app.oFormation:
        player = app.oFormation[position]
        if isinstance(player, RunningBack):
            return [player]

def inBoundsLeftRight(app, posX):
    if posX<=app.sideLineOffset:
        return 'leftOut'
    elif posX>=app.width-app.sideLineOffset:
        return 'rightOut'
    else: return None

def distance(x1, y1, x2, y2):
    return ((x2 - x1)**2 + (y2 - y1)**2)**0.5

def resetField(app):
    app.isPaused = True
    if app.oFormation==app.singleBack:
        formation = app.singleBackOriginalLocations
    elif app.oFormation==app.shotgun:
        formation = app.shotgunOriginalLocations
    elif app.oFormation==app.spread:
        formation = app.spreadOriginalLocations
    else:
        formation = app.bunchOriginalLocations
    for livePlayer in app.oFormation:
        for basePlayer in formation:
            if livePlayer==basePlayer:
                app.oFormation[livePlayer].cx = formation[basePlayer].cx
                app.oFormation[livePlayer].cy = formation[basePlayer].cy
                app.oFormation[livePlayer].dx = 0
                app.oFormation[livePlayer].dy = 0
    app.steps=0
    app.football.cx = app.oFormation['QB'].cx + Football.armOffset
    app.football.cy = app.oFormation['QB'].cy
    app.football.dx = app.football.dy = 0
    app.football.targetCX = None
    app.football.targetCY = None
    app.football.angle = 0
    app.isFootballThrown = False
    app.isWinScreen = False
    app.stepsSinceBallThrown = 0
    app.exportButton.text = "Export Play"
    app.dFormation = initializeCoverOne(app)

    #Must Reset Field after ball thrown or reset button clicked

#--------------------------#
#------ Draw Screens ------#
#--------------------------#

def redrawAll(app):
    if app.isField:
        drawField(app, scrimmageLine=True)
        drawDefense(app)
        drawOffense(app)
        drawSideline(app)
        drawFieldButtons(app)
        drawFootball(app)
        if not app.isPlayActive and app.steps == 0:
            drawLabel('Press Space to Play', app.width//2, 
                        app.height-50, size=30, bold=True)
        if not app.isPlayActive and app.isWinScreen and app.isComplete:
            drawLabel('Complete!', app.width//2, 
                        app.height-150, size=25, bold=True)
            drawLabel("Press 'r' to Reset", app.width//2, 
                        app.height-50, size=30, bold=True)
        elif not app.isPlayActive and app.isWinScreen and not app.isComplete:
            drawLabel('Incomplete X', app.width//2, 
                        app.height-150, size=25, bold=True)
            drawLabel("Press 'r' to Reset", app.width//2, 
                        app.height-50, size=30, bold=True)
        drawLabel("Click mouse", app.sideLineOffset//2-30, 
                    app.height//2+100, size=22)
        drawLabel("to throw", app.sideLineOffset//2-30, 
                    app.height//2+120, size=22)
        app.exportButton.draw()


    elif app.isMainMenu:
        drawMainMenu(app)
    elif app.isOffensiveMenu:
        drawOffensiveMenu(app)
    elif app.isDefeniveMenu(app):
        drawDefensiveMenu(app)

def drawOffensiveMenu(app):
    drawField(app, scrimmageLine=False)
    drawLabel("Select Formation", app.sideLineOffset//2, 
                13, size=20, bold=True)
    drawLabel("Select Route", app.width - app.sideLineOffset//2, 
                17, size=20, bold=True)

    drawLabel("Click a formation button ", app.sideLineOffset//2, 
                app.height//2+50, size=15, bold=True)
    drawLabel("to select formation", app.sideLineOffset//2, 
                app.height//2+70, size=15, bold=True)
    
    drawLabel("Click a player then a route", app.sideLineOffset//2, 
                app.height//2+110, size=15, bold=True)
    drawLabel("to set player route", app.sideLineOffset//2, 
                app.height//2+130, size=15, bold=True)
    
    drawLabel("Import plays using", app.sideLineOffset//2, 
                app.height//2+170, size=15, bold=True)
    drawLabel("button below, and export", app.sideLineOffset//2, 
                app.height//2+190, size=15, bold=True)
    drawLabel("plays on game screen", app.sideLineOffset//2, 
                app.height//2+210, size=15, bold=True)
    drawLabel("Note: only import using", app.sideLineOffset//2, 
                app.height//2+245, size=12, bold=True)
    drawLabel("exported file structure", app.sideLineOffset//2, 
                app.height//2+258, size=12, bold=True)
    drawLabel("to avoid failed imports", app.sideLineOffset//2, 
                app.height//2+271, size=12, bold=True)

    for button in app.offensiveFormationButtons:
        button.draw()
    if app.isWRMenu:
        for button in app.offensiveWRRouteButtons:
            button.draw()
    else:
        for button in app.offensiveRBRouteButtons:
            button.draw()
    app.startGameButton.draw()
    app.importButton.draw()
    drawRoutes(app)
    drawOffense(app)

def drawRoutes(app):
    for position in app.oFormation:
        if "WR" in position or "RB" in position or "TE" in position:
            player = app.oFormation[position]
            posX1 = player.cx + player.route.x1 * app.yardStep
            posY1 = player.cy + player.route.y1 * app.yardStep
            posX2 = posX1 + player.route.x2 * app.yardStep
            posY2 = posY1 + player.route.y2 * app.yardStep
            #Check to see if route goes out of bounds
            inBounds = inBoundsLeftRight(app, posX2)
            if inBounds != None:
                if inBounds == 'leftOut':
                    posX2 = app.sideLineOffset
                else: 
                    posX2 = app.width-app.sideLineOffset
            drawLine(player.cx, player.cy,
                     posX1, posY1, lineWidth=4)
            drawLine(posX1, posY1, posX2, posY2,
                     lineWidth=4, arrowEnd = True)
            drawRect(posX1, posY1, 4, 4, fill='black', align='center')

#Designed for multiple defensive formaitons evnetually
def drawDefensiveMenu(app):
    drawField(app, scrimmageLine=False)

def drawMainMenu(app):
    customGreen = rgb(27, 150, 85)
    customGreen1 = rgb(19, 130, 60)
    customGreen2 = rgb(10, 110, 30)
    customComplimentRed = rgb(215, 80, 75)
    customComplimentRed1 = rgb(190, 90, 70)
    drawRect(0, 0, app.width, app.height, fill=gradient(customGreen, 
                        customGreen1, customGreen2, start='left-top'))
    drawLine(-6, 60, 200, app.height+6, 
                fill=customComplimentRed, lineWidth = 6)
    drawLine(50, -6, 50, app.height+6, 
                fill=customComplimentRed1, lineWidth = 6)
    drawImage( "routeLabLogo.png", app.width//2, 150, align='center',
                width=750, height=300)
    drawLabel("Create your own football", app.width//2, 
                270, size=35, bold=True,font='monospace')
    drawLabel("routes and dominate the game.", app.width//2, 
                310, size=35,bold=True, font='monospace')
    if app.isMainMenuLabelHovering: 
        drawRect(app.width//2, app.height//2+45, 
                    510, 156, fill=customComplimentRed, 
                    border=customComplimentRed, borderWidth=3, align='center')
        bolded = True
        drawRect(app.width//2, app.height//2+45, 
                    500, 150, fill=customGreen1,  
                    border='black', borderWidth=3, align='center')
        drawLabel("Start Creating Plays ", app.width//2, 
                    app.height//2+45, size=35, 
                    bold=bolded, font='monospace')
    else: 
        drawRect(app.width//2, app.height//2+45, 
                    506, 153, fill=customComplimentRed, 
                    border=customComplimentRed, borderWidth=3, 
                    align='center')
        bolded = False
        drawRect(app.width//2, app.height//2+45, 500, 150, fill=customGreen1,  
                    border='black', borderWidth=3, align='center')
        drawLabel("Start Creating Plays ", app.width//2, 
                    app.height//2+45, size=33, 
                    bold=bolded, font='monospace')

    drawLine(270, app.height-60, 270, app.height-225, 
                lineWidth=7, arrowEnd=True)
    drawCircle(270, app.height-60, 18,
                    fill=customComplimentRed, border='black')

    drawLine(340, app.height-60, 340, app.height-130, lineWidth=7)
    drawLine(340, app.height-130, 450, app.height-130, 
                                        lineWidth=7, arrowEnd=True)
    drawRect(340, app.height-130, 7, 7, fill='black', align='center')
    drawCircle(340, app.height-60, 18,
                    fill=customComplimentRed, border='black')
    drawLine(app.width-190, app.height-60, app.width-190, 
                app.height-150, lineWidth=7)
    drawLine(app.width-190, app.height-150, app.width-270, 
                app.height-220, lineWidth=7, arrowEnd=True)
    drawRect(app.width-190, app.height-150, 
                7, 7, fill='black', align='center')
    drawCircle(app.width-190, app.height-60, 18,
                    fill=customComplimentRed, border='black')

def drawDefense(app):
    for position in app.dFormation:
        player = app.dFormation[position]
        drawCircle(player.cx, player.cy, 13,
                    fill='white', border='black')

def drawOffense(app):
    customComplimentRed = rgb(215, 80, 75)
    deepRed = rgb(180, 30, 50)
    for position in app.oFormation:
        player = app.oFormation[position]
        if app.selectedPlayer==None:
            drawCircle(player.cx, player.cy, 13,
                    fill=customComplimentRed, border='black')
        else:
            if app.selectedPlayer == position:
                drawCircle(player.cx, player.cy, 13,
                    fill=deepRed, border='black')
            else:
                drawCircle(player.cx, player.cy, 13,
                    fill=customComplimentRed, border='black')

def drawField(app, scrimmageLine=True):
    customGreen = rgb(27, 150, 85)
    drawRect(0, 0, app.width, app.height, fill=customGreen)
    tenCount=1
    fiveCount=0
    #Draw Yard Lines
    for i in range(app.height, 0, -app.yardStep):
        #Make it long yard line every 5 yards
        fiveCount+=1
        if fiveCount%5==0:
            drawLine(30+app.sideLineOffset, i, 
                        app.width-30-app.sideLineOffset, i, fill='white')
            if fiveCount%10==0:
                drawLabel(f'{tenCount} 0', 60+app.sideLineOffset, i,
                        size=20, fill='white', rotateAngle=90)
                drawLabel(f'{tenCount} 0', app.width-60-app.sideLineOffset, i,
                        size=20, fill='white', rotateAngle=270)
                tenCount+=1
        else:
            drawLine(30+app.sideLineOffset, i, 
                        40+app.sideLineOffset, i, fill='white')
            drawLine(app.width-30-app.sideLineOffset, i, 
                        app.width-40-app.sideLineOffset, i, fill='white')
            drawLine(3*app.width//7, i, 3*app.width//7+10, i, fill='white')
            drawLine(4*app.width//7, i, 4*app.width//7+10, i, fill='white')
    if scrimmageLine:
        drawLine(20+app.sideLineOffset, 
                    app.height-(app.yardStep*14), 
                    app.width-20-app.sideLineOffset,
                    app.height-(app.yardStep*14), fill='blue')

    drawLine(20+app.sideLineOffset, 0, 20+app.sideLineOffset, app.height,
                fill='white', lineWidth=4)
    drawLine(app.width-20-app.sideLineOffset, 0, 
                app.width-20-app.sideLineOffset, app.height,
                fill='white', lineWidth=4)

def drawSideline(app):
    customComplimentRed = rgb(215, 80, 75)
    drawCircle(app.sideLineOffset - 10, app.lineOfScrimmage, 13,
                    fill=customComplimentRed, border='black')
    drawCircle(app.sideLineOffset - 20, app.lineOfScrimmage + 25, 13,
                    fill=customComplimentRed, border='black')
    drawCircle(app.sideLineOffset - 20, app.lineOfScrimmage - 25, 13,
                    fill=customComplimentRed, border='black')
    drawCircle(app.sideLineOffset - 25, app.lineOfScrimmage - 50, 13,
                    fill=customComplimentRed, border='black')
    drawCircle(app.sideLineOffset - 25, app.lineOfScrimmage - 75, 13,
                    fill=customComplimentRed, border='black')
    
    drawCircle(42, 170, 13, fill=customComplimentRed, border='black')
    drawCircle(41, 196, 13, fill=customComplimentRed, border='black')
    drawCircle(40, 225, 13, fill=customComplimentRed, border='black')
    drawCircle(46, 258, 13, fill=customComplimentRed, border='black')
    drawCircle(45, 283, 13, fill=customComplimentRed, border='black')

    drawCircle(43, 355, 13, fill=customComplimentRed, border='black')
    drawCircle(47, 381, 13, fill=customComplimentRed, border='black')
    drawCircle(46, 419, 13, fill=customComplimentRed, border='black')

    drawCircle(42, 555, 13, fill=customComplimentRed, border='black')
    drawCircle(44, 583, 13, fill=customComplimentRed, border='black')
    drawCircle(40, 615, 13, fill=customComplimentRed, border='black')
    drawCircle(42, 642, 13, fill=customComplimentRed, border='black')

    drawCircle(app.width - app.sideLineOffset + 4, 
                    app.lineOfScrimmage + 8, 13, fill='white', border='black')
    drawCircle(app.width - app.sideLineOffset + 20, 
                    app.lineOfScrimmage + 30, 13, fill='white', border='black')
    drawCircle(app.width - app.sideLineOffset + 20, 
                    app.lineOfScrimmage - 21, 13, fill='white', border='black')
    drawCircle(app.width - app.sideLineOffset + 20, 
                    app.lineOfScrimmage - 50, 13, fill='white', border='black')
    drawCircle(app.width - app.sideLineOffset + 20, 
                    app.lineOfScrimmage - 75, 13, fill='white', border='black')
    
    drawLabel(f'Completions: {app.score}', 
            app.width-app.sideLineOffset//2 - 20, 50, size=23, bold=True)
    drawLabel(f'Yards: {int(app.totalYards)}', 
            app.width-app.sideLineOffset//2 - 30, 80, size=23, bold=True)
    drawLabel(' Yards', app.width-app.sideLineOffset//2 - 50, 
                110, size=20, bold=True)
    drawLabel('________', app.width-app.sideLineOffset//2 - 50, 
                120, size=20, bold=True)
    drawLabel('Completion', app.width-app.sideLineOffset//2 - 50, 
                135, size=18, bold=True)
    drawLabel('=', app.width-app.sideLineOffset//2 +10, 
                125, size=20, bold=True)
    if app.score!=0:
        drawLabel(f'{pythonRound(app.totalYards/app.score, 1)}', 
            app.width-app.sideLineOffset//2 + 50, 125, size=30, bold=True)
    else:
        drawLabel('0', app.width-app.sideLineOffset//2 + 30, 
                    125, size=30, bold=True)

    drawCircle(app.width-42, 175, 13, fill='white', border='black')
    drawCircle(app.width-45, 202, 13, fill='white', border='black')
    drawCircle(app.width-41, 229, 13, fill='white', border='black')

    drawCircle(app.width-48, 300, 13, fill='white', border='black')
    drawCircle(app.width-43, 331, 13, fill='white', border='black')
    drawCircle(app.width-46, 370, 13, fill='white', border='black')
    drawCircle(app.width-41, 405, 13, fill='white', border='black')

    drawCircle(app.width-41, 470, 13, fill='white', border='black')
    drawCircle(app.width-41, 504, 13, fill='white', border='black')
    drawCircle(app.width-45, 542, 13, fill='white', border='black')

    drawCircle(app.width-40, 642, 13, fill='white', border='black')
    drawCircle(app.width-49, 675, 13, fill='white', border='black')
    drawCircle(app.width-42, 702, 13, fill='white', border='black')

def drawFieldButtons(app):
    for button in app.fieldButtons:
        button.draw()

def drawFootball(app):
    app.football.draw()
 
#---------------------------------------#
#------ Player Movement Functions ------#
#---------------------------------------#

def onStep(app):
    # if app.isPaused:
    #     return
    if not app.isPlayActive:
        return
    elif app.isField:
        takeStep(app)

def takeStep(app):
    app.steps+=1
    if app.isFootballThrown:
        app.stepsSinceBallThrown +=1
    app.yardsRan = (app.velocity * app.steps)/app.yardStep
    runRoutes(app)
    moveDefense(app)
    moveBall(app)

#James wrote this function
def runRoutes(app):
    outOfBoundsDistance = 20
    for position in app.oFormation:
        if (isinstance(app.oFormation[position], WideReceiver) or
           isinstance(app.oFormation[position], TightEnd) or
           isinstance(app.oFormation[position], RunningBack)):
            player = app.oFormation[position]
            step1Length = (player.route.x1**2 + player.route.y1**2)**0.5
            step2Length = (player.route.x2**2 + player.route.y2**2)**0.5
            if  step1Length <= app.yardsRan:
                if  step1Length + step2Length <= app.yardsRan:
                    player.dx, player.dy = 0, 0
                else:
                    targetX = player.cx + player.route.x2*app.yardStep
                    targetY = player.cy + player.route.y2*app.yardStep
                    player.dx, player.dy = goToPoint(app,player,
                                                        targetX, targetY)
            else:  
                targetX = player.cx + player.route.x1*app.yardStep
                targetY = player.cy + player.route.y1*app.yardStep
                player.dx, player.dy = goToPoint(app,player,targetX, targetY)
            ballRange = 60
            reactionTime = 20
            if (app.isFootballThrown and app.football.targetCX!=None and
                app.stepsSinceBallThrown >= reactionTime and
                (distance(player.cx, player.cy, 
                app.football.targetCX, app.football.targetCY) <= ballRange)):
                targetX, targetY = app.football.targetCX, app.football.targetCY
                player.dx, player.dy = goToPoint(app,player,targetX, targetY)
            player.cx+=player.dx
            player.cy+=player.dy
            if player.cx <= app.sideLineOffset+outOfBoundsDistance:
                player.cx = app.sideLineOffset+outOfBoundsDistance
                player.dx, player.dy = 0, 0
            elif player.cx >= app.width-app.sideLineOffset-outOfBoundsDistance:
                player.cx = app.width-app.sideLineOffset-outOfBoundsDistance
                player.dx, player.dy = 0, 0

def moveDefense(app):
    rb = getRBLocation(app)
    rb = rb[0]
    maxLBDistance = None
    closestLB = None
    for position in app.dFormation:
        player = app.dFormation[position]
        if (isinstance(player, CornerBack) or 
            (isinstance(player, Safety) and player.man!=None)):
            movePlayer(app, player)
        elif isinstance(player, Safety) and player.man ==None:
            manSafety(app, player)
        elif (isinstance(player, LineBacker) and player.man!=None):
            movePlayer(app, player)
            maxLBDistance = 0
            closestLB = None
        elif isinstance(player, LineBacker) and player.man == None:
            if (maxLBDistance == None or 
                (distance(rb.cx, rb.cy, player.cx, player.cy) < maxLBDistance)):
                maxLBDistance = distance(rb.cx, rb.cy, player.cx, player.cy)
                closestLB = player
    if closestLB!=None:
        closestLB.man = rb

def movePlayer(app, player):
    ballRange = 50
    reactionTime = 30
    if (app.isFootballThrown and app.football.targetCX!=None and
        app.stepsSinceBallThrown >= reactionTime and
        (distance(player.cx, player.cy, 
        app.football.targetCX, app.football.targetCY) <= ballRange)):
        targetX, targetY = app.football.targetCX, app.football.targetCY
    else:
        targetX, targetY = getBallPlacement(player.man, app)
    player.dx, player.dy = goToPoint(app,player, targetX, targetY)
    player.cx += player.dx 
    player.cy += player.dy 
    if player.cx <= app.sideLineOffset:
        player.cx = app.sideLineOffset
    elif player.cx >= app.width-app.sideLineOffset:
        player.cx = app.width-app.sideLineOffset
    movePlayerIfColliding(app, player)

def manSafety(app, safety):
    yardToDefend = 20
    for position in app.oFormation:
        player = app.oFormation[position]
        if player.cy < app.height - yardToDefend*app.yardStep:
            safety.man = player

def movePlayerIfColliding(app, dPlayer):
    for playerString in app.oFormation:
        oPlayer = app.oFormation[playerString]
        if distance(dPlayer.cx, dPlayer.cy,
                    oPlayer.cx, oPlayer.cy) < 9:
            dPlayer.cy = dPlayer.cy - 0.1
            return movePlayerIfColliding(app, dPlayer)
    return

def moveBall(app):
    if app.football.targetCX == None: return
    app.football.cx += app.football.dx
    app.football.cy += app.football.dy
    if (app.football.cx-app.football.dx<=app.football.targetCX<=app.football.cx or
        app.football.cx-app.football.dx>=app.football.targetCX>=app.football.cx):
        app.football.cx = app.football.targetCX
        app.football.cy = app.football.targetCY
        app.football.dx = app.football.dy = 0
        checkSuccessfulThrow(app)
        #app.isPaused = True
        app.isPlayActive = False

def checkSuccessfulThrow(app):
    teLoco = getTELocations(app)
    wrLoco = getWRLocations(app)
    rbLoco = getRBLocation(app)
    players = teLoco + wrLoco + rbLoco
    oCatchRadius = 15
    toReturn = False
    for player in players:
        if distance(app.football.cx, app.football.cy,
                    player.cx, player.cy) <= oCatchRadius:
            app.score+=1
            yardsToAdd = (app.lineOfScrimmage-app.football.cy)//app.yardStep
            app.totalYards += yardsToAdd
            app.isComplete = True
            app.isWinScreen = True
            toReturn = True
    dStopRadius = 10
    for position in app.dFormation:
        player = app.dFormation[position]
        if distance(app.football.cx, app.football.cy, 
                    player.cx, player.cy) <= dStopRadius:
            if toReturn: 
                app.score-=1
                app.totalYards -= yardsToAdd
            app.isComplete = False
            app.isWinScreen = True
            return
    if toReturn: return
    app.isComplete = False
    app.isWinScreen = True

#James wrote this function
def getBallPlacement(receiver, app):
    #Assumes receiver is a WideReceiver, TightEnd, or RunningBack
    qb = app.oFormation['QB']
    ballVelo= app.velocity*3 #3
    playerVelo = (receiver.dx**2 + receiver.dy**2)**0.5
    vRatio=playerVelo/ballVelo
    C = distance(qb.cx, qb.cy, receiver.cx, receiver.cy)
    _, recieverAngle = getRadiusAndAngleToEndpoint(0, 0, 
                                                   receiver.dx, receiver.dy)
    _, wrAngleToQB = getRadiusAndAngleToEndpoint(receiver.cx, receiver.cy, 
                                               qb.cx, qb.cy)
    angleDifference = (recieverAngle - wrAngleToQB) % 360
    sinTheta = math.sin(math.radians(angleDifference))
    qbAngleToBall = math.degrees(math.asin(sinTheta * vRatio)) % 360
    ballAngle= 180-(angleDifference + qbAngleToBall)
    sinBallAngle = math.sin(math.radians(ballAngle))
    throwDistance = (C * sinTheta) / sinBallAngle
    throwAngle = (wrAngleToQB - 180) - qbAngleToBall
    ballX, ballY = getRadiusEndpoint(qb.cx, qb.cy, throwDistance, throwAngle)
    return ballX, ballY

#James wrote this function
def getRadiusEndpoint(cx, cy, r, theta):
    return (cx + r*math.cos(math.radians(theta)),
            cy - r*math.sin(math.radians(theta)))

#James wrote this function
def getRadiusAndAngleToEndpoint(cx, cy, targetX, targetY):
    radius = distance(cx, cy, targetX, targetY)
    angle = math.degrees(math.atan2(cy-targetY, targetX-cx)) % 360
    return (radius, angle)

#James wrote this function
def goToPoint(app,player,targetX, targetY):
    if distance(player.cx, player.cy,
                targetX, targetY) < app.velocity:
        dx, dy = (targetX - player.cx), (targetY - player.cy)
        return dx, dy
    ratio = app.velocity/distance(player.cx, player.cy,
                     targetX, targetY)
    dx = (targetX - player.cx) * ratio 
    dy = (targetY - player.cy) * ratio
    return dx, dy

def setFootballPlacement(app, mx, my):
    app.football.targetCX, app.football.targetCY = mx, my
    ballVelo = app.velocity*4 #3
    DX = abs(mx - app.football.cx)
    DY = abs(my - app.football.cy)
    dy = math.sqrt((ballVelo**2 * DY**2)/(DX**2 + DY**2))
    dx = (dy*DX)/DY
    if mx<=app.football.cx:
        dx = -dx
    if my<=app.football.cy:
        dy = -dy
    app.football.dx = dx
    app.football.dy = dy

def setBallAngle(app):
    x = app.football.cx - app.football.targetCX
    y = app.football.cy - app.football.targetCY
    angle = math.degrees(math.atan(x/y))
    app.football.angle = 180-angle
    
def importData(app):
    print('importing')
    app.dataPath = app.getTextInput('Input Play File Path')
    try: 
        with open(app.dataPath, 'r') as file:
            formation = json.load(file)
    except FileNotFoundError:
        app.importButton.text = "File Not Found"
        print('Invalid File')
        return
    if not isinstance(formation, dict): 
        print('Error: Invalid Player Data')
        return
    formationRes = dict()
    for position in formation:
        if "WR" in position or "RB" in position or "TE" in position:
            isLegal = checkLegalSkillPlayer(formation, position)
            if not isLegal:
                app.importButton.text = "Invalid Data"
                print('Error: Invalid Skill Player Data')
                return
            playerInfo = formation[position]
            route = Route((playerInfo["routeDX1"], 
                        playerInfo["routeDY1"]),
                        (playerInfo["routeDX2"],
                        playerInfo["routeDY2"]))
            if "WR" in position:
                formationRes[position] = WideReceiver(playerInfo["cx"],
                            playerInfo["cy"],playerInfo["dx"], 
                            playerInfo["dy"], route)
            elif "RB" in position:
                formationRes[position] = RunningBack(playerInfo["cx"],
                            playerInfo["cy"],playerInfo["dx"], 
                            playerInfo["dy"], route)
            elif "TE" in position:
                formationRes[position] = TightEnd(playerInfo["cx"],
                            playerInfo["cy"],playerInfo["dx"], 
                            playerInfo["dy"], route)
        else:
            isLegal = checkLegalNormalPlayer(formation, position)
            if not isLegal:
                app.importButton.text = "Invalid Data"
                print('Error: Invalid Normal Player Data')
                return
            playerInfo = formation[position]
            if "QB" in position:
                formationRes[position] = Quarterback(playerInfo["cx"],
                            playerInfo["cy"], playerInfo["dx"], 
                            playerInfo["dy"])
            else:
                formationRes[position] = Lineman(playerInfo["cx"],
                            playerInfo["cy"],playerInfo["dx"], 
                            playerInfo["dy"])
    app.importButton.text = "Imported!"
    app.oFormation = formationRes

def checkLegalSkillPlayer(formation, position):
    playerInfo = formation[position]
    return ("cx" in playerInfo and "cy" in playerInfo and 
            "dx" in playerInfo and "dy" in playerInfo and
            "routeDX1" in playerInfo and "routeDY1" in playerInfo and 
            "routeDX2" in playerInfo and "routeDY2" in playerInfo and
            len(formation[position]) == 8)

def checkLegalNormalPlayer(formation, position):
    playerInfo = formation[position]
    return ("cx" in playerInfo and "cy" in playerInfo and 
            "dx" in playerInfo and "dy" in playerInfo and
            len(formation[position]) == 4)

def exportData(app):
    resetField(app)
    playDict = dict()
    dx = dy = 0
    for position in app.oFormation:
        player = app.oFormation[position]
        if "WR" in position or "RB" in position or "TE" in position:
            playDict[position] = {"cx": player.cx, "cy":player.cy, 
                                "dx": dx, "dy":dy, 
                                "routeDX1": player.route.x1, 
                                "routeDY1": player.route.y1, 
                                "routeDX2": player.route.x2,  
                                "routeDY2": player.route.y2}
        else:
            playDict[position] = {"cx": player.cx, "cy":player.cy, 
                                "dx": dx, "dy":dy}
    with open(f"routeLabPlay{app.indexExport}.json", "w") as file:
        json.dump(playDict, file, indent=2)
    app.indexExport+=1
    app.exportButton.text = "Exported!"

#----------------------------------#
#------ User Input Functions ------#
#----------------------------------#

def onMouseMove(app, mx, my):
    if app.isMainMenu:
        #main button check
        if ((app.width//2)-250<=mx<=(app.width//2)+250 and 
            (app.height//2+45)-75<=my<=(app.height//2+45)+75):
            app.isMainMenuLabelHovering = True
        else: app.isMainMenuLabelHovering = False
    elif app.isOffensiveMenu:
        app.importButton.checkBold(mx, my)
        for button in app.offensiveFormationButtons:
            button.checkBold(mx, my)
        if app.isWRMenu:
            for button in app.offensiveWRRouteButtons:
                button.checkBold(mx, my)
        else:
            for button in app.offensiveRBRouteButtons:
                button.checkBold(mx, my)
        app.startGameButton.checkBold(mx, my)
    elif app.isField:
        for button in app.fieldButtons:
            button.checkBold(mx, my)
        if app.exportButton.text == "Export Play":
            app.exportButton.checkBold(mx, my)

def onMousePress(app, mx, my):
    if app.isMainMenu:
        if ((app.width//2)-250<=mx<=(app.width//2)+250 and 
            (app.height//2+45)-75<=my<=(app.height//2+45)+75):
            app.isMainMenuLabelHovering = False
            app.isMainMenu = False
            app.isOffensiveMenu = True
    elif app.isOffensiveMenu:
        if app.importButton.isClicked(mx, my):
            importData(app)
        for button in app.offensiveFormationButtons:
            if button.isClicked(mx, my):
                app.oFormation = button.formation
                app.selectedPlayer = None
        if app.isWRMenu:
            for button in app.offensiveWRRouteButtons:
                if button.isClicked(mx, my):
                    if app.selectedPlayer==None: return
                    player = app.oFormation[app.selectedPlayer]
                    if player.cx<=app.width//2:
                        player.route = button.leftRoute
                    else:
                        player.route = button.rightRoute
        else:
            for button in app.offensiveRBRouteButtons:
                if button.isClicked(mx, my):
                    if app.selectedPlayer==None: return
                    player = app.oFormation[app.selectedPlayer]
                    if player.cx<=app.width//2:
                        player.route = button.leftRoute
                    else:
                        player.route = button.rightRoute
        for position in app.oFormation:
            if 'WR' in position or "TE" in position:
                player = app.oFormation[position]
                if distance(player.cx, player.cy, mx, my) <= 13:
                    if app.selectedPlayer == position:
                        app.selectedPlayer = None
                    else:
                        app.selectedPlayer = position
                        app.isWRMenu = True
            elif "RB" in position:
                player = app.oFormation[position]
                if distance(player.cx, player.cy, mx, my) <= 13:
                    if app.selectedPlayer == position:
                        app.selectedPlayer = None
                    else:
                        app.selectedPlayer = position
                        app.isWRMenu = False
        if app.startGameButton.isClicked(mx, my):
            app.football = Football(app)
            app.isField = True
            app.isOffensiveMenu = False
            app.selectedPlayer = None
            app.dFormation = initializeCoverOne(app)
            app.isPlayActive = False
    elif app.isField:
        if (app.exportButton.text == "Export Play" and 
            app.exportButton.isClicked(mx, my)):
            exportData(app)
        for button in app.fieldButtons:
            if button.isClicked(mx, my):
                if button.text == 'Reset':
                    app.isPlayActive = False
                    resetField(app)
                    return
                else:
                    app.importButton.text = "Import Play"
                    app.isPlayActive = False
                    resetField(app)
                    app.isField = False
                    app.isOffensiveMenu = True
                    return
        if (app.sideLineOffset<=mx<=app.width-app.sideLineOffset and
            not app.isFootballThrown and app.isPlayActive):
            setFootballPlacement(app, mx, my)
            setBallAngle(app)
            app.isFootballThrown = True

def onKeyPress(app, key):
    if key == 'space':
        if not app.isPlayActive:
            app.isPlayActive = not app.isPlayActive
        #app.isPaused = not app.isPaused
    elif key == 's':
        takeStep(app)
    elif key=='r' and not app.isPlayActive:
        resetField(app)

#------------------#
#------ Main ------#
#------------------#

def main():
    runApp()

main()