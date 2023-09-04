from src.data import *

Gerador = generator("pipo")

Gerador.addGenerationPort(68)
Gerador.addOutputPort(1, 128, "10G") #Physical Port, Port ID(D_P), Port bw
Gerador.generate()
