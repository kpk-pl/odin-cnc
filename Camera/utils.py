#!/usr/bin/env python

import cv2
import numpy as np

def center_of_mass(contour):
    moments = cv2.moments(contour)
    m00 = moments['m00']
    if m00 != 0:
        return [moments['m10']/m00, moments['m01']/m00]
    return [0.0,0.0]
    
def find_in_prox(pointset, point, max_prox):
    close = []
    for pi in range(len(pointset)):
        dist = np.linalg.norm(pointset[pi]-point)
        if dist <= max_prox:
            close.append((pi, dist))
    if len(close) == 0:
        return None
    m = min(close,key=lambda x: x[1])
    return m[0]