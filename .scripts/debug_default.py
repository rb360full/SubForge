import base64
import re
from pathlib import Path

path = Path('subscriptions/default.txt')
text = path.read_text(encoding='utf-8').strip()
print('file_size', len(text))
print('contains_newline', '\n' in text)

try:
    decoded = base64.b64decode(text).decode('utf-8', errors='replace')
    print('decoded_ok true')
except Exception as exc:
    print('decoded_ok false', exc)
    decoded = text

print('decoded_lines', len(decoded.splitlines()))
print('decoded_prefix', decoded[:100])
print('decoded_suffix', decoded[-100:])

pat = re.compile(r'(?P<link>(?:vmess|vless|trojan|ss|socks)://[^\s<>"\n]+)', re.IGNORECASE)
links = pat.findall(decoded)
print('regex_matches', len(links))
print('unique_links', len(set(links)))
print('first_matches')
for i, link in enumerate(links[:30], 1):
    print(i, repr(link[:120]))

# find scheme counts
for scheme in ['vmess://', 'vless://', 'trojan://', 'ss://', 'socks://']:
    print(f'{scheme} count', decoded.count(scheme))

# detect fragments around suspicious positions
frags = []
for m in re.finditer(r'(?:vless|vmess|trojan|ss|socks)://', decoded, re.IGNORECASE):
    frags.append(decoded[max(0, m.start() - 20): m.end() + 50])
print('total scheme positions', len(frags))
print('first frag samples')
for frag in frags[:10]:
    print(repr(frag))
