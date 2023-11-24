import requests
from collections import ChainMap
from typing import List, Mapping, Dict, Any, Optional, Union


BASE_HOST = "http://10.101.3.118:4200"
BASE_CHAPI_URI = f"{BASE_HOST}/chapi/v1"
BASE_CHAPI_DASHBOARDS_URI = f"{BASE_CHAPI_URI}/dashboards"

HEADERS = {
    "Access-control-allow-credentials": "true", 
    "Access-control-allow-origin": "*", 
    "Content-length": "4076", 
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "",
}

def merge_and_filter_entities(data: Dict[str, Any]):
    return {
        k: [i for i in v if i is not None]
        for k, v in {k: [d.get(k) for d in data] for k in set().union(*data)}.items()
    }

def get_dashboards(
    board_uri: str,
    headers: Dict[str, str],
) -> List[Mapping[str, Any]]:
    DASHBOARDS = []
    with requests.get(board_uri, headers=headers) as response:
        boards = [r["dashboard"] for r in response.json()["dashboards"]]

    for board_name in boards:
        with requests.post(f"{board_uri}/{board_name}", headers=headers) as response:
            response.raise_for_status()
            
            _components = []
            _components.extend(
                [
                    {
                        i["key"]: {"type": i.get("type")}
                        if i.get("type")
                        else [{j["key"]: {"type": j["type"]} for j in i["tabs"]}]
                    }
                    for i in response.json()["components"]
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
                for i in response.json()["filters"]
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


def generate_jwt_token(api_token_uri: str, api_permissions: str):
    request_body = {"username": api_permissions, "password": api_permissions}
    with requests.post(api_token_uri, json=request_body) as response:
        response.raise_for_status()
        return response.text

if __name__ == "__main__":
    HEADERS["Authorization"] = generate_jwt_token("http://10.101.3.251:9001/api/login", "admin")
    # BOARDS = get_dashboards(BASE_CHAPI_DASHBOARDS_URI, HEADERS)
    # res = requests.get("http://stackoverflow.com")
    print(HEADERS)