from fastapi import APIRouter
import json
import datetime
from injector import (logger)
from service.status_handler import (StatusHanlder, StatusException)
from repository.repository_schema import ES_Host_Model
from typing import Optional


app = APIRouter(
    prefix="/elk-upgrade",
)


@app.get("/health", 
          status_code=StatusHanlder.HTTP_STATUS_200,
          responses={
            200: {"description" : "OK"},
            404 :{"description" : "URl not found"}
          },
          description="Sample Payload : http://localhost:8001/cluster/health?es_url=http://localhost:9200", 
          summary="Cluster Info")
async def get_es_health(es_url="http://localhost:9200"):
# async def get_es_info(es_url : ES_Host_Model):
    # logger.info(es_url)
    '''
    response =  SearchAPIHandlerInject.get_es_health(es_url)
    if isinstance(response, dict):
        logger.info('SearchOmniHandler:get_es_info - {}'.format(json.dumps(response, indent=2)))

    return response
    '''
    return {'message' : 'OK'}


"""
@app.post("/sharding_predict", description="Cluster sharding predict", summary="Cluster sharding predict")
async def Cluster_sharding_estimate(request: Performance):
    ''' Search to Elasticsearch '''
    StartTime, EndTime, Delay_Time = 0, 0, 0
    
    try:
        StartTime = datetime.datetime.now()
        
        # logger.info("api_controller doc: {}".format(json.dumps(doc, indent=2)))
        # request_json = {k : v for k, v in request}
        request_json = request.to_json()
        print(request, type(request), request.data_size, request_json)
        logger.info("Cluster_sharding_estimate_Controller : {}".format(json.dumps(request_json, indent=2)))
        
        EndTime = datetime.datetime.now()

        # return await ClusterShardingInject.sharding_predict(oas_query=request_json)
       
    except Exception as e:
        logger.error(e)
        return StatusException.raise_exception(e)
    
    finally:
        Delay_Time = str((EndTime - StartTime).seconds) + '.' + str((EndTime - StartTime).microseconds).zfill(6)[:2]
        logger.info('Metrics : {}'.format(Delay_Time))
"""
