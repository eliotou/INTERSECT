
from pox.core import core

import pox.openflow.libopenflow_01 as of

from pox.lib.util import dpidToStr

from pox.lib.addresses import IPAddr, EthAddr

from pox.lib.packet.arp import arp

from pox.lib.packet.ethernet import ethernet, ETHER_BROADCAST

from pox.lib.packet.packet_base import packet_base

from pox.lib.packet.packet_utils import *

import pox.lib.packet as pkt

from pox.lib.recoco import Timer

import time
from pox.openflow.of_json import *

 

log = core.getLogger()

input_pkts =0
output_pkts_s2= 0
output_pkts_s5= 0
packet_loss_rate=0


# we have 5 switches,which means 5 dpids

s1_dpid=0

s2_dpid=0

s3_dpid=0

s4_dpid=0

s5_dpid=0

 
s1_p1=0

s1_p2=0

s1_p3=0

s2_p1=0

s3_p1=0

s4_p1=0


pre_s1_p1=0

pre_s1_p2=0

pre_s1_p3=0

pre_s2_p1=0

pre_s3_p1=0

pre_s4_p1=0



def getTheTime():  #fuction to create a timestamp

  flock = time.localtime()

  then = "[%s-%s-%s" %(str(flock.tm_year),str(flock.tm_mon),str(flock.tm_mday))

 

  if int(flock.tm_hour)<10:

    hrs = "0%s" % (str(flock.tm_hour))

  else:

    hrs = str(flock.tm_hour)

  if int(flock.tm_min)<10:

    mins = "0%s" % (str(flock.tm_min))

  else:

    mins = str(flock.tm_min)

 

  if int(flock.tm_sec)<10:

    secs = "0%s" % (str(flock.tm_sec))

  else:

    secs = str(flock.tm_sec)

 

  then +="]%s.%s.%s" % (hrs,mins,secs)

  return then

 
# handler for timer function that sends the requests to all the
# switches connected to the controller.
 
def _timer_func ():

  global s1_dpid, s2_dpid, s3_dpid

  '''Now actually request flow stats from all switches
   While the system is running, the datapath may be queried about
  its current state using the OFPT_STATS_REQUEST message'''
  for connection in core.openflow._connections.values():
     #ofp_stats_request - Requesting statistics from switches, 
    #the .ofp attribute is a list of ofp_stats_reply messages.
      connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))    

      connection.send(of.ofp_stats_request(body=of.ofp_port_stats_request()))
 
       # Traffic to 10.0.0.2 should be sent out switch port 2 of s1

  print getTheTime(), "Packet Loss Rate  =", packet_loss_rate, "%"
  if  packet_loss_rate <= 2:  # packet_loss_rate <= 0:

      print getTheTime(), "send packets through s2 switch"

      msg = of.ofp_flow_mod() #flow_modification 
      #modify rules which strictly match wildcard values , modify the actions of existing entries
      msg.command=of.OFPFC_MODIFY_STRICT   

      msg.priority =100      

      msg.idle_timeout = 0

      msg.hard_timeout = 0

      msg.match.dl_type = 0x0800

      msg.match.nw_dst = "10.0.0.2"

      msg.actions.append(of.ofp_action_output(port = 2))
      #Send an OpenFlow message to a particular datapath - to s1 here
      core.openflow.sendToDPID(s1_dpid,msg)     
      return

  else:

      print getTheTime(), "change path-send packets through s3 switch"

      msg = of.ofp_flow_mod()
      # Modify entry strictly matching wildcards and priority
      msg.command = of.OFPFC_MODIFY_STRICT 

      msg.priority =100

      msg.idle_timeout = 0

      msg.hard_timeout = 0

      msg.match.dl_type = 0x0800

      msg.match.nw_dst = "10.0.0.2"

      msg.actions.append(of.ofp_action_output(port = 3))
     #Send an OpenFlow message to a particular datapath - to s1 here
      core.openflow.sendToDPID(s1_dpid,msg)  
      return



# structure of event.stats is defined by ofp_flow_stats()
def _handle_flowstats_received (event):

  global s1_dpid, s2_dpid, s3_dpid, s4_dpid, s5_dpid

  global s1_p1,s1_p2, s1_p3, s2_p1, s3_p1

  global pre_s1_p1,pre_s1_p2, pre_s1_p3, pre_s2_p1, pre_s3_p1

  global input_pkts, output_pkts_s2, output_pkts_s5,packet_loss_rate

  ''''print "FlowStatsReceived from %s: %s", dpidToStr(event.connection.dpid), event.stats
  stats : All of the individual stats bodies in a single list.
  the .stats attribute will contain a complete set of statistics (an array of ofp_flow_stats for FlowStatsReceived)
  the packet_count indicate the number of packets that were associated with this flow.
  This counter should behave like other statistic counters.'''
  for f in event.stats:
      if f.match.dl_type==0x0800 and f.match.nw_dst=="10.0.0.2" and event.connection.dpid==s1_dpid: 
        input_pkts = f.packet_count   
   
      if f.match.dl_type==0x0800 and event.connection.dpid==s2_dpid: 
        output_pkts_s2 = f.packet_count
      if f.match.dl_type==0x0800 and f.match.nw_dst=="10.0.0.2" and event.connection.dpid==s5_dpid: 
        output_pkts_s5 = f.packet_count
        #print getTheTime(), "output_pkts_s5 =", output_pkts_s5
        if input_pkts > 0 and output_pkts_s5 >0:
           packet_loss_rate = (input_pkts-output_pkts_s5)*1.0/input_pkts*100



def _handle_portstats_received (event):

  global s1_dpid, s2_dpid, s3_dpid, s4_dpid

  global s1_p1,s1_p2, s1_p3, s2_p1, s3_p1, s4_p1

  global pre_s1_p1, pre_s1_p2 , pre_s1_p3, pre_s2_p1, pre_s3_p1, pre_s4_p1


  if event.connection.dpid==s1_dpid:

    for f in event.stats:

      if int(f.port_no)<65534:

        if f.port_no==1:

          pre_s1_p1=s1_p1

          s1_p1=f.rx_packets #received packets in port 1 of switch 1


        if f.port_no==2:

          pre_s1_p2=s1_p2

          s1_p2=f.tx_packets #transmitted packets in port 2 of switch 1


        if f.port_no==3:

          pre_s1_p3=s1_p3

          s1_p3=f.tx_packets #transmitted packets in port 3 of switch 1
 

  if event.connection.dpid==s2_dpid:

     for f in event.stats:

       if int(f.port_no)<65534:

         if f.port_no==1:

           pre_s2_p1=s2_p1

           s2_p1=f.rx_packets  #received packets in switch 2, port 1

     print getTheTime(), "s1_p2(Sent):", (s1_p2-pre_s1_p2), "s2_p1(Received):", (s2_p1-pre_s2_p1)

 

  if event.connection.dpid==s3_dpid:

     for f in event.stats:

       if int(f.port_no)<65534:

         if f.port_no==1:

           pre_s3_p1=s3_p1

           s3_p1=f.rx_packets #received packets in switch 3 , port 1

     print getTheTime(), "s1_p3(Sent):", (s1_p3-pre_s1_p3), "s3_p1(Received):", (s3_p1-pre_s3_p1)    


  if event.connection.dpid==s4_dpid:

     for f in event.stats:

       if int(f.port_no)<65534:

         if f.port_no==1:

           pre_s4_p1=s4_p1

           s4_p1=f.rx_packets #received packets in switch 4 , port 1

     print getTheTime(), "s3_p1(Sent):", (s3_p1-pre_s3_p1), "s4_p1(Received):", (s4_p1-pre_s4_p1)  

#fired in response to the establishment of a new control channel with a switch
#the first sign that a connection exists


def _handle_ConnectionUp (event):   
  global s1_dpid, s2_dpid, s3_dpid, s4_dpid, s5_dpid 
  # A DPID is just a unique identifier for a switch - DataPath IDentifier

  print "ConnectionUp: ",dpidToStr(event.connection.dpid)


  for m in event.connection.features.ports:

    if m.name == "s1-eth1":

      s1_dpid = event.connection.dpid

      print "s1_dpid=", s1_dpid

    elif m.name == "s2-eth1":

      s2_dpid = event.connection.dpid

      print "s2_dpid=", s2_dpid

    elif m.name == "s3-eth1":

      s3_dpid = event.connection.dpid

      print "s3_dpid=", s3_dpid

    elif m.name == "s4-eth1":

      s4_dpid = event.connection.dpid

      print "s4_dpid=", s4_dpid

    elif m.name == "s5-eth1":

      s5_dpid = event.connection.dpid

      print "s5_dpid=", s5_dpid

 
  if s1_dpid<>0 and s2_dpid<>0 and s3_dpid<>0:

    Timer(1, _timer_func, recurring=True)   
    ''''after one second the rule is changed, every one second the function _timer_func is called 
    timeout -> Amount of time to wait before calling callback (absoluteTime = False),
    or specific time to call callback (absoluteTime = True)
    _timer_func ->a function to call when the timer elapses 
    recurring =True -> the timer fires every "timeToWake" seconds ,here every second'''
 

#OpenFlow messages are how Openflow switches communicate with controllers. 
#The messages are specified in the Openflow specification

def _handle_PacketIn(event):

  global s1_dpid, s2_dpid, s3_dpid, s4_dpid, s5_dpid
  packet=event.parsed


  if event.connection.dpid==s1_dpid:

     a=packet.find('arp')


     if a and a.protodst=="10.0.0.1":

       msg = of.ofp_packet_out(data=event.ofp)
      # ofp_packet_out -> sending packets from the switch 
      #(the main purpose of this message is to instruct a switch to send a packet.
       msg.actions.append(of.ofp_action_output(port=1))

       event.connection.send(msg)


     if a and a.protodst=="10.0.0.2":

       msg = of.ofp_packet_out(data=event.ofp)
       # Forward packets out of a physical or virtual port
       msg.actions.append(of.ofp_action_output(port=2)) 

       event.connection.send(msg)

 

     if a and a.protodst=="10.0.0.3":

       msg = of.ofp_packet_out(data=event.ofp)

       msg.actions.append(of.ofp_action_output(port=3))

       event.connection.send(msg)

     #Installing table entries for all switches

     #Traffic to 10.0.0.1 should be sent out switch port 1 of s1
     msg = of.ofp_flow_mod()

     msg.priority =100

     msg.idle_timeout = 0

     msg.hard_timeout = 0

     msg.match.dl_type = 0x0800

     msg.match.nw_dst = "10.0.0.1"

     msg.actions.append(of.ofp_action_output(port = 1))

     event.connection.send(msg)

 
     # Traffic to 10.0.0.2 should be sent out switch port 2 of s1

     msg = of.ofp_flow_mod()

     msg.priority =100

     msg.idle_timeout = 0

     msg.hard_timeout = 0

     msg.match.dl_type = 0x0800

     msg.match.nw_dst = "10.0.0.2"

     msg.actions.append(of.ofp_action_output(port = 2))

     event.connection.send(msg)

  
     # Traffic to 10.0.0.3 should be sent out switch port 3 of s1
     msg = of.ofp_flow_mod()

     msg.priority =100

     msg.idle_timeout = 0

     msg.hard_timeout = 0

     msg.match.dl_type = 0x0800

     msg.match.nw_dst = "10.0.0.3"

     msg.actions.append(of.ofp_action_output(port = 3))

     event.connection.send(msg)

 

  elif event.connection.dpid==s2_dpid: 

     msg = of.ofp_flow_mod()

     msg.priority =10

     msg.idle_timeout = 0

     msg.hard_timeout = 0

     msg.match.in_port = 1

     msg.match.dl_type=0x0806

     msg.actions.append(of.ofp_action_output(port = 2))

     event.connection.send(msg)

 

     msg = of.ofp_flow_mod()

     msg.priority =10

     msg.idle_timeout = 0

     msg.hard_timeout = 0

     msg.match.in_port = 1

     msg.match.dl_type=0x0800

     msg.actions.append(of.ofp_action_output(port = 2))

     event.connection.send(msg)

  

     msg = of.ofp_flow_mod()

     msg.priority =10

     msg.idle_timeout = 0

     msg.hard_timeout = 0

     msg.match.in_port = 2

     msg.match.dl_type=0x0806

     msg.actions.append(of.ofp_action_output(port = 1))

     event.connection.send(msg)

 

     msg = of.ofp_flow_mod()

     msg.priority =10

     msg.idle_timeout = 0

     msg.hard_timeout = 0

     msg.match.in_port = 2

     msg.match.dl_type=0x0800

     msg.actions.append(of.ofp_action_output(port = 1))

     event.connection.send(msg)




  elif event.connection.dpid==s3_dpid: 

     msg = of.ofp_flow_mod()

     msg.priority =10

     msg.idle_timeout = 0

     msg.hard_timeout = 0

     msg.match.in_port = 1

     msg.match.dl_type=0x0806

     msg.actions.append(of.ofp_action_output(port = 2))

     event.connection.send(msg)

 

     msg = of.ofp_flow_mod()

     msg.priority =10

     msg.idle_timeout = 0

     msg.hard_timeout = 0

     msg.match.in_port = 1

     msg.match.dl_type=0x0800

     msg.actions.append(of.ofp_action_output(port = 2))

     event.connection.send(msg)

  

     msg = of.ofp_flow_mod()

     msg.priority =10

     msg.idle_timeout = 0

     msg.hard_timeout = 0

     msg.match.in_port = 2

     msg.match.dl_type=0x0806

     msg.actions.append(of.ofp_action_output(port = 1))

     event.connection.send(msg)

 

     msg = of.ofp_flow_mod()

     msg.priority =10

     msg.idle_timeout = 0

     msg.hard_timeout = 0

     msg.match.in_port = 2

     msg.match.dl_type=0x0800

     msg.actions.append(of.ofp_action_output(port = 1))

     event.connection.send(msg)

  

  elif event.connection.dpid==s4_dpid: 

     msg = of.ofp_flow_mod()

     msg.priority =10

     msg.idle_timeout = 0

     msg.hard_timeout = 0

     msg.match.in_port = 1

     msg.match.dl_type=0x0806

     msg.actions.append(of.ofp_action_output(port = 2))

     event.connection.send(msg)

 

     msg = of.ofp_flow_mod()

     msg.priority =10

     msg.idle_timeout = 0

     msg.hard_timeout = 0

     msg.match.in_port = 1

     msg.match.dl_type=0x0800

     msg.actions.append(of.ofp_action_output(port = 2))

     event.connection.send(msg)

  

     msg = of.ofp_flow_mod()

     msg.priority =10

     msg.idle_timeout = 0

     msg.hard_timeout = 0

     msg.match.in_port = 2

     msg.match.dl_type=0x0806

     msg.actions.append(of.ofp_action_output(port = 1))

     event.connection.send(msg)

 

     msg = of.ofp_flow_mod()

     msg.priority =10

     msg.idle_timeout = 0

     msg.hard_timeout = 0

     msg.match.in_port = 2

     msg.match.dl_type=0x0800

     msg.actions.append(of.ofp_action_output(port = 1))

     event.connection.send(msg)

 

  elif event.connection.dpid==s5_dpid: 

     a=packet.find('arp')

     if a and a.protodst=="10.0.0.2":

       msg = of.ofp_packet_out(data=event.ofp)

       msg.actions.append(of.ofp_action_output(port=3))

       event.connection.send(msg)

 

     if a and a.protodst=="10.0.0.3":

       msg = of.ofp_packet_out(data=event.ofp)

       msg.actions.append(of.ofp_action_output(port=4))

       event.connection.send(msg)


 

     if a and a.protodst=="10.0.0.1":

       msg = of.ofp_packet_out(data=event.ofp)

       msg.actions.append(of.ofp_action_output(port=1))

       event.connection.send(msg)

 


     msg = of.ofp_flow_mod()

     msg.priority =100

     msg.idle_timeout = 0

     msg.hard_timeout = 0

     msg.match.dl_type = 0x0800

     msg.match.nw_dst = "10.0.0.1"

     msg.actions.append(of.ofp_action_output(port = 1))

     event.connection.send(msg)

 

     msg = of.ofp_flow_mod()

     msg.priority =10

     msg.idle_timeout = 0

     msg.hard_timeout = 0

     msg.match.in_port = 4

     msg.actions.append(of.ofp_action_output(port = 2))

     event.connection.send(msg)

 

     msg = of.ofp_flow_mod()

     msg.priority =100

     msg.idle_timeout = 0

     msg.hard_timeout = 0

     msg.match.dl_type = 0x0800

     msg.match.nw_dst = "10.0.0.1"

     msg.actions.append(of.ofp_action_output(port = 1))

     event.connection.send(msg)

 

     msg = of.ofp_flow_mod()

     msg.priority =100

     msg.idle_timeout = 0

     msg.hard_timeout = 0

     msg.match.dl_type = 0x0800

     msg.match.nw_dst = "10.0.0.2"

     msg.actions.append(of.ofp_action_output(port = 3))

     event.connection.send(msg)

 

     msg = of.ofp_flow_mod()

     msg.priority =100

     msg.idle_timeout = 0

     msg.hard_timeout = 0

     msg.match.dl_type = 0x0800

     msg.match.nw_dst = "10.0.0.3"

     msg.actions.append(of.ofp_action_output(port = 4))

     event.connection.send(msg)

#a launch function is a function that POX calls to tell the component to intialize itself. 
# The launch function is how commandline arguments are actually passed to the component
  
def launch ():  
  global start_time
 
  # FlowStatsReceived, listen for flow stats
  core.openflow.addListenerByName("FlowStatsReceived",_handle_flowstats_received) 
  # PortStatsReceived, listen for port stats
  core.openflow.addListenerByName("PortStatsReceived",_handle_portstats_received)

  core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)

  core.openflow.addListenerByName("PacketIn",_handle_PacketIn)
 
