"""Ortak klasör ve dosya yolları.

Yollar ortam değişkenleriyle değiştirilebilir; tanımlı değilse proje klasörü altındaki
varsayılan klasörler kullanılır.
"""
import os
from datetime import datetime

PROJE_KLASORU = os.path.dirname(os.path.abspath(__file__))

# İncelenecek karar metinlerinin (.txt) bulunduğu klasör
KLASOR_YOLU = os.environ.get("KARAR_KLASORU", os.path.join(PROJE_KLASORU, "veri", "kararlar"))
# Raporların ve işlenen dosya listesinin yazılacağı klasör
RAPOR_KLASORU = os.environ.get("RAPOR_KLASORU", os.path.join(PROJE_KLASORU, "raporlar"))
# Temiz (doğrulanmış) kararların kopyalanacağı klasör
NORMALIZE_KLASORU = os.environ.get("NORMALIZE_KLASORU", os.path.join(PROJE_KLASORU, "veri", "normalize_edilmis_kararlar"))
# Yapısal bozukluk tespit edilen dosyaların kopyalanacağı klasör
BOZUK_KLASORU = os.environ.get("BOZUK_KLASORU", os.path.join(RAPOR_KLASORU, "bozuk_dosyalar"))

BUGUN = datetime.now().strftime("%Y-%m-%d")
ISLENENLER_DOSYASI = os.path.join(RAPOR_KLASORU, "islenenler.json")
CSV_RAPOR = os.path.join(RAPOR_KLASORU, f"rapor_{BUGUN}.csv")
MD_RAPOR = os.path.join(RAPOR_KLASORU, f"rapor_{BUGUN}.md")
HATALI_CSV = os.path.join(RAPOR_KLASORU, f"hatali_dosyalar_{BUGUN}.csv")

os.makedirs(RAPOR_KLASORU, exist_ok=True)
