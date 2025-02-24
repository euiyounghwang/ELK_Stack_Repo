from pydantic import BaseModel
from datetime import datetime
from pytz import timezone as tz
from enum import Enum
from typing import List, Union
import uuid
from injector import es_hosts_enum_list
import sys


class Sort_Order(str, Enum):
    desc = 'DESC'
    asc = 'ASC'
    


class ES_Host_Model(str, Enum):
    # localhost = "http://localhost:9200"
    # print("ES_Host_Model - ", { f"day_{i}": es_hosts_enum_list[i] for i in range(len(es_hosts_enum_list)) })
    vars().update({ f"day_{i}": es_hosts_enum_list[i] for i in range(len(es_hosts_enum_list)) })
    

class Search(BaseModel):
    source_es_host: str = "http://localhost:9200"
    query_string: str = "test"
    index_name: str = "test"
    size: int = 20
    # sort_order: str = "DESC"
    sort_order: Sort_Order = Sort_Order.desc
    ids_filters : list = ["*"]
        
    def to_json(self):
        return {
            'source_es_host' : self.source_es_host,
            'query_string' : self.query_string,
            'index_name' : self.index_name,
            'size' : self.size,
            'sort_order' : self.sort_order,
            'ids_filters' : self.ids_filters
        }
    
class IndexMapping(BaseModel):
    # source_mapping : str = "{ \
    #     'employee': {  \
    #         'name':       'sonoo',  \
    #         'salary':      56000,   \
    #         'married':    true  \
    #     }  \
    # }"
    source_mapping : dict = {"test_mapping" : "test"}
    
    # target_mapping : str = "{ \
    #     'employee': {  \
    #         'name':       'sonoo',  \
    #         'salary':      56000,   \
    #         'married':    true  \
    #     }  \
    # }"
    target_mapping : dict = {"test_mapping" : "test"}
    
        
    def to_json(self):
        return {
            'source_mapping' : self.source_mapping,
            'target_mapping' : self.target_mapping
        }
