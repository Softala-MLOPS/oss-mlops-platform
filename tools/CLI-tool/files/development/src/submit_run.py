# submit_run.py
import kfp
import sys

sys.path.append('../src')
from kfp_config import get_kfp_endpoint
from pipelines.pipeline_definitions.pipeline_definition import pipeline
from pipelines.pipeline_arg.pipeline_arg import arguments

def submit_pipeline():

    client = kfp.Client(host=get_kfp_endpoint())


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
