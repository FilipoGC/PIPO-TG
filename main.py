from src.data import Generator
from src.headers import Field, Header

tg = Generator()

tg.addGenerationPort(68)
tg.setThroughputMode("meter")
tg.enableGraph()  # opcional

# -------------------------------------------------------
# Header custom
# -------------------------------------------------------
myhdr = Header(name="myhdr", size=16)
myhdr.addField(
    [
        Field("msg_type", 8, default_value=1),
        Field("flags", 4, default_value=0),
        Field("reserved", 4, default_value=0),
    ]
)

tg.addHeader(myhdr)

# --------------------------
# Flow 0 (simple) TX seted in 10 Gbps
# --------------------------
f0 = tg.addFlow()
f0.outputPort("10/-", 52, "100G")
f0.addIP(
    pktlen=1024,
    eth_dst="00:01:02:03:04:05",
    eth_src="00:06:07:08:09:0a",
    ether_type=0x0800,
    ip_src="192.168.0.1",
    ip_dst="192.168.0.2",
    ip_tos=0,
    ip_ttl=64,
    ip_id=0x0001,
    ip_ihl=None,
    ip_proto=0,
    srcRandom=False,
    srcMask="/24",
)
f0.addThroughput(10000)  # Mbps
# f0.addDuration()

# --------------------------
# Flow 1 (simple) TX seted in 5 Gbps
# --------------------------
f1 = tg.addFlow()
f1.outputPort("10/-", 52, "100G")
f1.addIP(
    pktlen=1024,
    eth_dst="00:01:02:03:04:10",
    eth_src="00:06:07:08:09:20",
    ether_type=0x0800,
    ip_src="192.168.0.10",
    ip_dst="192.168.0.20",
    ip_tos=0,
    ip_ttl=64,
    ip_id=0x0001,
    ip_ihl=None,
    ip_proto=0,
    srcRandom=False,
    srcMask="/24",
)
f1.addThroughput(5000)  # Mbps

# --------------------------
# Flow 2 (burst simulation) TX with variance, 5 seconds in 0.5 Gbps and 2 seconds in 50 Gbps
# --------------------------
f2 = tg.addFlow()
f2.outputPort("10/-", 52, "100G")
f2.addIP(
   pktlen=1024,
   ip_src="10.0.0.1",
   ip_dst="10.0.0.2",
   srcRandom=False,
   srcMask="/16",
)
# f2.addThroughput(1000)
f2.addThroughput([500, 50000], [5, 2])  # variance: 500Mbps/5s, 1500Mbps/2s
f2.addDuration(60)


# --------------------------
# Flow 3 (DDos simulation) TX of 20 Gbps with random src ip
# --------------------------
f3 = tg.addFlow()
f3.outputPort("10/-", 52, "100G")
f3.addIP(
   pktlen=1024,
   ip_dst="10.0.0.2",
   ip_src="10.0.0.1",
   srcRandom=True,
   srcMask="/16",
)
f3.addThroughput(20000)
f3.addDuration(60)

tg.generate()
