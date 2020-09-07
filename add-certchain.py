import certifi
from pathlib import Path

certs_pem = Path('certs/CA_CHAIN.pem')
#print(certs_pem)
print('Adding custom certs to Certifi store...')
cafile = certifi.where()
with open(certs_pem, 'rb') as infile:
    customca = infile.read()
with open(cafile, 'ab') as outfile:
    outfile.write(customca)
print('done.')
 
