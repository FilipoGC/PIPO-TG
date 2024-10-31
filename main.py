from src.data import *
from src.headers import *

Gerador = generator("pipo")

Gerador.addGenerationPort(68)
Gerador.addOutputPort(5, 160, "100G") #Physical Port, Port ID(D_P), Port bw
Gerador.addIP(ip_dst="10.2.2.2", ip_src = "10.2.2.1", pkt_len = 1024)
Gerador.addThroughput(3000, "port_shaping") #Define the throughput in Mbps and the mode (port_shaping or meter)




#chicoHeader = Header(name="chico", size=12)
#chicoHeader.addField([Field("src", 4), Field("dst", 4), Field("type", 4)])

#pipoHeader = Header(name="pipo", size=16)
#pipoHeader.addField([Field("src", 4), Field("dst", 4), Field("type", 4), Field("pad", 4)])

#Gerador.addHeader(chicoHeader)
#Gerador.addHeader(pipoHeader)


#Gerador.generate()
