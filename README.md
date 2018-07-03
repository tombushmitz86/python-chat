# Python client-server chat WebSockets based

### requirements
python >= 3.6
## init
run ```make init``` on project root

## checks
run ```make check``` for flakes

## server

```
server.py --port(default 3030)
```
will run server locally on 0.0.0.0:3030


## client

```
client.py -H=<host_address> -p=<port>
```

connects to server on ```<host>:<port>```


TODO:
* docs
* errors handling
* coroutins holds websockets when executing tasks 
