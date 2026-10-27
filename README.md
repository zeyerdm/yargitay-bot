# ⚖️ Yargıtay Karar Doğrulama Botu

> Yerel arşivdeki Yargıtay karar metinlerini resmî **karararama.yargitay.gov.tr** sitesindeki orijinalleriyle otomatik olarak karşılaştıran, yapısal bozuklukları tespit edip raporlayan Python / Playwright veri kalite aracı.
>
> *A Python + Playwright data-quality bot that cross-checks a local archive of Turkish Court of Cassation decisions against the official search portal and reports structural corruption.*

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-2EAD33?logo=playwright&logoColor=white)

## 📌 Proje Hakkında

Hukuk ve Ceza Genel Kurulu kararlarından oluşan büyük bir metin arşivi, HTML'den dönüştürülürken bazı dosyalarda kelimelerin birleşmesi (`kararıtemyiz`, `2012numarası` …) veya metin eksilmesi gibi hatalar içerebilir. Bu bot, her kararın Esas/Karar numarasını dosya adından çıkarır, resmî sitede aynı kararı bulur, iki metni karşılaştırır ve sonucu raporlar. Böylece veritabanına yalnızca doğrulanmış (temiz) kararların aktarılması sağlanır.

## ⚙️ Nasıl Çalışır?

1. **Tarama** — Karar klasöründeki tüm `.txt` dosyaları bulunur; dosya adından Esas ve Karar numaraları ayrıştırılır.
2. **Resmî metni çekme** — Playwright ile Yargıtay Karar Arama sitesinde detaylı arama yapılır ve karar metni okunur. Hız için görsel, CSS ve font istekleri engellenir.
3. **Karşılaştırma** — Yerel metinde birleşik kelime kalıpları (regex) aranır; boşluklar hariç karakter sayıları resmî metinle karşılaştırılır.
4. **Raporlama** — Her dosya `TEMİZ`, `❌ HATALI`, `❌ EKSİK / FAZLA` veya `⚠️ UYARI` olarak CSV ve Markdown raporlarına yazılır. İşlenen dosyalar kaydedildiği için bot kaldığı yerden devam edebilir.
5. **Gün sonu kontrolü** — Zaman aşımına uğrayan veya hatalı görünen kayıtlar tekrar kontrol edilir.
6. **Normalizasyon** — Temiz olarak işaretlenen kararlar ayrı bir klasöre kopyalanarak veritabanına aktarıma hazırlanır.

## 📁 Proje Yapısı

| Dosya | Görevi |
| --- | --- |
| `yargitay_analiz.py` | Ana bot: tarama, resmî siteden metin çekme, karşılaştırma ve raporlama |
| `gun_sonu_kontrol.py` | Gün sonu kalite kontrolü (uyarı/hata alan kayıtları yeniden doğrular) |
| `sirket_hizli_tarama.py` | İnternete çıkmadan, yalnızca regex kalıplarıyla hızlı bozukluk taraması |
| `veritabani_hazirlik.py` | Temiz kararları normalize klasörüne kopyalar |
| `site_baglanti_testi.py` | Karar arama sitesine erişimi ve form seçicilerini test eder |
| `config.py` | Tüm klasör ve rapor yolları |
| `ornekler/` | Örnek karar metni ve örnek rapor çıktıları |

## 📊 Örnek Çıktı

Örnek bir çalışmada 93 karar incelenmiştir:

| Durum | Adet |
| --- | --- |
| ✅ TEMİZ | 64 |
| ⚠️ UYARI (siteden yanıt alınamadı) | 23 |
| ❌ EKSİK / FAZLA | 6 |

Ayrıntılar için: [`ornekler/ornek_rapor.md`](ornekler/ornek_rapor.md)

## 🚀 Kurulum ve Kullanım

```bash
pip install -r requirements.txt
playwright install chromium

# Karar metinlerini veri/kararlar/ klasörüne koyun (veya KARAR_KLASORU ortam değişkenini ayarlayın)
python yargitay_analiz.py       # karşılaştırma ve raporlama
python gun_sonu_kontrol.py      # gün sonu tekrar kontrolü
python veritabani_hazirlik.py   # temiz kararları ayırma
```

| Ortam değişkeni | Varsayılan |
| --- | --- |
| `KARAR_KLASORU` | `veri/kararlar` |
| `RAPOR_KLASORU` | `raporlar` |
| `NORMALIZE_KLASORU` | `veri/normalize_edilmis_kararlar` |
| `BOZUK_KLASORU` | `raporlar/bozuk_dosyalar` |

## 🛠️ Kullanılan Teknolojiler

- Python 3 (`re`, `csv`, `json`, `os`)
- Playwright (Chromium, headless tarayıcı otomasyonu)

## 👩‍💻 Geliştirici

**Zeynep Erdem** — [github.com/zeyerdm](https://github.com/zeyerdm)
