
from config.log_config import create_log
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import json
import os


def get_headers():
    ''' Elasticsearch Header '''
    return {'Content-type': 'application/json', 'Authorization' : '{}'.format(os.getenv('BASIC_AUTH')), 'Connection': 'close'}


load_dotenv()
    
# Initialize & Inject with only one instance
logger = create_log()

# from ssl import create_default_context
# context = create_default_context(cafile=r'C:\Users\euiyoung.hwang\Git_Workspace\ELK-upgrade\root-ca.pem')
# context = create_default_context(cafile=r'C:\Users\euiyoung.hwang\Git_Workspace\ELK-upgrade\kirk.pem')

"""
If using SSL, there are several parameters that control how we deal with
    certificates (see :class:`~elasticsearch.Urllib3HttpConnection` for
    detailed description of the options)::

        es = Elasticsearch(
            ['localhost:443', 'other_host:443'],
            # turn on SSL
            use_ssl=True,
            # make sure we verify SSL certificates
            verify_certs=True,
            # provide a path to CA certs on disk
            ca_certs='/path/to/CA_certs'
        )

    If using SSL, but don't verify the certs, a warning message is showed
    optionally (see :class:`~elasticsearch.Urllib3HttpConnection` for
    detailed description of the options)::

        es = Elasticsearch(
            ['localhost:443', 'other_host:443'],
            # turn on SSL
            use_ssl=True,
            # no verify SSL certificates
            verify_certs=False,
            # don't show warnings about ssl certs verification
            ssl_show_warn=False
        )

    SSL client authentication is supported
    (see :class:`~elasticsearch.Urllib3HttpConnection` for
    detailed description of the options)::

        es = Elasticsearch(
            ['localhost:443', 'other_host:443'],
            # turn on SSL
            use_ssl=True,
            # make sure we verify SSL certificates
            verify_certs=True,
            # provide a path to CA certs on disk
            ca_certs='/path/to/CA_certs',
            # PEM formatted SSL client certificate
            client_cert='/path/to/clientcert.pem',
            # PEM formatted SSL client key
            client_key='/path/to/clientkey.pem'
        )
"""
es_client = Elasticsearch(hosts=os.getenv("ES_HOST"),
                          verify_certs=False,
                          # use_ssl=True,
                          # ssl_show_warn=False,
                          headers=get_headers(),
                          # cert=(r'C:\Users\euiyoung.hwang\Git_Workspace\ELK-upgrade\kirk.pem', r'C:\Users\euiyoung.hwang\Git_Workspace\ELK-upgrade\kirk-key.pem'),
                          # ca_certs=r'C:\Users\euiyoung.hwang\Git_Workspace\ELK-upgrade\root-ca.pem',  # PEM format
                          # client_cert=r'C:\Users\euiyoung.hwang\Git_Workspace\ELK-upgrade\kirk.pem',  # PEM format
                          # client_key=r'C:\Users\euiyoung.hwang\Git_Workspace\ELK-upgrade\kirk-key.pem',   # PEM format
                          # ssl_context=context, 
                          timeout=5
)
