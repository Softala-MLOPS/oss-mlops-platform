## Installation

> Supported OS: Linux, macOS.

Change the settings in [`config.env`](config.env) if needed.

Install the experimentation platform with:

```bash
./setup.sh [--test] [--debug]
```

- `--test`: Use this flag to run the tests right after installation.
- `--debug`: Print extra output information.

> **WARNING:** Using the `--test` flag will install the `requirements-tests.txt` in your current python environment.

## In-cluster GitHub Actions runner (ARC)

The setup script can install Actions Runner Controller and an autoscaling runner scale set.
Choose `y` at the “Install the in-cluster GitHub Actions runner” prompt, then provide:

- A GitHub repository or organization URL, such as `https://github.com/my-org/my-repo`
- A classic GitHub PAT with repository administration/self-hosted runner permissions

The PAT can also be supplied without a prompt:

```bash
GITHUB_CONFIG_URL=https://github.com/my-org/my-repo \
GITHUB_PAT=ghp_... \
./setup.sh
```

The PAT is passed directly to Kubernetes as an `arc-github-secret` Secret and is not written to `config.env`
or `.platform/.config`. Use a GitHub App for production where possible.

The default scale-set label is `arc-mlops`. A workflow can target it with:

```yaml
jobs:
  demo:
    runs-on: arc-mlops
```

Verify the ARC controller and scale set:

```bash
./scripts/test_arc_runner.sh
```

The `ARC in-cluster runner demo` workflow submits the development wine-quality pipeline
to Kubeflow and waits for the run to finish. A successful Actions job means the KFP run
completed with `Succeeded`; the run is also visible in the Kubeflow Pipelines UI.

## Deployment options

1. **Kubeflow:** Full Kubeflow deployment with all components.
2. **Kubeflow (without monitoring):** Full Kubeflow deployment without monitoring components (prometheus, grafana).
3. **Standalone KFP:** Standalone KFP deployment.
4. **Standalone KFP (without monitoring):** Standalone KFP deployment without monitoring components (prometheus, grafana).
5. **Standalone KFP and Kserve:** Standalone KFP and Kserve deployment.
6. **Standalone KFP and Kserve (without monitoring):** Standalone KFP and Kserve deployment without monitoring components (prometheus, grafana).

> The minimum recommended machine requirements are: 
> - **Kubeflow** options: 12 CPU cores, 25GB free disk space.
> - **Standalone KFP** options: 8 CPU cores, 18GB free disk space.

## Test the deployment (manually)

If you just deployed the platform, it will take a while to become ready. You can use
the following script to make sure the deployment is ready and all resource are running
correctly.

```bash
# install test requirements
pip install -r tests/requirements-tests.txt
```

```bash
# wait for the deployment to be ready
python tests/wait_deployment_ready.py --timeout 30
```

Run the tests with:

```bash
pytest tests/ [-vrP] [--log-cli-level=INFO]
```

*These are the same tests that are run automatically if you use the `--test` flag on installation.*


## Uninstall

Uninstall the MLOps Platform with:

```bash
./uninstall.sh
```

### Manual deletion

The `uninstall.sh` script should delete everything, but if you need to manually remove the platform, you can do it with:

```bash
# list kind clusters
kind get clusters

# delete the kind cluster
kind delete cluster --name [CLUSTER_NAME]
```

If you also installed the local docker registry:

```bash
# check if it is running (kind-registry)
$ docker ps

CONTAINER ID   IMAGE        COMMAND                  CREATED        STATUS        PORTS                       NAMES
6d7e3ef4e1fe   registry:2   "/entrypoint.sh /etc…"   2 hours ago    Up 2 hours    127.0.0.1:5001->5000/tcp    kind-registry
```

```bash
# delete it
docker rm -f $(docker ps -aqf "name=kind-registry")
```

## Troubleshooting

### Error: namespace "kubeflow-user-example-com" not found

This is not an error, and it is expected. Some of the things being deployed depend on other components, which need to be deployed and become ready first.
For example, the namespace `kubeflow-user-example-com` is created by a `kubeflow` component. That's why we deploy in a loop until everything is applied successfully.

Once the main `kubeflow` deployment is ready, the `kubeflow-user-example-com` namespace will be created, and the command should finish successfully.

However, if there is an underlying issue, the loop might never finish. In this case, you can check the status of the deployment with:

```bash
kubectl get pods --all-namespaces
```

Everything should be either in `Running` state, or being deployed (`ContainerCreating`). If there is an error, you will see it in the `STATUS` column.

If there is an error, you can check the pod errors with:

```bash
kubectl describe pod -n [NAMESPACE] [POD_NAME]

# check logs
kubectl logs -n [NAMESPACE] [POD_NAME]
```