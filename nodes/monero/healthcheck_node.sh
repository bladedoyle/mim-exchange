#!/bin/bash

curl -u foo:foo --digest http://$HOSTNAME:38081/json_rpc -d   '{"jsonrpc":"2.0","id":"0","method":"get_info"}'
