def _flows_from_obj(obj):
    flows = getattr(obj, 'flows', None)
    if not flows:
        return [obj]
    return flows

def _mask_prefix(mask_str: str) -> int:
    import ipaddress

    value = str(mask_str).strip()
    if value.startswith('/'):
        value = value[1:].strip()

    if value.isdigit():
        prefix = int(value)
        if prefix < 0 or prefix > 32:
            raise ValueError(f'Invalid prefix length: {prefix}')
        return prefix

    if '.' in value:
        try:
            return int(ipaddress.IPv4Network('0.0.0.0/' + value).prefixlen)
        except Exception as exc:
            raise ValueError(f'Invalid srcMask netmask: {mask_str}') from exc

    raise ValueError(f'Invalid srcMask: {mask_str}')

def _idx_width(n: int) -> int:
    return max(1, (int(n) - 1).bit_length())

def generateHeader(header_list):
    headers = open('files/headers.p4', 'w')

    headers.write('#ifndef _HEADERS_\n')
    headers.write('#define _HEADERS_\n\n')
    headers.write('typedef bit<48> mac_addr_t;\n')
    headers.write('typedef bit<32> ipv4_addr_t;\n')
    headers.write('typedef bit<12> vlan_id_t;\n\n')
    headers.write('typedef bit<16> ether_type_t;\n')
    headers.write('const ether_type_t ETHERTYPE_IPV4 = 16w0x0800;\n')
    headers.write('const ether_type_t ETHERTYPE_VLAN = 16w0x8100;\n\n')

    headers.write('typedef bit<8> ip_protocol_t;\n')
    headers.write('const ip_protocol_t IP_PROTOCOLS_TCP = 6;\n')
    headers.write('const ip_protocol_t IP_PROTOCOLS_UDP = 17;\n\n')

    headers.write('header ethernet_h {\n')
    headers.write(' mac_addr_t dst_addr;\n')
    headers.write(' mac_addr_t src_addr;\n')
    headers.write(' bit<16> ether_type;\n')
    headers.write('}\n\n')

    headers.write('header vlan_tag_h {\n')
    headers.write(' bit<3> pcp;\n')
    headers.write(' bit<1> cfi;\n')
    headers.write(' vlan_id_t vid;\n')
    headers.write(' bit<16> ether_type;\n')
    headers.write('}\n\n')

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
    headers.write('}\n\n')
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
    headers.write('}\n\n')

    headers.write('header udp_h {\n')
    headers.write(' bit<16> src_port;\n')
    headers.write(' bit<16> dst_port;\n')
    headers.write(' bit<16> hdr_length;\n')
    headers.write(' bit<16> checksum;\n')
    headers.write('}\n\n')

    for hdr in header_list:
        headers.write(f'header {hdr.name}_h {{\n')
        for field in hdr.fields:
            headers.write(f'    bit<{field.size}> {field.name};\n')
        headers.write('}\n\n')

    headers.write('struct empty_header_t {}\n\n')
    headers.write('struct empty_metadata_t {\n')
    headers.write('    bit<1> srcRandom;\n')
    headers.write('    bit<8> srcPrefix;\n')
    headers.write('}\n\n')
    headers.write('#endif /* _HEADERS_ */\n')

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

def generateExec(graph_enabled):
    script = open("execut.sh", "w")

    script.write("#!/bin/bash\n\n")
    script.write("killall bf_switchd 2>/dev/null\n")
    script.write("killall run_switchd 2>/dev/null\n")
    script.write("killall -f \"python3 files/run.py\" 2>/dev/null\n\n")

    script.write("RUN_PID=\"\"\n")
    script.write("cleanup() {\n")
    script.write("    if [ -n \"$RUN_PID\" ]; then\n")
    script.write("        kill $RUN_PID 2>/dev/null\n")
    script.write("        wait $RUN_PID 2>/dev/null\n")
    script.write("    fi\n")
    script.write("    killall bf_switchd 2>/dev/null\n")
    script.write("}\n")
    script.write("trap cleanup EXIT INT TERM\n\n")

    script.write("bf_kdrv_mod_load $SDE_INSTALL\n\n")

    script.write("/$SDE/../tools/p4_build.sh files/pipoTG.p4\n\n")

    script.write("/$SDE/run_switchd.sh -p pipoTG > switchd.log 2>&1 &\n")
    script.write("sleep 20\n\n")

    script.write("/$SDE/run_bfshell.sh -f files/portConfig.txt\n\n")

    script.write("#back terminal to normal state + ESC[H + ESC[2J\n")
    script.write("stty sane 2>/dev/null || true\n")
    script.write("printf '^[[H^[[2J'\n\n")

    if graph_enabled:
        script.write("python3 files/run.py\n")
    else:
        script.write("rm -f run.log\n")
        script.write("python3 files/run.py > run.log 2>&1 &\n")
        script.write("RUN_PID=$!\n")
        script.write("sleep 2\n")
        script.write("if ! ps -p $RUN_PID >/dev/null 2>&1; then\n")
        script.write("    echo '[PIPO-TG] ERROR: files/run.py terminated early'\n")
        script.write("    cat run.log\n")
        script.write("    exit 1\n")
        script.write("fi\n")
        script.write("/$SDE/run_bfshell.sh -f files/view\n")

    script.close()

def generatePortConfig(ports):

    port_file = open('files/portConfig.txt', 'w')

    port_file.write('ucli\n')
    port_file.write('pm\n')

    for port, bw in ports:
        speed = str(bw) if bw else '10G'
        port_file.write(f'port-add {port} {speed} NONE\n')
        port_file.write(f'port-enb {port}\n')
        port_file.write(f'an-set {port} 2 \n')
        port_file.write(f'port-dis {port}\n')
        port_file.write(f'port-enb {port}\n')

    port_file.write('show\n')
    port_file.write('exit\n')
    port_file.write('exit\n')


def generateP4(obj):

    flows = _flows_from_obj(obj)
    n_flows = len(flows) if flows else 1
    idx_w = _idx_width(n_flows)

    meter_enabled = (str(getattr(obj, 'throughput_mode', '')) == 'meter')

    filep4 = open('files/pipoTG.p4', 'w')

    filep4.write('/*******************************************************************************\n')
    filep4.write('* BAREFOOT NETWORKS CONFIDENTIAL & PROPRIETARY\n')
    filep4.write('*\n')
    filep4.write('* Copyright (c) 2019-present Barefoot Networks, Inc.\n')
    filep4.write('*\n')
    filep4.write('* All Rights Reserved.\n')
    filep4.write('******************************************************************************/\n\n')

    filep4.write('#if __TARGET_TOFINO__ == 2\n#include <t2na.p4>\n#else\n#include <tna.p4>\n#endif\n\n')
    filep4.write('#include "headers.p4"\n')
    filep4.write('#include "util.p4"\n\n')

    filep4.write('// ============================================================================\n')
    filep4.write('//  GENERATED P4 PROGRAM (PIPO-TG)\n')
    filep4.write('// ============================================================================\n\n')
    filep4.write('// ============================== HEADERS ====================================\n\n')

    filep4.write('struct headers {\n')
    filep4.write('  pktgen_timer_header_t     timer;\n')
    filep4.write('  pktgen_port_down_header_t port_down;\n')
    filep4.write('  ethernet_h    ethernet;\n')
    filep4.write('  ipv4_h        ipv4;\n')
    filep4.write('  tcp_h         tcp;\n')
    filep4.write('  udp_h         udp;\n')
    filep4.write('};\n\n')

    filep4.write('// ============================== PARSER =====================================\n\n')
    filep4.write('parser SwitchIngressParser(\n')
    filep4.write('  packet_in packet,\n')
    filep4.write('  out headers hdr,\n')
    filep4.write('  out empty_metadata_t md,\n')
    filep4.write('  out ingress_intrinsic_metadata_t ig_intr_md) {\n\n')

    filep4.write('  state start {\n')
    filep4.write('      packet.extract(ig_intr_md);\n')
    filep4.write('      packet.advance(PORT_METADATA_SIZE);\n\n')
    filep4.write('      pktgen_port_down_header_t pktgen_pd_hdr = packet.lookahead<pktgen_port_down_header_t>();\n')
    filep4.write('      transition select(pktgen_pd_hdr.app_id) {\n')
    filep4.write('          1 : parse_pktgen_timer;\n')
    filep4.write('          2 : parse_pktgen_timer;\n')
    filep4.write('          3 : parse_pktgen_port_down;\n')
    filep4.write('          4 : parse_pktgen_port_down;\n')
    filep4.write('          default : reject;\n')
    filep4.write('      }\n')
    filep4.write('  }\n\n')

    filep4.write('  state parse_pktgen_timer {\n')
    filep4.write('      packet.extract(hdr.timer);\n')
    filep4.write('      transition parse_ethernet;\n')
    filep4.write('  }\n\n')

    filep4.write('  state parse_ethernet {\n')
    filep4.write('      packet.extract(hdr.ethernet);\n')
    filep4.write('      transition select(hdr.ethernet.ether_type) {\n')
    filep4.write('          ETHERTYPE_IPV4:    parse_ipv4;\n')
    filep4.write('          default:           accept;\n')
    filep4.write('      }\n')
    filep4.write('  }\n\n')

    filep4.write('  state parse_ipv4 {\n')
    filep4.write('      packet.extract(hdr.ipv4);\n')
    filep4.write('      transition select(hdr.ipv4.protocol) {\n')
    filep4.write('          IP_PROTOCOLS_UDP:    parse_udp;\n')
    filep4.write('          IP_PROTOCOLS_TCP:    parse_tcp;\n')
    filep4.write('          default:             accept;\n')
    filep4.write('      }\n')
    filep4.write('  }\n\n')

    filep4.write('  state parse_tcp {\n')
    filep4.write('      packet.extract(hdr.tcp);\n')
    filep4.write('      transition accept;\n')
    filep4.write('  }\n\n')

    filep4.write('  state parse_udp {\n')
    filep4.write('      packet.extract(hdr.udp);\n')
    filep4.write('      transition accept;\n')
    filep4.write('  }\n\n')

    filep4.write('  state parse_pktgen_port_down {\n')
    filep4.write('      packet.extract(hdr.port_down);\n')
    filep4.write('      transition accept;\n')
    filep4.write('  }\n')
    filep4.write('}\n\n')

    filep4.write('// ============================== DEPARSER ===================================\n\n')

    filep4.write('control SwitchIngressDeparser(\n')
    filep4.write('      packet_out pkt,\n')
    filep4.write('      inout headers hdr,\n')
    filep4.write('      in empty_metadata_t ig_md,\n')
    filep4.write('      in ingress_intrinsic_metadata_for_deparser_t ig_intr_dprsr_md) {\n\n')
    filep4.write('\n  // --- Apply ----------------------------------------------------------------\n\n')

    filep4.write('  apply {\n')
    filep4.write('      pkt.emit(hdr);\n')
    filep4.write('  }\n')
    filep4.write('}\n\n')

    filep4.write('// =========================== INGRESS CONTROL ===============================\n\n')

    filep4.write('control SwitchIngress(\n')
    filep4.write('      inout headers hdr,\n')
    filep4.write('      inout empty_metadata_t md,\n')
    filep4.write('      in ingress_intrinsic_metadata_t ig_intr_md,\n')
    filep4.write('      in ingress_intrinsic_metadata_from_parser_t ig_intr_prsr_md,\n')
    filep4.write('      inout ingress_intrinsic_metadata_for_deparser_t ig_intr_dprsr_md,\n')
    filep4.write('      inout ingress_intrinsic_metadata_for_tm_t ig_intr_tm_md) {\n\n')

    filep4.write('  // --- Externs & state -----------------------------------------------------\n')
    filep4.write('  Random<bit<32>>() rnd_src;\n')

    if meter_enabled:
        filep4.write(f'  Meter<bit<{idx_w}>>({n_flows}, MeterType_t.BYTES) meter;\n')
        filep4.write('  bit<2> color = 0;\n\n')

    filep4.write(f'  Counter<bit<64>, bit<{idx_w}>>({n_flows}, CounterType_t.PACKETS_AND_BYTES) flow_counter;\n\n')

    filep4.write('\n  // --- Actions --------------------------------------------------------------\n\n')

    filep4.write('  action drop() {\n')
    filep4.write('      ig_intr_dprsr_md.drop_ctl = 0x1;\n')
    filep4.write('  }\n\n')

    filep4.write('  action match(PortId_t port) {\n')
    filep4.write('      ig_intr_tm_md.ucast_egress_port = port;\n')
    filep4.write('      ig_intr_tm_md.bypass_egress = 1w1;\n')
    filep4.write('  }\n\n')

    filep4.write('  action randomize_ipv4_src_pfx8() {\n')
    filep4.write('      bit<32> r = rnd_src.get();\n')
    filep4.write('      hdr.ipv4.src_addr = (hdr.ipv4.src_addr[31:24] ++ r[23:0]);\n')
    filep4.write('  }\n\n')
    filep4.write('  action randomize_ipv4_src_pfx16() {\n')
    filep4.write('      bit<32> r = rnd_src.get();\n')
    filep4.write('      hdr.ipv4.src_addr = (hdr.ipv4.src_addr[31:16] ++ r[15:0]);\n')
    filep4.write('  }\n\n')
    filep4.write('  action randomize_ipv4_src_pfx24() {\n')
    filep4.write('      bit<32> r = rnd_src.get();\n')
    filep4.write('      hdr.ipv4.src_addr = (hdr.ipv4.src_addr[31:8] ++ r[7:0]);\n')
    filep4.write('  }\n\n')
    filep4.write('  action flow_cfg(\n')
    filep4.write('      PortId_t     port,\n')
    filep4.write('      mac_addr_t   eth_dst,\n')
    filep4.write('      mac_addr_t   eth_src,\n')
    filep4.write('      bit<16>      ether_type,\n')
    filep4.write('      ipv4_addr_t  ip_src,\n')
    filep4.write('      ipv4_addr_t  ip_dst,\n')
    filep4.write('      bit<8>       ip_diffserv,\n')
    filep4.write('      bit<8>       ip_ttl,\n')
    filep4.write('      bit<16>      ip_id,\n')
    filep4.write('      bit<4>       ip_ihl,\n')
    filep4.write('      bit<8>       ip_proto,\n')
    filep4.write('      bit<1>       srcRandom,\n')
    filep4.write('      bit<8>       srcPrefix\n')
    filep4.write('  ) {\n')
    filep4.write('      ig_intr_tm_md.ucast_egress_port = port;\n')
    filep4.write('      ig_intr_tm_md.bypass_egress = 1w1;\n')
    filep4.write('      hdr.ethernet.dst_addr = eth_dst;\n')
    filep4.write('      hdr.ethernet.src_addr = eth_src;\n')
    filep4.write('      hdr.ethernet.ether_type = ether_type;\n')
    filep4.write('      hdr.ipv4.src_addr = ip_src;\n')
    filep4.write('      hdr.ipv4.dst_addr = ip_dst;\n')
    filep4.write('      hdr.ipv4.diffserv = ip_diffserv;\n')
    filep4.write('      hdr.ipv4.ttl = ip_ttl;\n')
    filep4.write('      hdr.ipv4.identification = ip_id;\n')
    filep4.write('      hdr.ipv4.ihl = ip_ihl;\n')
    filep4.write('      hdr.ipv4.protocol = ip_proto;\n')
    filep4.write('      md.srcRandom = srcRandom;\n')
    filep4.write('      md.srcPrefix = srcPrefix;\n')
    filep4.write('  }\n\n')
    filep4.write('\n  // --- Tables ---------------------------------------------------------------\n\n')

    filep4.write('  table t {\n')
    filep4.write('      key = {\n')
    filep4.write('          hdr.timer.pipe_id        : exact;\n')
    filep4.write('          hdr.timer.app_id         : exact;\n')
    filep4.write('          hdr.timer.batch_id       : exact;\n')
    filep4.write('          hdr.timer.packet_id      : exact;\n')
    filep4.write('          ig_intr_md.ingress_port  : exact;\n')
    filep4.write('      }\n')
    filep4.write('      actions = {\n')
    filep4.write('          flow_cfg;\n')
    filep4.write('          @defaultonly drop;\n')
    filep4.write('      }\n')
    filep4.write('      const default_action = drop();\n')
    filep4.write(f'      size = {n_flows};\n')
    filep4.write('  }\n\n')

    filep4.write('  apply {\n')
    filep4.write(f'      bit<{idx_w}> flow_idx = 0;\n')
    filep4.write('      if (hdr.timer.isValid()) {\n')
    filep4.write(f'          flow_idx = (bit<{idx_w}>) hdr.timer.packet_id;\n')
    filep4.write('      }\n\n')

    filep4.write('      if (hdr.timer.isValid()) {\n')
    filep4.write('          t.apply();\n')
    filep4.write('      } else {\n')
    filep4.write('          drop();\n')
    filep4.write('      }\n\n')

    if meter_enabled:
        filep4.write('      if (hdr.timer.isValid()) {\n')
        filep4.write('          color = (bit<2>) meter.execute(flow_idx);\n')
        filep4.write('          if (color >= 3) { drop(); }\n')
        filep4.write('      }\n\n')

    filep4.write('      // Per-flow IPv4 src randomization (after meter/drop)\n')
    filep4.write('      if (hdr.timer.isValid() && hdr.ipv4.isValid() && (ig_intr_dprsr_md.drop_ctl == 0) && (md.srcRandom == 1w1)) {\n')
    filep4.write('          if (md.srcPrefix == 8w8) { randomize_ipv4_src_pfx8(); }\n')
    filep4.write('          else if (md.srcPrefix == 8w16) { randomize_ipv4_src_pfx16(); }\n')
    filep4.write('          else if (md.srcPrefix == 8w24) { randomize_ipv4_src_pfx24(); }\n')
    filep4.write('      }\n\n')
    filep4.write('      // Count forwarded packets per flow (only if not dropped)\n')
    filep4.write('      if (hdr.timer.isValid() && (ig_intr_dprsr_md.drop_ctl == 0)) {\n')
    filep4.write('          flow_counter.count(flow_idx);\n')
    filep4.write('      }\n\n')

    filep4.write('      if (hdr.timer.isValid()) { hdr.timer.setInvalid(); }\n')
    filep4.write('      ig_intr_tm_md.bypass_egress = 1w1;\n')
    filep4.write('  }\n')
    filep4.write('}\n\n')

    filep4.write('// ============================= PIPELINE ===================================\n\n')

    filep4.write('Pipeline(SwitchIngressParser(),\n')
    filep4.write('      SwitchIngress(),\n')
    filep4.write('      SwitchIngressDeparser(),\n')
    filep4.write('      EmptyEgressParser(),\n')
    filep4.write('      EmptyEgress(),\n')
    filep4.write('      EmptyEgressDeparser()) pipe;\n\n')

    filep4.write('Switch(pipe) main;\n')

    filep4.close()

# Generate run.py (BFRT + pktgen + graph)

def generateRunPy(obj):

    import math

    flows = _flows_from_obj(obj)
    n_flows = len(flows) if flows else 1

    graph_enabled = bool(getattr(obj, 'graph_enabled', False))
    mode = str(getattr(obj, 'throughput_mode', ''))

    # Determine y-axis max from configured targets
    max_target = 1.0
    for f in flows:
        if getattr(f, 'throughput_defined', False):
            if getattr(f, 'throughput_pattern', None) is not None:
                try:
                    max_target = max(max_target, float(max(f.throughput_pattern)))
                except Exception:
                    pass
            else:
                try:
                    max_target = max(max_target, float(f.throughput))
                except Exception:
                    pass

    pad_ratio = 0.10
    intervals = 4
    raw_ymax = max(1.0, max_target * (1.0 + pad_ratio))
    step = int(math.ceil(raw_ymax / float(intervals)))
    ymax = int(step * intervals)
    yticks = [int(i * step) for i in range(intervals + 1)]

    # Ports
    i_port = int(getattr(obj, 'generation_port', 68))

    def _flow_dev_port(ff):
        if getattr(ff, 'out_dev_port', None) is not None:
            return int(ff.out_dev_port)
        return 0

    dev_port_for_stat = _flow_dev_port(flows[0]) if flows else 0

    # Packet template: use flow0 fields
    f0 = flows[0] if flows else obj
    pktlen = int(getattr(f0, 'pktLen', 64))

    colors = ['red', 'magenta', 'green', 'cyan', 'yellow', 'blue', 'white']

    # Build flow descriptors table programming data
    flow_desc = []
    for idx, f in enumerate(flows):
        src_prefix = 32
        if bool(getattr(f, 'ip_src_random', False)):
            src_prefix = _mask_prefix(getattr(f, 'ip_src_mask', '/24'))

        d = {
            'pid': int(f.id),
            'color': colors[idx] if idx < len(colors) else 'white',
            'duration': getattr(f, 'duration_sec', None),
            'has_variance': getattr(f, 'throughput_pattern', None) is not None and getattr(f, 'throughput_pattern_sec', None) is not None,
            'rates': list(getattr(f, 'throughput_pattern', []) or []),
            'secs': list(getattr(f, 'throughput_pattern_sec', []) or []),
            'const_rate': None,

            # Per-flow output port (dev_port)
            'out_dev_port': _flow_dev_port(f),

            # Packet fields
            'eth_dst': str(getattr(f, 'eth_dst', '00:01:02:03:04:05')),
            'eth_src': str(getattr(f, 'eth_src', '00:06:07:08:09:0a')),
            'ether_type': int(getattr(f, 'ether_type', 0x0800)),

            'ip_src': str(getattr(f, 'ip_src', '192.168.0.1')),
            'ip_dst': str(getattr(f, 'ip_dst', '192.168.0.2')),
            'ip_diffserv': int(getattr(f, 'ip_tos', 0)),
            'ip_ttl': int(getattr(f, 'ip_ttl', 64)),
            'ip_id': int(getattr(f, 'ip_id', 1)),
            'ip_ihl': int(getattr(f, 'ip_ihl', 0)),
            'ip_proto': int(getattr(f, 'ip_proto', 0)),

            'srcRandom': 1 if bool(getattr(f, 'ip_src_random', False)) else 0,
            'srcPrefix': int(src_prefix),
        }

        if getattr(f, 'throughput_defined', False) and not d['has_variance']:
            d['const_rate'] = getattr(f, 'throughput', None)

        flow_desc.append(d)

    script = open('files/run.py', 'w')

    script.write('#!/usr/bin/env python3\n')
    script.write('# -*- coding: utf-8 -*-\n')

    script.write('import sys\nimport os\nimport time\nfrom collections import deque\nfrom datetime import datetime\n\n')
    script.write("sys.path.append(os.path.expandvars('$SDE/install/lib/python3.10/site-packages/tofino/'))\n")
    script.write("sys.path.append(os.path.expandvars('$SDE/install/lib/python3.10/site-packages/'))\n")
    script.write("sys.path.append(os.path.expandvars('$SDE/install/lib/python3.10/site-packages/bf_ptf/'))\n\n")

    if graph_enabled:
        script.write('import plotext as plx\n')
    script.write('import grpc\n')
    script.write('import bfrt_grpc.client as gc\n')
    script.write('import ptf.testutils as testutils\n\n')

    if graph_enabled:
        script.write('plx.canvas_color(16)\nplx.axes_color(255)\nplx.ticks_color(160)\n\n')

    script.write('BFRT_ADDR = "localhost:50052"\nDEVICE_ID=0\nPIPE_ID=0xffff\nCLIENT_ID=0\n')
    script.write(f'DEV_PORT={dev_port_for_stat}\n')
    script.write(f'I_PORT={i_port}\n')
    script.write('APP_ID=1\n')
    script.write('INTERVAL_S=1.0\nWINDOW_SEC=50\n')
    script.write(f'YMAX_Mbps={ymax}\nYTICKS={yticks}\n')
    script.write('PLOT_COLS=90\nPLOT_ROWS=25\n')
    script.write(f'GRAPH_ENABLED={str(graph_enabled)}\n')
    script.write(f'THROUGHPUT_MODE="{mode}"\n')
    script.write(f'NUM_FLOWS={n_flows}\n')
    script.write(f'PKTLEN={pktlen}\n')
    script.write(f'FLOWS={flow_desc!r}\n\n')

    script.write('# =============================================================================\n')
    script.write('# 1) Helper functions\n')
    script.write('# =============================================================================\n')

    script.write('def _table_get(bfrt_info, candidates, contains=None):\n')
    script.write('    last = None\n')
    script.write('    for n in candidates:\n')
    script.write('        try:\n')
    script.write('            return bfrt_info.table_get(n)\n')
    script.write('        except Exception as e:\n')
    script.write('            last = e\n')
    script.write('    if contains is not None:\n')
    script.write('        try:\n')
    script.write('            for k in bfrt_info.table_dict.keys():\n')
    script.write('                if contains in k:\n')
    script.write('                    return bfrt_info.table_get(k)\n')
    script.write('        except Exception as e:\n')
    script.write('            last = e\n')
    script.write('    raise last\n\n')

    script.write('def _counter_key(tbl, idx):\n')
    script.write('    for fn in ["$COUNTER_INDEX", "$COUNTER_SPEC_INDEX", "$INDEX"]:\n')
    script.write('        try:\n')
    script.write('            return tbl.make_key([gc.KeyTuple(fn, int(idx))])\n')
    script.write('        except Exception:\n')
    script.write('            pass\n')
    script.write('    return tbl.make_key([gc.KeyTuple("$COUNTER_INDEX", int(idx))])\n\n')

    script.write('def _parse_counter_data(dct):\n')
    script.write('    pkts = 0\n    byt = 0\n')
    script.write('    def _walk(x):\n')
    script.write('        nonlocal pkts, byt\n')
    script.write('        if isinstance(x, dict):\n')
    script.write('            for k,v in x.items():\n')
    script.write('                ku = str(k).upper()\n')
    script.write('                if isinstance(v, (int,float)):\n')
    script.write('                    if "PACK" in ku or "PKT" in ku: pkts = int(v)\n')
    script.write('                    if "BYTE" in ku: byt = int(v)\n')
    script.write('                else:\n')
    script.write('                    _walk(v)\n')
    script.write('        elif isinstance(x, (list,tuple)):\n')
    script.write('            for it in x: _walk(it)\n')
    script.write('    _walk(dct)\n')
    script.write('    return pkts, byt\n\n')

    script.write('def _mac_to_int(mac):\n')
    script.write('    s = str(mac).strip().lower().replace("-", ":")\n')
    script.write('    parts = s.split(":")\n')
    script.write('    if len(parts) != 6: return int(s, 16)\n')
    script.write('    return int("".join(parts), 16)\n\n')

    script.write('def _ip_to_int(ip):\n')
    script.write('    s = str(ip).strip()\n')
    script.write('    if s.isdigit(): return int(s)\n')
    script.write('    o = s.split(".")\n')
    script.write('    if len(o) != 4: return int(s, 16)\n')
    script.write('    return (int(o[0])<<24) | (int(o[1])<<16) | (int(o[2])<<8) | int(o[3])\n\n')

    script.write('# =============================================================================\n')
    script.write('# 2) BFRT connection and table handles\n')
    script.write('# =============================================================================\n')

    script.write('try:\n')
    script.write('    print("[PIPO-TG] connecting to BFRT...")\n')
    script.write('    interface = gc.ClientInterface(grpc_addr=BFRT_ADDR, client_id=CLIENT_ID, device_id=DEVICE_ID, num_tries=5)\n')
    script.write('    bfrt_info = interface.bfrt_info_get()\n')
    script.write('    p4_name = bfrt_info.p4_name_get()\n')
    script.write('    print("[PIPO-TG] target program:", p4_name)\n')
    script.write('    interface.bind_pipeline_config(p4_name)\n')
    script.write('    bfrt_info = interface.bfrt_info_get()\n')
    script.write('    target = gc.Target(device_id=DEVICE_ID, pipe_id=PIPE_ID)\n\n')

    script.write('    t_fwd = _table_get(bfrt_info, ["SwitchIngress.t", "t"], contains=".t")\n')
    script.write('    meter = None\n')
    script.write('    if THROUGHPUT_MODE == "meter":\n')
    script.write('        meter = _table_get(bfrt_info, ["meter", "SwitchIngress.meter"], contains="meter")\n')
    script.write('    flow_ctr = _table_get(bfrt_info, ["flow_counter", "SwitchIngress.flow_counter"], contains="flow_counter")\n')

    script.write('# =============================================================================\n')
    script.write('# 3) Clear previus table entries\n')
    script.write('# =============================================================================\n')

    script.write('    try:\n')
    script.write('        resp = t_fwd.entry_get(target, [], {"from_hw": True})\n')
    script.write('        for _, key in resp:\n')
    script.write('            if key: t_fwd.entry_del(target, [key])\n')
    script.write('    except Exception:\n')
    script.write('        pass\n\n')

    script.write('# =============================================================================\n')
    script.write('# 5) Install per-flow forwarding/rewrite entries\n')
    script.write('# =============================================================================\n')
    script.write('# Each generated packet carries a pktgen timer header.\n')
    script.write('# The field hdr.timer.packet_id is used as the flow identifier.\n')
    script.write('#\n')
    script.write('# Current mapping:\n')
    script.write('#   packet_id 0 -> flow0\n')
    script.write('#   packet_id 1 -> flow1\n')
    script.write('#   ...\n')
    script.write('#\n')
    script.write('# The table action flow_cfg() rewrites Ethernet/IP fields and selects the\n')
    script.write('# output dev_port for each flow.\n')

    script.write('    print(f"[PIPO-TG] installing {NUM_FLOWS} flows in SwitchIngress.t (packet_id 0..{NUM_FLOWS-1})...")\n')
    script.write('    pipe_id = 0\n    batch_id = 0\n    app_id = APP_ID\n')

    script.write('    for f in FLOWS:\n')
    script.write('        pid = int(f["pid"])\n')
    script.write('        k = t_fwd.make_key([\n')
    script.write('            gc.KeyTuple("hdr.timer.pipe_id", pipe_id),\n')
    script.write('            gc.KeyTuple("hdr.timer.app_id", app_id),\n')
    script.write('            gc.KeyTuple("hdr.timer.batch_id", batch_id),\n')
    script.write('            gc.KeyTuple("hdr.timer.packet_id", pid),\n')
    script.write('            gc.KeyTuple("ig_intr_md.ingress_port", I_PORT),\n')
    script.write('        ])\n')
    script.write('        d = t_fwd.make_data([\n')
    script.write('            gc.DataTuple("port", int(f.get("out_dev_port", 0))),\n')
    script.write('            gc.DataTuple("eth_dst", _mac_to_int(f.get("eth_dst"))),\n')
    script.write('            gc.DataTuple("eth_src", _mac_to_int(f.get("eth_src"))),\n')
    script.write('            gc.DataTuple("ether_type", int(f.get("ether_type", 0x0800))),\n')
    script.write('            gc.DataTuple("ip_src", _ip_to_int(f.get("ip_src"))),\n')
    script.write('            gc.DataTuple("ip_dst", _ip_to_int(f.get("ip_dst"))),\n')
    script.write('            gc.DataTuple("ip_diffserv", int(f.get("ip_diffserv", 0))),\n')
    script.write('            gc.DataTuple("ip_ttl", int(f.get("ip_ttl", 64))),\n')
    script.write('            gc.DataTuple("ip_id", int(f.get("ip_id", 1))),\n')
    script.write('            gc.DataTuple("ip_ihl", int(f.get("ip_ihl", 0))),\n')
    script.write('            gc.DataTuple("ip_proto", int(f.get("ip_proto", 0))),\n')
    script.write('            gc.DataTuple("srcRandom", int(f.get("srcRandom", 0))),\n')
    script.write('            gc.DataTuple("srcPrefix", int(f.get("srcPrefix", 32))),\n')
    script.write('        ], "SwitchIngress.flow_cfg")\n')
    script.write('        t_fwd.entry_add(target, [k], [d])\n\n')

    script.write('# =============================================================================\n')
    script.write('# 6) Configure Packet Generator\n')
    script.write('# =============================================================================\n')

    script.write('    app_cfg = _table_get(bfrt_info, ["app_cfg"], contains="app_cfg")\n')
    script.write('    pkt_buf = _table_get(bfrt_info, ["pkt_buffer"], contains="pkt_buffer")\n')
    script.write('    port_cfg2 = _table_get(bfrt_info, ["port_cfg"], contains="port_cfg")\n\n')

    script.write('    print("[PIPO-TG] creating packet template")\n')
    script.write('    p = testutils.simple_ip_packet(pktlen=PKTLEN, eth_dst=FLOWS[0]["eth_dst"], eth_src=FLOWS[0]["eth_src"],\n')
    script.write('        dl_vlan_enable=False, vlan_vid=0, vlan_pcp=0, dl_vlan_cfi=0,\n')
    script.write('        ip_src=FLOWS[0]["ip_src"], ip_dst=FLOWS[0]["ip_dst"], ip_tos=int(FLOWS[0].get("ip_diffserv",0)),\n')
    script.write('        ip_ecn=None, ip_dscp=None, ip_ttl=int(FLOWS[0].get("ip_ttl",64)), ip_id=int(FLOWS[0].get("ip_id",1)),\n')
    script.write('        ip_ihl=None, ip_options=False, ip_proto=int(FLOWS[0].get("ip_proto",0)))\n')

    script.write('    src_port = I_PORT\n')
    script.write('    num_lines = (PKTLEN + 15) // 16\n')
    script.write('    max_line = 1024 - num_lines\n')
    script.write('    line = 9 if 9 <= max_line else 0\n')
    script.write('    buff_offset = line * 16\n')
    script.write('    b_count = 1\n')
    script.write('    p_count = NUM_FLOWS\n\n')

    script.write('    port_cfg2.entry_mod(target, [port_cfg2.make_key([gc.KeyTuple("dev_port", src_port)])], [port_cfg2.make_data([gc.DataTuple("pktgen_enable", bool_val=True)])])\n')
    script.write('    data = app_cfg.make_data([\n')
    script.write('        gc.DataTuple("timer_nanosec", 1),\n')
    script.write('        gc.DataTuple("app_enable", bool_val=False),\n')
    script.write('        gc.DataTuple("pkt_len", PKTLEN),\n')
    script.write('        gc.DataTuple("pkt_buffer_offset", buff_offset),\n')
    script.write('        gc.DataTuple("pipe_local_source_port", src_port),\n')
    script.write('        gc.DataTuple("increment_source_port", bool_val=False),\n')
    script.write('        gc.DataTuple("batch_count_cfg", b_count - 1),\n')
    script.write('        gc.DataTuple("packets_per_batch_cfg", p_count - 1),\n')
    script.write('        gc.DataTuple("ibg", 0),\n')
    script.write('        gc.DataTuple("ibg_jitter", 0),\n')
    script.write('        gc.DataTuple("ipg", 0),\n')
    script.write('        gc.DataTuple("ipg_jitter", 0),\n')
    script.write('        gc.DataTuple("batch_counter", 0),\n')
    script.write('        gc.DataTuple("pkt_counter", 0),\n')
    script.write('        gc.DataTuple("trigger_counter", 0),\n')
    script.write('    ], "trigger_timer_periodic")\n')
    script.write('    app_cfg.entry_mod(target, [app_cfg.make_key([gc.KeyTuple("app_id", APP_ID)])], [data])\n')
    script.write('    pkt_buf.entry_mod(\n')
    script.write('        target,\n')
    script.write('        [pkt_buf.make_key([gc.KeyTuple("pkt_buffer_offset", buff_offset), gc.KeyTuple("pkt_buffer_size", PKTLEN)])],\n')
    script.write('        [pkt_buf.make_data([gc.DataTuple("buffer", bytearray(bytes(p)))])]\n')
    script.write('    )\n')
    script.write('    app_cfg.entry_mod(target, [app_cfg.make_key([gc.KeyTuple("app_id", APP_ID)])], [app_cfg.make_data([gc.DataTuple("app_enable", bool_val=True)], "trigger_timer_periodic")])\n\n')

    script.write('# =============================================================================\n')
    script.write('# 7) Configure per-flow meters\n')
    script.write('# =============================================================================\n')

    script.write('    def _meter_set(idx, mbps):\n')
    script.write('        if meter is None: return\n')
    script.write('        kbps = int(float(mbps) * 1000)\n')
    script.write('        k = meter.make_key([gc.KeyTuple("$METER_INDEX", int(idx))])\n')
    script.write('        d = meter.make_data([\n')
    script.write('            gc.DataTuple("$METER_SPEC_CIR_KBPS", kbps),\n')
    script.write('            gc.DataTuple("$METER_SPEC_PIR_KBPS", kbps),\n')
    script.write('            gc.DataTuple("$METER_SPEC_CBS_KBITS", 1024),\n')
    script.write('            gc.DataTuple("$METER_SPEC_PBS_KBITS", 1024),\n')
    script.write('        ], None)\n')
    script.write('        try:\n')
    script.write('            meter.entry_mod(target, [k], [d])\n')
    script.write('        except Exception:\n')
    script.write('            try: meter.entry_add(target, [k], [d])\n')
    script.write('            except Exception: pass\n\n')

    script.write('    for f in FLOWS:\n')
    script.write('        pid = int(f["pid"])\n')
    script.write('        if f.get("has_variance") and len(f.get("rates", [])) > 0:\n')
    script.write('            f["current_target"] = float(f["rates"][0])\n')
    script.write('        elif f.get("const_rate") is not None:\n')
    script.write('            f["current_target"] = float(f["const_rate"])\n')
    script.write('        else:\n')
    script.write('            f["current_target"] = 0.0\n')
    script.write('        _rate = f["current_target"] if (f.get("has_variance") or f.get("const_rate") is not None) else 100000.0\n')
    script.write('        if THROUGHPUT_MODE == "meter": _meter_set(pid, _rate)\n\n')

    script.write('    port_stat = None\n')
    script.write('    try: port_stat = bfrt_info.table_get("$PORT_STAT")\n')
    script.write('    except Exception: port_stat = None\n')
    script.write('    port_key = None\n')
    script.write('    if port_stat is not None:\n')
    script.write('        port_key = port_stat.make_key([gc.KeyTuple("$DEV_PORT", DEV_PORT)])\n\n')

    script.write('# =============================================================================\n')
    script.write('# 8) Initialize counters and statistics\n')
    script.write('# =============================================================================\n')

    script.write('    prev = {}\n')
    script.write('    for f in FLOWS:\n')
    script.write('        pid = int(f["pid"])\n')
    script.write('        try:\n')
    script.write('            k = _counter_key(flow_ctr, pid)\n')
    script.write('            for data, _ in flow_ctr.entry_get(target, [k], {"from_hw": True}):\n')
    script.write('                pk, by = _parse_counter_data(data.to_dict())\n')
    script.write('                prev[pid] = (pk, by)\n')
    script.write('                break\n')
    script.write('        except Exception:\n')
    script.write('            prev[pid] = (0,0)\n\n')

    if graph_enabled:
        script.write('    xs = deque(maxlen=int(WINDOW_SEC))\n')
        script.write('    ys = {int(f["pid"]): deque(maxlen=int(WINDOW_SEC)) for f in FLOWS}\n')
        script.write('    plx.theme("clear")\n\n')

    script.write('    t0 = time.time()\n')
    script.write('    phase_t0 = {int(f["pid"]): t0 for f in FLOWS}\n')
    script.write('    phase_idx = {int(f["pid"]): 0 for f in FLOWS}\n')
    script.write('    disabled = {int(f["pid"]): False for f in FLOWS}\n\n')

    script.write('# =============================================================================\n')
    script.write('# 9) Runtime loop: duration, variance, monitoring and graph\n')
    script.write('# =============================================================================\n')

    script.write('    print("[PIPO-TG] running... Ctrl+C to exit")\n')
    script.write('    while True:\n')
    script.write('        now = time.time()\n')
    script.write('        elapsed = now - t0\n')
    script.write('        dt = INTERVAL_S\n\n')

    script.write('        for f in FLOWS:\n')
    script.write('            pid = int(f["pid"])\n')
    script.write('            dur = f.get("duration")\n')
    script.write('            if (dur is not None) and (not disabled[pid]) and elapsed >= float(dur):\n')
    script.write('                disabled[pid] = True\n')
    script.write('                f["current_target"] = 0.0\n')
    script.write('                if THROUGHPUT_MODE == "meter":\n')
    script.write('                    _meter_set(pid, 0.0)\n')
    script.write('                print(f"[PIPO-TG] flow{pid} disabled (duration reached) -> meter=0")\n\n')

    script.write('        for f in FLOWS:\n')
    script.write('            pid = int(f["pid"])\n')
    script.write('            if disabled[pid]:\n')
    script.write('                continue\n')
    script.write('            if f.get("has_variance") and len(f.get("rates", [])) > 0:\n')
    script.write('                idx = phase_idx[pid]\n')
    script.write('                secs = float(f["secs"][idx])\n')
    script.write('                if (now - phase_t0[pid]) >= secs:\n')
    script.write('                    idx = (idx + 1) % len(f["rates"])\n')
    script.write('                    phase_idx[pid] = idx\n')
    script.write('                    phase_t0[pid] = now\n')
    script.write('                    f["current_target"] = float(f["rates"][idx])\n')
    script.write('                    if THROUGHPUT_MODE == "meter":\n')
    script.write('                        _meter_set(pid, f["current_target"])\n\n')

    script.write('        tx_mbps = 0.0\n')
    script.write('        pps_port = 0\n')
    script.write('        if port_stat is not None and port_key is not None:\n')
    script.write('            try:\n')
    script.write('                for data, _ in port_stat.entry_get(target, [port_key], {"from_hw": True}):\n')
    script.write('                    d = data.to_dict()\n')
    script.write('                    tx_mbps = float(d.get("$TX_RATE", 0.0)) / 1e6\n')
    script.write('                    pps_port = int(d.get("$TX_PPS", 0))\n')
    script.write('                    break\n')
    script.write('            except Exception:\n')
    script.write('                pass\n\n')

    script.write('        flow_tx = {}\n')
    script.write('        flow_pps = {}\n')
    script.write('        for f in FLOWS:\n')
    script.write('            pid = int(f["pid"])\n')
    script.write('            try:\n')
    script.write('                k = _counter_key(flow_ctr, pid)\n')
    script.write('                for data, _ in flow_ctr.entry_get(target, [k], {"from_hw": True}):\n')
    script.write('                    pk, by = _parse_counter_data(data.to_dict())\n')
    script.write('                    pk0, by0 = prev.get(pid, (0,0))\n')
    script.write('                    dpk = pk - pk0\n')
    script.write('                    dby = by - by0\n')
    script.write('                    prev[pid] = (pk, by)\n')
    script.write('                    flow_pps[pid] = int(dpk / dt) if dt > 0 else 0\n')
    script.write('                    flow_tx[pid] = (float(dby) * 8.0 / dt / 1e6) if dt > 0 else 0.0\n')
    script.write('                    break\n')
    script.write('            except Exception:\n')
    script.write('                flow_pps[pid] = 0\n')
    script.write('                flow_tx[pid] = 0.0\n\n')

    if graph_enabled:
        script.write('        xs.append(elapsed)\n')
        script.write('        for f in FLOWS:\n')
        script.write('            pid = int(f["pid"])\n')
        script.write('            ys[pid].append(float(flow_tx.get(pid, 0.0)))\n')
        script.write('        plx.clear_terminal(); plx.clf(); plx.theme("clear"); plx.plotsize(PLOT_COLS, PLOT_ROWS)\n')
        script.write('        for f in FLOWS:\n')
        script.write('            pid = int(f["pid"])\n')
        script.write('            col = f.get("color", "white")\n')
        script.write('            plx.plot(xs, ys[pid], marker="braille", color=col, label=f"flow{pid}")\n')
        script.write('        x_min = max(0.0, elapsed - WINDOW_SEC)\n')
        script.write('        plx.xlim(x_min, x_min + WINDOW_SEC)\n')
        script.write('        plx.ylim(0, YMAX_Mbps)\n')
        script.write('        plx.yticks(YTICKS)\n')
        script.write('        plx.title(f"Measured TX per flow (Mbps) | PORT TX={tx_mbps:.1f} Mbps PPS={pps_port}")\n')
        script.write('        plx.xlabel("time (s)"); plx.ylabel("Mbps")\n')
        script.write('        plx.show()\n')

    script.write('        clock = datetime.now().strftime("%H:%M:%S.%f")[:-3]\n')
    script.write('        print(f"{clock} (+{elapsed:6.1f}s) PORT: TX={tx_mbps:8.3f} Mbps PPS={pps_port}")\n')
    script.write('        for f in FLOWS:\n')
    script.write('            pid = int(f["pid"])\n')
    script.write('            rem = "INF"\n')
    script.write('            if f.get("duration") is not None:\n')
    script.write("                rem = f\"{max(0.0, float(f['duration']) - elapsed):.1f}s\"\n")
    script.write('            txf = float(flow_tx.get(pid, 0.0))\n')
    script.write('            ppsf = int(flow_pps.get(pid, 0))\n')
    script.write('            tgt = float(f.get("current_target", 0.0))\n')
    script.write('            col = f.get("color", "white").upper()\n')
    script.write('            print(f"  flow{pid}(pid={pid} {col}): TX={txf:8.3f} Mbps PPS={ppsf:7d}  target={tgt:6.1f}  rem={rem}")\n')

    script.write('        time.sleep(INTERVAL_S)\n\n')

    script.write('except KeyboardInterrupt:\n')
    script.write('    print("\\n[PIPO-TG] Ctrl+C received — exiting")\n')
    script.write('except Exception as e:\n')
    script.write('    print("[PIPO-TG] ERROR:", e)\n')

    script.close()
