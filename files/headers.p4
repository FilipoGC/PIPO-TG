#ifndef _HEADERS_
#define _HEADERS_

typedef bit<48> mac_addr_t;
typedef bit<32> ipv4_addr_t;
typedef bit<12> vlan_id_t;

typedef bit<16> ether_type_t;
const ether_type_t ETHERTYPE_IPV4 = 16w0x0800;
const ether_type_t ETHERTYPE_VLAN = 16w0x8100;

typedef bit<8> ip_protocol_t;
const ip_protocol_t IP_PROTOCOLS_TCP = 6;
const ip_protocol_t IP_PROTOCOLS_UDP = 17;

header ethernet_h {
 mac_addr_t dst_addr;
 mac_addr_t src_addr;
 bit<16> ether_type;
}

header vlan_tag_h {
 bit<3> pcp;
 bit<1> cfi;
 vlan_id_t vid;
 bit<16> ether_type;
}

header ipv4_h {
 bit<4> version;
 bit<4> ihl;
 bit<8> diffserv;
 bit<16> total_len;
 bit<16> identification;
 bit<3> flags;
 bit<13> frag_offset;
 bit<8> ttl;
 bit<8> protocol;
 bit<16> hdr_checksum;
 ipv4_addr_t src_addr;
 ipv4_addr_t dst_addr;
}

header tcp_h {
 bit<16> src_port;
 bit<16> dst_port;
 bit<32> seq_no;
 bit<32> ack_no;
 bit<4> data_offset;
 bit<4> res;
 bit<8> flags;
 bit<16> window;
 bit<16> checksum;
 bit<16> urgent_ptr;
}

header udp_h {
 bit<16> src_port;
 bit<16> dst_port;
 bit<16> hdr_length;
 bit<16> checksum;
}

header myhdr_h {
    bit<8> msg_type;
    bit<4> flags;
    bit<4> reserved;
}

struct empty_header_t {}

struct empty_metadata_t {
    bit<1> srcRandom;
    bit<8> srcPrefix;
}

#endif /* _HEADERS_ */
