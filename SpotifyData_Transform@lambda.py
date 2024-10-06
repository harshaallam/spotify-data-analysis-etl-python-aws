import json
import boto3
import pandas as pd
from datetime import datetime
from io import StringIO

def album(data):
    album_list=[]
    for row in data['items']:
        album_id=row['track']['album']['id']
        album_name=row['track']['album']['name']
        release_date=row['track']['album']['release_date']
        album_url=row['track']['album']['external_urls']['spotify']
        album_tracks=row['track']['album']['total_tracks']
        album_dict={'album_id':row['track']['album']['id'],'album_name':row['track']['album']['name'],'release_date':row['track']['album']['release_date'],'album_url':row['track']['album']['external_urls']['spotify'],'album_tracks':row['track']['album']['total_tracks']}
        album_list.append(album_dict)
    return album_list
def artist(data):
    artist_list=[]                      # Data related to artist is stored in a list and later converts into a DataFrame
    for row in data['items']:     # As the artist deatails are stored in nested dictionary which is in a list, row.items gives the list of
        for key,val in row.items():       # elements in the row.items where artists is one of the element(which is a dictionary)
            if key=='track':
                for artist in val['artists']:
                    artist_dict={'artist_id':artist['id'],'artist_url':artist['href'],'artist_name':artist['name']}
                    artist_list.append(artist_dict)
    return artist_list
def song(data):
    song_list=[]                        # Data related to album is stored in a list and later converts into a DataFrame
    for row in data['items']:
        song_id=row['track']['id']
        song_name=row['track']['name']
        song_duration=row['track']['duration_ms']
        song_popularity=row['track']['popularity']
        song_added=row['added_at']
        song_url=row['track']['external_urls']['spotify']
        album_id=row['track']['album']['id']
        artist_id=row['track']['artists'][0]['id']
        song_dict={'song_id':song_id,'song_name':song_name,'song_duration':song_duration,'song_popularity':song_popularity,'song_added':song_added,'song_url':song_url,'album_id':album_id,'artist_id':artist_id}
        song_list.append(song_dict)
    return song_list
    

def lambda_handler(event, context):
    s3=boto3.client('s3')
    Buc='spotify-data-etl-harsha'
    Ky='raw_data/to_process/'
    spotify_data=[]
    spotify_keys=[]
    
    for file in s3.list_objects(Bucket=Buc,Prefix=Ky)['Contents']:
        file_key=file['Key']
        if file_key.split('.')[-1]=='json':
            response=s3.get_object(Bucket=Buc,Key=file_key)
            content=response['Body']
            jsonobj=json.loads(content.read())
            spotify_data.append(jsonobj)
            spotify_keys.append(file_key)
    for data in spotify_data:
        album_list=album(data)
        artist_list=artist(data)
        song_list=song(data)
    album_df=pd.DataFrame(album_list)
    album_df.drop_duplicates(subset=['album_id'],inplace=True)
    album_df['release_date']=pd.to_datetime(album_df['release_date'])
    artist_df=pd.DataFrame(artist_list)
    artist_df.drop_duplicates(subset=['artist_id'],inplace=True)
    song_df=pd.DataFrame(song_list)
    song_df.drop_duplicates(subset=['song_id'],inplace=True)
    song_df['song_added']=pd.to_datetime(song_df['song_added'])
    
    song_key='transformed_data/song_data/song_transformed'+ str(datetime.now()) + '.csv'
    song_strobj=StringIO()
    song_df.to_csv(song_strobj,index=False)
    song_str=song_strobj.getvalue()
    s3.put_object(Bucket=Buc,Key=song_key,Body=song_str)
    album_key='transformed_data/album_data/album_transformed'+ str(datetime.now()) + '.csv'
    album_strobj=StringIO()
    album_df.to_csv(album_strobj,index=False)
    album_str=album_strobj.getvalue()
    s3.put_object(Bucket=Buc,Key=album_key,Body=album_str)
    artist_key='transformed_data/artist_data/artist_transformed'+ str(datetime.now()) + '.csv'
    artist_strobj=StringIO()
    artist_df.to_csv(artist_strobj,index=False)
    s3.put_object(Bucket=Buc,Key=artist_key,Body=artist_strobj.getvalue())
    
    s3_resource=boto3.resource('s3')
    for file_key in spotify_keys:
        copy_source={
            'Bucket':Buc,
            'Key':file_key
        }
    s3_resource.meta.client.copy(copy_source,Buc,'raw_data/processed/'+file_key.split('/')[-1])
    s3_resource.Object(Buc,file_key).delete()
        