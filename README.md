# PIPO-TG: Parameterizable High Performance Traffic Generation


## About PIPO-TG
PIPO-TG is positioned, focusing on the creation of a traffic generator specifically designed for the Tofino Switch. Powered by the P4 programmable data plane technology, the PIPO-TG offers the capability to customize and forward packets on the TNA architecture with line-rate packet generation, ensuring accurate performance evaluations without introducing bottlenecks or distortions. With the goal of to develop a traffic generator that can generate realistic and diverse traffic patterns. It incorporates the ability to emulate various network anomalies and behavior patterns. By simulating scenarios such as network congestion, link failures, packet drops, and other disruptive events, PIPO-TG enables researchers to assess the resilience and performance of network systems under realistic and challenging conditions.

![Static Badge](https://img.shields.io/badge/in_progress-unknown-red)


___
<p align="center">
  To keep updated about this project, please don't forget to star ⭐️ the repository.
</p>

___

## Installation

## Usage

## Example
To define the generated traffic, the user needs to write a simple Python script describing the traffic patterns in main.py, we can see a example below.
```pyhton

myTG = PipoGenerator() #instatiante the traffic generator
myTG.addGenerationPort(68) #define the generation port
myTG.addOutputPort(5, 160, "100G") #physical port, port ID(D_P), portBW
myGenerator.addIP(dst = "10.0.0.2") #set IP header with destination address
customHeader = Header(name = "myHeader", size = 8) # create a 8 bits cutom header part 1
customHeader.addField(Field("metadata", 8)) # create a 8 bits cutom header part 1
myTG.addHeader(customHeader) # create a 8 bits cutom header part 3
myTG.addTroughput(100,"meter") #define throughput(Mbps) abd the type(port_shapig or meter)
myTG.generate() #start traffic generation

```

In that example of PIPO-TG input code to generate IP packets at 100 Mbps with destination IP 10.0.0.2 and a custom header to be sent via physical port 5. Additionally, the user defines configuration details such as the pipeline generation port, port bandwidth, and the type of traffic limitation desired.

## Team


