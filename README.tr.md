# FieldDesk

**Windows çalışma çantanı bir diskte taşı.**

[English](README.md) · [Yol haritası](ROADMAP.md) · [Katkı rehberi](CONTRIBUTING.md)

**Önizleme sürümü · Windows x64 · Kaynak kod MIT lisanslı**

USB diskte veya harici diskte bir çalışma alanı taşı: programlarını seç, belgelerinle çalış ve istersen yerel yapay zekâyla aynı arayüzden sohbet et. FieldDesk Windows bilgisayarında çalışır. Program indirmeleri internet gerektirir; dosya iş akışları ve belge araması yereldir. Bulut sohbeti isteğe bağlıdır ve kendi API anahtarını kullanır.

[**Windows x64 indir · yaklaşık 23 MB**](https://github.com/hasanyahsitr/fielddesk/releases/download/v0.8.0/FieldDesk-0.8.0-windows-x64.zip) · [Demoyu izle](https://github.com/hasanyahsitr/fielddesk/releases/download/v0.8.0/FieldDesk-0.8.0-demo.mp4) · [İlk kullanım rehberi](docs/FIRST_RUN.tr.md)

![Kısa demo: program seçme, iki PDF birleştirme ve proje notu arama](docs/demo.gif)

Gerçek uygulama kaydı ve kurgusal örnek belgeler kullanıldı. GIF kısa bir seçkidir; video işlem sırasını gösterir. Yapay zekâ ve OCR için ek bileşen gerekir. [Demo ayrıntıları](docs/DEMO.md).

## Üç kullanım örneği

- **Başka bir Windows bilgisayarda çalışma çantası:** çalışma alanını harici diskte tut, seçtiğin araçları indir ve desteklenen taşınabilir programları menüden aç. Bilgisayarın politikaları ve programların ek gereksinimleri geçerlidir.
- **Belge teslimi:** iki PDF seç, sıralama ve sayfa sayısını önizle; kaynakları koruyarak yeni bir çıktı klasöründe birleştir.
- **Çevrimdışı proje notları:** notlarını çalışma alanında tut, yerel dizini güncelle ve içeriklerini bir bulut servisine göndermeden ara.

## Başla

[v0.8.0 önizleme yayınından](https://github.com/hasanyahsitr/fielddesk/releases/tag/v0.8.0) `FieldDesk-0.8.0-windows-x64.zip` dosyasını indir, tamamını çıkar ve `START.cmd` dosyasını aç. Python, pypdf, Pillow ve PDFium pakete dahildir; ayrıca Python kurman gerekmez. Çalışma alanı klasörünü seç ve hazırlık kontrolünü çalıştır. Bu işlem eksik klasörleri oluşturur; program veya model indirmez.

Varsayılan dil İngilizcedir. Üst çubuktan **Türkçe** seçilebilir; tercih çalışma alanına kaydedilir. Dil değiştirmek yazılmış mesajı veya görünen sohbeti silmez. Belgeler, dosya yolları ve model yanıtları otomatik çevrilmez. İngilizce PDF iş akışındaki bazı dinamik mesajlar önizleme sürümünde henüz Türkçedir.

İndirme kontrolü için PowerShell'de `Get-FileHash .\FieldDesk-0.8.0-windows-x64.zip -Algorithm SHA256` çalıştır ve sonucu yayındaki `.sha256` dosyasıyla karşılaştır.

## Neler yapar?

- **Uygulamalar:** arama, favoriler, program başlatıcıları ve kendi taşınabilir çalıştırılabilir dosyalarını ekleme.
- **Program kataloğu:** resmî kaynaklardan 30 sabit sürümlü Windows x64 paketi; boyut ve SHA-256 kontrolü. 25 paket otomatik hazırlanır; 5 pakette yalnızca kurulum dosyası indirilir. Kurulum dosyaları kendiliğinden çalıştırılmaz.
- **Asistan:** yerel GGUF modelle normal sohbet ve sınırlı yakın konuşma bağlamı. Belgeler isteğe bağlıdır; ayrı belge modu ilgili alıntıları getirir. Model yanıt dili kullanıcı mesajını izler.
- **İsteğe bağlı API sohbeti:** NVIDIA, OpenAI, Google Gemini, Anthropic, Groq, OpenRouter, DeepSeek ve uyumlu yerel/özel uç noktalar. Erişim sağlayıcının model ve kotasına bağlıdır. Belge alıntıları buluta gönderilmeden önce incelenir.
- **Bilgi merkezi:** metin, kod, HTML, PDF, DOCX, XLSX ve PPTX içeriklerinde çevrimdışı arama. Eski Office biçimleri, şifreli belgeler ve gömülü nesneler desteklenmez; Excel formülleri hesaplanmaz.
- **İş akışları:** PDF birleştirme, görsel boyutlandırma/dönüştürme, OCR ve proje ortamı açma. Çıktılar ayrı görev klasörlerine yazılır; kaynaklar korunur. Proje kodu ve bağımlılık kurulumları otomatik çalıştırılmaz.
- **Sistem:** kapasite ve mevcut yedek kayıtları. İkinci fiziksel disk yedeği ayrıca yapılandırılır.

## Yerel yapay zekâ ve OCR

Büyük model dosyaları ve model çalıştırıcısı pakete dahil değildir. Uyumlu Windows x64 `llama-server.exe` ve desteklenen GGUF dosyası gerekir; dosya düzeni `app/engine.py` içinde tanımlıdır. Bu çalışma alanında küçük Gemma E2B seçeneği başlangıç için kullanıldı. HDD'de ilk yükleme birkaç dakika sürebilir. Bu sürümde yerel çıkarım CPU kullanır; model yanıtları özellikle önemli kararlarda kontrol gerektirir.

Normal sohbet için dizinlenmiş belge gerekmez. Yakın bağlam yalnızca açık sayfada, son dört mesajla ve mesaj başına en fazla 750 karakterle sınırlıdır. Sayfayı yenilemek geçmişi temizler; sağlayıcı veya normal/belge modu değişikliği bağlamı sıfırlar. Asistan metin sohbeti yapar; internet gezintisi, bilgisayar/telefon kontrolü veya sohbetten komut çalıştırma sunmaz.

OCR için ayrıca Tesseract motoru ve dil dosyaları gerekir; pakete dahil değildir.

## İndirmeler ve güncellemeler

Kesilen indirme, sunucu geçerli HTTPS Range yanıtını destekliyorsa kaldığı yerden devam eder. Arşivler boyut ve özet kontrolünden geçmeden açılmaz. 24 pakette resmî API, 6 pakette yayıncı sayfası üzerinden sürüm bilgisi kontrol edilir; karşılaştırma katalogdaki sabit sürümledir. Yeni sürümler otomatik indirilmez veya kurulmaz.

Yönetilen paketler geri alınabilir biçimde kaldırılır; dosyalar ve profil verileri saklandığı için bu işlem disk alanı boşaltmaz. İlgisiz mevcut klasörlerin üzerine yazılmaz. Üçüncü taraf lisansları, ağ veya ek çalışma zamanı gereksinimleri geçerlidir.

## Kaynak koddan çalıştır

```powershell
python -m pip install -r requirements.txt
python -X utf8 app/server.py --root "D:\FieldDesk"
```

Sunucu yalnızca yerel döngü adresinde çalışır. Değişiklik isteklerinde oturum, Host ve Origin kontrolleri uygulanır. API anahtarları varsayılan olarak oturumda tutulur; isteğe bağlı Windows DPAPI saklama kullanıcıya ve bilgisayara bağlıdır. Yerel servisi internete açma; kişisel çalışma alanını depoya ekleme.

Eski ATÖLYE çantaları desteklenir. `D:\ATOLYE`, `ATOLYE_ROOT`, `X-Atolye-*` ve dahili yapılandırma adları uyumluluk için korunur.

## Geri bildirim ve katkı

Önce [ilk kullanım rehberini](docs/FIRST_RUN.tr.md) dene; takıldığın yeri ve hangi işlevi tekrar kullanacağını paylaş. Türkçe ve İngilizce bildirim kabul edilir. Sürüm, Windows bilgisi ve örnek verilerle tekrarlama adımlarını ekle. Anahtarları, oturum bilgilerini ve özel belgeleri paylaşma. [Başlangıç görevleri](https://github.com/hasanyahsitr/fielddesk/issues?q=is%3Aissue%20is%3Aopen%20label%3A%22good%20first%20issue%22), [katkı rehberi](CONTRIBUTING.md), [güvenlik politikası](SECURITY.md), [değişiklikler](CHANGELOG.md) ve [yol haritası](ROADMAP.md) depoda yer alır.

Windows CI; işlev testleri, JavaScript sözdizimi, dil ve kaynak paket kontrollerini çalıştırır. Gerçek OCR ve model kontrolleri, ek yerel bileşenlerle ayrıca yapılır.

## Lisans

FieldDesk kaynak kodu [MIT lisanslıdır](LICENSE). Paketteki bağımlılıklar ve ayrıca indirilen programlar kendi lisanslarına tabidir; [üçüncü taraf bildirimlerini](THIRD_PARTY_NOTICES.md) incele. Yayın paketinde kişisel dosyalar, API anahtarları, model ağırlıkları, ISO'lar veya program arşivin bulunmaz. Kaynak ZIP, Windows paketi ve demo ayrı indirmelerdir.

FieldDesk çalışma adıdır; isim uygunluğu, tasarım özgünlüğü veya marka tescili güvencesi verilmez.
