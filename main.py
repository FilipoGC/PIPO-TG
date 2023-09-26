from src.data import *

Gerador = generator("pipo")

Gerador.addGenerationPort(68)
Gerador.addOutputPort(5, 160, "100G") #Physical Port, Port ID(D_P), Port bw
Gerador.addIP(dst="10.2.2.2", src = "10.2.2.1")
Gerador.addThroughput(3000, "port_shaping") #Define the throughput in Mbps and the mode (port_shaping or meter)
Gerador.generate()
