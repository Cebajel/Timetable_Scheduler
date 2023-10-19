import networkx as nx
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet


class SDNController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SDNController, self).__init__(*args, **kwargs)
        self.graph = nx.Graph()  # Network topology graph
        self.flow_table = {}  # Flow table for switches

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Install default flow entries (e.g., flood all unknown traffic)
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
        self.add_flow(datapath, 0, match, actions)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        #    # Handle incoming packets here (e.g., for LLDP or topology discovery)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        self.logger.info("packet in %s %s %s %s", dpid, src, dst, msg.in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = msg.in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            self.add_flow(datapath, msg.in_port, dst, src, actions)

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = datapath.ofproto_parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=msg.in_port,
            actions=actions,
            data=data,
        )
        datapath.send_msg(out)

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=datapath,
            priority=priority,
            match=match,
            instructions=inst,
            table_id=0,
        )
        datapath.send_msg(mod)

    def update_flow_table(self, datapath, new_paths):
        # Update the flow table entries based on new paths
        for dst, path in new_paths.items():
            actions = [datapath.ofproto_parser.OFPActionOutput(port) for port in path]
            match = datapath.ofproto_parser.OFPMatch(eth_dst=dst)
            self.add_flow(datapath, 1, match, actions)
	switch_list = get_switch(self.topology_api_app, None)
        switches=[switch.dp.id for switch in switch_list]
        links_list = get_link(self.topology_api_app, None)
        links=[(link.src.dpid,link.dst.dpid,{'port':link.src.port_no}) for link in links_list]
        print(f"Links : {links}")
        print(f"Switches : {switches}")
        self.net=nx.DiGraph()
        self.net.add_nodes_from(switches)
        self.net.add_edges_from(links)
        if src not in self.net: #Learn it
            self.net.add_node(src) # Add a node to the graph
            self.net.add_edge(src,dpid) # Add a link from the node to it's edge switch
            self.net.add_edge(dpid,src,{'port':msg.in_port})  # Add link from switch to node and make sure you are identifying the output port.
        if dst in self.net:
            path=nx.shortest_path(self.net,src,dst) # get shortest path  
            next=path[path.index(dpid)+1] #get next hop
            out_port=self.net[dpid][next]['port'] #get output port
        else:
            out_port = ofproto.OFPP_FLOOD
    # Implement functions for shortest path computation and link failure detection here


def main():
    from ryu.cmd import manager

    manager.main()


if __name__ == "__main__":
    main()

