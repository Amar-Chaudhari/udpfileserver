# TLEN 5330 Programming Assignment 1

## Objectives
- Learn Python UDP socket Programming
- Create client and server programs which can transfer content and messages over UDP socket

## Background
- In this assignement, I have used UDP sockets to transfer content and messages.
- The client and server programs run the infinite loop and client must send every command to server, the server then validates the command and replies with appropriate messages
- In general Unix/Linux enviornment, Sockets can not send data longer than `1500 Bytes`. Hence, there is need of reading files in chunks (<1450 Bytes) and transfer those chunks to the server.
- `Python2.7` does not require encoding/decoding and all files can be sent using the `rb` mode (read+binary) and written in the `wb` mode.
- UDP is a `connection-less` protocol, meaning there is no gurantee that packets will reach the destination. Although this is acceptable in some usecasses this can not be accepted in file-transfer as loss of packets will lead the file to be curropted/modified. This arrises need to implement some kind of acknowledge protocol over the UDP.

#### Chunking Process:
To overcome the limitation of message size in socket, file greater than 1500 bytes has to chuncked and trasfered.
- f.read(chunksize) - will return chunksize bytes from the file descriptor, return `None` at the `EOF`

#### Acknowledgment protocol
Client and server use stop-and-wait ARQ protocol.
- client append `0` to a message while sending.
- server will append `1` to reply message.
- if client receives `1` then send next packet.
- if client does not received `1` then stop

### Requirments
- Python 2.7
- Client Directory: `client`
- Server Directory: `server`

### Files included in the archive
- client.py (client program)
- server.py (server program)
- `client (directory)`
 - foo1.txt (29 bytes)
 - foo2.jpg (93 Kbytes)
 - foo3.aiff (1.2 MB audio file)
 - big.txt (6.5 MB)
- `server (directory)`

### How to run the programs
#### Server
```
python2.7 server.py 9000
```
#### Client
```
python2.7 client.py 127.0.0.1 9000
```
