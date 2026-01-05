from cmu_graphics import *
import random
import math
import copy
import json
'''
To do:
    Fix Base Routes
    Fix ArrowEnd drawing
    Update User Directions
    Change how player data imported/exported
'''
def onKeyPress(app, key):
    if key == 'p':
        app.isPaused = not app.isPaused
    elif key == 'space':
        takeStep(app)
    elif key == 'r':
        resetApp(app)
    elif key=='space':
        if not app.isPlayActive:
            app.isPlayActive = not app.isPlayActive

def onKeyHold(app, keys):
    if 'up' in keys and app.ball.carrier != None:
        carrier = app.ball.carrier
        carrier.targetY = carrier.cy-10*app.yardStep
    if 'down' in keys and app.ball.carrier != None:
        carrier = app.ball.carrier
        carrier.targetY = carrier.cy+10*app.yardStep
    if 'right' in keys and app.ball.carrier != None:
        carrier = app.ball.carrier
        carrier.targetX = carrier.cx+10*app.yardStep
    if 'left' in keys and app.ball.carrier != None:
        carrier = app.ball.carrier
        carrier.targetX = carrier.cx-10*app.yardStep
def onKeyRelease(app, key):
    if key == 'up' and app.ball.carrier != None:
        app.ball.carrier.targetY = app.ball.carrier.cy
    elif key == 'down' and app.ball.carrier != None:
        app.ball.carrier.targetY = app.ball.carrier.cy
    elif key == 'left' and app.ball.carrier != None:
        app.ball.carrier.targetX = app.ball.carrier.cx
    elif key == 'right' and app.ball.carrier != None:
        app.ball.carrier.targetX = app.ball.carrier.cx

def onAppStart(app):
    app.width = 1000
    app.height = 750
    app.sideLineOffset = 194
    app.yardLine = 0
    app.totalYards = 0
    app.score = 0
    app.yardStep = 20 #pixels per yard, 15
    app.lineOfScrimmage = app.height-(app.yardStep*14) # Line of Scrimmage
    app.stepsPerSecond = 40
    app.yardsPerSecond = 5
    app.velocity = app.yardsPerSecond * (app.yardStep/app.stepsPerSecond)
    app.maxSpeed = app.velocity #pixels per step
    app.acceleration = 0.2 * app.yardStep/app.stepsPerSecond#pixels per step^2
    app.fieldSides = [30, app.width-30]
    app.maxBallVelo = 5
    app.mouseX = 0
    app.mouseY = 0

    loadOffensiveRoutes(app)
    loadOffensiveFormations(app, firstTime =True)
    resetApp(app)
    loadOffensiveMenuButtons(app)
    loadFieldButtons(app)
    app.isField = False
    app.isMainMenu = True
    app.isOffensiveMenu = False
    app.isMainMenuLabelHovering = False
    app.isWRMenu = True

def resetApp(app):
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
    app.playIsActive = False
    app.selectedPlayer = None
    app.isField = True
    app.isDefensiveMenu = False
    app.isOffensiveMenu = False
    app.isRouteCombination = False
    app.isPaused = True
    app.steps = 0
    app.yardsRan = 0
    app.isPlayActive = False
    app.ballVelocity = 0
    app.throwing = False
    app.playResult = ''
    app.ballCarrier = None
    # loadOffensiveRoutes(app)
    # loadOffensiveFormations(app)
    # loadOffensivePlayerRoutes(app)
    app.ball = Ball(app.oFormation['C'].cx,app.oFormation['C'].cy,app.oFormation['C'])
    loadDefensiveFormations(app)
class Ball:
    def __init__(self, cx, cy, carrier, dx=0, dy=0, targetX=None, targetY=None):
        self.carrier = carrier
        self.dx = dx
        self.dy = dy
        self.cx = cx
        self.cy = cy
        self.targetX = targetX
        self.targetY = targetY
        self.beingSnapped = False
        self.height = 0
    def drawBall(self, app):
        offset = 0
        if self.cy <= 10*app.yardStep:
            offset = 10*app.yardStep - app.ball.cy
        scalefactor = 1+self.height/50
        angle = self.getAngle()
        drawOval(self.cx, self.cy + offset, 10 * scalefactor, 5*scalefactor, 
                 fill='brown', align='center', rotateAngle = angle)
    def throwToTarget(self, targetX, targetY, app):
        self.targetX = targetX
        self.targetY = targetY
        self.carrier = None
        self.height = 5
        self.throwDistance = distance(self.cx, self.cy, targetX, targetY)
        dx = self.targetX - self.cx
        dy = self.targetY - self.cy
        ratio = app.ballVelocity/self.throwDistance
        self.dx = dx * ratio
        self.dy = dy * ratio
        self.distanceTravelled = 0
    def updateBallPosition(self, app):
        if self.carrier != None:
            if self.carrier == app.oFormation['C']:
                self.beingSnapped = True
                app.ballVelocity = 4
                self.throwToTarget(app.oFormation['QB'].cx, 
                                   app.oFormation['QB'].cy, app)
                return
            self.cx = self.carrier.cx
            self.cy = self.carrier.cy
        elif app.playResult == 'incomplete':
            self.dx = random.randrange(-1, 2)
            self.dy = random.randrange(-1, 2)
            self.cx += self.dx
            self.cy += self.dy
        elif self.targetX != None and self.targetY != None:
            #Move ball towards target
            self.cx += self.dx
            self.cy += self.dy
            self.distanceTravelled += app.ballVelocity
            self.updateHeight(app)
            self.checkCatch(app)
    def updateHeight(self, app):
        #distanceTravelled = self.throwDistance - distance(self.cx, self.cy,
                                                #self.targetX, self.targetY)
        timePassed = self.distanceTravelled/app.ballVelocity
        totalTime = self.throwDistance/app.ballVelocity
        acceleration = 0.01
        
        yInitial = acceleration*totalTime/2
        yVelocity = yInitial-acceleration*timePassed
        self.height += yVelocity
    
    def checkCatch(self, app):
        if self.height <= 0:
            #Ball hit ground
            app.playResult = 'incomplete'
            app.isPaused = True
            self.height = 0
            self.dx, self.dy = 0, 0
            self.targetX, self.targetY = None, None
        elif self.height <= 6:
            #Ball is catchable
            closestReceiver = None
            closestDistance = float('inf')
            allPlayers = list(app.oFormation.values())+list(app.dFormation.values())
            for player in allPlayers:
                if (isinstance(player, SkillPlayer) 
                    or (isinstance(player, Quarterback) and self.beingSnapped) 
                    or isinstance(player, CoverPlayer)):
                    distToBall = distance(self.cx, self.cy, player.cx, player.cy)
                    if distToBall < closestDistance:
                        closestDistance = distToBall
                        closestReceiver = player
            if closestDistance <= 10:
                self.beingSnapped = False
                #Caught!
                self.carrier = closestReceiver
                if isinstance(closestReceiver, CoverPlayer):
                    app.playResult = 'intercepted'
                self.cx = closestReceiver.cx
                self.cy = closestReceiver.cy
                self.dx, self.dy = 0, 0
                self.targetX, self.targetY = None, None
                self.height = 0
        elif self.height <=8:
            defPlayers = list(app.dFormation.values())
            for player in defPlayers:
                if isinstance(player, CoverPlayer):
                    distToBall = distance(self.cx, self.cy, player.cx, player.cy)
                    if distToBall <= 10:
                        app.playResult = 'incomplete'
                        self.dx, self.dy = 0, 0
                        self.targetX, self.targetY = None, None
                        self.height = 0
    def getAngle(self):
        if self.targetX != None and self.targetY!= None:
            _, angle = getRadiusAndAngleToEndpoint(self.cx, self.cy, 
                                                   self.targetX, self.targetY)
            return -angle
        else:
            return 90
class Zone:
    def __init__(self,left, right, top, bottom, cx=None, cy=None):
        self.cx = cx if cx != None else (left + right)/2
        self.cy = cy if cy != None else (top + bottom)/2
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom 
class Player:
    def __init__(self, cx, cy, dx=0, dy=0, targetX=None, targetY=None):
        self.cx = cx
        self.cy = cy
        self.dx = dx
        self.dy = dy
        self.targetX = targetX
        self.targetY = targetY
   
    def __repr__(self):
        return f"cx = {self.cx}, cy = {self.cy}"
       
    def __eq__(self, other):
        return (isinstance(other, Player) and
                self.cx==other.cx and
                self.cy==other.cy)
               
    def __hash__(self):
        return hash(str(self))
       
    def isOutOfBounds(self,app):
        if self.cx <= 24 or self.cx>=app.width-24:
            return True
        else: return False

    def clickInPlayer(self, mouseX, mouseY):
        if distance(self.cx, self.cy, mouseX, mouseY) <= 10:
            return True
        else:
            return False
    
    def goToPoint(self, app):
        dx = self.targetX - self.cx
        dy = self.targetY - self.cy

        dist = distance(self.cx, self.cy, self.targetX, self.targetY)

        if dist == 0:
            return

        # Desired velocity direction
        desiredVx = (dx / dist) * app.maxSpeed
        desiredVy = (dy / dist) * app.maxSpeed
        # Slow down when close to target
        correctionDist = 2*app.yardStep
        if dist < correctionDist:
            desiredVx *= dist / correctionDist
            desiredVy *= dist / correctionDist

        # Steering = desired - current velocity
        steerX = desiredVx - self.dx
        steerY = desiredVy - self.dy

        # Limit steering force (acceleration)
        steerMag = distance(0, 0, steerX, steerY)
        if steerMag > app.acceleration:
            steerX = (steerX / steerMag) * app.acceleration
            steerY = (steerY / steerMag) * app.acceleration

        # Apply acceleration to velocity
        self.dx += steerX
        self.dy += steerY

        # Limit max speed
        speed = distance(0, 0, self.dx, self.dy)
        if speed > app.maxSpeed:
            self.dx = (self.dx / speed) * app.maxSpeed
            self.dy = (self.dy / speed) * app.maxSpeed
    def trackBall(self, app):
        # check if ball in sight
        self.targetX = app.ball.targetX
        self.targetY = app.ball.targetY
        self.goToPoint(app)
        self.movePlayer(app)
    def runWithBall(self, app):
        self.targetX = self.cx
        goalLine = app.lineOfScrimmage - app.yardStep*85
        self.targetY = goalLine 
        self.goToPoint(app)
        self.movePlayer(app)
    def block(self, app):
        defender = self.getNearestDefender(app)
        self.stopPlayer(app, defender)
    def movePlayer(self, app):
        self.cx+=self.dx
        self.cy+=self.dy
        if self.cx <= 24:
            self.cx = 24
        elif self.cx >= app.width-24:
            self.cx = app.width-24
    def stopPlayer(self, app, target):
        #Assumes target is a WideReceiver, TightEnd, or RunningBack
        #Find self
        playerVelo=app.maxSpeed
        targetVelo = (target.dx**2 + target.dy**2)**0.5
        vRatio=targetVelo/playerVelo
        C = distance(self.cx, self.cy, target.cx, target.cy)
        _, targetAngle = getRadiusAndAngleToEndpoint(0, 0, 
                                                    target.dx, target.dy)
        _, angleToTarget = getRadiusAndAngleToEndpoint(target.cx, target.cy, 
                                                self.cx, self.cy)
        angleDifference = (targetAngle - angleToTarget) % 360
        sinTheta = math.sin(math.radians(angleDifference))
        playerAngle = (math.degrees(math.asin(sinTheta * vRatio))) % 360
        ballAngle= 180-(angleDifference + playerAngle)
        sinGoalPointAngle = math.sin(math.radians(ballAngle))
        if - 0.0015< sinGoalPointAngle<0.0015 :
            self.targetX, self.targetY = getRadiusEndpoint(self.cx, self.cy, 
                                                       10*app.yardStep, 
                                                       targetAngle)
            self.goToPoint(app)
            self.movePlayer(app)
            return
        throwDistance = (C * sinTheta) / sinGoalPointAngle
        throwAngle = (angleToTarget - 180) - playerAngle

        self.targetX, self.targetY = getRadiusEndpoint(self.cx, self.cy, 
                                                       throwDistance, 
                                                       throwAngle)
        self.goToPoint(app)
        self.movePlayer(app)
        #put the tartget slightly in front of the target
        # ballDistanceToself = distance(self.cx, self.cy, ballX, ballY)
        # if (self.cx == ballX) and (self.cy == ballY):
        #     return ballX, ballY
        # ballToselfX =  (self.cx - ballX)/ballDistanceToself 
        # ballToselfY = (self.cy - ballY)/ballDistanceToself
        # correctedX = ballX + ballToselfX * app.yardStep*1
        # correctedY = ballY + ballToselfY * app.yardStep*1
    def getNearestDefender(self, app):
        closestDist = None
        closest = None
        for player in app.dFormation.values():
            dist = distance(self.cx, self.cy, player.cx, player.cy)
            if closestDist == None or dist<closestDist:
                closest = player
                closestDist = dist
        return closest
        
class SkillPlayer(Player):
    def __init__(self, app,  cx, cy, dx=0, dy=0, route=None):
        super().__init__( cx, cy, dx, dy)
        
        self.startX = cx
        self.startY = cy
        self.targetX = self.cx + route[0][0]*app.yardStep
        self.targetY = self.cy + route[0][1]*app.yardStep
        self.route = self.translateRoute(app,route)
    def runRoute(self, app):
        yardsRunAlready = 0
        for i in range(1, len(self.route)):
            currStep = self.route[i]
            prevStep = self.route[i-1]
            step = (currStep[0]-prevStep[0], currStep[1]-prevStep[1])
            stepLength = ((step[0])**2 + (step[1])**2)**0.5
            stepLength = stepLength/app.yardStep
            if app.yardsRan >= stepLength + yardsRunAlready: #Completed this step
                yardsRunAlready += stepLength
                if i == len(self.route)-1:
                    self.goToPoint(app)
                    break
                    
            else:  
                self.targetX = currStep[0]
                self.targetY = currStep[1]
                self.goToPoint(app)
                break
        self.movePlayer(app)
    def translateRoute(self, app, route):
        newRoute = [(x*app.yardStep,
                      y*app.yardStep) for (x,y) in route]
        newRoute = [(self.startX, self.startY)] + newRoute
        for i in range(1, len(newRoute)):
            endX, endY = newRoute[i]
            startX, startY = newRoute[i-1]
            endX += startX
            endY += startY
            newRoute[i] = (endX, endY)
        return newRoute
    def drawRoute(self, app):
        i=1
        print("drawingRoute")
        while i < len(self.route)-1:
            endX, endY = self.route[i]
            startX, startY = self.route[i-1]
    
            drawLine(startX, startY, endX, endY,
                     fill='black', lineWidth=2)
            i+=1
        arrowX, arrowY = self.route[-1]
        prevX, prevY = self.route[-2]
        print(self, arrowX, arrowY, prevX, prevY)
        drawLine(prevX, prevY, arrowX, arrowY, 
                fill='black', lineWidth=2, arrowEnd=True)

    def drawVelocity(self, app):
        drawLine(self.cx, self.cy,
                 self.cx + self.dx*5,
                 self.cy + self.dy*5,
                 fill='blue', lineWidth=2)
    

class WideReceiver(SkillPlayer):
    def __init__(self, app,  cx, cy, dx=0, dy=0, route=None):
        super().__init__( app, cx, cy, dx, dy, route)
    
class RunningBack(SkillPlayer):
    def __init__(self, app,  cx, cy, dx=0, dy=0, route=None):
        super().__init__( app, cx, cy, dx, dy, route)
class TightEnd(SkillPlayer):
    def __init__(self, app,  cx, cy, dx=0, dy=0, route=None):
        super().__init__( app, cx, cy, dx, dy, route)
class Quarterback(Player):
    def __init__(self,  cx, cy, dx=0, dy=0):
        super().__init__( cx, cy, dx, dy)
class Lineman(Player):
    def __init__(self,  cx, cy, dx=0, dy=0):
        super().__init__( cx, cy, dx, dy)
class CoverPlayer(Player):
    def __init__(self,  cx, cy, dx=0, dy=0, man=None, zone=None):
        super().__init__( cx, cy, dx, dy)
        self.zone = zone
        self.man = man
        self.targetX = cx
        self.targetY = cy
    def guardMan(self, app):
        if self.man == None:
            if self.zone != None:
                self.playZone(app)
            return
        self.targetX, self.targetY = getBallPlacement(self.man, app)
        if app.yardsRan < 3:
            self.targetY = min(app.lineOfScrimmage - app.yardStep*5, self.targetY)
        # if distance(self.cx, self.cy, self.targetX, self.targetY) < 30:
        #     self.targetX = self.cx
        #     self.targetY = self.cy
        self.goToPoint(app)
        self.cx += self.dx
        self.cy += self.dy
        
        
        if self.cx <= 24:
            self.cx = 24
        elif self.cx >= app.width-24:
            self.cx = app.width-24
    def playZone(self, app):
        zone = self.zone
        #Find target point in zone
        self.targetX = zone.cx
        self.targetY = zone.cy
        for player in app.oFormation.values():
            if isinstance(player, SkillPlayer):

                ballX, ballY = getBallPlacement(player, app)
                if (zone.left <= ballX <= zone.right and
                    zone.top <= ballY <= zone.bottom):
                    self.targetX = ballX
                    self.targetY = ballY
                    break
        self.goToPoint(app)
        self.cx += self.dx
        self.cy += self.dy
        
        if self.cx <= 24:
            self.cx = 24
        elif self.cx >= app.width-24:
            self.cx = app.width-24
    def checkTackle(self, app):
        ballCarrier= app.ball.carrier
        dist = distance(self.cx, self.cy, ballCarrier.cx, ballCarrier.cy)
        if dist <= 15:
            app.playResult = 'tackled'
            
        

class CornerBack(CoverPlayer):
    def __init__(self,  cx, cy, dx=0, dy=0, man=None, zone=None):
        super().__init__( cx, cy, dx, dy, man, zone)
class LineBacker(CoverPlayer):
    def __init__(self,  cx, cy, dx=0, dy=0, man=None, zone=None):
        super().__init__( cx, cy, dx, dy, man, zone)
class PassRusher(Player):
    def __init__(self,  cx, cy, dx=0, dy=0):
        super().__init__( cx, cy, dx, dy)
        self.rushingQB = False
    def rushQB(self, app):
        qb = app.oFormation['QB']
        if self.rushingQB:
            self.targetX = qb.cx
            self.targetY = qb.cy
        else:
            self.targetX = self.cx
            self.targetY = app.lineOfScrimmage + 1*app.yardStep
            if random.randrange(0, app.stepsPerSecond*40) == 1 and app.yardsRan >3:
                self.rushingQB = True
        self.goToPoint(app)
        self.movePlayer(app)
    def checkTackle(self, app):
        ballCarrier= app.ball.carrier
        dist = distance(self.cx, self.cy, ballCarrier.cx, ballCarrier.cy)
        if dist <= 15:
            app.playResult = 'tackled'
class DefensiveTackle(PassRusher):
    def __init__(self,  cx, cy, dx=0, dy=0):
        super().__init__( cx, cy, dx, dy)
class DefensiveEnd(PassRusher):
    def __init__(self,  cx, cy, dx=0, dy=0):
        super().__init__( cx, cy, dx, dy)
class Safety(CoverPlayer):
    def __init__(self,  cx, cy, dx=0, dy=0, man=None, zone=None):
        super().__init__( cx, cy, dx, dy, man, zone)

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
#Initialize Offense
def loadOffensiveFormations(app, firstTime = False):
    dx = dy = 0
    app.singleBack = {'WR1' : WideReceiver(app, 310, app.lineOfScrimmage+13, 
                                dx, dy, app.route),
                  'WR2': WideReceiver(app, 370, app.lineOfScrimmage+33, 
                                dx, dy, app.route),
                  'LT': Lineman(450, app.lineOfScrimmage+18, dx, dy),
                  'LG': Lineman(475, app.lineOfScrimmage+13, dx, dy),
                  'C': Lineman(app.width//2, app.lineOfScrimmage+13, dx, dy),
                  'RG': Lineman(525, app.lineOfScrimmage+13, dx, dy),
                  'RT': Lineman(550, app.lineOfScrimmage+13, dx, dy),
                  'TE': TightEnd(app, 575, app.lineOfScrimmage+28, 
                                dx, dy, app.route),
                  'WR3': WideReceiver(app, 660, app.lineOfScrimmage+13, 
                                dx, dy, app.route),
                  'QB': Quarterback(app.width//2, app.lineOfScrimmage+40, 
                                dx, dy),
                  'RB': RunningBack(app, app.width//2, app.lineOfScrimmage+70, 
                                dx, dy, app.rbRouteList[2]),
                 }
    app.shotgun = {'WR1' : WideReceiver(app, 310, app.lineOfScrimmage+13, 
                                dx, dy, app.route),
                  'WR2': WideReceiver(app, 370, app.lineOfScrimmage+33, 
                                dx, dy, app.route),
                  'LT': Lineman(450, app.lineOfScrimmage+18, dx, dy),
                  'LG': Lineman(475, app.lineOfScrimmage+13, dx, dy),
                  'C': Lineman(app.width//2, app.lineOfScrimmage+13, dx, dy),
                  'RG': Lineman(525, app.lineOfScrimmage+13, dx, dy),
                  'RT': Lineman(550, app.lineOfScrimmage+13, dx, dy),
                  'TE': TightEnd(app, 575, app.lineOfScrimmage+28, 
                                dx, dy, app.route),
                  'WR3': WideReceiver(app, 660, app.lineOfScrimmage+13, 
                                dx, dy, app.route),
                  'QB': Quarterback(app.width//2, app.lineOfScrimmage+70, 
                                dx, dy),
                  'RB': RunningBack(app, app.width//2 + 35, app.lineOfScrimmage+70, 
                                dx, dy, app.rbRouteList[2]),
                 }
    app.spread = {'WR1' : WideReceiver(app, 300, app.lineOfScrimmage+13, 
                                dx, dy, app.route),
                  'WR2': WideReceiver(app, 340, app.lineOfScrimmage+33, 
                                dx, dy, app.route),
                  'LT': Lineman(450, app.lineOfScrimmage+18, dx, dy),
                  'LG': Lineman(475, app.lineOfScrimmage+13, dx, dy),
                  'C': Lineman(app.width//2, app.lineOfScrimmage+13, dx, dy),
                  'RG': Lineman(525, app.lineOfScrimmage+13, dx, dy),
                  'RT': Lineman(550, app.lineOfScrimmage+18, dx, dy),
                  'WR3': WideReceiver(app, 660, app.lineOfScrimmage+33, 
                                dx, dy, app.route),
                  'WR4': WideReceiver(app, 725, app.lineOfScrimmage+13, 
                                dx, dy, app.route),
                  'QB': Quarterback(app.width//2, app.lineOfScrimmage+70, 
                                dx, dy),
                  'RB': RunningBack(app, app.width//2 + 35, app.lineOfScrimmage+70,
                                dx, dy, app.rbRouteList[2]),
                 }
    app.bunch = {'WR1' : WideReceiver(app, 310, app.lineOfScrimmage+13, 
                                dx, dy, app.route),
                  'WR2': WideReceiver(app, 340, app.lineOfScrimmage+27, 
                                dx, dy, app.route),
                  'WR3': WideReceiver(app, 380, app.lineOfScrimmage+15, 
                                dx, dy, app.route),
                  'LT': Lineman(450, app.lineOfScrimmage+18, dx, dy),
                  'LG': Lineman(475, app.lineOfScrimmage+13, dx, dy),
                  'C': Lineman(app.width//2, app.lineOfScrimmage+13, dx, dy),
                  'RG': Lineman(525, app.lineOfScrimmage+13, dx, dy),
                  'RT': Lineman(550, app.lineOfScrimmage+18, dx, dy),
                  'WR4': WideReceiver(app, 725, app.lineOfScrimmage+13, 
                                dx, dy, app.route),
                  'QB': Quarterback(app.width//2, app.lineOfScrimmage+70, 
                                dx, dy),
                  'RB': RunningBack(app, app.width//2 + 35, app.lineOfScrimmage+70,
                                dx, dy, app.rbRouteList[2]),
                 }
    if firstTime:
        app.selectedFormation = app.singleBack

    app.singleBackOriginalLocations = copy.deepcopy(app.singleBack)
    app.shotgunOriginalLocations = copy.deepcopy(app.shotgun)
    app.spreadOriginalLocations = copy.deepcopy(app.spread)
    app.bunchOriginalLocations = copy.deepcopy(app.bunch)
    app.oFormation = app.selectedFormation

    app.ball = Ball(app.oFormation['C'].cx,app.oFormation['C'].cy,app.oFormation['C'])
                        #target x and target y are self location

def loadOffensiveRoutes(app):
    #Routes are in (yards, dx, dy) format where yards are steps.
    #'Left/Right' is the starting location relative to center of field
    #RB routes start with 'rb'
    crossingLeft = [(10, -20), (20, -10)]
    crossingRight = [(-10, -20), (-20, -10)]

    slantLeft = [(0, -5), (15, -15)]
    slantRight = [(0, -5), (-15, -15)]

    quickOutLeft = [(0, -3), (-8, 0)]
    quickOutRight = [(0, -3), (8, 0)]  # ((3, 0, -3), (8, 3, 0))

    shallowDigLeft = [(0, -5), (15, 0)]
    shallowDigRight = [(0, -5), (-15, 0)]
    deepDigLeft = [(0, -10), (15, 0)]
    deepDigRight = [(0, -10), (-15, 0)]

    shallowOutLeft = [(0, -5), (-8, 0)]
    shallowOutRight = [(0, -5), (8, 0)]
    deepOutLeft = [(0, -10), (-8, 0)]
    deepOutRight = [(0, -10), (8, 0)]

    shallowHitchLeft = [(0, -8), (2, 2)]
    shallowHitchRight = [(0, -8), (2, -2)]
    deepHitchLeft = [(0, -12), (2, 2)]
    deepHitchRight = [(0, -12), (2, -2)]

    postLeft = [(0, -12), (5, -10)]
    postRight = [(0, -12), (15, -5 - 10)]
    cornerLeft = [(0, -12), (-5, -10)]
    cornerRight = [(0, -12), (5, -10)]

    go = [(0, -20), (0, -20)]

    rbOutLeft = [(-10, -5), (0, -20)]
    rbOutRight = [(10, -5), (0, -20)]
    rbZoneSit = [(0, -10), (0, 0)]

   
    app.wrRouteList= [crossingLeft, crossingRight, slantLeft, slantRight,
                    quickOutLeft, quickOutRight, shallowDigLeft,
                    shallowDigRight, deepDigLeft, deepDigRight,
                    shallowOutLeft, shallowOutRight, deepOutLeft,  
                    deepOutRight, shallowHitchLeft, shallowHitchRight,
                    deepHitchLeft, deepHitchRight, postLeft, postRight,
                    cornerLeft, cornerRight, go]
    app.rbRouteList = [rbOutRight, rbOutLeft, rbZoneSit]
    
    app.route = go  #Default route
   
def loadOffensivePlayerRoutes(app):
    for position in app.oFormation:
        player = app.oFormation[position]
        if isinstance(player, WideReceiver) or isinstance(player, TightEnd):
            randomRoute = random.randrange(len(app.wrRouteList))
            
            player.route = player.translateRoute(app, app.route) #app.rbRouteList[randomRoute]
            player.goToPoint(app)
        elif isinstance(player, RunningBack):
            route = app.rbRouteList[0] #Default to zone sit
            player.route = player.translateRoute(app, route) #app.rbRouteList[randomRoute]
            player.goToPoint(app)
            # randomRoute = random.randrange(len(app.rbRouteList))
            # player.route = app.route #app.rbRouteList[randomRoute]
            # targetX = player.cx + player.route.x1*app.yardStep
            # targetY = player.cy + player.route.y1*app.yardStep
            # player.dx, player.dy = goToPoint(app)

#Initialize Defense  
def loadDefensiveFormations(app):
    loadZones(app)
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
    rbLocations = getRBLocations(app)
    coverOne = dict()
    #Map a CB/LB to a WR/TE
    for i in range(len(wrLocations)):
        wr = wrLocations[i]
        cornerBack = f"CB{i+1}"
        coverOne[cornerBack] = CornerBack(wr.cx,
                    app.lineOfScrimmage-(wr.cy-app.lineOfScrimmage),
                    dx, dy, wr)
    
    
    #Assign LBs to RBs and TEs
    numLBs = 6-len(wrLocations)
    numCoverLBs = len(teLocations) + len(rbLocations)
    numZoneLBs = numLBs-numCoverLBs
    for i in range(numZoneLBs):
        linebacker = f"LB{i+1}"
        zone = app.zones["middleIntermediate"]
        coverOne[linebacker] = LineBacker(0,0,0,0, None, zone)
    
    for i in range(len(rbLocations)):
        rb = rbLocations[i]
        lineBacker = f"LB{i+1 + numZoneLBs}"
        coverOne[lineBacker] = LineBacker(rb.cx,
                app.lineOfScrimmage-(rb.cy-app.lineOfScrimmage+10),
                dx, dy, rb)
        
    numRBs = len(rbLocations)
        
    for i in range(len(teLocations)):
        te = teLocations[i]
        lineBacker = f"LB{i+1+numRBs+numZoneLBs}"
        coverOne[lineBacker] = LineBacker(te.cx,
                app.lineOfScrimmage-(te.cy-app.lineOfScrimmage+10),
                dx, dy, te)
    totalLBs = numZoneLBs + numRBs #not coutning TEs

    for i in range(totalLBs):
        linebacker = coverOne[f"LB{i+1}"]
        #Evenly distribute LBs not gaurding TEs between hash marks
        xCord = 2*app.width//5 + (i+1)*(app.width//5)//(totalLBs+1)
        linebacker.cx,linebacker.cy = xCord, app.lineOfScrimmage - app.yardStep*4
    toUnionCoverOne = {'DE1': DefensiveEnd(app.width*205/500, app.lineOfScrimmage-10, dx, dy),
                       'DE2': DefensiveEnd(app.width*293/500, app.lineOfScrimmage-10, dx, dy),
                       'DT1': DefensiveTackle(app.width*238/500, app.lineOfScrimmage-10, dx, dy),
                       'DT2': DefensiveTackle(app.width*263/500, app.lineOfScrimmage-10, dx, dy),
                       'S': Safety(app.width//2, 
                                   app.lineOfScrimmage-app.yardStep*12, dx, dy, 
                                   None, app.zones['middleDeep'])
                       }
    coverOne |= toUnionCoverOne
    return coverOne
def loadZones(app):
    fieldLeft = 30 #change this
    fieldRight = app.width - 30
    fieldWidth = (app.width - 60) #in pixels
    zones = dict()       #(left, right, top, bottom, cx, cy) in pixels
                                        
    
    zones['middleDeep'] = Zone(fieldWidth/5 + fieldLeft, 
                                       fieldRight - fieldWidth/5,  0, 
                                        app.lineOfScrimmage - 10*app.yardStep, 
                                        fieldWidth//2 + fieldLeft, 
                                        app.lineOfScrimmage - 15*app.yardStep)
    
    zones['middleIntermediate'] = Zone(fieldWidth//3 + fieldLeft, 
                                       fieldRight- fieldWidth//3,
                                        app.lineOfScrimmage - 9*app.yardStep, 
                                        app.lineOfScrimmage - 3*app.yardStep)
    # zones['leftIntermediate'] = Zone( fieldWidth//4 + 30, app.lineOfScrimmage - 6)
    # zones['rightIntermediate'] = Zone( 3*fieldWidth//4 + 30, app.lineOfScrimmage - 6)
    # zones['leftDeep'] = Zone(fieldWidth//4+30, app.lineOfScrimmage - 12) 
    # zones['rightDeep'] = Zone(3*fieldWidth//4+30, app.lineOfScrimmage - 12)
    
    app.zones = zones
    
    
#returns a list of WR Coords  
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
def getRBLocations(app):
    rbLocations = []
    for position in app.oFormation:
        player = app.oFormation[position]
        if isinstance(player, RunningBack):
            rbLocations.append(player)
    return rbLocations
def redrawAll(app):
    if app.isField:
        if app.playResult != '':
            menuHeight = 70
            margin = 50
            left = margin
            width = app.width - margin*2
            top = app.height/2 - menuHeight/2
            drawRect(left, top, width, menuHeight, 
                fill=rgb(20,20,20), border='black', opacity=85)
            if app.playResult == 'tackled':
                yardsGained = int((app.lineOfScrimmage - 
                                app.ball.carrier.cy)/app.yardStep)
                drawLabel(f"Play Result: tackled after {yardsGained} yards", 
                        left+width/2, top + 20, size=20, fill='white', 
                        align='center')
            else:
                drawLabel(f"Play Result: {app.playResult}", left+width/2, 
                top + 20, size=20, fill='white', align='center')
            drawLabel(f"Press R to Reset", left+width/2, 
                top + 50, size=15, fill='white', align='center')
        drawField(app)
        drawSideline(app)
        drawFieldButtons(app)
        drawOffense(app)
        drawDefense(app)
        drawLabel("Click mouse", app.sideLineOffset//2-30, 
                    app.height//2+100, size=22)
        drawLabel("to throw", app.sideLineOffset//2-30, 
                    app.height//2+120, size=22)
        app.exportButton.draw()
        app.ball.drawBall(app)
        if app.throwing:
            drawCircle(app.mouseX, app.mouseY, app.ballVelocity*3, fill='yellow')
        # drawLabel('ball height' + str(app.ball.height), 300, 300, size=22, 
        #       fill='black', align='left')
        if app.isPaused:
            drawControlsMenu(app)
    elif app.isMainMenu:
        drawMainMenu(app)
    elif app.isOffensiveMenu:
        drawOffensiveMenu(app)
        # targetX, targetY = getBallPlacement(app.oFormation['TE'], app)
        # drawCircle(targetX, targetY, 5, fill='brown')
    #drawLabel(f"{app.yardsRan}", 200, 200, size=40) Debugging
    
        
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


def drawDefense(app):
    offset = 0
    if app.ball.cy <= 10*app.yardStep:
        offset = 10*app.yardStep - app.ball.cy
    for position in app.dFormation:
        player = app.dFormation[position]
        cy = player.cy + offset
        if cy<0 or cy > app.height:
            continue
        drawCircle(player.cx, cy, 13,
                    fill='white', border='black')

def drawOffense(app):
    offset = 0
    customComplimentRed = rgb(215, 80, 75)
    deepRed = rgb(180, 30, 50)
    if app.ball.cy <= 10*app.yardStep:
        offset = 10*app.yardStep - app.ball.cy
    for position in app.oFormation:
        player = app.oFormation[position]
        color = customComplimentRed
        if app.selectedPlayer == position and app.isOffensiveMenu:
            color = deepRed
        cy = player.cy + offset
        if cy<0 or cy > app.height:
            continue
        drawCircle(player.cx, cy, 13,
                    fill=color, border='black')
        # velo = (player.dx**2 + player.dy**2)**0.5
        # drawLabel(f"{(velo)}", player.cx, player.cy, size=10)
        if isinstance(player, SkillPlayer):
            #player.drawVelocity(app)
            if not app.playIsActive:
                player.drawRoute(app)

def drawFieldOld(app):
    customGreen = rgb(27, 150, 85)
    tenCount=1
    fiveCount=0
    offset = 0
    if app.ball.cy <= 10*app.yardStep:
        offset = 10*app.yardStep - app.ball.cy # also subtract ball carrier dy from everyones cy 
    drawRect(0, 0, app.width, app.height, fill=customGreen)
    #Draw Yard Lines
    goalLine = app.lineOfScrimmage-app.yardStep*85
    for i in range(app.height, goalLine, -app.yardStep):
        #Make it long yard line every 5 yards
        i += offset
        fiveCount+=1
        if i < 0 or i > app.height:
            if fiveCount%10==0:
                tenCount+=1
            continue
        if fiveCount%5==0:
            drawLine(30, i, app.width-30, i, fill='white')
            if fiveCount%10==0:
                drawLabel(f'{tenCount} 0', 60, i,
                        size=20, fill='white', rotateAngle=90)
                drawLabel(f'{tenCount} 0', app.width-60, i,
                        size=20, fill='white', rotateAngle=270)
                tenCount+=1
        else:
            drawLine(30, i, 40, i, fill='white')
            drawLine(app.width-30, i, app.width-40, i, fill='white')
            drawLine(2*app.width//5, i, 2*app.width//5+10, i, fill='white')
            drawLine(3*app.width//5, i, 3*app.width//5+10, i, fill='white')
    # what is this?
    drawLine(20, app.height-(app.yardStep*14) + offset, app.width-20,
            app.height-(app.yardStep*14)+offset, fill='blue')
    drawLine(20, 0, 20, app.height,
            fill='white', lineWidth=4)
    drawLine(app.width-20, 0, app.width-20, app.height,
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
        

def drawFieldButtons(app):
    for button in app.fieldButtons:
        button.draw()
 
def drawControlsMenu(app):
    menuHeight = 130
    margin = 7
    left = margin
    width = app.width - margin*2
    top = app.height - menuHeight - margin

    # translucent background so it doesn't block much of the field
    
    drawRect(left, top, width, menuHeight, 
             fill=rgb(20,20,20), border='black', opacity=85)

    textLeft = left + 10
    lineY = top + 14
    lineSpacing = 30

    drawLabel("General Controls:", textLeft, lineY, size=12, fill='white', align='left')
    
    drawLabel("P: Pause/Resume    Space: Step once    R: Reset", textLeft+100, 
              lineY, size=15, fill='white', align='left')
    
    # drawLabel("Mouse:", textLeft, lineY + lineSpacing, size=12, fill='white', 
    #           align='left')
    drawLabel("Click a player to select/deselect. " \
                "Drag to edit selected player's route", 
              textLeft + 10, lineY + lineSpacing, size=15, fill='white', 
              align='left')
    drawLabel("Gameplay Controls:", textLeft, lineY + lineSpacing*2, 
              size=12, fill='white', align='left')
    drawLabel("Click and hold to throw ball. " \
                "Hold longer for faster throw", 
              textLeft + 50, lineY + lineSpacing*3, size=15, 
              fill='white', align='left')

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
    #drawRoutes(app)
    drawOffense(app)


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
    
#### Moving Logic ####
def moveOffense(app):
    for position in app.oFormation:
        player = app.oFormation[position]
        if player == app.ball.carrier and not isinstance(player, Lineman):
            player.goToPoint(app)
            player.movePlayer(app)
        elif isinstance(player, Quarterback):
            player.targetX = player.cx
            player.targetY = app.lineOfScrimmage + app.yardStep*3
            player.goToPoint(app)
            player.cx += player.dx
            player.cy += player.dy
        elif isinstance(player, SkillPlayer): #or \
        #    isinstance(app.oFormation[position], TightEnd) or \
        #    isinstance(app.oFormation[position], RunningBack):
            if (app.ball.targetX != None and app.ball.targetY != None 
                and not app.ball.beingSnapped):
                player.trackBall(app)
            elif app.ball.carrier == app.oFormation['QB']:
                player.runRoute(app)
            elif player == app.ball.carrier:
                player.runWithBall(app)
            else:
                player.block(app)

            # step1Length = ((player.route.x1 - player.cx)**2 + (player.route.y1 - player.cy)**2)**0.5
            # step2Length = ((player.route.x2-player.cx)**2 + (player.route.y2-player.cy)**2)**0.5
            
            # if  step1Length <= app.yardsRan * app.yardStep:
            #     if  step1Length + step2Length <= app.yardsRan * app.yardStep:
            #         player.dx, player.dy = 0, 0
            #         #print('None')
            #     else:
            #         targetX = player.route.x2
            #         targetY = player.route.y2
            #         player.dx, player.dy = goToPoint(app,player,targetX, targetY)
                    
            # else:  
            #     targetX =player.route.x1
            #     targetY = player.route.y1
            #     player.dx, player.dy = goToPoint(app,player,targetX, targetY)
            # player.cx+=player.dx
            # player.cy+=player.dy
            # if player.cx <= 24:
            #     player.cx = 24
            # elif player.cx >= app.width-24:
            #     player.cx = app.width-24

            #print(player, cx, cy, dx, dy, player.route)
def moveDefense(app):

    for position in app.dFormation:
        player = app.dFormation[position]
        if isinstance(player, CoverPlayer):
            if (app.ball.targetX != None and app.ball.targetY != None 
                and not app.ball.beingSnapped):
                player.trackBall(app)
            elif (app.ball.carrier == app.oFormation['QB'] and 
                  app.oFormation['QB'].cy > app.lineOfScrimmage
                  or app.ball.beingSnapped):
                player.guardMan(app)
            else: # try to tackle him
                player.stopPlayer(app, app.ball.carrier)
                player.checkTackle(app)
        elif isinstance(player, PassRusher):
            player.rushQB(app)
            if app.ball.carrier == app.oFormation['QB']:
                player.checkTackle(app)

            # targetX, targetY = getBallPlacement(player.man, app)
            # player.dx, player.dy = goToPoint(app,player,targetX, targetY)
            # player.cx += player.dx
            # player.cy += player.dy
            # if player.cx <= 24:
            #     player.cx = 24
            # elif player.cx >= app.width-24:
            #     player.cx = app.width-24
def getBallPlacement(target, app):
    #Assumes target is a WideReceiver, TightEnd, or RunningBack
    #Find self
    for position in app.oFormation:
        player = app.oFormation[position]
        if isinstance(player, Quarterback):
            self = player
            break
    ballVelo=app.velocity*3
    playerVelo = (target.dx**2 + target.dy**2)**0.5
    vRatio=playerVelo/ballVelo
    C = distance(self.cx, self.cy, target.cx, target.cy)
    _, targetAngle = getRadiusAndAngleToEndpoint(0, 0, 
                                                   target.dx, target.dy)
    _, angleToTarget = getRadiusAndAngleToEndpoint(target.cx, target.cy, 
                                               self.cx, self.cy)
    angleDifference = (targetAngle - angleToTarget) % 360
    sinTheta = math.sin(math.radians(angleDifference))
    playerAngle = math.degrees(math.asin(sinTheta * vRatio)) % 360
    ballAngle= 180-(angleDifference + playerAngle)
    Point = math.sin(math.radians(ballAngle))
    if Point == 0:
        Point = 0.0001
    throwDistance = (C * sinTheta) / Point
    throwAngle = (angleToTarget - 180) - playerAngle

    ballX, ballY = getRadiusEndpoint(self.cx, self.cy, throwDistance, throwAngle)
    #put the tartget slightly in front of the target
    ballDistanceToself = distance(self.cx, self.cy, ballX, ballY)
    if (self.cx == ballX) and (self.cy == ballY):
        return ballX, ballY
    ballToselfX =  (self.cx - ballX)/ballDistanceToself 
    ballToselfY = (self.cy - ballY)/ballDistanceToself
    correctedX = ballX + ballToselfX * app.yardStep*0.5
    correctedY = ballY + ballToselfY * app.yardStep*0.5
    return correctedX, correctedY
def getRadiusEndpoint(cx, cy, r, theta):
    return (cx + r*math.cos(math.radians(theta)),
            cy - r*math.sin(math.radians(theta)))
def getRadiusAndAngleToEndpoint(cx, cy, targetX, targetY):
    radius = distance(cx, cy, targetX, targetY)
    angle = math.degrees(math.atan2(cy-targetY, targetX-cx)) % 360
    return (radius, angle)

def distance(x1, y1, x2, y2):
    return ((x2 - x1)**2 + (y2 - y1)**2)**0.5
def onStep(app):
    if app.isPaused:
        return
    elif app.isField:
        takeStep(app)

def takeStep(app):
    #print(app.ball.carrier)
    #app.getTextInput()
    app.steps+=1
    app.playIsActive = True
    if app.throwing:
        app.ballVelocity += 0.3
        if app.ballVelocity >= app.maxBallVelo:
            app.ballVelocity = app.maxBallVelo
    app.yardsRan = (app.velocity * app.steps)/app.yardStep
    if app.playResult == '':
        moveDefense(app)
        moveOffense(app)
        handleCollisions(app)
    else: 
        app.throwing = False
    app.ball.updateBallPosition(app)

    
def correctPlayers(app):
    offset = 10*app.yardStep - app.ball.carrier.cy
    players = list(app.oFormation.values()) + list(app.dFormation.values())
    for player in players:
        player.cy += offset
    
def moveQB(app):
    self = app.oFormation['QB']
    self.targetX = 10#self.cx
    self.targetY = 10#app.lineOfScrimmage + app.yardStep*3
    self.goToPoint(app)
    self.cx += self.dx
    self.cy += self.dy

### Mouse Functions ###
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
    elif app.isField:
        checkFieldButtons(app, mx, my)
    if (app.playIsActive and app.ball.carrier == app.oFormation['QB'] 
        and app.playResult == '' and app.isField):
        app.ballVelocity = 1
        app.throwing = True
        app.mouseX = mx
        app.mouseY = my
    elif app.isOffensiveMenu:
        if app.importButton.isClicked(mx, my):
            #importData(app)
            pass
        for button in app.offensiveFormationButtons:
            if button.isClicked(mx, my):
                app.selectedFormation = button.formation
                app.oFormation = copy.deepcopy(app.selectedFormation)
                app.selectedPlayer = None
        if app.isWRMenu:
            for button in app.offensiveWRRouteButtons:
                if button.isClicked(mx, my):
                    if app.selectedPlayer==None: return
                    player = app.oFormation[app.selectedPlayer]
                    if player.cx<=app.width//2:
                        player.route = player.translateRoute(app, button.leftRoute)
                    else:
                        player.route = player.translateRoute(app, button.rightRoute)
        else:
            for button in app.offensiveRBRouteButtons:
                if button.isClicked(mx, my):
                    if app.selectedPlayer==None: return
                    player = app.oFormation[app.selectedPlayer]
                    if player.cx<=app.width//2:
                        player.route = player.translateRoute(app, button.leftRoute)
                    else:
                        player.route = player.translateRoute(app, button.rightRoute)
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
            app.isField = True
            app.isOffensiveMenu = False
            app.selectedPlayer = None
            app.dFormation = initializeCoverOne(app)
            app.isPlayActive = False

def checkFieldButtons(app, mx, my):
    if (app.exportButton.text == "Export Play" and 
            app.exportButton.isClicked(mx, my)):
        #exportData(app)
        pass
    for button in app.fieldButtons:
        if button.isClicked(mx, my):
            if button.text == 'Reset':
                app.isPlayActive = False
                resetApp(app)
                return
            else:
                app.importButton.text = "Import Play"
                app.isPlayActive = False
                resetApp(app)
                app.isField = False
                app.isOffensiveMenu = True
                return

def onMouseDrag(app, mouseX, mouseY):
    if app.isOffensiveMenu and app.selectedPlayer != None:
        player = app.oFormation[app.selectedPlayer]
        player.route += [(mouseX, mouseY)]
        if player.clickInPlayer(mouseX,mouseY):
            startX = player.startX
            startY = player.startY
            player.route = [(startX, startY),(mouseX, mouseY)]
    if app.isField and app.throwing:
        app.mouseX = mouseX
        app.mouseY = mouseY
    
def onMouseRelease(app, mouseX, mouseY):
    if app.throwing:
        app.throwing = False
        app.ball.throwToTarget(mouseX, mouseY, app)

def handleCollisions(app):
    players = list(app.oFormation.values()) + list(app.dFormation.values())
    r1 = r2 = 10  # radius of players
    for i in range(len(players)):
        for j in range(i+1, len(players)):
            p1 = players[i]
            p2 = players[j]
            xDiff = p2.cx - p1.cx
            yDiff = p2.cy - p1.cy
            dist = distance(p1.cx, p1.cy, p2.cx, p2.cy)
            if dist == 0:
                xDiff = 0.01
                yDiff = 0.01
                dist = distance(0,0,xDiff,yDiff)
            overlap = (r1 + r2) - dist
            
            if overlap > 7:  # collision detected
                nx, ny = xDiff/dist, yDiff/dist
                correction = 0.5
            
                p1.cx -= nx * correction 
                p1.cy -= ny * correction 
                p2.cx += nx * correction 
                p2.cy += ny * correction 

### Data Functions ###
  
# def importData(app):
#     print('importing')
#     app.dataPath = app.getTextInput('Input Play File Path')
#     try: 
#         with open(app.dataPath, 'r') as file:
#             formation = json.load(file)
#     except FileNotFoundError:
#         app.importButton.text = "File Not Found"
#         print('Invalid File')
#         return
#     if not isinstance(formation, dict): 
#         print('Error: Invalid Player Data')
#         return
#     formationRes = dict()
#     for position in formation:
#         if "WR" in position or "RB" in position or "TE" in position:
#             isLegal = checkLegalSkillPlayer(formation, position)
#             if not isLegal:
#                 app.importButton.text = "Invalid Data"
#                 print('Error: Invalid Skill Player Data')
#                 return
#             playerInfo = formation[position]
#             route = Route((playerInfo["routeDX1"], 
#                         playerInfo["routeDY1"]),
#                         (playerInfo["routeDX2"],
#                         playerInfo["routeDY2"]))
#             if "WR" in position:
#                 formationRes[position] = WideReceiver(playerInfo["cx"],
#                             playerInfo["cy"],playerInfo["dx"], 
#                             playerInfo["dy"], route)
#             elif "RB" in position:
#                 formationRes[position] = RunningBack(playerInfo["cx"],
#                             playerInfo["cy"],playerInfo["dx"], 
#                             playerInfo["dy"], route)
#             elif "TE" in position:
#                 formationRes[position] = TightEnd(playerInfo["cx"],
#                             playerInfo["cy"],playerInfo["dx"], 
#                             playerInfo["dy"], route)
#         else:
#             isLegal = checkLegalNormalPlayer(formation, position)
#             if not isLegal:
#                 app.importButton.text = "Invalid Data"
#                 print('Error: Invalid Normal Player Data')
#                 return
#             playerInfo = formation[position]
#             if "QB" in position:
#                 formationRes[position] = Quarterback(playerInfo["cx"],
#                             playerInfo["cy"], playerInfo["dx"], 
#                             playerInfo["dy"])
#             else:
#                 formationRes[position] = Lineman(playerInfo["cx"],
#                             playerInfo["cy"],playerInfo["dx"], 
#                             playerInfo["dy"])
#     app.importButton.text = "Imported!"
#     app.oFormation = formationRes

# def checkLegalSkillPlayer(formation, position):
#     playerInfo = formation[position]
#     return ("cx" in playerInfo and "cy" in playerInfo and 
#             "dx" in playerInfo and "dy" in playerInfo and
#             "routeDX1" in playerInfo and "routeDY1" in playerInfo and 
#             "routeDX2" in playerInfo and "routeDY2" in playerInfo and
#             len(formation[position]) == 8)

# def checkLegalNormalPlayer(formation, position):
#     playerInfo = formation[position]
#     return ("cx" in playerInfo and "cy" in playerInfo and 
#             "dx" in playerInfo and "dy" in playerInfo and
#             len(formation[position]) == 4)

# def exportData(app):
#     resetApp(app)
#     playDict = dict()
#     dx = dy = 0
#     for position in app.oFormation:
#         player = app.oFormation[position]
#         if "WR" in position or "RB" in position or "TE" in position:
#             playDict[position] = {"cx": player.cx, "cy":player.cy, 
#                                 "dx": dx, "dy":dy, 
#                                 "routeDX1": player.route.x1, 
#                                 "routeDY1": player.route.y1, 
#                                 "routeDX2": player.route.x2,  
#                                 "routeDY2": player.route.y2}
#         else:
#             playDict[position] = {"cx": player.cx, "cy":player.cy, 
#                                 "dx": dx, "dy":dy}
#     with open(f"routeLabPlay{app.indexExport}.json", "w") as file:
#         json.dump(playDict, file, indent=2)
#     app.indexExport+=1
#     app.exportButton.text = "Exported!"

                
def main():
    runApp()
main()