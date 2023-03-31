from gns3fy import Gns3Connector, Project
from tabulate import tabulate
import re
import json

class Groupe:
    def __init__(self,id,x,y,w,h,color,ipRangeStart,ipRangeEnd,ipRangeMask,ipLoopbackStart,ipLoopbackEnd,ipLoopbackMask,igp):
        self.id = id
        self.size=(w,h)
        self.coord=(x,y)
        self.pointUpLeft=(x,y)
        self.pointDownRight=(x+w,y+h)
        self.AS = []
        self.routers = []
        self.color=color
        self.ipRangeStart=ipRangeStart
        self.ipRangeEnd=ipRangeEnd
        self.ipRangeMask=ipRangeMask

        self.ipLoopbackStart=ipLoopbackStart
        self.ipLoopbackEnd=ipLoopbackEnd
        self.ipLoopbackMask=ipLoopbackMask
        self.igp=igp


def findInter(startR, endR):
    for group in groups:
        for router in group.routers:
            for link in router[1]:
                if link[0]==endR and router[0].name==startR:
                    return link[1]

if __name__ == '__main__':
    server = Gns3Connector("http://localhost:3080")
    lab = Project(name="nas-gns3", connector=server)
    lab.get()

    groups = []
    numberOfAs=0
    mappage={}
    mappage2={}
    mappage3={}
    id=1

    for draw in lab.drawings:
        
        svg_string = draw['svg']
        if svg_string.find("rect")!=-1:
            width_match = re.search(r'width="(\d+)"', svg_string)
            height_match = re.search(r'height="(\d+)"', svg_string)

            if width_match and height_match:
                width = int(width_match.group(1))
                height = int(height_match.group(1))

            fill_color_match = re.search(r'fill="#([a-fA-F0-9]{6})"', svg_string)

            if fill_color_match:
                fill_color = fill_color_match.group(1)





            temp=Groupe(numberOfAs,int(draw['x']),int(draw['y']),width,height,fill_color,None,None,None,None,None,None,None)
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

                        for text_t in lab.drawings:
                            svg_string = text_t['svg']
                            if svg_string.find("text")!=-1:
                                pattern = r'ipRange_start =\s*(\S+)\nipRange_end =\s*(\S+)\nipRange_mask=\s*(\d+)\n\nipLoopback_start =\s*(\S+)\nipLoopback_end =\s*(\S+)\nipLoopback_mask=\s*(\d+)\n\nigp=\s*(\S+?)<\/text><\/svg>'
                                resultat = re.search(pattern, svg_string)

                                if resultat:
                                    ipRange_start = str(resultat.group(1))
                                    ipRange_end = str(resultat.group(2))
                                    ipRange_mask = str(int(resultat.group(3)))
                                    ipLoopback_start = str(resultat.group(4))
                                    ipLoopback_end = str(resultat.group(5))
                                    ipLoopback_mask = str(int(resultat.group(6)))
                                    igp = resultat.group(7)

                                    x_t=int(text_t['x'])
                                    y_t=int(text_t['y'])

                                    if (x1<=x_t<=x2) and (y1<=y_t<=y2):
                                        group.ipRangeStart=ipRange_start
                                        group.ipRangeEnd=ipRange_end
                                        group.ipRangeMask=ipRange_mask

                                        group.ipLoopbackStart=ipLoopback_start
                                        group.ipLoopbackEnd=ipLoopback_end
                                        group.ipLoopbackMask=ipLoopback_mask
                                        group.igp=igp




    for group in groups:
        for routeur in group.routers:
            mappage[routeur[0].node_id]=routeur[0].name
            mappage2[routeur[0].name]=id
            mappage3[routeur[0].name]=group.AS

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
            "start": group.ipRangeStart,
            "end": group.ipRangeEnd,
            "mask": group.ipRangeMask
        }
        AS_dict["IpLoopbackRange"] = {
            "start": group.ipLoopbackStart,
            "end": group.ipLoopbackEnd,
            "mask": group.ipLoopbackMask
        }
        print(group.AS, group.ipRangeMask,group.ipLoopbackMask)
        AS_dict["igp"] = {"type": group.igp}
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
    
    ASLinks = {"IPRange": {"start": "192.168.124.0", "end": "192.168.255.255", "mask": "30"}, "links": []}


    mappage4={}
    inc=1
    for group in groups:
        if group.AS!=100:
            existing_value = mappage4.get(group.color)
            if existing_value is None:
                mappage4[group.color] = inc
                inc += 1

    for group in groups:
        if group.AS!=100:
            for router in group.routers:
                for link in router[1]:
                    if "PE" in link[0]:

                        router2=link[0]

                        interface=findInter(str(router2),str(router[0].name))
                        color=mappage4[group.color]


                        link = {
                        "firstAS": str(mappage3[router2]),
                        "firstRouter": str(mappage2[router2]),
                        "firstInterface": {"id": str(interface)},
                        "secondAS": str(group.AS),
                        "secondRouter": str(mappage2[router[0].name]),
                        "secondInterface": {"id": str(link[1])},
                        "relationship": "vpnclient",
                        "client": str(color),
                        "filter1": {"in": {"prefixes": []}, "out": {"prefixes": []}},
                        "filter2": {"in": {"prefixes": []}, "out": {"prefixes": []}}}

                        ASLinks["links"].append(link)

    data = {"AS": AS_list, "ASLink": ASLinks}

    with open("network.json", "w") as f:
        json.dump(data, f, indent=4)
