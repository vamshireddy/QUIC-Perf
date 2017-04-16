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

def start_quic_experiment(net, outfile, filesize):
    server = net.get('m')
    client = net.get('h1')
    # Start the server.
    server.cmd("sudo sh ./run_quic_server.sh www &")
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

def start_tcp_experiment(net, outfile, filesize):
    server = net.get('m')
    client = net.get('h1')
    # Start the server.
    server.cmd("sudo ../../Dynamo/server &")
    sleep(5)
    # Start the client. 
    out = client.cmd("sudo sh ./monitor_and_start_tcp_client.sh %s %s %s"%(server.IP(), filesize, outfile))
    print out

def create_folder_if_not_exists(directory):
    print "Creating folder "+str(directory)
    if not os.path.exists(directory):
            os.makedirs(directory)

def plot_graph(infile1, infile2, outfile, title, bandwidth):
    print "sudo sh scripy.sh %s %s %s %s %s"%(infile1, infile2, outfile, title, bandwidth)
    os.system("cd tests;sh scripy.sh %s %s %s %s %s;cd .."%(infile1, infile2, outfile, title, bandwidth))

class MyTopo(Topo):
    def __init__(self, bw, delay, loss):    
        # Initialize topology
        Topo.__init__( self )
        bottleneck_link_config = {'bw': bw, 'delay': delay, 'loss': loss}
        access_link_config = {}
        switch = self.addSwitch('s1')
        server = self.addHost('m')
        client1 = self.addHost('h1')
        client2 = self.addHost('h2')

        self.addLink(switch, server, **bottleneck_link_config)
        self.addLink(switch, client1, **access_link_config)
        self.addLink(switch, client2, **access_link_config)

if len(sys.argv) != 5:
    print "Usage: sudo python filesize bandwidth latency loss"
    sys.exit(1)

filesize = int(sys.argv[1])
bandwidth = int(sys.argv[2])
latency = sys.argv[3]
loss = int(sys.argv[4])
print "Starting the test with latency: "+latency+" loss: "+str(loss)+" bw: "+str(bandwidth)+" filesize: "+str(filesize)

topo = MyTopo(bandwidth, latency, loss)
net = Mininet(topo=topo, link=TCLink, autoSetMacs=True)
net.start()
timestamp = time.time()
print "Timestamp :"+str(timestamp)
create_folder_if_not_exists("tests/outputdata/%sMB_%sMbps_%sms_%sloss"%(filesize, bandwidth, latency, loss))
create_folder_if_not_exists("tests/outputdata/%sMB_%sMbps_%sms_%sloss/%s"%(filesize, bandwidth, latency, loss, timestamp))
HOME = "tests/outputdata/%sMB_%sMbps_%sms_%sloss/%s/"%(filesize, bandwidth, latency, loss, timestamp)
SCRIPY_DIR = "outputdata/%sMB_%sMbps_%sms_%sloss/%s/"%(filesize, bandwidth, latency, loss, timestamp)
print "Home directory for tests: "+HOME
start_quic_experiment(net, HOME+'quic.txt', filesize)
start_tcp_experiment(net, HOME+'tcp.txt', filesize)
plot_graph(SCRIPY_DIR+'quic.txt', SCRIPY_DIR+'tcp.txt', SCRIPY_DIR+'graph.png', "%sMB_%sMbps_%sms_%sloss"%(filesize, bandwidth, latency, loss), bandwidth)
net.stop()
