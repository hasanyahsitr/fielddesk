# FieldDesk'i beş dakikada dene

[English](FIRST_RUN.md) · [README'ye dön](../README.tr.md)

Windows x64 bilgisayar ve örnek belgeler kullan. FieldDesk 0.8.0 bir önizleme sürümüdür. Bu deneme için API anahtarı, yapay zekâ modeli veya uygulamanın kendisi için yönetici yetkisi gerekmez; bilgisayarındaki Windows politikaları çalıştırmayı sınırlayabilir. Yavaş indirmeler beş dakikadan uzun sürebilir.

## 1. Çalışma alanını aç

[Önizleme yayınından](https://github.com/hasanyahsitr/fielddesk/releases/tag/v0.8.0) `FieldDesk-0.8.0-windows-x64.zip` dosyasını indir. ZIP'in tamamını `C:\FieldDesk-Test` gibi kısa bir yola çıkar ve `START.cmd` dosyasını aç. `runtime` klasörü yanında kalmalı; ayrıca Python kurman gerekmez.

Üst çubuktan **Türkçe** seç. **Çanta hazırlığı** ekranında ayrı bir deneme klasörü seç, kontrol et ve sunulursa klasör hazırlığını uygula. Bu işlem eksik klasörleri oluşturur; program kurmaz veya model indirmez.

Windows ya da kurum politikası bir bileşeni engellerse mesajı kaydedip bildir. Denemeyi tamamlamak için korumaları kapatma. Önizleme paketi kod imzalı değildir.

## 2. Bir program hazırla

**Uygulamalar → Program indir** bölümünde **Notepad++** ara, işaretle ve **Seçilenleri indir ve hazırla** düğmesine bas. İnternet gerekir. Hazır olduğunda aç. Katalog, hazırlıktan önce sabit boyut ve SHA-256 kontrolü yapar. Kurulum dosyası olan programlarda yalnızca indirme yapılır; otomatik kurulum yoktur.

## 3. İki örnek PDF'i birleştir

**İş akışları → PDF birleştir** bölümüne iki küçük deneme PDF'i ekle. **Sonucu önizle** ile sıralamayı ve sayfa sayısını kontrol et; **Onayla ve işlemi başlat** düğmesine bas. Çıktı klasöründeki `birlestirilmis.pdf` dosyasını incele. Çıktılar `12_ISLER/Ciktilar` altında oluşur; kaynaklar korunur.

## 4. Bir proje notu bul

Çalışma alanının içinde `04_PROJELER/Sample/notes.txt` dosyası oluştur ve şu örnek metni yaz:

```text
Örnek teslim: salı gününden önce iki PDF'i gözden geçir.
```

**Bilgi merkezi → Dizini güncelle** düğmesine bas. Tarama bitince `teslim` ara ve `notes.txt` sonucunu kontrol et. Belge araması yapay zekâ modeli gerektirmez. Taranan çalışma klasörlerinin dışındaki dosyalar kendiliğinden görünmez.

## Sohbeti sonra deneyebilirsin

Asistan normal sohbeti ve ayrı bir belge modunu destekler. Yerel sohbet için uyumlu llama.cpp ve desteklenen GGUF model gerekir; bunlar 23 MB pakete dahil değildir. OCR için Tesseract ve dil dosyaları gerekir. Bulut sohbetinde kendi sağlayıcı erişimini ve API anahtarını kullanırsın. Bu bileşenlerin eksik olması temel denemenin başarısız olduğu anlamına gelmez. [README](../README.tr.md) ayrıntıları açıklar.

## Geri bildirim ver

Tekrarlanabilir hatalar için [hata bildirimi](https://github.com/hasanyahsitr/fielddesk/issues/new?template=bug_report.yml), genel deneyim için [ilk kullanım geri bildirim başlığı](https://github.com/hasanyahsitr/fielddesk/issues?q=is%3Aissue%20%22First-run%20feedback%22) kullanılabilir.

- Windows sürümü, x64 bilgisi, kaynak kod/Windows ZIP seçimi ve dahili/USB disk.
- Tamamlanan adımlar, takıldığın yer ve yaklaşık süre.
- Beklediğin ve gerçekleşen davranış; gerekirse örnek verili ekran görüntüsü.
- Tekrar kullanacağın işlev veya geri dönmeme sebebin.

Türkçe veya İngilizce yazabilirsin. Anahtarları, oturum bilgilerini, kişisel yolları ve gerçek belge alıntılarını paylaşma. Güvenlik açıkları için [özel bildirim](https://github.com/hasanyahsitr/fielddesk/security/advisories/new) kullan.
