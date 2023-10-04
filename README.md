# NSO hello world using Restconf

Simple hello world in NSO using Restconf.

The script prints the status of the NCS deamon and the NCS version. Validates the deamon is in "started" state. If the deamon is not in _"started"_ status, the script will raise an exception.

This script can be useful to monitor continously the status of NSO.

For real use, consider using environment variables rather than hardcoding credentials for your NSO instance.

For demo purposes, the script connects to the NSO always-On sandbox, so you can test it right away.

Below are the restconf paths used to get the data.

```javascript
/restconf/data/tailf-ncs-monitoring:ncs-state/daemon-status
/restconf/data/tailf-ncs-monitoring:ncs-state/version
```

### How to use it

Install dependencies

```bash
pip install -r requirements.txt
```

To run the script do:

```bash
python hello_world.py
```

Output printed

```bash
❯ python hello_world.py

NSO version: 5.4.3.3
NSO daemon running. Status: STARTED
❯
```
