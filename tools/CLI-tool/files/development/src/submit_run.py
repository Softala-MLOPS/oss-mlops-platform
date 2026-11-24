# submit_run.py
import kfp
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kfp_config import get_kfp_endpoint
from pipelines.pipeline_definitions.pipeline_definition import pipeline
from pipelines.pipeline_arg.pipeline_arg import arguments

def submit_pipeline():
    client = kfp.Client(host=get_kfp_endpoint())

    experiment_name = "demo-experiment"
    run_name = "demo-run-through-github-actions-on-OSS-MLOps-platform-in-development-environment"

    created_run = client.create_run_from_pipeline_func(
        pipeline_func=pipeline,
        arguments=arguments,
        run_name=run_name,
        experiment_name=experiment_name,
        mode=kfp.dsl.PipelineExecutionMode.V2_COMPATIBLE,
        enable_caching=False,
    )
    print(f"Submitted demo pipeline run: {created_run.run_id}")

    if os.getenv("KFP_WAIT_FOR_RUN_COMPLETION", "").lower() == "true":
        timeout = int(os.getenv("KFP_RUN_TIMEOUT_SECONDS", "5400"))
        run_detail = created_run.wait_for_run_completion(timeout=timeout)
        finished_run = run_detail.to_dict()["run"]
        status = finished_run["status"]
        print(f"Demo pipeline run {created_run.run_id} finished with status: {status}")
        if status != "Succeeded":
            raise RuntimeError(
                f"Demo pipeline run {created_run.run_id} did not succeed: {status}"
            )

if __name__ == "__main__":
    submit_pipeline()
