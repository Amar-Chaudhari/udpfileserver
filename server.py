#!/usr/bin/env python2.7

import os
import socket
import sys
from os import listdir

serverdir = 'server'
MAX_BYTES = 1500


def ShowMenu():
    data = """
Welcome to Amar's File Server
     list - list files
     get - get [filename]
     put - put [filename]
     exit - stop the server
     help - to display available commands
"""
    return data


# function to add delimiters to data
def packdata(data, seq):
    return str(seq) + "|||" + str(data)


# function to print list received from the server
def ListFiles(serverdir):
    return "\nServer Files:\n" + str('\n'.join(listdir(serverdir))+"\n")


# Main server function
# Function will exit on keyboardinterrupt or if timeout is received
# Default timeout is 10s
def server(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', port))
    print "Waiting on port:%d" % port

    try:

        while True:

            data, clientadd = s.recvfrom(MAX_BYTES)

            s_response = ""
            if data:
                seq, cmd, fdata = ExtractData(data)

                try:
                    mode = cmd.split()[0]
                except IndexError:
                    mode = ""
                # if user entered list command
                # return a List of files in server directory
                if mode == "list":
                    filelist = ListFiles(serverdir)
                    s_response = cmd + "|||" + filelist

                # if user entered get [filename] command
                # function checks if file exists in server directory
                # function will also send data in chunks of 1400 bytes
                elif mode == "get":
                    try:
                        fname = cmd.split()[1]
                        if CheckFileExists(fname, serverdir):


                                # In python2.7, 'rb' can be used for all formats
                                f2 = open((serverdir + "/" + fname), 'rb')

                                # By default program works in chunking
                                # chunkzise is 1400 bytes
                                while True:
                                    chunk = f2.read(1400)

                                    # chunk will be None at the end of file
                                    if chunk:
                                        tmp = ('|||', cmd, '|||', chunk)
                                    else:
                                        tmp = ('|||', cmd, '|||', 'EOF')
                                        f2.close()
                                    rseq = int(seq) + 1
                                    propmsg1 = str(rseq) + ''.join(tmp)
                                    s.sendto(propmsg1, clientadd)
                                    rcv_data, clientadd = s.recvfrom(MAX_BYTES)
                                    seq, cmd, fdata = ExtractData(rcv_data)

                                    # Send more data only if the clients as for it
                                    # if the cmd is anything but True then the get operation will stop
                                    if cmd != "True":
                                        break
                        else:
                            s_response = cmd + b'|||' + "File not present on the server"
                    except IndexError:
                        s_response = cmd + b'|||' + "File not present on the server"

                # if user entered get [filename] command
                # Function accepts chunks by default
                # Chunks are written to file as they are received.
                # Implemented stop-and-wait and no re-ordering is needed
                elif mode == "put":
                    fname = cmd.split()[1]

                    f = open(serverdir + "/" + fname, 'wb')
                    transfer = False
                    seq, cmd, fdata = ExtractData(data)

                    while True:
                        if fdata == 'EOF':
                            transfer = True
                            f.close()
                            break
                        f.write(fdata)
                        propmsg = str(int(seq) + 1) + b'|||' + "True"
                        s.sendto(propmsg, clientadd)
                        data, clientadd = s.recvfrom(MAX_BYTES)
                        seq, cmd, fdata = ExtractData(data)

                    if transfer:
                        s_response = "File sent"
                    else:
                        s_response = "Error in transfer"

                # If user entered exit command
                # System will exit gracefully
                elif mode == "exit":
                    s_response = cmd + b'|||' + "Bye"
                    propmsg = str(int(seq) + 1) + b'|||' + s_response
                    s.sendto(propmsg, clientadd)
                    sys.exit(0)

                # If user entered anything else than above command
                # Resent the command and error message
                elif mode.lower() == "hello" or mode.lower() == "help":
                    s_response = cmd + b'|||' + ShowMenu()
                else:
                    s_response = cmd + '|||' + cmd + " command not understood"

                propmsg = str(int(seq) + 1) + b'|||' + s_response
                #print propmsg
                s.sendto(propmsg, clientadd)
    except (KeyboardInterrupt):
        sys.exit(0)


def ExtractData(rcv_data):
    try:
        seq = rcv_data.split('|||')[0]
    except IndexError:
        seq = ""
    try:
        cmd = rcv_data.split('|||')[1]
    except IndexError:
        cmd = ""
    try:
        data = rcv_data.split('|||')[2]
    except IndexError:
        data = ""
    return seq, cmd, data


def ReadFile(fname):
    fp = open(serverdir + "/" + fname, 'rb')
    data = fp.read(MAX_BYTES)
    fp.close()
    return data


def CheckFileExists(fname, serverdir):
    try:

        check = os.path.exists(serverdir + "/" + fname)
        return check
    except:
        pass

    return False

def CheckServerDirectories():
    try:
        if os.path.isdir(serverdir):
            return True
        else:
            print "Server directoy not present\nCreating server directory"
            os.makedirs(serverdir)
            return True
    except:
        return False


if __name__ == "__main__":
    try:
        if len(sys.argv) == 2:
            if sys.argv[1].isdigit() and int(sys.argv[1]) > 5000 and int(sys.argv[1]) <= 65535:
                if CheckServerDirectories():
                    server(int(sys.argv[1]))
            else:
                print "5000<= Port Number <=65535 accepted"
                sys.exit(0)
    except AttributeError:
        sys.exit(0)
