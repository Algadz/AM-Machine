import math
import matplotlib.pyplot as plt
import sys
import re

radianToDegree = (360 / (2 * math.pi))
toolVector = [1, 0]  # Orientation of the tool
F = 0
feedrate = 1000  # mm/min


# Definition of the function used for point rotation

def get_magnitude(v1):  # return the magnitude of a given vector
    return math.sqrt((v1[0] * v1[0]) + (v1[1] * v1[1]))


def get_vector(p1, p2):  # Return a list containing vector coordinate from the input (start point, endpoint)
    return[p2[0] - p1[0], p2[1] - p1[1]]


def get_scalar_product(v1, v2):  # return the scalar product of two given vector
    return v1[0] * v2[0] + v1[1] * v2[1]


def get_determinant(v1, v2):  # return the determinant of two vector
    return v1[0] * v2[1] - v2[0] * v1[1]


def get_angle(v1, v2):  # return the trigonometric angle between two vector
    if get_determinant(v1, v2) >= 0:
        return math.acos(get_scalar_product(v1, v2) / (get_magnitude(v1) * get_magnitude(v2)))

    if get_determinant(v1, v2) < 0:
        return -math.acos(get_scalar_product(v1, v2) / (get_magnitude(v1) * get_magnitude(v2)))


def rotate_point(point, angle):  # return a point rotated of a given angle
    rotated_point = [0, 0]
    rotated_point[0] = point[0] * math.cos(angle) - point[1] * math.sin(angle)
    rotated_point[1] = point[0] * math.sin(angle) + point[1] * math.cos(angle)
    return rotated_point



class Line:
    def __init__(self, text):
        self.text = text
        self.g = None
        self.x = None
        self.y = None
        self.z = None
        self.e = None
        self.f = None
        self.m = None
        self.comment = None
        self.xt = None
        self.yt = None
        self.ct = None
        self.et = None

    def get_gcode(self):
        if len(re.findall("G([0|1])\s", self.text)) > 0:  # if G character exists assign its value, G2 not implemented
            self.g = re.findall("G([0|1])\s", self.text)[0]

        if self.g is not None:
            if len(re.findall("X(\+?-?\d*\.?\d*)", self.text)) > 0:  # assign value to x (+ - int and float accepted)
                self.x = re.findall("X(\+?-?\d*\.?\d*)", self.text)[0]

            if len(re.findall("Y(\+?-?\d*\.?\d*)", self.text)) > 0:  # assign value to y (+ - int and float accepted)
                self.y = re.findall("Y(\+?-?\d*\.?\d*)", self.text)[0]

            if len(re.findall("Z(\+?-?\d*\.?\d*)", self.text)) > 0:  # assign value to z (+ - int and float accepted)
                self.z = re.findall("Z(\+?-?\d*\.?\d*)", self.text)[0]

line = Line("#hello G1 X-0.53 Y548 Z0.3")
line.get_gcode()

print(line.g)
print(line.x)
print(line.y)
print(line.z)

print("fin")
sys.exit("End of test")

# TODO : Implémenter le code de reconnaissance de charactère pour G1 X Y etc.. qui vient ecrire dans les variables de l'instance de classe Line

class Gcode:
    def __init__(self, address):
        self.address = address
        self.textLineList = [] # list of text from gcode
        self.lineList=[] # list of Line instance

    def get_textline_list(self): # get a list of line from gcode
        # TODO : fonction qui donne une liste de ligne self.textLineList

        self.textLineList = ["#je suis un commentaire", "G1 X0.254 Y2.245 Z0 E0 F1500"]
        # TODO : STUB, à enlever une fois la fonction définie

    def get_line_list(self):
        for x in self.textLineList:
            self.lineList.append(Line(x)) # for each line in Gcode create a Line instance

    def get_c_axis(self):
        # TODO : get the two consecutive line where .point is not None
        # TODO : calculate the angle between the vector and the tool
        # TODO : write C axis in endpoint
        first_line = None
        second_line = None
        i = 0
        while i < len(self.lineList):
            if self.lineList[i].point is not None:
                first_line = i
            else :
                i += 1
        i += 1
        while i < len(self.lineList):
            if self.lineList[i] is not None:
                second_line = i
            else :
                i += 1

        print (first_line)
        print (second_line)








###definition des listes
O=[]
V=[]
MVMT=[]

### Calcul des rotations 0
### 0[i] correspond à l'angle entre le vecteur P[i+1]P[i+2] et u

i=0
while i < len(gcodeList):
    O.append(get_angle(get_vector(gcodeList[i + 1], gcodeList[i + 2]), toolVector))
    i=i+1
O.append(O[len(O)-1])
print(O)

### modification des angles 0 pour prendre en compte la 2pi periodicité

i = 0
while i < len(O):

    while abs(O[i - 1] - O[i]) > math.pi and O[i]>O[i-1]:
        O[i] = O[i] - 2 * math.pi


    while abs(O[i - 1] - O[i]) > math.pi and O[i]<O[i-1]:
        O[i] = O[i] + 2 * math.pi

    i = i + 1

print(O)


### Calcul des déplacements correctifs aux rotations
### V[i] correspont au vecteur correctif associé à la rotation O[i] du point P[i+1]

i=0
while i<len(gcodeList)-1:
    V.append(get_vector(rotate_point(gcodeList[i + 1], O[i]), [0, 0]))
    i=i+1
"print(V)"



### Ecriture des position XYC absolue successives


i=0
while i<len(gcodeList)-1:
    X=V[i][0]
    Y=V[i][1]
    C=O[i]
    MVMT.append([X,Y,C])
    i=i+1




### ecriture des position X et y et C successives pour représentation
AxeX=[]
AxeY=[]

AxeXt=[]
AxeYt=[]
AxeCt=[]
i=0
while i<len(MVMT):
    AxeX.append(gcodeList[i][0])
    AxeY.append(gcodeList[i][1])


    AxeXt.append(MVMT[i][0])
    AxeYt.append(MVMT[i][1])
    AxeCt.append(MVMT[i][2])
    i=i+1

plt.scatter(AxeX,AxeY,s=100)
plt.title('Nuage de points')
plt.xlabel('x')
plt.ylabel('y')
plt.savefig('cercle.png')
plt.show()

plt.scatter(AxeXt,AxeYt,s=100)
plt.title('Nuage de points')
plt.xlabel('x')
plt.ylabel('y')
plt.savefig('cercle2.png')
plt.show()

#### fin de l'impression

### Calcul des vitesses vrai des axes X Y
vitXY=[]
vitC=[]
i=0
while i<len(MVMT)-1:
    vitXY.append((get_magnitude(get_vector(MVMT[i], MVMT[i + 1])) / (get_magnitude(get_vector(gcodeList[i + 1], gcodeList[i])))) * feedrate)
    print("norme nouveaux", (get_magnitude(get_vector(MVMT[i], MVMT[i + 1]))))
    print("norme origine", get_magnitude(get_vector(gcodeList[i + 1], gcodeList[i])))
    print("feedrate", i, vitXY[i])
    i=i+1

print(("--------"))
"""i=0
while i<len(MVMT):
    print(MVMT[i])
    i=i+1"""
print(("--------"))
"""print((vitXY))
print(max(vitXY))"""



i=0
I=[]
while i<len(O):
    I.append(i)
    i=i+1



plt.scatter(I,O,s=100)
plt.title('Nuage de points')
plt.xlabel('I')
plt.ylabel('Angles O')
plt.savefig('cercle2.png')
plt.show()

print (len(MVMT), "len(MVMT)")
print (len(vitXY), "len(vitXY)")

### Impression du code G dans un fichier texte
fichier = open("cercle-15-10-4.gcode", "w")
fichier.write("G1 X0 Y0 U0")
fichier.write("\n")

i=0
while i==0:

    fichier.write("G1 X")
    fichier.write(str(int(MVMT[i][0]*1000)/1000))
    fichier.write(" Y")
    fichier.write(str(int(MVMT[i][1]*1000)/1000))
    fichier.write(" U")
    fichier.write(str(-(int(MVMT[i][2] * 1000 * radianToDegree) / 1000)))
    fichier.write(" F")
    fichier.write(str((int(5000*1000)/1000)))
    fichier.write("\n")
    fichier.write("M106 P0 S1")
    fichier.write("\n")
    fichier.write("G4 P100")
    fichier.write("\n")
    i=i+1
while i<len(MVMT):

    fichier.write("G1 X")
    fichier.write(str(int(MVMT[i][0]*1000)/1000))
    fichier.write(" Y")
    fichier.write(str(int(MVMT[i][1]*1000)/1000))
    fichier.write(" U")
    fichier.write(str(-(int(MVMT[i][2] * 1000 * radianToDegree) / 1000)))
    fichier.write(" F")
    fichier.write(str((int(vitXY[i-1]*1000)/1000)))
    fichier.write("\n")
    i=i+1
fichier.write("M106 P0 S0")
fichier.write("\n")
fichier.write("G4 P100")
fichier.write("\n")
fichier.write("G1 X0 Y0 U0 F5000")
fichier.write("\n")

fichier.close()