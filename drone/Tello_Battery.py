from djitellopy import Tello
tello = Tello()
tello.connect(False)
print("Battery percentage:", tello.query_battery())