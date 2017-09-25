import math
import matplotlib.pyplot as plt
import sys
import regex
import time

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

        if self.text == "\n":
            self.blank = True
            return
        else:
            self.blank = False

        if len(regex.findall("(?<!;.*)G(0|1|3|92|90|91)\s", self.text)) > 0:  # if G character exists assign its value, G2 not implemented
            self.g = regex.findall("(?<!;.*)G(0|1|3|92|90|91)\s", self.text)[0]

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
# todo : ajouter les feedrates

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
            if line.g in ["1", "0"] and line.x is not None and line.y is not None:
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
            print(start_point.text)
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

        line.xt = round(transformed_pos[0], 3)  # limit command length
        line.yt = round(transformed_pos[1], 3)

    def transform_xy(self):

        self.get_g_command_ref()

        counter = 0
        while counter < len(self.gLineRefList):

            actual_point = self.lineList[self.gLineRefList[counter]]
            self.transform_pos(actual_point, actual_point.ct)

            counter += 1

    def improve_trajectory(self, max_angle):

    # pour chaque g1 point append ce meme point en G0 transformé par c-1

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
                    counter -= 1

            else:
                counter -= 1

    def interpolate(self, max_angle):
        """
        parcourir les G
        Si la différence d'angle entre le point actuel et le point suivant est supérieur à Cmax
        append un nouveau point en counter + 1 qui à :
            C = C1 + C2 / 2
            Xt Yt = rotation de -C du point 1 non transformé
        """
        counter = 0
        self.get_g_command_ref()

        while counter < len(self.gLineRefList)-1:

            actual_pos = self.lineList[self.gLineRefList[counter]]                    # define actual position
            next_pos = self.lineList[self.gLineRefList[counter + 1]]                  # define next position
            if counter % 100 == 0:
                print((1-(len(self.gLineRefList)-counter)/len(self.gLineRefList))*100," %")
            if abs(actual_pos.ct - next_pos.ct) > max_angle:

                c = (actual_pos.ct + next_pos.ct)/2

                x = actual_pos.x
                y = actual_pos.y
                point_t = get_vector([0, 0], rotate_point([x, y], c * math.pi / 180))
                xt = point_t[0]
                yt = point_t[1]

                self.lineList.insert(self.gLineRefList[counter + 1], Line("G0 X%s Y%s\n" % (x, y)))
                self.lineList[self.gLineRefList[counter + 1]].xt = round(xt, 3)
                self.lineList[self.gLineRefList[counter + 1]].yt = round(yt, 3)
                self.lineList[self.gLineRefList[counter + 1]].ct = c

            else:
                counter += 1
            #insérer à gLineRefList à la position counter+1 la valeur glineRefList[counter+1]-1
            # incrémenter de 1 toute les valeurs suivantes à counter + 1

            #self.gLineRefList.insert(counter + 1, self.gLineRefList[counter + 1]-1)
            #i = counter
            #while i < len(self.gLineRefList):
                #self.gLineRefList[i] += 1
                #i += 1
            self.get_g_command_ref()

    def print_gcode(self):
        for line in self.lineList:
            text = ""
            if line.g is not None:
                text += "G%s " % line.g
            if line.x is not None:
                text += "X%s " % (round(line.xt, 3))
            if line.y is not None:
                text += "Y%s " % (round(line.yt, 3))
            if line.z is not None:
                text += "Z%s " % (round(line.z, 3))
            if line.ct is not None:
                text += "U%s " % (round((line.ct*-1), 3))
            if line.e is not None:
                text += "E%s " % (round(line.e, 3))
            if line.f is not None:
                text += "F%s " % (round(line.f, 3))
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
# TODO : mouvement parasites de rotation entre G0
# todo : bug si le fichier ne termine pas par une ligne vide ? ou un G1 ?

gcode = Gcode("test.gcode")
gcode.get_g_command_ref()

gcode.get_c_axis()
gcode.clean_c_axis()
gcode.transform_xy()
gcode.improve_trajectory(25)
gcode.interpolate(25)
open('4axis.gcode', 'w').close()
f = open('4axis.gcode', 'a')
gcode.print_gcode()
f.close()

print(get_vector([0, 0], rotate_point([-50, 50], 315 * math.pi / 180)))

sys.exit("End of test")