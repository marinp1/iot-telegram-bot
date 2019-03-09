import energenie

class EnergeniePlug:
    def __init__(self):
        energenie.init()
        self.devices = {
            'all': energenie.Devices.MIHO008((None, 0)),
            'plug_2': energenie.Devices.MIHO008((None, 2)),
            'plug_4': energenie.Devices.MIHO008((None, 4)),
        }
        
    def on(self, id):
        self.devices[id].turn_on()
        
    def off(self, id):
        self.devices[id].turn_off()
        
    def cleanup(self):
        energenie.finished()
