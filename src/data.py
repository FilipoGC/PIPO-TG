from src.GenerateFiles import *
from src.headers import *

class generator:

	def __init__(self, name):
		#config params
		self.name = name
		self.p4_code = ''
		self.generation_port = 68
		self.output_port = 0
		self.channel = 0
		self.port_bw = ''
		self.throughput_defined = False
		self.throughput = 0
		self.throughput_mode = '' #meter or port_shaping
		self.pktLen = 64

		#list of customized headers
		self.headers = []

		#header params
		self.version = 4
		self.ihl = 5
		self.tos = '0x0'
		self.len =  None
		self.frag = 0
		self.flags = None
		self.ttl = 61
		self.proto = 'udp'
		self.chksum = '0x66df'
		self.src =  None
		self.dst =  None
		self.hwsrc =  None
		self.hwdst =  None
		self.type = 'Ipv4'
		self.data =  None

		#defineds
		self.eth_defined = False
		self.IP_defined = False
		self.udp_defined = False
		self.tcp_defined = False

		#new params
		self.eth_dst = "00:01:02:03:04:05"
		self.eth_src = "00:06:07:08:09:0a"
		self.ip_src = "192.168.0.1"
		self.ip_dst = "192.168.0.2"
		self.ip_proto = 0
		self.ip_tos = 0
		self.vlan_vid = 0
		self.vlan_pcp = 0
		self.dl_vlan_cfi = 0
		self.dl_vlan_enable = False
		self.ip_ecn=None
		self.ip_dscp=None
		self.ip_ttl=64
		self.ip_id=0x0001
		self.ip_ihl=None
		self.ip_options=False


	def addGenerationPort(self, port):
		self.generation_port = port
	
	def addOutputPort(self, port, channel, bw):
		self.output_port = port
		self.channel = channel
		self.port_bw = bw

	def addIP(self, pktlen=100, eth_dst="00:01:02:03:04:05", eth_src="00:06:07:08:09:0a", dl_vlan_enable=False, vlan_vid=0, vlan_pcp=0, dl_vlan_cfi=0, ip_src="192.168.0.1", ip_dst="192.168.0.2", ip_tos=0, ip_ecn=None, ip_dscp=None, ip_ttl=64, ip_id=0x0001, ip_ihl=None, ip_options=False, ip_proto=0):

		"""
		Return a simple dataplane IP packet

		Supports a few parameters:
		@param len Length of packet in bytes w/o CRC
		@param eth_dst Destinatino MAC
		@param eth_src Source MAC
		@param dl_vlan_enable True if the packet is with vlan, False otherwise
		@param vlan_vid VLAN ID
		@param vlan_pcp VLAN priority
		@param ip_src IP source
		@param ip_dst IP destination
		@param ip_tos IP ToS
		@param ip_ecn IP ToS ECN
		@param ip_dscp IP ToS DSCP
		@param ip_ttl IP TTL
		@param ip_id IP ID

		Generates a simple IP packet.  Users
		shouldn't assume anything about this packet other than that
		it is a valid ethernet/IP frame.
		"""
		self.IP_defined = True

		self.pktLen = pktlen
		self.hwdst = eth_dst
		self.hwsrc = eth_src
		self.src = ip_src
		self.dst = ip_dst
		#self.ttl = ip_ttl
		#self.ihl = ip_ihl
		self.tos = ip_tos
		self.proto = ip_proto

		self.eth_dst = eth_dst
		self.eth_src = eth_src
		self.ip_src = ip_src
		self.ip_dst = ip_dst
		self.ip_proto = ip_proto
		self.ip_tos = ip_tos
		self.vlan_vid = vlan_vid
		self.vlan_pcp = vlan_pcp
		self.dl_vlan_cfi = dl_vlan_cfi
		self.dl_vlan_enable = dl_vlan_enable
		self.ip_ecn= ip_ecn
		self.ip_dscp= ip_dscp
		self.ip_ttl= ip_ttl
		self.ip_id= ip_id
		self.ip_ihl= ip_ihl
		self.ip_options= ip_options
    
	def addEthernet(self, hwsrc = None, hwdst = None, type = 'Ipv4',data = None):
		self.hwsrc =  hwsrc
		self.hwdst =  hwdst
		self.type = type
		self.data =  data	
     
	def addThroughput(self, throughput, mode):
		self.throughput_defined = True
		self.throughput = throughput
		self.throughput_mode = mode

	def addHeader(self, header):	
		if isinstance(header, Header) or isinstance(header, list):

			if isinstance(header, list):

				if len(header) ==0:
					print("ERROR! The list of headers is invalid!")
					sys.exit()

				for fi in header:
					if not isinstance(fi, Header):
						print("ERROR! The list of headers is invalid!")
						sys.exit()
					
					if not fi.validHeader():
						print("ERROR! The list of headers is invalid!")
						sys.exit()

				self.headers.extend(header)

			else:
				if not header.validHeader():
						print("ERROR! The header is invalid!")
						sys.exit()
	
				self.headers.append(header)


			#print("Sucessfull!")

		else:
			print("ERROR! The list of fields is invalid!")
			sys.exit()

	def printHeaders(self):

		print("Customized headers defined:")
		for hdr in self.headers:
			hdr.printHeader()


	def generate(self):
		
		if not self.eth_defined and not self.IP_defined and not self.udp_defined and not self.tcp_defined:
			self.eth_defined = True		

		generatePy(self.generation_port, self.channel, self.throughput_defined, self.throughput_mode, self.throughput, self)
		generateP4(self.throughput_defined, self.throughput_mode, self)
		generateHeader(self.headers, self.eth_defined, self.IP_defined, self.udp_defined, self.tcp_defined)
		generateUtil()
		generatePortConfig(self.output_port, self.port_bw)
		self.printHeaders()
