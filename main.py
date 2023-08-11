from src.data import *

Gerador = generator("pipo")

Gerador.addGenerationPort(68)
Gerador.addOutputPort(1, 128) #Physical Port, Port ID(D_P)
Gerador.generate()