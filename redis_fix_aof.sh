#!/bin/bash

docker stop redis
docker run -it --rm -v exchange:/data:rw -u redis redis:7.0.7 \
    rm -f /data/appendonlydir/appendonly.aof.2.incr.aof.bak; \
    cp /data/appendonlydir/appendonly.aof.2.incr.aof /data/appendonlydir/appendonly.aof.2.incr.aof.bak; \
    redis-check-aof --fix appendonlydir/appendonly.aof.2.incr.aof
docker start redis
