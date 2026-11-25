#!/bin/bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPOSITORY_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)

if [[ -f "$REPOSITORY_ROOT/.platform/.config" ]]; then
  source "$REPOSITORY_ROOT/.platform/.config"
else
  source "$REPOSITORY_ROOT/config.env"
fi

: "${GITHUB_CONFIG_URL:?GITHUB_CONFIG_URL must be set}"
: "${GITHUB_PAT:?Set GITHUB_PAT in the environment or pass it through setup.sh}"

if [[ -z "$GITHUB_CONFIG_URL" ]]; then
  echo "GITHUB_CONFIG_URL must not be empty." >&2
  exit 1
fi

kubectl apply -f "$REPOSITORY_ROOT/deployment/namespace.yaml"

kubectl create secret generic arc-github-secret \
  --namespace arc-runners \
  --from-literal=github_token="$GITHUB_PAT" \
  --dry-run=client -o yaml | kubectl apply -f -

helm upgrade --install arc \
  --namespace arc-system \
  --create-namespace \
  --version "$ARC_CONTROLLER_VERSION" \
  --wait \
  --timeout 10m \
  oci://ghcr.io/actions/actions-runner-controller-charts/gha-runner-scale-set-controller

helm upgrade --install "$ARC_RUNNER_SCALE_SET_NAME" \
  --namespace arc-runners \
  --create-namespace \
  --version "$ARC_CONTROLLER_VERSION" \
  --values "$REPOSITORY_ROOT/deployment/arc-runner-values.yaml" \
  --set-string "githubConfigUrl=$GITHUB_CONFIG_URL" \
  --set-string "runnerScaleSetName=$ARC_RUNNER_SCALE_SET_NAME" \
  --set "minRunners=$ARC_MIN_RUNNERS" \
  --set "maxRunners=$ARC_MAX_RUNNERS" \
  --set-string "template.spec.containers[0].image=ghcr.io/actions/actions-runner:$ARC_RUNNER_VERSION" \
  --wait \
  --timeout 10m \
  oci://ghcr.io/actions/actions-runner-controller-charts/gha-runner-scale-set

kubectl wait --for=condition=Available \
  --namespace arc-system \
  --timeout=5m \
  deployment/arc-gha-rs-controller

echo "ARC runner scale set '$ARC_RUNNER_SCALE_SET_NAME' installed."
