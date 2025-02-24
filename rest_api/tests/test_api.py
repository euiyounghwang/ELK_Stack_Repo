
import pytest


@pytest.mark.skip(reason="no way of currently testing this")
def test_skip():
    assert 1 != 1


# @pytest.mark.skip(reason="no way of currently testing this")
def test_api(mock_client):
    response = mock_client.get("/cluster/health?es_url=http://localhost:9200")
    assert response is not None
    assert response.status_code == 200
    assert 'cluster_name' in response.json()


# @pytest.mark.skip(reason="no way of currently testing this")    
def test_index_mapping_compare_api(mock_client):

    URL = "/index/mapping_compare_test" 

    # - same jsons
    sample_payload = {
        "source_mapping" : {"test_mapping" : "test"},
        "target_mapping" : {"test_mapping" : "test"}
    }
     
    response = mock_client.post(URL, json=sample_payload)
    assert response.status_code == 200

    # It will be added diff login into service model on FastAPI F/W
    assert response.json() == {
        "diff": "Same mapping"
    }

    # - diff jsons
    sample_payload = {
        "source_mapping" : {"test_mapping" : "test"},
        "target_mapping" : {"test_mapping" : "test1"}
    }
     
    response = mock_client.post(URL, json=sample_payload)
    assert response.status_code == 200

    # It will be added diff login into service model on FastAPI F/W
    assert response.json() == 	{
        "diff": "Different mapping",
        "result": {
            "test_mapping": [
            "test",
            "test1"
            ]
        }
    }

    sample_payload = {
    "source_mapping": {
        "test_mapping": "test"
    },
    "target_mapping": {
        "test_mapping": "test",
        "add" : "new one"
      }
    }

    response = mock_client.post(URL, json=sample_payload)
    assert response.status_code == 200

    # It will be added diff login into service model on FastAPI F/W
    assert response.json() == 	{
        "diff": "Different mapping",
        "result": {
            "$insert": {
                "add": "new one"
            }
        }
    }