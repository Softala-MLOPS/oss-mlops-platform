# Incluster GitHub Action runner setup

The script `runner_setup.sh` is an alternative way to install the GitHub Action runner in to the MLOPS platform Kubernetes cluster as a pod.

Currently you have to run the script again once you restart the cluster as the token has expired. More details in the development documentation.

## Requirements

- The script uses `jq` command-line tool to parse a .json file
- The MLOPS platform running in the same environment as the script with `kubectl` associated to it
- `gh` command-line tool authentication in place for fetching the GitHub Action runner token
- Working repository set up for the ML project

## Usage

You can move the script `runner_setup.sh` and the deployment file `github-runner-deployment.yaml` in to more convenient location for running the script, but the script needs the deployment file to be in the same folder.

The script will ask for the organization (or username) and the repository name for fetching the token for the Action runner with `gh` from GitHub's API.

After running the script a GitHub Action runner pod should be part of the MLOPS cluster and associated to the working repository. You can check the runner status from repository's GitHub site Settings > Actions > Runners.

## Troubleshooting commands

Some of the commands require the full instanced name of the runner and some work with just the partial name.

Deleting the runner deployment from the cluster:
```bash
kubectl delete deployment github-runner --namespace=actions-runner
```

Deleting the runner's secrets from the namespace:
```bash
kubectl delete secret github-runner-secrets --namespace actions-runner
```

Accessing the runner inside the pod:
```bash
kubectl exec -it <github-runner-pod-name> -n actions-runner -- /bin/bash
```

Listing a status report for the runner:
```bash
kubectl describe pod <github-runner-pod-name> -n actions-runner 
```

Showing the deployment .yaml file used for the deployment:
```bash
kubectl get deployment github-runner -n actions-runner -o yaml
```

Kubernetes documentation:
https://kubernetes.io/docs/reference/kubectl/quick-reference/