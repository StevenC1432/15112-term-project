from cmu_112_graphics import *

def appStarted(app):
    app.line = [(100, 400), (300, 300), (400, 500)]
    pass

def redrawAll(app, canvas):
    canvas.create_line(app.line, fill="lightgrey", width=100)
    canvas.create_line(app.line)
    outsidePoints(app, canvas, app.line)
    
def outsidePoints(app, canvas, line):
    x1, y1 = line[0][0], line[0][1]
    x2, y2 = line[1][0], line[1][1]
    x3, y3 = line[2][0], line[2][1]
    
    # account for division by 0
    slope1 = (x1-x2) / (y1-y2)
    slope2 = (x2-x3) / (y2-y3)
    averageSlope = -(slope1 + slope2) / 2
    
    intercept = y2 - averageSlope * x2
    
    newX = x2 - 50
    newY = averageSlope * newX + intercept
    canvas.create_line(x2, y2, newX, newY)
    
runApp(width=500, height=500)