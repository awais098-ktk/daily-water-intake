import requests
import os

# Create the directory if it doesn't exist
os.makedirs('water_tracker/static/images/avatars', exist_ok=True)

# URLs for the avatar images
male_avatar_url = 'https://raw.githubusercontent.com/user-attachments/files/main/male_avatar.png'
female_avatar_url = 'https://raw.githubusercontent.com/user-attachments/files/main/female_avatar.png'

# Download the male avatar
response = requests.get(male_avatar_url)
if response.status_code == 200:
    with open('water_tracker/static/images/avatars/male_avatar.png', 'wb') as f:
        f.write(response.content)
    print("Male avatar downloaded successfully")
else:
    print(f"Failed to download male avatar: {response.status_code}")

# Download the female avatar
response = requests.get(female_avatar_url)
if response.status_code == 200:
    with open('water_tracker/static/images/avatars/female_avatar.png', 'wb') as f:
        f.write(response.content)
    print("Female avatar downloaded successfully")
else:
    print(f"Failed to download female avatar: {response.status_code}")
