#!/usr/bin/env python

import cv2
import numpy as np

class PositionTracker:
    def __init__(self, pattern, scaling_file, coord_scale):
        with np.load(scaling_file) as data:
            self._camera_mtx, self._camera_dist = [data[i] for i in ('mtx', 'dist')]
            
        self._coord_scale = coord_scale
        self._pattern3d = np.float32(np.append(pattern, np.zeros([len(pattern),1]), 1))
        
        self._ori_center = np.float32([0,0,0]).reshape(-1,3)
        self._ori_axis = coord_scale*30.0*np.float32([[1,0,0], [0,1,0], [0,0,1]]).reshape(-1,3)
        
    def getCoords(self, points, outimage=None):
        rvec, tvec, _ = cv2.solvePnPRansac(self._pattern3d, points, self._camera_mtx, self._camera_dist)
        
        if outimage != None:
            self._draw_coords(outimage, rvec, tvec)
            
        return rvec, tvec*self._coord_scale
        
    def _draw_coords(self, img, rvec, tvec):
        pr_imgpts = cv2.projectPoints(self._ori_axis, rvec, tvec, self._camera_mtx, self._camera_dist)[0]
        pr_center = cv2.projectPoints(self._ori_center, rvec, tvec, self._camera_mtx, self._camera_dist)[0]
        cv2.line(img, tuple(pr_center.ravel()), tuple(pr_imgpts[0].ravel()), (0,255,0) if img.shape[2] == 3 else 255, 5)
        cv2.line(img, tuple(pr_center.ravel()), tuple(pr_imgpts[1].ravel()), (0,150,0) if img.shape[2] == 3 else 150, 5)
        cv2.line(img, tuple(pr_center.ravel()), tuple(pr_imgpts[2].ravel()), (0,50,0) if img.shape[2] == 3 else 50, 5)
        