import ipfshttpclient

def test_ipfs_connection():
    try:
        client = ipfshttpclient.connect()  # default: /dns/localhost/tcp/5001/http
        version = client.version()
        print("✅ Connected to IPFS!")
        print(f"IPFS Version: {version['Version']}")
    except Exception as e:
        print("❌ Failed to connect to IPFS:")
        print(str(e))

if __name__ == "__main__":
    test_ipfs_connection()
