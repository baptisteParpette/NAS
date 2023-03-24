import json

from jinja2 import Environment, FileSystemLoader

import models


def incrementSubnetIP(ip, mask, ipMax):
    ip = ip.copy()
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
    ip = ip.copy()
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
    print(ip)
    return ip

    

def handle_network(network):
    ASList = {}
    for As in network['AS']:
        IPstart = list(map(int,As["IpRange"]["start"].split(".")))
        IPend = list(map(int,As["IpRange"]["end"].split(".")))

        LoopbackStart = list(map(int,As["IpLoopbackRange"]["start"].split(".")))
        LoopbackEnd = list(map(int,As["IpLoopbackRange"]["end"].split(".")))

        maskLink = int(As["IpRange"]["mask"])
        maskLoopback = int(As["IpLoopbackRange"]["mask"])
        mpls = As["mpls"]["enabled"]
        number = As["number"]
        igp = As["igp"]["type"]

        as_object = models.AS(IPstart,IPend,LoopbackStart,LoopbackEnd,maskLink, maskLoopback, mpls, number, igp)
        for routeur in As["routers"]:
            as_object.routers.append(handle_router(as_object,routeur))

            
        ASList[number] = as_object
    return ASList

def handle_router(as_object,routeur):
    router_object = models.Router()
    router_object.id = int(routeur['id'])
    router_object.hostname = routeur['hostname']
    router_object.loopback = handle_loopback(as_object, router_object, routeur['loopback'])
    for connection in routeur['connections']:
        router_object.interfaces.append(handle_interface(connection, as_object, router_object))

    router_object.igp = handle_igp(as_object, router_object)





    return router_object

def handle_loopback(as_object, router_object, loopback):
    interfaceLoopback = models.Interface()
    interfaceLoopback.id = 0
    interfaceLoopback.name = "Loopback"+str(interfaceLoopback.id)
    subnet_ip = incrementSubnetIP(as_object.indexLoopback, as_object.maskLoopback, as_object.indexLoopbackEnd)
    interfaceLoopback.ip = ".".join(map(str, subnet_ip))
    as_object.indexLoopback = subnet_ip
    interfaceLoopback.mask = maskFormat(as_object.maskLoopback)
    interfaceLoopback.ospf = models.OspfInterface(router_object.id, loopback['ospfArea'], None)
    return interfaceLoopback


def handle_interface(connection, as_object, router_object):
    interface = models.Interface()
    interface.id = connection["interface"]
    interface.name = "GigabitEthernet" +connection["interface"]+"/0"
    print(as_object.connections)
    if as_object.connections.get(router_object.id) is not None:
        if as_object.connections[router_object.id].get(int(connection['router'])) is not None:
            interface.ip = ".".join(map(str, as_object.connections[router_object.id][int(connection['router'])]))
        else:
            attributeIP(as_object, connection, interface, router_object)
    else:
        as_object.connections[router_object.id] = {}
        attributeIP(as_object, connection, interface, router_object)

    #Convert mask of the form ## to a mask in the form ###.###.###.###
    mask = as_object.maskLink
    mask = maskFormat(mask)
    interface.mask = mask
    interface.mpls = as_object.mpls
    interface.ospf = models.OspfInterface(router_object.id, connection['ospfArea'], connection['ospfCost'])
    return interface


def maskFormat(maskP):
    mask = 2 ** maskP - 1
    mask = mask << (32 - maskP)
    mask = [mask >> 24 & 0xff, mask >> 16 & 0xff, mask >> 8 & 0xff, mask & 0xff]
    mask = ".".join(map(str, mask))
    return mask


def attributeIP(as_object, connection, interface, router_object):
    subnet_ip = as_object.indexLink
    ip1 = incrementIP(subnet_ip, 1)
    ip2 = incrementIP(subnet_ip, 2)
    print("router id : " + str(router_object.id)+ "ip1 : " + str(ip1) + "ip2 : " + str(ip2) + "subnet : " + str(subnet_ip))
    interface.ip = ".".join(map(str, ip1))
    as_object.indexLink = incrementSubnetIP(as_object.indexLink, as_object.maskLink, as_object.indexLinkEnd)
    as_object.connections[router_object.id][int(connection['router'])] = ip1
    if as_object.connections.get(int(connection['router'])) is None:
        as_object.connections[int(connection['router'])] = {}
    as_object.connections[int(connection['router'])][router_object.id] = ip2

def handle_igp(as_object, router_object):
    igp = models.Igp()
    igp.id = router_object.id
    igp.type = as_object.igp
    igp.router_id = router_object.loopback.ip
    return igp

if __name__ == '__main__':
    environment = Environment(loader=FileSystemLoader('templates/'), trim_blocks=True, lstrip_blocks=True)
    template = environment.get_template('configTemplate.txt')
    f = open('network.json', 'r')
    load = json.load(f)
    ASList = handle_network(load)
    f.close()
    for AS in ASList.values():
        for router in AS.routers:
            print(router.hostname)
            f = open("configRendered/" + router.hostname + ".cfg", "w")
            f.write(template.render(router=router))
            f.close()

