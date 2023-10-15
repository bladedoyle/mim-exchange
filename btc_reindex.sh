#!/bin/bash
docker stop bitcoind
export REINDEX=true
docker-compose up -d bitcoind
