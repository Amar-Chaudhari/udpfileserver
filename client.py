#!/usr/bin/env python2.7
import os
import socket
import sys

# Default Client Directory
# All file-server operation refers this directory
clientdir = 'client'

# Max size of socket to accept data
# 1500 Bytes
MAX_BYTES = 1500


# Main client function
# Function will exit on keyboardinterrupt or if socket error
def client(server_addr, port):
    try:
        rcv_data = send_data("hello", server_addr, port)
        cmd, fdata = ExtractData(rcv_data)
        if cmd == "hello":
            print fdata

        while 1:

                try:
                    data = raw_input("$ ")
                    if len(data) == 0:
                        data = ""
                    else:
                        cmd = data.split()[0]
                        if cmd == "list":
                            if len(data) > 4:
                                test = data.split()[1]
                                if test:
                                    print "Wrong Command\nget [filname]\nput [filename]\nlist"
                                    continue

                    if cmd == "get":

                        rcv_data = send_data(data, server_addr, port)

                        cmd, fdata = ExtractData(rcv_data)
                        fname = cmd.split()[1]
                        if "not present" in fdata:
                            print fdata
                        else:
                            transfer = False
                            f = open((clientdir + "/" + "received_" + fname), 'wb')
                            while True:
                                f.write(fdata)
                                rcv_data = send_data("True", server_addr, port)
                                cmd, fdata = ExtractData(rcv_data)
                                if fdata == 'EOF':
                                    transfer = True
                                    f.close()
                                    break
                            if transfer:
                                send_data("Done", server_addr, port)
                                print("File Received")
                            else:
                                send_data("Error", server_addr, port)

                    elif cmd == "put":
                        fname = data.split()[1].strip()
                        if CheckFileExists(fname):

                            f = open(clientdir + "/" + fname, 'rb')

                            while True:
                                chunk = f.read(1400)
                                if chunk:
                                    propmsg = data + b'|||' + chunk
                                else:
                                    propmsg = data + b'|||' + 'EOF'
                                rcv_data = send_data(propmsg, server_addr, port)
                                if rcv_data != "True":
                                    break

                            f.close()
                            if rcv_data:
                                print rcv_data
                        else:
                            print "File not found in client directory"

                    elif cmd == "exit":
                        rcv_data = send_data(data, server_addr, port)
                        # print rcv_data
                        cmd, reply = ExtractData(rcv_data)

                        if reply == "Bye":
                            sys.exit(0)
                    elif cmd == "list":
                        rcv_data = send_data(data, server_addr, port)
                        cmd, reply = ExtractData(rcv_data)
                        print reply
                    else:
                        rcv_data = send_data(data, server_addr, port)
                        cmd, reply = ExtractData(rcv_data)
                        print reply

                except EOFError:
                    data = ""
                except IndexError:
                    # Exception to handles wrong commands
                    # Example:
                    # get [space]
                    # put [space]
                    print "Wrong Command\nget [filname]\nput [filename]\nlist"

    except (KeyboardInterrupt, socket.error):
        sys.exit(0)


def ExtractData(rcv_data):
    try:
        cmd = rcv_data.split('|||')[0]
    except IndexError:
        cmd = ""
    try:
        data = rcv_data.split('|||')[1]
    except IndexError:
        data = ""
    return cmd, data


def send_data(data, server_addr, port):
    seq = 0
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        propmsg = str(seq) + '|||' + data
        s.sendto(propmsg, (server_addr, port))
        s.settimeout(10)
        data, svraddr = s.recvfrom(MAX_BYTES)
        if int(data.split('|||')[0]) == 1:
            s.close()
            return data.split('|||', 1)[1]
    except (socket.timeout,socket.error):
        print "Server is probably down"
        sys.exit(0)


def read_in_chunks(infile, chunk_size=MAX_BYTES):
    while True:
        chunk = infile.read(chunk_size)
        if chunk:
            yield chunk
        else:
            # The chunk was empty, which means we're at the end
            # of the file
            return


def FileWrite(fname, data):
    try:
        f = open(clientdir + "/Received-" + fname, 'wb')
        f.write(data)
        f.close()
    except:
        pass


def send_reliable_data(data, server_addr, port):
    delay = 2

    seq = 0
    propmsg = str(seq) + '|||' + data
    # print "Sending: %s" % propmsg
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(propmsg, (server_addr, port))

        s.settimeout(delay)

        try:

            data, svraddr = s.recvfrom(MAX_BYTES)
            if data:
                # ack_seq = int(data.split('|||')[0].strip())
                # recv_data = data.split('|||',1)[1].strip()
                recv_data = data.split('|||')[1].strip()

                if recv_data:
                    s.close()
                    return recv_data
        except socket.timeout:
            delay *= 2
            # yield print "Resending message %s" % propmsg
            s.sendto(propmsg, (server_addr, port))
            # delay = 0.2
            if delay >= 10:
                print "Probably server is down"
                return False


def ReadFile(fname):
    fp = open(clientdir + "/" + fname, 'rb')
    data = fp.read(MAX_BYTES)
    fp.close()
    return data


def CheckFileExists(fname):
    try:
        check = os.path.exists(clientdir + "/" + fname)
        return check
    except:
        pass

    return False

def CheckClientDirectories():
    try:
        if os.path.isdir(clientdir):
            return True
        else:
            return False
    except:
        return False

if __name__ == "__main__":
    try:
        if len(sys.argv) == 3:
            if sys.argv[2].isdigit():
                if CheckClientDirectories():
                    client(sys.argv[1], int(sys.argv[2]))
                else:
                    print "Client directory not found\nPlease create client directory and re-run the program"
                    sys.exit(0)
    except AttributeError:
        sys.exit(1)
