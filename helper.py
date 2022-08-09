import math

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

# * ROTATE POLYGON
# * uses formula to rotate a 2D point 
# * https://en.wikipedia.org/wiki/Rotation_matrix#In_two_dimensions

# returns list of points rotated around given center and angle
def rotatePolygon(points, center, angle):
    cx, cy = center
    rotated = []
    angle = math.radians(angle)
    cos = math.cos(angle)
    sin = math.sin(angle)
    # rotates each point in polygon by {angle} radians around the center
    for px, py in points:
        x = px - cx
        y = py - cy
        newX = x*cos - y*sin
        newY = x*sin + y*cos
        rotated.append((newX + cx, newY + cy))
    return rotated

# * INTERSECTION OF TWO LINE SEGMENTS 
# * uses formula provided in Introduction to Algorithms, Third Edition
# * https://sd.blackball.lv/library/Introduction_to_Algorithms_Third_Edition_(2009).pdf
# * (33.1 pg 1036 line segment properties)

# returns true if line segments AB and CD
def linesIntersect(A, B, C, D):
    # finds 4 orientations that cover general and special cases
    or1 = orientation(A, B, C)
    or2 = orientation(A, B, D)
    or3 = orientation(C, D, A)
    or4 = orientation(C, D, B)
    # general case
    if or1 != or2 and or3 != or4:
        return True
    # special cases
    if or1 == 0 and pointOnLine(C, (A, B)):
        return True
    if or2 == 0 and pointOnLine(D, (A, B)):
        return True
    if or3 == 0 and pointOnline(A, (C, D)):
        return True
    if or4 == 0 and pointOnLine(B, (C, D)):
        return True
    return False

# finds orientation of a triplet of points as either collinear, clockwise,
# or counterclockwise
def orientation(A, B, C):
    Ax, Ay = A
    Bx, By = B
    Cx, Cy = C
    val = (By-Ay)*(Cx-Bx) - (Bx-Ax)*(Cy-By)
    if val == 0:
        return "collinear"
    elif val < 0:
        return "counterclockwise"
    else:
        return "clockwise"

# given a point and two segment endpoints checks if point is on line segment
def pointOnLine(point, line):
    lineP1, lineP2 = line[0], line[1]
    # point must be between x and y values of two endpoints
    if (point[0] <= max(lineP1[0], lineP2[0]) and 
        point[0] >= min(lineP1[0], lineP2[0]) and 
        point[1] <= max(lineP1[1], lineP2[1]) and 
        point[1] >= min(lineP1[1], lineP2[1])):
       return True
    return False

# finds coefficents of line in standard form given two points
# Ax + By + C = 0
def line(p1, p2):
    A = (p1[1] - p2[1])
    B = (p2[0] - p1[0])
    C = (p1[0]*p2[1] - p2[0]*p1[1])
    return A, B, -C

# finds intersection point between two lines or returns False if none
def intersectionPoint(l1, l2):
    d = l1[0] * l2[1] - l1[1] * l2[0]
    dx = l1[2] * l2[1] - l1[1] * l2[2]
    dy = l1[0] * l2[2] - l1[2] * l2[0]
    if d != 0:
        x = dx / d
        y = dy / d
        return x, y
    else:
        return False