import os
from cassandra.cluster import Cluster

cassandra_host = os.getenv("CASSANDRA_HOST", "127.0.0.1")
cluster = Cluster([cassandra_host], port=9042)
session = cluster.connect("tinyurl")
