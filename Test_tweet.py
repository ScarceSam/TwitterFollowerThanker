from twython import Twython

from auth import (
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
)

twitter = Twython(
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
)

message = "Hello, World! \n\nThis is Test_tweet.py from @ScarceSam's Auto follower-thanking script (~60% WIP) found at: \nhttps://github.com/ScarceSam/TwitterFollowerThanker\nDid it work?"
twitter.update_status(status=message)
print("Tweeted:\n%s\n" % message)
