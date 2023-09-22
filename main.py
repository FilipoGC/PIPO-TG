from src.data import *

Gerador = generator("pipo")

Gerador.addGenerationPort(68)
Gerador.addOutputPort(1, 128, "10G") #Physical Port, Port ID(D_P), Port bw
Gerador.addIP(dst="10.2.2.2", src = "10.2.2.2")
Gerador.generate()
