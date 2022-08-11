class Button:
    def __init__(self, name, x, y, width, height, fill="white", outline="black"):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.fill = fill
        self.outline = outline
    
    # updates button rectangle points relative to center
    def updatePosition(self):
        self.x1 = self.x - self.width
        self.y1 = self.y - self.height
        self.x2 = self.x + self.width
        self.y2 = self.y + self.height
    
    # returns True if button was clicked
    def pressed(self, cx, cy):
        self.updatePosition()
        return (self.x1 < cx and cx < self.x2 and self.y1 < cy and cy < self.y2)
    
    # draws button on canvas
    def draw(self, canvas):
        self.updatePosition()
        # box
        canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2,
                                fill=self.fill, outline=self.outline)
        # text
        canvas.create_text(self.x, self.y, text=self.name)
    
    