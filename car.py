from helper import *
from button import *

import random

class Car:
    def __init__(self, app, name, x, y, color):
        self.app = app
        # car info
        self.name = name
        self.color = color
        # position vars
        self.x = x
        self.y = y
        self.vx = 0         # x velocity
        self.vy = 0         # y velocity
        self.angle = -170
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
        self.score = 0
        self.laps = 1
        self.checkpointRank = 0
        self.racing = True

    def draw(self, app, canvas):
        canvas.create_polygon(self.position, fill=self.color)
        # TODO: make explosion object for collision
        # if self.xWall and self.yWall:
        #     r = 5
        #     canvas.create_oval(self.xWall-r, self.yWall-r, 
        #                        self.xWall+r, self.yWall+r, fill="orange")
    
    def move(self, app):
        # checks if the car has collided with another object
        self.collision(app)
        # only responds to player input if not in collision
        if not self.inCollision:
            if self.accelerating:
                if self.vx < self.maxSpeed: self.vx += 1
                if self.vy < self.maxSpeed: self.vy += 1
            if self.rotating: 
                if self.angle + self.rotation > 180: self.angle = -178
                elif self.angle + self.rotation < -178: self.angle = 180
                else: self.angle += self.rotation
        # updates car position
        self.x, self.y = self.updateCarCenter(self.angle, self.x, self.y, self.vx, self.vy)
        self.updateCarRectangle()
        # adds friction to car movement
        self.friction()
    
    # * ########################
    # * CALCULATING CAR POSITION
    
    # creates and rotates car rectangle based on center
    def updateCarRectangle(self):
        l, w = 12, 24
        topLeft = (self.x-w, self.y-l)
        topRight = (self.x+w, self.y-l)
        bottomRight = (self.x+w, self.y+l)
        bottomLeft = (self.x-w, self.y+l)
        self.position = [topLeft, topRight, bottomRight, bottomLeft]
        self.position = rotatePolygon(self.position, (self.x, self.y), self.angle)
    
    # calculates new position of car
    def updateCarCenter(self, angle, x, y, vx, vy):
        x += math.cos(math.radians(angle)) * vx 
        y += math.sin(math.radians(angle)) * vy 
        return x, y
    
    # * #################
    # * COLLISION PHYSICS

    def collision(self, app):
        if self.touchingObject(app):
            # line car is touching
            (x1, y1), (x2, y2) = self.lineIntersected[0], self.lineIntersected[1]
            
            # * ANGLE AFTER REFLECTION
            # treat collision as bouncing off a flat surface with the angle
            # of the tangent at the point of contact
            if self.collisionType == "Car":
                dx = x1 - x2
                dy = y1 - y2
                tangent = math.atan2(dy, dx)
                self.angle = 2 * tangent - self.angle
                self.collidedCar.angle = 2 * tangent - self.collidedCar.angle
                # account for existing overlap when collision detected
                a = 0.5 * math.pi + tangent
                self.x += math.sin(a)
                self.y -= math.cos(a)
                self.collidedCar.x -= math.sin(a)
                self.collidedCar.y += math.cos(a)
            
            # * REFLECTION OF VECTOR 
            # * Uses formula provided by the Phong Reflection Model
            # * https://en.wikipedia.org/wiki/Phong_reflection_model
           
            # find angle of reflecting surface 
            rise, run = (y1-y2), (x1-x2)
            angle = math.atan2(rise, run)
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
    
    # * ######################      
    # * CHECKING FOR COLLISION
    
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
            if not self.carIntersectLine(app, self.position, self.collidedCar.position):
                self.inCollision = False
        else:
            # loop through wall list and find intersection
            if not self.carIntersectLine(app, self.position, self.lineIntersected):
                self.inCollision = False
    
    def inCarCollision(self, app):
        for car in app.cars:
            if car.name != self.name and self.carIntersectLine(app, self.position, car.position):
                self.collisionType = "Car"
                self.collidedCar = car
                return True
        return False
    
    def inWallCollision(self, app):
        if (self.carIntersectLine(app, self.position, app.map.interiorWall) or
            self.carIntersectLine(app, self.position, app.map.exteriorWall)):
            self.collisionType = "Wall"
            return True
        return False

    def carIntersectLine(self, app, carPoints, objectPoints):
        carLines = getPairs(carPoints)
        objectLines = getPairs(objectPoints)
        for objectLine in objectLines:
            for carLine in carLines:
                if (linesIntersect(carLine[0], carLine[1], objectLine[0], objectLine[1])):
                    line1, line2 = line(carLine[0], carLine[1]), line(objectLine[0], objectLine[1])
                    self.xWall, self.yWall = intersectionPoint(line1, line2)
                    self.lineIntersected = objectLine
                    self.inCollision = True
                    return True
        return False

    def friction(self):
        if self.vx > 0: self.vx -= 0.1
        elif self.vx < 0: self.vx += 0.1
        if self.vy > 0: self.vy -= 0.1
        elif self.vy < 0: self.vy += 0.1

    # * ###############
    # * CAR CHECKPOINTS
    
    # creates checkpoints at track vertices to guide car
    def checkpoints(self, app):
        for i in range(len(self.trackPoints)):
            # after car reaches checkpoint changes to next checkpoint
            atCheckpoint = False
            if (distance((self.x, self.y), self.trackPoints[i]) < self.trackWidth):
                # if finished lap
                if len(self.visitedCheckpoints) == len(self.trackPoints)-1:
                    self.visitedCheckpoints = []
                # checkpoint not already visited in lap    
                if self.trackPoints[i] not in self.visitedCheckpoints:
                    atCheckpoint = True
                    self.atNewCheckpoint(app, i)

                if (self.score >= len(self.trackPoints) and 
                    self.trackPoints[i] == self.trackPoints[0] and atCheckpoint):
                    self.finishedLap()
                    # laps only increase on first contact, not continously
                    atCheckpoint = False
    
    def atNewCheckpoint(self, app, trackPointIndex):
        self.visitedCheckpoints.append(self.trackPoints[trackPointIndex])
        if trackPointIndex+1 > len(self.trackPoints)-1:
            self.checkpoint = self.trackPoints[0]
        else:
            self.checkpoint = self.trackPoints[trackPointIndex+1]
        self.score += 1
        # implement checkpoint ranking
        self.checkpointRank = 0
        for car in app.cars:
            if self.name != car.name and self.score == car.score:
                self.checkpointRank += 1
    
    def finishedLap(self):
        if self.laps+1 == 3:
            self.racing = False
        else:
            self.laps += 1
        

class Player(Car):
    def __init__(self, app, name, x, y, color):
        super().__init__(app, name, x, y, color)
        # scrolling
        self.xOldPos = 640 # ? offset of camera to stay center
        self.yOldPos = 360
        self.xCamera = 640
        self.yCamera = 360
        self.centralizedPoints = self.centralizeMapDeconstructor(app.map.miniMap)
        self.rankings = []
    
    # player controls
    def pressedW(self): self.accelerating = True
    def pressedA(self): self.rotating = True; self.rotation = -5
    def pressedD(self): self.rotating = True; self.rotation = 5
    def releasedW(self): self.accelerating = False
    def releasedA(self): self.rotating = False
    def releasedD(self): self.rotating = False
    
    def draw(self, app, canvas):
        # update camera view
        self.updateCamera(canvas)
        # draw player car
        canvas.create_polygon(self.position, fill=self.color)
        # draw player info
        self.drawHUD(app, canvas)
    
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
    
    def drawHUD(self, app, canvas):
        r = 5
        canvas.create_oval(self.xCamera-5, self.yCamera-5, self.xCamera+5, self.yCamera+5)
        # relative to player, not canvas
        canvas.create_text(self.xCamera, self.yCamera+300, anchor="s",
                            text=f"Position: ({int(self.x)}, {int(self.y)}) \
                            Angle: {self.angle} \
                            Camera: ({self.xCamera},{self.yCamera})")
        self.drawMinimap(app, canvas)
        self.drawLeaderboard(app, canvas)
    
    def drawLeaderboard(self, app, canvas):
        x, y = self.xCamera + 535, self.yCamera+100
        w = 90
        l = 150
        # player positions
        self.rankings = []
        for car in app.cars:
            self.rankings.append((car.name, car.color, car.racing, car.laps, 
                             car.score, car.checkpointRank))
        self.rankings.sort(key = lambda x: (x[2], -x[4], x[5]), reverse=True)
        # assume leaderboard is already sorted
        for index, (name, color, racing, laps, score, checkpointRank) in enumerate(self.rankings):
            standing = ((x-w, y-l), (x+w, y+l-30*index))
            if not racing:
                color = "white"
                fontColor = "black"
            else:
                fontColor = "white"
            canvas.create_rectangle(standing, fill=color, outline="black")
            canvas.create_text((x-80, y+l - 30*(index+1)+8), text=f"{name}", 
                               fill=fontColor, anchor="nw")
            if not racing:
                canvas.create_text((x+40, y+l - 30*(index+1)+8), text=f"FINISH", 
                               fill=fontColor, anchor="nw")
        # lap display
        # print(rankings)
        leadingLap = self.rankings[len(self.rankings)-1][3]
        canvas.create_rectangle(self.xCamera+445, self.yCamera-100,
                                self.xCamera+625, self.yCamera-50, fill="black")
        canvas.create_text(self.xCamera + 535, self.yCamera-85, text="Leaderboard", 
                           fill="white", font="Arial 11")
        canvas.create_text(self.xCamera + 535, self.yCamera-65, text=f"LAP {leadingLap}/2", 
                           fill="white", font="Arial 14 bold")

    def drawMinimap(self, app, canvas):
        canvas.create_rectangle(self.xCamera + 340, self.yCamera-340,
                                self.xCamera + 625, self.yCamera-110,
                                fill="white", outline="black")
        canvas.create_rectangle(self.xCamera + 340, self.yCamera-340,
                                self.xCamera + 625, self.yCamera-295,
                                fill="black")
        canvas.create_text(self.xCamera + 480, self.yCamera-325, text="Map", 
                           fill="white", font="Arial 11")
        canvas.create_text(self.xCamera + 480, self.yCamera-310, text="ALBERT PARK", 
                           fill="white", font="Arial 14 bold")
        # track
        displayPoints = self.centralizeMapConstructor(self.centralizedPoints)
        canvas.create_line(displayPoints, width=12, fill="black")
        canvas.create_line(displayPoints, width=10, fill="grey")
        # player dot icon 
        for car in app.cars:
            mX, mY = car.x//33, car.y//33
            x = self.xCamera + mX + 290
            y = self.yCamera + mY - 340 + 45
            r = 5
            canvas.create_oval(x-r, y-r, x+r, y+r, fill=car.color)

    def centralizeMapDeconstructor(self, mapPoints):
        centralize = []
        for (x, y) in mapPoints:
            dx = self.xCamera + x
            dy = self.yCamera + y
            centralize.append((dx, dy))
        return centralize
    
    def centralizeMapConstructor(self, centralizedPoints):
        displayPoints = []
        for (dx, dy) in centralizedPoints:
            x = self.xOldPos + dx - 350
            y = self.yOldPos + dy - 700 + 45
            displayPoints.append((x, y))
        return displayPoints

class Enemy(Car):
    # initalize first checkpoint
    def __init__(self, app, name, x, y, color):
        super().__init__(app, name, x, y, color)
    
    # enemy driving
    def selfDrive(self, app):
        if self.checkpoint == None:
            self.checkpoint = self.trackPoints[0]
        leftPos, rightPos = self.checkFuturePosition()
        # get future positions of car after left/right shift
        leftDist = distance(leftPos, self.checkpoint)
        rightDist = distance(rightPos, self.checkpoint)
        # checks whether moving left or right places the car closer to the next checkpoint
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
                
    def visualizeSelfDrive(self, app, canvas):
        # draw checkpoints
        for point in self.trackPoints:
            x, y = point
            r = self.trackWidth
            if point in self.visitedCheckpoints:
                canvas.create_oval(x-r, y-r, x+r, y+r, outline="red", width=3)
            elif point == self.checkpoint:
                canvas.create_oval(x-r, y-r, x+r, y+r, outline="orange", width=3)
            else:
                canvas.create_oval(x-r, y-r, x+r, y+r, outline="green", width=3)
        # draw sensors
        left = self.updateCarCenter(self.angle-30, self.x, self.y, 50, 50)
        right = self.updateCarCenter(self.angle+30, self.x, self.y, 50, 50)
        for x, y in (left, right):
            canvas.create_oval(x-1, y-1, x+1, y+1, fill="white")