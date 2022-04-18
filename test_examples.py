import allure
import json
import pytest

import api

from bear import Bear
from bear import get_pairwise_bear_data
from common_helper import get_subdicts, get_sublists

# docker ps -a | awk '{ print $1,$2 }' | grep azshoo/alaska | awk '{print $1 }' | xargs -I {} docker rm -f {}


@allure.feature("post bear")
@allure.feature("get bear")
@allure.feature("delete bear")
@pytest.mark.parametrize("bear_params", get_pairwise_bear_data())
def test_post_real_bear(service, client, bear_params):
    try:
        bear = Bear.get_real().set_name(bear_params[0]).set_type(bear_params[1]).set_age(bear_params[2])
    
        res = client.post_bear(bear=bear)
        assert res.status_code == 200
    
        bear_id = int(res.text)
        assert bear_id == 1
    
        res = client.get_bear(bear=bear)
        assert res.status_code == 200
        assert res.json() == json.loads(bear.to_json())

        res = client.delete_bear(bear=bear)
        assert res.status_code == 200
        assert res.text == "OK"

        res = client.get_bear(bear=bear)
        assert res.status_code == 200
        assert res.text == "EMPTY"

    finally:
        allure.attach.file(service.log_file)
        

@allure.feature("post bear")
@pytest.mark.parametrize("to_update", get_subdicts(bear_type=None, bear_name=None, bear_age=None))
def test_post_bear_none_values(service, client, to_update):
    try:
        bear = Bear.get_real()
        payload = {"bear_type": bear.bear_type, "bear_name": bear.bear_name, "bear_age": bear.bear_age}
        payload.update(to_update)
    
        res = api.post_bear(client=client.session, **payload)
        assert res.status_code == 500
        assert "Internal Server Error" in res.text

    finally:
        allure.attach.file(service.log_file)


@allure.feature("post bear")
@pytest.mark.parametrize("to_remove", get_sublists("bear_type", "bear_name", "bear_age"))
def test_post_bear_missed_params(service, client, to_remove):
    try:
        bear = Bear.get_real()
        payload = {"bear_type": bear.bear_type, "bear_name": bear.bear_name, "bear_age": bear.bear_age}
    
        for key in to_remove:
            del payload[key]
    
        res = api.post_bear(client=client.session, **payload)
    
        assert res.status_code == 200  # why shouldn't the code be 4xx?
        assert res.text == "Error. Pls fill all parameters"
    
    finally:
        allure.attach.file(service.log_file)


@allure.feature("post bear")
def test_post_bear_extra_id(service, client):
    try:
        bear1 = Bear.get_real()
        payload = {"bear_type": bear1.bear_type, "bear_name": bear1.bear_name, "bear_age": bear1.bear_age, "bear_id": 2}
    
        res = api.post_bear(client=client.session, **payload)
        assert res.status_code == 200
        assert res.text == "1"
    
        res = api.get_bear(client=client.session, b_id=1)
        assert res.status_code == 200
        assert res.json()["bear_id"] == 1
        assert res.json()["bear_type"] == bear1.bear_type
        assert res.json()["bear_name"] == bear1.bear_name
        assert res.json()["bear_age"] == bear1.bear_age
    
        res = api.get_bear(client=client.session, b_id=2)
        assert res.text == "EMPTY"
    
        bear2 = Bear.get_real()
        payload = {"bear_type": bear2.bear_type, "bear_name": bear2.bear_name, "bear_age": bear2.bear_age, "bear_id": 1}
    
        res = api.post_bear(client=client.session, **payload)
        assert res.status_code == 200
        assert res.text == "2"
    
        res = api.get_bear(client=client.session, b_id=1)
        assert res.status_code == 200
        assert res.json()["bear_id"] == 1
        assert res.json()["bear_type"] == bear1.bear_type
        assert res.json()["bear_name"] == bear1.bear_name
        assert res.json()["bear_age"] == bear1.bear_age

    finally:
        allure.attach.file(service.log_file)


@allure.feature("post bear")
def test_post_bear_duplicate_name(service, client):
    try:
        bear1 = Bear.get_real().set_age(1.0)
        res = client.post_bear(bear=bear1)
        assert res.status_code == 200
        assert bear1.bear_id == 1
    
        bear2 = Bear.get_real().set_name(bear1.bear_name).set_age(bear1.bear_age + 0.5)
        res = client.post_bear(bear=bear2)
        assert res.status_code == 200
        assert bear2.bear_id == 2
    
        all_bears = client.get_bears().json()
        assert len(all_bears) == 2
        assert all_bears[0] == json.loads(bear1.to_json())
        assert all_bears[1] == json.loads(bear2.to_json())

    finally:
        allure.attach.file(service.log_file)


@allure.feature("post bear")
def test_post_bear_full_duplicate(service, client):
    try:
        bear1 = Bear.get_real()
        res = client.post_bear(bear=bear1)
        assert res.status_code == 200
        assert bear1.bear_id == 1
    
        bear2 = Bear().set_type(bear1.bear_type).set_name(bear1.bear_name).set_age(bear1.bear_age)
        res = client.post_bear(bear=bear2)
        assert res.status_code == 200
        assert bear2.bear_id == 2
    
        all_bears = client.get_bears().json()
        assert len(all_bears) == 2
        assert all_bears[0] == json.loads(bear1.to_json())
        assert all_bears[1] == json.loads(bear2.to_json())
    
    finally:
        allure.attach.file(service.log_file)

