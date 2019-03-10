import energenie
import time

class IndividualSocket:
    def __init__(self, id, name = None):
        self.device = energenie.Devices.MIHO008((None, id))
        self.id = id
        self.name = 'Socket #{}'.format(id) if name is None else name
        self.turn_off()

    def turn_on(self, no_action = False):
        self.value = True
        self.device.turn_on()

    def turn_off(self):
        self.value = False
        self.device.turn_off()

    def get_name(self):
        return self.name

    def get_value(self):
        return self.value

    def rename(self, new_name):
        self.name = new_name.strip()
        return self.name

class EnergenieSocketController:
    def __init__(self):
        energenie.init()
        self.all_sockets = []

    def add_socket(self, id):
        socket = IndividualSocket(id)
        self.all_sockets.append(socket)
        return socket

    def turn_all_off(self):
        for socket in self.all_sockets:
            socket.turn_off()

    def turn_all_on(self):
        for socket in self.all_sockets:
            socket.turn_on()
    
    def cleanup(self):
        energenie.finished()