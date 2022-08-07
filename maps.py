from helper import *

import math

class Map:
    def __init__(self):
        self.inDrawMode = True
        self.displayDots = True
        self.selectedIndex = []
        
        self.trackLine = [(689, 544), (547, 524), (532, 522), (525, 519), (520, 516), (515, 510), (511, 504), (507, 492), (503, 484), (498, 478), (490, 474), (480, 470), (470, 468), (457, 466), (368, 454), (355, 450), (312, 434), (302, 431), (241, 409), (234, 405), (229, 400), (227, 395), (228, 388), (230, 384), (234, 379), (255, 362), (260, 356), (262, 350), (261, 343), (259, 338), (256, 334), (223, 306), (215, 297), (210, 288), (207, 280), (205, 272), (205, 260), (206, 253), (208, 244), (210, 233), (213, 223), (218, 211), (246, 150), (261, 123), (263, 116), (267, 100), (269, 95), (273, 92), (279, 91), (305, 89), (311, 88), (316, 86), (337, 73), (347, 67), (356, 63), (367, 60), (380, 58), (394, 58), (406, 59), (421, 63), (432, 68), (443, 75), (528, 152), (531, 159), (531, 163), (529, 167), (518, 180), (516, 186), (515, 193), (516, 200), (519, 208), (546, 253), (552, 261), (568, 283), (575, 291), (588, 305), (611, 325), (622, 332), (634, 339), (650, 345), (670, 351), (681, 353), (727, 359), (750, 360), (763, 359), (769, 357), (773, 355), (778, 350), (804, 319), (807, 317), (812, 315), (820, 314), (891, 316), (912, 318), (937, 323), (951, 327), (963, 333), (1060, 399), (1067, 407), (1072, 414), (1075, 422), (1076, 432), (1076, 439), (1073, 447), (1029, 519), (1022, 524), (1014, 525), (1005, 525), (995, 521), (962, 501), (949, 496), (938, 495), (929, 495), (920, 499), (916, 504), (914, 513), (912, 547), (910, 553), (907, 558), (901, 563), (894, 565), (887, 566), (876, 566), (689, 544)]
        self.interiorWall = [(689, 518), (564, 502), (549, 500), (542, 497), (537, 494), (532, 488), (529, 482), (523, 468), (519, 462), (513, 455), (506, 450), (496, 446), (486, 444), (473, 442), (368, 427), (355, 423), (312, 407), (302, 404), (286, 398), (279, 394), (274, 389), (272, 384), (273, 377), (275, 373), (279, 368), (283, 362), (286, 356), (287, 348), (286, 341), (284, 332), (276, 319), (260, 306), (250, 298), (240, 288), (234, 280), (230, 271), (229, 262), (231, 252), (233, 242), (235, 233), (238, 223), (243, 211), (263, 170), (276, 145), (282, 130), (286, 122), (288, 117), (292, 114), (298, 113), (307, 113), (313, 112), (318, 110), (335, 102), (345, 96), (354, 92), (365, 87), (378, 84), (392, 83), (404, 84), (417, 88), (429, 96), (440, 105), (492, 154), (495, 161), (496, 167), (495, 173), (492, 184), (490, 190), (489, 197), (490, 204), (493, 212), (514, 253), (525, 269), (535, 283), (547, 299), (563, 319), (582, 338), (603, 352), (624, 364), (647, 372), (670, 376), (694, 380), (738, 384), (761, 385), (774, 384), (780, 382), (784, 380), (789, 375), (813, 346), (818, 341), (823, 339), (831, 338), (903, 341), (921, 344), (937, 349), (951, 356), (963, 364), (1027, 408), (1034, 415), (1039, 422), (1042, 430), (1043, 438), (1043, 445), (1040, 453), (1020, 485), (1014, 490), (1006, 491), (996, 490), (987, 486), (953, 470), (941, 466), (930, 466), (919, 468), (909, 473), (900, 480), (894, 489), (890, 501), (888, 524), (887, 532), (884, 536), (880, 538), (876, 539), (853, 537), (689, 518)]
        self.exteriorWall = [(688, 571), (528, 550), (518, 548), (507, 545), (500, 541), (494, 534), (489, 525), (486, 516), (482, 508), (477, 502), (469, 498), (459, 494), (449, 492), (436, 490), (396, 486), (359, 479), (317, 465), (280, 452), (221, 431), (209, 422), (201, 411), (198, 398), (199, 386), (204, 373), (210, 363), (219, 354), (222, 347), (220, 340), (214, 333), (205, 326), (198, 319), (192, 310), (187, 300), (182, 291), (178, 280), (176, 271), (176, 260), (177, 252), (179, 243), (181, 232), (184, 222), (189, 210), (210, 166), (225, 135), (236, 115), (241, 101), (243, 91), (248, 81), (254, 73), (265, 68), (300, 63), (305, 61), (310, 58), (347, 38), (356, 35), (369, 31), (384, 29), (399, 29), (413, 31), (427, 35), (442, 42), (459, 52), (551, 136), (556, 145), (558, 154), (558, 162), (556, 171), (552, 179), (546, 186), (544, 191), (545, 197), (551, 209), (556, 217), (572, 242), (579, 251), (592, 270), (614, 294), (626, 305), (638, 312), (654, 318), (674, 324), (685, 326), (727, 333), (742, 333), (749, 333), (755, 331), (760, 328), (766, 323), (791, 295), (798, 290), (808, 288), (816, 287), (894, 289), (915, 291), (940, 296), (954, 300), (972, 307), (1080, 378), (1092, 390), (1100, 404), (1104, 419), (1105, 430), (1103, 444), (1097, 458), (1049, 536), (1038, 545), (1023, 550), (1010, 552), (997, 550), (985, 545), (974, 539), (951, 525), (946, 524), (941, 526), (938, 531), (936, 551), (934, 563), (928, 574), (921, 582), (911, 589), (898, 593), (887, 593), (876, 593), (688, 571)]
        self.editingShape = []       
        self.gameMap = self.scalePolygon(self.trackLine, 10)
        self.miniMap = self.scalePolygon(self.trackLine, 0.3)
        self.interiorWall = self.scalePolygon(self.interiorWall, 10)
        self.exteriorWall = self.scalePolygon(self.exteriorWall, 10)
        
    def userInput(self, inputType, action):
        if inputType == "keyPress":
            if action == "a": self.addPoint()
            elif action == "r": self.removePoint()
            elif action == "p": print(self.editingShape)
            elif action == "m": self.inDrawMode = not self.inDrawMode
            elif action == "x": self.scaleMap(self.editingShape, 10)
            elif action == "d": self.selectedIndex = []
            elif action == "c": self.displayDots = not self.displayDots
            elif action == "Up": self.movePoints(0, -1)
            elif action == "Down": self.movePoints(0, 1)
            elif action == "Left": self.movePoints(-1, 0)
            elif action == "Right": self.movePoints(1, 0)   
        elif inputType == "mousePress":
            # draws new point
            if self.inDrawMode: self.addPoint(action)
            # selects existing point
            else: self.selectPoint(action)

    def draw(self, app, canvas):
        if app.screen == "selection":
            canvas.create_line(self.trackLine, fill="grey", width=30)
            # display current mode
            # mode = "Drawing" if self.inDrawMode else "Editing"
            # canvas.create_text(app.width//2, app.height-50, text=mode)
        elif app.screen == "game":
            # grass
            canvas.create_rectangle(0, 0, app.canvasWidth, app.canvasHeight, 
                                    fill="lightGreen")
            self.drawRaceTrack(canvas)
            self.drawRaceLine(canvas, self.gameMap)
    
    def drawRaceTrack(self, canvas):
        # track red/white indicators
        canvas.create_line(self.gameMap, fill="white", width=320)
        for i in range(1, len(self.gameMap)):
            p1, p2 = self.gameMap[i-1], self.gameMap[i]
            canvas.create_line(p1, p2, fill="red", dash=(50, 50), width=320)
        # trackbed
        canvas.create_line(self.gameMap, fill="grey", width=300)
        # track center line markings
        for i in range(1, len(self.gameMap)):
            p1, p2 = self.gameMap[i-1], self.gameMap[i]
            canvas.create_line(p1, p2, fill="black", dash=(10, 10), width=5)
        # barriers
        canvas.create_line(self.interiorWall, fill="grey", width=5)
        canvas.create_line(self.exteriorWall, fill="grey", width=5)

    def drawRaceLine(self, canvas, points):
        # align raceline to slope of track
        x, y = points[0][0]+400, points[0][1]+47
        x2, y2 = points[1][0]+400, points[1][1]+47
        slope = (x-x2) / (y-y2)
        # draw raceline
        self.alternatingSquares(canvas, x, y, slope, 0, 0)
        self.alternatingSquares(canvas, x, y, slope, 20, 1)
        
    def alternatingSquares(self, canvas, x, y, slope, shift, oddStart):
        l, w = 150, 10
        raceline = [(x-w-shift, y-l), (x-w-shift, y+l), 
                    (x+w-shift, y+l), (x+w-shift, y-l)]
        for i in range(16):
            raceline[1] = (x-w-shift, y+l - 20*i)
            raceline[2] = (x+w-shift, y+l - 20*i)
            block = raceline[:]
            block = rotatePolygon(block, (x, y), slope)
            if i%2 == oddStart: canvas.create_polygon(block, fill="black")
            else: canvas.create_polygon(block, fill="white")

    def drawEditingShape(self, canvas, shape, r=2):
        if len(shape) > 1:
            canvas.create_line(shape, width=1, fill="red")
            if self.displayDots:
                for index, point in enumerate(shape):
                    (x, y) = point
                    color = "white" if index in self.selectedIndex else "black"
                    canvas.create_oval(x-r, y-r, x+r, y+r, fill=color)

    def addPoint(self, clickedPoint=None):
        # draw mode: creates new point at mouseclick
        if self.inDrawMode: self.editingShape.append(clickedPoint)
        # edit mode: creates new point near selected point
        elif len(self.selectedIndex) == 1: 
            (x, y)= self.editingShape[self.selectedIndex[0]]
            self.editingShape.insert(self.selectedIndex[0], (x+10, y))
            self.selectedIndex = []
    
    def removePoint(self):
        # draw mode: removes last drawn point
        if self.inDrawMode and self.editingShape: self.editingShape.pop()
        # edit mode: removes selected point
        elif len(self.selectedIndex) == 1: 
            self.editingShape.pop(self.selectedIndex[0])
            self.selectedIndex = []

    # edit mode: selects clicked point
    def selectPoint(self, clickedPoint):
        if not self.inDrawMode:
            for currentIndex, (x, y) in enumerate(self.editingShape):
                if distance((x, y), (clickedPoint)) < 5:
                    self.selectedIndex.append(currentIndex)

    # edit mode: shifts selected points
    def movePoints(self, dx, dy):
        for index, (x, y) in enumerate(self.editingShape):
            if index in self.selectedIndex:
                self.editingShape[index] = (x+dx, y+dy)
                    
    # scales polygon by given factor
    def scalePolygon(self, polygon, scale):
        scaled = polygon[:]
        for index, (x, y) in enumerate(polygon):
            x *= scale
            y *= scale
            scaled[index] = (x, y)
        return scaled