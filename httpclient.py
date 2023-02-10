#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

#References: 
# https://www.cs.unb.ca/~bremner/teaching/cs2613/books/python3-doc/library/urllib.parse.html
# https://docs.citrix.com/en-us/citrix-adc/current-release/appexpert/http-callout/http-request-response-notes-format.html
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        #get http type and code part then split it to get code
        code = int(data.split("\r\n")[0].split()[1])
        return code

    def get_headers(self,data):
        #use \r\n\r\n to split and get only header part
        header = data.split("\r\n\r\n")[0]
        return header

    def get_body(self, data):
        #use \r\n\r\n to split and get only body part
        body = data.split("\r\n\r\n")[1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    #split url to get host, port and path
    def manage_url(self, url):
        parse_url = urllib.parse.urlparse(url)
        #check if port is in url
        if ":" in parse_url.netloc:
            host, port = parse_url.netloc.split(":")
        else:
            host = parse_url.netloc8
            #check if https or http
            if parse_url.scheme == "https":
                port = 443
            elif parse_url.scheme == "http":
                port = 80
        #check if path is empty
        if parse_url.path == "":
            path = "/"
        else:
            path = parse_url.path

        return host, port, path

    def GET(self, url, args=None):
        code = 500
        body = ""
        host, port, path = self.manage_url(url)
        self.connect(host, int(port))

        #create request
        request = "GET " + path + " HTTP/1.1\r\n" + "Host: " + host + "\r\n" 
        request = request + "Accept: */*\r\n"
        request = request + "Accept-Language: en-US\r\n"
        request = request + "Accept-Encoding: gzip, deflate\r\n"
        request = request + "Connection: close\r\n\r\n"
        self.sendall(request)
        #get response
        data = self.recvall(self.socket)
        self.close()
        #split response to get code, header and body
        code = self.get_code(data)
        header = self.get_headers(data)
        body = self.get_body(data)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        host, port, path = self.manage_url(url)
        self.connect(host, int(port))
        #check if args is empty
        if args is not None:
            Info = urllib.parse.urlencode(args)
        else:
            Info = ""
        #create request POST version
        request = "POST " + path + " HTTP/1.1\r\n"
        request = request + "Host: " + host + "\r\n"
        request = request + "Content-Type: application/x-www-form-urlencoded\r\n"
        request = request + "Content-Length: " + str(len(Info)) + "\r\n"
        request = request + "Accept: */*\r\n"
        request = request + "Accept-Language: en-US\r\n"
        request = request + "Accept-Encoding: gzip, deflate\r\n"
        request = request + "Connection: close\r\n\r\n"
        request = request + Info
        self.sendall(request)
        #get response
        data = self.recvall(self.socket)
        self.close()
        #split response to get code, header and body
        code = self.get_code(data)
        header = self.get_headers(data)
        body = self.get_body(data)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
