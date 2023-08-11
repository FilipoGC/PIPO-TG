from src.GenerateFiles import *

class generator:

	def __init__(self, name):
		self.name = name
		self.p4_code = ''
		self.generation_port = 68
		self.output_port = 0
		self.channel = 0
	
	def addGenerationPort(self, port):
		self.generation_port = port
	
	def addOutputPort(self, port, channel):
		self.output_port = port
		self.channel = channel


	def generate(self):
		generatePy(self.generation_port, self.channel)
		generateP4()
		generateHeader()
		generateUtil()
		generatePortConfig(self.output_port)
