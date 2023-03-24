import models 


def incrementSubnetIP(ip, mask, ipMax):
    add = 2 ** (32 - mask)
    ip[3] += add
    if ip[3] > 255:
        ip[2] += 1
        ip[3] -= 256
    if ip[2] > 255:
        ip[1] += 1
        ip[2] -= 256
    if ip[1] > 255:
        ip[0] += 1
        ip[1] -= 256
    if ip[0] > 255:
        raise Exception("IP overflow")
    if ip > ipMax:
        raise Exception("Ip is greater than max")
    return ip
    
def incrementIP(ip, amount):
    ip[3] += amount
    if ip[3] > 255:
        ip[2] += 1
        ip[3] -= 256
    if ip[2] > 255:
        ip[1] += 1
        ip[2] -= 256
    if ip[1] > 255:
        ip[0] += 1
        ip[1] -= 256
    if ip[0] > 255:
        raise Exception("IP overflow")
    return ip

    

def handle_network(network):
    ASList = {}
    for As in network['AS']:
        IPstart = list(map(int,As["IpRange"]["start"].split(".")))
        IPend = list(map(int,As["IpRange"]["end"].split(".")))

        LoopbackStart = list(map(int,As["IpLoopbackRange"]["start"].split(".")))
        LoopbackEnd = list(map(int,As["IpLoopbackRange"]["start"].split(".")))

        mask = int(As["IpRange"]["mask"])
        mpls = As["mpls"]["enabled"]
        as_object = models.AS(IPstart,IPend,LoopbackStart,LoopbackEnd,mask, mpls)
        for routeur in As:
            handle_router(as_object,routeur)

            
            pass

def handle_router(as_object,routeur):
    loopback=handle_loopback(as_object)



    pass

def handle_loopback(as_object):
    pass

def handle_interface(connection, as_object, router_object):
    interface = models.Interface()
    interface.id = connection["interface"]
    interface.name = "GigabitEthernet" +connection["interface"]+"/0"
    if as_object.connections.get(router_object.id) is not None:
        if as_object.connections[router_object.id].get(connection['router']) is not None:
            interface.ip = as_object.connections[router_object.id][connection['router']]
        else:
            attributeIP(as_object, connection, interface, router_object)
    else:
        as_object.connections[router_object.id] = {}
        attributeIP(as_object, connection, interface, router_object)

    #Convert mask of the form ## to a mask in the form ###.###.###.###
    mask = as_object.mask
    mask = 2 ** mask - 1
    mask = mask << (32 - as_object.mask)
    mask = [mask >> 24 & 0xff, mask >> 16 & 0xff, mask >> 8 & 0xff, mask & 0xff]
    mask = ".".join(map(str, mask))
    interface.mask = mask
    interface.mpls = as_object.mpls
    interface.ospf = models.OspfInterface(router_object.id, connection['ospfArea'], connection['ospfCost'])



def attributeIP(as_object, connection, interface, router_object):
    subnet_ip = incrementSubnetIP(as_object.indexLink, as_object.mask, as_object.indexLinkEnd)
    ip1 = incrementIP(subnet_ip, 1)
    ip2 = incrementIP(subnet_ip, 2)
    interface.ip = ip1
    as_object.indexLink = subnet_ip
    as_object.connections[router_object.id][connection['router']] = ip1
    as_object.connections[connection['router']][router_object.id] = ip2


if __name__ == '__main__':
    pass
