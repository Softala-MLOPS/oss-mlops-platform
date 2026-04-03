# submit_run.py
import kfp
import sys
import os

sys.path.append('../src')
from pipelines.pipeline_definitions.pipeline_definition import pipeline
from pipelines.pipeline_arg.pipeline_arg import arguments

def submit_pipeline():

    # 1. Get the Kubeflow address from environment variables (Default is None if not set)
    kfp_host = os.environ.get("KFP_HOST")

    # 2. Initialize the client with the specific host
    # If kfp_host = None, it will fall back to the default behavior (looking for ~/.kube/config)
    client = kfp.Client(host=kfp_host) 
    
    # Define your experiment and run name
    experiment_name = "demo-experiment"
    run_name = "demo-run-through-github-actions-on-OSS-MLOps-platform-in-development-environment"

    # Submit the pipeline run
    client.create_run_from_pipeline_func(
        pipeline_func=pipeline,
        arguments=arguments,
        run_name=run_name,
        experiment_name=experiment_name,
        mode=kfp.dsl.PipelineExecutionMode.V2_COMPATIBLE,
        enable_caching=False,
    )

if __name__ == "__main__":
    submit_pipeline()
