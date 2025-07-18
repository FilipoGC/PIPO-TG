# PIPO-TG: Parameterizable High Performance Traffic Generation
⚠️**This repository is in state of development**

## About PIPO-TG
PIPO-TG is positioned, focusing on the creation of a traffic generator specifically designed for the Tofino Switch. Powered by the P4 programmable data plane technology, the PIPO-TG offers the capability to customize and forward packets on the TNA architecture with line-rate packet generation, ensuring accurate performance evaluations without introducing bottlenecks or distortions. With the goal of to develop a traffic generator that can generate realistic and diverse traffic patterns. It incorporates the ability to emulate various network anomalies and behavior patterns. By simulating scenarios such as network congestion, link failures, packet drops, and other disruptive events, PIPO-TG enables researchers to assess the resilience and performance of network systems under realistic and challenging conditions.

PIPO-TG extends Tofino traffic generation capabilities and provides features never seen in other Tofino-based traffic generators. In Figure below, we illustrate the entire traffic generation process: 1️⃣ users set the traffic generation parameters, 2️⃣ PIPO-TG generates traffic utilizing the Tofino traffic generation unit, 3️⃣ tailors it using the PIPO-TG P4 code, and 4️⃣ subsequently routes it to the user’s P4 code or the designated physical port.

![Alt text](https://github.com/FilipoGC/PIPO-TG/blob/main/images/tg_mod.jpg)

___
<p align="center">
  To keep updated about this project, please don't forget to star ⭐️ the repository.
</p>

___
## Requiriments

- git
- python3
- Tofino Switch™

## Installation
```terminal
$ git clone https://github.com/FilipoGC/PIPO-TG.git
```
## How to run
- set environment variables in Tofino
- Prepare the device that will receive the traffic
- Change "main.py" according to the desired traffic, and with the correct port configuration

*working in bf-sde 9.12.0
  
```terminal
$ python3 main.py
$ ./execut.sh
```
## Usage
#Functions
```python
#this values are default(if not declare in parameters)
addIP(pktlen=100, eth_dst="00:01:02:03:04:05", eth_src="00:06:07:08:09:0a", dl_vlan_enable=False, vlan_vid=0, vlan_pcp=0, dl_vlan_cfi=0, ip_src="192.168.0.1", ip_dst="192.168.0.2", ip_tos=0, ip_ecn=None, ip_dscp=None, ip_ttl=64, ip_id=0x0001, ip_ihl=None, ip_options=False, ip_proto=0)
        #pktlen (Length of packet in bytes w/o CRC)
        #eth_dst (Destinatino MAC)
	#eth_src (Source MAC)
	#dl_vlan_enable (True if the packet is with vlan, False otherwise)
	#vlan_vid (VLAN ID)
	#vlan_pcp (VLAN priority)
	#ip_src (IP source)
	#ip_dst (IP destination)
	#ip_tos (IP ToS)
	#ip_ecn (IP ToS ECN)
	#ip_dscp (IP ToS DSCP)
	#ip_ttl (IP TTL)
	#ip_id (IP ID)
```

```python
#this values are default(if not declare in parameters)
addEthernet(hwsrc = None, hwdst = None, type = 'Ipv4',data = None):
  #hwsrc (Source MAC)
  #hwdst (Destinatino MAC)
  #type (protocol)
  #data (data)
```

```python
addThroughput(throughput, mode):
  #throughput (value of throughput)
  #mode ("port_shaping" or "meter")
```

```python
printHeaders
  #print the defined headers
```

```python
NameTrafficGenerator = PipoGenerator()
  #instatiate the traffic generator with the name "NameTrafficGenerator"
```
```python
NameTrafficGenerator.addGenerationPort(port)
  #port (generation port on Tofino)
```

```python
NameTrafficGenerator.addOutputPort(port, channel, bw)
  #port (physical port)
  #channel (port ID(D_P))
  #bw (portBW)
```
## Example
To define the generated traffic, the user needs to write a simple Python script describing the traffic patterns in main.py, we can see a example below.
In that example of PIPO-TG input code to generate IP packets at 100 Mbps with destination IP 10.0.0.2 and a custom header to be sent via physical port 5. Additionally, the user defines configuration details such as the pipeline generation port, port bandwidth, and the type of traffic limitation desired.

```python

myTG = PipoGenerator()                             #instatiate the traffic generator
myTG.addGenerationPort(68)                         #define the generation port
myTG.addOutputPort(5, 160, "100G")                 #physical port, port ID(D_P), portBW
myGenerator.addIP(dst = "10.0.0.2")                #set IP header with destination address
customHeader = Header(name = "myHeader", size = 8) #create a 8 bits cutom header part 1
customHeader.addField(Field("metadata", 8))        #create a 8 bits cutom header part 1
myTG.addHeader(customHeader)                       #create a 8 bits cutom header part 3
myTG.addTroughput(100,"meter")                     #define throughput(Mbps) and the type(port_shaping or meter)
myTG.generate()                                    #start traffic generation

```

In the code below, we presents the additional code necessary to generate burst traffic using PIPO-TG. In this example, we define that the bursts will be standard IP packets sent to port 5. Instead of limiting a throughput, we use the command **addVariance()** to define that we will have a throughput of 10 Gbps for 8s, followed by 90 Gbps for 2s. It means that we will have regular traffic of 10 Gbps, and every 8s, we will have a burst of 90 Gbps lasting 2s.

```python

myTG = PipoGenerator()                             #instatiate the traffic generator
myTG.addGenerationPort(68)                         #define the generation port
myTG.addOutputPort(5, 160, "100G")                 #physical port, port ID(D_P), portBW
myGenerator.addIP(dst = "10.0.0.2")                #set IP header with destination address

myTG.addVariance([10000, 90000], [8, 2])	   #([Throughputs], [Intervals])

myTG.generate()                                    #start traffic generation
```
The next example outlines the DDoS attack scenario. The user specifies a desired throughput, in this case, 10 Gbps, and provides a pool of IP addresses for the attackers, each with an IP base and a mask. Attackers can use a portion of the available link bandwidth to send traffic randomly. The destination IP, representing the target address for the attackers, is defined. Traffic generation starts subsequently.

```python

myTG = PipoGenerator()                             #instatiate the traffic generator
myTG.addGenerationPort(68)                         #define the generation port
myTG.addOutputPort(5, 160, "100G")                 #physical port, port ID(D_P), portBW

myTG.addThroughput(10000,"meter")		   #define throughput(Mbps) and the type(port_shaping or meter)
myTG.addIP(src="192.168.1.0", srcRandom = True, srcMask = 24, dst="192.168.2.2")
myTG.generate()                                    #start traffic generation
```

## Team

- **Filipo G. Costa**, Federal University of Pampa (UNIPAMPA), Brazil
- **Francisco G. Vogt**, University of Campinas (UNICAMP), Brazil
- **Fabricio Rodrıguez Cesen**, University of Campinas (UNICAMP), Brazil
- **Ariel Goes de Castro**, University of Campinas (UNICAMP), Brazil
- **Marcelo Caggiani Luizelli**, Federal University of Pampa (UNIPAMPA), Brazil 
- **Christian Esteve Rothenberg**, University of Campinas (UNICAMP), Brazil

