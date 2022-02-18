import os
import tweepy
from pprint import  pprint
import time
from threading import Timer,Thread,Event
from dotenv import load_dotenv
load_dotenv()

consumer_key = os.getenv('CONSUMER_KEY')
consumer_secret = os.getenv('CONSUMER_SECRET')
auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
api = tweepy.API(auth)

#================================================ OLD TEST CODE ================================================

# class perpetualTimer():
#    def __init__(self,t,hFunction):
#       self.t=t
#       self.hFunction = hFunction
#       self.thread = Timer(self.t,self.handle_function)
#
#    def handle_function(self):
#       self.hFunction()
#       self.thread = Timer(self.t,self.handle_function)
#       self.thread.start()
#
#    def start(self):
#       self.thread.start()
#
#    def cancel(self):
#       self.thread.cancel()

# init_followers()
# t = perpetualTimer(1800,run) #30 mins
# t.start()


#================================================ SET IDs ================================================

# Find IDs
# print(api.lookup_users(screen_name=['username1']))
# print('\n')
# print(api.lookup_users(screen_name=['username2']))
# print('\n')
username1_id = '12345'
username2_id = '54321'

# Storage
twitter_ids = [username1_id, username2_id]
id_to_follower_dict = {
    username1_id: "user1readable",
    username2_id: "user2readable",
}
recent_follows = []

# Initialize recent_follows as array of arrays of ids
def init_followers():
    global recent_follows
    for id in twitter_ids:
        following = api.get_friends(user_id=id, count=5)
        time.sleep(1)
        temp_arr =[]
        for i in following:
            temp_arr.append(i._json['id'])
        recent_follows.append(temp_arr)

# Loop function to scan for new follows
# Returns None if no new follows OR a list of strings if there are new follows
def scan_followers():
    global recent_follows
    global twitter_ids # will not change
    global id_to_follower_dict # will not change
    check_follows = [] # used to store array of arrays of recent follows ids
    id_to_screenname_list = [] # used to store array of dicts, each dict is id -> screen_name of recent follows
    # create new lists of most recent followers
    for id in twitter_ids:
        temp_arr =[] # will hold array of recent follow ids
        id_to_screenname_dict = dict() # will hold dict of id -> screen_name of recent follows
        following = api.get_friends(user_id=id, count=5)
        time.sleep(1)
        for i in following:
            id = i._json['id']
            screenname = i._json['screen_name']
            temp_arr.append(id) # append id to array
            id_to_screenname_dict[id] = screenname # append id -> screen_name to dict
        check_follows.append(temp_arr) # append id array to check_follows array
        id_to_screenname_list.append(id_to_screenname_dict) # building a list of dicts where each dict is id -> screen_name

    # compare to old lists
    new_follows = [] # will hold new follower ids
    alerts = []
    is_returning = False
    for i in range(len(check_follows)): # iterate by users we are watching
        new_follows = list(set(check_follows[i]) - set(recent_follows[i]))
        for j in new_follows: # all new followers that weren't in recent_follows
            # print new follower
            follower_name = id_to_follower_dict[twitter_ids[i]] # grab screen_name of who did the follow
            followed_name = id_to_screenname_list[i][j] # grab screen_name of who was followed
            alerts.append(f'{follower_name} followed {followed_name}')
            is_returning = True
    # update global
    recent_follows = check_follows
    if(is_returning):
        return alerts
    else:
        print('None found (Twitter)')
        return None

# Intitialize recent_follows list
def prepare():
    init_followers()

# Scan for new follows
def scanTwitters():
    return scan_followers()
