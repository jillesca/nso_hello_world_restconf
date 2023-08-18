import urllib3
import requests
import xmltodict
from requests.auth import HTTPBasicAuth

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://sandbox-nso-1.cisco.com"
USERNAME = "developer"
PASSWORD = "Services4Ever"

# Add the 'data' path between restconf and tailf-ncs...
# show ncs-state version | display restconf
# show ncs-state daemon-status | display restconf
API_ENDPOINTS = [
    "/restconf/data/tailf-ncs-monitoring:ncs-state/daemon-status",
    "/restconf/data/tailf-ncs-monitoring:ncs-state/version",
]


def create_restconf_session() -> requests.Session:
    session = requests.session()
    session.auth = HTTPBasicAuth(USERNAME, PASSWORD)
    session.headers.update({"Accept": "application/yang-data+xml"})
    session.verify = False
    return session


def fetch_data(session: requests.Session, endpoint: str) -> str:
    try:
        response = session.get(BASE_URL + endpoint)
        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as err:
        print(f"Http Error: {err=}")
        exit()
    except requests.exceptions.ConnectionError as err:
        print(f"Error Connecting: {err=}")
        exit()
    except requests.exceptions.Timeout as err:
        print(f"Timeout Error: {err=}")
        exit()
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error happened: {err=}")
        exit()


def classify_results(parsed_data: dict) -> dict:
    if "daemon-status" in parsed_data:
        return {"daemon_status": parsed_data["daemon-status"]["#text"]}
    if "version" in parsed_data:
        return {"nso_version": parsed_data["version"]["#text"]}


def parse_xml(xml: str) -> dict:
    return xmltodict.parse(xml)


def print_results(results: dict) -> None:
    daemon_status = results.get("daemon_status", "FAILED_TO_GET_STATUS")
    nso_version = results.get("nso_version", "FAILED_TO_GET_VERSION")
    msg = f"\nNSO version: {nso_version}"

    if not valid_deamon_status(daemon_status):
        msg += f"\nNSO not running. Status: {daemon_status}"
        print(msg)
        raise ValueError(msg)

    msg += f"\nNSO daemon running. Status: {daemon_status.upper()}"
    print(msg)


def valid_deamon_status(status: str) -> bool:
    # https://developer.cisco.com/docs/nso/guides/#!nso-system-management/monitoring-nso
    return "started" in status.lower()


def main() -> None:
    session = create_restconf_session()
    responses = [fetch_data(session, endpoint) for endpoint in API_ENDPOINTS]

    parsed_responses = [parse_xml(response) for response in responses]

    combined_results: dict = {}
    for parsed_response in parsed_responses:
        combined_results.update(classify_results(parsed_response))

    print_results(combined_results)


if __name__ == "__main__":
    main()
