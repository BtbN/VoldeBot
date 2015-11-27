#!/bin/bash
cd "$(dirname "$0")"
wget https://twitchemotes.com/api_cache/v2/global.json -O global_emotes.json || exit -1
wget http://twitchemotes.com/api_cache/v2/subscriber.json -O subscriber_emotes.json || exit -1
