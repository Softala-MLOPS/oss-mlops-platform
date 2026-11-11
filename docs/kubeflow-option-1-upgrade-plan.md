# Option 1 upgrade plan

Companion to [kubeflow-setup-option-1-vs-5.md](kubeflow-setup-option-1-vs-5.md). Branch `kubeflow-option1-vs-option5`, cut from `platform-upgrade` at `2c387ba`.

Option 1 is `setup.sh` menu `[1]`, `deployment/envs/kubeflow-monitoring`. This plan covers the Kubeflow pieces that menu installs and that the comparison left behind the already-upgraded stack. KServe stays out of scope.

## Returned patches

`295c746` (`KFP fixes`, 12 Nov 2025) upgraded the pipeline manifests from `gcr.io/ml-pipeline:2.0.0-alpha.7` to the Kubeflow Pipelines 2.5 layout and deleted:

`deployment/kubeflow/manifests/apps/pipeline/upstream/env/cert-manager/platform-agnostic-multi-user/delete-cache-deployer.yaml`

That file had been in the tree since the Kubeflow import `d624c5c` (Oct 2023). The same commit rewrote the overlay `kustomization.yaml` to load six split files that upstream adds in that upgrade. Those six files were not part of the commit, so `kustomize build deployment/envs/kubeflow-monitoring` failed. Option 5 does not use this overlay.

The six documents are back, split to the paths the current kustomization already names:

- `patches/delete.clusterrole.cache-deployer.yaml`
- `patches/delete.crb.cache-deployer.yaml`
- `patches/delete.deployment.cache-deployer.yaml`
- `patches/delete.role.cache-deployer.yaml`
- `patches/delete.rolebinding.cache-deployer.yaml`
- `patches/delete.sa.cache-deployer.yaml`

Each document is the matching resource from `git show 295c746^:.../delete-cache-deployer.yaml`. Restoring that single file at the old path would not have been loaded. With these files present, `kustomize build deployment/envs/kubeflow-monitoring` completes, `cache-deployer-deployment` is absent from the output, and `cache-server` still receives `--tls_cert_filename=tls.crt` and `--tls_key_filename=tls.key` from the inline patches that were already in the kustomization.

A later sync of this overlay from upstream must bring `patches/` with it. The `dev` overlay's shorter `delete-cache-deployer.yaml` is a different file and was left as it is. Option 1 does not install the `dev` overlay.

## Already on the upgraded stack

Leave these in place. They are shared with option 5, or they were already bumped on `platform-upgrade`.

| Piece | On this branch | Notes |
| --- | --- | --- |
| Kubernetes | kind node `v1.37.0` | `scripts/create_cluster.sh` |
| Istio | 1.29.0 | Both in-cluster kustomizations use `common/istio-1-29` |
| cert-manager | 1.19.4 | Shared |
| Kubeflow Pipelines | 2.16.0 | Shared base. Local crashloop fixes in `ml-pipeline-apiserver-deployment.yaml` and `metadata-envoy-deployment.yaml` stay |
| Katib | 0.19.0 | Option 1 only. Matches Kubeflow 1.11 |
| Dex | 2.45.0 | Option 1 only. Ahead of Kubeflow 1.11 (2.43.1 / 2.44) |
| Knative, MinIO/Silo, MLflow, Grafana, Prometheus | already bumped | Shared with option 5 |

Kubeflow 1.11 (15 Dec 2025) validated Kubernetes 1.32, with the release text also saying 1.33+, Istio 1.28.0, cert-manager 1.16.1, and Pipelines 2.15.0. Istio 1.29.0 landed on the manifests line on 26 Feb 2026, after that release. This branch is past 1.11 on Kubernetes, Istio, cert-manager, and Pipelines. Re-syncing those four from the 1.11 tag would move them backwards.

## What option 1 still runs old

The notebook and dashboard images are `v1.10.0`. Kubeflow 1.11 still ships that same tag for central dashboard, Jupyter web app, notebook controller, KFAM, profile controller, PodDefaults, TensorBoard, and the volumes web app. There is no newer tag in that release to copy. PVC viewer on this branch is also `v1.10.0`.

Two option-1 components are actually behind 1.11:

| Component | This branch | Kubeflow 1.10 and 1.11 |
| --- | --- | --- |
| Training operator | `ghcr.io/kubeflow/training-v1/training-operator:v1-3f15cb8` with the CRDs under `apps/training-operator/upstream/base` | Training Operator v1.9.2. 1.11 also offers Trainer v2.1.0 as a separate component |
| OIDC authservice | `docker.io/kubeflowmanifestswg/oidc-authservice:e236439` | 1.11 documents oauth2-proxy as the OIDC client (dependency table 7.10.0, release text 7.13). This repo already has `common/oidc-client/oauth2-proxy` with `newTag: v7.14.3`. Option 1 does not install it |

The `v1.10.0` controllers were built for about Kubernetes 1.31–1.32 and Istio 1.24. They are the images 1.11 still uses, and 1.11's tested window stops around Kubernetes 1.33 and Istio 1.28. Running them on Kubernetes 1.37 and Istio 1.29 is outside both matrices. Their VirtualServices are `networking.istio.io/v1alpha3`, which the Istio 1.29 CRDs in this tree still serve, so the objects apply. Whether the controllers and the old authservice work at runtime is an install test, not a tag bump.

## Order of work

1. Keep the six restored delete patches. Do not revert `kustomization.yaml` to `patchesStrategicMerge`.
2. Build and apply option 1 on the current kind cluster (`kindest/node:v1.37.0`). Confirm every option-1 workload from the comparison doc reaches Running, then log in through Dex, open the central dashboard, create a notebook, and open Pipelines from the dashboard. The pipeline UI is the 2.16.0 frontend. The dashboard only frames it and still expects the `kubeflow-userid` header.
3. Replace the training operator as a set. Take the v1.9.2 manifests (image and CRDs together) into `apps/training-operator/upstream`. Changing `newTag` alone leaves the old CRDs in place. Trainer v2 is a second API (`TrainJob`) and is a separate decision. It does not replace this step if existing TFJob, PyTorchJob, and MPIJob manifests must keep working.
4. Change the auth path only if step 2 cannot log in. Point the option-1 kustomization at `common/oidc-client/oauth2-proxy` instead of `oidc-authservice`, and keep Dex. Dex is already 2.45.0.
5. Leave the shared pipeline base on 2.16.0, including the two crashloop fixes and the Silo image for MinIO. A future copy of the cert-manager multi-user overlay from upstream Pipelines 2.16 has to include `patches/`. It must not overwrite `ml-pipeline-apiserver-deployment.yaml` or `metadata-envoy-deployment.yaml` without replaying those fixes.

## Check after install

- `kustomize build deployment/envs/kubeflow-monitoring` exits 0 and does not emit `cache-deployer-deployment`.
- Pods in `auth`, `istio-system`, and `kubeflow` for Dex, authservice, dashboard, Jupyter, notebook controller, profiles, PVC viewer, volumes, TensorBoard, training operator, Katib, and the pipeline profile controller are Running.
- A notebook starts in `kubeflow-user-example-com`.
- The Pipelines page in the dashboard loads the 2.16.0 UI.
- A TFJob or PyTorchJob is admitted after the training-operator manifest sync, if that step is done.
