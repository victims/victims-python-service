## Victims Python Service

Victims Python Service is a microservice that provides Python hash information to the Victims REST project. It uses the same interface as victims-java-service.

### How does it work?

the `hash` endpoint is called passing some files to hash. This service explodes the python whl or egg and hashes the code files and package itself. Those hashes are then returned to the caller as JSON.

### API Documentation

#### POST /hash 

```
$ curl -X POST -F "library2=@six-1.11.0-py2.py3-none-any.whl" http://localhost:8080/hash
[
{"hash": "b71248ef493ac12b115fdf06206090078fac147ec6ab6efb67b87e2b9c07a69d55bf8e70fde713d81735a99e560a17da714274e2ecbd7b0200d2e9a0f39970a7", "name": "six-1.11.0-py2.py3-none-any.whl", "verison": "1.11.0", "files": [{"name": "/tmp/tmprjeahd0x/_extraction/six.py", "hash": "5cd9ece76f3c7a0021f819943b3caaf2cf740f58bd0924d639f5d0bfc35d1d5842bf2a245156a3aaf0b3e253a4b71b4cc4afdcd3aea5ac4639768dedbe4f55c3"}]
]
```


#### GET /health

Checks the service is up and can access the database

```
$ curl -v http://localhost:8080/healthz

> GET /healthz HTTP/1.1
> Host: localhost:8080
> Accept: */*
> 
< HTTP/1.1 200 OK
< 

```

### Building this service

Run a local service:
`python3 server.py`

### Running with Docker

Package the service as a Docker image using S2I:
`sudo s2i build -E .s2i/environment . registry.access.redhat.com/rhscl/python-36-rhel7:latest victims-python`

Run
`sudo docker run -ti --rm -p 127.0.0.1:8080:8080 victims-python`
