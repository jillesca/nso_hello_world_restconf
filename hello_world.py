import urllib3
import requests
import xmltodict
from requests.auth import HTTPBasicAuth

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL_BASE = "https://sandbox-nso-1.cisco.com"
USERNAME = "developer"
PASSWORD = "Services4Ever"

# Add the 'data' path between restconf and tailf-ncs...
# show ncs-state version | display restconf
# show ncs-state daemon-status | display restconf
URL_DEAMON_STATUS = "/restconf/data/tailf-ncs-monitoring:ncs-state/daemon-status"
URL_NSO_VERSION = "/restconf/data/tailf-ncs-monitoring:ncs-state/version"

urls_to_call = [URL_DEAMON_STATUS, URL_NSO_VERSION]


def restconf_session() -> list:
    responses: list = []
    session = requests.session()
    session.auth = HTTPBasicAuth(USERNAME, PASSWORD)
    session.headers.update({"Accept": "application/yang-data+xml"})
    session.verify = False

    with session as s:
        for url in urls_to_call:
            responses.append(get_restconf(s, url))
    return responses


def get_restconf(session: requests.Session, url: str) -> dict:
    res = session.get(URL_BASE + url)
    return {"xml_reply": res.text}


def parse_xml_to_dict(xml: str) -> dict:
    return xmltodict.parse(xml)


def parse_responses(responses: list) -> list:
    result: dict = {}
    for res in responses:
        result.update(clasify_results(res["xml_reply"]))
    return result


def clasify_results(xml_reply: str) -> dict:
    res_dict = parse_xml_to_dict(xml_reply)
    if "daemon-status" in res_dict:
        return {"daemon_status": res_dict["daemon-status"]["#text"]}
    if "version" in res_dict:
        return {"nso_version": res_dict["version"]["#text"]}


def print_results(res: dict) -> None:
    deamon_status = res["daemon_status"]
    msg = f'\nNSO version: {res["nso_version"]}'

    if not valid_deamon_status(deamon_status):
        msg += f"\nNSO not running. Status: {deamon_status}"
        print(msg)
        raise ValueError(msg)

    msg += f"\nNSO deamon running. Status: {deamon_status.upper()}"
    print(msg)


def valid_deamon_status(status: str) -> bool:
    # https://developer.cisco.com/docs/nso/guides/#!nso-system-management/monitoring-nso
    if "started" in status.lower():
        return True
    return False


def main() -> None:
    res = restconf_session()
    results = parse_responses(res)
    print_results(results)


if __name__ == "__main__":
    main()
