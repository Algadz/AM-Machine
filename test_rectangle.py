from unittest import TestCase
from MasterGround import Rectangle


class TestRectangle(TestCase):
    def Test_Area_Succeed(self):
        r = Rectangle(2,3)
        self.assertEquals(r.area(),6)
