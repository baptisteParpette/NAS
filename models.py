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
    def __init__(self, id, area =0 , cost = 0):
        self.id = id
        self.area = area
        self.cost = cost

class AS:
    def __init__(self, ipStart, ipEnd, loopbackStart, loopbackEnd, maskLink, maskLoopback, mpls, number, igp):
        self.number = number
        self.connections = {}
        self.maskLink=maskLink
        self.maskLoopback = maskLoopback
        self.indexLinkEnd = ipEnd
        self.indexLoopbackEnd = loopbackEnd
        self.indexLoopback = loopbackStart
        self.indexLink = ipStart
        self.mpls = mpls
        self.routers = []
        self.igp = igp

class Igp:
    def __init__(self):
        self.id = None
        self.router_id = None
        self.type = None
        self.passive_interfaces = []


