from time import sleep
from myo import init, Hub, DeviceListener, pose
import math
from gtts import gTTS
import subprocess
import os

#Commands = ["Left", "Right", "Follow me", "Stop", "Proceed", "Meet here", "Dot", "Dash"]

with open("commands.txt", "r") as f:
    content = f.read()
    Commands = content.split("\n")

fac = 0.9
Up = 1
Down = 2

def speech(s):
    if not os.path.isfile(s + ".mp3"):
        tts = gTTS(text=s, lang="en-us")
        tts.save(s + ".mp3")
    subprocess.Popen(["afplay", s + ".mp3"])
    
class Listener(DeviceListener):
    def __init__(self):
        self.prev = (0, 0, 0)
        self.mavg = (0, 0, 0)
        self.last_dir_chg = (0, 0, 0)
        self.direction = [Up, Up, Up]
        self.dir_switches = [0, 0, 0]
        
        self.count=0
        self.x1=0
        self.y1=0
        self.z1=0
        self.mon=0
        self.w1 =0

        self.startquat = (-5, -5, -5, -5)
        
    def lock(self,myo,timestamp, p):
        if(self.count==0):
            speech("Lock")
            self.count=1
            self.on_pose(myo,timestamp,p)
        
    def on_pair(self, myo, timestamp, firmware_version):
        print("Hello, Myo!")

    def on_unpair(self, myo, timestamp):
        print("Goodbye, Myo!")

    def on_pose(self, myo, timestamp, p):
        if self.count == 0:
            if abs(self.mavg[1]) < 0.2:  # forearm down
                if p == pose.rest:
                    print("rest")
                elif p == pose.fist:
                    speech(Commands[6])
                elif p == pose.fingers_spread:
                    speech(Commands[7])
                elif p == pose.wave_in:# and abs(self.w1)<0.5:
                    speech(Commands[0])
                elif p == pose.wave_out:# and abs(self.w1)>0.5:
                    speech(Commands[1])
                elif p == pose.double_tap:
                    speech(Commands[2])
                else:
                    pass
            elif (self.mavg[1]) > 0.9:  # forearm up
                if p == pose.fist:
                    speech(Commands[3])
                elif p == pose.fingers_spread:
                    speech(Commands[4])
                elif p == pose.double_tap:
                    speech(Commands[5])
            elif (self.mavg[1]) < -0.9:  # forearm down
                if self.count==0:    
                    if (p==pose.fist):
                        self.lock(myo,timestamp,p)
                    elif (p == pose.double_tap):
                        speech(Commands[6])

                    #self.dir_switches[2] = 0
        if self.count != 0 and (self.mavg[1]) < -0.9:
            if (p==pose.fingers_spread):
                speech("Unlock")
                self.count=0

        print(p)
        
    def on_orientation_data(self, myo, timestamp, quat):
        if self.startquat == (-5, -5, -5, -5):
            self.startquat = quat
        
        roll = math.atan2(2.0 * (quat.w * quat.x + quat.y * quat.z),
                     1.0 - 2.0 * (quat.x * quat.x + quat.y * quat.y))
        pitch = math.asin(max(-1.0, min(1.0, 2.0 * (quat.w * quat.y - quat.z * quat.x))))
        yaw = math.atan2(2.0 * (quat.w * quat.z + quat.x * quat.y),
                         1.0 - 2.0 * (quat.y * quat.y + quat.z * quat.z))

        self.mavg = (self.mavg[0]*fac + roll*(1-fac),
                self.mavg[1]*fac + pitch*(1-fac),
                self.mavg[2]*fac + yaw*(1-fac))

        #print(self.mavg[1])

        #print("Orientation:", round(self.mavg[0], 3),  round(self.mavg[1], 3), round(self.mavg[2], 3), "*** Direction:",
        #      "+" if self.direction[0] == Up else "-",
        #      "+" if self.direction[1] == Up else "-",
        #      "+" if self.direction[2] == Up else "-")

        last_dir = self.direction
        self.direction = (Up if self.mavg[0] - self.prev[0] > 0 else Down,
                          Up if self.mavg[1] - self.prev[1] > 0 else Down,
                          Up if self.mavg[2] - self.prev[2] > 0 else Down)
        for i in range(3):
            if self.direction[i] != last_dir[i] and abs(self.direction[i] >= 1.0):
                self.dir_switches[i] += 1
        #print(self.dir_switches)

        self.prev = self.mavg
        
        self.x1 = quat.x
        self.y1 = quat.y
        self.z1 = quat.z
        self.w1 = quat.w

        #print(self.z1 - self.startquat[2])
            
        #print(self.w1)

init("/users/andrew/dev/xcode/myo/myo.framework")
hub = Hub()
hub.run(1000, Listener())
try:
    while True:
        sleep(0.5)
except KeyboardInterrupt:
    print('\nQuit')
finally:
    hub.shutdown()  # !! crucial
