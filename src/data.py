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
		self.version = 4
		self.ihl = 5
		self.tos = '0x0'
		self.len =  None
		self.frag = 0
		self. flags = None
		self.ttl = 61
		self.proto = 'udp'
		self.chksum = '0x66df'
		self.src =  None
		self.dst =  None
		self.hwsrc =  None
		self.hwdst =  None
		self.type = 'Ipv4'
		self.data =  None
	
	def addGenerationPort(self, port):
		self.generation_port = port
	
	def addOutputPort(self, port, channel, bw):
		self.output_port = port
		self.channel = channel
		self.port_bw = bw
  
	def addIP(self, version = 4, ihl = 5, tos = '0x0',  len = None, frag = 0, flags = None, ttl = 61, proto = 'udp', chksum = '0x66df',src = None, dst = None):
		self.version = version
		self.ihl = ihl
		self.tos = tos
		self.len =  len
		self.frag = frag
		self. flags = flags
		self.ttl = ttl
		self.proto = proto
		self.chksum = chksum
		self.src =  src
		self.dst =  dst
    
	def addEthernet(self, hwsrc = None, hwdst = None, type = 'Ipv4',data = None):
		self.hwsrc =  hwsrc
		self.hwdst =  hwdst
		self.type = type
		self.data =  data	
     
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
