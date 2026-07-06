import os
import glob
import shutil
import re

# Sisteminize (Zeynep ERDEM) özel ayarlanmış yollar
KLASOR_YOLU = r"C:\Users\Zeynep ERDEM\Downloads\Hukuk ve Ceza Kurul Son" 
HEDEF_KLASOR = r"C:\Users\Zeynep ERDEM\.gemini\antigravity-ide\scratch\kararlar\Sirket_Bozuk_Dosyalar"

def bozuk_dosyalari_bul_ve_listele():
    bozuk_dosyalar = []
    
    os.makedirs(HEDEF_KLASOR, exist_ok=True)
    
    print(f"🔍 '{KLASOR_YOLU}' dizinindeki dosyalar taranıyor...")
    txt_dosyalari = glob.glob(os.path.join(KLASOR_YOLU, "**/*.txt"), recursive=True)
    
    if not txt_dosyalari:
        print("⚠️ HATA: Belirtilen klasörde hiç .txt uzantılı dosya bulunamadı! Klasör yolunu kontrol et.")
        return

    # Sadece HTML birleşme hatalarına odaklanan KESİN kalıplar
    aranacak_kaliplar = [
        re.compile(r"\d{4}numaras[ıi]", re.IGNORECASE),            # Örn: 2012NUMARASI
        re.compile(r"mahkemesitarih[iı]", re.IGNORECASE),          # Örn: mahkemesitarihi
        re.compile(r"karar[ıi]temyiz", re.IGNORECASE),             # Örn: kararıtemyiz
        re.compile(r"vekil[iı]hukuk", re.IGNORECASE),              # Örn: vekiliHUKUK
        re.compile(r"direnilmi[şs]tir\.?[tT]emyiz", re.IGNORECASE),# Örn: direnilmiştir.TEMYİZ
        
        # --- YENİ EKLENEN CEZA DAİRESİ KALIPLARI ---
        re.compile(r"\d{4,5}yarg[ıi]tay", re.IGNORECASE),          # Örn: 30984Yargıtay
        re.compile(r"dairesimahkemesi", re.IGNORECASE),            # Örn: DairesiMahkemesi
        re.compile(r"cezag[üu]n[üu]", re.IGNORECASE)               # Örn: CezaGünü
    ]

    for dosya_yolu in txt_dosyalari:
        icerik = ""
        try:
            with open(dosya_yolu, "r", encoding="utf-8") as f:
                icerik = f.read()
        except UnicodeDecodeError:
            try:
                with open(dosya_yolu, "r", encoding="cp1254") as f:
                    icerik = f.read()
            except Exception:
                continue

        # Sadece kesin kanıtlara (yapışık kelimelere) bakıyoruz. 
        for kalip in aranacak_kaliplar:
            if kalip.search(icerik):
                bozuk_dosyalar.append(dosya_yolu)
                break # Dosyanın bozuk olduğunu kanıtlayan 1 tane yapı bulması yeterli

    print(f"\n📊 Toplam {len(txt_dosyalari)} dosya tarandı.")
    print(f"🚨 {len(bozuk_dosyalar)} adet kesin bozuk formatlı dosya bulundu.")
    
    #  Kopyalama işlemi
    if bozuk_dosyalar:
        print("\n🚀 Kopyalama işlemi başlıyor...")
        basarili_kopyalama = 0
        for bd in bozuk_dosyalar:
            try:
                shutil.copy(bd,HEDEF_KLASOR)
                basarili_kopyalama += 1
            except Exception as e:
                print(f"⚠️ Kopyalama hatası ({os.path.basename(bd)}): {e}")
                
        print(f"✅ {basarili_kopyalama} adet dosya '{HEDEF_KLASOR}' konumuna başarıyla kopyalandı!")
    else:
        print("✅ Kopyalanacak bozuk dosya bulunamadı.")

if __name__ == "__main__":
    bozuk_dosyalari_bul_ve_listele()
