# submit_run.py
import kfp
import sys
import os
import re
import requests

sys.path.append('../src')
from pipelines.pipeline_definitions.pipeline_definition import pipeline
from pipelines.pipeline_arg.pipeline_arg import arguments

def get_dex_cookie(host: str, username: str, password: str) -> str:
    """Get session cookie from Dex using username/password."""
    session = requests.Session()
    
    # 1. Fetch the login page, follow redirects to Dex
    resp = session.get(host, allow_redirects=True)
    
    # 2. Find the action URL of the login form
    login_url = re.search(r'action="(/dex/auth/[^"]+)"', resp.text)
    if not login_url:
        raise ValueError("Dex login form not found")
        
    dex_login_url = f"{host}{login_url.group(1)}"
    
    # 3. Submit credentials
    resp = session.post(
        dex_login_url,
        data={"login": username, "password": password},
        allow_redirects=True,
    )
    
    # 4. Get the authservice_session cookie
    cookie = session.cookies.get("authservice_session")
    if not cookie:
        raise ValueError("Login failed, please check your username and password")
        
    return cookie

def submit_pipeline():
    # 1. Get the Kubeflow address, namespace, and credentials from environment variables
    kfp_host = os.environ.get("KFP_HOST", "http://localhost:8080")  # Default to localhost if not provided
    kfp_namespace = os.environ.get("KFP_NAMESPACE", "kubeflow-user-example-com")
    
    # Authentication variables for Dex
    kfp_username = os.environ.get("KFP_USERNAME")  # Add to GitLab CI / GitHub Actions variables
    kfp_password = os.environ.get("KFP_PASSWORD")  # Add to GitLab CI / GitHub Actions variables

    # 2. Initialize the client based on provided credentials
    if kfp_username and kfp_password:
        print(f"🌐 [REMOTE MODE] Connecting to: {kfp_host}")
        print(f"📂 Namespace: {kfp_namespace}")
        
        # Fetch the Dex session cookie
        cookie = get_dex_cookie(kfp_host, kfp_username, kfp_password)
        
        # Initialize KFP client with the Dex cookie
        client = kfp.Client(
            host=f"{kfp_host}/pipeline",
            cookies=f"authservice_session={cookie}",  # <-- Pass the cookie here
            namespace=kfp_namespace,
        )
    else:
        print(f"💻 [LOCAL MODE] Connecting to: {kfp_host}")
        # Local mode (port-forward) usually doesn't require namespace or token, 
        # but we can still provide the namespace if needed.
        client = kfp.Client(host=kfp_host, namespace=kfp_namespace)

    # 3. Define your experiment and run name
    experiment_name = "demo-experiment"
    run_name = "demo-run-through-github-actions-on-OSS-MLOps-platform-in-development-environment"

    # 4. Submit the pipeline run
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
    submit_pipeline()# submit_run.py
import kfp
import sys
import os
import re
import requests

sys.path.append('../src')
from pipelines.pipeline_definitions.pipeline_definition import pipeline
from pipelines.pipeline_arg.pipeline_arg import arguments

def get_dex_cookie(host: str, username: str, password: str) -> str:
    """Get session cookie from Dex using username/password with debugging."""
    session = requests.Session()
    
    print(f"🔍 [DEBUG] Step 1: Fetching login page from {host}")
    resp = session.get(host, allow_redirects=True)
    
    login_url = re.search(r'action="(/dex/auth/[^"]+)"', resp.text)
    if not login_url:
        print(f"🚨 [DEBUG] Cannot find login form. Current URL: {resp.url}")
        raise ValueError("Dex login form not found")
        
    dex_login_url = f"{host}{login_url.group(1)}"
    print(f"🔍 [DEBUG] Step 2: Submitting credentials to {dex_login_url}")
    
    resp = session.post(
        dex_login_url,
        data={"login": username, "password": password},
        allow_redirects=True,
    )
    
    cookie = session.cookies.get("authservice_session")
    if not cookie:
        print("🚨 [DEBUG] LOGIN FAILED. Printing response info:")
        print(f"   -> Final URL after redirects: {resp.url}")
        print(f"   -> Status Code: {resp.status_code}")
        print(f"   -> Cookies received: {session.cookies.get_dict()}")
        print(f"   -> Username is set: {bool(username)}")
        print(f"   -> Password is set: {bool(password)}")
        # In ra 300 ký tự đầu của response để xem có báo lỗi sai pass hay lỗi Istio không
        print(f"   -> Response snippet: {resp.text[:300]}") 
        raise ValueError("Login failed, please check your username and password")
        
    return cookie
    
def submit_pipeline():
    # 1. Get the Kubeflow address, namespace, and credentials from environment variables
    kfp_host = os.environ.get("KFP_HOST", "http://localhost:8080")  # Default to localhost if not provided
    kfp_namespace = os.environ.get("KFP_NAMESPACE", "kubeflow-user-example-com")
    
    # Authentication variables for Dex
    kfp_username = os.environ.get("KFP_USERNAME")  # Add to GitLab CI / GitHub Actions variables
    kfp_password = os.environ.get("KFP_PASSWORD")  # Add to GitLab CI / GitHub Actions variables

    # 2. Initialize the client based on provided credentials
    if kfp_username and kfp_password:
        print(f"🌐 [REMOTE MODE] Connecting to: {kfp_host}")
        print(f"📂 Namespace: {kfp_namespace}")
        
        # Fetch the Dex session cookie
        cookie = get_dex_cookie(kfp_host, kfp_username, kfp_password)
        
        # Initialize KFP client with the Dex cookie
        client = kfp.Client(
            host=f"{kfp_host}/pipeline",
            cookies=f"authservice_session={cookie}",  # <-- Pass the cookie here
            namespace=kfp_namespace,
        )
    else:
        print(f"💻 [LOCAL MODE] Connecting to: {kfp_host}")
        # Local mode (port-forward) usually doesn't require namespace or token, 
        # but we can still provide the namespace if needed.
        client = kfp.Client(host=kfp_host, namespace=kfp_namespace)

    # 3. Define your experiment and run name
    experiment_name = "demo-experiment"
    run_name = "demo-run-through-github-actions-on-OSS-MLOps-platform-in-development-environment"

    # 4. Submit the pipeline run
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