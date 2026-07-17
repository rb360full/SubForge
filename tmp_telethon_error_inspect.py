from telethon import errors
import telethon
print('telethon', telethon.__version__)
for name in dir(errors):
    if 'Username' in name:
        print(name)
