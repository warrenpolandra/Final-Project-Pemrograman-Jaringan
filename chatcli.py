import socket
import os
import sys
import json

TARGET_IP = "127.0.0.1"


class ChatClient:
    def __init__(self, server):
        self.server = server
        self.portnumber = 8889
        if server == 'A':
            self.portnumber = 8889
        elif server == 'B':
            self.portnumber = 9000
        elif server == 'C':
            self.portnumber = 9001
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (TARGET_IP, self.portnumber)
        self.sock.connect(self.server_address)
        self.tokenid = ""

    def proses(self, cmdline):
        j = cmdline.split(" ")
        try:
            command = j[0].strip()
            if command == 'auth':
                username = j[1].strip()
                password = j[2].strip()
                return self.login(username, password)
            elif command == 'connect':
                server_id = j[1].strip()
                return self.connect(server_id)
            elif command == 'logout':
                return self.logout()
            elif command == 'addserver':
                server_id = j[1].strip()
                server_ip = j[2].strip()
                server_port = int(j[3].strip())
                return self.add_server(server_id, server_ip, server_port)
            elif command == 'send':
                address = j[1].strip().split('@')
                usernameto = address[0].strip()
                serverto = address[1].strip()
                message = ""
                for w in j[2:]:
                    message = "{} {}".format(message, w)
                if serverto == self.server:
                    return self.send_message(usernameto, message)
                else:
                    return self.send_message_to_server(serverto, usernameto, message)
            elif command == 'sendgroup':
                group_id = j[1].strip()
                message = ""
                for w in j[2:]:
                    message = "{} {}" . format(message, w)
                return self.sendgroupmessage(group_id, message)
            elif command == 'sendfile':
                address = j[1].strip()
                filename = j[2].strip()
                return self.send_file(address, filename)
            elif command == 'sendfilegroup':
                groupid = j[1].strip()
                filename = j[2].strip()
                return self.send_file_group(groupid, filename)
            elif command == 'inbox':
                return self.inbox()
            elif command == 'register':
                username = j[1].strip()
                password = j[2].strip()
                return self.register(username, password)
            elif command == 'creategroup':
                group_id = j[1].strip()
                group_members = j[2].strip()
                return self.create_group(group_id, group_members)
            else:
                return "*Maaf, command tidak benar"
        except IndexError:
            return "-Maaf, command tidak benar"

    def sendstring(self, string):
        try:
            self.sock.sendall(string.encode())
            receivemsg = ""
            while True:
                data = self.sock.recv(64)
                if data:
                    # data harus didecode agar dapat di operasikan dalam bentuk string
                    receivemsg = "{}{}" . format(receivemsg, data.decode())
                    if receivemsg[-4:] == '\r\n\r\n':
                        return json.loads(receivemsg)
        except:
            self.sock.close()
            return {'status': 'ERROR', 'message': 'Gagal'}

    def register(self, username, password):
        message = "register {} {}\r\n".format(username, password)
        result = self.sendstring(message)
        if result['status'] == 'OK':
            return 'User {} succesfully registered'.format(username)
        else:
            return 'Error: {}'.format(result['message'])

    def login(self, username, password):
        if self.tokenid != '':
            return "Error: another user already logged in"
        string = "auth {} {} \r\n" . format(username, password)
        result = self.sendstring(string)
        if result['status'] == 'OK':
            self.tokenid = result['tokenid']
            return "username {} logged in, token {} " .format(username, self.tokenid)
        else:
            return "Error: {}" . format(result['message'])

    def logout(self):
        string = "logout {}\r\n".format(self.tokenid)
        result = self.sendstring(string)
        if result['status'] == 'OK':
            self.tokenid = ''
            return "Logged out"
        else:
            return "Error: {}".format(result['message'])

    def connect(self, server_id):
        if self.tokenid == "":
            return "Error, not authorized"
        message = "connect {} \r\n".format(server_id)
        result = self.sendstring(message)
        if result['status'] == 'OK':
            return 'Server {} succesfully connected'.format(server_id)
        else:
            return "Error: {}".format(result['message'])

    def add_server(self, server_id, server_ip, server_port):
        if self.tokenid == "":
            return "Error: not authorized"
        string = "addserver {} {} {}\r\n".format(server_id, server_ip, server_port)
        result = self.sendstring(string)
        if result['status'] == 'OK':
            return "Server {}:{} added with id: {}".format(server_ip, server_port, server_id)
        else:
            return "Error: {}".format(result['message'])

    def send_message(self, usernameto="xxx", message="xxx"):
        if self.tokenid == "":
            return "Error: not authorized"
        string = "send {} {} {}\r\n" . format(
            self.tokenid, usernameto, message)
        result = self.sendstring(string)
        if result['status'] == 'OK':
            return "message sent to {}" . format(usernameto)
        else:
            return "Error: {}" . format(result['message'])

    def send_message_to_server(self, serverid, usernameto, message):
        if self.tokenid == "":
            return "Error, not authorized"
        string = "sendserver {} {} {} {}\r\n".format(self.tokenid, serverid, usernameto, message)
        result = self.sendstring(string)
        if result['status'] == 'OK':
            return "Message sent to server {}".format(serverid)
        else:
            return "Error: {}".format(result['message'])
        
    # def send_message_to_server_ngrox(self, serverid, usernameto, message):
    #     if self.tokenid == "":
    #         return "Error, not authorized"
    #     string = "sendserver {} {} {} {}\r\n".format(self.tokenid, serverid, usernameto, message)
    #     result = self.sendstring(string)
    #     if result['status'] == 'OK':
    #         return "Message sent to server {}".format(serverid)
    #     else:
    #         return "Error: {}".format(result['message'])

    def inbox(self):
        if self.tokenid == "":
            return "Error, not authorized"

        string = "inbox {}\r\n".format(self.tokenid)
        result = self.sendstring(string)

        if result['status'] == 'OK':
            formatted_string = ""

            for sender, messages in result['messages'].items():
                for message in messages:
                    formatted_message = message["msg"].replace("\r\n", "").strip()
                    formatted_string += f"{sender}: {formatted_message}\n"

            return "{}".format(formatted_string)
        else:
            return "Error: {}".format(result['message'])

    def sendgroupmessage(self, group_id="xxx", message="xxx"):
        if self.tokenid == "":
            return "Error: not authorized"
        string = "sendgroup {} {} {} {}\r\n" . format(self.tokenid, group_id, self.server, message)
        result = self.sendstring(string)
        if result['status'] == 'OK':
            return "Message sent to {}" . format(group_id)
        else:
            return "Error: {}" . format(result['message'])

    def send_file(self, address, filename):
        if self.tokenid == "":
            return "Error: not authorized"
        string = "sendfile {} {} {}\r\n" . format(self.tokenid, address, filename)
        result = self.sendstring(string)
        if result['status'] == 'OK':
            return 'File {} sent to {}'.format(filename, address)
        else:
            return 'Error: {}'.format(result['message'])

    def send_file_group(self, group_id, filename):
        if self.tokenid == "":
            return "Error: not authorized"
        string = "sendfilegroup {} {} {}\r\n".format(self.tokenid, group_id, filename)
        result = self.sendstring(string)
        if result['status'] == 'OK':
            return 'File {} sent to group {}'.format(filename, group_id)
        else:
            return 'Error: {}'.format(result['message'])

    def create_group(self, group_id, members):
        if self.tokenid == "":
            return "Error: not authorized"
        string = "creategroup {} {}\r\n".format(group_id, members)
        result = self.sendstring(string)
        if result['status'] == 'OK':
            return 'Group {} created with member: {}'.format(group_id, members)
        else:
            return 'Error: {}'.format(result['message'])


if __name__ == "__main__":
    server = 'A'
    try:
        server = sys.argv[1]
    except:
        pass

    if server != 'A' and server != 'B' and server != 'C':
        print("Server tidak ada!")
        sys.exit()

    cc = ChatClient(server)
    while True:
        cmdline = input("\nCommand: ")
        print(cc.proses(cmdline))
