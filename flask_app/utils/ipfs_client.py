import ipfshttpclient

def get_ipfs_client():
    return ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
