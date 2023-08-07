import os

# Import the following modules
from pushbullet import PushBullet

# Get the access token from Pushbullet.com
access_token = os.environ.get('PBTOKEN')

# Taking input from the user
data = "the data"

# Taking large text input from the user
text = "the text"

# Get the instance using access token
pb = PushBullet(access_token)

# Send the data by passing the main title
# and text to be send
push = pb.push_note(data, text)
