
from elasticsearch import Elasticsearch
import json
import os
from datetime import datetime
import pandas as pd
import re
import logging
from dotenv import load_dotenv

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

''' pip install python-dotenv'''
load_dotenv(dotenv_path="../.env") # will search for .env file in local folder and load variables 


class Search():
    ''' elasticsearch class '''
    
    def __init__(self, host):
        self.timeout = 600
        self.MAX_BYTES = 10485760
        self.max_len = 0
        self.total_count = 0
        self.total_buffer = 0
        self.response_total_time = 0
        self.response_request_cnt = 0
        self.target_idx = None
        self.actions = []
        self.error_flag = False
        
        # self.es_client = Elasticsearch(hosts=host, headers=self.get_headers(), timeout=self.timeout)
        # create a new instance of the Elasticsearch client class
        # Elasticseach < 8.x basic auth example:
        # self.es_client = Elasticsearch(hosts=host, headers=self.get_headers(), http_auth=('elastic','gsaadmin'), timeout=self.timeout)
        ''' With HTTP compression, you can reduce the size of your documents by to up to 80%, lowering bandwidth utilization and latency, leading to improved transfer speeds.  '''
        self.es_client = Elasticsearch(hosts=host, headers=self.get_headers(), http_compress = True, timeout=self.timeout,  verify_certs=False)
        
        # Elasticsearch >= 8.x
        # self.es_client = Elasticsearch(hosts=_host, headers=self.get_headers(), basic_auth=('elastic','gsaadmin'), timeout=self.timeout)
    
    
    def get_es_instance(self):
        return self.es_client
    
    
    def close(self):
        self.es_client.close()
        
    
    def get_headers(self):
        ''' Elasticsearch Header '''
        return {
            'Content-type': 'application/json', 
            'Authorization' : '{}'.format(os.getenv('BASIC_AUTH')),
            # 'Connection': 'close'
        }
        
    
    def Get_Buffer_list_Length(self, docs):
        """
        :param docs:
        :return:
        """
        max_len = 0
        for doc in docs:
            max_len += len(str(doc))

        # logging.info(f"max_len : {max_len}")

        return max_len
    

    def Set_buffer_Lengh(self):
        self.max_len = 0


    def Get_Buffer_Length(self, actions):
        """
        :param docs:
        :return:
        """
        
        # self.max_len += len(json.dumps(actions))
        # logging.info(f"max_len : {self.max_len}")

        self.max_len += len(''.join(map(str, actions)))

        return self.max_len
    
        
    def create_index(self, _index):
        ''' sample index & mapping '''
        print(self.es_client)
        
        mapping = {
            "mappings": {
                "properties": {
                    # "title": {
                    #     "type": "text",
                    #     "analyzer": "standard",
                    #     "fields": {
                    #         "keyword": {
                    #             "type": "keyword"
                    #         }
                    #     }
                    # }
                }
            }
        }
        
        def try_delete_create_index(index):
            try:
                if self.es_client.indices.exists(index):
                    print('Successfully deleted: {}'.format(index))
                    self.es_client.indices.delete(index)
                    # now create a new index
                    self.es_client.indices.create(index=index, body=mapping)
                    # es_client.indices.put_alias(index, "omnisearch_search")
                    self.es_client.indices.refresh(index=index)
                    print("Successfully created: {}".format(index))
            
            except NotFoundError:
                pass
            
        ''' delete and create index into ES '''
        try_delete_create_index(index=_index)
        
    
    def post_search(self, _index):
        ''' search after indexing as validate '''
        response = self.es_client.search(
            index=_index,
            body={
                    "query" : {
                       "match_all" : {
                       }
                    }
            }
        )
        print("Total counts for search - {}".format(json.dumps(response['hits']['total']['value'], indent=2)))
        # print("response for search - {}".format(json.dumps(response['hits']['hits'][0], indent=2)))
    
    
    def transform_df_to_clean_characters(self, df):
        ''' Clean dataframe '''
        df = df.fillna('')
        return df
    
    
    def transform_json_clean_characters(self, to_replace):
        ''' Clean dataframe '''
        if isinstance(to_replace, (str)):
            to_replace = to_replace.strip()
            to_replace = re.sub(r'\n|\\n', ' ', to_replace)
            to_replace = re.sub(r'\t|\\t', ' ', to_replace)
            to_replace = re.sub(r'\f|\\f', ' ', to_replace)
            to_replace = re.sub(r'\s+', ' ', to_replace)
            to_replace = re.sub(r'string', '', to_replace)
            to_replace = re.sub(r'_id', '', 'key')
        
        return to_replace
    

    def export_file(self, index_name, msg):
        ''' export to file '''
        self.error_flag = True
        directory = f"./output"
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(directory + f"/{index_name}", "w") as f:
            f.write(f"# {msg}" + '\n')


    def logging_show_msg(self, msg):
        print('\n\n\n\n')
        print('-'*30)
        print(f"{msg}")
        print('-'*30)
        print('\n\n\n\n')


    def transform_field_name(self, raw):
        json_str = json.dumps(raw, ensure_ascii=False)
        json_str = json_str.replace("POTYPE,", "POTYPE")
        json_str = json_str.replace("PACKAGINGCODE ", "PACKAGINGCODE")
        
        return json.loads(json_str)
    

    def transform_value_from_json(self, d):
        ''' Lookup and change value in json dict'''
        def get_recursive_nested_all(d):
            if isinstance(d, list):
                for i in d:
                    get_recursive_nested_all(i)
            elif isinstance(d, dict):
                for k, v in d.items():
                    if not isinstance(v, (list, dict)):
                        d[k] = f"added to value : {v}"
                    else:
                        get_recursive_nested_all(v)
            return d
        
        ''' call get_recursive_nested_all func'''
        return get_recursive_nested_all(d)

    
    def buffered_json_to_es(self, raw_json, _index, _type, version=5):
        ''' https://opster.com/guides/elasticsearch/how-tos/optimizing-elasticsearch-bulk-indexing-high-performance/ '''
        ''' To further improve bulk indexing performance, you can use multiple threads or processes to send bulk requests concurrently. This can help you utilize the full capacity of your Elasticsearch cluster and reduce the time it takes to index large datasets.'''
        ''' When using multiple threads or processes, make sure to monitor the performance and resource usage of your Elasticsearch cluster. '''
        ''' If you notice high CPU or memory usage, you may need to reduce the number of concurrent requests or adjust your Elasticsearch configuration.'''
        '''
        raw_json : 
        # [{'_index': 'recommendation_test', '_id': 'cLOXEosBDeViDjrDAL8Z', '_score': 1.0, '_source': {'intern': 'Richard', 'grade': 'bad', 'type': 'grade'}},
        ...]
        '''
        self.logging_show_msg(f"buffered_json_to_es Loading.. counts : {len(raw_json)}")
        self.target_idx = _index
        
        try:
            
            for each_raw in raw_json:

                ''' ES v.5 header'''
                if version < 8:
                    # _header = {'index': {'_index': _index, '_type' : _type, "_id" : each_raw['_id'], "op_type" : "create"}}
                    _header = {'index': {'_index': _index, '_type' : _type, "_id" : each_raw['_id']}}

                elif version >= 8:
                    ''' When indexing with ES v.8, _type is deleted and must be excluded. In Elasticsearch 8.0 and later, _type is completely removed in favor of indices and mapping types. '''
                    ''' So, when indexing with ES v.8, spark job also needs to remove the _type field.'''
                    _header = {'index': {'_index': _index, "_id" : each_raw['_id']}}
                    # _header = {'index': {'_index': _index, "_id" : each_raw['_id'], "op_type" : "create"}}
                                        
                self.actions.append(_header)
                # _body = self.transform_field_name(each_raw['_source'])
                # _body = self.transform_value_from_json(each_raw['_source'])
                _body = each_raw['_source']
                # print(_body)
                self.actions.append(_body)
                '''
                actions += [
                    # {'index': {'_index': _index, '_type' : _type, "_id" : each_raw['_id'], "op_type" : "create"}},
                    {'index': {'_index': _index, "_id" : each_raw['_id'], "op_type" : "create"}},
                    each_raw['_source']
                ]
                '''

                self.total_count += 1
                # self.total_buffer += len(json.dumps(_header)) + len(json.dumps(_body))
                # self.total_buffer += len(str(_header)) + len(str(_body))

                # logging.info(f"size of buffer : {list(map(len,actions))}")
                
                # if self.Get_Buffer_Length(self.actions) > self.MAX_BYTES:
                # if self.total_buffer > self.MAX_BYTES:
                if self.total_count % 1000 == 0:
                    Bulk_StartTime = datetime.now()
                    
                    response = self.es_client.bulk(body=self.actions)
                    ''' es v5'''
                    # if str(response['errors']).lower() == 'true':
                    ''' es v8'''
                    if response['errors']:
                        # logging.error(response)
                        print('\n\n\n\n')
                        print(response)
                        self.export_file(self.target_idx, str(response))
                        print('\n\n\n\n')
                        pass
                    else:
                        logging.info("** indexing ** : {}".format(len(response['items'])))

                    Bulk_EndTime = datetime.now()
                    ''' accumulate response_total_time'''
                    self.response_total_time += float(str((Bulk_EndTime - Bulk_StartTime).seconds) + '.' + str((Bulk_EndTime - Bulk_StartTime).microseconds).zfill(6)[:2])
                    self.response_request_cnt += 1
                    logging.info(f"response_total_time :{self.response_total_time}, response_request_cnt = {self.response_request_cnt}")
                    
                    ''' initialize variables'''
                    ''' ----------------------'''
                    # self.Set_buffer_Lengh()
                    del self.actions[:]
                    self.total_count = 0
                    self.total_buffer = 0
                    ''' ----------------------'''
                
            # --
            # Index for the remain Dataset
            # --
            '''
            if len(actions) > 0:
                response = self.es_client.bulk(body=actions)
                
                if response['errors'] == 'true':
                    logging.error(response)
                else:
                    logging.info("** remain indexing ** : {}".format(len(response['items'])))
                    del actions[:]
            '''        
            
            # --
            # refresh
            # self.es_client.indices.refresh(index=_index)
            
          
        except Exception as e:
            print('buffered_json_to_es exception : {}'.format(str(e)))
            pass


    def remained_buffered_json_to_es(self, version):
        ''' push remain buffered json to target cluster'''
        
        self.logging_show_msg(f"remained_buffered_json_to_es.. counts : {len(self.actions)}")
        
        Bulk_StartTime = datetime.now()
        response = self.es_client.bulk(body=self.actions)

        if 'errors' in response:
            if str(response['errors']).lower() == 'true':
                print('\n\n\n\n')
                print(response)
                self.export_file(self.target_idx, str(response))
                print('\n\n\n\n')
                pass
            else:
                logging.info("** remain indexing ** : {}".format(len(response['items'])))
    
        Bulk_EndTime = datetime.now()
        ''' accumulate response_total_time'''
        self.response_total_time += float(str((Bulk_EndTime - Bulk_StartTime).seconds) + '.' + str((Bulk_EndTime - Bulk_StartTime).microseconds).zfill(6)[:2])
        self.response_request_cnt += 1
        logging.info(f"response_total_time :{self.response_total_time}, response_request_cnt = {self.response_request_cnt}")

        del self.actions[:]
        self.total_count = 0
        self.total_buffer = 0
                

    def buffered_df_to_es(self, df, _index):
        ''' df : Dataframe format, _index: Elasticsearch index name that you want to save '''
        print("buffered_df_to_es Loading..")
        ''' Nan to black for each field value '''
        try:
            df = self.transform_df_to_clean_characters(df)
            actions = []
        
            # creating a list of dataframe columns 
            columns = list(df) 
            # print(columns)
            for row in list(df.values.tolist()):
                rows_dict = {}
                for i, colmun_name in enumerate(columns):
                    rows_dict.update({self.transform_json_clean_characters(colmun_name) : self.transform_json_clean_characters(row[i])})
                
                # print(rows_dict)
                actions.append({'index': {'_index': _index}})
                actions.append(rows_dict)
                # print(json.dumps(actions, indent=2))
                
                if self.Get_Buffer_Length(actions) > self.MAX_BYTES:
                    response = self.es_client.bulk(body=actions)
                    print("** indexing Error - True/False ** : {}".format(json.dumps(response['errors'], indent=2)))
                    del actions[:]
            
            # --
            # Index for the remain Dataset
            # --
            response = self.es_client.bulk(body=actions)
            # print(response)
            print("** Remain indexing Error - True/False ** : {}".format(json.dumps(response['errors'], indent=2)))
            
            # --
            # refresh
            self.es_client.indices.refresh(index=_index)
        
        except Exception as e:
            print('buffered_df_to_es exception : {}'.format(str(e)))



class Search_Utils():
    ''' Utils for Search class'''

    def __init__(self):
        pass

    @staticmethod
    def get_query_dsl(query, version):
        ''' 
        The track_total_hits parameter in Elasticsearch controls whether the search API accurately calculates and
        returns the total number of matching documents for a query
        '''
        if version < 7:
            return query
        
        ''' 
        Elasticsearch 7.x and later versions have track_total_hits set to 10000, 
        Setting it to true provides an accurate count for all hits, but can impact performance 
        '''
        # query.update({"track_total_hits" : True})
        # print(query)
        return query



class QueryBuilder:
   
    def __init__(self, logger):
        self.logger = logger
        self.es_query = {}
        self.must_clauses = []
        self.should_clauses = []
        self.filter_clauses = []
        self.query_string = ""  # ES query string
        self.highlight_clauses = {}
        

    def build_sort(self, oas_query=None):
        '''  Builds the sort field format for elasticsearch '''
        order = oas_query.get("sort_order", "DESC")
        sort_field = oas_query.get("sort_field")

        ordered_date_sorts = [
            {
                # "start_date": {
                #     "order": oas_query.get("sort_order"),
                #     "missing": "_last"
                # },
                # "title.keyword": {
                #     "order": oas_query.get("sort_order"),
                #     "missing": "_last"
                # }
            }
        ]

        if not sort_field:
            return [{"_score": {"order": order}}] + ordered_date_sorts
        else:
            return [
                {sort_field: {"order": order, "missing": "_last"}},
                ordered_date_sorts[0]
            ]


    def transform_query_string(self, oas_query=None):
        # Base case for search, empty query string
        if not oas_query.get("query_string", ""):
            self.query_string = {"match_all": {}}
        else:
            self.query_string = {
                "query_string": {
                    # "fields": ['title^3', 'field2'],
                    "fields": ['*'],
                    "default_operator": "AND",
                    "analyzer": "standard",
                    "query": oas_query.get('query_string'),
                    "lenient" : True,
                }
            }


    def add_highlighting(self):
        self.highlight_clauses = {
            "highlight": {
                "order": "score",
                "pre_tags": [
                    "<b>"
                ],
                "post_tags": [
                    "</b>"
                ],
                "fields": {
                    "*": {
                        "number_of_fragments": 1,
                        "type": "plain",
                        "fragment_size": 150
                    }
                }
            }
        }

        self.es_query.update(self.highlight_clauses)


  
    def build_terms_filters_batch(self, _terms, max_terms_count=65000):
        '''The logic to separate terms clauses based on max_terms_count '''
        if len(_terms) < 2 and "*" in _terms:
            return []
        
        terms_filters = []
        terms_chunks = [_terms[i: i + max_terms_count] for i in range(0, len(_terms), max_terms_count)]
        print(terms_chunks)
        for _chunks in terms_chunks:
            terms_filters.append({"terms": {"_id": _chunks}})

        return terms_filters


    def build_query(self, oas_query=None):
        if not oas_query:
            return {}

        # self.logger.info('QueryBuilder:oas_query_params - {}'.format(oas_query))

        self.transform_query_string(oas_query)
        self.must_clauses = [self.query_string]
        self.filter_clauses = [{
            "bool": {
                "must": [
                    {
                        "bool": {
                            "should": self.build_terms_filters_batch(_terms=oas_query.get("ids_filters",[]), max_terms_count=5)
                        }
                    }
                ]
            }
        }]
        self.es_query = {
            # "track_total_hits": True,
            "sort": self.build_sort(oas_query),
            "query" : {
                "bool" : {
                    "must": self.must_clauses,
                    "should" : self.should_clauses,
                    "filter": self.filter_clauses
                }
            },
            "size" : oas_query.get("size", 1)
        }

        self.add_highlighting()
        
        # self.logger.info('QueryBuilder:oas_query_build - {}'.format(json.dumps(self.es_query, indent=2)))

        return self.es_query