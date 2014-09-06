#!/usr/bin/env python

import cv2
import numpy as np
import math
import utils

class DotFinder:
    def __init__(self, points, limits, max_dot_size=1000.0):
        self._limits = limits
        self._no_points = points
        self._max_dot_size = max_dot_size
        
    def tune_limits(self, img, show_hsv=True):
        hsv = self._conv_hsv(img)
        
        if show_hsv:
            separated = cv2.split(hsv)
            cv2.imshow("H", separated[0])
            cv2.imshow("S", separated[1])
            cv2.imshow("V", separated[2])
    
        mask_blue = self._get_mask(hsv)
        cv2.imshow("Mask", mask_blue)
    
    def find(self, img):
        retimg = img.copy()
        mask = self._get_mask(img)

        contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        areas = None
        #contours, areas = self._filter_ellipses(contours)
        #contours, areas = self._sort_contours_by_area(contours, areas)
        #contours = self._filter_close_size(contours, areas)
        
        centers = []
        if contours:
            cv2.drawContours(retimg, contours, -1, (0,0,255) if retimg.shape[2] == 3 else 255, -1)
            
            for cont in contours:
                centers.append(utils.center_of_mass(cont))
            centers = np.float32(centers)
            for c in centers:
                cv2.circle(retimg, (int(c[0]), int(c[1])), 5, (255, 0, 0) if retimg.shape[2] == 3 else 255, 1) 
        
        return centers, mask, retimg
        
    def _filter_ellipses(self, contours, shape_eps=0.3):
        areas = [cv2.contourArea(ctr) for ctr in contours]
        convHulls = [cv2.convexHull(ctr) for ctr in contours]
        minAreaRects = [cv2.minAreaRect(ctr) for ctr in contours]
        ind = []
        for i in range(len(contours)):
            if areas[i] > 2.0 and areas[i] < self._max_dot_size:
                rectArea = minAreaRects[i][1][0]*minAreaRects[i][1][1]
                ratio = rectArea/areas[i]*math.pi/4.0
                if ratio < 1.0+shape_eps and ratio > 1.0-shape_eps:
                    ind.append(i)
        return [contours[i] for i in ind], [areas[i] for i in ind]
                    
    def _sort_contours_by_area(self, contours, areas=None):
        if not areas:
            areas = [cv2.contourArea(ctr) for ctr in contours]
        assert len(contours) == len(areas)
        ind = range(len(contours))
        sort = sorted(ind, key=lambda i: areas[i])
        return [contours[i] for i in sort if areas[i] > 0.0], [areas[i] for i in sort if areas[i] > 0.0]
        
    def _filter_close_size(self, contours, areas=None, delta=0.1):
        if not areas:
            areas = [cv2.contourArea(ctr) for ctr in contours]
        assert len(contours) == len(areas)
        if len(contours) < self._no_points:
            return None
        # areas is sorted, make a list of differences between max and min area taking all possible n-points
        # where n is self._no_points
        n_diffs = [areas[i+self._no_points-1] - areas[i] for i in range(len(contours)-self._no_points+1)]
        # check if that difference is not too big with relation to the area of the min element in sequence
        # filter wrong sized poins
        for i in range(len(n_diffs)):
            if n_diffs[i]/areas[i] > 1.0+delta:
                n_diffs[i] = float('Inf')
        # now, if n_diffs[i] is not Inf, then the sequence is valid
        # might be a good idea to exclude points that are too far away from each other (center of mass)
        # for all allowed sequences of points
        # find the best sequence, that is the one with the smallest difference in size
        min_diff_pos = n_diffs.index(min(n_diffs))
        return contours[min_diff_pos:min_diff_pos+self._no_points]    
    
    def _get_mask(self, image):
        if len(self._limits[0]) == 3:
            return cv2.inRange(self._conv_hsv(image), self._limits[0], self._limits[1])
        else:
            return cv2.inRange(image, self._limits[0], self._limits[1]);
        
    def _conv_hsv(self, img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2HSV)