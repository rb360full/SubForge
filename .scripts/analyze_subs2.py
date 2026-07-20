import base64,re
p='subscriptions/Telegram-List1.txt'
with open(p,'rb') as f:
    raw=f.read()

# helper to parse nodes from text
def parse_nodes(text):
    lines=[ln.strip() for ln in text.splitlines() if ln.strip()!='']
    nodes=[]
    for ln in lines:
        parts=re.split(r'(?=(?:vmess|vless|trojan|ssr|ss|trojan-go)://)', ln)
        for part in parts:
            if part.strip():
                nodes.append(part.strip())
    return nodes

# 1) treat as raw text
try:
    txt=raw.decode('utf-8')
except:
    txt=None
raw_nodes = parse_nodes(txt or '') if txt else []

# 2) try base64 decode whole file
b64_nodes=[]
try:
    dec=base64.b64decode(raw)
    dec_txt=dec.decode('utf-8',errors='replace')
    b64_nodes = parse_nodes(dec_txt)
    b64_ok=True
except Exception as e:
    b64_ok=False

print('file:',p)
print('raw_text_lines:', len((txt or '').splitlines()) if txt else 0)
print('raw_parsed_nodes:', len(raw_nodes))
print('raw_unique:', len(set(raw_nodes)))
print('base64_decoded_ok:', b64_ok)
if b64_ok:
    print('b64_parsed_nodes:', len(b64_nodes))
    print('b64_unique:', len(set(b64_nodes)))

# show duplicates in best candidate
best = b64_nodes if b64_ok and len(b64_nodes)>0 else raw_nodes
uniq = list(dict.fromkeys(best))
print('best_parsed_count:', len(best))
print('best_unique:', len(uniq))
print('best_duplicates:', len(best)-len(uniq))

# invalid entries sample
valid_prefixes=('vmess://','vless://','trojan://','ss://','ssr://','trojan-go://','trojan-go:')
invalid=[n for n in best if not n.startswith(valid_prefixes)]
print('invalid_count:', len(invalid))
if invalid:
    print('invalid_sample:', invalid[:5])

print('\n--- first 10 parsed nodes ---')
for i,n in enumerate(best[:10],1):
    print(i, n[:300])
