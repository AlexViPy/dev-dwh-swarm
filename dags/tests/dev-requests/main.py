#!/usr/bin/env python3

import json
import urllib.request
from collections import ChainMap
from typing import List, Mapping, Dict, Any, Optional, Union


BASE_HOST = "http://10.101.3.118:4200"
BASE_CHAPI_URI = f"{BASE_HOST}/chapi/v1"
BASE_CHAPI_DASHBOARDS_URI = f"{BASE_CHAPI_URI}/dashboards"

HEADERS = {
    "Accept": "application/*+json;version=36.1",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64)",
    "Authorization": "",
}

def merge_and_filter_entities(data: Dict[str, Any]):
    return {
        k: [i for i in v if i is not None]
        for k, v in {k: [d.get(k) for d in data] for k in set().union(*data)}.items()
    }

def generate_jwt_token(api_token_uri: str, api_permissions: str):
    request_body = {"username": api_permissions, "password": api_permissions}

    req = urllib.request.Request(
        method ='POST', 
        url = api_token_uri,
        headers={"Content-type": "application/json"},
        data = json.dumps(request_body).encode("utf-8")
    )
    with urllib.request.urlopen(req) as response:
        return response.read()

def api_request(
    method: str,
    url: str,
    headers: Dict[str, str],
    data: bytes = None,
    timeout: int = 60,
):
    req = urllib.request.Request(
        method = method, 
        url = url,
        headers = headers,
        data = json.dumps(data).encode("utf-8") if data else None
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8")

def get_dashboards(
    board_uri: str,
    headers: Dict[str, str],
) -> List[Mapping[str, Any]]:
    DASHBOARDS = []
    response = api_request(method="GET", url=board_uri, headers=headers)
    boards = [r["dashboard"] for r in json.loads(response)["dashboards"]]

    for board_name in boards:
        response = api_request(method="POST", url=f"{board_uri}/{board_name}", headers=headers)
        current_response = json.loads(response)
        _components = []
        _components.extend(
            [
                {
                    i["key"]: {"type": i.get("type")}
                    if i.get("type")
                    else [{j["key"]: {"type": j["type"]} for j in i["tabs"]}]
                }
                for i in current_response["components"]
            ]
        )
        components = dict(ChainMap(*_components))
        _mappings = [
            {
                j["key"]: {
                    "column": j["column"],
                    "type": i["type"],
                    "options": i["options"] if i["options"] else i["values"],
                }
            }
            for i in current_response["filters"]
            for j in i["mappings"]
            if i["type"] not in ("input")
        ]
        filters = merge_and_filter_entities(_mappings)

        for k, v in components.items():
            if isinstance(v, dict):
                components[k].update({"filters": filters.get(k, [])})
            else:
                for el in v:
                    for k1, _ in el.items():
                        el[k1].update({"filters": filters.get(k1, [])})

        DASHBOARDS.append({board_name: components})

    return DASHBOARDS

if __name__ == "__main__":
    # в HEADERS в поле Authorization появится внось сгенерированный код, тем самым мы полили 200 ответ и нужный там объект
    HEADERS["Authorization"] = generate_jwt_token("http://10.101.3.251:9001/api/login", "admin")
    print(HEADERS)
    
    # вот тут мы должны получить все борды с сервиса "http://10.101.3.118:4200/chapi/v1/dashboards"
    BOARDS = get_dashboards(BASE_CHAPI_DASHBOARDS_URI, HEADERS)
    # res = requests.get("http://stackoverflow.com")
    print(BOARDS)