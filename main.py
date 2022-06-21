import requests
import json
import threading
import time
import random

headers_main = {
    'accept-encoding' : 'gzip, deflate, br',
    'origin':'https://www.instagram.com',
    'referer': 'https://www.instagram.com/',
    'cookie':'',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.81 Safari/537.36'
}

headers_accSecond = {
    'accept-encoding' : 'gzip, deflate, br',
    'origin':'https://www.instagram.com',
    'referer': 'https://www.instagram.com/',
    'cookie':'',
    'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.81 Safari/537.36'
}

def download_video(item):
    print(item['media']['code'])
    file = requests.get(item['media']['video_versions'][0]['url'], headers=headers_main)
    open('downloaded_videos/'+item['media']['code']+'.mp4', 'wb').write(file.content)

def download_comments(item):
    #print('Post: ' + item['media']['code'] + ' - pk: ' + item['media']['pk'])
    comments = ''
    if 'caption' in item['media']:
        comments = comments + item['media']['caption']['text'] + "\n" #add caption if existent
    
    parsed = {}
    parsed['next_min_id'] = ''
    parsed['has_more_headload_comments'] = True
    while parsed['has_more_headload_comments']: #load more comments
            x = requests.get('https://i.instagram.com/api/v1/media/' + item['media']['pk'] + '/comments/?can_support_threading=true&min_id=' + parsed['next_min_id'], headers=headers_accSecond)
            parsed = json.loads(x.text)
            if 'comments' in parsed: #check if comments exist
                for comment in parsed['comments']:
                    #print(comment['text'])
                    comments = comments + comment['text'] + "\n" #save text of every comment
                    if comment['child_comment_count'] != 0:
                        comments = comments + get_child_comments(comment['pk'], item['media']['pk']) #if it has child comments, add
                    
    
    print("Finished post: " + item['media']['code'])
    with open('downloaded_videos/'+item['media']['code']+'.txt', 'wb') as f: #create text file for every posts comments
        f.write(comments.encode("UTF-8"))

def get_child_comments(comment_pk, media_pk): #get only one child comment load for now
    child_comments = ''
    x = requests.get('https://i.instagram.com/api/v1/media/' + media_pk + '/comments/' + comment_pk + '/child_comments/', headers=headers_accSecond)
    parsed = {}
    parsed = json.loads(x.text)
    for child_comment in parsed['child_comments']:
        child_comments = child_comments + child_comment['text'] + '\n'
    return child_comments

def create_thread(item): 
    th = threading.Thread(target=download_comments, args=(item,)) #new thread for every single post
    th.start()

def get_saved_post_urls(collection):
    parsed = {}
    parsed['next_max_id'] = ''
    parsed['more_available'] = True
    while parsed['more_available']: #load more posts
        x = requests.get('https://i.instagram.com/api/v1/feed/collection/' + collection + '/posts/?max_id='+parsed['next_max_id'] , headers=headers_main)
        parsed = json.loads(x.text)
        for item in parsed['items']: #for every post
            create_thread(item)
            #time.sleep(1) #wait 1 second

get_saved_post_urls('17929862582090717')
