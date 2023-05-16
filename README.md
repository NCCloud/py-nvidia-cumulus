# py-nvidia-cumulus
Unofficial Python API client for [Nvidia Cumulus Linux](https://docs.nvidia.com/networking-ethernet-software/cumulus-linux-54/pdf/).

## 📖 General information
The client aims to provide a thin wrapper over the [Cumulus OpenAPI specification](https://docs.nvidia.com/networking-ethernet-software/cumulus-linux-54/api/index.html).<br>
Therefore, it abstracts endpoints in a Pythonic fashion.

## 🛠 Installation

To install the package, run the following command:
```
pip install py-nvidia-cumulus
```

To install the package locally, clone this repository and run the following command:
```
pip install .
```

## 🚀 Quickstart

To start using the client, instantiate the Cumulus class with the host and authentication details
```python
from cumulus import Cumulus

nv = Cumulus(
    url="https://127.0.0.1:8765",
    auth=("cumulus", "password")
)
# nv.http_session = requests.Session() # set your own session if necessary
nv.http_session.verify = False # disable SSL verification if necessary
```

## 📄 Examples

1. Get the IP address of an interface relative to the OpenAPI endpoint
```python
# Instantiate the Cumulus class first
loopback = nv.interface.get('lo/ip/address')
print(loopback) # {'127.0.0.1/8': {}, '::1/128': {}}
```
2. Update interface configuration relative to the OpenAPI endpoint:
```python
# Instantiate the Cumulus class first
nv.revision.create() # create a revision
# patch an interface by providing the created revision ID, new data, and path to the object
nv.interface.patch(rev=nv.revision.rev,
                   data={"10.255.255.2/32": {}},
                   target_path="lo/ip/address")
nv.revision.apply() # apply the changes
nv.revision.is_applied() # watch the switch to make sure the changes were applied successfully
```

3. Here is a more complex example on how to deploy the entire switch configuration using the `root` endpoint.
We will also see how to get the diff between the current revision and the one we are applying.
```python
from cumulus import Cumulus

configuration = {"key": "value"}
nv = Cumulus(
    url="https://127.0.0.1:8765",
    auth=("cumulus", "password")
)
nv.http_session.verify = False # by default the switch uses self-signed certificate

nv.revision.create()
# remove previous configuration completely.
# Otherwise, only new keys will be applied and old ones won't be removed
nv.root.delete(nv.revision.rev)
nv.root.patch(rev=nv.revision.rev, data=configuration)

# see the changes between the current and pending revisions
print(nv.root.diff(nv.revision.rev))

nv.revision.apply()

# check switch status for 3 minutes
nv.revision.is_applied(retries=180)
# update revision to get the success/error message
nv.revision.refresh()
print(nv.revision.config)
```

4. Due to the very dynamic nature of Nvidia Cumulus API, there may not always be a model to cover the endpoint you want to use.
Adding your own model is very simple.
```python
from cumulus import Cumulus
from cumulus.models import BaseModel

nv = Cumulus(
    url="https://127.0.0.1:8765",
    auth=("cumulus", "password")
)
programming = BaseModel(client=nv, endpoint="system/forwarding/programming")
print(programming.get(endpoint_params={"rev": "applied"}))
```

## 🏷️ Versioning

We use [SemVer](http://semver.org/) for versioning.
To see the available versions, check the [PyPI page](https://pypi.org/project/py-nvidia-cumulus/#history) or [tags in this repository](https://github.com/NCCloud/py-nvidia-cumulus/tags).

## 🤝 Contribution

We welcome contributions, issues, and feature requests!
Also, please refer to our [contribution guidelines](https://github.com/NCCloud/py-nvidia-cumulus/blob/main/.github/CONTRIBUTING.md) for details.

Made with <span style="color: #e25555;">&hearts;</span> by [Namecheap Cloud Team](https://github.com/NCCloud)
