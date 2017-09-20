import math
import matplotlib.pyplot as plt
import sys
import regex

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
        self.blank = None
        self.g = None
        self.x = None
        self.y = None
        self.point = None
        self.z = None
        self.e = None
        self.f = None
        self.m = None
        self.comment = None
        self.xt = None
        self.yt = None
        self.ct = None
        self.et = None

        self.get_gcode()

    def __str__(self):
        return "G%s X%s Y%s Z%s C%s E%s F%s ;%s" % (self.g,self.x,self.y,self.z,self.ct,self.e,self.f,self.comment)

    def get_gcode(self):



        """
        This method scan the text parameter of the instance and assign values to parameters :
            -g         None | 1 | 0
            -x         None | positive | negative | int |  float
            -y         None | positive | negative | int |  float
            -z         None | positive | negative | int |  float
            -e         None | positive | negative | int |  float
            -f         None | positive | int |  float
            -m         None | positive int                     Include optional S parameter | M108 S210 -> ["108","210"]
            -comment   None | everything between # and EOL     Comments should be placed at end of line or solo

            Gcode command must be written uppercase
        """
        # TODO : implementer G92 G91 G90 M82
        if self.text == "\n":
            self.blank = True
            return
        else:
            self.blank = False

        if len(regex.findall("(?<!;.*)G(0|1|3|92|90|91)\s", self.text)) > 0:  # if G character exists assign its value, G2 not implemented
            self.g = regex.findall("(?<!;.*)G(0|1|3|92|90|91)\s", self.text)[0]
            print(self.text," -- g", self.g)
        if self.g in ["0", "1", "92"]:
            if len(regex.findall("(?<!;.*)X(\+?-?\d*\.?\d*)", self.text)) > 0:  # assign value to x (pos, neg, int, float accepted)
                self.x = float(regex.findall("(?<!;.*)X(\+?-?\d*\.?\d*)", self.text)[0])

            if len(regex.findall("(?<!;.*)Y(\+?-?\d*\.?\d*)", self.text)) > 0:  # assign value to y (pos, neg, int, float accepted)
                self.y = float(regex.findall("(?<!;.*)Y(\+?-?\d*\.?\d*)", self.text)[0])

            self.point = [self.x, self.y]

            if len(regex.findall("(?<!;.*)Z(\+?-?\d*\.?\d*)", self.text)) > 0:  # assign value to z (pos, neg, int, float accepted)
                self.z = float(regex.findall("(?<!;.*)Z(\+?-?\d*\.?\d*)", self.text)[0])

            if len(regex.findall("(?<!;.*)U(\+?-?\d*\.?\d*)", self.text)) > 0:  # assign value to z (pos, neg, int, float accepted)
                self.ct = float(regex.findall("(?<!;.*)U(\+?-?\d*\.?\d*)", self.text)[0])

        if len(regex.findall("(?<!;.*)E(\+?-?\d*\.?\d*)", self.text)) > 0:      # assign value to e (pos, neg, int, float accepted)
            self.e = float(regex.findall("(?<!;.*)E(\+?-?\d*\.?\d*)", self.text)[0])


        if len(regex.findall("(?<!;.*)F(\+?\d*\.?\d*)", self.text)) > 0:        # assign value to e (pos, int, float accepted)
            self.f = regex.findall("(?<!;.*)F(\+?\d*\.?\d*)", self.text)[0]

        if len(regex.findall("(?<!;.*)M(\d+)", self.text)) > 0:                 # assign value to e (pos, int, float accepted)
            self.m = regex.findall("(?<!;.*)M(\d+)\s?S?(\d+)?", self.text)[0]   # TODO: Check other param

        if len(regex.findall(";(.*)", self.text)) > 0:                  # Comments must be at the end of line or solo
            self.comment = regex.findall(";(.*)\\n", self.text)[0]

# todo : prendre en compte les deplacement nuls  /0 ds magnitude
# todo : prendre en compte les commandes G sans X ou Y

class Gcode:
    def __init__(self, address):
        self.address = address
        self.textLineList = []                                          # list of text from gcode
        self.lineList = []                                               # list of Line instance
        self.gLineRefList = []  # list of the reference of line containing G in the lineList

        self.get_text_line_list()
        self.get_line_list()

    def get_text_line_list(self):                                         # get a list of line from gcode
        self.textLineList = open(self.address).readlines()
        print(self.textLineList)

    def get_line_list(self):
        for element in self.textLineList:
            self.lineList.append(Line(element))  # for each line in Gcode create a Line instance

    def interpolate(self, max_length):
        """
        Method to interpolate G1 movement when exceeding input parameter "max_length"
        Strategy :
        browse g1 line dans le sens normal
            get actual position
                if magnitude(previous position, actual position) > max_length :
                    append @list of Line after actual point the barycenter of the two point
                        Characteristic of point : G Point(X,Y)

            previous position = actual position

        """
        counter = 0
        last_e = 0
        while counter < len(self.gLineRefList)-1:
            actual_pos = self.lineList[self.gLineRefList[counter]]                    # define actual position
            next_pos = self.lineList[self.gLineRefList[counter + 1]]                  # define next position
            magnitude = get_magnitude(get_vector(actual_pos.point, next_pos.point))   # define movement length
            if magnitude > max_length:

                g = actual_pos.g
                x = (next_pos.x - actual_pos.x) / 2 + actual_pos.x
                y = (next_pos.y - actual_pos.y) / 2 + actual_pos.y
                if actual_pos.e is not None:
                    last_e = actual_pos.e
                if next_pos.e is not None:
                    e = (next_pos.e - last_e) / 2 + last_e
                    self.lineList.insert(self.gLineRefList[counter + 1], Line("G%s X%s Y%s E%s \n" % (g, x, y, e)))

                else:
                    self.lineList.insert(self.gLineRefList[counter + 1], Line("G%s X%s Y%s \n" % (g, x, y)))

            else:
                counter += 1
            self.get_g_command_ref()

    def transform_xy(self):

        self.get_g_command_ref()
        counter = 0

        while counter < len(self.gLineRefList):
            actual_point = self.lineList[self.gLineRefList[counter]]
            transformed_point = get_vector([0, 0], rotate_point(actual_point.point, actual_point.ct*math.pi/180))

            actual_point.xt = round(transformed_point[0], 3)
            actual_point.yt = round(transformed_point[1], 3)

            counter += 1

    def get_g_command_ref(self):
        counter = 0
        self.gLineRefList = []
        for line in self.lineList:   # Get list of line reference containing a G movement
            if line.g in ["1", "0"]:
                self.gLineRefList.append(counter)
                counter += 1
            else:
                counter += 1

    def get_c_axis(self):
        """
            Method to calculate the value of the C axis for each G0/G1 command
            each point must have the orientation of the vector to come
        """

        counter = 0
        while counter < len(self.gLineRefList)-1:     # -1 because len([1,2,3])=3

            start_point = self.lineList[self.gLineRefList[counter]]
            end_point = self.lineList[self.gLineRefList[counter + 1]]

            if start_point.x == end_point.x and start_point.y == end_point.y:   # todo : Dégueulasse , problème lorsque point double
                start_point.point[0] += 0.001


            start_point.ct = get_angle(get_vector(start_point.point, end_point.point), toolVector) * 180 / math.pi  # calculation of ct
            start_point.ct = round(start_point.ct, 3)

            counter += 1

        if counter == len(self.gLineRefList) - 1:
            self.lineList[self.gLineRefList[counter]].ct = self.lineList[self.gLineRefList[counter-1]].ct
        # the following line apply c axis for G0 command

    def clean_c_axis(self):

        counter = 0         # no angle for first element
        self.get_g_command_ref()
        while counter < len(self.gLineRefList)-1:     # -1 because len([1,2,3])=3
            angle1 = self.lineList[self.gLineRefList[counter]].ct
            angle2 = self.lineList[self.gLineRefList[counter+1]].ct
            angle2 = angle2 - round((angle2 - angle1)/360)*360
            self.lineList[self.gLineRefList[counter+1]].ct = angle2
            counter += 1

        if counter == len(self.gLineRefList) - 1:
            self.lineList[self.gLineRefList[counter]].ct = self.lineList[self.gLineRefList[counter - 1]].ct

    def transform_pos(self, line, angle):
        transformed_pos = get_vector([0, 0], rotate_point(line.point, angle * math.pi / 180))

        line.xt = round(transformed_pos[0], 3)
        line.yt = round(transformed_pos[1], 3)

    def transform_xy(self):

        self.get_g_command_ref()

        counter = 0
        while counter < len(self.gLineRefList):

            actual_point = self.lineList[self.gLineRefList[counter]]
            self.transform_pos(actual_point, actual_point.ct)

            counter += 1

    def improve_trajectory(self, max_angle):

    # pour chaque g1 point append ce meme point transformé par c-1
        self.get_g_command_ref()

        counter = len(self.gLineRefList)-1
        while counter != 1:
            if self.lineList[self.gLineRefList[counter]].g == "1":

                actual_point = self.lineList[self.gLineRefList[counter]]

                prev_point = self.lineList[self.gLineRefList[counter-1]]
                if abs(actual_point.ct-prev_point.ct) > max_angle:
                    actual_point.g = "0"
                    actual_point.e = None
                    new_point = Line(actual_point.text)
                    self.transform_pos(new_point, prev_point.ct)
                    new_point.ct = prev_point.ct
                    new_point.g = "1"
                    self.lineList.insert(self.gLineRefList[counter], new_point)

                    counter -= 1
                else:
                    counter -=1

            else:
                counter -= 1

    def print_gcode(self):
        for line in self.lineList:
            text = ""
            if line.g is not None:
                text += "G%s " % line.g
            if line.x is not None:
                text += "X%s " % line.xt
            if line.y is not None:
                text += "Y%s " % line.yt
            if line.z is not None:
                text += "Z%s " % line.z
            if line.ct is not None:
                text += "U%s " % (line.ct*-1)
            if line.e is not None:
                text += "E%s " % line.e
            if line.m is not None:
                if line.m[0] is not "":
                    text += "M%s " % line.m[0]
                if line.m[1] is not "":
                    text += "S%s " % line.m[1]
            if line.comment is not None:
                text += ";%s" % line.comment


            f.write(text + '\n')

    def graph_gcode(self):
        self.get_g_command_ref()
        counter = 0
        x_list = []
        y_list = []
        while counter < len(self.gLineRefList):
            point = self.lineList[self.gLineRefList[counter]]
            x_list.append(point.x)
            y_list.append(point.y)
            counter += 1

        plt.scatter(x_list, y_list, s=100)
        plt.title('Gcode')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.savefig('gcode.png')
        plt.show()


# todo : modified xt yt
# todo : adjust feedrate after modification
# todo : interpolate non lineaire pour C
# todo : interpoler après le calcul du C en mesurant l'erreur !

gcode = Gcode("test.gcode")
gcode.get_g_command_ref()

gcode.get_c_axis()
gcode.clean_c_axis()
gcode.transform_xy()
gcode.improve_trajectory(25)

open('4axis.gcode', 'w').close()
f = open('4axis.gcode', 'a')
gcode.print_gcode()
f.close()

sys.exit("End of test")




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
