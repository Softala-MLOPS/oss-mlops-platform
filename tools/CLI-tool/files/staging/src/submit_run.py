# submit_run.py
import kfp
import sys

sys.path.append('../src')
from pipelines.pipeline_definitions.pipeline_definition import pipeline
from pipelines.pipeline_arg.pipeline_arg import arguments
from pipelines.client_connection.client_connection import client_connect
from ci_context import get_ci_context

def submit_pipeline():
    client = client_connect() 

    ci_platform, branch = get_ci_context()
    
    # Define your experiment and run name
    experiment_name = "demo-experiment"
    run_name = f"demo-run-through-{ci_platform}-on-OSS-MLOps-platform-in-{branch}-environment"
    print(f"Experiment Name: {experiment_name}")
    print(f"Run Name: {run_name}")

    # Submit the pipeline run
    print("🚀 Submitting pipeline...")
    result = client.create_run_from_pipeline_func(
        pipeline_func=pipeline,
        arguments=arguments,
        run_name=run_name,
        experiment_name=experiment_name,
        mode=kfp.dsl.PipelineExecutionMode.V2_COMPATIBLE,
        enable_caching=False,
        namespace="kubeflow-user-example-com"
    )
    print(f"✅ Pipeline submitted successfully! Run ID: {result.run_id}")

if __name__ == "__main__":
    submit_pipeline()
