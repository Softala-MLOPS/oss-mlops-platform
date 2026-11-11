# client_connection.py
import kfp

from kfp_config import get_kfp_endpoint

client = kfp.Client(host=get_kfp_endpoint())