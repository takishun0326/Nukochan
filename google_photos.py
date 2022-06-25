import google.oauth2.credentials
import google_auth_oauthlib.flow
import json,os
from datetime import datetime,date
from googleapiclient.discovery import build
import random

SCOPES = ['https://www.googleapis.com/auth/photoslibrary']
API_SERVICE_NAME = 'photoslibrary'
API_VERSION = 'v1'
CLIENT_SECRET_FILE = 'client_secret.json'
CREDENTIAL_FILE = 'credential.json'

def support_datetime_default(o):
  if isinstance(o, datetime):
    return o.isoformat()
  raise TypeError(repr(o) + " is not JSON serializable")

def getCredentials():
  if os.path.exists(CREDENTIAL_FILE):
    with open(CREDENTIAL_FILE) as f_credential_r:
      credentials_json = json.loads(f_credential_r.read())
      credentials = google.oauth2.credentials.Credentials(
        credentials_json['token'],
        refresh_token=credentials_json['_refresh_token'],
        token_uri=credentials_json['_token_uri'],
        client_id=credentials_json['_client_id'],
        client_secret=credentials_json['_client_secret']
      )
  else:
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE,scopes=SCOPES)
    
    credentials = flow.run_console()
  with open(CREDENTIAL_FILE, mode='w') as f_credential_w:
    f_credential_w.write(json.dumps(vars(credentials), default=support_datetime_default, sort_keys=True))
    
  return credentials

# アルバム名とキーワードが一致するアルバムを取得
def getTargetAlbum(service, word):
    # 共有アルバムを一括収集
    sharedAlbums = service.sharedAlbums().list(pageSize=20).execute()
    for sharedAlbum in sharedAlbums['sharedAlbums']:
        if word in sharedAlbum['title']:
            return sharedAlbum

# 取得したアルバム内の画像を取り出す
def getTargetPhotos(service, word, GET_NUM_OF_PHOTOS):
    photos = []

    Album = getTargetAlbum(service, word)
    AlbumId = Album['id'] 
    photo = {}
    body = {
        'albumId' : AlbumId,
        'pageSize' : 50,
    }
    mediaItems = service.mediaItems().search(body=body).execute()
    for mediaItem in mediaItems['mediaItems']:
        photo['id'],photo['url'] = mediaItem['id'],mediaItem['baseUrl']
        photo['width'],photo['height'] = mediaItem['mediaMetadata']['width'],mediaItem['mediaMetadata']['height']
        photos.append(photo)
    
    # ランダムに GET_NUM_OF_PHOTOSの数だけ取得 list
    random.seed()
    return random.sample(photos, GET_NUM_OF_PHOTOS)

def urlFormat(url, width, height):
    return url + '=w' + str(width) + '-h' + str(height)

def getPhotos():
    # 取得する画像の枚数
    GET_NUM_OF_PHOTOS = 1
    
    photos_urls = []

    credentials = getCredentials()
    service = build(
        API_SERVICE_NAME,
        API_VERSION,
        credentials=credentials,
        static_discovery=False
    )
    # catアルバム
    cat_photos = getTargetPhotos(service, 'cat', GET_NUM_OF_PHOTOS) 

    # urlの結合
    for cat_photo in cat_photos:
        width = cat_photo['width']
        height = cat_photo['height']
        url = urlFormat(cat_photo['url'], width, height)
        # print(url)
        photos_urls.append(url)
    
    # 画像のurlのみ返す
    return photos_urls

if __name__ == '__main__':
    getPhotos()