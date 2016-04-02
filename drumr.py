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
        
    def on_pair(self, myo, timestamp, firmware_version):
        print("Hello, Myo!")

    def on_unpair(self, myo, timestamp):
        print("Goodbye, Myo!")

    def on_pose(self, myo, timestamp, p):
        if p == pose.rest:
            print("rest")
        elif p == pose.fist:
            speech("Stop")
            
        print(p)

    def on_orientation_data(self, myo, timestamp, quat):
        roll = math.atan2(2.0 * (quat.w * quat.x + quat.y * quat.z),
                     1.0 - 2.0 * (quat.x * quat.x + quat.y * quat.y))
        pitch = math.asin(max(-1.0, min(1.0, 2.0 * (quat.w * quat.y - quat.z * quat.x))))
        yaw = math.atan2(2.0 * (quat.w * quat.z + quat.x * quat.y),
                         1.0 - 2.0 * (quat.y * quat.y + quat.z * quat.z))

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
