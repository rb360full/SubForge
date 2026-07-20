import base64,re
p='subscriptions/Telegram-List1.txt'
with open(p,'rb') as f:
    raw=f.read()
try:
    txt=raw.decode('utf-8')
except:
    txt=None
# detect base64 payload heuristic
is_b64=False
if txt is not None:
    s=txt.strip()
    if '\n' not in s and re.fullmatch(r'[A-Za-z0-9+/=\\n]+', s[:200]):
        is_b64=True

if is_b64:
    try:
        dec=base64.b64decode(s)
        data=dec.decode('utf-8',errors='replace')
        source='base64_decoded'
    except Exception as e:
        data=txt
        source='raw_fallback'
else:
    data=txt or raw.decode('utf-8',errors='replace')
    source='raw'

lines=[ln.strip() for ln in data.splitlines() if ln.strip()!='']
# split multi-node lines by known schemes
nodes=[]
for ln in lines:
    parts=re.split(r'(?=(?:vmess|vless|trojan|ssr|ss|trojan-go)://)', ln)
    for ppart in parts:
        ppart=ppart.strip()
        if ppart:
            nodes.append(ppart)

unique=list(dict.fromkeys(nodes))
valid_prefixes=('vmess://','vless://','trojan://','ss://','ssr://','trojan-go://','trojan-go:')
invalid=[n for n in nodes if not n.startswith(valid_prefixes)]

print('file_path:',p)
print('source_detected:',source)
print('raw_line_count:', len(lines))
print('parsed_nodes_count:', len(nodes))
print('unique_nodes_count:', len(unique))
print('duplicates:', len(nodes)-len(unique))
print('invalid_count:', len(invalid))
if invalid:
    print('invalid_sample:', invalid[:5])
print('\n--- first 20 parsed nodes ---')
for i,n in enumerate(nodes[:20],1):
    print(i, n[:300])
