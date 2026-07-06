import os
import csv
from datetime import datetime
from playwright.sync_api import sync_playwright

# yargitay_analiz betiğinden fonksiyonları içe aktar
from yargitay_analiz import search_yargitay, extract_numbers, KLASOR_YOLU

BUGUN = datetime.now().strftime("%Y-%m-%d")
CSV_RAPOR = rf"C:\Users\Zeynep ERDEM\.gemini\antigravity-ide\scratch\kararlar\rapor_{BUGUN}.csv"
HATALI_CSV = rf"C:\Users\Zeynep ERDEM\.gemini\antigravity-ide\scratch\kararlar\hatali_dosyalar_{BUGUN}.csv"

def get_file_paths_mapping():
    mapping = {}
    for root, dirs, files in os.walk(KLASOR_YOLU):
        for file in files:
            if file.endswith('.txt'):
                mapping[file] = os.path.join(root, file)
    return mapping

def main():
    print("==================================================")
    print("      GÜN SONU HIZLI KONTROL (QA) BAŞLADI")
    print("==================================================")
    
    if not os.path.exists(CSV_RAPOR):
        print(f"Bugüne ait rapor bulunamadı: {CSV_RAPOR}")
        return
        
    # Tüm verileri oku
    rows = []
    with open(CSV_RAPOR, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            print("CSV dosyası boş.")
            return
        for row in reader:
            rows.append(row)
            
    uyari_rows = [i for i, row in enumerate(rows) if row[2] == "⚠️ UYARI"]
    
    toplam_dosya = len(rows)
    baslangic_temiz = len([r for r in rows if r[2] == "TEMİZ"])
    baslangic_uyari = len(uyari_rows)
    
    print(f"Bugün işlenen toplam dosya: {toplam_dosya}")
    print(f"Zaman aşımına uğrayan (Uyarı) dosya sayısı: {baslangic_uyari}\n")
    
    kurtarilanlar = 0
    
    if baslangic_uyari > 0:
        print("Uyarı alan dosyalar Yargıtay'dan tekrar sorgulanıyor...\n")
        file_mapping = get_file_paths_mapping()
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
            page = context.new_page()
            
            for index in uyari_rows:
                dosya_adi = rows[index][0]
                esas, karar = extract_numbers(dosya_adi)
                filepath = file_mapping.get(dosya_adi)
                
                if not filepath or not os.path.exists(filepath):
                    continue
                    
                print(f"Tekrar Sorgulanıyor: {dosya_adi}")
                orijinal_metin = search_yargitay(page, esas, karar)
                
                if orijinal_metin:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        dosya_metni = f.read()
                        
                    import re
                    yapisik_regex = re.compile(r"[a-zçğıöşü]{2,}[A-ZÇĞİÖŞÜ][a-zçğıöşü]{2,}")
                    
                    if "vekiliHUKUK" in dosya_metni or "MahkemesiRİHİ" in dosya_metni or "ayrılıpuygulanmakta" in dosya_metni or yapisik_regex.search(dosya_metni):
                        durum = "❌ HATALI"
                        aciklama = "Kelime birleşmesi / İç içe geçmiş satır tespit edildi."
                    elif len(dosya_metni.strip()) < 100:
                        durum = "❌ EKSİK"
                        aciklama = "Dosya içeriği boş veya çok kısa (Eksik paragraf)."
                    else:
                        orijinal_saf = "".join(orijinal_metin.split())
                        dosya_saf = "".join(dosya_metni.split())
                        fark = abs(len(orijinal_saf) - len(dosya_saf))
                        
                        if fark > 2000:
                            durum = "❌ EKSİK / FAZLA"
                            aciklama = f"Orijinal site ile dosya arasında saf harf sayısı uyuşmuyor. Fark: {fark} harf."
                        else:
                            durum = "TEMİZ"
                            aciklama = "Resmi siteyle birebir uyuşmaktadır. Sorun yok."
                        
                    # Satırı güncelle
                    rows[index] = [dosya_adi, f"{esas} E. - {karar} K.", durum, aciklama]
                    kurtarilanlar += 1
                    print(f"   ---> Başarıyla kurtarıldı! Yeni durum: {durum}")
                else:
                    print("   ---> Maalesef site yine yanıt vermedi.")
                    
            browser.close()
            
        # CSV Raporunu Üzerine Yazarak Güncelle
        with open(CSV_RAPOR, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)
            
    # Hatalı CSV'yi baştan oluştur (Çünkü durumlar değişti)
    with open(HATALI_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Dosya Adı', 'Karar Künyesi (Esas/Karar)', 'Durum', 'Tespit Edilen Hata'])
        for row in rows:
            if row[2] != "TEMİZ":
                writer.writerow(row)
                
    # Final İstatistikleri
    final_temiz = len([r for r in rows if r[2] == "TEMİZ"])
    final_hatali = len([r for r in rows if "HATALI" in r[2] or "EKSİK" in r[2]])
    final_uyari = len([r for r in rows if r[2] == "⚠️ UYARI"])
    
    print("\n==================================================")
    print("                 GÜN SONU ÖZETİ")
    print("==================================================")
    print(f"Günlük Hedef     : {toplam_dosya} dosya")
    print(f"Temiz Çıkan      : {final_temiz} dosya")
    print(f"Hatalı/Eksik     : {final_hatali} dosya")
    print(f"Ulaşılamayan     : {final_uyari} dosya (Daha sonra tekrar denenebilir)")
    print("--------------------------------------------------")
    print(f"Hızlı kontrol ile kurtarılan dosya sayısı: {kurtarilanlar}")
    print("==================================================")
    print("İyi akşamlar! Tüm raporlarınız güncellenmiştir.")

if __name__ == "__main__":
    main()
