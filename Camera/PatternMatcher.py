#!/usr/bin/env python

import cv2
import numpy as np
import math
import utils

class MatchError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

#              4
#        3           5
#    2         15        6
#   
#  1     14    0          7
# 
#    12        13       8
#        11          9
#              10        
class PatternMatcher:
    def __init__(self, pattern, scaling_file):
        self._pattern = pattern
        self._center_i = 0
        self._hull_i = range(1, 13)
        self._max_prox = 50.0
        with np.load(scaling_file) as data:
            self._camera_mtx, self._camera_dist = [data[i] for i in ('mtx', 'dist')]
        
    def match(self, points):
        if len(points) != len(self._pattern):
            raise MatchError("Matching pattern with incorrect number of points")
         
        # undistort points coordinates for better linear matching    
        undist_points = cv2.undistortPoints(np.array([points]), self._camera_mtx, self._camera_dist)[0] * 1000.0
            
        # indices of the convex hull points    
        hull_i = cv2.convexHull(undist_points, returnPoints=False, clockwise=False)
        hull_i = [x[0] for x in hull_i] # change array packing
        if len(hull_i) != len(self._hull_i):
            raise MatchError("Cannot find convex hull with desired number of points")
            
        # find center point
        center_mass = utils.center_of_mass(np.float32([[undist_points[i]] for i in hull_i]))
        center_i = utils.find_in_prox(undist_points, center_mass, self._max_prox)
        if center_i == None:
            raise MatchError("Cannot find center of mass")    

        # find rest of the points
        rest_i = list(set(range(len(self._pattern))) - set([center_i]) - set(hull_i))
        if len(rest_i) != len(self._pattern)-1-len(self._hull_i):
            raise MatchError("Incorrect number of rest points")
        
        # match points 10-13, 4-15, 1-14
        pairs_i = []
        for ri in rest_i:
            prediction = undist_points[center_i] + [2.0,2.0]*(undist_points[ri]-undist_points[center_i])
            result = utils.find_in_prox(undist_points, prediction, self._max_prox)
            if result == None or result not in hull_i:
                raise MatchError("Cannot find relationship to rest points")
            pairs_i.append(result)

        # try to find the point #7 on the hull
        lonely_i = None
        for i in range(3):
            li = hull_i[(hull_i.index(pairs_i[i]) - 3) % len(hull_i)]
            if li not in pairs_i:
                lonely_i = li
                break
        if lonely_i == None:
            raise MatchError("Cannot locate lonely point on the hull")
        
        # rotate hull array knowing which is the lonely point      
        rot_i = (hull_i.index(lonely_i) + len(hull_i)/2) % len(hull_i)
        rot_hull_i = hull_i[rot_i:] + hull_i[:rot_i]
        
        # sort rest points having hull already sorted
        sort_rest_i = [None, None, None]
        sort_rest_i[0] = rest_i[pairs_i.index(rot_hull_i[9])]
        sort_rest_i[1] = rest_i[pairs_i.index(rot_hull_i[0])]
        sort_rest_i[2] = rest_i[pairs_i.index(rot_hull_i[3])]
        
        # merge final map
        match_map = [center_i] + rot_hull_i + sort_rest_i
        
        # check if projection matches pattern
        homography, mask = cv2.findHomography(np.float32([points[i] for i in match_map]), self._pattern, cv2.RANSAC, self._max_prox)
        if 0 in mask:
            raise MatchError("Reprojection error exceeds specified maximum")
        
        return match_map, homography
        
    def mark_map(self, img, points, match_map):
        assert len(points) == len(match_map)
        for i in range(len(match_map)):
            cv2.putText(img, str(i), tuple([int(round(nb)) for nb in points[match_map[i]]+[3.0,-3.0]]), cv2.FONT_HERSHEY_PLAIN, 1.0, (0,0,255) if img.shape[2] == 3 else 255)
            
    def undistort(self, img):
        return cv2.remap(img, slef._camera_mapx, celf._camera_mapy, cv2.INTER_LINEAR)