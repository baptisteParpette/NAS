import json

from jinja2 import Environment, FileSystemLoader

import models


def incrementSubnetIP(ip, mask, ipMax):
    """
    Calculate and return the next IPv4 address within a subnet range.

    This function computes the next IPv4 address from a given address and mask,
    considering the maximum allowed IPv4 address in the subnet range.

    Parameters:
        ip (List[int]): The reference IPv4 address in the format [xxx, xxx, xxx, xxx]. Example: ip = [192, 168, 0, 0]\n
        mask (int): The subnet mask.\n
        ipMax (List[int]): The maximum IPv4 address in the range, in the format [xxx, xxx, xxx, xxx]. Example: ipMax = [192, 168, 255, 255]\n

    Returns:
        List[int]: The new IPv4 address within the subnet range.

    Raises:
        Exception: If the calculated IPv4 address overflows the valid address range or is greater than the maximum allowed IPv4 address.
    """
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
    """
    Calculate and return the incremented IPv4 address by a given amount.

    This function computes the IPv4 address by incrementing the given IP address
    with a specified amount.

    Parameters:
        ip (List[int]): The reference IPv4 address in the format [xxx, xxx, xxx, xxx]. Example: ip = [192, 168, 0, 0]\n
        amount (int): The number of steps to increment the IP address. Example: amount = 2

    Returns:
        List[int]: The incremented IPv4 address in the format [xxx, xxx, xxx, xxx]. Example: ip = [192, 168, 0, 2]

    Raises:
        Exception: If the calculated IPv4 address overflows the valid address range.
    """
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
    '''
    This function creates objects representing Autonomous Systems (AS) based on a provided network architecture.

    Parameters:
        network (dict): A JSON object representing the network architecture, which must contain a key 'AS' with a list of AS objects.

    Returns:
        dict: A dictionary containing all the created AS objects, indexed by their AS number.

    Raises:
        ValueError: If the 'AS' key is missing from the provided JSON object.
    '''

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
            as_object.routers[int(routeur['id'])] = handle_router(as_object,routeur)

            
        ASList[number] = as_object

    handle_AS_links(ASList, network['ASLink'])
    return ASList

def handle_router(as_object,routeur):
    """
    This function creates objects representing routers based on a provided router list.

    Parameters:
        as_object (AS object): The AS object to which the router belongs.\n
        routeur (dict): A dictionary representing the router to be created, with keys 'id', 'hostname', 'loopback', and 'connections'.\n

    Returns:
        Router object: An object representing the created router.
    """
    router_object = models.Router()
    router_object.id = int(routeur['id'])
    router_object.hostname = routeur['hostname']
    router_object.loopback = handle_loopback(as_object, router_object, routeur['loopback'])
    for connection in routeur['connections']:
        router_object.interfaces.append(handle_interface(connection, as_object, router_object))

    router_object.igp = handle_igp(as_object, router_object)
    return router_object

def handle_loopback(as_object, router_object, loopback):
    """
    This function creates objects representing loopback interfaces based on a provided loopback list.

    Parameters:
        as_object (AS object): The AS object to which the loopback interface belongs.\n
        router_object (Router object): The router object to which the loopback interface belongs.\n
        loopback (dict): A dictionary representing the loopback interface to be created, with keys 'ospfArea'.\n

    Returns:
        OspfInterface object: An object representing the created loopback interface.
    """
     
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
    """
    This function creates objects representing loopback interfaces based on a provided loopback list.

    Parameters:
        as_object (AS object): The AS object to which the loopback interface belongs.\n
        router_object (Router object): The router object to which the loopback interface belongs.\n
        loopback (dict): A dictionary representing the loopback interface to be created, with keys 'ospfArea'.

    Returns:
        OspfInterface object: An object representing the created loopback interface.
    """
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
    mask = as_object.maskLink
    mask = maskFormat(mask)
    interface.mask = mask
    interface.mpls = as_object.mpls
    interface.ospf = models.OspfInterface(router_object.id, connection['ospfArea'], connection['ospfCost'])
    return interface


def maskFormat(maskP):
    """
    This function converts a CIDR mask to a dotted decimal subnet mask.

    Parameters:
        maskP (int): The CIDR mask to be converted.

    Returns:
        str: The subnet mask in dotted decimal notation.

    Example:
        mask = maskFormat(24)
    """
    mask = 2 ** maskP - 1
    mask = mask << (32 - maskP)
    mask = [mask >> 24 & 0xff, mask >> 16 & 0xff, mask >> 8 & 0xff, mask & 0xff]
    mask = ".".join(map(str, mask))
    return mask


def attributeIP(as_object, connection, interface, router_object):
    """
    This function attributes IP addresses to a given interface.

    Args:
        as_object (AS object): The AS object to which the interface belongs.\n
        connection (dict): A dictionary representing the connection to another router, with keys 'router' and 'interface'.\n
        interface (Interface object): The interface to which the IP addresses should be assigned.\n
        router_object (Router object): The router object to which the interface belongs.

    Returns:
        None.
    """
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
    """
    This function creates objects representing Interior Gateway Protocols (IGP) based on a provided AS object and router object.

    Args:
        as_object (AS object): The AS object to which the IGP belongs.\n
        router_object (Router object): The router object to which the IGP belongs.

    Returns:
        Igp object: An object representing the created IGP.
    """
    igp = models.Igp()
    igp.id = router_object.id
    igp.type = as_object.igp
    igp.router_id = router_object.loopback.ip
    return igp



def handle_AS_links(ASList, links):
    ipStart = list(map(int,links["IPRange"]["start"].split(".")))
    ipEnd = list(map(int,links['IPRange']['end'].split(".")))
    mask = int(links['IPRange']['mask'])
    linkManager = models.LinksManager(ipStart, ipEnd, mask)

    for link in links['links']:
        AS1 = ASList[link['firstAS']]
        AS2 = ASList[link['secondAS']]
        router1 = AS1.routers[int(link['firstRouter'])]
        router2 = AS2.routers[int(link['secondRouter'])]
        handle_link_router(AS1, AS2,router1, router2, link, linkManager)

    for AS in ASList.values():
        handle_neighbors(AS)


def handle_link_router(AS1, AS2, router1, router2, link, linkManager):

    bgp1 = models.Bgp(AS1.number, router1.loopback.ip)
    bgp2 = models.Bgp(AS2.number, router2.loopback.ip)
    router1.bgp = bgp1
    router2.bgp = bgp2
    interface1 = models.Interface()
    interface1.id = int(link['firstInterface']['id'])
    interface1.name = "GigabitEthernet" + str(interface1.id) + "/0"
    subnetIP = linkManager.indexLink
    ip1 = incrementIP(subnetIP, 1)
    ip2 = incrementIP(subnetIP, 2)
    interface1.ip = ".".join(map(str, ip1))
    linkManager.indexLink = incrementSubnetIP(linkManager.indexLink, linkManager.linkMask, linkManager.indexLinkEnd)
    mask = linkManager.linkMask
    mask = maskFormat(mask)
    interface1.mask = mask
    if link['relationship'] == "vpnclient":
        if not router1.id in AS1.provEdgeRouters:
            AS1.provEdgeRouters.append(router1.id)
        client = link['client']
        VRFclientName = "v" + str(client)
        if not VRFclientName in router1.vrfs:
            router1.vrfs[VRFclientName] = models.Vrf(VRFclientName)
        vrf = router1.vrfs[VRFclientName]
        vrf.routeDistinguisher = str(client) +":500"
        routeTargetImp = models.RouteTarget(str(client) +":" + str(client), "import")
        routeTargetExp = models.RouteTarget(str(client) +":" + str(client), "export")
        vrf.routeTargets.append(routeTargetImp)
        vrf.routeTargets.append(routeTargetExp)
        interface1.vrfs.append(vrf.name)




    router1.interfaces.append(interface1)



    # interface2 = models.Interface()
    # interface2.id = int(link['secondInterface']['id'])
    # interface2.name = "GigabitEthernet" + str(interface2.id) + "/0"
    # interface2.ip = ".".join(map(str, ip2))
    # interface2.mask = mask
    # router2.interfaces.append(interface2)
    # if not router1.id in AS1.provEdgeRouters:
    #     AS1.provEdgeRouters.append(router1.id)





def handle_neighbors(AS):
    for router in AS.provEdgeRouters:
        for neighbor in AS.provEdgeRouters:
            if neighbor != router:
                neighbor_object = models.Neighbor(AS.number, AS.routers[neighbor].loopback.ip)
                AS.routers[router].bgp.neighbors.append(neighbor_object)




if __name__ == '__main__':
    environment = Environment(loader=FileSystemLoader('templates/'), trim_blocks=True, lstrip_blocks=True)
    template = environment.get_template('configTemplate.txt')
    f = open('network.json', 'r')
    load = json.load(f)
    ASList = handle_network(load)
    f.close()
    for AS in ASList.values():
        for router in AS.routers.values():
            print(router.hostname)
            f = open("configRendered/" + router.hostname + ".cfg", "w")
            f.write(template.render(router=router))
            f.close()

