from cmu_112_graphics import *
import math

def appStarted(app):
    # game
    app.screen = "selection"
    app.timerDelay = 1000//60
    app.map = Map()
    # TODO: create map
    track = app.loadImage("images/monacoTrack.jpeg")
    track = app.scaleImage(track, 1)
    app.track = ImageTk.PhotoImage(track)
    app.action = None
    app.gameStarted = False

def redrawAll(app, canvas):
    # TODO: make HUD relative to car to stay on screen
    canvas.configure(xscrollincrement=1)
    canvas.configure(yscrollincrement=1)
    canvas.configure(scrollregion = (0, 0, 15000, 15000))
    if app.action == "Up": canvas.yview_scroll(-50, "units")
    if app.action == "Down": canvas.yview_scroll(50, "units")
    if app.action == "Left": canvas.xview_scroll(-50, "units")
    if app.action == "Right": canvas.xview_scroll(50, "units")
    # selection screen
    if app.screen == "selection":
        canvas.create_image(app.width//2, app.height//2, image=app.track)
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
            # app.enemy1.visualizeSelfDrive(app, canvas)
            # canvas.scale(ALL, app.player.x, app.player.y, 2, 2)
    
def startGame(app):
    # start positions
    xStart, yStart = app.map.trackLine[0][0], app.map.trackLine[0][1]
    x1, y1 = xStart-13, yStart+3
    x2, y2 = xStart, yStart+15
    x3, y3 = xStart-28, yStart+18
    x4, y4 = xStart-15, yStart+30
    x5, y5 = xStart-40, yStart+30
    # cars
    app.enemy1 = Enemy(app, 'Enemy1', x1, y1, 0, 0)
    app.enemy2 = Enemy(app, 'Enemy2', x2, y2, 0, 0)
    app.enemy3 = Enemy(app, 'Enemy3', x3, y3, 0, 0)
    app.enemy4 = Enemy(app, 'Enemy4', x4, y4, 0, 0)
    app.player = Player(app, 'Player', x5-100, y5, 0, 0)
    app.cars = [app.player, app.enemy1]

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
        self.xCamera = 640
        self.yCamera = 360
    
    def draw(self, app, canvas):
        # scrolling
        if self.name == "Player":
            # * find distance from (0, 0) to car center
            xDiff = int(self.x - self.xCamera)
            yDiff = int(self.y - self.yCamera)
            canvas.xview_scroll(xDiff, "units")
            canvas.yview_scroll(yDiff, "units")
            self.xCamera = self.x
            self.yCamera = self.y
        
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
        self.mapShapes = [[(289, 221), (373, 166), (418, 147), (468, 144), (507, 154), (522, 166), (550, 200), (636, 284), (670, 331), (740, 380), (799, 451), (818, 467), (847, 475), (879, 476), (902, 466), (917, 445), (927, 392), (938, 378), (954, 370), (974, 370), (1153, 393), (1159, 404), (1153, 418), (1141, 426), (1128, 435), (1116, 454), (1107, 468), (1098, 486), (1096, 501), (1108, 515), (1120, 515), (1129, 507), (1148, 460), (1157, 455), (1169, 452), (1198, 477), (1210, 494), (1211, 508), (1103, 563), (1053, 574), (957, 584), (915, 581), (888, 567), (813, 519), (757, 479), (675, 392), (657, 397), (640, 381), (641, 366), (505, 192), (493, 186), (467, 184), (417, 196), (372, 216), (345, 241), (341, 274), (270, 338), (257, 342), (237, 333), (221, 341), (181, 396), (166, 439), (169, 483), (159, 496), (149, 494), (124, 467), (103, 431), (106, 425), (120, 416), (151, 357), (196, 305), (257, 246), (289, 221)], 
                          [(294, 229), (379, 175), (421, 157), (468, 154), (504, 164), (516, 172), (542, 207), (628, 290), (663, 339), (734, 387), (791, 460), (814, 477), (846, 484), (884, 485), (910, 473), (925, 450), (937, 398), (943, 388), (956, 381), (974, 381), (1146, 403), (1147, 410), (1145, 414), (1133, 419), (1118, 430), (1096, 465), (1087, 485), (1086, 505), (1104, 525), (1123, 525), (1138, 512), (1153, 473), (1160, 465), (1171, 465), (1190, 482), (1200, 496), (1200, 504), (1101, 554), (1050, 564), (957, 574), (918, 570), (893, 559), (817, 512), (762, 472), (678, 382), (659, 386), (650, 377), (652, 363), (511, 185), (495, 178), (468, 174), (414, 186), (367, 208), (337, 234), (333, 267), (265, 329), (257, 332), (238, 322), (216, 333), (172, 391), (155, 437), (159, 481), (156, 484), (152, 485), (133, 464), (117, 437), (117, 431), (128, 421), (160, 363), (205, 312), (263, 254), (294, 229)], 
                          [(281, 214), (368, 158), (415, 138), (470, 133), (512, 145), (530, 160), (559, 195), (644, 278), (676, 324), (745, 373), (805, 444), (820, 457), (848, 465), (875, 466), (895, 455), (908, 439), (917, 387), (931, 371), (953, 360), (976, 360), (1157, 383), (1168, 397), (1170, 407), (1162, 423), (1148, 433), (1137, 441), (1116, 475), (1109, 489), (1108, 500), (1115, 505), (1120, 498), (1124, 487), (1141, 448), (1156, 442), (1170, 443), (1206, 471), (1220, 491), (1220, 516), (1108, 573), (1055, 584), (957, 595), (913, 592), (885, 577), (809, 529), (752, 489), (673, 404), (653, 406), (630, 384), (629, 368), (500, 201), (492, 197), (467, 195), (419, 206), (378, 225), (355, 245), (350, 278), (275, 347), (259, 354), (238, 346), (227, 352), (191, 400), (176, 441), (179, 485), (162, 507), (145, 503), (117, 477), (94, 433), (99, 419), (113, 410), (143, 352), (188, 299), (250, 239), (281, 214)]]
        gameMap = self.scaleMap(self.mapShapes, 10)
        self.trackLine = gameMap[0]
        self.interiorWall = gameMap[1]
        self.exteriorWall = gameMap[2]
    
        # enlarged map
        # self.mapShapes = [[(1445, 1105), (1865, 830), (2090, 735), (2340, 720), (2535, 770), (2610, 830), (2750, 1000), (3180, 1420), (3350, 1655), (3700, 1900), (3995, 2255), (4090, 2335), (4235, 2375), (4395, 2380), (4510, 2330), (4585, 2225), (4635, 1960), (4690, 1890), (4770, 1850), (4870, 1850), (5765, 1965), (5805, 2035), (5785, 2125), (5720, 2175), (5645, 2225), (5605, 2330), (5565, 2405), (5530, 2455), (5520, 2495), (5545, 2525), (5615, 2520), (5635, 2450), (5715, 2255), (5770, 2230), (5830, 2245), (5990, 2385), (6050, 2470), (6055, 2540), (5515, 2815), (5265, 2870), (4785, 2920), (4575, 2905), (4440, 2835), (4065, 2595), (3785, 2395), (3375, 1960), (3285, 1985), (3200, 1905), (3205, 1830), (2525, 960), (2465, 930), (2335, 920), (2085, 980), (1860, 1080), (1725, 1205), (1705, 1370), (1350, 1690), (1285, 1710), (1185, 1665), (1105, 1705), (905, 1980), (830, 2195), (845, 2415), (795, 2480), (745, 2470), 
        #                    (620, 2335), (515, 2155), (530, 2125), (600, 2080), (755, 1785), (980, 1525), (1285, 1230), (1445, 1100)], [(1460, 1125), (1880, 850), (2100, 750), (2345, 740), (2525, 790), (2600, 850), (2725, 1000), (3175, 1450), (3335, 1675), (3690, 1915), (3970, 2265), (4090, 2360), (4230, 2400), (4410, 2405), (4525, 2345), (4605, 2240), (4655, 1970), (4705, 1910), (4775, 1875), (4870, 1870), (5765, 1990), (5785, 2040), (5770, 2120), (5640, 2220), (5565, 2380), (5525, 2445), (5505, 2500), (5530, 2535), (5570, 2540), (5630, 2535), (5730, 2275), (5775, 2255), (5820, 2265), (5980, 2400), (6030, 2475), (6045, 2530), (5525, 2800), (5270, 2855), (4795, 2905), (4585, 2890), (4055, 2570), (3785, 2375), (3395, 1955), (3370, 1950), (3290, 1960), (3225, 1900), (3230, 1840), (3220, 1810), (2540, 955), (2465, 920), (2335, 905), (2075, 965), (1855, 1060), (1710, 1205), (1690, 1370), (1355, 1670), (1290, 1690), 
        #                     (1190, 1655), (1090, 1690), (890, 1980), (810, 2210), (820, 2365), (830, 2415), (785, 2465), (750, 2460), (630, 2325), (535, 2170), (540, 2145), (620, 2095), (765, 1800), (970, 1555), (1275, 1270), (1460, 1125)], [(1445, 1090), (1890, 805), (2095, 720), (2350, 705), (2550, 755), (2620, 815), (2765, 995), (3195, 1415), (3355, 1640), (3720, 1900), (4000, 2240), (4095, 2320), (4235, 2365), (4390, 2360), (4500, 2320), (4575, 2220), (4620, 1960), (4680, 1885), (4770, 1835), (4885, 1830), (5780, 1960), (5825, 2035), (5805, 2145), (5660, 2245), (5610, 2365), (5545, 2465), (5540, 2495), (5550, 2510), (5605, 2500), (5695, 2250), (5780, 2220), (5850, 2240), (6005, 2375), (6070, 2470), (6075, 2550), (5530, 2835), (5280, 2890), (4805, 2940), (4565, 2930), (3935, 2535), (3780, 2420), (3370, 1985), (3285, 2010), (3175, 1905), (3190, 1830), (2510, 975), (2460, 955), (2330, 940), (2095, 1000), (1870, 1105), (1740, 1220), (1725, 1385), (1365, 1710), (1280, 1720), (1195, 1690), (1120, 1720), (925, 1990), (850, 2185), (860, 2430), (805, 2500), (745, 2495), (620, 2365), (500, 2170), (515, 2120), (590, 2075), (740, 1780), (915, 1575), (1250, 1245), (1445, 1090)]]
        # self.trackLine = self.mapShapes[0]
        # self.interiorWall = self.mapShapes[1]
        # self.exteriorWall = self.mapShapes[2]
        
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

    def draw(self, app, canvas):
        if app.screen == "selection":
            canvas.create_line(self.trackLine, width=20, fill="grey")
            #canvas.create_line(self.exteriorWall, width=2, fill="red")
            #canvas.create_line(self.interiorWall, width=2, fill="red")
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
        else:
            canvas.create_line(self.trackLine, fill="grey", width=200)
            canvas.create_line(self.trackLine, fill="black", width=3)
            canvas.create_line(self.interiorWall, fill="black", width=5)
            canvas.create_line(self.exteriorWall, fill="black", width=5)

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
    
    def scaleMap(self, point, scale):
        result = []
        for shape in self.mapShapes:
            new = []
            for x, y in shape:
                x *= scale
                y *= scale
                new.append((x, y))
            result.append(new)
        return result

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