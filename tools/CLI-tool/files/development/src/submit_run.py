# submit_run.py
import kfp
import sys
import os

sys.path.append('../src')
from pipelines.pipeline_definitions.pipeline_definition import pipeline
from pipelines.pipeline_arg.pipeline_arg import arguments

def submit_pipeline():

    # 1. Get the Kubeflow address, namespace, and token from environment variables (Default is None if not set)
    kfp_host = os.environ.get("KFP_HOST", "http://localhost:8080")  # Default to localhost if not provided
    kfp_namespace = os.environ.get("KFP_NAMESPACE")
    kfp_token = os.environ.get("KFP_BEARER_TOKEN")

    # 2. Initialize the client with the specific host
    if kfp_token:
        print(f"🌐 [REMOTE MODE] Connecting to: {kfp_host}")
        print(f"📂 Namespace: {kfp_namespace}")
        client = kfp.Client(
            host=kfp_host, 
            namespace=kfp_namespace, 
            existing_token=kfp_token
        )
    else:
        print(f"💻 [LOCAL MODE] Connecting to: {kfp_host}")
        # Local mode (port-forward) usually doesn't require namespace or token, but we can still provide namespace if needed.
        client = kfp.Client(host=kfp_host, namespace=kfp_namespace)

    # Define your experiment and run name
    experiment_name = "demo-experiment"
    run_name = "demo-run-through-github-actions-on-OSS-MLOps-platform-in-development-environment"

    # Submit the pipeline run
    print("🚀 Submitting pipeline...")
    result = client.create_run_from_pipeline_func(
        pipeline_func=pipeline,
        arguments=arguments,
        run_name=run_name,
        experiment_name=experiment_name,
        namespace=kfp_namespace,
        mode=kfp.dsl.PipelineExecutionMode.V2_COMPATIBLE,
        enable_caching=False,
    )
    print(f"✅ Pipeline submitted successfully! Run ID: {result.run_id}")

if __name__ == "__main__":
    submit_pipeline()
