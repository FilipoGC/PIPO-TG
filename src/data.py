from src.GenerateFiles import *

class generator:

	def __init__(self, name):
		self.name = name
		self.p4_code = ''
		self.generation_port = 68
		self.output_port = 0
	
	def addGenerationPort(self, port):
		self.generation_port = port
	
	def addOutputPort(self, port):
		self.output_port = port
	
	def generate(self):
		generatePy(self.generation_port, self.output_port)
		generateP4()
		generateHeader()
		generateUtil()
