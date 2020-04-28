from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# https://github.com/gsuitedevs/python-samples/blob/master/drive/quickstart
# https://stackoverflow.com/questions/56294506/mediaitems-search-next-returns-400

# If modifying these scopes, delete the file token.pickle.
# SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']


def main():
    """Shows basic usage of the Drive v1 API.
    Prints the names and ids of the first n files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('photoslibrary', 'v1', credentials=creds)

    # Call the Photo v1 API
    results = service.albums().list(pageSize=10, excludeNonAppCreatedData=False,
                                    fields="nextPageToken,albums(id,title,mediaItemsCount)").execute()
    items = results.get('albums', [])

    pontoAlbum = next((item for item in items[1:] if item["title"] == "Ponto"), None)
    if not pontoAlbum:
        print('Album not found.')
    else:
        photos_mediaitems_api = service.mediaItems()
        print('Album {0} with id {1} has {2} photos'.format(pontoAlbum['title'].encode('utf8'), pontoAlbum['id'], pontoAlbum['mediaItemsCount']))
        mediaitems_search_req = photos_mediaitems_api.search(body={'albumId': pontoAlbum['id'], "pageSize": min(100, int(pontoAlbum['mediaItemsCount']))})

        total_files = 0
        while mediaitems_search_req is not None:
            mediaitems_search = mediaitems_search_req.execute()

            total_files += len(mediaitems_search['mediaItems'])
            # print(mediaitems_search['mediaItems'][0])

            # mediaItems pagination management
            mediaitems_search_req = photos_mediaitems_api.list_next(mediaitems_search_req, mediaitems_search)
        print(f'Downloaded {total_files} files.')


if __name__ == '__main__':
    main()
