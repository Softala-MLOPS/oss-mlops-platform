# inference_component.py
from kfp.v2.dsl import component, Input, Artifact

@component(
    base_image="python:3.9",  # kserve on python 3.10 comes with a dependency that fails to get installed
    packages_to_install=["kserve==0.11.0", "scikit-learn~=1.0.2"],
    output_component_file='src/components_yaml/inference_component.yaml',
)
def inference(
    model_name: str,
    scaler_in: Input[Artifact]
):
    """
    Test inference.
    """
    from kserve import KServeClient
    import requests
    import pickle
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    namespace = 'kserve-inference'
    
    input_sample = [[5.6, 0.54, 0.04, 1.7, 0.049, 5, 13, 0.9942, 3.72, 0.58, 11.4],
                    [11.3, 0.34, 0.45, 2, 0.082, 6, 15, 0.9988, 2.94, 0.66, 9.2]]

    logger.info(f"Loading standard scaler from: {scaler_in.path}")
    with open(scaler_in.path, 'rb') as fp:
        scaler = pickle.load(fp)

    logger.info(f"Standardizing sample: {scaler_in.path}")
    input_sample = scaler.transform(input_sample)

    # get inference service
    KServe = KServeClient()

    # wait for deployment to be ready
    KServe.get(model_name, namespace=namespace, watch=True, timeout_seconds=120)

    inference_service = KServe.get(model_name, namespace=namespace)
    header = {"Host": f"{model_name}.{namespace}.example.com"}
    is_url = f"http://istio-ingressgateway.istio-system.svc.cluster.local:80/v1/models/{model_name}:predict"
    
    logger.info(f"\nInference service status:\n{inference_service['status']}")
    logger.info(f"\nInference service URL:\n{is_url}\n")

    inference_input = {
        'instances': input_sample.tolist()
    }
    response = requests.post(
        is_url,
        json=inference_input,
        headers=header,
    )
    if response.status_code != 200:
        raise RuntimeError(f"HTTP status code '{response.status_code}': {response.json()}")
    
    logger.info(f"\nPrediction response:\n{response.json()}\n")