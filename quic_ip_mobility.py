from mininet.topo import Topo
from mininet.node import RemoteController
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from functools import partial
from mininet.util import dumpNodeConnections
from multiprocessing import Process
from mininet.log import lg, output
from time import sleep
import time
import sys
import os

def start_quic_experiment(net, outfile, filesize, server_outfile):
    server = net.get('h2')
    client = net.get('h1')

    # Start monitoring on the server.
    # Start the server.
    server.cmd("sudo sh ./monitor_and_start_quic_server.sh www %s &"%(server_outfile))
    sleep(5)

    # Start the client.
    if filesize == 10:
        print "Starting 10MB file download"
        out = client.cmd("sudo sh ./monitor_and_start_quic_client.sh %s %s %s"%(server.IP(), outfile, "https://mail.example.org/"))
    elif filesize == 100:
        print "Starting 100MB file download"
        out = client.cmd("sudo sh ./monitor_and_start_quic_client.sh %s %s %s"%(server.IP(), outfile, "https://www.example.org/"))
    else:
        print "File size not supported"
        sys.exit(1)
    print out

def create_folder_if_not_exists(directory):
    print "Creating folder "+str(directory)
    if not os.path.exists(directory):
        os.makedirs(directory)

def plot_graph(infile1, infile2, outfile, title, bandwidth):
    print "sudo sh scripy.sh %s %s %s %s %s"%(infile1, infile2, outfile, title, bandwidth)
    os.system("cd tests;sh scripy.sh %s %s %s %s %s;cd .."%(infile1, infile2, outfile, title, bandwidth))

""" This plot only one graph with measurements of TX """
def plot_graph_one_tx(infile, outfile, title, bandwidth):
    print "Plotting one graph TX of "+infile
    os.system("cd tests;sh scripy_one_graph_tx.sh %s %s %s %s;cd .."%(infile, outfile, title, bandwidth))

""" This plot only one graph with measurements of RX """
def plot_graph_one_rx(infile, outfile, title, bandwidth):
    print "Plotting one graph RX of "+infile
    os.system("cd tests;sh scripy_one_graph_rx.sh %s %s %s %s;cd .."%(infile, outfile, title, bandwidth))

class MyTopo(Topo):
    def __init__(self, bw, delay, loss):    
        # Initialize topology
        Topo.__init__( self )
        bottleneck_link_config = {'bw': bw, 'delay': delay, 'loss': loss}
        access_link_config = {}
        switch = self.addSwitch('s1')
        server = self.addHost('h2')
        client = self.addHost('h1')

        self.addLink(switch, server, **bottleneck_link_config)
        # Client has two interfaces connected to the switch. 
        self.addLink(switch, client, **access_link_config)
        self.addLink(switch, client, **access_link_config)

if len(sys.argv) != 7:
    print "Usage arguments: switchover_time switchback_time filesize bw latency loss"
    sys.exit(1)

switchover_time = int(sys.argv[1])
switchback_time = int(sys.argv[2])
filesize = int(sys.argv[3])
bandwidth = int(sys.argv[4])
latency = sys.argv[5]
loss = int(sys.argv[6])


print "Starting the IP mobility test."
print "IP address will be changed to a new one at "+sys.argv[1]
print "IP address will be changed back at "+sys.argv[2]

topo = MyTopo(bandwidth, latency, loss)
net = Mininet(topo=topo, link=TCLink, autoSetMacs=True)
net.start()
timestamp = time.time()
print "Timestamp :"+str(timestamp)
create_folder_if_not_exists("tests/outputdata/IPMobility_%sMB_%sMbps_%sms_%sloss"%(filesize, bandwidth, latency, loss))
create_folder_if_not_exists("tests/outputdata/IPMobility_%sMB_%sMbps_%sms_%sloss/%s"%(filesize, bandwidth, latency, loss, timestamp))
HOME = "tests/outputdata/IPMobility_%sMB_%sMbps_%sms_%sloss/%s/"%(filesize, bandwidth, latency, loss, timestamp)
SCRIPY_DIR = "outputdata/IPMobility_%sMB_%sMbps_%sms_%sloss/%s/"%(filesize, bandwidth, latency, loss, timestamp)
print "Home directory for tests: "+HOME
start_quic_experiment(net, HOME+'quic.txt', filesize, HOME+'server_quic.txt')
plot_graph(SCRIPY_DIR+'quic.txt', SCRIPY_DIR+'server_quic.txt', SCRIPY_DIR+'graph.png', "IPMobility_%sMB_%sMbps_%sms_%sloss"%(filesize, bandwidth, latency, loss), bandwidth)
plot_graph_one_tx(SCRIPY_DIR+'server_quic.txt', SCRIPY_DIR+'graph_server_tx.png', "Server TX", bandwidth)
net.stop()
