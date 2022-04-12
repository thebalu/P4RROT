import socket
import struct

server_addr = ('192.168.11.1',5555)
s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

while True:
    op = input('operation (a(dd) / r(emove))> ')
    if op == 'a':
        a = int(input('a (uint32_t)> '))
    else:
        a = 0

    s.sendto(struct.Struct('!BI').pack(ord(op[0]),a),server_addr)
    r,_ = s.recvfrom(256)
    r_num = struct.Struct('!I?').unpack(r)[0]
    r_suc = struct.Struct('!I?').unpack(r)[1]
    print('Result:',r_num)
    print('Error:',r_suc)
    print()
