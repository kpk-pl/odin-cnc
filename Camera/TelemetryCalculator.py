#!/usr/bin/env python

from collections import deque
import numpy as np
import math
import cv2

class TelemetryCalculator:
    def __init__(self, n_init):
        self._init_len = n_init
        self._is_calibrated = False
        self._calib_queue = deque([None for _ in range(self._init_len)])
        self._base_pair = None
        
        self._turn_counter = np.zeros((3,1), dtype=np.int)
        self._prev_rvec = None
        
    def __call__(self, rvec, tvec):      
        if not self._is_calibrated:
            adjrvec = self._adjust_rotation(rvec)
            self._calib_queue.popleft()
            self._calib_queue.append([adjrvec, tvec])
            if self.calibrated():                                                             # this modifies turn counter
                self._base_pair[0] = np.mat(cv2.Rodrigues(self._base_pair[0])[0])             # convert angle vector to base rotation matrix
                self._turn_counter = np.zeros((3,1), dtype=np.int)                            # reset turn counter vector - robot in base position
                self._prev_rvec = None
            return None
        else:                                                                                 # calibrated now for sure, in base position
            rmat = np.mat(cv2.Rodrigues(rvec)[0])
            X = self._base_pair[0].T * (np.mat(tvec) - np.mat(self._base_pair[1]))
            R = cv2.Rodrigues(self._base_pair[0].T * rmat)[0]     
            
            R = self._adjust_rotation(R)
            return R, X
    
    def _adjust_rotation(self, rvec):
        if self._prev_rvec == None:
            self._prev_rvec = rvec.copy()
            return rvec
        half_pi = math.pi / 2.0
        for i in range(3):
            if rvec[i]*self._prev_rvec[i] < 0:
                if rvec[i] < -half_pi and self._prev_rvec[i] > half_pi:
                    self._turn_counter[i] += 1
                elif rvec[i] > half_pi and self._prev_rvec[i] < -half_pi:
                    self._turn_counter[i] -= 1
        self._prev_rvec = rvec.copy()
        return rvec + np.multiply(self._turn_counter, 2.0*math.pi*np.ones((3,1)))
    
    def calibrated(self, delta_pos=3.0, delta_rot=1.0):
        if self._is_calibrated:
            return True
            
        delta_rot *= math.pi/180.0    
        posmin = np.array([[np.inf],[np.inf],[np.inf]])
        posmax = -posmin
        rotmin = posmin.copy()
        rotmax = posmax.copy()
                
        for c_obj in self._calib_queue:
            if c_obj == None:
                return False
            posmax = np.maximum(posmax, c_obj[1])
            posmin = np.minimum(posmin, c_obj[1])
            rotmax = np.maximum(rotmax, c_obj[0])
            rotmin = np.minimum(rotmin, c_obj[0])

        dpos = posmax-posmin
        drot = rotmax-rotmin

        if np.all([i < delta_pos for i in dpos]) and np.all([i < delta_rot for i in drot]):
            self._is_calibrated = True
            self._base_pair = [np.zeros((3,1)), np.zeros((3,1))]
            for c_obj in self._calib_queue:
                self._base_pair[0] += c_obj[0]
                self._base_pair[1] += c_obj[1]
            self._base_pair[0] /= len(self._calib_queue)
            self._base_pair[1] /= len(self._calib_queue)
            del self._calib_queue
            print "Calibrated"
            return True
        else:
            return False