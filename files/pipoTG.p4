/*******************************************************************************
* BAREFOOT NETWORKS CONFIDENTIAL & PROPRIETARY
*
* Copyright (c) 2019-present Barefoot Networks, Inc.
*
* All Rights Reserved.
******************************************************************************/

#if __TARGET_TOFINO__ == 2
#include <t2na.p4>
#else
#include <tna.p4>
#endif

#include "headers.p4"
#include "util.p4"

// ============================================================================
//  GENERATED P4 PROGRAM (PIPO-TG)
// ============================================================================

// ============================== HEADERS ====================================

struct headers {
  pktgen_timer_header_t     timer;
  pktgen_port_down_header_t port_down;
  ethernet_h    ethernet;
  ipv4_h        ipv4;
  tcp_h         tcp;
  udp_h         udp;
};

// ============================== PARSER =====================================

parser SwitchIngressParser(
  packet_in packet,
  out headers hdr,
  out empty_metadata_t md,
  out ingress_intrinsic_metadata_t ig_intr_md) {

  state start {
      packet.extract(ig_intr_md);
      packet.advance(PORT_METADATA_SIZE);

      pktgen_port_down_header_t pktgen_pd_hdr = packet.lookahead<pktgen_port_down_header_t>();
      transition select(pktgen_pd_hdr.app_id) {
          1 : parse_pktgen_timer;
          2 : parse_pktgen_timer;
          3 : parse_pktgen_port_down;
          4 : parse_pktgen_port_down;
          default : reject;
      }
  }

  state parse_pktgen_timer {
      packet.extract(hdr.timer);
      transition parse_ethernet;
  }

  state parse_ethernet {
      packet.extract(hdr.ethernet);
      transition select(hdr.ethernet.ether_type) {
          ETHERTYPE_IPV4:    parse_ipv4;
          default:           accept;
      }
  }

  state parse_ipv4 {
      packet.extract(hdr.ipv4);
      transition select(hdr.ipv4.protocol) {
          IP_PROTOCOLS_UDP:    parse_udp;
          IP_PROTOCOLS_TCP:    parse_tcp;
          default:             accept;
      }
  }

  state parse_tcp {
      packet.extract(hdr.tcp);
      transition accept;
  }

  state parse_udp {
      packet.extract(hdr.udp);
      transition accept;
  }

  state parse_pktgen_port_down {
      packet.extract(hdr.port_down);
      transition accept;
  }
}

// ============================== DEPARSER ===================================

control SwitchIngressDeparser(
      packet_out pkt,
      inout headers hdr,
      in empty_metadata_t ig_md,
      in ingress_intrinsic_metadata_for_deparser_t ig_intr_dprsr_md) {


  // --- Apply ----------------------------------------------------------------

  apply {
      pkt.emit(hdr);
  }
}

// =========================== INGRESS CONTROL ===============================

control SwitchIngress(
      inout headers hdr,
      inout empty_metadata_t md,
      in ingress_intrinsic_metadata_t ig_intr_md,
      in ingress_intrinsic_metadata_from_parser_t ig_intr_prsr_md,
      inout ingress_intrinsic_metadata_for_deparser_t ig_intr_dprsr_md,
      inout ingress_intrinsic_metadata_for_tm_t ig_intr_tm_md) {

  // --- Externs & state -----------------------------------------------------
  Random<bit<32>>() rnd_src;
  Meter<bit<2>>(4, MeterType_t.BYTES) meter;
  bit<2> color = 0;

  Counter<bit<64>, bit<2>>(4, CounterType_t.PACKETS_AND_BYTES) flow_counter;


  // --- Actions --------------------------------------------------------------

  action drop() {
      ig_intr_dprsr_md.drop_ctl = 0x1;
  }

  action match(PortId_t port) {
      ig_intr_tm_md.ucast_egress_port = port;
      ig_intr_tm_md.bypass_egress = 1w1;
  }

  action randomize_ipv4_src_pfx8() {
      bit<32> r = rnd_src.get();
      hdr.ipv4.src_addr = (hdr.ipv4.src_addr[31:24] ++ r[23:0]);
  }

  action randomize_ipv4_src_pfx16() {
      bit<32> r = rnd_src.get();
      hdr.ipv4.src_addr = (hdr.ipv4.src_addr[31:16] ++ r[15:0]);
  }

  action randomize_ipv4_src_pfx24() {
      bit<32> r = rnd_src.get();
      hdr.ipv4.src_addr = (hdr.ipv4.src_addr[31:8] ++ r[7:0]);
  }

  action flow_cfg(
      PortId_t     port,
      mac_addr_t   eth_dst,
      mac_addr_t   eth_src,
      bit<16>      ether_type,
      ipv4_addr_t  ip_src,
      ipv4_addr_t  ip_dst,
      bit<8>       ip_diffserv,
      bit<8>       ip_ttl,
      bit<16>      ip_id,
      bit<4>       ip_ihl,
      bit<8>       ip_proto,
      bit<1>       srcRandom,
      bit<8>       srcPrefix
  ) {
      ig_intr_tm_md.ucast_egress_port = port;
      ig_intr_tm_md.bypass_egress = 1w1;
      hdr.ethernet.dst_addr = eth_dst;
      hdr.ethernet.src_addr = eth_src;
      hdr.ethernet.ether_type = ether_type;
      hdr.ipv4.src_addr = ip_src;
      hdr.ipv4.dst_addr = ip_dst;
      hdr.ipv4.diffserv = ip_diffserv;
      hdr.ipv4.ttl = ip_ttl;
      hdr.ipv4.identification = ip_id;
      hdr.ipv4.ihl = ip_ihl;
      hdr.ipv4.protocol = ip_proto;
      md.srcRandom = srcRandom;
      md.srcPrefix = srcPrefix;
  }


  // --- Tables ---------------------------------------------------------------

  table t {
      key = {
          hdr.timer.pipe_id        : exact;
          hdr.timer.app_id         : exact;
          hdr.timer.batch_id       : exact;
          hdr.timer.packet_id      : exact;
          ig_intr_md.ingress_port  : exact;
      }
      actions = {
          flow_cfg;
          @defaultonly drop;
      }
      const default_action = drop();
      size = 4;
  }

  apply {
      bit<2> flow_idx = 0;
      if (hdr.timer.isValid()) {
          flow_idx = (bit<2>) hdr.timer.packet_id;
      }

      if (hdr.timer.isValid()) {
          t.apply();
      } else {
          drop();
      }

      if (hdr.timer.isValid()) {
          color = (bit<2>) meter.execute(flow_idx);
          if (color >= 3) { drop(); }
      }

      // Per-flow IPv4 src randomization (after meter/drop)
      if (hdr.timer.isValid() && hdr.ipv4.isValid() && (ig_intr_dprsr_md.drop_ctl == 0) && (md.srcRandom == 1w1)) {
          if (md.srcPrefix == 8w8) { randomize_ipv4_src_pfx8(); }
          else if (md.srcPrefix == 8w16) { randomize_ipv4_src_pfx16(); }
          else if (md.srcPrefix == 8w24) { randomize_ipv4_src_pfx24(); }
      }

      // Count forwarded packets per flow (only if not dropped)
      if (hdr.timer.isValid() && (ig_intr_dprsr_md.drop_ctl == 0)) {
          flow_counter.count(flow_idx);
      }

      if (hdr.timer.isValid()) { hdr.timer.setInvalid(); }
      ig_intr_tm_md.bypass_egress = 1w1;
  }
}

// ============================= PIPELINE ===================================

Pipeline(SwitchIngressParser(),
      SwitchIngress(),
      SwitchIngressDeparser(),
      EmptyEgressParser(),
      EmptyEgress(),
      EmptyEgressDeparser()) pipe;

Switch(pipe) main;
