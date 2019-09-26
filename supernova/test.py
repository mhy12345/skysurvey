import cv2
import numpy as np
import matplotlib.pyplot as plt
from star import Star, list_stars

def test0():
    star = Star('c20190610_1_ST0049_L_237_00001')
    print(star.test())
    print(star.properties)


def test1():
    samples = [
        ('c20190610_1_NT0142_L_357_00000','BRI','PASS'),
        ('c20190610_1_NT0055_L_303_00005','SIM','PASS'),
        ('c20190610_1_NT0060_L_615_00001','SIM','PASS'),
        ('c20190610_1_NT0141_L_351_00000','SIM','PASS'),
        ('c20190610_1_ST0049_L_237_00001','SIM','PASS'),
        ('c20190610_1_ST0049_L_237_00002','SIM','BLOCKED'),
        ('c20190610_1_NT0064_L_591_00004','SIM','BLOCKED')
        ]

    for name, tag, answer in samples:
        print(">>>>>>> %s %s %s" %(name, tag, answer))
        star = Star(name)
        res, details = star.test()
        print("PRO : ", star.properties)
        print("RES : ", res)
        print("DETAIL : ", details)

test1()
