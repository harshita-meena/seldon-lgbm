#!/bin/bash

function get_num_cpus() {
  # Determine OSTYPE and get number of CPU's
  if [[ "$OSTYPE" == darwin* ]]; then
    NUM_CPUS=$(sysctl -n hw.ncpu)
  elif [[ "$OSTYPE" == linux* ]]; then
    NUM_CPUS=$(nproc)
  fi
  echo ${NUM_CPUS}
}

# Change working directory
cd /app

ENTRYPOINT="${SELDON_ENTRYPOINT:?The SELDON_ENTRYPOINT environment variable must be set and be non-empty.}"

NUM_CPUS=$(get_num_cpus)
echo "NUM_CPUS=${NUM_CPUS}"

# Default number of threads to 1 for thread safety.
GUNICORN_THREADS="${SELDON_REST_THREADS:-1}"
# Default number of REST gunicorn workers is half the number of CPU's
# $((NUM_CPUS/2)) rounds down
GUNICORN_WORKERS="${SELDON_REST_WORKERS:-$((NUM_CPUS/2))}"

# Default number of threads to 1 for thread safety.
GRPC_THREADS="${SELDON_GRPC_THREADS:-1}"
# Default number of GRPC workers is half the number of CPU's
GRPC_WORKERS="${SELDON_GRPC_WORKERS:-$((NUM_CPUS/2))}"

set -x
exec seldon-core-microservice ${ENTRYPOINT} \
  --service-type MODEL \
  --http-port 80 \
  --grpc-port 79 \
  --workers ${GUNICORN_WORKERS} \
  --threads ${GUNICORN_THREADS} \
  --grpc-workers ${GRPC_WORKERS} \
  --grpc-threads ${GRPC_THREADS}
