#!/bin/bash
docker stop zcash
export REINDEX=true
docker-compose up -d zcash
