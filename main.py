from cmu_112_graphics import *
import math

def appStarted(app):
    # screen
    app.screen = "selection"
    # map
    app.map = Map()
    # players
    # start positions
    xStart, yStart = app.map.trackLine[0][0], app.map.trackLine[0][1]
    x1, y1 = xStart-13, yStart+3
    x2, y2 = xStart, yStart+15
    x3, y3 = xStart-28, yStart+18
    x4, y4 = xStart-15, yStart+30
    x5, y5 = xStart-40, yStart+30
    app.enemy1 = Enemy(app, 'Enemy1', x1, y1, 0, 0)
    app.enemy2 = Enemy(app, 'Enemy2', x2, y2, 0, 0)
    app.enemy3 = Enemy(app, 'Enemy3', x3, y3, 0, 0)
    app.enemy4 = Enemy(app, 'Enemy4', x4, y4, 0, 0)
    app.player = Player(app, 'Player', 640, 360, 0, 0)
    app.cars = [app.player]
    app.timerDelay = 1000//60
    # track image
    track = app.loadImage("images/monacoTrack.jpeg")
    track = app.scaleImage(track, 1)
    app.track = ImageTk.PhotoImage(track)
    
    # scrolling 
    app.cx, app.cy = 640, 360
    app.direction = None

def redrawAll(app, canvas):
    scrolling(app, canvas)
    # make HUD relative to car to stay on screen
    canvas.configure(xscrollincrement=1)
    canvas.configure(yscrollincrement=1)
    canvas.configure(scrollregion = (0, 0, 5000, 5000))
    # scrolling(app, canvas)
    if app.screen == "selection":
        canvas.create_image(app.width//2, app.height//2, image=app.track)
        app.map.draw(canvas)
    else:
        # canvas.create_polygon(app.map.seaLine, fill="lightGrey")
        # canvas.create_line(app.map.trackLine, fill="grey", width=245)
        # # * Dashed line is glitched 
        # canvas.create_line(app.map.trackLine, fill="black", width=3)
        # canvas.create_line(app.map.exteriorWall, fill="black", width=10)
        # canvas.create_line(app.map.interiorWall, fill="black", width=10)
        for l in app.map.mapShapes:
            canvas.create_line(l)
        for car in app.cars:
            car.draw(app, canvas)
        # app.enemy1.visualizeSelfDrive(app, canvas)
        # canvas.scale(ALL, app.player.x, app.player.y, 2, 2)
        r = 3
        canvas.create_oval(app.cx-r, app.cy-r, app.cx+r, app.cy+r, fill="black")

def scrolling(app, canvas):
    # if app.direction == "left":
    #     canvas.xview_scroll(-5, "units")
    # elif app.direction == "right":
    #     canvas.xview_scroll(5, "units")
    # elif app.direction == "up":
    #     canvas.yview_scroll(-5, "units")
    #     print('up')
    # elif app.direction == "down":
    #     canvas.yview_scroll(5, "units")
    pass

def mousePressed(app, event):
    
    if app.screen == "selection":
        app.map.input("mousePress", (event.x, event.y))

def timerFired(app):
    app.cx += app.player.xChange
    app.cy += app.player.yChange
    print((app.cx, app.cy))
    if app.screen == "selection":
        pass
    else:
        for car in app.cars:
            if isinstance(car, Enemy):
                car.checkpoints(app)
                car.selfDrive(app)
            car.move(app)

def keyPressed(app, event):
    if app.screen == "selection":
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
    def __init__(self, app, name, x, y, vx, vy):
        self.app = app
        self.name = name
        # position vars
        self.x = x
        self.y = y
        self.vx = vx    # x velocity
        self.vy = vy    # y velocity
        self.angle = -45
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
        
        # scrolling
        self.xChange, self.yChange = 0, 0
    
    def draw(self, app, canvas):
        # scrolling
        # * find distance from (0, 0) to car center 
        
        canvas.create_polygon(self.position, fill="blue")
        if self.name == "Player":
            canvas.create_text(app.width//2, app.height-50, text=f"{self.angle}",
                            anchor="sw")
            if self.xWall and self.yWall:
                r = 3
                canvas.create_oval(self.xWall-r, self.yWall-r, self.xWall+r, self.yWall+r,
                                    fill="orange")
        # car image
        # image = ImageTk.PhotoImage(app.image.rotate(-self.angle, expand=True)) 
        # canvas.create_image(self.x, self.y, image=image)
    
    def move(self, app):
        # checks if the car has collided with another object
        # ! self.collision(app)
        # only responds to player controls if not in collision
        if not self.inCollision:
            if self.accelerating:
                if self.vx < 5: self.vx += 1
                if self.vy < 5: self.vy += 1
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
        l, w = 20, 40
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

class Player(Car):
    def pressedW(self): self.accelerating = True
    def pressedA(self): self.rotating = True; self.rotation = -5
    def pressedD(self): self.rotating = True; self.rotation = 5
    def releasedW(self): self.accelerating = False
    def releasedA(self): self.rotating = False
    def releasedD(self): self.rotating = False

class Enemy(Car):
    # initalize first checkpoint
    def __init__(self, app, name, x, y, vx, vy):
        super().__init__(app, name, x, y, vx, vy)
        self.checkpoint = None
        self.trackWidth = 20
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
    # creates checkpoints at track vertices to guide car
    def checkpoints(self, app):
        for i in range(len(app.map.trackLine)):
            r = self.trackWidth
            # after car reaches checkpoint changes to next checkpoint
            print(distance((self.x, self.y), app.map.trackLine[i]))
            if distance((self.x, self.y), app.map.trackLine[i]) < r:
                print('new checkpoint')
                self.checkpoint = app.map.trackLine[i+1]
                break
    def visualizeSelfDrive(self, app, canvas):
        # draw checkpoints
        for point in app.map.trackLine:
            x, y = point
            r = self.trackWidth
            if point == self.checkpoint:
                canvas.create_oval(x-r, y-r, x+r, y+r, outline="orange", width=3)
            else:
                canvas.create_oval(x-r, y-r, x+r, y+r, outline="purple", width=3)
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
        self.mapShapes = []
        self.currentShape = []
        self.drawing = True
        self.selectedIndex = None
        
        self.trackLine = [(283, 213), (390, 149), (467, 137), (526, 158), (641, 279), (675, 327), (749, 376), (803, 446), (857, 471), (907, 456), (918, 397), (952, 359), (1150, 391), (1152, 420), (1103, 480), (1105, 504), (1130, 509), (1179, 474), (1199, 476), (1219, 514), (1107, 575), (919, 591), (813, 529), (746, 478), (681, 404), (653, 402), (636, 386), (632, 361), (493, 192), (417, 202), (353, 241), (344, 278), (260, 354), (235, 341), (192, 400), (175, 451), (181, 484), (166, 504), (126, 470), (100, 416), (121, 403), (145, 353), (283, 213)]
        self.exteriorWall = [(272, 198), (383, 131), (469, 118), (538, 144), (657, 268), (689, 314), (761, 361), (815, 430), (859, 451), (890, 439), (901, 388), (944, 341), (953, 340), (1156, 373), (1167, 381), (1172, 425), (1124, 487), (1127, 488), (1170, 458), (1177, 455), (1207, 458), (1216, 465), (1239, 511), (1237, 523), (1226, 533), (1115, 593), (916, 612), (796, 542), (732, 494), (672, 424), (645, 422), (618, 394), (613, 369), (487, 215), (424, 221), (370, 254), (364, 284), (268, 373), (251, 373), (240, 367), (210, 411), (196, 452), (201, 486), (179, 520), (164, 526), (155, 522), (110, 483), (81, 420), (83, 406), (106, 390), (129, 342), (272, 198)]
        self.interiorWall = [(294, 230), (398, 168), (466, 158), (516, 176), (626, 292), (659, 340), (734, 391), (789, 462), (850, 491), (861, 491), (919, 473), (926, 461), (937, 407), (960, 381), (1131, 407), (1132, 413), (1085, 473), (1086, 508), (1093, 520), (1132, 529), (1146, 523), (1184, 495), (1187, 496), (1193, 506), (1103, 556), (924, 571), (822, 512), (759, 464), (695, 390), (683, 384), (661, 383), (654, 377), (651, 353), (644, 345), (507, 177), (495, 173), (411, 183), (340, 227), (333, 237), (326, 268), (258, 330), (236, 321), (220, 327), (174, 391), (155, 450), (159, 474), (142, 459), (126, 424), (137, 417), (161, 366), (294, 230)]
        
        self.seaLine = [(412, 716), (185, 493), (203, 467), (209, 411), (382, 258), (376, 239), (486, 213), (616, 381), (636, 412), (716, 475), (832, 597), (959, 619), (1086, 599), (1239, 534), (1240, 2), (40, 4), (41, 714), (410, 715)]
        
        self.mapShapes.append(self.trackLine)
        self.mapShapes.append(self.exteriorWall)
        self.mapShapes.append(self.interiorWall)
        self.mapShapes.append(self.seaLine)
        
    def input(self, inputType, action):
        if inputType == "keyPress":
            if action == "r": self.removePoint()
            elif action == "s": self.saveShape()
            elif action == "p": self.printShapes()
            elif action == "m": self.changeMode()
            elif action == "x": self.shiftMap()
        elif inputType == "mousePress":
            if self.drawing: self.addPoint(action)
            else: self.movePoint(action)

    def draw(self, canvas):
        if len(self.currentShape) > 1:
            canvas.create_line(self.currentShape, width=2, fill="orange")
        if self.mapShapes:
            for shapeIndex, shape in enumerate(self.mapShapes):
                canvas.create_line(shape, width=3, fill="red")
                for pointIndex, (x, y) in enumerate(shape):
                    r = 3
                    if (shapeIndex, pointIndex) == self.selectedIndex:
                        canvas.create_oval(x-r, y-r, x+r, y+r, fill="white")
                    else:
                        canvas.create_oval(x-r, y-r, x+r, y+r, fill="black")

    def saveShape(self):
        if self.drawing:
            if self.currentShape:
                self.mapShapes.append(self.currentShape)
                self.currentShape = []
    
    def addPoint(self, point):
        if self.drawing:
            self.currentShape.append(point)
    
    def removePoint(self):
        if self.drawing:
            if self.currentShape:
                self.currentShape.pop()
        
    def printShapes(self):
        print(self.mapShapes)
    
    def movePoint(self, clickPoint):
        if not self.drawing:
            if not self.selectedIndex:
                for shapeIndex, shape in enumerate(self.mapShapes):
                    for pointIndex, (x, y) in enumerate(shape):
                        if distance((x, y), (clickPoint)) < 5:
                            self.selectedIndex = (shapeIndex, pointIndex)
            else:
                self.mapShapes[self.selectedIndex[0]][self.selectedIndex[1]] = clickPoint
                self.selectedIndex = None
    
    def changeMode(self):
        self.drawing = not self.drawing
    
    def shiftMap(self):
        newShape = []
        result = []
        for l in self.mapShapes:
            new = []
            for x, y in l:
                x *= 5
                y *= 5
                new.append((x, y))
            result.append(new)
        self.mapShapes = result
            

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

# runApp(width=1280, height=720)
runApp(width=1280, height=720)