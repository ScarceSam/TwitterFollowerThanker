import datetime
import time
import customFunctions as cF

##User followers to list
queried_user = cF.user_name
stepPauses = 0.2
dbFileName = queried_user + '.db'
loopPause = 30


# Check for Existing DB file
# If not, Create it and populate it with follower list
try:
    f = open(dbFileName)
    f.close()

except FileNotFoundError:
    print('No DataBase found for %s' % queried_user)

    print('Creating DataBase %s' % dbFileName)
    DB = cF.sql_connection(dbFileName)
    cF.sql_followers_table(DB)

    print('Fetching list of @%s\'s Followers' % queried_user)
    follower_list = cF.getFollowers(queried_user)

    print('@%s has %d followers' % ( queried_user, len( follower_list)))
    time.sleep(stepPauses)

    cF.startProgress('Populating DataBase')
    numOfEntries = len(follower_list)
    now = datetime.datetime.now()
    for i in reversed(range(numOfEntries)):
        cursorObj = DB.cursor()
        entities = (follower_list[i], "", 1, now.replace(microsecond=0), 0, '', 0, 0)
        cursorObj.execute('''INSERT INTO connections VALUES(?, ?, ?, ?, ?, ?, ?, ?)''', entities)
        DB.commit()
        cF.progress(((numOfEntries-i)/numOfEntries)*100)
    cF.endProgress()

#variables used in the main loop
old_follower_count = 0
old_friend_count = 0
new_follower_count = 0
new_friend_count = 0
follower_list = []
friend_list = []
followers_to_thank = 0

while(1):


    print('Checking %s\'s Follower Count and Friend Count' % queried_user)
    time.sleep(stepPauses)
    users_userobject = cF.getUsersTwitterData(queried_user)
    new_follower_count = users_userobject[0]['followers_count']
    new_friend_count = users_userobject[0]['friends_count']
    followerDif = new_follower_count - old_follower_count
    friendDif = new_friend_count - old_friend_count

    if not followerDif and not friendDif and not followers_to_thank:
        print('No changes to follower or friend counts and all followers have been thanked')
        time.sleep(stepPauses)
    else:

        #What was the change in follower and/or friend count?

        print('Starting thanking process')
        time.sleep(stepPauses)

        DB = cF.sql_connection(dbFileName)
        cursorObj = DB.cursor()

        now = datetime.datetime.now()

        if friendDif or followerDif:
            if followerDif:
                #check user's follower list save to list
                print('Pulling follower list')
                follower_list = cF.getFollowers(queried_user)
                old_follower_count = len(follower_list)


            #pull user's friends list save to list
            print('Pulling friend list')
            friend_list = cF.getFriends(queried_user)
            old_friend_count = len(friend_list)

            ############################ update is_friend ###############################
            rowsInDB = cF.total_rows(cursorObj, 'connections', False)
            cF.startProgress('Updating is_Friend')
            progressTotal = (len(friend_list) + rowsInDB)

            # for each name DB list
            for row in range( 1, ( rowsInDB + 1)):
                cursorObj.execute("SELECT * FROM connections WHERE ROWID = {}".format( row))
                current = cursorObj.fetchone()
                #print(current)
                #if found in frind_list and DB.is_friend = 1
                if(( current[0] in friend_list) and (current[4] == 1)):
                    #remove from friend_list
                    friend_list.remove(current[0])
                #if found in friend_list with DB.is_friend = 0
                elif(( current[0] in friend_list) and (current[4] == 0)):
                    #update data.is_friend = 1
                    entities = (now.replace(microsecond=0), current[0])
                    cursorObj.execute('''UPDATE connections SET isFriend = 1, friendDate = ?  WHERE user_IDs = ?''', entities)
                    DB.commit()
                    #remove name from friends list
                    friend_list.remove(current[0])
                #if not found in friend_list
                else:
                    #update DB.is_friend = 0
                    entities = (current[0],)
                    cursorObj.execute('''UPDATE connections SET isFriend = 0, friendDate = ''  WHERE user_IDs = ?''', entities)
                    DB.commit()
                cF.progress(((progressTotal-(progressTotal-row))/progressTotal)*100)

            #names in friend_list
            while( friend_list ):
                #add to data
                entities = ( friend_list[0], "", 0, '', 1, now.replace(microsecond=0), 0, 0)
                cursorObj.execute('''INSERT INTO connections VALUES(?, ?, ?, ?, ?, ?, ?, ?)''', entities)
                DB.commit()
                #remove name from friend_list
                del friend_list[0]
                cF.progress(((progressTotal-len(friend_list))/progressTotal)*100)

            #if friend_list is not empty there is an error.
            cF.endProgress()
            if( friend_list ):
                print("Error: Friends list is not empty after saving all friends")

        if followerDif or followers_to_thank:
            tweetSent = False
            followers_to_thank = 0
            cpy_follower_list = follower_list.copy()
            ######################################update is_follower (?repeat until tweet sent?)<- maybe not###########
            rowsInDB = cF.total_rows(cursorObj, 'connections', False)
    #        cF.startProgress('Updating is_Follower')
    #        progressTotal = (len(follower_list) + rowsInDB)

            #name in the DB
            for row in range( 1, ( rowsInDB + 1)):
                cursorObj.execute("SELECT * FROM connections WHERE ROWID = {}".format( row))
                current = cursorObj.fetchone()
                #if found in follower_list with data.is_follower = 1
                if( (current[0] in cpy_follower_list) and ( current[2] == 1)):
                    #if data.thanked = 0 and time_since_last_tweet > delay
                    if( (current[6] == 0) and (tweetSent  == False)):
                        userName = cF.userName(current[0])
                        #send thank you tweet
                        cF.followTweet(userName)
                        #data.thanked = 1
                        ent = (userName, current[0],)
                        cursorObj.execute('''UPDATE connections SET screen_name = ?, thanked = 1 WHERE user_IDs = ?''', ent)
                        DB.commit()
                        tweetSent = True
                    #else if data.thanked = 0 and time_since_last_tweet < delay
                    elif((current[6] == 0) and (tweetSent  == True)):
                        #people to than +1
                        followers_to_thank += 1
                    #remove name from follower_list
                    cpy_follower_list.remove(current[0])
                #if found in follower_list with data.is_follower = 0
                elif ((current[0] in cpy_follower_list) and (current[2] == 0)):
                    #if data.thanked = 0
                    if ((current[6] == 0) and (tweetSent == False)):
                        userName = cF.userName(current[0])
                        #if data.is_friend = 1
                        if (current[4] == 1):
                            #"follow back thanks"
                            cF.followBackTweet(userName)
                            tweetSent = True
                        #else
                        else:
                            #"thanks"
                            cF.followTweet(userName)
                            tweetSent = True
                        #data.thanked = 1
                        ent = (userName, now.replace(microsecond=0), current[0],)
                        cursorObj.execute('''UPDATE connections SET screen_name = ?, isFollower = 1, followDate = ?, thanked = 1 WHERE user_IDs = ?''', ent)
                        DB.commit()
                    #else if data.rethanked = 0
                    elif ((current[6] == 1) and (tweetSent == False)):
                        userName = cF.userName(current[0])
                        #if data.is_friend = 1
                        if (current[4] == 1):
                            #"follow back rethanks"
                            cF.reFollowBackTweet(userName)
                            tweetSent = True
                        #else
                        else:
                            #"rethanks"
                            cF.reFollowTweet(userName)
                            tweetSent = True
                        #data.rethanked = 1
                        ent = (userName, now.replace(microsecond=0), current[0],)
                        cursorObj.execute('''UPDATE connections SET screen_name = ?, isFollower = 1, followDate = ?, rethanked = 1 WHERE user_IDs = ?''', ent)
                        DB.commit()
                    elif (tweetSent == True):
                        followers_to_thank += 1
                    #remove name from follower_list
                    cpy_follower_list.remove(current[0])
                #if not found in follower_list
                elif (current[0] not in cpy_follower_list):
                    #update data.is_follower = 0
                    ent = (current[0],)
                    cursorObj.execute('''UPDATE connections SET isFollower = 0, followDate = ''  WHERE user_IDs = ?''', ent)
                    DB.commit()
                    #remove name from follower_list

            #name in follower_list
            for ID in cpy_follower_list:
                #if in data
                    #error
                #add to data
                cursorObj = DB.cursor()
                entities = (ID, "", 1, now.replace(microsecond=0), 0, '', 0, 0)
                cursorObj.execute('''INSERT INTO connections VALUES(?, ?, ?, ?, ?, ?, ?, ?)''', entities)
                DB.commit()
                #"thanks"
                if(tweetSent  == False):
                    userName = cF.userName(ID)
                    #send thank you tweet
                    cF.followTweet(userName)
                    #data.thanked = 1
                    ent = (userName, ID,)
                    cursorObj.execute('''UPDATE connections SET screen_name = ?, thanked = 1 WHERE user_IDs = ?''', ent)
                    DB.commit()
                    tweetSent = True
                #else if tweet recently sent put in queue
                elif(tweetSent  == True):
                    #people to than +1
                    followers_to_thank += 1
                #remove name from follower_list
                cpy_follower_list.remove(ID)

	    ## The follower list pulled from twitter should be empty now
            if len(cpy_follower_list):
                #error
                print("Error: Followers list copy is not empty after saving all followers")

            ##save the screen_name of up to 20 users missing them in the DB.

    #followers_to_thank = 1 #dev
    print('Pausing loop, people to thank = %d' % followers_to_thank)
    time.sleep(loopPause)

    #exit() #dev

