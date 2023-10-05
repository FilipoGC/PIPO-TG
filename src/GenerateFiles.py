#Generate .py file
def generatePy(defaultPort, HWport, throughput_defined, throughput_mode, throughput, obj):
    script = open("files/tableEntries.py", "w")
    
    script.write('#!/usr/bin/env python\n')
    script.write('import sys\n')
    script.write('import os\n')
    script.write('import time\n')
    script.write("sys.path.append(os.path.expandvars('$SDE/install/lib/python3.6/site-packages/tofino/'))\n")
    script.write("sys.path.append(os.path.expandvars('$SDE/install/lib/python3.6/site-packages/'))\n")
    script.write("sys.path.append(os.path.expandvars('$SDE/install/lib/python3.6/site-packages/bf_ptf/'))\n")
    script.write('import grpc\n')
    script.write('import bfrt_grpc.bfruntime_pb2 as bfruntime_pb2\n')
    script.write('import bfrt_grpc.client as gc\n')
    script.write('\n')
                 
    script.write('import ptf.testutils as testutils\n')
    script.write('\n')

    script.write('# Connect to BF Runtime Server\n')
    script.write('interface = gc.ClientInterface(grpc_addr = "localhost:50052",\n')
    script.write('                              client_id = 0,\n')
    script.write('                              device_id = 0)\n')
    script.write("print('Connected to BF Runtime Server')\n")
    script.write('\n')

    script.write('# Get the information about the running program on the bfrt server.\n')
    script.write('bfrt_info = interface.bfrt_info_get()\n')
    script.write("print('The target runs program ', bfrt_info.p4_name_get())\n")
    script.write('\n')

    script.write('# Establish that you are working with this program\n')
    script.write('interface.bind_pipeline_config(bfrt_info.p4_name_get())\n')
    script.write('\n')

    script.write('####### You can now use BFRT CLIENT #######\n')
    script.write('target = gc.Target(device_id=0, pipe_id=0xffff)\n')
    script.write('t_cfg_table = bfrt_info.table_get("$mirror.cfg")\n')
    script.write('t_fwd_table = bfrt_info.table_get("t")\n')

    if throughput_defined and throughput_mode == 'meter':
        script.write('meter = bfrt_info.table_get("meter")\n')

    script.write('\n')

    script.write('# ####### t_table ########\n')
    script.write('print("clean timer table")\n')
    script.write('resp = t_fwd_table.entry_get(target, [], {"from_hw": True})\n')
    script.write('for _, key in resp:\n')
    script.write('  if key:\n')
    script.write('      t_fwd_table.entry_del(target, [key])\n')
    script.write('\n')

    script.write('print("configure timer table")\n')
    script.write(f'i_port = {defaultPort}     # Default port for pktgen\n')
    script.write('pipe_id = 0\n')
    script.write('g_timer_app_id = 1\n')
    script.write('batch_id = [0,1,2,3] # 0,1,2,3\n')
    script.write('packet_id = [0,1] # 0,1\n')
    script.write(f'o_port = {HWport}     # HW port to send the packets\n')
    script.write('\n')


    #meters

    if throughput_defined and throughput_mode == 'meter':

        th = str(int(throughput * 1000))

        script.write('meter_cfg = []\n')

        script.write('meter_cfg.append([0,\n') 
        script.write(f'                  {th},\n') 
        script.write(f'                  {th},\n') 
        script.write('                  1,\n') 
        script.write('                  1])\n')


        script.write('meter.entry_add(\n')
        script.write('          target,\n')
        script.write("          [meter.make_key([gc.KeyTuple('$METER_INDEX', meter_cfg[0][0])])],\n")
        script.write("          [meter.make_data([gc.DataTuple('$METER_SPEC_CIR_KBPS', meter_cfg[0][1]),\n")
        script.write("                            gc.DataTuple('$METER_SPEC_PIR_KBPS', meter_cfg[0][2]),\n")
        script.write("                            gc.DataTuple('$METER_SPEC_CBS_KBITS', meter_cfg[0][3]),\n")
        script.write("                            gc.DataTuple('$METER_SPEC_PBS_KBITS', meter_cfg[0][4])],\n") 
        script.write('                            None)])\n')

    #fimMeters


    #port shaping
    if throughput_defined and throughput_mode == 'port_shaping':
        th = str(int(throughput * 1000))

        script.write('p_shaping = bfrt_info.table_get("tf1.tm.port.sched_cfg")\n')
        script.write('p_shaping2 = bfrt_info.table_get("tf1.tm.port.sched_shaping")\n')
        script.write(f"p_shaping.entry_mod(target, [p_shaping.make_key([gc.KeyTuple('dev_port', {HWport})])], [p_shaping.make_data([gc.DataTuple('max_rate_enable', bool_val=True)])])\n")
        script.write(f"p_shaping2.entry_mod(target, [p_shaping2.make_key([gc.KeyTuple('dev_port', {HWport})])], [p_shaping2.make_data([gc.DataTuple('unit', str_val='BPS'), gc.DataTuple('provisioning', str_val='MIN_ERROR'), gc.DataTuple('max_rate', {th}), gc.DataTuple('max_burst_size', 1000)])])\n")

    script.write('# for i in range(4):\n')
    script.write('#     for j in range(2):\n')
    script.write('t_fwd_table.entry_add(\n')
    script.write(' target,\n')
    script.write("  [t_fwd_table.make_key([ gc.KeyTuple('ig_intr_md.ingress_port', i_port),\n")
    script.write("                      gc.KeyTuple('hdr.timer.pipe_id', pipe_id),\n")
    script.write("                      gc.KeyTuple('hdr.timer.app_id', g_timer_app_id),\n")
    script.write("                      gc.KeyTuple('hdr.timer.batch_id', batch_id[0]),\n")
    script.write("                      gc.KeyTuple('hdr.timer.packet_id', packet_id[0])])],\n")
    script.write("  [t_fwd_table.make_data([gc.DataTuple('port', o_port)],\n")
    script.write("                      'SwitchIngress.match')]\n")
    script.write(')\n')
    script.write('\n')

    script.write('pktgen_app_cfg_table = bfrt_info.table_get("app_cfg")\n')
    script.write('pktgen_pkt_buffer_table = bfrt_info.table_get("pkt_buffer")\n')
    script.write('pktgen_port_cfg_table = bfrt_info.table_get("port_cfg")\n')
    script.write('\n')

    script.write('app_id = g_timer_app_id\n')
    script.write('pktlen = 1024\n')
    script.write('pgen_pipe_id = 0\n')
    script.write('src_port = 68\n')
    script.write('p_count = 1  # packets per batch\n')
    script.write('b_count = 1  # batch number\n')
    script.write("buff_offset = 144  # generated packets' payload will be taken from the offset in buffer\n")
    script.write('\n')

    script.write('# build expected generated packets\n')
    script.write('print("Create packet")\n')

    if obj.IP_defined:
        script.write(f'p = testutils.simple_ip_packet(pktlen={obj.pktLen}, eth_dst="{obj.eth_dst}", eth_src="{obj.eth_src}", dl_vlan_enable={obj.dl_vlan_enable}, vlan_vid={obj.vlan_vid}, vlan_pcp={obj.vlan_pcp}, dl_vlan_cfi={obj.dl_vlan_cfi}, ip_src="{obj.ip_src}", ip_dst="{obj.ip_dst}", ip_tos={obj.ip_tos}, ip_ecn={obj.ip_ecn}, ip_dscp={obj.ip_dscp}, ip_ttl={obj.ip_ttl}, ip_id={obj.ip_id}, ip_ihl={obj.ip_ihl}, ip_options={obj.ip_options}, ip_proto={obj.ip_proto})\n')
    elif obj.eth_defined:
        script.write('p = testutils.simple_eth_packet(pktlen=pktlen)\n')
    script.write('\n')

    script.write('print("enable pktgen port")\n')
    script.write('\n')

    script.write('pktgen_port_cfg_table.entry_add(\n')
    script.write('  target,\n')
    script.write("  [pktgen_port_cfg_table.make_key([gc.KeyTuple('dev_port', src_port)])],\n")
    script.write("  [pktgen_port_cfg_table.make_data([gc.DataTuple('pktgen_enable', bool_val=True)])])\n")
    script.write('\n')

    script.write('# Configure the packet generation timer application\n')
    script.write('print("configure pktgen application")\n')
    script.write("data = pktgen_app_cfg_table.make_data([gc.DataTuple('timer_nanosec', 1),\n")
    script.write("                                gc.DataTuple('app_enable', bool_val=False),\n")
    script.write("                                gc.DataTuple('pkt_len', (pktlen - 6)),\n")
    script.write("                                gc.DataTuple('pkt_buffer_offset', buff_offset),\n")
    script.write("                                gc.DataTuple('pipe_local_source_port', src_port),\n")
    script.write("                                gc.DataTuple('increment_source_port', bool_val=False),\n")
    script.write("                                gc.DataTuple('batch_count_cfg', b_count - 1),\n")
    script.write("                                gc.DataTuple('packets_per_batch_cfg', p_count - 1),\n")
    script.write("                                gc.DataTuple('ibg', 0),\n")
    script.write("                                gc.DataTuple('ibg_jitter', 0),\n")
    script.write("                                gc.DataTuple('ipg', 0),\n")
    script.write("                                gc.DataTuple('ipg_jitter', 0),\n")
    script.write("                                gc.DataTuple('batch_counter', 0),\n")
    script.write("                                gc.DataTuple('pkt_counter', 0),\n")
    script.write("                                gc.DataTuple('trigger_counter', 0)],\n")
    script.write("                                'trigger_timer_periodic')\n")
    script.write("pktgen_app_cfg_table.entry_mod(\n")
    script.write("  target,\n")
    script.write("  [pktgen_app_cfg_table.make_key([gc.KeyTuple('app_id', g_timer_app_id)])],\n")
    script.write("  [data])\n")
    script.write('\n')
    script.write('\n')


    script.write('print("configure packet buffer")\n')
    script.write("pktgen_pkt_buffer_table.entry_mod(\n")
    script.write("  target,\n")
    script.write("  [pktgen_pkt_buffer_table.make_key([gc.KeyTuple('pkt_buffer_offset', buff_offset),\n")
    script.write("                                  gc.KeyTuple('pkt_buffer_size', (pktlen - 6))])],\n")
    script.write("  [pktgen_pkt_buffer_table.make_data([gc.DataTuple('buffer', bytearray(bytes(p)[6:]))])])  # p[6:]))])\n")
    script.write('\n')
    script.write('\n')


    script.write('print("enable pktgen")\n')
    script.write('pktgen_app_cfg_table.entry_mod(\n')
    script.write('  target,\n')
    script.write("  [pktgen_app_cfg_table.make_key([gc.KeyTuple('app_id', g_timer_app_id)])],\n")
    script.write("  [pktgen_app_cfg_table.make_data([gc.DataTuple('app_enable', bool_val=True)],\n")
    script.write("                                  'trigger_timer_periodic')]\n")
    script.write(")\n")
    script.write('\n')
    script.write('\n')


    #script.write("time.sleep(10)\n")
    #script.write('\n')

    # Disable the application.
    #script.write('print("disable pktgen")\n')
    #script.write("pktgen_app_cfg_table.entry_mod(\n")
    #script.write("  target,\n")
    #script.write("  [pktgen_app_cfg_table.make_key([gc.KeyTuple('app_id', g_timer_app_id)])],\n")
    #script.write("  [pktgen_app_cfg_table.make_data([gc.DataTuple('app_enable', bool_val=False)],\n")
    #script.write("                                  'trigger_timer_one_shot')])\n")

    script.close()

#Generate .p4 file
def generateP4(throughput_defined, throughput_mode, full_obj):

    filep4 = open("files/pipoTG.p4", "w")
    
    filep4.write('/*******************************************************************************\n')
    filep4.write('* BAREFOOT NETWORKS CONFIDENTIAL & PROPRIETARY\n')
    filep4.write('*\n')
    filep4.write('* Copyright (c) 2019-present Barefoot Networks, Inc.\n')
    filep4.write('*\n')
    filep4.write('* All Rights Reserved.\n')
    filep4.write('*\n')
    filep4.write('* NOTICE: All information contained herein is, and remains the property of\n')
    filep4.write('* Barefoot Networks, Inc. and its suppliers, if any. The intellectual and\n')
    filep4.write('* technical concepts contained herein are proprietary to Barefoot Networks, Inc.\n')
    filep4.write('* and its suppliers and may be covered by U.S. and Foreign Patents, patents in\n')
    filep4.write('* process, and are protected by trade secret or copyright law.  Dissemination of\n')
    filep4.write('* this information or reproduction of this material is strictly forbidden unless\n')
    filep4.write('* prior written permission is obtained from Barefoot Networks, Inc.\n')
    filep4.write('*\n')
    filep4.write('* No warranty, explicit or implicit is provided, unless granted under a written\n')
    filep4.write('* agreement with Barefoot Networks, Inc.\n')
    filep4.write('*\n')
    filep4.write('******************************************************************************/\n')
    filep4.write('\n')

    filep4.write('#if __TARGET_TOFINO__ == 2\n')
    filep4.write('#include <t2na.p4>\n')
    filep4.write('#else\n')
    filep4.write('#include <tna.p4>\n')
    filep4.write('#endif\n')
    filep4.write('\n')

    filep4.write('#include "headers.p4"\n')
    filep4.write('#include "util.p4"\n')
    filep4.write('\n')
    filep4.write('\n')


    filep4.write('struct headers {\n')
    filep4.write('  pktgen_timer_header_t     timer;\n')
    filep4.write('  pktgen_port_down_header_t port_down;\n')
    if full_obj.eth_defined or full_obj.IP_defined or full_obj.tcp_defined or full_obj.udp_defined:
        filep4.write('  ethernet_h    ethernet;\n')
        filep4.write('  ipv4_h        ipv4;\n')
        filep4.write('  tcp_h         tcp;\n')
        filep4.write('  udp_h         udp;\n')
    for hd in full_obj.headers:
        filep4.write(f'  {hd.name}_h    {hd.name};\n')
    filep4.write('}\n')
    filep4.write('\n')

    filep4.write('parser SwitchIngressParser(\n')
    filep4.write('  packet_in packet, \n')
    filep4.write('  out headers hdr, \n')
    filep4.write('  out empty_metadata_t md, \n')
    filep4.write('  out ingress_intrinsic_metadata_t ig_intr_md) {\n')
    filep4.write('\n')

    filep4.write('  state start {\n')
    filep4.write('      packet.extract(ig_intr_md);\n')
    filep4.write('      packet.advance(PORT_METADATA_SIZE);\n')
    filep4.write('\n')

    filep4.write('      pktgen_port_down_header_t pktgen_pd_hdr = packet.lookahead<pktgen_port_down_header_t>();\n')
    filep4.write('      transition select(pktgen_pd_hdr.app_id) {\n')
    filep4.write('          1 : parse_pktgen_timer;\n')
    filep4.write('          2 : parse_pktgen_timer;\n')
    filep4.write('          3 : parse_pktgen_port_down;\n')
    filep4.write('          4 : parse_pktgen_port_down;\n')
    filep4.write('          default : reject;\n')
    filep4.write(       '}\n')
    filep4.write('  }\n')
    filep4.write('\n')

    filep4.write('  state parse_pktgen_timer {\n')
    filep4.write('      packet.extract(hdr.timer);\n')
    if full_obj.eth_defined or full_obj.IP_defined or full_obj.tcp_defined or full_obj.udp_defined:
        filep4.write('      transition parse_ethernet;\n')
    else:
        filep4.write('      transition accept;\n')
    filep4.write('  }\n')
    filep4.write('\n')


    #state to parse eth
    if full_obj.eth_defined or full_obj.IP_defined or full_obj.tcp_defined or full_obj.udp_defined:
        filep4.write('  state parse_ethernet {\n')
        filep4.write('      packet.extract(hdr.ethernet);\n')
        filep4.write('      transition select(hdr.ethernet.ether_type) {\n')
        filep4.write('          ETHERTYPE_IPV4:    parse_ipv4;\n')
        filep4.write('          default:           accept;\n')
        filep4.write('      }\n')
        filep4.write('  }\n')


    if full_obj.eth_defined or full_obj.IP_defined or full_obj.tcp_defined or full_obj.udp_defined:
        filep4.write('  state parse_ipv4 {\n')
        filep4.write('      packet.extract(hdr.ipv4);\n')
        filep4.write('      transition select(hdr.ipv4.protocol) {\n')
        filep4.write('          IP_PROTOCOLS_UDP:    parse_udp;\n')
        filep4.write('          IP_PROTOCOLS_TCP:    parse_tcp;\n')
        filep4.write('          default:             accept;\n')
        filep4.write('      }\n')
        filep4.write('  }\n')

    if full_obj.eth_defined or full_obj.IP_defined or full_obj.tcp_defined or full_obj.udp_defined:
        filep4.write('  state parse_tcp {\n')
        filep4.write('      packet.extract(hdr.tcp);\n')
        filep4.write('      transition accept;\n')
        filep4.write('  }\n')

    if full_obj.eth_defined or full_obj.IP_defined or full_obj.tcp_defined or full_obj.udp_defined:
        filep4.write('  state parse_udp {\n')
        filep4.write('      packet.extract(hdr.udp);\n')
        filep4.write('      transition accept;\n')
        filep4.write('  }\n')

        

    filep4.write('  state parse_pktgen_port_down {\n')
    filep4.write('      packet.extract(hdr.port_down);\n')
    filep4.write('      transition accept;\n')
    filep4.write('  }\n')
    filep4.write('}\n')
    filep4.write('\n')
    filep4.write('\n')


    filep4.write('control SwitchIngressDeparser(\n')
    filep4.write('      packet_out pkt,\n')
    filep4.write('      inout headers hdr,\n')
    filep4.write('      in empty_metadata_t ig_md,\n')
    filep4.write('      in ingress_intrinsic_metadata_for_deparser_t ig_intr_dprsr_md) {\n')
    filep4.write('\n')

    filep4.write('  apply {\n')
    filep4.write('      pkt.emit(hdr);\n')
    filep4.write('  }\n')
    filep4.write('}\n')
    filep4.write('\n')
    filep4.write('\n')


    filep4.write('control SwitchIngress(\n')
    filep4.write('      inout headers hdr, \n')
    filep4.write('      inout empty_metadata_t md,\n')
    filep4.write('      in ingress_intrinsic_metadata_t ig_intr_md,\n')
    filep4.write('      in ingress_intrinsic_metadata_from_parser_t ig_intr_prsr_md,\n')
    filep4.write('      inout ingress_intrinsic_metadata_for_deparser_t ig_intr_dprsr_md,\n')
    filep4.write('      inout ingress_intrinsic_metadata_for_tm_t ig_intr_tm_md) {\n')
    filep4.write('\n')

    #meter
    if throughput_defined and throughput_mode == 'meter':
        filep4.write('  Meter<bit<10>>(10, MeterType_t.BYTES) meter;\n')
        filep4.write('  bit<2> color = 0;\n\n')

    filep4.write('  action drop() {\n')
    filep4.write('      ig_intr_dprsr_md.drop_ctl = 0x1;\n')
    filep4.write('  }\n')
    filep4.write('\n')

    filep4.write('  action match(PortId_t port) {\n')
    filep4.write('      ig_intr_tm_md.ucast_egress_port = port;\n')
    filep4.write('      ig_intr_tm_md.bypass_egress = 1w1;\n')
    filep4.write('  }\n')
    filep4.write('\n')

    filep4.write('  table t {\n')
    filep4.write('      key = {\n')
    filep4.write('          hdr.timer.pipe_id : exact;\n')
    filep4.write('          hdr.timer.app_id  : exact;\n')
    filep4.write('          hdr.timer.batch_id : exact;\n')
    filep4.write('          hdr.timer.packet_id : exact;\n')
    filep4.write('          ig_intr_md.ingress_port : exact;\n')
    filep4.write('      }\n')
    filep4.write('      actions = {\n')
    filep4.write('          match;\n')
    filep4.write('          @defaultonly drop;\n')
    filep4.write('      }\n')
    filep4.write('      const default_action = drop();\n')
    filep4.write('      size = 1024;\n')
    filep4.write('  }\n')
    filep4.write('  table p {\n')
    filep4.write('      key = {\n')
    filep4.write('          hdr.port_down.pipe_id   : exact;\n')
    filep4.write('          hdr.port_down.app_id    : exact;\n')
    filep4.write('          hdr.port_down.port_num  : exact;\n')
    filep4.write('          hdr.port_down.packet_id : exact;\n')
    filep4.write('          ig_intr_md.ingress_port : exact;\n')
    filep4.write('      }\n')
    filep4.write('      actions = {\n')
    filep4.write('          match;\n')
    filep4.write('          @defaultonly drop;\n')
    filep4.write('      }\n')
    filep4.write('      const default_action = drop();\n')
    filep4.write('      size = 1024;\n')
    filep4.write('  }\n')
    filep4.write('\n')

    filep4.write('  apply {\n')


    for hd in full_obj.headers:
        filep4.write(f'      hdr.{hd.name}.setValid();\n')

    filep4.write('      if (hdr.timer.isValid()) {\n')
    filep4.write('          t.apply();\n')
    filep4.write('      } else if (hdr.port_down.isValid()) {\n')
    filep4.write('          p.apply();\n')
    filep4.write('      } else {\n')
    filep4.write('          drop();\n')
    filep4.write('      }\n')
    filep4.write('\n')

    #meters
    if throughput_defined and throughput_mode == 'meter': 
        filep4.write('      if (hdr.timer.isValid()) {\n')   
        filep4.write('          color = (bit<2>) meter.execute(0);\n')
        filep4.write('          if (color >= 3) {\n')
        filep4.write('                drop();\n')
        filep4.write('          }\n')
        filep4.write('      }\n')

    #fim meters

    filep4.write('      // No need for egress processing, skip it and use empty controls for egress.\n')
    filep4.write('      ig_intr_tm_md.bypass_egress = 1w1;\n')
    filep4.write('  }\n')
    filep4.write('}\n')
    filep4.write('\n')
    filep4.write('\n')


    filep4.write('Pipeline(SwitchIngressParser(),\n')
    filep4.write('      SwitchIngress(),\n')
    filep4.write('      SwitchIngressDeparser(),\n')
    filep4.write('      EmptyEgressParser(),\n')
    filep4.write('      EmptyEgress(),\n')
    filep4.write('      EmptyEgressDeparser()) pipe;\n')
    filep4.write('\n')

    filep4.write('Switch(pipe) main;\n')
    filep4.write('\n')

    filep4.close()

#Generate Headers
def generateHeader(header_list, eth_defined, IP_defined, udp_defined, tcp_defined):
    headers = open("files/headers.p4", "w")
    
    headers.write('/*******************************************************************************\n')
    headers.write('* BAREFOOT NETWORKS CONFIDENTIAL & PROPRIETARY\n')
    headers.write('*\n')
    headers.write('* Copyright (c) 2019-present Barefoot Networks, Inc.\n')
    headers.write('*\n')
    headers.write('* All Rights Reserved.\n')
    headers.write('*\n')
    headers.write('* NOTICE: All information contained herein is, and remains the property of\n')
    headers.write('* Barefoot Networks, Inc. and its suppliers, if any. The intellectual and\n')
    headers.write('* technical concepts contained herein are proprietary to Barefoot Networks, Inc.\n')
    headers.write('* and its suppliers and may be covered by U.S. and Foreign Patents, patents in\n')
    headers.write('* process, and are protected by trade secret or copyright law.  Dissemination of\n')
    headers.write('* this information or reproduction of this material is strictly forbidden unless\n')
    headers.write('* prior written permission is obtained from Barefoot Networks, Inc.\n')
    headers.write('*\n')
    headers.write('* No warranty, explicit or implicit is provided, unless granted under a written\n')
    headers.write('* agreement with Barefoot Networks, Inc.\n')
    headers.write('*\n')
    headers.write('******************************************************************************/\n')
    headers.write('\n')

    headers.write('#ifndef _HEADERS_\n')
    headers.write('#define _HEADERS_\n')
    headers.write('\n')

    headers.write('typedef bit<48> mac_addr_t;\n')
    headers.write('typedef bit<32> ipv4_addr_t;\n')
    headers.write('typedef bit<128> ipv6_addr_t;\n')
    headers.write('typedef bit<12> vlan_id_t;\n')
    headers.write('\n')

    headers.write('typedef bit<16> ether_type_t;\n')
    headers.write('const ether_type_t ETHERTYPE_IPV4 = 16w0x0800;\n')
    headers.write('const ether_type_t ETHERTYPE_ARP = 16w0x0806;\n')
    headers.write('const ether_type_t ETHERTYPE_IPV6 = 16w0x86dd;\n')
    headers.write('const ether_type_t ETHERTYPE_VLAN = 16w0x8100;\n')
    headers.write('\n')

    headers.write('typedef bit<8> ip_protocol_t;\n')
    headers.write('const ip_protocol_t IP_PROTOCOLS_ICMP = 1;\n')
    headers.write('const ip_protocol_t IP_PROTOCOLS_TCP = 6;\n')
    headers.write('const ip_protocol_t IP_PROTOCOLS_UDP = 17;\n')
    headers.write('\n')


    if eth_defined or IP_defined or tcp_defined or udp_defined:
        headers.write('header ethernet_h {\n')
        headers.write(' mac_addr_t dst_addr;\n')
        headers.write(' mac_addr_t src_addr;\n')
        headers.write(' bit<16> ether_type;\n')
        headers.write('}\n')
        headers.write('\n')


    headers.write('header vlan_tag_h {\n')
    headers.write(' bit<3> pcp;\n')
    headers.write(' bit<1> cfi;\n')
    headers.write(' vlan_id_t vid;\n')
    headers.write(' bit<16> ether_type;\n')
    headers.write('}\n')
    headers.write('\n')

    headers.write('header mpls_h {\n')
    headers.write(' bit<20> label;\n')
    headers.write(' bit<3> exp;\n')
    headers.write(' bit<1> bos;\n')
    headers.write(' bit<8> ttl;\n')
    headers.write('}\n')
    headers.write('\n')


    if eth_defined or IP_defined or tcp_defined or udp_defined:
        headers.write('header ipv4_h {\n')
        headers.write(' bit<4> version;\n')
        headers.write(' bit<4> ihl;\n')
        headers.write(' bit<8> diffserv;\n')
        headers.write(' bit<16> total_len;\n')
        headers.write(' bit<16> identification;\n')
        headers.write(' bit<3> flags;\n')
        headers.write(' bit<13> frag_offset;\n')
        headers.write(' bit<8> ttl;\n')
        headers.write(' bit<8> protocol;\n')
        headers.write(' bit<16> hdr_checksum;\n')
        headers.write(' ipv4_addr_t src_addr;\n')
        headers.write(' ipv4_addr_t dst_addr;\n')
        headers.write('}\n')
        headers.write('\n')

    headers.write('header ipv6_h {\n')
    headers.write(' bit<4> version;\n')
    headers.write(' bit<8> traffic_class;\n')
    headers.write(' bit<20> flow_label;\n')
    headers.write(' bit<16> payload_len;\n')
    headers.write(' bit<8> next_hdr;\n')
    headers.write(' bit<8> hop_limit;\n')
    headers.write(' ipv6_addr_t src_addr;\n')
    headers.write(' ipv6_addr_t dst_addr;\n')
    headers.write('}\n')
    headers.write('\n')


    if eth_defined or IP_defined or tcp_defined or udp_defined:
        headers.write('header tcp_h {\n')
        headers.write(' bit<16> src_port;\n')
        headers.write(' bit<16> dst_port;\n')
        headers.write(' bit<32> seq_no;\n')
        headers.write(' bit<32> ack_no;\n')
        headers.write(' bit<4> data_offset;\n')
        headers.write(' bit<4> res;\n')
        headers.write(' bit<8> flags;\n')
        headers.write(' bit<16> window;\n')
        headers.write(' bit<16> checksum;\n')
        headers.write(' bit<16> urgent_ptr;\n')
        headers.write('}\n')
        headers.write('\n')

    if eth_defined or IP_defined or tcp_defined or udp_defined:
        headers.write('header udp_h {\n')
        headers.write(' bit<16> src_port;\n')
        headers.write(' bit<16> dst_port;\n')
        headers.write(' bit<16> hdr_length;\n')
        headers.write(' bit<16> checksum;\n')
        headers.write('}\n')
        headers.write('\n')

    headers.write('header icmp_h {\n')
    headers.write(' bit<8> type_;\n')
    headers.write(' bit<8> code;\n')
    headers.write(' bit<16> hdr_checksum;\n')
    headers.write('}\n')
    headers.write('\n')

    headers.write('// Address Resolution Protocol -- RFC 6747\n')
    headers.write('header arp_h {\n')
    headers.write(' bit<16> hw_type;\n')
    headers.write(' bit<16> proto_type;\n')
    headers.write(' bit<8> hw_addr_len;\n')
    headers.write(' bit<8> proto_addr_len;\n')
    headers.write(' bit<16> opcode;\n')
    headers.write(' // ...\n')
    headers.write('}\n')
    headers.write('\n')

    headers.write('// Segment Routing Extension (SRH) -- IETFv7\n')
    headers.write('header ipv6_srh_h {\n')
    headers.write(' bit<8> next_hdr;\n')
    headers.write(' bit<8> hdr_ext_len;\n')
    headers.write(' bit<8> routing_type;\n')
    headers.write(' bit<8> seg_left;\n')
    headers.write(' bit<8> last_entry;\n')
    headers.write(' bit<8> flags;\n')
    headers.write(' bit<16> tag;\n')
    headers.write('}\n')
    headers.write('\n')

    headers.write('// VXLAN -- RFC 7348\n')
    headers.write('header vxlan_h {\n')
    headers.write(' bit<8> flags;\n')
    headers.write(' bit<24> reserved;\n')
    headers.write(' bit<24> vni;\n')
    headers.write(' bit<8> reserved2;\n')
    headers.write('}\n')
    headers.write('\n')

    headers.write('// Generic Routing Encapsulation (GRE) -- RFC 1701\n')
    headers.write('header gre_h {\n')
    headers.write(' bit<1> C;\n')
    headers.write(' bit<1> R;\n')
    headers.write(' bit<1> K;\n')
    headers.write(' bit<1> S;\n')
    headers.write(' bit<1> s;\n')
    headers.write(' bit<3> recurse;\n')
    headers.write(' bit<5> flags;\n')
    headers.write(' bit<3> version;\n')
    headers.write(' bit<16> proto;\n')
    headers.write('}\n')
    headers.write('\n')

    headers.write('// Customized headers (if exist)\n')
    for hdr in header_list:
        headers.write(f'\nheader {hdr.name}_h {{\n')
        for field in hdr.fields:
            headers.write(f'\tbit<{field.size}> {field.name};\n')
        headers.write('}\n')




    headers.write(' // Add more headers here.\n')
    headers.write('\n')

    headers.write('struct empty_header_t {}\n')
    headers.write('\n')

    headers.write('struct empty_metadata_t {}\n')
    headers.write('\n')

    headers.write('#endif /* _HEADERS_ */\n')
    headers.write('\n')

#Generate Contants
def generateUtil():
    util = open("files/util.p4", "w")

    util.write('/*******************************************************************************\n')
    util.write('* BAREFOOT NETWORKS CONFIDENTIAL & PROPRIETARY\n')
    util.write('*\n')
    util.write('* Copyright (c) 2019-present Barefoot Networks, Inc.\n')
    util.write('*\n')
    util.write('* All Rights Reserved.\n')
    util.write('*\n')
    util.write('* NOTICE: All information contained herein is, and remains the property of\n')
    util.write('* Barefoot Networks, Inc. and its suppliers, if any. The intellectual and\n')
    util.write('* technical concepts contained herein are proprietary to Barefoot Networks, Inc.\n')
    util.write('* and its suppliers and may be covered by U.S. and Foreign Patents, patents in\n')
    util.write('* process, and are protected by trade secret or copyright law.  Dissemination of\n')
    util.write('* this information or reproduction of this material is strictly forbidden unless\n')
    util.write('* prior written permission is obtained from Barefoot Networks, Inc.\n')
    util.write('*\n')
    util.write('* No warranty, explicit or implicit is provided, unless granted under a written\n')
    util.write('* agreement with Barefoot Networks, Inc.\n')
    util.write('*\n')
    util.write('******************************************************************************/\n')
    util.write('\n')

    util.write('#ifndef _UTIL_\n')
    util.write('#define _UTIL_\n')
    util.write('\n')

    util.write('parser TofinoIngressParser(\n')
    util.write('        packet_in pkt,\n')
    util.write('        out ingress_intrinsic_metadata_t ig_intr_md) {\n')
    util.write('    state start {\n')
    util.write('        pkt.extract(ig_intr_md);\n')
    util.write('        transition select(ig_intr_md.resubmit_flag) {\n')
    util.write('            1 : parse_resubmit;\n')
    util.write('            0 : parse_port_metadata;\n')
    util.write('        }\n')
    util.write('    }\n')
    util.write('\n')

    util.write('    state parse_resubmit {\n')
    util.write('        // Parse resubmitted packet here.\n')
    util.write('        transition reject;\n')
    util.write('    }\n')
    util.write('\n')

    util.write('    state parse_port_metadata {\n')
    util.write('        pkt.advance(PORT_METADATA_SIZE);\n')
    util.write('        transition accept;\n')
    util.write('    }\n')
    util.write('}\n')
    util.write('\n')

    util.write('parser TofinoEgressParser(\n')
    util.write('        packet_in pkt,\n')
    util.write('        out egress_intrinsic_metadata_t eg_intr_md) {\n')
    util.write('    state start {\n')
    util.write('        pkt.extract(eg_intr_md);\n')
    util.write('        transition accept;\n')
    util.write('    }\n')
    util.write('}\n')
    util.write('\n')

    util.write('// Skip egress\n')
    util.write('control BypassEgress(inout ingress_intrinsic_metadata_for_tm_t ig_tm_md) {\n')
    util.write('\n')

    util.write('    action set_bypass_egress() {\n')
    util.write('        ig_tm_md.bypass_egress = 1w1;\n')
    util.write('    }\n')
    util.write('    table bypass_egress {\n')
    util.write('        actions = {\n')
    util.write('            set_bypass_egress();\n')
    util.write('        }\n')
    util.write('        const default_action = set_bypass_egress;\n')
    util.write('    }\n')
    util.write('\n')

    util.write('    apply {\n')
    util.write('        bypass_egress.apply();\n')
    util.write('    }\n')
    util.write('}\n')
    util.write('\n')

    util.write('// Empty egress parser/control blocks\n')
    util.write('parser EmptyEgressParser(\n')
    util.write('        packet_in pkt,\n')
    util.write('        out empty_header_t hdr,\n')
    util.write('        out empty_metadata_t eg_md,\n')
    util.write('        out egress_intrinsic_metadata_t eg_intr_md) {\n')
    util.write('    state start {\n')
    util.write('        transition accept;\n')
    util.write('    }\n')
    util.write('}\n')
    util.write('\n')

    util.write('control EmptyEgressDeparser(\n')
    util.write('        packet_out pkt,\n')
    util.write('        inout empty_header_t hdr,\n')
    util.write('        in empty_metadata_t eg_md,\n')
    util.write('        in egress_intrinsic_metadata_for_deparser_t ig_intr_dprs_md) {\n')
    util.write('    apply {}\n')
    util.write('}\n')
    util.write('\n')

    util.write('control EmptyEgress(\n')
    util.write('        inout empty_header_t hdr,\n')
    util.write('        inout empty_metadata_t eg_md,\n')
    util.write('        in egress_intrinsic_metadata_t eg_intr_md,\n')
    util.write('        in egress_intrinsic_metadata_from_parser_t eg_intr_md_from_prsr,\n')
    util.write('        inout egress_intrinsic_metadata_for_deparser_t ig_intr_dprs_md,\n')
    util.write('        inout egress_intrinsic_metadata_for_output_port_t eg_intr_oport_md) {\n')
    util.write('    apply {}\n')
    util.write('}\n')
    util.write('\n')

    util.write('#endif /* _UTIL */\n')


#Generate Contants
def generatePortConfig(port, port_bw):
    ports = open("files/portConfig.txt", "w")

    ports.write('ucli\n')
    ports.write('pm\n')
    ports.write(f'port-add {port}/- {port_bw} NONE\n')
    ports.write(f'port-enb {port}/-\n')
    ports.write(f'an-set {port}/- 2 \n')
    ports.write(f'port-dis {port}/-\n')
    ports.write(f'port-enb {port}/-\n')
    ports.write('show\n')
    ports.write('exit\n')
    ports.write('exit\n')
