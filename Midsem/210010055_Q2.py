from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch, CPULimitedHost
from mininet.log import setLogLevel
from mininet.cli import CLI

setLogLevel( 'info' )


class SingleSwitchTopo(Topo):
	def build(self):
		c1 = self.addSwitch('c1')
		a1 = self.addSwitch('a1')
		a2 = self.addSwitch('a2')
		e1 = self.addSwitch('e1')
		e2 = self.addSwitch('e2')
		e3 = self.addSwitch('e3')
		e4 = self.addSwitch('e4')

		h1 = self.addHost('h1', cpu=0.5)
		h2 = self.addHost('h2', cpu=0.5)
		h3 = self.addHost('h3', cpu=0.5)
		h4 = self.addHost('h4', cpu=0.5)
		h5 = self.addHost('h5', cpu=0.5)
		h6 = self.addHost('h6', cpu=0.5)
		h7 = self.addHost('h7', cpu=0.5)
		h8 = self.addHost('h8', cpu=0.5)
		
		self.addLink(c1, a1, bw=10, delay='5ms', loss=1, max_queue_size=1000)
		self.addLink(c1, a2, bw=10, delay='5ms', loss=1, max_queue_size=1000)
		self.addLink(a1, e1, bw=10, delay='5ms', loss=1, max_queue_size=1000)
		self.addLink(a1, e2, bw=10, delay='5ms', loss=1, max_queue_size=1000)
		self.addLink(a2, e3, bw=10, delay='5ms', loss=1, max_queue_size=1000)
		self.addLink(a2, e4, bw=10, delay='5ms', loss=1, max_queue_size=1000)
		self.addLink(e1, h1, bw=10, delay='5ms', loss=1, max_queue_size=1000)
		self.addLink(e1, h2, bw=10, delay='5ms', loss=1, max_queue_size=1000)
		self.addLink(e2, h3, bw=10, delay='5ms', loss=1, max_queue_size=1000)
		self.addLink(e2, h4, bw=10, delay='5ms', loss=1, max_queue_size=1000)
		self.addLink(e3, h5, bw=10, delay='5ms', loss=1, max_queue_size=1000)
		self.addLink(e3, h6, bw=10, delay='5ms', loss=1, max_queue_size=1000)
		self.addLink(e4, h7, bw=10, delay='5ms', loss=1, max_queue_size=1000)
		self.addLink(e4, h8, bw=10, delay='5ms', loss=1, max_queue_size=1000)


if __name__ == '__main__':
	topo = SingleSwitchTopo()
	net = Mininet(topo=topo, host = CPULimitedHost)
	net.start()
	net.pingAllFull()
	for h1 in net.hosts:
        	for h2 in net.hosts:
            		if h1 != h2:
                		net.iperf((h1, h2), l4Type='UDP')
	CLI( net )
	net.stop()
# ryu:

#ryu-manager --ofp-tcp-listen-port 6634 ryu.app.simple_switch_13

#Mininet:

#sudo mn --controller=remote,ip=127.0.0.1:6634 --switch=ovsk,protocols=OpenFlow13 --topo=linear,4
