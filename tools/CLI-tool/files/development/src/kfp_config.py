import os


DEFAULT_KFP_ENDPOINT = "http://localhost:8080"


def get_kfp_endpoint():
    """Return the configured KFP endpoint for local or in-cluster execution."""
    return os.getenv("KFP_ENDPOINT", DEFAULT_KFP_ENDPOINT).rstrip("/")