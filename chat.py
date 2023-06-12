import sys
import os
import json
import uuid
import logging
from queue import Queue
import threading
import socket
import base64
import traceback


class ServerToServerThread(threading.Thread):
    def __init__(self, chat, target_server, target_port):
        self.chat = chat
        self.target_server_address = target_server
        self.target_server_port = target_port
        self.queue = Queue()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        threading.Thread.__init__(self)

    def run(self):
        self.sock.connect((self.target_server_address, self.target_server_port))
        while True:
            while not self.queue.empty():
                msg = self.queue.get()
                self.sock.sendall(msg.encode())

    def put(self, msg):
        self.queue.put(msg)


class Chat:
    def __init__(self):
        self.sessions = {}
        self.users = {'messi': {'nama': 'Lionel Messi', 'negara': 'Argentina', 'password': 'surabaya', 'incoming': {},
                                'outgoing': {}},
                      'henderson': {'nama': 'Jordan Henderson', 'negara': 'Inggris', 'password': 'surabaya',
                                    'incoming': {}, 'outgoing': {}},
                      'lineker': {'nama': 'Gary Lineker', 'negara': 'Inggris', 'password': 'surabaya', 'incoming': {},
                                  'outgoing': {}},
                      'ronaldo': {'nama': 'Christiano Ronaldo', 'negara': 'Portugal', 'password': 'surabaya',
                                  'incoming': {}, 'outgoing': {}},
                      'maguire': {'nama': 'Harry Maguire', 'negara': 'Inggris', 'password': 'surabaya', 'incoming': {},
                                  'outgoing': {}}}
        self.servers = {'A': ServerToServerThread(self, '127.0.0.1', 8889),
                        'B': ServerToServerThread(self, '127.0.0.1', 9000),
                        'C': ServerToServerThread(self, '127.0.0.1', 9001)}
        self.running_servers = []
        self.groups = {'groupA': ['messi@A', 'lineker@A', 'maguire@A'],
                       'groupB': ['messi@A', 'lineker@B', 'maguire@B'],
                       'groupC': ['messi@A', 'ronaldo@A', 'henderson@B']}

    def proses(self, data):
        j = data.split(" ")
        try:
            command = j[0].strip()
            if command == 'auth':
                username = j[1].strip()
                password = j[2].strip()
                logging.warning("AUTH: auth {} {}".format(username, password))
                return self.autentikasi_user(username, password)
            elif command == 'register':
                username = j[1].strip()
                password = j[2].strip()
                return self.register_user(username, password)
            elif command == 'logout':
                tokenid = j[1].strip()
                return self.logout(tokenid)
            elif command == 'send':
                sessionid = j[1].strip()
                usernameto = j[2].strip()
                message = ""
                for w in j[3:]:
                    message = "{} {}".format(message, w)
                usernamefrom = self.sessions[sessionid]['username']
                logging.warning(
                    "SEND: session {} send message from {} to {}".format(sessionid, usernamefrom, usernameto))
                return self.send_message(sessionid, usernamefrom, usernameto, message)
            elif command == 'inbox':
                sessionid = j[1].strip()
                username = self.sessions[sessionid]['username']
                logging.warning("INBOX: {}".format(sessionid))
                return self.get_inbox(username)
            elif command == 'sendgroup':
                sessionid = j[1].strip()
                group_id = j[2].strip()
                server_from = j[3].strip()
                message = ""
                for w in j[4:]:
                    message = "{} {}".format(message, w)
                usernamefrom = self.sessions[sessionid]['username']
                logging.warning("SEND: session {} sent message from {} to {}".format(sessionid, usernamefrom, group_id))
                return self.send_group_message(sessionid, usernamefrom, group_id, server_from, message)
            elif command == 'connect':
                server_id = j[1].strip()
                return self.connect(server_id)
            elif command == 'addserver':
                server_id = j[1].strip()
                server_ip = j[2].strip()
                server_port = int(j[3].strip())
                return self.add_server(server_id, server_ip, server_port)
            elif command == 'sendserver':
                sessionid = j[1].strip()
                server_id = j[2].strip()
                usernameto = j[3].strip()
                message = ""
                for w in j[4:]:
                    message = "{} {}".format(message, w)
                logging.warning("SendServer: session {} sent message from {} to {}@{}".format(sessionid,
                                                                                              self.sessions[
                                                                                                  sessionid][
                                                                                                  'username'],
                                                                                              usernameto,
                                                                                              server_id))
                return self.send_to_other_server(sessionid, server_id, usernameto, message)
            elif command == 'server_inbox':
                username_from = j[1].strip()
                username_to = j[2].strip()
                message = ""
                for w in j[3:]:
                    message = "{} {}".format(message, w)
                return self.server_inbox(username_from, username_to, message)
            elif command == 'sendfile':
                sessionid = j[1].strip()
                address = j[2].strip()
                filename = j[3].strip()
                address_split = address.split('@')
                username_to = address_split[0].strip()
                server_id = address_split[1].strip()
                return self.send_file(sessionid, username_to, server_id, filename)
            elif command == 'sendfilegroup':
                sessionid = j[1].strip()
                groupid = j[2].strip()
                filename = j[3].strip()
                return self.send_file_group(sessionid, groupid, filename)
            elif command == 'creategroup':
                group_id = j[1].strip()
                members = j[2].strip()
                return self.create_group(group_id, members)
            else:
                return {'status': 'ERROR', 'message': '**Protocol Tidak Benar'}
        except KeyError:
            return {'status': 'ERROR', 'message': 'Informasi tidak ditemukan'}
        except IndexError:
            return {'status': 'ERROR', 'message': '--Protocol Tidak Benar'}

    def autentikasi_user(self, username, password):
        if username not in self.users:
            return {'status': 'ERROR', 'message': 'User Tidak Ada'}
        if self.users[username]['password'] != password:
            return {'status': 'ERROR', 'message': 'Password Salah'}
        tokenid = str(uuid.uuid4())
        self.sessions[tokenid] = {'username': username, 'userdetail': self.users[username]}
        return {'status': 'OK', 'tokenid': tokenid}

    def register_user(self, username, password):
        if username in self.users:
            return {'status': 'ERROR', 'message': 'User Sudah Ada'}
        self.users[username] = {'nama': username, 'negara': 'Inggris', 'password': password, 'incoming': {},
                                'outgoing': {}}
        os.chdir('files/')
        os.mkdir(username)
        os.chdir('../')
        return {'status': 'OK', 'message': 'user registered'}

    def logout(self, tokenid):
        if tokenid in self.sessions:
            del self.sessions[tokenid]
            return {'status': 'OK', 'message': "User logged out"}
        else:
            return {'status': 'ERROR', 'message': "Session not found"}

    def get_user(self, username):
        if username not in self.users:
            return False
        return self.users[username]

    def connect(self, server_id):
        if server_id in self.running_servers:
            return {'status': 'ERROR', 'message': 'Server {} is already connected'.format(server_id)}
        else:
            try:
                self.servers[server_id].start()
                self.running_servers.append(server_id)
                return {'status': 'OK'}
            except:
                trace = traceback.format_exc()
                return {'status': 'ERROR', 'message': trace}

    def add_server(self, server_id, server_ip, server_port):
        if server_id in self.servers:
            return {'status': 'ERROR', 'message': 'Server {} is already exist'.format(server_id)}

        self.servers[server_id] = ServerToServerThread(self, server_ip, server_port)
        return {'status': 'OK'}

    def send_message(self, sessionid, username_from, username_dest, message):
        if sessionid not in self.sessions:
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        s_fr = self.get_user(username_from)
        s_to = self.get_user(username_dest)

        if s_fr is False or s_to is False:
            return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}

        message = {'msg_from': s_fr['nama'], 'msg_to': s_to['nama'], 'msg': message}
        outqueue_sender = s_fr['outgoing']
        inqueue_receiver = s_to['incoming']
        try:
            outqueue_sender[username_from].put(message)
        except KeyError:
            outqueue_sender[username_from] = Queue()
            outqueue_sender[username_from].put(message)
        try:
            inqueue_receiver[username_from].put(message)
        except KeyError:
            inqueue_receiver[username_from] = Queue()
            inqueue_receiver[username_from].put(message)
        return {'status': 'OK', 'message': 'Message Sent'}

    def send_group_message(self, sessionid, username_from, group_id, server_from, message):
        if sessionid not in self.sessions:
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        if group_id not in self.groups:
            return {'status': 'ERROR', 'message': 'Group Tidak Ditemukan'}
        s_fr = self.get_user(username_from)
        if s_fr is False:
            return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}
        if username_from + '@' + server_from not in self.groups[group_id]:
            return {'status': 'ERROR', 'message': 'User Tidak Ada dalam {}'.format(group_id)}
        sent_id = []

        for member in self.groups[group_id]:
            address = member.split("@")
            username_to = address[0].strip()
            server_to = address[1].strip()
            s_to = self.get_user(username_to)
            if s_to is False or server_to not in self.servers or s_to is s_fr:
                continue
            if server_to == server_from:
                self.send_message(sessionid, username_from, username_to, message)
                sent_id.append(username_to)
            else:
                self.send_to_other_server(sessionid, server_to, username_to, message)
                sent_id.append(s_to['nama'])

        return {'status': 'OK', 'message': 'Message Sent to {} in {}'.format(', '.join(sent_id), group_id)}

    def get_inbox(self, username):
        s_fr = self.get_user(username)
        incoming = s_fr['incoming']
        msgs = {}
        for users in incoming:
            msgs[users] = []
            while not incoming[users].empty():
                msgs[users].append(s_fr['incoming'][users].get_nowait())
        return {'status': 'OK', 'messages': msgs}

    def server_inbox(self, username_from, username_to, message):
        s_fr = self.get_user(username_from)
        s_to = self.get_user(username_to)
        if s_fr == False or s_to == False:
            return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}
        message = {'msg_from': s_fr['nama'], 'msg_to': s_to['nama'], 'msg': message}
        outqueue_sender = s_fr['outgoing']
        inqueue_receiver = s_to['incoming']
        try:
            outqueue_sender[username_from].put(message)
        except KeyError:
            outqueue_sender[username_from] = Queue()
            outqueue_sender[username_from].put(message)
        try:
            inqueue_receiver[username_from].put(message)
        except KeyError:
            inqueue_receiver[username_from] = Queue()
            inqueue_receiver[username_from].put(message)
        return {'status': 'OK', 'message': 'Message Sent'}

    def send_to_other_server(self, sessionid, server_id, username_to, message):
        if sessionid not in self.sessions:
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        if server_id not in self.servers:
            return {'status': 'ERROR', 'message': 'Server Tidak Ada'}
        username_from = self.sessions[sessionid]['username']
        self.servers[server_id].put('server_inbox {} {} {}'.format(username_from, username_to, message))
        return {'status': 'OK', 'message': 'Message Sent to Server'}

    def send_file(self, sessionid, username_to, server_id, filename):
        if sessionid not in self.sessions:
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        if username_to not in self.users:
            return {'status': 'ERROR', 'message': 'User Tujuan Tidak Ditemukan'}
        if server_id not in self.servers:
            return {'status': 'ERROR', 'message': 'Server Tidak Ada'}
        username_from = self.sessions[sessionid]['username']
        path_from = 'files/' + username_from + '/'
        path_to = '../' + username_to + '/'
        print(os.path.abspath(path_from))
        os.chdir(path_from)

        if os.path.exists(filename):
            fp = open(f"{filename}", 'rb')
            isi_file = fp.read()
            fp.close()
            os.chdir(path_to)
            if os.path.exists(f"{filename}"):
                os.chdir('../../')
                return {'status': 'ERROR', 'message': 'File sudah ada di user {}'.format(username_to)}
            fp_new = open(filename, 'wb+')
            fp_new.write(isi_file)
            fp_new.close()
            os.chdir('../../')
            return {'status': 'OK', 'message': 'File terkirim'}
        else:
            os.chdir('../../')
            return {'status': 'ERROR', 'message': 'File tidak ada'}

    def send_file_group(self, sessionid, groupid, filename):
        if sessionid not in self.sessions:
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        if groupid not in self.groups:
            return {'status': 'ERROR', 'message': 'Group Tidak Ditemukan'}

        username_from = self.sessions[sessionid]['username']
        path_from = 'files/' + username_from + '/'

        for member in self.groups[groupid]:
            address = member.split("@")
            username_to = address[0].strip()
            if username_from == username_to:
                continue
            server_to = address[1].strip()
            path_to = '../' + username_to + '/'
            print(os.path.abspath(path_from))
            os.chdir(path_from)

            if os.path.exists(filename):
                fp = open(f"{filename}", 'rb')
                isi_file = fp.read()
                fp.close()
                os.chdir(path_to)
                if os.path.exists(f"{filename}"):
                    os.chdir('../../')
                    return {'status': 'ERROR', 'message': 'File sudah ada di user {}'.format(username_to)}
                fp_new = open(filename, 'wb+')
                fp_new.write(isi_file)
                fp_new.close()
                os.chdir('../../')
            else:
                os.chdir('../../')
                return {'status': 'ERROR', 'message': 'File tidak ada'}
        return {'status': 'OK', 'message': 'File terkirim ke group {}'.format(groupid)}

    def create_group(self, group_id, members):
        if group_id in self.groups:
            return {'status': 'ERROR', 'message': 'Group {} sudah ada'.format(group_id)}
        self.groups[group_id] = []
        user_member = members.split(',')
        for user in user_member:
            if user not in self.groups[group_id]:
                self.groups[group_id].append(user)

        return {'status': 'OK', 'message': 'Group {} dibuat'.format(group_id)}


if __name__ == "__main__":
    j = Chat()
