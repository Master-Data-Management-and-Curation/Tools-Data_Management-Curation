import requests

def get_authentication_token(nomad_url, username, password):
    '''Get the token for accessing your NOMAD unpublished uploads remotely'''
    try:
        response = requests.get(
            nomad_url + 'auth/token', params=dict(username=username, password=password), timeout=10)
        token = response.json().get('access_token')
        if token:
            return token

        print('response is missing token: ')
        print(response.json())
        return
    except Exception:
        print('something went wrong trying to get authentication token')
        return


def create_dataset(nomad_url, token, dataset_name):
    '''Create a dataset to group a series of NOMAD entries'''
    try:
        response = requests.post(
            nomad_url + 'datasets/',
            headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json'},
            json={"dataset_name": dataset_name},
            timeout=10
            )
        dataset_id = response.json().get('dataset_id')
        if dataset_id:
            return dataset_id

        print('response is missing dataset_id: ')
        print(response.json())
        return
    except Exception:
        print('something went wrong trying to create a dataset')
        return
    
def get_datasets_list(nomad_url, page_size=10, offset=0):
    try:
        all_datasets = []
        while True:
            # Make the GET request with limit and offset
            response = requests.get(
                    nomad_url + 'datasets/?page_size=' + str(page_size) + '&order=asc' + '&page_offset=' + str(offset), 
                    timeout=10)

            datasets = response.json()['data']
            all_datasets.extend(datasets)

            # If fewer users are returned than the 'page_size', stop fetching
            if len(datasets) < page_size:
                break

            # Update offset for the next batch
            offset += page_size
        
        return all_datasets

    except Exception:
        print('something went wrong trying to get authentication token')
        return

def upload_to_NOMAD(nomad_url, token, upload_file, upload_name, embargo_length=0):
    '''Upload a single file for NOMAD upload, e.g., zip format'''
    with open(upload_file, 'rb') as f:
        try:
            response = requests.post(
                nomad_url + 'uploads?upload_name=' + upload_name + '&embargo_length=' + str(embargo_length),
                headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json'},
                data=f, timeout=30)
            upload_id = response.json().get('upload_id')
            if upload_id:
                return upload_id

            print('response is missing upload_id: ')
            print(response.json())
            return
        except Exception:
            print('something went wrong uploading to NOMAD')
            return

def check_upload_status(nomad_url, token, upload_id):
    '''
    # upload success => returns 'Process publish_upload completed successfully'
    # publish success => 'Process publish_upload completed successfully'
    '''
    try:
        response = requests.get(
            nomad_url + 'uploads/' + upload_id,
            headers={'Authorization': f'Bearer {token}'}, timeout=30)
        status_message = response.json().get('data').get('last_status_message')
        if status_message:
            return status_message

        print('response is missing status_message: ')
        print(response.json())
        return
    except Exception:
        print('something went wrong trying to check the status of upload' + upload_id)
        # upload gets deleted from the upload staging area once published...or in this case something went wrong
        return

def show_upload_metadata(nomad_url, token, upload_id):
    try:
        response = requests.get(nomad_url+'uploads/' + upload_id, headers={'Authorization': f'Bearer {token}'})
        return response.json()
    except Exception:
        print('something went wrong trying to show metadata to upload' + upload_id)
        return

def edit_upload_metadata(nomad_url, token, upload_id, metadata):
    '''
    Example of new metadata:
    upload_name = 'Test_Upload_Name'
    metadata = {
        "metadata": {
        "upload_name": upload_name,
        "references": ["https://doi.org/xx.xxxx/xxxxxx"],
        "datasets": dataset_id,
        "embargo_length": 0,
        "coauthors": ["coauthor@affiliation.de"],
        "comment": 'This is a test upload...'
        },
    }
    '''

    try:
        response = requests.post(
            nomad_url+'uploads/' + upload_id + '/edit',
            headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json'},
            json=metadata, timeout=30)
        return response
    except Exception:
        print('something went wrong trying to add metadata to upload' + upload_id)
        return

def publish_upload(nomad_url, token, upload_id):
    '''Publish an upload'''
    try:
        response = requests.post(
            nomad_url+'uploads/' + upload_id + '/action/publish',
            headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json'},
            timeout=30)
        return response
    except Exception:
        print('something went wrong trying to publish upload: ' + upload_id)
        return

def perform_query(nomad_url, query):
    try:
        response = requests.post(
                nomad_url + 'entries/query',
                json=query, timeout=30)
        return response.json()
    except Exception:
        print('something went wrong trying to perform the query')
        return
    
def download_from_upload_id(nomad_url,upload_id,download_name):
    try:
        response = requests.get(nomad_url + 'uploads/' + upload_id + '/raw', 
                                    stream=True)

        if response.status_code == 200:
            # Open a local file for writing in binary mode
            with open(download_name, 'wb') as f:
                # Write the content to the file in chunks to handle large files
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # Filter out keep-alive new chunks
                        f.write(chunk)
            print(f"Download successful, saved as '{download_name}'")
        else:
            print(f"Failed to download file. Status code: {response.status_code}")
            print(response.text)

        return
    
    except Exception:
        print('something went wrong trying to download')
        return



