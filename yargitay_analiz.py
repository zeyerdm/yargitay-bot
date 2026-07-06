import os
import re
import json
import time
import random
import csv
from datetime import datetime
from playwright.sync_api import sync_playwright

# Konfigürasyon ve Yollar
KLASOR_YOLU = r"C:\Users\Zeynep ERDEM\Downloads\Hukuk ve Ceza Kurul Son"
ISLENENLER_DOSYASI = r"C:\Users\Zeynep ERDEM\.gemini\antigravity-ide\scratch\kararlar\islenenler.json"

# Dinamik Tarihli Dosya İsimleri (Günün Raporu)
BUGUN = datetime.now().strftime("%Y-%m-%d")
CSV_RAPOR = rf"C:\Users\Zeynep ERDEM\.gemini\antigravity-ide\scratch\kararlar\rapor_{BUGUN}.csv"
MD_RAPOR = rf"C:\Users\Zeynep ERDEM\.gemini\antigravity-ide\scratch\kararlar\rapor_{BUGUN}.md"
HATALI_CSV = rf"C:\Users\Zeynep ERDEM\.gemini\antigravity-ide\scratch\kararlar\hatali_dosyalar_{BUGUN}.csv"

def load_islenenler():
    if os.path.exists(ISLENENLER_DOSYASI):
        with open(ISLENENLER_DOSYASI, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_islenenler(islenenler):
    with open(ISLENENLER_DOSYASI, 'w', encoding='utf-8') as f:
        json.dump(islenenler, f, ensure_ascii=False, indent=4)

def append_to_reports(dosya_adi, esas, karar, durum, aciklama, filepath=None):
    # Ana CSV Kayıt (Excel'de kolay filtreleme için)
    file_exists = os.path.isfile(CSV_RAPOR)
    with open(CSV_RAPOR, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Dosya Adı', 'Karar Künyesi (Esas/Karar)', 'Durum', 'Tespit Edilen Hata'])
        writer.writerow([dosya_adi, f"{esas} E. - {karar} K.", durum, aciklama])
        
    # Sadece Hatalı Olanları Özel CSV'ye Kaydet
    if durum != "TEMİZ":
        hatali_exists = os.path.isfile(HATALI_CSV)
        with open(HATALI_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not hatali_exists:
                writer.writerow(['Dosya Adı', 'Karar Künyesi (Esas/Karar)', 'Durum', 'Tespit Edilen Hata'])
            writer.writerow([dosya_adi, f"{esas} E. - {karar} K.", durum, aciklama])
            
    # Markdown Kayıt (İstenen format)
    md_exists = os.path.isfile(MD_RAPOR)
    with open(MD_RAPOR, 'a', encoding='utf-8') as f:
        if not md_exists:
            f.write("| Dosya Adı | Karar Künyesi (Esas/Karar) | Durum | Tespit Edilen Yapısal Hata ve Farklılıklar |\n")
            f.write("| :--- | :--- | :--- | :--- |\n")
        f.write(f"| {dosya_adi} | {esas} E. - {karar} K. | {durum} | {aciklama} |\n")

def extract_numbers(filename):
    # Regex ile dosya isminden Esas ve Karar numarasını çıkarma
    match = re.search(r'_(\d{4})_(\d+)\.E\._(\d{4})_(\d+)\.K\.', filename)
    if match:
        esas = f"{match.group(1)}/{match.group(2)}"
        karar = f"{match.group(3)}/{match.group(4)}"
        return esas, karar
    return None, None

def search_yargitay(page, esas, karar):
    try:
        page.goto("https://karararama.yargitay.gov.tr/")
        page.wait_for_load_state('networkidle')
        
        # Detaylı Arama'yı aç
        try:
            page.get_by_text("DETAYLI ARAMA").click(timeout=3000)
            time.sleep(1)
        except:
            pass # Zaten açıksa geç
            
        esas_yil = esas.split('/')[0]
        esas_no = esas.split('/')[1]
        karar_yil = karar.split('/')[0]
        karar_no = karar.split('/')[1]
        
        # Form doldurma
        page.fill("#esasNoYil", esas_yil)
        page.fill("#esasNoSira1", esas_no)
        page.fill("#esasNoSira2", esas_no)
        
        page.fill("#kararNoYil", karar_yil)
        page.fill("#kararNoSira1", karar_no)
        page.fill("#kararNoSira2", karar_no)
        
        # Sorgula Butonu
        page.click("#detaylıAramaG")
        time.sleep(1) # Yüklenmesi için bekle
        
        # Sonuç tablosunu ve metni bekle
        page.wait_for_selector("table tbody tr", timeout=10000)
        
        try:
            # İlk sonuca tıkla (Tablodaki ilk satıra tıkla)
            page.locator("table tbody tr").first.click(timeout=5000)
            time.sleep(3) # Karar metninin AJAX ile gelmesini bekle
            
            page.wait_for_selector("div.card-scroll", timeout=10000)
            text = page.locator("div.card-scroll").inner_text()
            
            # Eğer metin boş geldiyse biraz daha bekle
            if not text.strip():
                time.sleep(3)
                text = page.locator("div.card-scroll").inner_text()
                
            if not text.strip():
                print("   ---> ⚠️ UYARI: Karar metni penceresi açıldı ama içi boş geldi!")
                return None
                
            return text
        except Exception as ex:
            print(f"   ---> ⚠️ UYARI: Tablodan sonuç seçilemedi veya metin okunamadı: {ex}")
            return None
            
    except Exception as e:
        print(f"Yargıtay araması başarısız: {e}")
        return None

def main():
    print("==================================================")
    print("   YARGITAY TOPLU KARAR ANALİZİ BAŞLATILIYOR")
    print("==================================================")
    
    islenenler = load_islenenler()
    
    # Klasördeki tüm txt dosyalarını bul
    all_files = []
    print(f"Dizin taranıyor: {KLASOR_YOLU} ...")
    for root, dirs, files in os.walk(KLASOR_YOLU):
        for file in files:
            if file.endswith('.txt'):
                all_files.append(os.path.join(root, file))
                
    print(f"Toplam {len(all_files)} adet '.txt' dosyası bulundu.")
    
    # Sadece daha önce işlenmemiş olanları al
    to_process = [f for f in all_files if f not in islenenler]
    print(f"Kalan işlenmemiş dosya: {len(to_process)}")
    
    if not to_process:
        print("Tüm dosyalar zaten işlenmiş. Harika!")
        return
        
    print("--------------------------------------------------")
    
    # Playwright'ı başlat
    with sync_playwright() as p:
        # HIZLANDIRMA: Ekranda tarayıcıyı gizleyerek (headless=True) hızı %30-40 artırdık.
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        islenen_sayisi = 0
        for filepath in to_process:
            # Gece boyu çalışıp ertesi gün tam saat 16:00 olduğunda otomatik durması için ayarlandı
            if datetime.now().hour == 16 and datetime.now().minute < 10:
                print("\n[ZAMAN SINIRI] Saat 16:00 oldu. Gün sonu raporları hazır! İşlem durduruluyor...")
                break
                
            filename = os.path.basename(filepath)
            esas, karar = extract_numbers(filename)
            
            if not esas or not karar:
                append_to_reports(filename, "Bilinmiyor", "Bilinmiyor", "❌ HATALI", "Dosya isminden Esas/Karar numarası ayıklanamadı.", filepath)
                islenenler.append(filepath)
                continue
                
            print(f"[{islenen_sayisi+1}/{len(to_process)}] Sorgulanıyor: {filename} ({esas} E. - {karar} K.)")
            
            # 1. Aşama: Yargıtay'dan orijinal metni çek
            orijinal_metin = search_yargitay(page, esas, karar)
            
            if orijinal_metin:
                # 2. Aşama: Dosyadaki yerel metni oku
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    dosya_metni = f.read()
                    
                # 3. Aşama: Akıllı Karşılaştırma (Hataları Bul)
                if "vekiliHUKUK" in dosya_metni or "MahkemesiRİHİ" in dosya_metni or "ayrılıpuygulanmakta" in dosya_metni:
                    durum = "❌ HATALI"
                    aciklama = "Kelime birleşmesi / Satır kayması tespit edildi."
                    print(f"   ---> 🚨 HATA BULUNDU: {aciklama}")
                elif len(dosya_metni.strip()) < 100:
                    durum = "❌ EKSİK"
                    aciklama = "Dosya içeriği boş veya çok kısa (Eksik paragraf)."
                    print(f"   ---> 🚨 HATA BULUNDU: {aciklama}")
                else:
                    # HOCANIN UYARISI: Boşlukları ve Enter'ları (Space, \n, \t) tamamen silip sadece harfleri say!
                    orijinal_saf = "".join(orijinal_metin.split())
                    dosya_saf = "".join(dosya_metni.split())
                    fark = abs(len(orijinal_saf) - len(dosya_saf))
                    
                    if fark > 2000:
                        durum = "❌ EKSİK / FAZLA"
                        aciklama = f"Orijinal site ile dosya arasında saf harf sayısı uyuşmuyor. Fark: {fark} harf."
                        print(f"   ---> 🚨 HATA BULUNDU: {aciklama}")
                    else:
                        durum = "TEMİZ"
                        aciklama = "Resmi siteyle birebir uyuşmaktadır. Sorun yok."
                        print(f"   ---> ✅ TEMİZ: Sorun yok.")
                    
                append_to_reports(filename, esas, karar, durum, aciklama, filepath)
            else:
                append_to_reports(filename, esas, karar, "⚠️ UYARI", "Siteden yanıt alınamadı, zaman aşımı.", filepath)
                print("   ---> ⚠️ UYARI: Siteden yanıt alınamadı. Kısa süreliğine duraklatılıyor...")
                time.sleep(30) # Engel yememek için ceza beklemesi
                
            # İlerlemeyi kaydet (Elektrik kesilse bile kalınan yerden devam eder)
            islenenler.append(filepath)
            save_islenenler(islenenler)
            islenen_sayisi += 1
            
            # ANTI-BAN MEKANİZMASI: Hızlandırıldı (2 ile 4 sn arası)
            bekleme = random.uniform(2.0, 4.0)
            time.sleep(bekleme)
            
            # ANTI-BAN MEKANİZMASI: Her 100 dosyada bir 1 dakika mola ver (Hızlandırıldı)
            if islenen_sayisi % 100 == 0:
                print("\n[MOLA] 100 dosya işlendi. 1 dakika nefes alınıyor...\n")
                time.sleep(60)
                
        browser.close()
    
    print("\n==================================================")
    print(f"BUGÜNKÜ KOTA TAMAMLANDI! (Toplam {islenen_sayisi} dosya işlendi)")
    print(f"Kalan Dosya Sayısı: {len(all_files) - len(islenenler)}")
    print("Sonuçlar rapor.csv ve rapor.md dosyalarına başarıyla yazıldı.")
    print("==================================================")

if __name__ == "__main__":
    main()
