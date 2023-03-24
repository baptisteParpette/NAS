class Router:
    def __init__(self):
        self.id = None
        self.hostname = ""
        self.interfaces = []
        self.loopback = None
        self.igp = None
        self.bgp = None
        self.vrfs = {}


class Interface:
    def __init__(self):
        self.id = None
        self.name = ""
        self.ip = ""
        self.mask = ""
        self.ospf = None
        self.mpls = False
        self.vrfs = []

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
        self.routers = {}
        self.igp = igp
        self.provEdgeRouters = []

class Igp:
    def __init__(self):
        self.id = None
        self.router_id = None
        self.type = None
        self.passive_interfaces = []

class LinksManager:
    def __init__(self, ipStart, ipEnd, mask):
        self.indexLink = ipStart
        self.indexLinkEnd = ipEnd
        self.linkMask = mask

class Bgp:
    def __init__(self, asn, router_id):
        self.id = asn
        self.neighbors = []
        self.router_id = router_id

class Neighbor:
    def __init__(self, remote_as, ip):
        self.remote_as = remote_as
        self.ip = ip

class Vrf:
    def __init__(self, name):
        self.name = name
        self.routeDistinguisher = None
        self.routeTargets = []

class RouteTarget:
    def __init__(self, community, type):
        self.community = community
        self.type = type

