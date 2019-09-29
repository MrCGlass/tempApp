from kmip.services.server import KmipServer
from OpenSSL import crypto
import os,json,sqlite3 as sql
import base64,socket


name = {'C':'US','ST':'GA','L':'Atlanta','O':
        'COLLECTIVE COMMUNITY INVESTMENTS',
        'OU':'MEDIA AND SOFTWARE','CN':'CCINVESTMENTS','emailAddress':'comminvestinc@outlook.com'}

def createCertificate(req,pkey,*args,digest='sha256'):

    cert = crypto.X509()
    cert.set_serial_number(serial)
    cert.gmtime_adj_notBefore(notBefore)
    cert.gmtime_adj_notAfter(notAfter)
    cert.set_issuer(req.get_subject())
    cert.set_subject(req.get_subject())
    cert.set_pubkey(req.get_pubkey())
    cert.sign(pkey,digest)
    return cert

def createKeyPair(type,bits):
    pkey = crypto.PKey()
    pkey.generate_key(type,bits)
    return pkey

def createRequest(pkey,digest='md5',**name):
    req = crypto.X509Req()
    subj = req.get_subject()
    for key,value in name.items():
        for key in value:
            val = value[key]
            setattr(subj,key,val)
        
    req.set_pubkey(pkey)
    req.sign(pkey,digest)
    return req,pkey
    
    
notBefore=1
notAfter= 0
serial= 1
key_pair = createKeyPair(crypto.TYPE_RSA,2048)
private_key = key_pair.to_cryptography_key()
pub_key= private_key.public_key()
print(dir(pub_key))
cert = createCertificate(*createRequest(key_pair,name=name),
                             notBefore,notAfter,serial)
try:
    os.chdir(os.getcwd()+'\configfiles')
    server_file = open('certfile.pem','wb')
    key_file = open('keypairfile.pem','wb')
    key_cert = cert.to_cryptography()

    key_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM,key_pair))
    server_file.write(crypto.dump_certificate(crypto.FILETYPE_PEM,key_cert))
    
    server_file.close()
    key_file.close()
    
except Exception as e:
    print(e)
finally:
    pass

class keymanager(KmipServer):
    __key_safe = []
    _socket = socket.socket(family=socket.AF_INET)
    def __init__(self,*args,**kwargs):
        super(keymanager,self).__init__(*args,**kwargs)
        
    






if __name__=='__main__':
    manager = keymanager(
                         config_path=os.getcwd() +'/server.conf', 
                         )
    manager.start()
    manager.serve()

    
