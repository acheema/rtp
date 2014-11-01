import sys
import getopt


import Checksum
import BasicSender

'''
This is a skeleton sender class. Create a fantastic transport protocol here.
'''

class Sender(BasicSender.BasicSender):

    def __init__(self, dest, port, filename, debug=False, sackMode=False):
        super(Sender, self).__init__(dest, port, filename, debug)
        self.sentPkts = {}
        self.ackPkts = {}
        self.globalseq = 0
        self.done = False
        #if sackMode:
            #raise NotImplementedError

    def start(self):
        msg_type = None
        sent_type = None
        while not self.done:
            while not len(self.sentPkts) >= 5 and sent_type != 'end':
                sent_type = self.send_data()
            response = self.receive(0.5)		
            print "recv: %s" % response
            #Using the handle_response from examples
            if Checksum.validate_checksum(response):
                ackSeqNum = int(float(self.split_packet(response)[1]))
                if ackSeqNum not in self.ackPkts:
                    self.ackPkts[ackSeqNum] = 0
                    self.handle_new_ack(ackSeqNum)
                else:
                    self.ackPkts[ackSeqNum] += 1
                    #fast retransmit
                    if self.ackPkts[ackSeqNum] == 3:
                        self.handle_dup_ack(ackSeqNum)
            if response == None:
                    self.handle_timeout()
        if len(self.sentPkts) == 0:
            self.done = True
        self.infile.close()

    def handle_timeout(self):
        for s in self.sentPkts:
            self.send(self.sentPkts[s])

    def handle_new_ack(self, ack):
        for s in self.sentPkts.keys():
            if s < ack:
                del self.sentPkts[s]
		del self.ackPkts[s]
        if not len(self.sentPkts) >= 5:
            msg_type = self.send_data()
            if msg_type == 'end':
                self.done = True

    def handle_dup_ack(self, ack):
	self.send(self.sentPkts[ack])

    def log(self, msg):
        if self.debug:
            print msg

    def send_data(self):
        msg = self.infile.read(1372)
        if self.globalseq == 0:
            msg_type = 'start'
        elif len(msg) == 0:
            msg_type = 'end'
            msg = ""
        else:
            msg_type = 'data'
        currseq = self.globalseq
        self.globalseq += 1
        packet = self.make_packet(msg_type, currseq, msg)
        self.ackPkts[currseq] = 0
        self.sentPkts[currseq] = packet
        self.send(packet)
        print "sent: %s|%d|%s|" % (msg_type, currseq, msg[:5])
        return msg_type

'''
This will be run if you run this script from the command line. You should not
change any of this; the grader may rely on the behavior here to test your
submission.
'''
if __name__ == "__main__":
    def usage():
        print "BEARS-TP Sender"
        print "-f FILE | --file=FILE The file to transfer; if empty reads from STDIN"
        print "-p PORT | --port=PORT The destination port, defaults to 33122"
        print "-a ADDRESS | --address=ADDRESS The receiver address or hostname, defaults to localhost"
        print "-d | --debug Print debug messages"
        print "-h | --help Print this usage message"
        print "-k | --sack Enable selective acknowledgement mode"

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                               "f:p:a:dk", ["file=", "port=", "address=", "debug=", "sack="])
    except:
        usage()
        exit()

    port = 33122
    dest = "localhost"
    filename = None
    debug = False
    sackMode = False

    for o,a in opts:
        if o in ("-f", "--file="):
            filename = a
        elif o in ("-p", "--port="):
            port = int(a)
        elif o in ("-a", "--address="):
            dest = a
        elif o in ("-d", "--debug="):
            debug = True
        elif o in ("-k", "--sack="):
            sackMode = True

    s = Sender(dest, port, filename, debug, sackMode)
    try:
        s.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
