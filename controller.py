import energenie

class EnergeniePlug:
    def __init__(self):
        energenie.init()
        self.device = energenie.Devices.MIHO008((None, 0))
        
    def on(self):
        self.device.turn_on()
        
    def off(self):
        self.device.turn_off()
        
    def cleanup(self):
        energenie.finished()
