import random, os
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

def Proxy():
# Path ke file proxy.txt
    file_path = os.getenv('PATH_PROXY')
    try:
        # Membaca file proxy.txt dan memasukkan proxy ke dalam list
        with open(file_path, 'r') as file:
            proxies = [line.strip() for line in file if line.strip()]
        
        # Memastikan daftar proxy tidak kosong
        if not proxies:
            print("File proxy.txt kosong atau tidak ada proxy yang valid.")
            proxies=None
        else:
            # Mengambil proxy secara acak
            proxies = random.choice(proxies)
            ip_port, user, password = proxies.rsplit(":", 2)
            proxies = f"{user}:{password}@{ip_port}"
            # print(f"Proxy yang dipilih secara acak : {proxies}")
    except FileNotFoundError:
        print(f"File tidak ditemukan: {file_path}")
        proxies=None
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        proxies =None
    return proxies

def proxy_get():
    # Koneksi ke mongodb
    client = MongoClient(os.getenv('DB_HOST'), username=os.getenv('DB_USER'), password=os.getenv('DB_PASS'), authSource=os.getenv('DB_NAME'), directConnection=True)
    db = client[os.getenv('DB_NAME')]
    collection = db['proxy']

    try:
        data = collection.aggregate([{"$sample": {"size": 1}}])
        for data in data:
            # proxy = data['proxy_address']
            full_proxy = data['proxy']
            
        client.close()
        return full_proxy
    except Exception as e:
        print(f"Error: {e}")
        client.close()
        return None

