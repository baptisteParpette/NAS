class Router:
    def __init__(self):
        self.id = None
        self.hostname = ""
        self.interfaces = []
        self.loopback = None
        self.igp = None
        self.bgp = None


class Interface:
    def __init__(self):
        self.id = None
        self.name = ""
        self.ip = ""
        self.mask = ""
        self.ospf = None
        self.mpls = False

class OspfInterface:
    def __init__(self):
        self.id = None
        self.area = None
        self.cost = None


class Igp:
    def __init__(self):
        self.id = None
        self.router_id = None
        self.type = None
        self.passive_interfaces = []


