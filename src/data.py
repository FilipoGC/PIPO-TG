import sys

from src.GenerateFiles import (
    generateRunPy,
    generateP4,
    generateHeader,
    generateUtil,
    generatePortConfig,
    generateExec,
)
from src.headers import Header

class Flow:
    def __init__(self, flow_id: int):
        self.id = int(flow_id)

        self.out_port = None
        self.out_dev_port = None
        self.out_bw = None

        self.pktLen = 64
        self.eth_dst = '00:01:02:03:04:05'
        self.eth_src = '00:06:07:08:09:0a'
        self.ether_type = 0x0800

        self.ip_src = '192.168.0.1'
        self.ip_dst = '192.168.0.2'
        self.ip_tos = 0
        self.ip_ttl = 64
        self.ip_id = 0x0001
        self.ip_ihl = 0
        self.ip_proto = 0

        self.ip_src_random = False
        self.ip_src_mask = '/24'

        self.throughput_defined = False
        self.throughput = 0
        self.throughput_pattern = None
        self.throughput_pattern_sec = None
        self.duration_sec = None

    def outputPort(self, port, dev_port: int, bw: str = None):
        self.out_port = str(port)
        self.out_dev_port = int(dev_port)
        self.out_bw = None if bw is None else str(bw)

    def addIP(
        self,
        pktlen: int = 64,
        eth_dst: str = '00:01:02:03:04:05',
        eth_src: str = '00:06:07:08:09:0a',
        ip_src: str = '192.168.0.1',
        ip_dst: str = '192.168.0.2',
        ip_tos: int = 0,
        ip_ttl: int = 64,
        ip_id: int = 0x0001,
        ip_ihl=None,
        ip_proto: int = 0,
        ether_type: int = 0x0800,
        srcRandom: bool = False,
        srcMask: str = '/24',
        #**_ignored,
    ):
        self.pktLen = int(pktlen)
        self.eth_dst = str(eth_dst)
        self.eth_src = str(eth_src)
        self.ether_type = int(ether_type)

        self.ip_src = str(ip_src)
        self.ip_dst = str(ip_dst)
        self.ip_tos = int(ip_tos)
        self.ip_ttl = int(ip_ttl)
        self.ip_id = int(ip_id)
        self.ip_proto = int(ip_proto)

        if ip_ihl is None:
            self.ip_ihl = 0
        else:
            try:
                self.ip_ihl = int(ip_ihl)
            except Exception:
                self.ip_ihl = 0

        self.ip_src_random = bool(srcRandom)
        self.ip_src_mask = str(srcMask)

    def addThroughput(self, throughput, durations=None):
        self.throughput_defined = True

        if durations is not None:
            self.throughput = list(throughput)
            self.throughput_pattern = list(throughput)
            self.throughput_pattern_sec = list(durations)
            return

        self.throughput = throughput
        self.throughput_pattern = None
        self.throughput_pattern_sec = None

    def addDuration(self, duration_sec: float):
        self.duration_sec = float(duration_sec)


class Generator:
    def __init__(self, name: str = 'pipo'):
        self.name = str(name)
        self.generation_port = 68
        self.throughput_mode = 'meter'
        self.graph_enabled = False
        self.headers = []
        self.flows = []

    def addGenerationPort(self, port: int):
        self.generation_port = int(port)


    #isso aqui ta meio atoa
    def setThroughputMode(self, mode: str):
        self.throughput_mode = mode

    def enableGraph(self):
        self.graph_enabled = True

    def addHeader(self, header):
        if isinstance(header, Header):
            self.headers.append(header)
            return
        if isinstance(header, list) and all(isinstance(item, Header) for item in header):
            self.headers.extend(header)
            return
        print('ERROR! The header is invalid!')
        sys.exit(1)

    def addFlow(self) -> Flow:
        flow = Flow(flow_id=len(self.flows))
        self.flows.append(flow)
        return flow

    def printSummary(self):
        print('\n================ PIPO-TG CONFIGURATION ================')
        print(f'Generation port: {self.generation_port}')
        print(f'Throughput mode: {self.throughput_mode}')
        print(f"Graph: {'enabled' if self.graph_enabled else 'disabled'}")
        print(f'Flows: {len(self.flows)}')

        for flow in self.flows:
            random_src = ''
            if flow.ip_src_random:
                random_src = f' random(srcMask={flow.ip_src_mask})'

            out = '(not set)'
            if flow.out_port is not None and flow.out_dev_port is not None:
                bw = f', bw={flow.out_bw}' if flow.out_bw else ''
                out = f'{flow.out_port} (dev_port={flow.out_dev_port}{bw})'

            if flow.throughput_pattern is not None and flow.throughput_pattern_sec is not None:
                parts = []
                for rate, sec in zip(flow.throughput_pattern, flow.throughput_pattern_sec):
                    parts.append(f'{rate}Mbps/{sec}s')
                throughput = 'variance [' + ', '.join(parts) + ']'
            else:
                throughput = f'{flow.throughput} Mbps'

            duration = 'INF' if flow.duration_sec is None else f'{flow.duration_sec}s'
            print(
                f'  - flow{flow.id}: out={out} len={flow.pktLen} '
                f'src={flow.ip_src} dst={flow.ip_dst}{random_src} '
                f'tos={flow.ip_tos} ttl={flow.ip_ttl} id={hex(flow.ip_id)} proto={flow.ip_proto}\n'
                f'      throughput={throughput} duration={duration}\n'
            )

        print('=======================================================\n')

    def generate(self):
        if not self.flows:
            raise ValueError('Configure at least one flow before calling generate().')

        pktlens = {int(flow.pktLen) for flow in self.flows}
        if len(pktlens) > 1:
            raise ValueError(
                'Current version requires a single pktLen for all flows. '
                f'Found: {sorted(pktlens)}'
            )

        ports = []
        seen = set()
        for flow in self.flows:
            if flow.out_port is None:
                continue
            key = (str(flow.out_port), str(flow.out_bw) if flow.out_bw else '10G')
            if key in seen:
                continue
            seen.add(key)
            ports.append(key)

        if not ports:
            raise ValueError('Each flow must define an outputPort(port, dev_port, bw).')

        generateRunPy(self)
        generateP4(self)
        generateHeader(self.headers)
        generateUtil()
        generatePortConfig(ports)
        generateExec(self.graph_enabled)
        self.printSummary()
