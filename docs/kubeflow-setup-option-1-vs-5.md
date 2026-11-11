# Kubeflow install split: `setup.sh` option 1 vs option 5

Branch analyzed: `platform-upgrade` at `2c387ba` (`upgrade grafana and prometheus versions to target`).
This note lives on `kubeflow-option1-vs-option5`, branched from that commit.

KServe is left out of the three categories below. A short exclusion list is at the end.

## What the two menu choices actually build

`setup.sh` selects a kustomize root and applies it:

| Menu | Prompt | `DEPLOYMENT_OPTION` | Kustomize root |
| --- | --- | --- | --- |
| 1 | Kubeflow (all components) | `kubeflow-monitoring` | `deployment/envs/kubeflow-monitoring` |
| 5 | Standalone KFP and KServe | `standalone-kfp-kserve-monitoring` | `deployment/envs/standalone-kfp-kserve-monitoring` |

Kubeflow entry packages:

| Option | In-cluster package | Pipeline package |
| --- | --- | --- |
| 1 | `deployment/kubeflow/manifests/in-cluster-setup/kubeflow` | `apps/pipeline/upstream/env/cert-manager/platform-agnostic-multi-user` (multi-user KFP) |
| 5 | `deployment/kubeflow/manifests/in-cluster-setup/standalone-kfp-kserve` | `apps/pipeline/upstream/cluster-scoped-resources` plus `apps/pipeline/upstream/env/platform-agnostic-emissary` (namespace-scoped standalone KFP) |

Both env roots also pull `deployment/mlflow/env/local` and `deployment/monitoring`. Those are platform add-ons. They are listed under the common category so the installed set is complete, and marked as outside the Kubeflow manifests.

Workloads below are Deployments and StatefulSets produced by `kustomize build` of those two roots (kustomize 5.2.1). Container name and image were compared, then args and env. The six cache-deployer delete patches option 1 needs are restored on this branch; see [kubeflow-option-1-upgrade-plan.md](kubeflow-option-1-upgrade-plan.md).

Recent `platform-upgrade` commits that look KFP-specific edit the **shared** pipeline base, so they land in both options:

| Commit | What changed | Which category |
| --- | --- | --- |
| `7288ab9` fix kubeflow ml-pipeline crashloop | `apps/pipeline/upstream/base/pipeline/ml-pipeline-apiserver-deployment.yaml` | Common file. Both options run `kubeflow/ml-pipeline`. |
| `db2acda` fix metadata-envoy-deployment crashloop | `apps/pipeline/upstream/base/metadata/base/metadata-envoy-deployment.yaml` | Common file. Both options run `kubeflow/metadata-envoy-deployment`. |
| `53da74c` upgrade kubeflow components | KFP image tags to `2.16.0` in the shared base; Knative and cert-manager manifests | Common. The same commit also bumps Katib and Dex, which are option 1 only, and `contrib/kserve/kserve/kserve-runtimes.yaml`, which is excluded here. |
| `9d78684` / `fc26d44` Istio 1.29 | Both in-cluster kustomizations switched from `common/istio-1-17` to `common/istio-1-29` | Common Istio and cluster-local-gateway paths. |

Standalone KFP is the pipeline **entrypoint** used by option 5 (and by menu options 3 and 4). It is not a separate copy of the pipeline containers.

---

## 1. Only in option 5

### Container workload

One Kubeflow workload is installed by option 5 and removed from option 1.

| Namespace | Workload | Container | Image |
| --- | --- | --- | --- |
| `kubeflow` | Deployment `cache-deployer-deployment` | `main` | `ghcr.io/kubeflow/kfp-cache-deployer:2.16.0` |

The Deployment YAML is not unique to option 5. It lives in the shared pipeline base (`apps/pipeline/upstream/base/cache-deployer/`), and option 1's multi-user install pulls that base in. Option 1's cert-manager overlay is written to delete it:

`apps/pipeline/upstream/env/cert-manager/platform-agnostic-multi-user/kustomization.yaml` references:

- `patches/delete.clusterrole.cache-deployer.yaml`
- `patches/delete.crb.cache-deployer.yaml`
- `patches/delete.deployment.cache-deployer.yaml`
- `patches/delete.role.cache-deployer.yaml`
- `patches/delete.rolebinding.cache-deployer.yaml`
- `patches/delete.sa.cache-deployer.yaml`

Those six files were missing after `295c746`. They are restored on this branch from the combined `delete-cache-deployer.yaml` that commit deleted. With them present, the overlay deletes cache-deployer and gives `cache-server` `--tls_cert_filename=tls.crt` and `--tls_key_filename=tls.key`. `kustomize build deployment/envs/kubeflow-monitoring` completes, and the built manifest has no `cache-deployer-deployment`.

### Files referenced only by option 5

16 kustomize files. They select the standalone pipeline entry and namespace-scoped Argo RBAC. They do not add a second copy of the KFP API, UI, MinIO, or MySQL manifests.

- `deployment/envs/standalone-kfp-kserve-monitoring/kustomization.yaml`
- `deployment/kubeflow/manifests/in-cluster-setup/standalone-kfp-kserve/kustomization.yaml`
- `deployment/custom/kubeflow-custom/env/standalone-kfp-kserve/kustomization.yaml`
- `deployment/kubeflow/manifests/apps/pipeline/upstream/cluster-scoped-resources/kustomization.yaml`
- `deployment/kubeflow/manifests/apps/pipeline/upstream/cluster-scoped-resources/namespace.yaml`
- `deployment/kubeflow/manifests/apps/pipeline/upstream/cluster-scoped-resources/params.yaml`
- `deployment/kubeflow/manifests/apps/pipeline/upstream/env/platform-agnostic-emissary/kustomization.yaml`
- `deployment/kubeflow/manifests/apps/pipeline/upstream/env/platform-agnostic/kustomization.yaml`
- `deployment/kubeflow/manifests/apps/pipeline/upstream/third-party/application/cluster-scoped/kustomization.yaml`
- `deployment/kubeflow/manifests/apps/pipeline/upstream/third-party/application/cluster-scoped/application-crd.yaml`
- `deployment/kubeflow/manifests/apps/pipeline/upstream/third-party/argo/installs/namespace/kustomization.yaml`
- `deployment/kubeflow/manifests/apps/pipeline/upstream/third-party/argo/installs/namespace/workflow-controller-deployment-patch.json`
- `deployment/kubeflow/manifests/apps/pipeline/upstream/third-party/argo/installs/namespace/cluster-scoped/kustomization.yaml`
- `deployment/kubeflow/manifests/apps/pipeline/upstream/third-party/argo/upstream/manifests/namespace-install/workflow-controller-rbac/kustomization.yaml`
- `deployment/kubeflow/manifests/apps/pipeline/upstream/third-party/argo/upstream/manifests/namespace-install/workflow-controller-rbac/workflow-controller-role.yaml`
- `deployment/kubeflow/manifests/apps/pipeline/upstream/third-party/argo/upstream/manifests/namespace-install/workflow-controller-rbac/workflow-controller-rolebinding.yaml`

`kserve-deployer.yaml` next to that custom overlay is KServe RBAC and is excluded.

### Same containers, option-5-only settings

These workloads are in both installs (category 2). Option 5's standalone entry changes how they run:

| Workload | Option 5 difference |
| --- | --- |
| `kubeflow/workflow-controller` | Extra arg `--namespaced`. Image stays `quay.io/argoproj/workflow-controller:v3.5.14`. Executor image stays `quay.io/argoproj/argoexec:v3.5.14`. |
| `kubeflow/ml-pipeline` | No `KUBEFLOW_USERID_HEADER` or `KUBEFLOW_USERID_PREFIX`. Image stays `ghcr.io/kubeflow/kfp-api-server:2.16.0`. |
| `kubeflow/ml-pipeline-ui` | No `DEPLOYMENT=KUBEFLOW`, `ENABLE_AUTHZ=true`, artifact proxy, or Kubeflow user-id header. Image stays `ghcr.io/kubeflow/kfp-frontend:2.16.0`. |
| `kubeflow/ml-pipeline-persistenceagent` | `NAMESPACE` comes from the pod namespace field. Option 1 sets `NAMESPACE` to empty (all namespaces). |
| `kubeflow/ml-pipeline-scheduledworkflow` | Same namespace-field behavior. |
| `kubeflow/ml-pipeline-viewer-crd` | Same namespace-field behavior. |
| `kubeflow/metadata-writer` | `NAMESPACE_TO_WATCH` comes from the pod namespace field. Option 1 sets it empty. |
| `kubeflow/cache-server` | No TLS cert/key args. `NAMESPACE_TO_WATCH` comes from the pod namespace field. Image stays `ghcr.io/kubeflow/kfp-cache-server:2.16.0`. |

---

## 2. Common between option 1 and option 5

37 workloads resolve to the same namespace, name, and container image. Eight of them differ in args or env; those are the table in category 1. The other 29 match including args and env.

### Kubeflow Pipelines (shared base)

| Workload | Container | Image |
| --- | --- | --- |
| `kubeflow/ml-pipeline` | `ml-pipeline-api-server` | `ghcr.io/kubeflow/kfp-api-server:2.16.0` |
| `kubeflow/ml-pipeline-ui` | `ml-pipeline-ui` | `ghcr.io/kubeflow/kfp-frontend:2.16.0` |
| `kubeflow/ml-pipeline-persistenceagent` | `ml-pipeline-persistenceagent` | `ghcr.io/kubeflow/kfp-persistence-agent:2.16.0` |
| `kubeflow/ml-pipeline-scheduledworkflow` | `ml-pipeline-scheduledworkflow` | `ghcr.io/kubeflow/kfp-scheduled-workflow-controller:2.16.0` |
| `kubeflow/ml-pipeline-viewer-crd` | `ml-pipeline-viewer-crd` | `ghcr.io/kubeflow/kfp-viewer-crd-controller:2.16.0` |
| `kubeflow/ml-pipeline-visualizationserver` | `ml-pipeline-visualizationserver` | `ghcr.io/kubeflow/kfp-visualization-server:2.16.0` |
| `kubeflow/metadata-envoy-deployment` | `container` | `ghcr.io/kubeflow/kfp-metadata-envoy:2.16.0` |
| `kubeflow/metadata-grpc-deployment` | `container` | `gcr.io/tfx-oss-public/ml_metadata_store_server:1.14.0` |
| `kubeflow/metadata-writer` | `main` | `ghcr.io/kubeflow/kfp-metadata-writer:2.16.0` |
| `kubeflow/cache-server` | `server` | `ghcr.io/kubeflow/kfp-cache-server:2.16.0` |
| `kubeflow/mysql` | `mysql` | `gcr.io/ml-pipeline/mysql:8.0.26` |
| `kubeflow/minio` | `minio` | `pgsty/silo:RELEASE.2026-09-16T00-00-00Z` |
| `kubeflow/workflow-controller` | `workflow-controller` | `quay.io/argoproj/workflow-controller:v3.5.14` |

`ml-pipeline` also injects the same driver images in both options: `ghcr.io/kubeflow/kfp-driver:2.16.0` and `ghcr.io/kubeflow/kfp-launcher:2.16.0`.

The crashloop fixes (`ml-pipeline-apiserver-deployment.yaml`, `metadata-envoy-deployment.yaml`) and the `2.16.0` tag bumps are in this shared base.

### Cert-manager, Istio, Knative

Both in-cluster packages include these, and the built containers match.

| Workload | Container | Image |
| --- | --- | --- |
| `cert-manager/cert-manager` | `cert-manager-controller` | `quay.io/jetstack/cert-manager-controller:v1.19.4` |
| `cert-manager/cert-manager-cainjector` | `cert-manager-cainjector` | `quay.io/jetstack/cert-manager-cainjector:v1.19.4` |
| `cert-manager/cert-manager-webhook` | `cert-manager-webhook` | `quay.io/jetstack/cert-manager-webhook:v1.19.4` |
| `istio-system/istiod` | `discovery` | `docker.io/istio/pilot:1.29.0` |
| `istio-system/istio-ingressgateway` | `istio-proxy` | `docker.io/istio/proxyv2:1.29.0` |
| `istio-system/cluster-local-gateway` | `istio-proxy` | `docker.io/istio/proxyv2:1.29.0` |
| `knative-serving/activator` | `activator` | `gcr.io/knative-releases/knative.dev/serving/cmd/activator@sha256:c2994c2b6c2c7f38ad1b85c71789bf1753cc8979926423c83231e62258837cb9` |
| `knative-serving/autoscaler` | `autoscaler` | `gcr.io/knative-releases/knative.dev/serving/cmd/autoscaler@sha256:8319aa662b4912e8175018bd7cc90c63838562a27515197b803bdcd5634c7007` |
| `knative-serving/controller` | `controller` | `gcr.io/knative-releases/knative.dev/serving/cmd/controller@sha256:98a2cc7fd62ee95e137116504e7166c32c65efef42c3d1454630780410abf943` |
| `knative-serving/webhook` | `webhook` | `gcr.io/knative-releases/knative.dev/serving/cmd/webhook@sha256:4305209ce498caf783f39c8f3e85dfa635ece6947033bf50b0b627983fd65953` |
| `knative-serving/domain-mapping` | `domain-mapping` | `gcr.io/knative-releases/knative.dev/serving/cmd/domain-mapping@sha256:f66c41ad7a73f5d4f4bdfec4294d5459c477f09f3ce52934d1a215e32316b59b` |
| `knative-serving/domainmapping-webhook` | `domainmapping-webhook` | `gcr.io/knative-releases/knative.dev/serving/cmd/domain-mapping-webhook@sha256:7368aaddf2be8d8784dc7195f5bc272ecfe49d429697f48de0ddc44f278167aa` |
| `knative-serving/net-istio-controller` | `controller` | `gcr.io/knative-releases/knative.dev/net-istio/cmd/controller@sha256:421aa67057240fa0c56ebf2c6e5b482a12842005805c46e067129402d1751220` |
| `knative-serving/net-istio-webhook` | `webhook` | `gcr.io/knative-releases/knative.dev/net-istio/cmd/webhook@sha256:bfa1dfea77aff6dfa7959f4822d8e61c4f7933053874cd3f27352323e6ecd985` |
| `knative-eventing/eventing-controller` | `eventing-controller` | `gcr.io/knative-releases/knative.dev/eventing/cmd/controller@sha256:92967bab4ad8f7d55ce3a77ba8868f3f2ce173c010958c28b9a690964ad6ee9b` |
| `knative-eventing/eventing-webhook` | `eventing-webhook` | `gcr.io/knative-releases/knative.dev/eventing/cmd/webhook@sha256:ebf93652f0254ac56600bedf4a7d81611b3e1e7f6526c6998da5dd24cdc67ee1` |
| `knative-eventing/pingsource-mt-adapter` | `dispatcher` | `gcr.io/knative-releases/knative.dev/eventing/cmd/mtping@sha256:6d35cc98baa098fc0c5b4290859e363a8350a9dadc31d1191b0b5c9796958223` |

Knative is part of the standalone-KFP kustomization in this repo, including menu options 3 and 4, which do not install KServe. It is grouped here as a shared install, separate from the KServe controller.

### Platform add-ons both menus install

| Workload | Container | Image |
| --- | --- | --- |
| `mlflow/mlflow` | `mlflow` | `ghcr.io/oss-mlops-platform/mlflow_v2:0.0.2` |
| `mlflow/mlflow-minio` | `mlflow-minio` | `pgsty/silo:RELEASE.2026-09-16T00-00-00Z` |
| `mlflow/postgres` | `postgres` | `postgres:18.6` |
| `monitoring/grafana` | `grafana` | `grafana/grafana:13.2` |
| `monitoring/prometheus-deployment` | `prometheus` | `prom/prometheus:v3.13.4` |
| `monitoring/alertmanager` | `alertmanager` | `prom/alertmanager:latest` |
| `monitoring/prometheus-pushgateway` | `prometheus-pushgateway` | `prom/pushgateway` (tag unset in the manifest) |

`2c387ba` changes Grafana and Prometheus only. Both option 1 and option 5 include `deployment/monitoring`, so that commit applies to both.

### Common files

181 kustomize-referenced files are on both roots. 138 of those are under the Kubeflow manifests or `deployment/custom/kubeflow-custom/base`. The rest are MLflow (20) and monitoring (23).

| Area | Files | Role |
| --- | --- | --- |
| `apps/pipeline` shared base | 94 | Generic KFP install, metadata, cache server, cache-deployer YAML, MinIO, MySQL, Argo workflow controller base |
| `common/istio-1-29` | 20 | CRDs, istiod, ingress gateway, cluster-local gateway, Kubeflow Istio resources |
| `common/knative` | 18 | Serving, net-istio, eventing |
| `common/cert-manager` | 4 | cert-manager and the Kubeflow issuer |
| `custom/kubeflow-custom/base` | 2 | `aws-secret` Secret. Option 1 applies it in `kubeflow-user-example-com`. Option 5 applies it in `kubeflow`. |
| `deployment/mlflow` | 20 | MLflow, its Postgres, its MinIO |
| `deployment/monitoring` | 23 | Prometheus, Grafana, Alertmanager |

Shared namespaces: `cert-manager`, `istio-system`, `knative-serving`, `knative-eventing`, `kubeflow`, `mlflow`, `monitoring`.

---

## 3. Only in option 1

### Container workloads

18 workloads. All of them are the full Kubeflow multi-user surface: login, dashboard, notebooks, Katib, TensorBoard, training, and the multi-user pipeline profile controller.

| Namespace | Workload | Containers | Image |
| --- | --- | --- | --- |
| `auth` | Deployment `dex` | `dex` | `ghcr.io/dexidp/dex:v2.45.0` |
| `istio-system` | StatefulSet `oidc-authservice` | `authservice` | `docker.io/kubeflowmanifestswg/oidc-authservice:e236439` |
| `kubeflow` | Deployment `centraldashboard` | `centraldashboard` | `ghcr.io/kubeflow/kubeflow/central-dashboard:v1.10.0` |
| `kubeflow` | Deployment `admission-webhook-deployment` | `admission-webhook` | `ghcr.io/kubeflow/kubeflow/poddefaults-webhook:v1.10.0` |
| `kubeflow` | Deployment `jupyter-web-app-deployment` | `jupyter-web-app` | `ghcr.io/kubeflow/kubeflow/jupyter-web-app:v1.10.0` |
| `kubeflow` | Deployment `notebook-controller-deployment` | `manager` | `ghcr.io/kubeflow/kubeflow/notebook-controller:v1.10.0` |
| `kubeflow` | Deployment `profiles-deployment` | `kfam`, `manager` | `ghcr.io/kubeflow/kubeflow/kfam:v1.10.0`, `ghcr.io/kubeflow/kubeflow/profile-controller:v1.10.0` |
| `kubeflow` | Deployment `pvcviewer-controller-manager` | `manager`, `kube-rbac-proxy` | `ghcr.io/kubeflow/kubeflow/pvcviewer-controller:v1.10.0`, `quay.io/brancz/kube-rbac-proxy:v0.13.1` |
| `kubeflow` | Deployment `volumes-web-app-deployment` | `volumes-web-app` | `ghcr.io/kubeflow/kubeflow/volumes-web-app:v1.10.0` |
| `kubeflow` | Deployment `tensorboard-controller-deployment` | `manager`, `kube-rbac-proxy` | `ghcr.io/kubeflow/kubeflow/tensorboard-controller:v1.10.0`, `quay.io/brancz/kube-rbac-proxy:v0.8.0` |
| `kubeflow` | Deployment `tensorboards-web-app-deployment` | `tensorboards-web-app` | `ghcr.io/kubeflow/kubeflow/tensorboards-web-app:v1.10.0` |
| `kubeflow` | Deployment `training-operator` | `training-operator` | `ghcr.io/kubeflow/training-v1/training-operator:v1-3f15cb8` |
| `kubeflow` | Deployment `katib-controller` | `katib-controller` | `ghcr.io/kubeflow/katib/katib-controller:v0.19.0` |
| `kubeflow` | Deployment `katib-db-manager` | `katib-db-manager` | `ghcr.io/kubeflow/katib/katib-db-manager:v0.19.0` |
| `kubeflow` | Deployment `katib-ui` | `katib-ui` | `ghcr.io/kubeflow/katib/katib-ui:v0.19.0` |
| `kubeflow` | Deployment `katib-mysql` | `katib-mysql` | `mysql:8.0.29` |
| `kubeflow` | Deployment `kubeflow-pipelines-profile-controller` | `profile-controller` | `public.ecr.aws/docker/library/python:3.12` |
| `kubeflow` | StatefulSet `metacontroller` | `metacontroller` | `ghcr.io/metacontroller/metacontroller:v4.11.22` |

`profiles-deployment` creates the example profile (`user@example.com`, profile `kubeflow-user-example-com`) from `common/user-namespace`. That profile namespace is not a static Namespace manifest. The `auth` namespace is the only Namespace object that option 1 adds on top of the shared set.

`kubeflow-pipelines-profile-controller` is accompanied by a `DecoratorController` (`metacontroller` sync hook). Option 5 does not install that object. Metacontroller itself is only in option 1 because multi-user KFP pulls `third-party/metacontroller`.

### Files referenced only by option 1

331 files in git, grouped by the package option 1 adds. Counts are files the kustomize walk actually opens (resources, patches, configurations), not every file sitting unused in the manifests tree. Six of them are the restored cache-deployer delete patches.

| Package | Files | Workloads it adds |
| --- | --- | --- |
| `common/dex` | 10 | `auth/dex` |
| `common/oidc-client/oidc-authservice` | 9 | `istio-system/oidc-authservice` |
| `common/kubeflow-namespace` | 2 | `kubeflow` namespace is also created by option 5's `cluster-scoped-resources/namespace.yaml`, so the namespace is common. This package file is still only on the option 1 path. |
| `common/kubeflow-roles` | 2 | Cluster roles for the full platform |
| `common/user-namespace` | 4 | Example Profile |
| `apps/centraldashboard` | 16 | `centraldashboard` (overlay directory is named `kserve`; the workload is the Kubeflow dashboard) |
| `apps/admission-webhook` | 14 | `admission-webhook-deployment` |
| `apps/jupyter` (web app and notebook controller) | 36 | `jupyter-web-app-deployment`, `notebook-controller-deployment` |
| `apps/profiles` | 22 | `profiles-deployment` |
| `apps/pvcviewer-controller` | 32 | `pvcviewer-controller-manager` |
| `apps/volumes-web-app` | 13 | `volumes-web-app-deployment` |
| `apps/tensorboard` | 33 | tensorboard controller and web app |
| `apps/training-operator` | 19 | `training-operator` |
| `apps/katib` (`installs/katib-with-kubeflow` and its components) | 39 | four Katib workloads. `53da74c` edits these Katib configs only on this path. |
| `apps/pipeline` multi-user and cluster Argo | 77 | `kubeflow-pipelines-profile-controller`, `metacontroller`, Istio VirtualServices and AuthorizationPolicies for multi-user KFP, cluster-scoped workflow-controller RBAC. Includes the cert-manager multi-user overlay and its six restored cache-deployer delete patches. |
| Entry files | 3 | `deployment/envs/kubeflow-monitoring/kustomization.yaml`, `in-cluster-setup/kubeflow/kustomization.yaml`, `custom/kubeflow-custom/env/kubeflow/kustomization.yaml` |

Pipeline files that exist only on the option 1 path:

- `apps/pipeline/upstream/env/cert-manager/platform-agnostic-multi-user/kustomization.yaml`
- `apps/pipeline/upstream/env/cert-manager/platform-agnostic-multi-user/patches/` (six cache-deployer deletes, restored on this branch)
- `apps/pipeline/upstream/env/cert-manager/base/`
- `apps/pipeline/upstream/env/platform-agnostic-multi-user/kustomization.yaml`
- `apps/pipeline/upstream/base/installs/multi-user/` (UI, API, cache, metadata-writer, persistence-agent, scheduled-workflow, and viewer patches, plus `pipelines-profile-controller/`)
- `apps/pipeline/upstream/base/metadata/options/istio/`
- `apps/pipeline/upstream/third-party/metacontroller/`
- `apps/pipeline/upstream/third-party/minio/options/istio/`
- `apps/pipeline/upstream/third-party/mysql/options/istio/`
- `apps/pipeline/upstream/third-party/argo/installs/cluster/`
- `apps/pipeline/upstream/third-party/argo/upstream/manifests/cluster-install/workflow-controller-rbac/`

Option 5 reaches the same API, UI, metadata, MinIO, and MySQL containers through `base/installs/generic` and `third-party/argo/installs/namespace` instead of these multi-user and cluster-Argo files.

---

## Excluded: KServe

Left out of the three categories, as requested.

| | Option 1 | Option 5 |
| --- | --- | --- |
| Manifest package | `contrib/kserve/kserve` and `contrib/kserve/models-web-app/overlays/kubeflow` | `contrib/kserve/kserve` only |
| Custom package | `custom/kserve-custom/env/kubeflow` | `custom/kserve-custom/env/standalone-kfp` |
| Controller | `kubeflow/kserve-controller-manager` (`kserve/kserve-controller:v0.11.0`, `quay.io/brancz/kube-rbac-proxy:v0.13.1`) | same controller and image |
| Models web app | `kubeflow/kserve-models-web-app` (`kserve/models-web-app:v0.10.0`) | not installed |
| Extra namespace | none from the KServe custom overlay | `kserve-inference` |
| Extra RBAC | none from `kubeflow-custom` | `kserve-deployer` ClusterRole, only on the option 5 custom overlay |

`ClusterServingRuntime` objects from `kserve-runtimes.yaml` are installed by both options. They are KServe and are not counted above.
