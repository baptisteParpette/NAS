from gns3fy import Gns3Connector, Project
from tabulate import tabulate
import re
import json


class Groupe:
    def __init__(self,id,x,y,w,h):
        self.id = id
        self.size=(w,h)
        self.coord=(x,y)
        self.pointUpLeft=(x,y)
        self.pointDownRight=(x+w,y+h)
        self.AS = []
        self.routers = []


if __name__ == '__main__':
    server = Gns3Connector("http://localhost:3080")
    lab = Project(name="nas-gns3", connector=server)
    lab.get()

    groups = []
    numberOfAs=0
    mappage={}
    mappage2={}
    id=1


    for draw in lab.drawings:
        
        svg_string = draw['svg']
        if svg_string.find("rect")!=-1:
            width_match = re.search(r'width="(\d+)"', svg_string)
            height_match = re.search(r'height="(\d+)"', svg_string)

            if width_match and height_match:
                width = int(width_match.group(1))
                height = int(height_match.group(1))
            temp=Groupe(numberOfAs,int(draw['x']),int(draw['y']),width,height)
            groups.append(temp)
            numberOfAs+=1

    for node in lab.nodes:
        for group in groups:
            x1,y1=group.pointUpLeft
            x2,y2=group.pointDownRight
            
            xNode = node.x
            yNode = node.y
            if (x1<=xNode<=x2) and (y1<=yNode<=y2):
                group.routers.append([node,[]])
    
    for text in lab.drawings:
        svg_string = text['svg']
        if svg_string.find("text")!=-1:
            asNumber = re.search(r'>AS_(\d+)<', svg_string)
            if asNumber:
                as_number = int(asNumber.group(1))
            x=int(text['x'])
            y=int(text['y'])
            for group in groups:
                x1,y1=group.pointUpLeft
                x2,y2=group.pointDownRight
                if (x1<=x<=x2) and (y1<=y<=y2):
                    group.AS=as_number  

    for group in groups:
        for routeur in group.routers:
            mappage[routeur[0].node_id]=routeur[0].name
            mappage2[routeur[0].name]=id
            id+=1


    temp=[]
    for link in lab.links:
            interface1=link.nodes[0]["adapter_number"]
            routeur1=link.nodes[0]["node_id"]
            port1=link.nodes[0]["port_number"]
            interface2=link.nodes[1]["adapter_number"]
            routeur2=link.nodes[1]["node_id"]
            port2=link.nodes[1]["port_number"]
            temp.append([mappage[routeur1],interface1,mappage[routeur2],interface2])

    for group in groups:
        for routeur in group.routers:
            routerName=routeur[0].name
            for link in temp:
                if(routerName==link[0]):
                    routeur[1].append([link[2],link[1]])
                elif(routerName==link[2]):
                    routeur[1].append([link[0],link[3]])

    AS_list = []
    numberOfRouter=1
    for group in groups:
        AS_dict = {}
        AS_dict["number"] = str(group.AS)
        AS_dict["IpRange"] = {
            "start": "192.168.64.0",
            "end": "192.168.223.255",
            "mask": "30"
        }
        AS_dict["IpLoopbackRange"] = {
            "start": "192.168.0.0",
            "end": "192.168.63.255",
            "mask": "32"
        }
        AS_dict["igp"] = {"type": "ospf"}
        AS_dict["bgp"] = {"enabled": True, "routerID": "loopback"}
        AS_dict["mpls"] = {"enabled": True, "type": "ldp"}
        AS_dict["baseHostname"] = f"R{group.AS}"

        routers_list = []
        for router in group.routers:
            router_dict = {}
            router_dict["id"] = str(mappage2[router[0].name])
            router_dict["hostname"] = router[0].name
            router_dict["loopback"] = {"ospfArea": "0"}
            router_dict["connections"] = []
            router_dict["bgp"] = {"out": {"networks": "", "filter": {}}, "in": {"filter": {}}}

            
            for link in router[1]:
                connection_dict = {}
                connection_dict["router"] = str(mappage2[link[0]])
                connection_dict["interface"] = str(link[1])
                connection_dict["ospfArea"] = "0"
                connection_dict["ospfCost"] = "1"
                router_dict["connections"].append(connection_dict)
            routers_list.append(router_dict)

        AS_dict["routers"] = routers_list

        AS_list.append(AS_dict)

    data = {"AS": AS_list, "ASLink": {"IpRange": {"start": "192.168.124.0", "end": "192.168.255.255", "mask": "30"}, "links": []}}

    with open("resultats.json", "w") as f:
        json.dump(data, f, indent=4)
