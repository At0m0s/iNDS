import hashlib
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import json
import os
import sqlite3 as sqlite
import time

file_path = os.path.dirname(os.path.realpath(__file__))

# Create DB if it doesn't exist
con = sqlite.connect(file_path + '/bugs.sqlite')
cursor = con.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS bugs(Id INTEGER PRIMARY KEY, device TEXT, major TEXT, minor TEXT, isSystem INT, description TEXT, game TEXT, gameCode TEXT, save TEXT, image TEXT, date TEXT)")
con.commit()



class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
    
    def do_GET(self):
        self._set_headers()
        self.wfile.write("huh?")
    
    def do_HEAD(self):
        self._set_headers()
    
    def do_POST(self):
        # Create folders and DB
        if not os.path.exists(file_path + '/images'):
            os.makedirs(file_path + '/images')
        if not os.path.exists(file_path + '/saves'):
            os.makedirs(file_path + '/saves')
        
        # Doesn't do anything with posted data
        self._set_headers()
        content_len = int(self.headers.getheader('content-length', 0))
        print "Receiving post of length:", content_len / 1000000.0, "MB"
        post_body = self.rfile.read(content_len)
        jdata = json.loads(post_body)

        if (not "game" in jdata):
            jdata["game"] = ""
            jdata["gameCode"] = ""
        if ("save" in jdata):
            save = jdata["save"]
            saveHash = hashlib.sha1(save).hexdigest()
            f = open(file_path + '/saves/' + saveHash + '.dsv', 'w')
            f.write(save.decode('base64'))
            f.close()
            jdata["save"] = saveHash
        else:
            jdata["save"] = ""
        if ("image" in jdata):
            image = jdata["image"]
            imageHash = hashlib.sha1(image).hexdigest()
            f = open(file_path + '/images/' + imageHash + '.jpg', 'w')
            f.write(image.decode('base64'))
            f.close()
            jdata["image"] = imageHash
        else:
            jdata["image"] = ""
        
        cur = con.cursor()
        cur.execute("""INSERT INTO bugs 
                       (device, major, minor, isSystem, description, game, gameCode, save, image, date)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                       (jdata["device"], jdata["major"], jdata["minor"], jdata["isSystem"], jdata["description"],
                       jdata["game"], jdata["gameCode"], jdata["save"], jdata["image"], time.ctime()))
        

        print "Post Success"
        self.wfile.write('{"result": "success"}')
        con.commit()

def run(server_class=HTTPServer, handler_class=S, port=6768):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting server on port:', port
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv
    
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()