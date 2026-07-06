import os
import csv

KLASOR_YOLU = r"C:\Users\Zeynep ERDEM\Downloads\Hukuk ve Ceza Kurul Son"
HEDEF_KLASOR = r"C:\Users\Zeynep ERDEM\Downloads\Normalize_Edilmis_Kararlar"

# En güncel raporu otomatik bulalım
RAPOR_KLASORU = r"C:\Users\Zeynep ERDEM\.gemini\antigravity-ide\scratch\kararlar"

def en_guncel_raporu_bul():
    raporlar = [f for f in os.listdir(RAPOR_KLASORU) if f.startswith("rapor_") and f.endswith(".csv")]
    if not raporlar:
        return None
    raporlar.sort(reverse=True) # En yeni tarihli olanı en üste alır
    return os.path.join(RAPOR_KLASORU, raporlar[0])

def normalize_et():
    RAPOR_DOSYASI = en_guncel_raporu_bul()
    if not RAPOR_DOSYASI:
        print("⚠️ HATA: Rapor dosyası bulunamadı!")
        return

    print(f"📄 Kullanılan Rapor Dosyası: {os.path.basename(RAPOR_DOSYASI)}")
    os.makedirs(HEDEF_KLASOR, exist_ok=True)
    
    temiz_dosyalar = []
    
    print("1. Rapor okunuyor ve TEMİZ dosyalar ayıklanıyor...")
    with open(RAPOR_DOSYASI, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader) # Başlığı atla
        for row in reader:
            if len(row) >= 3 and row[2] == "TEMİZ":
                temiz_dosyalar.append(row[0]) # Dosya adı
                
    print(f"Toplam {len(temiz_dosyalar)} adet TEMİZ dosya bulundu. Normalizasyon başlıyor...\n")
    
    basarili_islem = 0
    for dosya_adi in temiz_dosyalar:
        kaynak_yol = os.path.join(KLASOR_YOLU, dosya_adi)
        hedef_yol = os.path.join(HEDEF_KLASOR, dosya_adi)
        
        if not os.path.exists(kaynak_yol):
            # Dosya alt klasörlerde olabilir, onu bulalım
            bulunanlar = [os.path.join(dp, f) for dp, dn, filenames in os.walk(KLASOR_YOLU) for f in filenames if f == dosya_adi]
            if bulunanlar:
                kaynak_yol = bulunanlar[0]
            else:
                print(f"⚠️ Dosya bulunamadı: {dosya_adi}")
                continue
                
        # Dosyayı oku
        try:
            with open(kaynak_yol, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"⚠️ Okuma hatası {dosya_adi}: {e}")
            continue
            
        # Normalizasyon Mantığı (Kırık Satırları Birleştir)
        normalize_edilmis_satirlar = []
        gecici_satir = ""
        
        for line in lines:
            stripped_line = line.strip()
            if not stripped_line:
                # Boş satırsa ve elimizde birikmiş satır varsa onu ekle
                if gecici_satir:
                    normalize_edilmis_satirlar.append(gecici_satir + "\n")
                    gecici_satir = ""
                normalize_edilmis_satirlar.append("\n") # Orijinal boşluğu koru
                continue
                
            if gecici_satir:
                gecici_satir += " " + stripped_line
            else:
                gecici_satir = stripped_line
                
            # Eğer bu satır nokta, iki nokta vs. ile bitiyorsa cümleyi kapat
            if gecici_satir[-1] in ".!?:;,":
                normalize_edilmis_satirlar.append(gecici_satir + "\n")
                gecici_satir = ""
                
        # Dosyanın sonunda açık kalan satır varsa ekle
        if gecici_satir:
            normalize_edilmis_satirlar.append(gecici_satir + "\n")
            
        # Yeni dosyaya yaz
        try:
            with open(hedef_yol, 'w', encoding='utf-8') as f:
                f.writelines(normalize_edilmis_satirlar)
            basarili_islem += 1
        except Exception as e:
            print(f"⚠️ Yazma hatası {dosya_adi}: {e}")
            
    print(f"\n✅ İŞLEM TAMAMLANDI! {basarili_islem} dosya kırık satırlardan kurtarılarak şu klasöre kopyalandı:")
    print(f"📁 {HEDEF_KLASOR}")

if __name__ == "__main__":
    normalize_et()
