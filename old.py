from cmu_112_graphics import *
from tkinter import *
import math, random

def appStarted(app):
    # start game
    app.screen = "menu"
    app.timerDelay = 1000//60
    # create menu screen
    menuButtons = createMenuButtons(app)
    app.menu = Menu('menu', menuButtons)
    # create selection screen
    selectionButtons = createSelectionButtons(app)
    app.selection = Selection('selection', selectionButtons)
    # create game screen
    map1 = Map()
    app.game = Game('game', [], map1)
    app.zoom = 1
    # create player car
    xStart, yStart = app.game.map.cx, app.game.map.cy
    app.player = Player(app, 'player', xStart+10, yStart+30)
    # app.enemy = Enemy(app, 'enemy1', xStart-40, yStart+60)
    app.cars = [app.player]
    image = app.loadImage("f1car.png")
    app.image = app.scaleImage(image, 0.1)
    monaco = app.loadImage("monacoTrack.jpeg")
    app.monaco = app.scaleImage(monaco, 1)
    pass

def redrawAll(app, canvas):
    if app.screen == "menu":
        drawMenu(app, canvas)
    elif app.screen == "selection":
        image = ImageTk.PhotoImage(app.monaco)
        canvas.create_image(app.width//2, app.height//2, image=image)
        drawSelection(app, canvas)
        app.game.draw(app, canvas)
    elif app.screen == "game":
        app.game.draw(app, canvas)
        # player (currently enemy for testing)
        app.player.draw(app, canvas)
        # app.enemy.draw(app, canvas)
        # app.player.selfDrive(app)
        # app.player.checkpoints(app, canvas)
        # app.player.visualizeOffTrack(app, canvas)
        # app.player.visualizeSelfDrive(app, canvas)
        canvas.scale(ALL, app.player.cx, app.player.cy, 3, 3)
        #app.player.rayCast(canvas)

def timerFired(app):
    if app.screen == "game":
        app.player.move(app)
        # app.enemy.move(app)

def mousePressed(app, event):
    app.game.map.movePoint(app, (event.x, event.y))
    print(event.x, event.y)
    if app.screen == "menu":
        app.menu.checkForPress(app, event.x, event.y)
    elif app.screen == "selection":
        app.selection.checkForPress(app, event.x, event.y)
    elif app.screen == "game":
        pass

def keyPressed(app, event):
    if event.key == "w": app.player.pressedW()
    if event.key == "a": app.player.pressedA()
    if event.key == "d": app.player.pressedD()
    if event.key == "Space": print(app.game.map.points)

def keyReleased(app, event):
    if event.key == "w": app.player.releasedW()
    if event.key == "a": app.player.releasedA()
    if event.key == "d": app.player.releasedD()

###########
# DRAW MENU
###########

def drawMenu(app, canvas):
    drawTitle(app, canvas)
    app.menu.draw(app, canvas)

def drawTitle(app, canvas):
    canvas.create_text(app.width//2, app.height//3, text="Title",
                       font=f"Modern 18", anchor="n")

def createMenuButtons(app):
    start = Button("start", "Start", app.width//2, app.height//2, app.width//16,
                   app.height//20, "grey", "white", "Modern 12")
    end = Button("end", "Quit", app.width//2, app.height//1.6, app.width//16,
                 app.height//20, "grey", "white", "Modern 12")
    return [start, end]

################
# DRAW SELECTION
################

# have all three screens and switch between so that high scores are remembered

def drawSelection(app, canvas):
    app.selection.draw(app, canvas)
    #canvas.create_rectangle()
    pass

def createSelectionButtons(app):
    play = Button("play", "Play", app.width//8, app.height//1.3, app.width//16,
                   app.height//20, "grey", "white", "Modern 12")
    back = Button("back", "Back", app.width//8, app.height//1.1, app.width//16,
                   app.height//20, "grey", "white", "Modern 12")     
    return [play, back]

#########
# SCREENS
#########

class Screen:
    def __init__(self, name, buttons):
        self.name = name
        self.buttons = buttons # store list of buttons in screen object

    def draw(self, app, canvas):
        # draw buttons
        for button in self.buttons:
            button.draw(app, canvas)

class Menu(Screen):
    def __init__(self, name, buttons):
        super().__init__(name, buttons)

    def checkForPress(self, app, x, y):
        for button in self.buttons:
            if button.pressed(x, y):
                if button.name == "start":
                    app.screen = "selection"
                elif button.name == "end":
                    app.quit()

class Selection(Screen):
    def __init__(self, name, buttons):
        super().__init__(name, buttons)
        self.mapIndex = 0
    
    def checkForPress(self, app, x, y):
        for button in self.buttons:
            if button.pressed(x, y):
                if button.name == "play":
                    app.screen = "game"
                elif button.name == "back":
                    app.screen = "menu"

class Game(Screen):
    def __init__(self, name, buttons, map):
        super().__init__(name, buttons)
        self.map = map
    
    def draw(self, app, canvas):
        self.map.draw(app, canvas)

#########
# BUTTONS
#########

class Button:
    def __init__(self, name, text, cx, cy, width, height, color, outline, font):
        self.name = name
        self.text = text
        self.cx = cx
        self.cy = cy
        self.width = width
        self.height = height
        self.color = color
        self.outline = outline
        self.font = font
    def draw(self, app, canvas):
        canvas.create_rectangle(self.cx-self.width, self.cy-self.height,
                                self.cx+self.width, self.cy+self.height,
                                fill=self.color, outline=self.outline)
        canvas.create_text(self.cx, self.cy, fill=self.outline, 
                           text=self.text, font=self.font)
    def pressed(self, x, y):
        if (self.cx-self.width < x and x < self.cx+self.width
        and self.cy-self.height < y and y < self.cy+self.height):
            return True
        return False

######
# MAPS
######

class Map:
    def __init__(self, name="map1"):
        self.name = name
        self.points = self.map()
        self.width = 4
        self.zoomWidth = self.width*70
        self.selected = None
        self.cx, self.cy, self.angle = 0, 0, 0
        self.raceline = []
        self.getRaceline()

    # standardize maps at 1280x720 resolution
    # first and last points make raceline
    # map maker
    def movePoint(self, app, click):
        if self.selected:
            for index, point in enumerate(self.points):
                if point == self.selected:
                    self.points[index] = click
                    self.selected = None
        else:
            for point in self.points:
                if distance(point, click) < 5:
                    self.selected = point

    def map(self):
        mapPoints = [(320, 350), (290, 315), (100, 290), (120, 250), (70, 190),
                    (110, 60), (200, 30), (280, 75), (340, 175), (400, 210),
                    (510, 175), (610, 170), (730, 230), (675, 310), (610, 280),
                    (600, 340), (320, 350)]

        monaco = [(400, 50), (424, 47), (448, 54), (467, 70), (686, 271), (733, 285), (761, 263), (787, 234), (796, 192), (819, 160), (986, 110), (1023, 126), (1041, 157), (1028, 186), (949, 261), (914, 300), (914, 334), (936, 346), (977, 343), (1031, 323), (1056, 330), (1077, 376), (1074, 398), (1058, 420), (867, 494), (816, 490), (757, 473), (694, 422), (641, 380), (601, 374), (554, 336), (541, 297), (460, 214), (420, 205), (354, 258), (350, 297), (277, 352), (234, 353), (202, 375), (178, 451), (154, 477), (127, 477), (44, 362), (46, 338), (62, 320), (88, 310), (400, 50)]
        # scaling
        newPoints = []
        for point in monaco:
            newPoints.append((point[0]*1, point[1]*1))
        return newPoints

    def draw(self, app, canvas):
        if app.screen == "selection":
            canvas.create_line(self.points, fill="grey", width=30)
            canvas.create_line(self.points, fill="blue", width=self.width)
            for x, y in self.points:
                r = 5
                if (x, y) == self.selected:
                    canvas.create_oval(x-r, y-r, x+r, y+r, fill="orange")
                else:
                    canvas.create_oval(x-r, y-r, x+r, y+r, fill="blue")
        elif app.screen == "game":
            # grass
            canvas.create_rectangle(0, 0, app.width, app.height, fill="PaleGreen3")
            # barrier
            canvas.create_line(self.points, fill="white", width=self.zoomWidth+10)
            #canvas.create_line(self.points, fill="coral1", dash=(30, 30), width=self.zoomWidth+10)
            # grass
            canvas.create_line(self.points, fill="PaleGreen3", width=self.zoomWidth)
            # track
            canvas.create_line(self.points, fill="grey", width=self.zoomWidth-50)
            # track marker
            canvas.create_line(self.points, fill="black", dash=(10, 5), width=3)
            # raceline
            canvas.create_polygon(self.raceline, fill="black")

    def getRaceline(self):
        p1 = self.points[0]
        p2 = self.points[-2]
        rise = (p1[1] - p2[1]) 
        run = (p1[0] - p2[0])
        self.angle = math.degrees(math.atan2(rise, run))

        self.cx, self.cy = (p1[0]+p2[0])/2, (p1[1]+p2[1])/2
        l, w = 30, 10
        topLeft = (self.cx-w, self.cy-l)
        topRight = (self.cx+w, self.cy-l)
        bottomRight = (self.cx+w, self.cy+l)
        bottomLeft = (self.cx-w, self.cy+l)
        self.raceline = [topLeft, topRight, bottomRight, bottomLeft]
        self.raceline = rotatePolygon(self.raceline, (self.cx, self.cy), self.angle)
        return self.cx, self.cy, self.angle

######
# CARS
######

class Car:
    def __init__(self, app, name, cx, cy):
        self.app = app
        self.name = name
        self.cx = cx
        self.cy = cy
        self.acceleration = 0
        self.accelerating = False
        self.rotation = 0
        self.rotating = False
        self.angle = 0
        self.position = []
        self.getPosition()
        self.trackWidth = app.game.map.zoomWidth//7
        self.color = "white"

    # draws car on canvas
    def draw(self, app, canvas):
        canvas.create_polygon(self.position, fill=self.color)
        #image = ImageTk.PhotoImage(app.image.rotate(-self.angle, expand=True)) 
        #canvas.create_image(self.cx, self.cy, image=image)
    
    # updates car position after acceleration/angle changes
    def move(self, app):
        self.angle = self.getAngle()
        if self.accelerating and self.acceleration < 20:
                self.acceleration += 1
        elif self.acceleration != 0:
            self.acceleration -= 1
        if self.rotating:
            self.rotate()
        if self.offTrack(app, (self.cx, self.cy)): 
            # find perpendicular line to car slope
            x1, y1 = self.position[0]
            x2, y2 = self.position[1]
            dy, dx = y1-y2, x1-x2
            #slope = -1 * dx / dy
            if self.color != "red":
                if (0 < self.angle and self.angle < 90):
                    self.rotation = -90
                elif (90 < self.angle and self.angle < 180):
                    self.rotation = 90
                elif (-90 < self.angle and self.angle < 0):
                    self.rotation = 90
                elif (-180 < self.angle and self.angle < -90):
                    self.rotation = -90
                self.rotate()
                self.acceleration = self.acceleration // 2
            self.color = "red"
        else: 
            self.color = "white"
        self.updatePosition()
        self.checkCarCollision(app)
    
    def rayCast(self, canvas):
        x1, y1 = self.position[0]
        x2, y2 = self.position[1]
        slope = (y1-y2) / (x1-x2)
        intercept = y1 - slope*x1
        if (-90 < self.angle and self.angle < 90):
            x3 = self.cx + 100
            y3 = slope*x3 + intercept
        elif (self.angle < -90 or self.angle > 90):
            x3 = self.cx - 100
            y3 = slope*x3 + intercept
        else:
            x3 = self.cx
            if self.angle == 90:
                y3 = app.height
            else:
                y3 = 0
        canvas.create_line(self.cx, self.cy, x3, y3)

    # creates four vertices of car rectangle from center
    def getPosition(self):
        l, w = 5, 10
        topLeft = (self.cx-w, self.cy-l)
        topRight = (self.cx+w, self.cy-l)
        bottomRight = (self.cx+w, self.cy+l)
        bottomLeft = (self.cx-w, self.cy+l)
        position = [topLeft, topRight, bottomRight, bottomLeft]
        self.position = rotatePolygon(position, (self.cx, self.cy), 140)

    # checks if car collided with another car
    def checkCarCollision(self, app):
        for other in app.cars:
            if self.name != other.name:
                if do_polygons_intersect(self.position, other.position):
                    #slope = other.cy - self.cy / other.cx - self.cx
                    #self.angle = math.tan(slope)
                    self.acceleration = -self.acceleration
                    other.acceleration = -self.acceleration

    # updates position of car based on angle and acceleration
    def updatePosition(self):
        self.cx, self.cy = self.newPosition((self.cx, self.cy), self.angle, self.acceleration)
        for index, point in enumerate(self.position):
            self.position[index] = self.newPosition(point, self.angle, self.acceleration)

    # calculates new position of point based on angle and acceleration
    def newPosition(self, point, angle, acceleration):
        x = point[0] + math.cos(math.radians(angle)) * (acceleration // 6)
        y = point[1] + math.sin(math.radians(angle)) * (acceleration // 6)
        return (x, y)

    # gets angle of car
    def getAngle(self):
        (x1, y1), (x2, y2) = self.position[0], self.position[1]
        # avoids division by zero for car angle facing directly up and down
        if x1 - x2 == 0:
            if self.angle > 0:
                angle = 90
            else:
                angle = -90
        else:
            angle = math.degrees(math.atan2(y1 - y2, x1 - x2))
        return angle
    
    # rotate car points 
    def rotate(self):
        self.position = rotatePolygon(self.position, (self.cx, self.cy), self.rotation)
    
    # checks if point if off track
    def offTrack(self, app, point):
        distances = self.distFromCarToTrack(app, point)
        if len(distances) > 0 and min(distances) > self.trackWidth:
            return True
        return False

    # find distances from car to track
    def distFromCarToTrack(self, app, center):
        distances = []
        trackPoints = app.game.map.points
        # distance from car center to track lines
        for i in range(1, len(trackPoints)):
            p1 = trackPoints[i-1]
            p2 = trackPoints[i]
            p3 = self.pointPerpendicularToCar(p1, p2, center)
            if p3[0] > min(p1[0], p2[0]) and p3[0] < max(p1[0], p2[0]):
                distances.append(self.distFromPointToLine(p1, p2, center))
        # distance from car center to track vertices
        for point in trackPoints:
            distances.append(distance(center, point))
        return distances
    
    # calculates point on line perpendicular to car center
    def pointPerpendicularToCar(self, p1, p2, center):
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = center
        dx, dy = x2-x1, y2-y1
        det = dx*dx + dy*dy
        a = (dy*(y3-y1) + dx*(x3-x1)) / det
        return x1+a*dx, y1+a*dy
    
    # finds distance from line (coordinates p1 and p2) to car center
    def distFromPointToLine(self, p1, p2, center):
        # convert line points to standard form
        x1, y1 = p1
        x2, y2 = p2
        a = (y1-y2)
        b = (x2-x1)
        c = (x1*y2 - x2*y1)
        # find distance
        cx, cy = center
        if a*a + b*b == 0:
            return 100 # why am i returning 100?
        d = abs((a*cx + b*cy + c)) / ((a * a + b * b)**0.5) 
        return d

    # debug off track algorithm
    def visualizeOffTrack(self, app, canvas):
        trackPoints = app.game.map.points
        for i in range(1, len(trackPoints)):
            p1 = trackPoints[i-1]
            p2 = trackPoints[i]
            p3 = self.pointPerpendicularToCar(p1, p2, (self.cx, self.cy))
            if p3[0] > min(p1[0], p2[0]) and p3[0] < max(p1[0], p2[0]):
                canvas.create_line((self.cx, self.cy), p3, fill="blue")
        # for point in trackPoints:
        #     canvas.create_line((self.cx, self.cy), point, fill="orange")

class Player(Car):
    # player controls
    def pressedW(self):
        self.accelerating = True
    def releasedW(self):
        self.accelerating = False
    def pressedA(self):
        self.rotating = True
        self.rotation = -3
    def releasedA(self):
        self.rotating = False
    def pressedD(self):
        self.rotating = True
        self.rotation = 3
    def releasedD(self):
        self.rotating = False

class Enemy(Car):
    # initalize first checkpoint
    def __init__(self, app, name, cx, cy):
        super().__init__(app, name, cx, cy)
        self.checkpoint = (app.game.map.points[0][0], app.game.map.points[0][1])
    # enemy driving
    def selfDrive(self, app):
        leftPos, rightPos = self.checkFuturePosition()
        # get future positions of car after left/right shift
        leftDist = distance(leftPos, self.checkpoint)
        rightDist = distance(rightPos, self.checkpoint)
        # checks whether moving left or right places the car closer to the next checkpoint
        # (distance must be signficant, >10, to reduce wiggling)
        if leftDist - rightDist < -app.game.map.width*2:
            self.rotating = True
            self.rotation = -5
        elif leftDist - rightDist > app.game.map.width*2:
            self.rotating = True
            self.rotation = 5
        else:
            self.rotating = False
        self.accelerating = True
    # creates sensors: possible future positions of car after left/right shift
    def checkFuturePosition(self):
        left = self.newPosition((self.cx, self.cy), self.angle-30, 200)
        right = self.newPosition((self.cx, self.cy), self.angle+30, 200)
        return left, right
    # creates checkpoints at track vertices to guide car
    def checkpoints(self, app, canvas):
        for i in range(len(app.game.map.points)):
            r = self.trackWidth
            # after car reaches checkpoint changes to next checkpoint
            print(distance((self.cx, self.cy), app.game.map.points[i]))
            if distance((self.cx, self.cy), app.game.map.points[i]) < r:
                print('new checkpoint')
                self.checkpoint = app.game.map.points[i+1]
                break
    # debug self drive
    def visualizeSelfDrive(self, app, canvas):
        # draw checkpoints
        for point in app.game.map.points:
            x, y = point
            r = self.trackWidth
            if point == self.checkpoint:
                canvas.create_oval(x-r, y-r, x+r, y+r, outline="orange", width=3)
            else:
                canvas.create_oval(x-r, y-r, x+r, y+r, outline="purple", width=3)
        # draw sensors
        left = self.newPosition((self.cx, self.cy), self.angle-30, 200)
        right = self.newPosition((self.cx, self.cy), self.angle+30, 200)
        for x, y in (left, right):
            canvas.create_oval(x-1, y-1, x+1, y+1, fill="white")

##################
# HELPER FUNCTIONS
##################

# calculates distance between two points
def distance(p1, p2):
    return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5

# rotates polygon by an angle
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

def do_polygons_intersect(a, b): # UNDERSTAND
    polygons = [a, b]
    minA, maxA, projected, i, i1, j, minB, maxB = None, None, None, None, None, None, None, None
    for i in range(len(polygons)):
        # for each polygon, look at each edge of the polygon, and determine if it separates
        # the two shapes
        polygon = polygons[i]
        for i1 in range(len(polygon)):
            # grab 2 vertices to create an edge
            i2 = (i1 + 1) % len(polygon)
            p1 = polygon[i1]
            p2 = polygon[i2]
            # find the line perpendicular to this edge
            normal = { 'x': p2[1] - p1[1], 'y': p1[0] - p2[0] }
            minA, maxA = None, None
            # for each vertex in the first shape, project it onto the line perpendicular to the edge
            # and keep track of the min and max of these values
            for j in range(len(a)):
                projected = normal['x'] * a[j][0] + normal['y'] * a[j][1];
                if (minA is None) or (projected < minA): 
                    minA = projected
                if (maxA is None) or (projected > maxA):
                    maxA = projected
            # for each vertex in the second shape, project it onto the line perpendicular to the edge
            # and keep track of the min and max of these values
            minB, maxB = None, None
            for j in range(len(b)): 
                projected = normal['x'] * b[j][0] + normal['y'] * b[j][1]
                if (minB is None) or (projected < minB):
                    minB = projected
                if (maxB is None) or (projected > maxB):
                    maxB = projected
            # if there is no overlap between the projects, the edge we are looking at separates the two
            # polygons, and we know there is no overlap
            if (maxA < minB) or (maxB < minA):
                return False
    return True

runApp(width=1280, height=720)