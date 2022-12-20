#!/usr/bin/python

 

from mininet.topo import Topo

from mininet.net import Mininet

from mininet.node import CPULimitedHost

from mininet.link import TCLink

from mininet.util import dumpNodeConnections

from mininet.log import setLogLevel

from mininet.node import Controller 

from mininet.cli import CLI

from functools import partial

from mininet.node import RemoteController

import os

 
#the following program creates a topology with 5 switches and 3 hosts
class MyTopo(Topo):

    "Single switch connected to n hosts."

    def __init__(self):

        Topo.__init__(self)

        s1=self.addSwitch('s1')

        s2=self.addSwitch('s2')

        s3=self.addSwitch('s3')

        s4=self.addSwitch('s4')

        s5=self.addSwitch('s5') 

        h1=self.addHost('h1')

        h2=self.addHost('h2')

        h3=self.addHost('h3')


        self.addLink(h1, s1,bw=100,loss=0) 
        self.addLink(s1, s2,bw=100,loss=5) 
        self.addLink(s1, s3,bw=100,loss=0)
        self.addLink(s2, s5,bw=100,loss=0) 
        self.addLink(s3, s4,bw=100,loss=0)
        self.addLink(s4, s5,bw=100,loss=0)
        self.addLink(s5, h2,bw=100,loss=0)
        self.addLink(s5, h3,bw=100,loss=0)


  
def perfTest():

    "Create network and run simple performance test"

    topo = MyTopo()


    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink, controller=partial(RemoteController, ip='127.0.0.1', port=6633))

    net.start()

    print "Dumping host connections"

    dumpNodeConnections(net.hosts)

    h1,h2, h3=net.get('h1','h2','h3')

    h1.setMAC("0:0:0:0:0:1")

    h2.setMAC("0:0:0:0:0:2")

    h3.setMAC("0:0:0:0:0:3")



    CLI(net)

    net.stop()

 

if __name__ == '__main__':

    setLogLevel('info')

    perfTest()
