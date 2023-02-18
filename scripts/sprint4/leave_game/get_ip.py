import json
import os
import sys
import docker

postgres_id = sys.argv[1]

client = docker.APIClient()

container = client.inspect_container(postgres_id)
networks = container['NetworkSettings']['Networks']
networks_pairs = json.dumps(networks).split(',')
for pair in networks_pairs:
    if pair.find('IPAddress') != -1:
        pair = pair.split(': ')
        print(pair[1][1:-1])
        exit()
