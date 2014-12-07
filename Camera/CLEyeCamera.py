import ctypes
from ctypes import cdll, Structure, byref
from ctypes.wintypes import BYTE, WORD, DWORD
import numpy as np

# camera modes
CLEYE_MONO_PROCESSED = 0
CLEYE_COLOR_PROCESSED = 1
CLEYE_MONO_RAW = 2
CLEYE_COLOR_RAW = 3
CLEYE_BAYER_RAW = 4
def isCameraMode(mode):
    return mode >= 0 and mode <= 4

# camera resolution
CLEYE_QVGA = 0
CLEYE_VGA = 1
def isCameraResolution(resolution):
    return resolution >= 0 and resolution <= 1

# camera parameters
# camera sensor parameters
CLEYE_AUTO_GAIN             = 0     # [false, true]
CLEYE_GAIN                  = 1	    # [0, 79]
CLEYE_AUTO_EXPOSURE         = 2	    # [false, true]
CLEYE_EXPOSURE              = 3     # [0, 511]
CLEYE_AUTO_WHITEBALANCE     = 4     # [false, true]
CLEYE_WHITEBALANCE_RED      = 5     # [0, 255]
CLEYE_WHITEBALANCE_GREEN    = 6     # [0, 255]
CLEYE_WHITEBALANCE_BLUE     = 7     # [0, 255]
# camera linear transform parameters (valid for CLEYE_MONO_PROCESSED, CLEYE_COLOR_PROCESSED modes)
CLEYE_HFLIP                 = 8     # [false, true]
CLEYE_VFLIP                 = 9     # [false, true]
CLEYE_HKEYSTONE             = 10    # [-500, 500]
CLEYE_VKEYSTONE             = 11    # [-500, 500]
CLEYE_XOFFSET               = 12    # [-500, 500]
CLEYE_YOFFSET               = 13    # [-500, 500]
CLEYE_ROTATION              = 14    # [-500, 500]
CLEYE_ZOOM                  = 15    # [-500, 500]
# camera non-linear transform parameters (valid for CLEYE_MONO_PROCESSED, CLEYE_COLOR_PROCESSED modes)
CLEYE_LENSCORRECTION1       = 16    # [-500, 500]
CLEYE_LENSCORRECTION2       = 17    # [-500, 500]
CLEYE_LENSCORRECTION3       = 18    # [-500, 500]
CLEYE_LENSBRIGHTNESS        = 19    # [-500, 500]
def isCameraParameter(param):
    return param >= 0 and param <= 19

class CLEyeUUID(Structure):
    _fields_ = [("Data1", DWORD), 
        ("Data2", WORD),
        ("Data3", WORD),
        ("Data4", BYTE * 8)]
        
class CLEyeDLL:
    def __init__(self, dllpath=None):
        self.dllpath = dllpath if dllpath else 'CLEyeMulticam.dll'
        self.dll = cdll.LoadLibrary(self.dllpath)
        
        # Camera information
        # IMPORT(int) CLEyeGetCameraCount()
        self.dll.CLEyeGetCameraCount.restype = ctypes.c_int
        # IMPORT(GUID) CLEyeGetCameraUUID(int camId);
        self.dll.CLEyeGetCameraUUID.restype = CLEyeUUID 

        # Library initialization
        # IMPORT(CLEyeCameraInstance) CLEyeCreateCamera(GUID camUUID, CLEyeCameraColorMode mode, 
												# CLEyeCameraResolution res, float frameRate);
        self.dll.CLEyeCreateCamera.restype = ctypes.c_void_p
        # IMPORT(bool) CLEyeDestroyCamera(CLEyeCameraInstance cam);
        self.dll.CLEyeDestroyCamera.restype = ctypes.c_bool
        
        # Camera capture control
        # IMPORT(bool) CLEyeCameraStart(CLEyeCameraInstance cam);
        self.dll.CLEyeCameraStart.restype = ctypes.c_bool
        # IMPORT(bool) CLEyeCameraStop(CLEyeCameraInstance cam);
        self.dll.CLEyeCameraStop.restype = ctypes.c_bool
        
        # Camera LED control
        # IMPORT(bool) CLEyeCameraLED(CLEyeCameraInstance cam, bool on);
        self.dll.CLEyeCameraLED.restype = ctypes.c_bool
        
        # Camera parameters control
        # IMPORT(bool) CLEyeSetCameraParameter(CLEyeCameraInstance cam, CLEyeCameraParameter param, int value);
        self.dll.CLEyeSetCameraParameter.restype = ctypes.c_bool
        # IMPORT(int) CLEyeGetCameraParameter(CLEyeCameraInstance cam, CLEyeCameraParameter param);
        self.dll.CLEyeGetCameraParameter.restype = ctypes.c_int
        
        # Camera video frame image data retrieval
        # IMPORT(bool) CLEyeCameraGetFrameDimensions(CLEyeCameraInstance cam, int &width, int &height);
        self.dll.CLEyeCameraGetFrameDimensions.restype = ctypes.c_bool
        # IMPORT(bool) CLEyeCameraGetFrame(CLEyeCameraInstance cam, PBYTE pData, int waitTimeout = 2000);
        self.dll.CLEyeCameraGetFrame.restype = ctypes.c_bool
    
    def CLEyeGetCameraCount(self):
        return self.dll.CLEyeGetCameraCount()
    def CLEyeGetCameraUUID(self, camId):
        assert camId >= 0 and type(camId) == int
        return self.dll.CLEyeGetCameraUUID(camId)
    def CLEyeCreateCamera(self, uuid, mode, res, frameRate):
        assert type(uuid) == CLEyeUUID
        assert isCameraMode(mode)
        assert isCameraResolution(res)
        assert frameRate > 0
        return self.dll.CLEyeCreateCamera(uuid, mode, res, ctypes.c_float(frameRate))
    def CLEyeDestroyCamera(self, cam):
        return self.dll.CLEyeDestroyCamera(cam)
    def CLEyeCameraStart(self, cam):
        return self.dll.CLEyeCameraStart(cam)
    def CLEyeCameraStop(self, cam):
        return self.dll.CLEyeCameraStop(cam)
    def CLEyeCameraLED(self, cam, on):
        assert type(on) == Bool
        return self.dll.CLEyeCameraLED(cam, on)
    def CLEyeSetCameraParameter(self, cam, param, value):
        assert isCameraParameter(param)
        return self.dll.CLEyeSetCameraParameter(cam, param, value)
    def CLEyeGetCameraParameter(self, cam, param):
        assert isCameraParameter(param)
        return self.dll.CLEyeDetCameraParameter(cam, param)
    def CLEyeCameraGetFrameDimensions(self, cam):
        height = ctypes.c_int(0)
        width = ctypes.c_int(0)
        self.dll.CLEyeCameraGetFrameDimensions(cam, byref(width), byref(height))
        return (width.value, height.value)
    def CLEyeCameraGetFrame(self, cam, image, waitTimeout = 2000):
        return self.dll.CLEyeCameraGetFrame(cam, image.ctypes.data_as(ctypes.POINTER(BYTE)), waitTimeout)
        
class CLEyeException(Exception):
    def __init__(self, str):
        self.value = str
    def __str__(self):
        return repr(self.value)
    
class CLEyeCamera:
    _CLDLL = CLEyeDLL()
    
    def __init__(self, num = 0, **params):
        assert num >= 0, "Camera number cannot be negative"
        self._mode = params['mode'] if 'mode' in params else CLEYE_MONO_PROCESSED
        self._resolution = params['resolution'] if 'resolution' in params else CLEYE_VGA
        self._frameRate = params['frameRate'] if 'frameRate' in params else 30.0
        self._uuid = self._CLDLL.CLEyeGetCameraUUID(num)
        self._cam = self._CLDLL.CLEyeCreateCamera(self._uuid, self._mode, self._resolution, self._frameRate)
        if not self._cam or self._cam == 0:
            raise CLEyeException("Cannot create camera object")
        if not self._CLDLL.CLEyeCameraStart(self._cam):
            self._CLDLL.CLEyeDestroyCamera(self._cam)
            raise CLEyeException("Cannot start camera")  
    def __del__(self):
        if self._cam:
            self._CLDLL.CLEyeCameraStop(self._cam)
            self._CLDLL.CLEyeDestroyCamera(self._cam)
    def setParam(self, param, value):
        return self._CLDLL.CLEyeSetCameraParameter(self._cam, param, value)
    def getParam(self, param):
        return self._CLDLL.CLEyeGetCameraParameter(self._cam, param)
    def getFrameSize(self):
        return self._CLDLL.CLEyeCameraGetFrameDimensions(self._cam)
    def getFrame(self):
        image = self._createImage()
        self.getFrameX(image)
        return image
    def getFrameX(self, image):
        return self._CLDLL.CLEyeCameraGetFrame(self._cam, image)
    def _createImage(self):
        width, height = (640, 480) if self._resolution==CLEYE_VGA else (320, 240)
        depth = 4 if self._mode==CLEYE_COLOR_PROCESSED or self._mode==CLEYE_COLOR_RAW else 1
        image = np.zeros((height, width, depth), dtype=np.uint8)
        return image
  
import time  
import cv2
if __name__ == '__main__':
    cam = CLEyeCamera(0, mode=CLEYE_COLOR_RAW, resolution=CLEYE_VGA, frameRate=30.0)
    cam.setParam(CLEYE_AUTO_GAIN, False)
    cam.setParam(CLEYE_AUTO_EXPOSURE, False)
    cam.setParam(CLEYE_AUTO_WHITEBALANCE, True)
    cam.setParam(CLEYE_GAIN, 30)
    cam.setParam(CLEYE_EXPOSURE, 400)
    #cam.setParam(CLEYE_WHITEBALANCE_RED, 150)
    #cam.setParam(CLEYE_WHITEBALANCE_GREEN, 150)
    #cam.setParam(CLEYE_WHITEBALANCE_BLUE, 150)
    
    image = cam.getFrame()
    height, width, layers = image.shape
    #video = cv2.VideoWriter('output.avi',0,30,(width,height),True)
    ptime = time.clock()
    stime = ptime
    counter = 0
    while(True):
        cam.getFrameX(image)
        counter += 1
        cv2.imshow('Capture', image)
        #print image
        #video.write(image)
        tm = time.clock()
        if tm-ptime > 1.0:
            print "%.1f FPS" % (float(counter)/(tm-ptime))
            ptime = tm
            counter = 0
        #if tm-stime > 10.0:
            #break;
        if cv2.waitKey(1) == 27:
            break
    #cv2.destroyAllWindows()
    #video.release()