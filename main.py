from cmu_112_graphics import *
import math

def appStarted(app):
    # game
    app.screen = "selection"
    app.timerDelay = 1000//60
    app.map = Map()
    #track = app.loadImage("images/albert_park.jpeg")
    #track = app.scaleImage(track, 0.6)
    #app.track = ImageTk.PhotoImage(track)
    app.action = None
    app.gameStarted = False
    app.canvasWidth, app.canvasHeight = 15000, 15000

def redrawAll(app, canvas):
    # TODO: make HUD relative to car to stay on screen
    canvas.configure(xscrollincrement=1)
    canvas.configure(yscrollincrement=1)
    canvas.configure(scrollregion = (0, 0, app.canvasWidth, app.canvasHeight))
    if app.action == "Up": canvas.yview_scroll(-50, "units")
    if app.action == "Down": canvas.yview_scroll(50, "units")
    if app.action == "Left": canvas.xview_scroll(-50, "units")
    if app.action == "Right": canvas.xview_scroll(50, "units")
    # selection screen
    if app.screen == "selection":
        #canvas.create_image(app.width//2, app.height//2-50, image=app.track)
        app.map.draw(app, canvas)
    # game screen
    else:
        if app.gameStarted:
            app.map.draw(app, canvas)
            # canvas.create_rectangle(0, 0, 5000, 5000, fill="lightGreen")
            # canvas.create_polygon(app.map.seaLine, fill="lightGrey")
            # # * Dashed line is glitched 
            # canvas.create_line(app.map.trackLine, fill="black", width=3)
            # canvas.create_line(app.map.exteriorWall, fill="black", width=10)
            # canvas.create_line(app.map.interiorWall, fill="black", width=10)
            for car in app.cars:
                car.draw(app, canvas)
            app.enemy1.visualizeSelfDrive(app, canvas)
            # canvas.scale(ALL, app.player.x, app.player.y, 2, 2)
            # print((app.player.x, app.player.y))
    
def startGame(app): 
    # start positions
    xStart, yStart = app.map.gameMap[0][0][0], app.map.gameMap[0][0][1]
    # print(xStart)
    x1, y1 = xStart+500, yStart
    x2, y2 = xStart+500, yStart+100
    x3, y3 = xStart-28, yStart+18
    x4, y4 = xStart-15, yStart+30
    x5, y5 = xStart, yStart
    # cars
    app.enemy1 = Enemy(app, 'Redbull', x1, y1, 'green')
    app.enemy2 = Enemy(app, 'Ferrari', x2, y2, 'red')
    app.player = Player(app, 'Player', x5, y5, 'blue')
    app.cars = [app.player, app.enemy1, app.enemy2]

def mousePressed(app, event):
    print(event.x, event.y)
    if app.screen == "selection":
        app.map.input("mousePress", (event.x, event.y))

def timerFired(app):
    if app.screen == "selection":
        pass
    else:
        if not app.gameStarted:
            startGame(app)
            app.gameStarted = True
        for car in app.cars:
            if isinstance(car, Enemy):
                car.checkpoints(app)
                car.selfDrive(app)
            car.move(app)

def keyPressed(app, event):
    if app.screen == "selection":
        if event.key == "Up": app.action = "Up"
        elif event.key == "Down": app.action = "Down"
        elif event.key == "Left": app.action = "Left"
        elif event.key == "Right": app.action = "Right" 
        if event.key == "Space":
            app.screen = "game"
        else:
            app.map.input("keyPress", event.key)
    else:
        if event.key == "w": app.player.pressedW()
        if event.key == "a": app.player.pressedA()
        if event.key == "d": app.player.pressedD()
        # scrolling
        if event.key == "Left": app.direction = "left"
        if event.key == "Right": app.direction = "right"
        if event.key == "Up": app.direction = "up"
        if event.key == "Down": app.direction = "down"

def keyReleased(app, event):
    if app.screen == "selection":
        if event.key == "Up": app.action = None
        elif event.key == "Down": app.action = None
        elif event.key == "Left": app.action = None
        elif event.key == "Right": app.action = None
        pass
    else:
        if event.key == "w": app.player.releasedW()
        if event.key == "a": app.player.releasedA()
        if event.key == "d": app.player.releasedD()
        # scrolling
        if event.key == "Left": app.direction = None
        if event.key == "Right": app.direction = None
        if event.key == "Up": app.direction = None
        if event.key == "Down": app.direction = None

#####
# CAR
#####

class Car:
    def __init__(self, app, name, x, y, color):
        self.app = app
        self.name = name
        self.color = color
        # position vars
        self.x = x
        self.y = y
        self.vx = 0   # x velocity
        self.vy = 0    # y velocity
        self.angle = -180
        self.position = []
        self.updateCarRectangle()
        # movement vars
        self.rotating = False
        self.rotation = 0
        self.accelerating = False
        # collision vars
        self.lineIntersected = None
        self.inCollision = False
        # contact wall
        self.xWall, self.yWall = None, None
        self.collisionType = "None"
        self.collidedCar = None
        # scoring
        self.checkpoint = None
        self.visitedCheckpoints = []
        self.trackWidth = 150
        self.score = 0
    
    def draw(self, app, canvas):
        canvas.create_polygon(self.position, fill=self.color)
        # collision impact
        if self.xWall and self.yWall:
            r = 3
            canvas.create_oval(self.xWall-r, self.yWall-r, self.xWall+r, self.yWall+r,
                                fill="orange")
        # * car image
        # image = ImageTk.PhotoImage(app.image.rotate(-self.angle, expand=True)) 
        # canvas.create_image(self.x, self.y, image=image)
    
    def move(self, app):
        # checks if the car has collided with another object
        self.collision(app)
        # only responds to player controls if not in collision
        if not self.inCollision:
            if self.accelerating:
                if self.vx < 10: self.vx += 1
                if self.vy < 10: self.vy += 1
            if self.rotating: 
                if self.angle+self.rotation>180: self.angle = -178
                elif self.angle+self.rotation<-178: self.angle = 180
                else: self.angle += self.rotation
        # updates car position
        self.x, self.y = self.updateCarCenter(self.angle, self.x, self.y, self.vx, self.vy)
        self.updateCarRectangle()
        # adds friction to car movement
        self.friction()

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
    
    def collision(self, app):
        if self.touchingObject(app):
            if self.collisionType == "Car": 
                (x1, y1), (x2, y2) = self.lineIntersected[0], self.lineIntersected[1]
                # treat collision as bouncing off a flat surface with the angle
                # of the tangent at the point of contact
                dx = x1 - x2
                dy = y1 - y2
                tangent = math.atan2(dy, dx)
                angle = 2 * tangent - self.angle
                # self.angle = angle
                # self.collidedCar.angle = 2*tangent - self.collidedCar.angle
                # # account for existing overlap when collision detected
                # a = 0.5 * math.pi + tangent
                # self.x += math.sin(a)
                # self.y -= math.cos(a)
                # self.collidedCar.x -= math.sin(a)
                # self.collidedCar.y += math.cos(a)
            else:
                (x1, y1), (x2, y2) = self.lineIntersected[0], self.lineIntersected[1]
            
            # find angle of collided object
            rise, run = (y1-y2), (x1-x2)
            angle = math.atan2(rise, run)
            # find normal 
            d = math.degrees(angle)
            # find normal vector of plane
            if (-180 < d and d < -90) or (0 < d and d < 90): 
                nx = math.sin(angle)
            elif (-90 < d and d < 0) or (90 < d and d < 180): 
                nx = -math.sin(angle)
            else: 
                nx = -math.sin(angle)
            ny = math.cos(angle)
            # velocity after reflection
            dot = self.vx * nx + self.vy * ny 
            self.vx = (self.vx - 2 * dot * nx)
            self.vy = (self.vy - 2 * dot * ny)
            # elasticity
            self.vx *= 0.5
            self.vy *= 0.5
            self.x += self.vx
            self.y += self.vy
            # if contact with another car exchange velocity
            # checks position of car relative to point of contact 
            
            if self.collisionType == "Car":
                #(self.vx, self.vy, self.collidedCar.vx, self.collidedCar.vy) = \
                #(self.collidedCar.vx, self.collidedCar.vy, self.vx, self.vy,)
                """
                if self.collidedCar.x < self.x: 
                    self.x += self.vx
                    self.collidedCar.x -= self.collidedCar.vx
                else: 
                    self.x -= self.vx
                    self.collidedCar.x += self.collidedCar.vx
            
                if self.collidedCar.y < self.y: 
                    self.y += self.vy
                    self.collidedCar.y -= self.collidedCar.vy
                else: 
                    self.y -= self.vy
                    self.collidedCar.y += self.collidedCar.vy
            """

    # finds which object the car is touching
    def touchingObject(self, app):
        # car position
        (p1, p2, p3, p4) = (self.position[0], self.position[1], 
                            self.position[2], self.position[3])
        if self.inCollision:
            # if the car is touching another object, check if it is still touching
            if self.collisionType == "Car":
                if not self.carIntersectingLine(app, self.position, self.collidedCar.position):
                    self.inCollision = False
            else:
                # loop through wall list and find intersection
                if not self.carIntersectingLine(app, self.position, self.lineIntersected):
                    self.inCollision = False
        else:
            # check if car is touching any other cars
            for car in app.cars:
                if car.name != self.name and self.carIntersectingLine(app, self.position, car.position):
                    self.collisionType = "Car"
                    self.collidedCar = car
                    return True
            # check if car is intersecting any walls
            if (self.carIntersectingLine(app, self.position, app.map.interiorWall) or
                self.carIntersectingLine(app, self.position, app.map.exteriorWall)):
                self.collisionType = "Wall"
                return True
        return False

    def carIntersectingLine(self, app, carPoints, objectPoints):
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

    # creates checkpoints at track vertices to guide car
    def checkpoints(self, app):
        for i in range(len(app.map.trackLine)):
            r = self.trackWidth
            # after car reaches checkpoint changes to next checkpoint
            # print(distance((self.x, self.y), app.map.trackLine[i]))
            if (distance((self.x, self.y), app.map.trackLine[i]) < r):
                # if finished lap
                if len(self.visitedCheckpoints) == len(app.map.trackLine)-1:
                    self.visitedCheckpoints = []
                # checkpoint not already visited in lap    
                if app.map.trackLine[i] not in self.visitedCheckpoints:
                    self.visitedCheckpoints.append(app.map.trackLine[i])
                    if i+1 > len(app.map.trackLine)-1:
                        self.checkpoint = app.map.trackLine[0]
                    else:
                        self.checkpoint = app.map.trackLine[i+1]
                    self.score += 1
            # if self.score == len(app.map.trackLine)+2:
            #     print('lap finished!')

class Player(Car):
    def __init__(self, app, name, x, y, color):
        super().__init__(app, name, x, y, color)
        # scrolling
        self.xOldPos = 640 # ? offset of camera to stay center
        self.yOldPos = 360
        self.xCamera = 640
        self.yCamera = 360
        self.centralizedPoints = self.centralizeMapDeconstructor(app.map.miniMap)
        
    # player controls
    def pressedW(self): self.accelerating = True
    def pressedA(self): self.rotating = True; self.rotation = -5
    def pressedD(self): self.rotating = True; self.rotation = 5
    def releasedW(self): self.accelerating = False
    def releasedA(self): self.rotating = False
    def releasedD(self): self.rotating = False

    def move(self, app):
        # checks if the car has collided with another object
        self.collision(app)
        # only responds to player controls if not in collision
        if not self.inCollision:
            if self.accelerating:
                if self.vx < 10: self.vx += 1
                if self.vy < 10: self.vy += 1
            if self.rotating: 
                if self.angle+self.rotation>180: self.angle = -178
                elif self.angle+self.rotation<-178: self.angle = 180
                else: self.angle += self.rotation
        # updates car position
        self.x, self.y = self.updateCarCenter(self.angle, self.x, self.y, self.vx, self.vy)
        self.updateCarRectangle()
        # adds friction to car movement
        self.friction()
        self.checkpoints(app)
    
    def draw(self, app, canvas):
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
        
        # draw player car
        canvas.create_polygon(self.position, fill="blue")
        # draw player info
        self.drawHUD(app, canvas)
    
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
    
    def drawMinimap(self, app, canvas):
        # track
        displayPoints = self.centralizeMapConstructor(self.centralizedPoints)
        canvas.create_line(displayPoints, width=10, fill="black")
        # player dot icon 
        for car in app.cars:
            mX, mY = car.x//33, car.y//33
            x = self.xCamera + mX + 290
            y = self.yCamera + mY - 340
            r = 5
            canvas.create_oval(x-r, y-r, x+r, y+r, fill=car.color)
    
    def drawLeaderboard(self, app, canvas):
        x, y = self.xCamera + 500, self.yCamera+20
        w = 90
        l = 165
        # player positions
        # [(player, score)]
        rankings = []
        for car in app.cars:
            rankings.append((car.name, car.color, car.score))
        rankings.sort(key = lambda x: x[2])
        # assume leaderboard is already sorted
        board = [(x-w, y-l), (x-w, y+l), (x+w, y+l), (x+w, y-l)]
        for index, (name, color, score) in enumerate(rankings):
            board[1] = (x-w, y+l - 30*index)
            board[2] = (x+w, y+l - 30*index)
            standing = board[:]
            canvas.create_polygon(standing, fill=color, outline="black")
            canvas.create_text((x-80, y+l - 30*(index+1)+8), text=name, fill="white", anchor="nw")
    
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
            y = self.yOldPos + dy - 700
            displayPoints.append((x, y))
        return displayPoints

class Enemy(Car):
    # initalize first checkpoint
    def __init__(self, app, name, x, y, color):
        super().__init__(app, name, x, y, color)
    # enemy driving
    def selfDrive(self, app):
        if self.checkpoint == None:
            self.checkpoint = app.map.trackLine[0]
        leftPos, rightPos = self.checkFuturePosition()
        # get future positions of car after left/right shift
        leftDist = distance(leftPos, self.checkpoint)
        rightDist = distance(rightPos, self.checkpoint)
        # checks whether moving left or right places the car closer to the next checkpoint
        # (distance must be signficant, >10, to reduce wiggling)
        if leftDist - rightDist < -3:
            self.rotating = True
            self.rotation = -5
        elif leftDist - rightDist > 3:
            self.rotating = True
            self.rotation = 5
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
        for point in app.map.trackLine:
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

###########
# MAP MAKER
###########

class Map:
    def __init__(self):
        self.currentShape = []
        self.drawing = True
        self.selectedIndex = None
        self.trackLine = [(689, 544), (547, 524), (532, 522), (525, 519), (520, 516), (515, 510), (511, 504), (507, 492), (503, 484), (498, 478), (490, 474), (480, 470), (470, 468), (457, 466), (368, 454), (355, 450), (312, 434), (302, 431), (241, 409), (234, 405), (229, 400), (227, 395), (228, 388), (230, 384), (234, 379), (255, 362), (260, 356), (262, 350), (261, 343), (259, 338), (256, 334), (223, 306), (215, 297), (210, 288), (207, 280), (205, 272), (205, 260), (206, 253), (208, 244), (210, 233), (213, 223), (218, 211), (246, 150), (261, 123), (263, 116), (267, 100), (269, 95), (273, 92), (279, 91), (305, 89), (311, 88), (316, 86), (337, 73), (347, 67), (356, 63), (367, 60), (380, 58), (394, 58), (406, 59), (421, 63), (432, 68), (443, 75), (528, 152), (531, 159), (531, 163), (529, 167), (518, 180), (516, 186), (515, 193), (516, 200), (519, 208), (546, 253), (552, 261), (568, 283), (575, 291), (588, 305), (611, 325), (622, 332), (634, 339), (650, 345), (670, 351), (681, 353), (727, 359), (750, 360), (763, 359), (769, 357), (773, 355), (778, 350), (804, 319), (807, 317), (812, 315), (820, 314), (891, 316), (912, 318), (937, 323), (951, 327), (963, 333), (1060, 399), (1067, 407), (1072, 414), (1075, 422), (1076, 432), (1076, 439), (1073, 447), (1029, 519), (1022, 524), (1014, 525), (1005, 525), (995, 521), (962, 501), (949, 496), (938, 495), (929, 495), (920, 499), (916, 504), (914, 513), (912, 547), (910, 553), (907, 558), (901, 563), (894, 565), (887, 566), (876, 566), (689, 544)]
        self.interiorWall = [(0, 0)]
        self.exteriorWall = [(0, 0)]
        self.editingShape = self.trackLine[:]
        
        self.selectionMap = [self.trackLine, self.interiorWall, self.exteriorWall]
        self.gameMap = self.scaleMap(self.selectionMap, 10)
        self.miniMap = self.scaleMap(self.selectionMap, 0.3)[0]
        self.trackLine = self.gameMap[0]
        
    def input(self, inputType, action):
        if inputType == "keyPress":
            if action == "r": self.removePoint()
            elif action == "s": self.saveShape()
            elif action == "p": self.printShapes()
            elif action == "m": self.changeMode()
            elif action == "x": self.scaleMap(self.editingShape, 10)
            elif action == "e": self.finishMap()
        elif inputType == "mousePress":
            if self.drawing: self.addPoint(action)
            else: self.movePoint(action)

    def draw(self, app, canvas):
        if app.screen == "selection":
            # display mode
            if self.drawing: mode = "creating"
            else: mode = "editing"
            # canvas.create_line(self.trackLine, width=5, fill="grey")
            # canvas.create_line(self.miniMap, width=1, fill="black")
            canvas.create_text(app.width//2, app.height-50, text=mode)
            
            # draw editing shape
            if len(self.editingShape) > 1:
                # draw line
                canvas.create_line(self.editingShape, width=1, fill="red")
                # draw vertices
                r = 2
                for currentIndex, point in enumerate(self.editingShape):
                    (x, y) = point
                    if currentIndex == self.selectedIndex:
                        canvas.create_oval(x-r, y-r, x+r, y+r, fill="white")
                    else:
                        canvas.create_oval(x-r, y-r, x+r, y+r, fill="black")
        else:
            scaledTrack = self.gameMap[0]
            # grass
            canvas.create_rectangle(0, 0, app.canvasWidth, app.canvasHeight, 
                                    fill="lightGreen")
            # track edge lines
            canvas.create_line(scaledTrack, fill="white", width=330)
            for i in range(1, len(scaledTrack)):
                p1 = scaledTrack[i-1]
                p2 = scaledTrack[i]
                canvas.create_line(p1, p2, fill="red", dash=(50, 50), width=330)
            # trackbed
            canvas.create_line(scaledTrack, fill="grey", width=300)
            # track markings
            for i in range(1, len(scaledTrack)):
                p1 = scaledTrack[i-1]
                p2 = scaledTrack[i]
                # track center lines
                canvas.create_line(p1, p2, fill="black", dash=(10, 10), width=5)
            # raceline
            self.drawStartLine(canvas, scaledTrack)

    def drawStartLine(self, canvas, points):
        l = 150
        w = 10
        # align line to slope of track
        x, y = points[0][0], points[0][1]
        x2, y2 = points[1][0], points[1][1]
        slope = (x-x2) / (y-y2)
        # first line
        raceline = [(x-w, y-l), (x-w, y+l), (x+w, y+l), (x+w, y-l)]
        for i in range(16):
            raceline[1] = (x-w, y+l - 20*i)
            raceline[2] = (x+w, y+l - 20*i)
            block = raceline[:]
            block = rotatePolygon(block, (x, y), slope)
            if i%2 == 0: canvas.create_polygon(block, fill="black")
            else: canvas.create_polygon(block, fill="white")
        # second line
        shift = 20
        raceline = [(x-w-shift, y-l), (x-w-shift, y+l), (x+w-shift, y+l), (x+w-shift, y-l)]
        for i in range(16):
            raceline[1] = (x-w-shift, y+l - 20*i)
            raceline[2] = (x+w-shift, y+l - 20*i)
            block = raceline[:]
            block = rotatePolygon(block, (x, y), slope)
            if i%2 == 1: canvas.create_polygon(block, fill="black")
            else: canvas.create_polygon(block, fill="white")

    def saveShape(self):
        if self.drawing:
            if self.currentShape:
                self.editingShape.append(self.currentShape)
                self.currentShape = []

    def addPoint(self, point):
        if self.drawing:
            self.currentShape.append(point)
        elif self.selectedIndex:
            point = self.editingShape[self.selectedIndex]
            self.editingShape.insert(self.selectedIndex, point)
    
    def removePoint(self):
        if self.drawing:
            if self.currentShape:
                self.currentShape.pop()
        elif self.selectedIndex:
            point = self.editingShape[self.selectedIndex]
            self.editingShape.remove(point)
            self.selectedIndex = None

    def printShapes(self):
        print(self.editingShape)
    
    def movePoint(self, clickPoint):
        if not self.drawing:
            # if point not selected select point at mouseclick
            if not self.selectedIndex:
                for currentIndex, (x, y) in enumerate(self.editingShape):
                    if distance((x, y), (clickPoint)) < 5:
                        self.selectedIndex = currentIndex
            else:
                # if point selected move to mouseclick and reset selected index
                self.editingShape[self.selectedIndex] = clickPoint
                self.selectedIndex = None
    
    def changeMode(self):
        self.drawing = not self.drawing

    def scaleMap(self, shapes, scale):
        result = []
        for shape in shapes:
            new = []
            for x, y in shape:
                x *= scale
                y *= scale
                new.append((x, y))
            result.append(new)
        return result

    def finishMap(self):
        self.currentShape.append(self.currentShape[0])

##################
# HELPER FUNCTIONS
##################

# calculates distance between two points
def distance(p1, p2):
    return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5

# get all consecutive sublist pairs of a list
def getPairs(L):
    pairs = []
    for i in range(1, len(L)):
        pair = (L[i-1], L[i])
        pairs.append(pair)
    # add last and first value pair
    end = (L[len(L)-1], L[0])
    pairs.append(end)
    return pairs

# rotates a polygon
def rotatePolygon(points, center, angle):
    cx, cy = center
    rotated = []
    angle = math.radians(angle)
    cos = math.cos(angle)
    sin = math.sin(angle)
    for px, py in points:
        x = px - cx
        y = py - cy
        newX = x*cos - y*sin
        newY = x*sin + y*cos
        rotated.append((newX + cx, newY + cy))
    return rotated

# checks if two line segments AB and CD intersect
def linesIntersect(A, B, C, D):
    dir1 = direction(A, B, C)
    dir2 = direction(A, B, D)
    dir3 = direction(C, D, A)
    dir4 = direction(C, D, B)
    if dir1 != dir2 and dir3 != dir4:
        return True
    if dir1 == 0 and pointOnLine(C, (A, B)):
        return True
    if dir2 == 0 and pointOnLine(D, (A, B)):
        return True
    if dir3 == 0 and pointOnline(A, (C, D)):
        return True
    if dir4 == 0 and pointOnLine(B, (C, D)):
        return True
    return False

def direction(A, B, C):
    Ax, Ay = A
    Bx, By = B
    Cx, Cy = C
    val = (By-Ay)*(Cx-Bx) - (Bx-Ax)*(Cy-By)
    if val == 0:
        return "collinear"
    elif val < 0:
        return "anti-clockwise"
    else:
        return "clockwise"

def pointOnLine(point, line):
    lineP1, lineP2 = line[0], line[1]
    if (point[0] <= max(lineP1[0], lineP2[0]) and point[0] >= min(lineP1[0], lineP2[0])
       and point[1] <= max(lineP1[1], lineP2[1]) and point[1] >= min(lineP1[1], lineP2[1])):
       return True
    return False

def line(p1, p2):
    A = (p1[1] - p2[1])
    B = (p2[0] - p1[0])
    C = (p1[0]*p2[1] - p2[0]*p1[1])
    return A, B, -C

def intersectionPoint(L1, L2):
    D  = L1[0] * L2[1] - L1[1] * L2[0]
    Dx = L1[2] * L2[1] - L1[1] * L2[2]
    Dy = L1[0] * L2[2] - L1[2] * L2[0]
    if D != 0:
        x = Dx / D
        y = Dy / D
        return x,y
    else:
        return False
    
runApp(width=1280, height=720)