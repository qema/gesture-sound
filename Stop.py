from time import sleep
from myo import init, Hub, DeviceListener, pose
import math
from gtts import gTTS
import subprocess

fac = 0.9
Up = 1
Down = 2


def speech(s):
    tts = gTTS(text=s, lang="en")
    tts.save("tmp.mp3")
    subprocess.call(["afplay", "tmp.mp3"])
    
class Listener(DeviceListener):
    def __init__(self):
        self.prev = (0, 0, 0)
        self.mavg = (0, 0, 0)
        self.direction = [Up, Up, Up]
        self.count=0
        self.x1=0
        self.y1=0
        self.z1=0
        self.mon=0
        self.w1 =0
        
        
        
    def on_pair(self, myo, timestamp, firmware_version):
        print("Hello, Myo!")

    def on_unpair(self, myo, timestamp):
        print("Goodbye, Myo!")

    def lock(self,myo,timestamp, p):
        if(self.count==0):
            
            speech("lock")
            self.count=1
            self.on_pose(myo,timestamp,p)

    
        
            
            
        
    def on_pose(self, myo, timestamp, p):
        
        g = [self.x1,self.y1,self.z1,self.w1]
        
        print(g)
        if self.count==0:    
                
            if p == pose.rest:
                print("rest")
            elif (p == pose.fist)&(abs(self.mon)<1):
                speech("Stop")
                self.count = 0
            elif (p==pose.double_tap):
                self.lock(myo,timestamp,p)
            elif (p==pose.wave_out)&(self.w1<0.7):
                speech("left")
            elif (p==pose.wave_out)&(self.w1>0.7):
                speech("right")
            ##print(p)
                
        else:
            if (p==pose.fist):
                speech("Unlock")
                self.count=0
                
        
            
        
        
        

    

    def on_orientation_data(self, myo, timestamp, quat):
        
        roll = math.atan2(2.0 * (quat.w * quat.x + quat.y * quat.z),
                     1.0 - 2.0 * (quat.x * quat.x + quat.y * quat.y))
        
        pitch = math.asin(max(-1.0, min(1.0, 2.0 * (quat.w * quat.y - quat.z * quat.x))))
        yaw = math.atan2(2.0 * (quat.w * quat.z + quat.x * quat.y),
                         1.0 - 2.0 * (quat.y * quat.y + quat.z * quat.z))
        self.xroll=roll
        self.yroll = pitch
        self.zroll = yaw

        self.mavg = (self.mavg[0]*fac + roll*(1-fac),
                self.mavg[1]*fac + pitch*(1-fac),
                self.mavg[2]*fac + yaw*(1-fac))

        #print("Orientation:", round(self.mavg[0], 3),  round(self.mavg[1], 3), round(self.mavg[2], 3), "*** Direction:",
        #      "+" if self.direction[0] == Up else "-",
        #      "+" if self.direction[1] == Up else "-",
        #      "+" if self.direction[2] == Up else "-")
        
        self.direction = (Up if self.mavg[0] - self.prev[0] > 0 else Down,
                          Up if self.mavg[1] - self.prev[1] > 0 else Down,
                          Up if self.mavg[2] - self.prev[2] > 0 else Down)

        self.prev = self.mavg

        self.x1 = quat.x
        self.y1=quat.y
        self.z1=quat.z
        self.w1 = quat.w
        
        

    

        

        
        

        
    
            
    

        
        

init("/users/dominic/downloads/sdk/myo.framework")
hub = Hub()
hub.run(1000, Listener(),lil_sleep=0.01)
try:
    while True:
        sleep(0.5)
except KeyboardInterrupt:
    print('\nQuit')
finally:
    hub.shutdown()  # !! crucial
