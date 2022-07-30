class Map:
    def __init__(self):
        self.mapShapes = []
        self.currentShape = []
        self.drawing = True
        self.selectedIndex = None
        
    def input(self, inputType, action):
        if inputType == "keyPress":
            if action == "r": self.removePoint()
            elif action == "s": self.saveShape()
            elif action == "p": self.printShapes()
            elif action == "m": self.changeMode()
        elif inputType == "mousePress":
            if self.drawing: self.addPoint(action)
            else: self.movePoint(action)

    def draw(self, canvas):
        if len(self.currentShape) > 2:
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