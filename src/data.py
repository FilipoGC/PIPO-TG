from src.GenerateFiles import *

class generator:

	def __init__(self, name):
		self.name = name
		self.p4_code = ''
		self.generation_port = 68
		self.output_port = 0
		self.channel = 0
		self.port_bw = ''
		self.throughput_defined = False
		self.throughput = 0
		self.throughput_mode = '' #meter or port_shaping
	
	def addGenerationPort(self, port):
		self.generation_port = port
	
	def addOutputPort(self, port, channel, bw):
		self.output_port = port
		self.channel = channel
		self.port_bw = bw
  
	#pps = packets per second, len = packet size
	def addIP(src = None, dst = None, pps = None, len = None):
		print("src:", src)
		print("dst:", dst)
		print("pps:", pps)
		print("length:", pps)	
      
	def addThroughput(self, throughput, mode):
		self.throughput_defined = True
		self.throughput = throughput
		self.throughput_mode = mode

	def generate(self):
		generatePy(self.generation_port, self.channel, self.throughput_defined, self.throughput_mode, self.throughput)
		generateP4(self.throughput_defined, self.throughput_mode)
		generateHeader()
		generateUtil()
		generatePortConfig(self.output_port, self.port_bw)
