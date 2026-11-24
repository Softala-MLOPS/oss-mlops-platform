#!/bin/bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPOSITORY_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)

if [[ -f "$REPOSITORY_ROOT/.platform/.config" ]]; then
  source "$REPOSITORY_ROOT/.platform/.config"
else
  source "$REPOSITORY_ROOT/config.env"
fi

kubectl get namespace arc-runners
kubectl get namespace arc-system

kubectl get deployment \
  --namespace arc-system \
  arc-gha-rs-controller

kubectl get pods --namespace arc-runners
kubectl get autoscalingrunnersets \
  --namespace arc-runners

kubectl wait --for=condition=Available \
  --namespace arc-system \
  --timeout=5m \
  deployment/arc-gha-rs-controller

scale_set_name="${ARC_RUNNER_SCALE_SET_NAME:-arc-mlops}"
scale_set_phase=$(kubectl get autoscalingrunnerset \
  --namespace arc-runners \
  "$scale_set_name" \
  --output jsonpath='{.status.phase}')

if [[ "$scale_set_phase" != "Running" ]]; then
  echo "ARC scale set '$scale_set_name' is not Running (phase: ${scale_set_phase:-Unknown})." >&2
  exit 1
fi

echo "ARC controller and scale set are healthy."
