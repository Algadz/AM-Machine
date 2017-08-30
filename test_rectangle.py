from unittest import TestCase  # import unittest
from MasterGround import Rectangle  # import Rectangle from MasterGround


class TestRectangle(TestCase):  # define class TestRectangle
    def test_Area_Succeed(self):  # define test for area
        r1 = Rectangle(2, 3)  # i
        r2 = Rectangle(2, 3.2)  # i
        self.assertEquals(r1.area(), 6)  # i
        self.assertEquals(r2.area(), 6.4)  # i
