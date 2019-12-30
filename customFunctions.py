from twython import Twython
import sys
import sqlite3
from sqlite3 import Error



########## Twython Interactions ##########

##Pull in API keys from file
from auth import (
    user_name,
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
)

##Create twitter object
twitter = Twython(
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
)

def getFollowers(queried_user):

    data = twitter.cursor(twitter.get_followers_ids, screen_name = queried_user, return_pages=True)

    output = []

    for result in data:
        output.extend(result)

    return output


def getFriends(queried_user):

    data = twitter.cursor(twitter.get_friends_ids, screen_name = queried_user, return_pages=True)

    output = []

    for result in data:
        output.extend(result)

    return output

def getUsersTwitterData(queried_user):
    output = twitter.lookup_user(screen_name = queried_user)
    return output


def followBackTweet(user):
    message = '''{}, Thank you for the Follow Back!
\U0001f44b\U0001f600

-My Follower Thanking #TwitterBot'''.format(user)
    twitter.update_status(status=message)
    return(user, "Follow Back thanks")


def followTweet(user):
    message = '''{}, Thank you for the Follow!
\U0001f44b\U0001f600

-My Follower Thanking #TwitterBot'''.format(user)
    twitter.update_status(status=message)
    return(user, "Follow thanks")


def reFollowBackTweet(user):
    message = '''Welcome back {} \U0001f601, Thanks for the re-Follow Back!
\U0001f44b\U0001f600

-My Follower Thanking #TwitterBot'''.format(user)
    twitter.update_status(status=message)
    return(user, "reFollow Back thanks")


def reFollowTweet(user):
    message = '''Welcome back {} \U0001f601, Thanks for the re-Follow!
\U0001f44b\U0001f600

-My Follower Thanking #TwitterBot'''.format(user)
    twitter.update_status(status=message)
    return(user, "reFollow thanks")


def userName(userID):
    #print("Fetching user's screen name")
    userObject = twitter.lookup_user(user_id = userID)
    return ("@%s" % userObject[0]['screen_name'])

######### Progress Bar #########

def startProgress(title):
    global progress_x
    sys.stdout.write(title + ": [" + "-"*40 + "]" + chr(8)*41)
    sys.stdout.flush()
    progress_x = 0

def progress(x):
    global progress_x
    x = int(x * 40 // 100)
    sys.stdout.write("#" * (x - progress_x))
    sys.stdout.flush()
    progress_x = x

def endProgress():
    sys.stdout.write("#" * (40 - progress_x) + "]\n")
    sys.stdout.flush()

########## Database manipulation ##########

def sql_connection(fileName):
    try:
        con = sqlite3.connect(fileName)
        return con
    except Error:
        print(Error)

def sql_followers_table(con):
    cursorObj = con.cursor()
    cursorObj.execute("CREATE TABLE connections(user_IDs int PRIMARY KEY, screen_name text, isFollower bool, followDate text, isFriend bool, friendDate text, thanked bool, rethanked bool)")
    con.commit()

def total_rows(cursor, table_name, print_out=False):
    """ Returns the total number of rows in the database """
    cursor.execute('SELECT COUNT(*) FROM {}'.format(table_name))
    count = cursor.fetchall()
    if print_out:
        print('\nTotal rows: {}'.format(count[0][0]))
    return count[0][0]
