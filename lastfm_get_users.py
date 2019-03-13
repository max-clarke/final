import pylast
import time
import pickle

# You have to have your own unique two values for API_KEY and API_SECRET
# Obtain yours from https://www.last.fm/api/account/create for Last.fm
API_KEY = "e1c4eb5ed5eec78f43ff7d2c82fe033a"  # this is a sample key
API_SECRET = "0776e51b111136a002f9f10a724460dc"

# In order to perform a write operation you need to authenticate yourself
print('logging in')
username = "jmclarke94"
password_hash = pylast.md5("Xkcd94!!")

network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET,
                               username=username, password_hash=password_hash)
print('status...\n')
print(network)

# seed user
usr = network.get_user('wildaman1')

user_list = usr.get_friends()
print('initial user list:\t')
print(user_list)

def user_list_descend(user_list):
    count = 0
    new_user_list = []
    
    
    for user in user_list:
        try:
            friends = user.get_friends()
            for friend in friends:
                if friend not in new_user_list:
                    new_user_list.append(friend)
                    time.sleep(.2)
                    count += 1
                    if count % 50 == 0:
                        print('current length of new new list:\n', len(new_user_list))
        except:
            continue  # just skip this user
    
    return new_user_list

print('exploring userlist')
for n in range(3):
    user_list = user_list_descend(user_list)
    print(f'current length is:\t {len(user_list)}')
    
print('finished exploring userlist')

with open('user_list.p', 'wb') as f:
    pickle.dump(user_list, f)
    
print('finished saving file')
