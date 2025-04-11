import time
import board
import digitalio


class MotorController:
    def __init__(self):
        
        self.enable_pin = digitalio.DigitalInOut(board.D18)
        self.coil_A_1_pin = digitalio.DigitalInOut(board.D4)
        self.coil_A_2_pin = digitalio.DigitalInOut(board.D17)
        self.coil_B_1_pin = digitalio.DigitalInOut(board.D23)
        self.coil_B_2_pin = digitalio.DigitalInOut(board.D24)

        self.enable_pin.direction = digitalio.Direction.OUTPUT
        self.coil_A_1_pin.direction = digitalio.Direction.OUTPUT
        self.coil_A_2_pin.direction = digitalio.Direction.OUTPUT
        self.coil_B_1_pin.direction = digitalio.Direction.OUTPUT
        self.coil_B_2_pin.direction = digitalio.Direction.OUTPUT

        self.enable_pin.value = True

        self.STEP_ANGLE = 1.8

    def setStep(self, w1, w2, w3, w4):
        self.coil_A_1_pin.value = w1
        self.coil_A_2_pin.value = w2
        self.coil_B_1_pin.value = w3
        self.coil_B_2_pin.value = w4

    def rotate_degrees(self, degrees, delay):
        steps = int(degrees / self.STEP_ANGLE)  # Calculate how many steps to take
        for _ in range(steps):
            self.setStep(1, 0, 1, 0)
            time.sleep(delay)
            self.setStep(0, 1, 1, 0)
            time.sleep(delay)
            self.setStep(0, 1, 0, 1)
            time.sleep(delay)
            self.setStep(1, 0, 0, 1)
            time.sleep(delay)


if __name__ == "__Main__":
    mc = MotorController()
    # Main loop to rotate by x degrees
    while True:
        user_degrees = float(input("Enter degrees to rotate: "))
        user_delay = float(input("Delay between steps (milliseconds)? ")) / 1000.0
        mc.rotate_degrees(user_degrees, user_delay)
