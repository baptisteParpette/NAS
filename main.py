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
    
    
    

def handle_network(network):
    ASList = {}
    for As in network['AS']:
        IPstart = list(map(int,As["IpRange"]["start"].split(".")))
        IPend = list(map(int,As["IpRange"]["end"].split(".")))

        LoopbackStart = list(map(int,As["IpLoopbackRange"]["start"].split(".")))
        LoopbackEnd = list(map(int,As["IpLoopbackRange"]["start"].split(".")))

        mask = int(As["IpRange"]["mask"])

        as_object = models.AS(IPstart,IPend,LoopbackStart,LoopbackEnd,mask)
        for routeur in As:
            handle_router(as_object,routeur)

            
            pass

def handle_router(as_object,routeur):
    loopback=handle_loopback(as_object)



    pass

def handle_loopback(as_object):
    pass



if __name__ == '__main__':
    pass
