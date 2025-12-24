#!/bin/bash
# wait_for_mongo.sh

set -e

host="$1"
shift
cmd="$@"

echo "Waiting for MongoDB at $host..."

until nc -z "$host" 27017; do
  echo "MongoDB is unavailable - sleeping"
  sleep 2
done

echo "MongoDB is up - executing command"
exec $cmd
