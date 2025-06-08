from azure.storage.blob import BlobServiceClient
import pandas as pd
from io import StringIO
import os
from dotenv import load_dotenv

load_dotenv()

connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_name = "aec-insights"

# Create container if it doesn't exist
try:
    blob_service_client.create_container(container_name)
except:
    pass

def upload_insights_to_blob(df, filename="insights.csv"):
    output = StringIO()
    df.to_csv(output, index=False)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)
    blob_client.upload_blob(output.getvalue(), overwrite=True)

def load_insights_from_blob(filename="insights.csv"):
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)
    if blob_client.exists():
        stream = blob_client.download_blob()
        return pd.read_csv(StringIO(stream.readall().decode()))
    return pd.DataFrame()  