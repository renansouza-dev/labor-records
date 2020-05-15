from __future__ import print_function

import os.path
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# https://github.com/gsuitedevs/python-samples/blob/master/drive/quickstart
# https://stackoverflow.com/questions/56294506/mediaitems-search-next-returns-400

# If modifying these scopes, delete the file token.pickle.
# SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']


def get_files():
    """Shows basic usage of the Drive v1 API.
    Prints the names and ids of the first n files the user has access to.
    """
    credentials = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('resources/token.pickle'):
        with open('resources/token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('resources/credentials.json', SCOPES)
            credentials = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('resources/token.pickle', 'wb') as token:
            pickle.dump(credentials, token)

    service = build('photoslibrary', 'v1', credentials=credentials)

    # Call the Photo v1 API
    results = service.albums().list(
        pageSize=10,
        excludeNonAppCreatedData=False,
        fields="nextPageToken,albums(id,title,mediaItemsCount)").execute()
    items = results.get('albums', [])

    album = next((item for item in items[1:] if item["title"] == "Ponto"), None)
    if not album:
        print('Album not found.')
    else:
        api = service.mediaItems()
        api_request = api.search(body={'albumId': album['id'], "pageSize": min(100, int(album['mediaItemsCount']))})

        files = []
        while api_request is not None:
            api_search = api_request.execute()

            for photo in api_search['mediaItems']:
                files.append({
                    'filename': photo['filename'],
                    'url': photo['baseUrl'],
                    'creationTime': photo['mediaMetadata']['creationTime']
                })

            # mediaItems pagination management
            api_request = api.list_next(api_request, api_search)
        return files
