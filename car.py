from cmu_112_graphics import *
from helper import *
from button import *

import random, time
from pygame import mixer

class Car:
    def __init__(self, app, name, x, y, color, image, logo, angle=-170,
                 score=0, laps=1, checkpointRank=0, racing=True):
        self.app = app
        # car info
        self.name = name
        self.color = color
        # position vars
        self.x = x
        self.y = y
        self.vx = 0         # x velocity
        self.vy = 0         # y velocity
        self.angle = angle
        self.position = []
        self.updateCarRectangle()
        # movement vars
        self.rotating = False
        self.rotation = 0
        self.accelerating = False
        self.maxSpeed = 30
        # collision vars
        self.lineIntersected = None
        self.inCollision = False
        self.xWall, self.yWall = None, None
        self.collisionType = "None"
        self.collidedCar = None
        self.trackPoints = app.map.gameMap
        # scoring
        self.checkpoint = None
        self.visitedCheckpoints = []
        self.trackWidth = 400
        self.score = score
        self.laps = laps
        self.checkpointRank = checkpointRank
        self.racing = racing
        self.raceTime = time.time()
        self.image = image
        self.logo = logo

    # draws car on canvas
    def draw(self, app, canvas):
        # bounding box:
        # canvas.create_polygon(self.position, fill=self.color)
        # car image: 
        carImage = ImageTk.PhotoImage(self.image.rotate(-self.angle, 
                                                        expand=True)) 
        canvas.create_image(self.x, self.y, image=carImage)

    # updates car position
    def move(self, app):
        # collision check
        self.collision(app)
        # update movement variables
        if not self.inCollision:
            self.movement()
        # updates position
        self.x, self.y = self.updateCarCenter(self.angle, self.x, self.y, 
                                              self.vx, self.vy)
        self.updateCarRectangle()
        # adds friction
        self.friction()
    
    def movement(self):
        if self.accelerating:
            if self.vx < self.maxSpeed: self.vx += 1
            if self.vy < self.maxSpeed: self.vy += 1
        if self.rotating: 
            if self.angle + self.rotation > 180: self.angle = -178
            elif self.angle + self.rotation < -178: self.angle = 180
            else: self.angle += self.rotation
    
    ##########################
    # CALCULATING CAR POSITION
    
    # creates and rotates car rectangle based on center
    def updateCarRectangle(self):
        l, w = 12, 24
        topLeft = (self.x-w, self.y-l)
        topRight = (self.x+w, self.y-l)
        bottomRight = (self.x+w, self.y+l)
        bottomLeft = (self.x-w, self.y+l)
        self.position = [topLeft, topRight, bottomRight, bottomLeft]
        self.position = rotatePolygon(self.position, (self.x, self.y), 
                                      self.angle)

    # calculates new position of car
    def updateCarCenter(self, angle, x, y, vx, vy):
        x += math.cos(math.radians(angle)) * vx 
        y += math.sin(math.radians(angle)) * vy 
        return x, y

    ###################
    # COLLISION PHYSICS

    def collision(self, app):
        if self.touchingObject(app):
            # play crash sound if player collided
            if isinstance(self, Player):
                self.playCrashSound()
            # get points of the line the car is intersecting
            ((x1, y1), (x2, y2)) = (self.lineIntersected[0], 
                                    self.lineIntersected[1])
            dx = x1 - x2
            dy = y1 - y2
            # calculate new angle and velocity after collision
            if self.collisionType == "Car":
                self.collisionAngle(dx, dy)
            self.collisionVelocity(dx, dy)
    
    def playCrashSound(self):
        mixer.music.load("sounds/carCrash.wav")
        mixer.music.set_volume(0.1)
        mixer.music.play()
    
    ###############################################################
    # ANGLE AFTER REFLECTION
    # treat collision as bouncing off a flat surface with the angle
    # of the tangent at the point of contact
    ###############################################################
    def collisionAngle(self, dx, dy):
        tangent = math.atan2(dy, dx)
        self.angle = 2 * tangent - self.angle
        self.collidedCar.angle = 2 * tangent - self.collidedCar.angle
        # account for existing overlap when collision detected
        a = 0.5 * math.pi + tangent
        self.x += math.sin(a)
        self.y -= math.cos(a)
        self.collidedCar.x -= math.sin(a)
        self.collidedCar.y += math.cos(a)
    
    ######################################################
    # REFLECTION OF VECTOR 
    # Uses formula provided by the Phong Reflection Model
    # https://en.wikipedia.org/wiki/Phong_reflection_model
    ######################################################
    def collisionVelocity(self, dx, dy):
        # find angle of reflecting surface 
        angle = math.atan2(dy, dx)
        # find surface normal
        nx, ny = self.lineNormal(angle)
        # find dot product of car vector and surface normal
        dot = self.vx * nx + self.vy * ny 
        # find reflection vector
        self.vx = self.vx - 2 * dot * nx
        self.vy = self.vy - 2 * dot * ny
        # add elasticity
        self.vx *= 0.5
        self.vy *= 0.5

    # finds normal vector of line
    def lineNormal(self, angle):
        d = math.degrees(angle)
        if (-180 < d and d < -90) or (0 < d and d < 90): nx = math.sin(angle)
        elif (-90 < d and d < 0) or (90 < d and d < 180): nx = -math.sin(angle)
        else: nx = -math.sin(angle)
        ny = math.cos(angle)
        return nx, ny
    
    ########################
    # CHECKING FOR COLLISION
    ########################
    
    # finds which object the car is touching
    def touchingObject(self, app):
        if self.inCollision:
            self.stillInCollsion(app)
            return False
        else:
            # check if car is touching any other cars or walls
            return self.inCarCollision(app) or self.inWallCollision(app)
    
    def stillInCollsion(self, app):
        # if the car is touching another object, check if it is still touching
        if self.collisionType == "Car":
            if not self.carIntersectLine(app, self.position, 
                                         self.collidedCar.position):
                self.inCollision = False
        else:
            # loop through wall list and find intersection
            if not self.carIntersectLine(app, self.position, 
                                         self.lineIntersected):
                self.inCollision = False
    
    # returns True is car is colliding with another car
    def inCarCollision(self, app):
        for car in app.cars:
            if (car.name != self.name and 
                self.carIntersectLine(app, self.position, car.position)):
                self.collisionType = "Car"
                self.collidedCar = car
                return True
        return False
    
    # returns True if car is colliding with a wall
    def inWallCollision(self, app):
        if (self.carIntersectLine(app, self.position, app.map.interiorWall) or
            self.carIntersectLine(app, self.position, app.map.exteriorWall)):
            self.collisionType = "Wall"
            return True
        return False

    # returns True if car bounding box (4 line segments) is intersecting with
    # given line segments
    def carIntersectLine(self, app, carPoints, objectPoints):
        carLines = getPairs(carPoints)
        objectLines = getPairs(objectPoints)
        for objectLine in objectLines:
            for carLine in carLines:
                if (linesIntersect(carLine[0], carLine[1], 
                                   objectLine[0], objectLine[1])):
                    (line1, line2) = (line(carLine[0], carLine[1]), 
                                      line(objectLine[0], objectLine[1]))
                    self.xWall, self.yWall = intersectionPoint(line1, line2)
                    self.lineIntersected = objectLine
                    self.inCollision = True
                    return True
        return False

    #################
    # CAR CHECKPOINTS
    
    # creates checkpoints at track vertices to guide car
    def checkpoints(self, app):
        for i in range(len(self.trackPoints)):
            # after car reaches checkpoint changes to next checkpoint
            atCheckpoint = False
            if (distance((self.x, self.y), self.trackPoints[i]) < 
                self.trackWidth):
                # if finished lap
                if len(self.visitedCheckpoints) == len(self.trackPoints)-1:
                    self.visitedCheckpoints = []
                # checkpoint not already visited in lap    
                if self.trackPoints[i] not in self.visitedCheckpoints:
                    atCheckpoint = True
                    self.atNewCheckpoint(app, i)

                # if car finishes lap
                if (self.score >= len(self.trackPoints) and 
                    self.trackPoints[i] == self.trackPoints[0] and 
                    atCheckpoint):
                    self.finishedLap(app)
                    # laps only increase on first contact, not continously
                    atCheckpoint = False
    
    # if at new checkpoint change goal to next checkpoint
    def atNewCheckpoint(self, app, trackPointIndex):
        self.visitedCheckpoints.append(self.trackPoints[trackPointIndex])
        if trackPointIndex+1 > len(self.trackPoints)-1:
            self.checkpoint = self.trackPoints[0]
        else:
            self.checkpoint = self.trackPoints[trackPointIndex+1]
        # increases car score for reaching checkpoint
        self.score += 1
        # checkpoint ranking: if cars have same score ranks by order of arrival
        self.checkpointRank = 0
        for car in app.cars:
            if self.name != car.name and self.score == car.score:
                self.checkpointRank += 1
    
    # if car finishes lap
    def finishedLap(self, app):
        # if car finishes race calculate car's time
        if self.laps+1 == 2:
            self.raceTime = round(time.time() - self.raceTime, 2)
            self.racing = False
        else:
            self.laps += 1

    #################

    # adds friction to car velocity
    def friction(self):
        if self.vx > 0: self.vx -= 0.1
        elif self.vx < 0: self.vx += 0.1
        if self.vy > 0: self.vy -= 0.1
        elif self.vy < 0: self.vy += 0.1
        

class Player(Car):
    def __init__(self, app, name, x, y, color, image, logo, angle=-170,
                 score=0, laps=1, checkpointRank=0, racing=True):
        super().__init__(app, name, x, y, color, image, logo, angle,
                         score, laps, checkpointRank, racing)
        # scrolling
        self.xOldPos = 640 # ? offset of camera to stay center
        self.yOldPos = 360
        self.xCamera = 640
        self.yCamera = 360
        self.centralizedPoints = self.alignMapPoints(app.map.miniMap)
        self.rankings = []
        self.xShift = 0
        self.yShift = 0
        
        # loading shift
        self.loadX = 0
        self.loadY = 0
        self.loading = False
    
    # player controls
    def pressedW(self): self.accelerating = True
    def pressedA(self): self.rotating = True; self.rotation = -5
    def pressedD(self): self.rotating = True; self.rotation = 5
    def releasedW(self): self.accelerating = False
    def releasedA(self): self.rotating = False
    def releasedD(self): self.rotating = False
    
    def gameLoaded(self, x, y):
        self.loadX = x
        self.loadY = y
        self.loading = True
    
    # draws player car
    def draw(self, app, canvas):
        if self.loading:
            canvas.xview_scroll(self.loadX, "units")
            canvas.yview_scroll(self.loadY, "units")
            self.loading = False
        # update camera view
        self.updateCamera(canvas)
        # player bounding box
        # canvas.create_polygon(self.position, fill=self.color)
        # draw player info
        self.drawHUD(app, canvas)
        # draw car image
        carImage = ImageTk.PhotoImage(self.image.rotate(-self.angle, 
                                                        expand=True)) 
        canvas.create_image(self.x, self.y, image=carImage)
    
    def updateCamera(self, canvas):
        # find difference between new and old car positions
        xDiff = int((self.x - self.xOldPos))
        yDiff = int((self.y - self.yOldPos))
        # updates camera position by adding difference
        self.xCamera += xDiff 
        self.yCamera += yDiff 
        canvas.xview_scroll(xDiff, "units") 
        canvas.yview_scroll(yDiff, "units") 
        # sets old position to current position
        self.xOldPos = self.x 
        self.yOldPos = self.y 
        # finds int rounding difference between car position and camera position
        xShift = int(self.x - self.xCamera)
        yShift = int(self.y - self.yCamera)
        # adds rounding difference to camera
        self.xCamera += xShift
        canvas.xview_scroll(xShift, "units") 
        self.yCamera += yShift
        canvas.yview_scroll(yShift, "units") 

        # keep track of total difference
        self.xShift += xDiff + xShift
        self.yShift += yDiff + yShift
    
    # draws player HUD
    def drawHUD(self, app, canvas):
        r = 5
        canvas.create_oval(self.xCamera-5, self.yCamera-5, 
                           self.xCamera+5, self.yCamera+5)
        # DISPLAY CAR STATS (DEBUG)
        # canvas.create_text(self.xCamera, self.yCamera+300, anchor="s",
        #                     text=f"Position: ({int(self.x)}, {int(self.y)}) \
        #                     Angle: {self.angle} \
        #                     Camera: ({self.xCamera},{self.yCamera})")
        self.drawMinimap(app, canvas)
        self.drawLeaderboard(app, canvas)
    
    # draws leaderboard of car rankings
    def drawLeaderboard(self, app, canvas):
        x, y = self.xCamera + 535, self.yCamera+100
        w = 90
        l = 150
        # draw rows with car info
        i = 0
        for car in app.cars:
            name  = car.name
            color = car.color
            
            row = ((x-w, y-l), (x+w, y+l-30*i))
            canvas.create_rectangle(row, fill=color, outline="black")
            # team name
            canvas.create_text((x-80, y+l - 30*(i+1)+8), 
                               text=f"{name}", fill="white", anchor="nw")
            # team logo
            logo = ImageTk.PhotoImage(app.scaleImage(car.logo, 0.06))
            canvas.create_image(x+70, y+l - 30*(i+1)+15, image=logo)
            i += 1
        # display leading lap
        leaderLap = app.cars[-1].laps
        canvas.create_rectangle(self.xCamera+445, self.yCamera-100,
                                self.xCamera+625, self.yCamera-50, 
                                fill="black")
        canvas.create_text(self.xCamera + 535, self.yCamera-85, 
                           text="Leaderboard", fill="white", font="Arial 11")
        canvas.create_text(self.xCamera + 535, self.yCamera-65, 
                           text=f"LAP {leaderLap}/1", fill="white", 
                           font="Arial 14 bold")

    def drawMinimap(self, app, canvas):
        # minimap background
        canvas.create_rectangle(self.xCamera + 340, self.yCamera-340,
                                self.xCamera + 625, self.yCamera-110,
                                fill="white", outline="black")
        canvas.create_rectangle(self.xCamera + 340, self.yCamera-340,
                                self.xCamera + 625, self.yCamera-295,
                                fill="black")
        # minimap text
        canvas.create_text(self.xCamera + 480, self.yCamera-325, text="Map", 
                           fill="white", font="Arial 11")
        canvas.create_text(self.xCamera + 480, self.yCamera-310, 
                           text="ALBERT PARK", fill="white", 
                           font="Arial 14 bold")
        # minimap track
        displayPoints = self.centralizeMapPoints(self.centralizedPoints)
        canvas.create_line(displayPoints, width=12, fill="black")
        canvas.create_line(displayPoints, width=10, fill="grey")
        # car icons on map
        for car in app.cars:
            if car.racing:
                mX, mY = car.x//33, car.y//33
                x = self.xCamera + mX + 290
                y = self.yCamera + mY - 340 + 45
                r = 5
                canvas.create_oval(x-r, y-r, x+r, y+r, fill=car.color)

    # transforms map by converting all points (x, y) into (cx+a, cy+b) where
    # cx and cy is a given point --> allows for map to be scaled and moved
    def centralizeMapPoints(self, centralizedPoints):
        displayPoints = []
        for (dx, dy) in centralizedPoints:
            x = self.xOldPos + dx - 350
            y = self.yOldPos + dy - 700 + 45
            displayPoints.append((x, y))
        return displayPoints
    
    # takes in transformed map and sets center to screen center, returns list of
    # drawable points
    def alignMapPoints(self, mapPoints):
        centralize = []
        for (x, y) in mapPoints:
            dx = self.xCamera + x
            dy = self.yCamera + y
            centralize.append((dx, dy))
        return centralize

class Enemy(Car):
    # enemy driving
    def selfDrive(self, app):
        if self.checkpoint == None:
            self.checkpoint = self.trackPoints[0]
        leftPos, rightPos = self.checkFuturePosition()
        # get future positions of car after left/right shift
        leftDist = distance(leftPos, self.checkpoint)
        rightDist = distance(rightPos, self.checkpoint)
        # checks whether moving left or right places the car closer to the next 
        # checkpoint
        # (distance must be signficant, to reduce wiggling)
        if leftDist - rightDist < -10:
            self.rotating = True
            self.rotation = -random.randint(3, 7)
        elif leftDist - rightDist > 10:
            self.rotating = True
            self.rotation = random.randint(3, 7)
        else:
            self.rotating = False
        self.accelerating = True
    
    # creates sensors: possible future positions of car after left/right shift
    def checkFuturePosition(self):
        left = self.updateCarCenter(self.angle-30, self.x, self.y, 50, 50)
        right = self.updateCarCenter(self.angle+30, self.x, self.y, 50, 50)
        return left, right
    
    # visualizes enemy self driving algorithm
    def visualizeSelfDrive(self, app, canvas):
        # draw checkpoints
        for point in self.trackPoints:
            x, y = point
            r = self.trackWidth
            if point in self.visitedCheckpoints:
                canvas.create_oval(x-r, y-r, x+r, y+r, outline="red", width=3)
            elif point == self.checkpoint:
                canvas.create_oval(x-r, y-r, x+r, y+r, outline="orange", 
                                   width=3)
            else:
                canvas.create_oval(x-r, y-r, x+r, y+r, outline="green", width=3)
        # draw sensors
        left = self.updateCarCenter(self.angle-30, self.x, self.y, 50, 50)
        right = self.updateCarCenter(self.angle+30, self.x, self.y, 50, 50)
        for x, y in (left, right):
            canvas.create_oval(x-1, y-1, x+1, y+1, fill="white")