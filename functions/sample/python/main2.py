import sys
import json
from ibmcloudant.cloudant_v1 import CloudantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

def get_review():
    
    authenticator = IAMAuthenticator("8eNTd3ObehB2qJkw1aLs7cAu4G7H8Qn9ler9rmw3vTuw")
    service = CloudantV1(authenticator=authenticator)
    service.set_service_url("https://18fdd4da-2b79-4454-a9b6-9d96e3cc8fd8-bluemix.cloudantnosqldb.appdomain.cloud")
    
    response = service.post_all_docs(
        db='reviews',
        include_docs=True,
        start_key='abc',
        limit=10
    ).get_result()

    result = json.dumps(response['rows'])
    return result

print(get_review())
