import lzma
import json

# Fayl yo'lini to'g'ri belgilang
path = r'C:\Users\user\Desktop\Sobranie Restourant Bot\wkxzode\wkxzode_63618969259.json.xz'

# Faylni ochib, ichidagi JSON ma'lumotlarini o'qing
with lzma.open(path) as file:
    json_bytes = file.read()
    json_str = json_bytes.decode('utf-8')
    data = json.loads(json_str)

    print(data)
