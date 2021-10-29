import pyttsx3
from robot.camera import Camera
from robot.led import Led
from robot.motor import Motor
from robot.steering import Steering

from threading import Timer

try:
    import Adafruit_PCA9685
    pwm = Adafruit_PCA9685.PCA9685()
except:
    from unittest.mock import Mock
    pwm = Mock()
    pwm.set_pwm = lambda *args : print(f"pwm.set_pwm{args}")
pwm.set_pwm_freq(60)

# Initialization
Motor.setup()
Steering.setup(config={}, pwm=pwm)
Camera.setup(config={}, pwm=pwm)
Led.setup()
voice_engine = pyttsx3.init(debug=True)

class Controller:
    Timers = []

    @staticmethod
    def _cancel_event():
        for timer in Controller.Timers:
            timer.cancel()
        Motor.Timers = []

    @staticmethod
    def _schedule_event(delay, function, args=[], kwargs={}):
        timer = Timer(delay, function, args, kwargs)
        timer.start()
        Controller.Timers.append(timer)

    @staticmethod
    def move(direction, speed, heading, duration):
        Camera.ahead()
        Motor.move(direction, speed)
        Steering.head(heading)
        Controller._schedule_event(duration, Motor.stop)
        Controller._schedule_event(duration, Steering.middle)

    @staticmethod
    def moves(moves):
        Camera.ahead()
        delay = 0
        for move in moves:
            Controller._schedule_event(delay,
                                       Motor.move,
                                       [move['direction'], move['speed']])
            Controller._schedule_event(delay,
                                       Steering.head,
                                       [move['heading']])
            delay += move['duration']
        Controller._schedule_event(delay, Motor.stop)
        Controller._schedule_event(delay, Steering.middle)

    @staticmethod
    def set_camera_position(x, y):
        Camera.set_position(x, y)

    @staticmethod
    def set_led_state(left_on, left_color, right_on, right_color):
        Led.set(left_on, left_color, right_on, right_color)

    @staticmethod
    def say(text):
        print(f'Busy {voice_engine.isBusy()}, {voice_engine._inLoop}')
        if voice_engine._inLoop:
            voice_engine.endLoop()
        voice_engine.say(text)
        voice_engine.runAndWait()


    @staticmethod
    def serialize():
        return {
            'camera': Camera.serialize(),
            'led': Led.serialize()
        }
