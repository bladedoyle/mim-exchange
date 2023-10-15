#!/bin/bash
docker stop dash
export REINDEX=true
docker-compose up -d dash
