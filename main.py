from cmu_112_graphics import *
import math

def appStarted(app):
    # players
    app.player = Player(app, 'Player', app.width//2, app.height//2-170, 0, 0)
    app.p1 = Enemy(app, 'Car1', app.width//2-25, app.height//2-170, 0, 0)
    app.p2 = Enemy(app, 'Car2', app.width//2, app.height//2-160, 0, 0)
    app.p3 = Enemy(app, 'Car3', app.width//2-25, app.height//2-190, 0, 0)
    app.p4 = Enemy(app, 'Car4', app.width//2, app.height//2-180, 0, 0)
    app.cars = [app.player, app.p1, app.p2, app.p3, app.p4]
    # walls
    app.points = [(400, 50), (424, 47), (448, 54), (467, 70), (627, 182), (753, 250), (860, 311), (900, 291), (918, 260), (923, 202), (945, 173), (1135, 141), (1151, 152), (1111, 206), (1098, 265), (1120, 269), (1153, 215), (1209, 253), (1105, 339), (975, 379), (883, 376), (826, 354), (659, 265), (622, 285), (600, 268), (591, 236), (459, 134), (407, 138), (379, 151), (357, 175), (341, 215), (337, 243), (281, 307), (257, 304), (231, 311), (222, 363), (226, 430), (238, 476), (235, 508), (198, 492), (161, 462), (135, 425), (157, 392), (172, 331), (205, 260), (269, 176), (400, 50)]
    app.insideWalls = Wall([(607, 226), (616, 256), (624, 259), (653, 246), (667, 247), (756, 295), (832, 334), (883, 355), (972, 358), (1097, 321), (1175, 255), (1160, 244), (1138, 280), (1120, 287), (1086, 282), (1078, 267), (1092, 197), (1117, 164), (957, 190), (941, 212), (937, 263), (913, 305), (864, 330), (841, 324), (613, 197), (439, 74), (421, 66), (409, 69), (282, 188), (223, 265), (190, 335), (176, 398), (160, 423), (174, 444), (203, 470), (215, 477), (206, 439), (201, 362), (211, 304), (220, 295), (261, 284), (275, 285), (316, 235), (322, 206), (340, 167), (368, 136), (404, 118), (465, 114), (607, 226)])
    app.outsideWalls = Wall([(659, 289), (879, 397), (979, 399), (1116, 357), (1225, 265), (1227, 252), (1225, 240), (1157, 196), (1132, 214), (1169, 160), (1167, 140), (1139, 122), (937, 155), (906, 193), (897, 253), (887, 275), (860, 287), (639, 167), (480, 56), (461, 38), (427, 29), (392, 30), (257, 157), (186, 248), (156, 320), (138, 386), (118, 414), (117, 432), (146, 475), (187, 509), (227, 526), (249, 521), (256, 476), (246, 430), (242, 364), (249, 328), (259, 326), (284, 326), (354, 254), (358, 223), (372, 188), (389, 168), (414, 157), (453, 156), (572, 245), (583, 279), (609, 301), (631, 301), (659, 289)])
    # app.walls = Wall(app.inside + app.outside)
    app.timerDelay = 1000//60
    # car image
    image = app.loadImage("f1car.png")
    app.image = app.scaleImage(image, 0.1)
    app.clicked = []

def redrawAll(app, canvas):
    canvas.create_line(app.points, fill="grey", width=40) #200
    canvas.create_line(app.points, fill="black", width=3) 
    for car in app.cars:
        car.draw(app, canvas)
    app.insideWalls.draw(canvas)
    app.outsideWalls.draw(canvas)
    app.p2.visualizeSelfDrive(app, canvas)
    #canvas.scale(ALL, app.player.x, app.player.y, 5, 5)
    if len(app.clicked) > 2:
        canvas.create_line(app.clicked, fill="blue")

def mousePressed(app, event):
    app.clicked.append((event.x, event.y))

def timerFired(app):
    for car in app.cars:
        if isinstance(car, Enemy):
            car.checkpoints(app)
            car.selfDrive(app)
        car.move(app)

def keyPressed(app, event):
    if event.key == "w":
        app.player.pressedW()
    if event.key == "a":
        app.player.pressedA()
    if event.key == "d":
        app.player.pressedD()
    
    if event.key == "r":
        app.clicked.pop()
    if event.key == "p":
        print(app.clicked)

def keyReleased(app, event):
    if event.key == "w":
        app.player.releasedW()
    if event.key == "a":
        app.player.releasedA()
    if event.key == "d":
        app.player.releasedD()

class Car:
    def __init__(self, app, name, x, y, vx, vy):
        self.app = app
        self.name = name
        # position vars
        self.x = x
        self.y = y
        self.vx = vx    # x velocity
        self.vy = vy    # y velocity
        self.angle = 0 
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
    
    def draw(self, app, canvas):
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
        self.collision(app)
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
        l, w = 2.5, 5
        topLeft = (self.x-w, self.y-l)
        topRight = (self.x+w, self.y-l)
        bottomRight = (self.x+w, self.y+l)
        bottomLeft = (self.x-w, self.y+l)
        self.position = [topLeft, topRight, bottomRight, bottomLeft]
        self.position = rotatePolygon(self.position, (self.x, self.y), self.angle)
    
    # calculates new position of car
    def updateCarCenter(self, angle, x, y, vx, vy):
        x += math.cos(math.radians(angle)) * vx * 0.3
        y += math.sin(math.radians(angle)) * vy * 0.3
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
            if (self.carIntersectingLine(app, self.position, app.insideWalls.position) or
                self.carIntersectingLine(app, self.position, app.outsideWalls.position)):
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
        self.trackWidth = 15
    # enemy driving
    def selfDrive(self, app):
        if self.checkpoint == None:
            self.checkpoint = app.points[5]
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
        for i in range(len(app.points)):
            r = self.trackWidth
            # after car reaches checkpoint changes to next checkpoint
            print(distance((self.x, self.y), app.points[i]))
            if distance((self.x, self.y), app.points[i]) < r:
                print('new checkpoint')
                self.checkpoint = app.points[i+1]
                break
    def visualizeSelfDrive(self, app, canvas):
        # draw checkpoints
        for point in app.points:
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

class Wall:
    def __init__(self, position):
        self.position = position

    def draw(self, canvas):
        canvas.create_line(self.position, width=5)

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