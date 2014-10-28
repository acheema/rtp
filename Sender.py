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
        if sackMode:
            raise NotImplementedError #remove this line when you implement SACK
    
    def start(self):
        seqnum = 0
        sentPkts = []
        ackPkts = []
        msgIter = self.infile.read(1400)
        msg_type = 'start'
        while not msg_type == 'end':
            packet = self.make_packet(msg_type,seqnum,msgIter)
            sentPkts.append(seqnum)
            self.send(packet)
            #print "--------------------------------------------------------"
            print "sent: %s|%d|%s|" % (msg_type, seqnum, msgIter[:5])
            
            response = self.receive(.5)
            #ackPkts.append(int(float(self.split_packet(response)[1])))
            if self.handle_response(response):
                next_msg = self.infile.read(1400)
                msg_type = 'data'
                if next_msg == "":
                    msg_type = 'end'
                msgIter = next_msg
                seqnum += 1
            else:
                continue
        #print sentPkts
        #print ackPkts
        self.infile.close()
        
    #This kind of takes care of corruption
    def handle_response(self,response_packet):
        if Checksum.validate_checksum(response_packet):
            print "recv: %s" % response_packet
            #print "--------------------------------------------------------"
            return True
        else:
            print "recv: %s <--- CHECKSUM FAILED" % response_packet
            #print "--------------------------------------------------------"
            return False

    def handle_timeout(self):
        pass

    def handle_new_ack(self, ack):
        pass

    def handle_dup_ack(self, ack):
        pass

    def log(self, msg):
        if self.debug:
            print msg


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
