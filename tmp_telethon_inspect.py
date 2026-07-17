import inspect
import telethon
from telethon import TelegramClient

print('telethon', telethon.__version__)
print('get_messages signature:', inspect.signature(TelegramClient.get_messages))
print('iter_messages signature:', inspect.signature(TelegramClient.iter_messages))
print('get_messages source preview:')
print(inspect.getsource(TelegramClient.get_messages)[:4000])
print('\n---\niter_messages source preview:')
print(inspect.getsource(TelegramClient.iter_messages)[:4000])
