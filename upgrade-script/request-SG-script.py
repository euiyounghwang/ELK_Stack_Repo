
import requests
from requests.auth import HTTPBasicAuth
import json
from elasticsearch import Elasticsearch, exceptions
import os 
from dotenv import load_dotenv
import sys
import warnings
warnings.filterwarnings("ignore")


''' pip install python-dotenv'''
load_dotenv() # will search for .env file in local folder and load variables 

INDEX = "om_test"
ca_cert_path = './upgrade-script\certs\qa13_new\qa13-es8-ca.pem'
# ca_cert_path = './upgrade-script/certs/dev/root-ca.pem'

''' https://restfulapi.net/http-status-codes/ '''
http_status_code = {
    200 : 'Indicates that the request has succeeded.',
    201 : 'Indicates that the request has succeeded and a new resource has been created as a result.',
    400 : 'The server could not understand the request due to incorrect syntax. The client should NOT repeat the request without modifications.',
    401 : 'Unauthorized rquests. Insufficient permissions',
    403 : 'Unauthorized request. Insufficient permissions. The client does not have access rights to the content. ',
    500 : 'The server encountered an unexpected condition that prevented it from fulfilling the request.'
}

def get_headers(auth):
    ''' Basic Auth with ssl certification'''
    header =  {
            'Content-type': 'application/json', 
            'Authorization' : '{}'.format(os.getenv(auth)),
            'Connection': 'close'
    }

    return header


def es_client_certificates():
    '''
    verify if the request with ssl works via es_client library
    '''
    
    ''' The verify_certs=False disables the underlying Python SSL modules from verifying the self-signed certs, '''
    ''' You can configure the client to use SSL for connecting to your elasticsearch cluster,'''
    '''
    * root ca : Root CA (Certificate Authority) is a certificate that will be used to sign all other certificates within a system. 
    In other words, Root CA is an issuer of node, client and admin certificates. 
    * Node certificates : used to identify and secure traffic between Elasticsearch nodes on the transport layer
    * Client certificates: used to identify Elasticsearch clients on the REST and transport layer.

    '''
    ''' root-ca.pem - the root certificate 
        root-ca-key.pem - the private key for the root certificate
        node.pem - the node certificate
        node-key.pem - the private key for the node certificate
        admin.pem - the admin certificate
        admin-key.pem - the private key for the admin certificate
    '''
    ''' We are using Elasticsearch 8.12.0 with self-signed certs in SG'''
    ''' https://stackoverflow.com/questions/61961725/how-to-connect-to-elasticsearch-with-python-using-ssl'''

    """ raise HTTP_EXCEPTIONS.get(status_code, TransportError)(elasticsearch.exceptions.AuthenticationException: AuthenticationException(401, 'Unauthorized') without header"""
    ''' There should be an option to disable certificate verification during SSL connection. It will simplify developing and debugging process. '''

    try:
        
        print('\n')
        print('*'*10)
        print(sys._getframe().f_code.co_name)
        print('*'*10)
        print('\n')

        ''' To disable certificate verification, at the client side, one can use verify attribute.  -- Verify False'''
        ''' one can also pass the link to the certificate for validation via python requests only. '''
        ''' caused by: SSLError([SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1006)) if it doesn't exist ca certs'''
        es_client = Elasticsearch(hosts=os.getenv("ES_DEV_V8_HOST"),
                                headers=get_headers('BASIC_AUTH_OM'),
                                use_ssl=True, # Useful if the connection is using SSL. If no, SSL certificates will not be validated
                                ca_certs=ca_cert_path,
                                # client_cert="upgrade-script/certs/qa13_new/qa13-es8-client.pem",
                                # client_key="upgrade-script/certs/qa13_new/qa13-es8-client.key",
                                verify_certs=True,
                                # verify_certs=False,
                                max_retries=0,
                                timeout=5)
        # print(json.dumps(es_client.cluster.health(), indent=2))
        print(es_client.cluster.health())
        print('\n')

        query_all = {
            "query" : {
                "match_all" : {}
            }
        }
        resp = es_client.search(index=INDEX, body=query_all)
        if resp:
            print("Got {} hits:".format(resp["hits"]["total"]["value"]))
            print(json.dumps(resp['hits']['hits'], indent=2))
        '''
        for hit in resp["hits"]["hits"]:
            print("{}".format(hit["_source"]))
        '''
        # resp = es_client.get(index=INDEX, id=1)
        # print(json.dumps(resp['_source'], indent=2))
     
    except Exception as e:
        print(str(e))

    print('\n')


def request_es_certificates():
    '''
    verify if the request with ssl works via request library
    '''
   
    # res = requests.get(url=os.getenv("ES_DEV_V8_HOST"), verify=False, cert=(r'C:\Users\euiyoung.hwang\Git_Workspace\ELK-Stack-Upgrade\upgrade-script\cert_files\dev\kirk.pem', r'C:\Users\euiyoung.hwang\Git_Workspace\ELK-Stack-Upgrade\upgrade-script\cert_files\dev\kirk-key.pem'))
    
    ''' (Caused by SSLError('Client private key is encrypted, password is required'))'''
    ''' The passphrase is used to protect and encrypt the private key.  it must be decrypted before use in any transaction with that passphrase'''
    try:
    
        print('\n')
        print('*'*10)
        print(sys._getframe().f_code.co_name)
        print('*'*10)
        print('\n')
    
        ''' To disable certificate verification, at the client side, one can use verify attribute.  -- Verify False'''
        ''' otherwise you can also pass the link to the certificate for validation via python requests only. '''
        ''' if we don't pass headers, it may have response like 401 Unauthorized rquests. Insufficient permissions'''
        ''' caused by: SSLError([SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1006)) if it doesn't exist ca certs'''
     
        # res = requests.get(url=os.getenv("ES_DEV_V8_HOST"), verify='./upgrade-script\certs\qa13_new\qa13-es8-ca.pem')
        # res = requests.get(url=os.getenv("ES_DEV_V8_HOST"), headers=get_headers(), verify=False)
        res = requests.get(url=os.getenv("ES_DEV_V8_HOST"), headers=get_headers('BASIC_AUTH_WX'), verify=ca_cert_path)
        # res = requests.get(url=os.getenv("ES_DEV_V8_HOST"), headers=get_headers(), verify='/home/biadmin/monitoring/reindexing/certs/qa13-es8-ca.pem')

        # print(json.dumps(res.json(), indent=2))
        if not res.status_code == 200:
            print(res.status_code, http_status_code.get(res.status_code, "None"))
            print('\n')
            return

        print(res.json())
        print('\n')

        query_all = {
            "query" : {
                "match_all" : {}
            }
        }

        # resp = requests.get(url="{}/{}/_search".format(os.getenv("ES_DEV_V8_HOST"), INDEX), headers=get_headers(), verify=False)
        resp = requests.get(url="{}/{}/_search".format(os.getenv("ES_DEV_V8_HOST"), INDEX), headers=get_headers('BASIC_AUTH_WX'), verify=ca_cert_path, json=query_all)
        # resp = requests.get(url="{}/{}/_search".format(os.getenv("ES_DEV_V8_HOST"), INDEX), headers=get_headers(), verify='/home/biadmin/monitoring/reindexing/certs/qa13-es8-ca.pem', json=query_all)
        
        if not resp.status_code == 200:
            print(f"Index : {INDEX}")
            print(resp.status_code, http_status_code.get(resp.status_code, "None"))
            print('\n')
            return
        
        ''' get results from ES Cluster'''
        print("Got {} hits:".format(resp.json()["hits"]["total"]["value"]))
        print(json.dumps(resp.json()['hits']['hits'], indent=2))

    except Exception as e:
        print("Excption : ", str(e))

    print('\n')
    

if __name__ == '__main__':
    ''' Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#tls-warnings '''
    ''' Validating the http request with Search Guard Authentication '''
    """
    https://docs.search-guard.com/latest/tls-in-production
    https://groups.google.com/g/search-guard/c/e1gCz_RU_wQ/m/ZsYHp4mlBAAJ
    https://www.elastic.co/guide/en/elasticsearch/reference/current/setting-up-authentication.html 
    --> When security features are enabled, depending on the realms you’ve configured, you must attach your user credentials to the requests sent to Elasticsearch. For example, when using realms that support usernames and passwords you can simply attach basic auth header to the requests.
    https://stackoverflow.com/questions/23172137/understanding-the-purpose-of-realm-in-basic-www-authentication
    
    - Node certificates are used to identify and secure traffic between Elasticsearch nodes on the transport layer (inter-node traffic). 
    - Client certificates are regular TLS certificates without any special requirements. They are used to identify Elasticsearch clients on the REST and transport layer. 
    They can be used for HTTP client certificate authentication or when using a Java Transport Client on transport layer.
    - Admin certificates are client certificates that have elevated rights to perform administrative tasks.
    - verfy_certs=True -> TLS error caused by: SSLError([SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self signed certificate in certificate chain (_ssl.c:1131))

    Basic authentication is a very simple authentication scheme that is built into the HTTP protocol. 
    The client sends HTTP requests with the Authorization header that contains the Basic word followed by a space and a base64-encoded username:password string

    """
    '''
    # ------------------------------------------------------------------------
    The TLS Tool has created the following files:
    root-ca.pem - the root certificate
    root-ca-key.pem - the private key for the root certificate
    node.pem - the node certificate
    node-key.pem - the private key for the node certificate
    admin.pem - the admin certificate
    admin-key.pem - the private key for the admin certificate
    '''
    '''
    (.venv) ➜  python ./upgrade-script/request-SG-script.py
    '''
    ''' verify if the request with ssl works via es_client library '''
    # es_client_certificates()
    ''' verify if the request with ssl works via request es_client library '''
    request_es_certificates()
    