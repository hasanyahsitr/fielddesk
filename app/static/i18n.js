'use strict';
// Turkish source messages keep stored categories and existing kits compatible.
// Only interface text is localized; user content and API payload values are preserved.
const EN = {
  'İçeriğe geç':'Skip to content','Taşınabilir araçlar':'Portable workspace','Çalışma alanı':'Workspace','Ana menü':'Main navigation',
  'Genel bakış':'Overview','Uygulamalar':'Apps','İş akışları':'Workflows','Asistan':'Assistant','Bilgi merkezi':'Library','Projeler':'Projects','Kurulum arşivi':'Installer archive','Sistem ve yedek':'System & backup','Çanta hazırlığı':'Workspace setup',
  'Yerel çalışma alanı':'Local workspace','Dosyaların bu diskte':'Your files stay on this drive','● Yerel oturum':'● Local session','Durumu yenile':'Refresh status','Dil':'Language',
  'Uygulamaların, dosyaların ve yerel araçların.':'Your apps, files and local tools.','Çalışma alanı ayarları':'Workspace settings','Çanta klasörü':'Workspace folder','Kontrol ediliyor…':'Checking…',
  'Uygulama':'Application','Kullanıma hazır':'Ready to use','Yerel model':'Local models','Çevrimdışı sohbet':'Offline chat','Dizindeki dosya':'Indexed files','Belge araması':'Document search','Boş alan':'Free space','Arşiv kontrol ediliyor':'Checking archive',
  'Hızlı erişim':'Quick access','Tüm uygulamalar':'All apps','Yerel kaynaklarında ara; asistanın ilgili dosyalardan bir yanıt hazırlasın.':'Search local sources or ask the assistant about relevant documents.','Bilgi merkezine git →':'Open library →','Yedekleme':'Backup','Yedek durumun kontrol ediliyor':'Checking backup status','Sistem ve yedek →':'System & backup →',
  'Çantandaki programlar ve klasörler. Açmak için bir uygulama seç.':'Programs and folders on your drive. Choose an app to open it.','Program indir':'Get apps','Uygulama ekle':'Add app','Uygulama, kategori veya iş ara…':'Search apps, categories or tasks…','Uygulamalarda ara':'Search apps','Kategori / tür':'Category / type','İşlem':'Action',
  'Tümü':'All','Favoriler':'Favorites','Yazılım':'Development','Günlük':'Everyday','Medya':'Media','Tasarım':'Design','Ofis':'Office','Dosyalar':'Files','Kurulum':'Installers','Kurtarma':'Recovery','Belgeler':'Documents','Sistem':'System','Yapay zekâ':'AI','Geliştirme araçları':'Developer tools','Kendi araçlarım':'My tools',
  'Aç':'Open','aç':'open','Eksik':'Missing','dosya eksik':'file missing','Terminal':'Terminal','Klasör':'Folder','Menüden kaldır':'Remove from menu','Favorilere ekle':'Add to favorites','Favorilerden çıkar':'Remove from favorites',
  'Bu aramada uygulama bulunamadı.':'No apps match your search.','Çantana araç eklediğinde burada görünür.':'Apps you add to this workspace will appear here.',
  'Kod yaz, projelerini düzenle':'Write code and organize projects','Hızlı metin ve kod düzenleme':'Quick text and code editing','PDF ve e-kitap oku':'Read PDFs and e-books','Dosyaları ve klasörleri karşılaştır':'Compare files and folders','Kendi parolanla bir parola kasası oluştur':'Create a password-protected vault','Video ve ses dosyalarını oynat':'Play video and audio','Ekran ve video kaydı':'Record your screen and video','Çizim ve görsel düzenleme':'Draw and edit images','3B modelleme ve animasyon':'3D modeling and animation','SQLite veritabanlarını görsel olarak düzenle':'Browse and edit SQLite databases','Belge, tablo ve sunum hazırla':'Create documents, spreadsheets and presentations',
  'Projelerim':'My projects','Bilgisayarından alınan proje kopyaları':'Project copies from your computer','Tasarım dosyaları':'Design files','Marka, görsel ve medya dosyaları':'Brand assets, images and media','Başlangıç projeleri':'Starter projects','Hazırlanmış web ve Python örnekleri':'Ready-made web and Python examples','Orijinal kurulum ve dağıtım paketleri':'Original installers and distribution packages','Kurtarma araçları':'Recovery tools','Kurtarma ISO ve USB hazırlama paketi':'Recovery images and USB preparation tools','Bilgi bankası':'Knowledge files','Çevrimdışı belgeler ve rehberler':'Offline documents and guides','Python belgeleri':'Python documentation','Python kılavuzunu çevrimdışı oku':'Read the Python manual offline','SQLite belgeleri':'SQLite documentation','Veritabanı belgelerini çevrimdışı oku':'Read database documentation offline','İşletim sistemi arşivi':'Operating system archive','Windows ve Ubuntu medyaları':'Windows and Ubuntu installation media','Geliştirme ortamı':'Development environment','Python, Node.js, Git ve diğer araçlar hazır':'Python, Node.js, Git and other available tools',
  'Çevrimdışı yerel model veya kendi anahtarınla bir API servisi.':'Chat offline with a local model or connect an API with your own key.','Sohbeti temizle':'Clear chat','Yerel mod · Mesajlar bu bilgisayarda işlenir.':'Local mode · Messages are processed on this computer.','Yerel mod · Mesajlar ve belge alıntıları bu bilgisayarda işlenir.':'Local mode · Messages and document excerpts are processed on this computer.',
  'Yeni sohbet':'New conversation','Bir fikri geliştir, bir metin hazırla':'Explore an idea, draft some text','veya yerel belgelerin hakkında soru sor.':'or ask about your local documents.','Çalışma planı hazırla':'Draft a work plan','Belgelerde bir bilgi bul':'Find information in documents','Asistana mesaj':'Message the assistant','Bir soru yaz…':'Write a message…','Belgelerime dayan':'Use my documents','Gönder ↑':'Send ↑',
  'Yanıtlar kontrol gerektirir. Belge modu ilgili alıntıları getirir; tüm dosyaları bildiğini varsaymaz. Sohbet geçmişi sayfa yenilenince silinir.':'Check important answers. Document mode retrieves relevant excerpts, not every file. Conversation history is cleared when this page reloads.',
  'ASİSTAN BAĞLANTISI':'MODEL CONNECTION','Model ve bağlantı':'Model & connection','Sağlayıcı':'Provider','Bu bilgisayar · Çevrimdışı':'This computer · Offline','Sohbet modeli':'Chat model','Gemma E2B bu çantada hız ve bellek için başlangıç seçeneği. E4B daha fazla kaynak ister.':'Gemma E2B is the starting option for lower memory use. E4B requires more resources.','Model kimliği':'Model ID','Listeden seç veya model kimliğini yaz':'Choose or enter a model ID','API bağlantısını düzenle':'Edit API connection','Modelleri getir':'List models','Bağlantıyı dene':'Test connection',
  'Bağlantı testi kısa bir istek gönderir; ücret/kota tüketebilir. Listedeki her model metin sohbetini desteklemeyebilir.':'Connection tests send a short request and may use credits or quota. Some listed models may not support text chat.','Gerektiğinde başlar':'Starts when needed','Yanıtı / yerel modeli durdur':'Stop response / local model','Bu sürüm metin sohbetini destekler. Yerel ilk yükleme HDD’de birkaç dakika sürebilir. API erişimi, ücret ve kota sağlayıcının koşullarına bağlıdır.':'This version supports text chat. Loading a local model from an HDD can take a few minutes. API access, pricing and quotas depend on the provider.',
  'Normal sohbet':'General chat','Belgelerle sohbet':'Document chat','Normal sohbet için belge gerekmez. İstersen belge moduna geç.':'No documents needed for general chat. Switch to document mode when you want to use local sources.','Normal sohbet · Belgeler aranmaz.':'General chat · Documents are not searched.','Belge modu · İlgili yerel alıntılar kullanılır.':'Document mode · Uses relevant local excerpts.',
  'Projeler, belgeler ve rehberlerde çevrimdışı metin araması.':'Offline text search across projects, documents and guides.','Dizini güncelle ↻':'Update index ↻','Belgelerde ara':'Search documents','Bir konu, proje adı veya kelime yaz…':'Enter a topic, project name or keyword…','Ara →':'Search →','Bu soruyu asistana sor ✳':'Ask the assistant →','Bilgin burada. Yukarıdan bir arama başlat.':'Enter a search above to find local information.',
  'Metin, kod, HTML, PDF, DOCX, XLSX ve PPTX dosyaları taranır. Görsel ve taranmış PDF için İş akışları → Metin oku seçeneğini kullan. Eski DOC/XLS/PPT, şifreli dosyalar ve gömülü nesneler desteklenmez. Excel formülleri hesaplanmaz; kayıtlı değerler okunur. Gizli klasörler ve yaygın sır dosyaları tarama dışında tutulur; bu bir sır tarama güvencesi değildir.':'Search supports text, code, HTML, PDF, DOCX, XLSX and PPTX. Use Workflows → Read text for images and scanned PDFs. Legacy DOC/XLS/PPT, encrypted files and embedded objects are not supported. Excel formulas are not evaluated; saved values are read. Hidden folders and common secret files are excluded, but this is not a guarantee that every secret is detected.',
  'Proje klasörünü veya taşınabilir VS Code çalışma alanını aç.':'Open a project folder or a portable VS Code workspace.','Geliştirme terminali ↗':'Development terminal ↗','Projeler 04_PROJELER klasöründen, başlangıç şablonları 03_YAZILIM/Sablonlar klasöründen keşfedilir. Bağımlılık kurulumu ve proje sunucusu otomatik başlatılmaz.':'Projects are discovered in 04_PROJELER and starter templates in 03_YAZILIM/Sablonlar. Dependencies and project servers are not started automatically.','KOD ÇALIŞMA ALANI':'CODE WORKSPACE','KLASÖR':'FOLDER','VS Code’da aç ↗':'Open in VS Code ↗','Klasör ↗':'Folder ↗','04_PROJELER klasörüne bir proje eklediğinde burada görünür.':'Projects added to 04_PROJELER will appear here.','proje':'project','şablon':'template',
  'Kurulum paketleri, işletim sistemleri ve kurtarma medyaları.':'Installers, operating systems and recovery media.','Arşiv klasörü ↗':'Archive folder ↗','Arşivde ara':'Search archive','Paket adı veya kategori ara…':'Search package name or category…','Dosyalar arşivdir; tek tıkla sistem kurulumu yapılmaz. Bir ISO’yu saklamak diski önyüklenebilir yapmaz.':'These are archived files, not one-click system installations. Storing an ISO does not make this drive bootable.','PAKET':'PACKAGE','KATEGORİ':'CATEGORY','BOYUT':'SIZE','DURUM / KAYIT':'STATUS / RECORD','Doğrulama kaydı yok':'No verification record','Eşleşen paket bulunamadı.':'No matching packages.',
  'Doğrulama etiketleri indirme sırasında kaydedilmiş kontrollerdir; bu ekran her açılışta dosyaları yeniden hash’lemez. Ticari yazılımlar kendi lisans ve kullanım koşullarına tabidir.':'Verification labels show checks recorded during download; files are not rehashed each time this page opens. Commercial software is subject to its own licenses and terms.',
  'Cihaz kapasitesi, disk alanı ve yedek durumu.':'Device capacity, disk space and backup status.','İKİNCİ DİSKE KOPYA':'COPY TO A SECOND DRIVE','Mevcut çantanın yedekleme başlatıcısını açar. Tanımlı ayrı fiziksel disk gerekir; sonucu tamamlandığında yenile.':'Opens the existing backup launcher. A configured separate physical drive is required; refresh after the backup completes.','Yedeklemeyi aç ↗':'Open backup ↗','OTURUMU TAMAMLA':'END SESSION','Oturumu kapat':'Close workspace','FieldDesk’i kapatmak yerel modeli durdurur. Açtığın diğer programları kapatıp Windows’ta diski güvenle kaldır.':'Closing FieldDesk stops the local model. Close other running apps, then safely eject the drive in Windows.','FieldDesk’i kapat':'Close FieldDesk','Kişisel kasa klasörü kendiliğinden şifrelenmez. Yüklü programların tüm iş akışları bu ekran tarafından test edilmez.':'The personal vault folder is not automatically encrypted. This screen does not test every workflow in your installed apps.',
  'BU BİLGİSAYAR':'THIS COMPUTER','BELLEK':'MEMORY','ÇANTANIN DİSKİ':'WORKSPACE DRIVE','Son yedek tamamlandı':'Last backup completed','Yedek kaydı yok':'No backup record','İkinci diske fiziksel yedek henüz tamamlanmadı. Tanımlı yedek diskini bağladığında hazır.':'A physical backup to a second drive has not been completed. Connect the configured backup drive when ready.','Henüz başarılı fiziksel yedek kaydı yok. İkinci diskin bağlanması ve tanımlanması gerekiyor.':'No successful physical backup has been recorded. Connect and configure a second drive.',
  'Dosyalarını seç, sonucu önizle, işlemi başlat. Kaynaklar korunur.':'Choose files, preview the result and start the task. Source files are preserved.','Yerel işlem':'Local processing','PDF birleştir':'Merge PDFs','Belgelerini tek dosyada topla.':'Combine documents into one PDF.','Web görselleri':'Web images','Boyutlandır, sıkıştır, dönüştür.':'Resize, compress and convert.','Metin oku · OCR':'Read text · OCR','Taranmış belgelerini aranabilir yap.':'Make scanned documents searchable.','Proje ortamı':'Project environment','Terminalin ve araçların hazır olsun.':'Open your terminal and tools.',
  '01 / GİRDİLER':'01 / INPUTS','02 / ÖNİZLEME VE SONUÇ':'02 / PREVIEW & RESULT','Belgeleri seç':'Choose documents','Görselleri seç':'Choose images','Çalışma alanı seç':'Choose a workspace','Okunacak belgeleri seç':'Choose documents to read','En fazla 30 dosya; dosya başına 50 MB, toplam 150 MB. Sırayı aşağıdan değiştirebilirsin.':'Up to 30 files, 50 MB per file and 150 MB total. You can reorder files below.','Bilgisayardan ekle +':'Add from computer +','Çantadan seç ↗':'Browse workspace ↗','Henüz dosya seçilmedi.':'No files selected.','En fazla genişlik (px)':'Maximum width (px)','Kalite':'Quality','Metnin dili':'Text language','Türkçe + İngilizce':'Turkish + English','Türkçe':'Turkish','İngilizce':'English','Saat yönünde döndür':'Rotate clockwise','Döndürme':'No rotation',
  'En fazla 50 sayfa. PDF sayfaları 300 DPI ile okunur. Düz ve net basılı metinler en iyi sonucu verir; kritik bilgileri kaynağıyla karşılaştır.':'Up to 50 pages. PDFs are read at 300 DPI. Clear, straight printed text works best; compare important information with the source.','Proje veya şablon':'Project or template','VS Code’u da aç':'Also open VS Code','Terminal seçilen klasörde açılır. Bağımlılık yüklenmez ve proje kodu çalıştırılmaz.':'The terminal opens in the selected folder. Dependencies are not installed and project code is not executed.','Sonucu önizle →':'Preview result →','İşlem önizlemesi':'Task preview','Dosyalarını eklediğinde sayfa sayısı, çıktı boyutları ve işlem adımları burada görünür.':'Add files to see page counts, output sizes and processing steps here.','Onayla ve işlemi başlat →':'Confirm and start →','OCR işlemini iptal et':'Cancel OCR','Sonuçları Bilgi merkezine ekle ↗':'Add results to library ↗','Çıktı klasörünü aç ↗':'Open output folder ↗',
  'Çıktılar çantanın 12_ISLER/Ciktilar klasöründe ayrı bir işlem klasörüne yazılır. Bilgisayardan eklediğin girdilerin kopyaları 12_ISLER/Girdiler içinde kalır.':'Outputs are written to a separate task folder in 12_ISLER/Ciktilar. Copies of inputs added from your computer remain in 12_ISLER/Girdiler.','Dosyalarını seç ve sonucu önizle.':'Choose your files and preview the result.','Çıktılar ayrı bir klasöre yazılır. Kaynak dosyalar değişmez.':'Outputs go to a separate folder. Source files are unchanged.','TAMAMLANDI ✓':'COMPLETED ✓','İPTAL EDİLDİ':'CANCELLED','TAMAMLANAMADI':'FAILED','Okunan metin':'Extracted text','Doğrulama ve işlem ayrıntıları islem-raporu.json dosyasında.':'Verification and task details are in islem-raporu.json.','Bu işlem başarılı sonuç olarak kaydedilmedi. Kaynak dosyalar korundu.':'This task was not recorded as successful. Source files were preserved.',
  'Çantanın klasörünü seç. Araçlarını, bağımlılıklarını ve eksikleri birlikte kontrol edelim.':'Choose a workspace folder to check tools, dependencies and missing components.','KONTROL BEKLİYOR':'NOT CHECKED','HAZIRLIK TAMAMLANDI':'SETUP COMPLETE','İLK AÇILIŞ':'FIRST RUN','Örneğin E:\\ATOLYE':'For example E:\\FieldDesk','Klasör seç ↗':'Choose folder ↗','Kontrol et →':'Check →','Mevcut dosyalar korunur. Hazırlık yalnızca eksik çalışma klasörlerini oluşturur; uygulama veya model indirmez.':'Existing files are preserved. Setup creates missing workspace folders only; it does not download apps or models.','Çanta klasörünü kontrol ederek başla.':'Check your workspace folder to get started.','Bu çalışma alanını hazırla ✓':'Set up this workspace ✓','Windows x64 · Yerel çalışma alanı':'Windows x64 · Local workspace','FieldDesk · Yerel çalışma merkezi':'FieldDesk · Portable workspace',
  'KENDİ ARAÇLARIN':'YOUR TOOLS','Uygulama adı':'App name','Örneğin: GIMP':'For example: GIMP','Çanta içindeki .exe dosyası':'Executable inside the workspace','01_TASINABILIR/Uygulamam/program.exe':'01_TASINABILIR/MyApp/program.exe','Dosya seç ↗':'Choose file ↗','Kısa açıklama':'Short description','Bu araç ne işe yarıyor?':'What does this tool do?','Kategori':'Category','Taşınabilir program klasörünü çantana koy, ardından .exe dosyasını seç. Bu işlem programı kopyalamaz veya çalıştırmaz. Taşınabilirlik uygulamanın kendi desteğine bağlıdır.':'Place the portable app folder in your workspace, then choose its .exe. This does not copy or run the app. Portability depends on the app itself.','Menüye ekle +':'Add to menu +','ÇANTANIN İÇİNDE':'WORKSPACE FILES','Dosya seç':'Choose files','Kapat':'Close','↑ Üst klasör':'↑ Parent folder','Seçimi tamamla ✓':'Done ✓','Çanta kökü':'Workspace root','Bu klasörde uygun dosya bulunamadı.':'No compatible files in this folder.',
  'Göndermeden önce kontrol et.':'Review before sending','Gönderimi iptal et':'Cancel sending','Sorun':'Your question','Gönderilecek alıntılar':'Excerpts to send','Alıntılardaki kişisel veya gizli bilgileri kontrol et. Bu istek önceki sohbet geçmişini içermez. Sağlayıcının veri işleme koşulları uygulanır.':'Check excerpts for personal or confidential information. This request does not include previous conversation history. The provider’s data processing terms apply.','Bu soru ve alıntıları gönder →':'Send this question and excerpts →','Vazgeç':'Cancel',
  'KENDİ ANAHTARINLA BAĞLAN':'CONNECT YOUR OWN API KEY','API bağlantısı':'API connection','API ayarlarını kapat':'Close API settings','FieldDesk anahtar sağlamaz. Sağlayıcı hesabının erişimi, ücretleri ve veri işleme koşulları geçerlidir.':'FieldDesk does not provide API keys. Your provider’s access, pricing and data processing terms apply.','API temel adresi':'API base URL','https://sunucu.example/v1':'https://server.example/v1','Protokol':'Protocol','Chat Completions uyumlu':'Chat Completions compatible','Anthropic Messages uyumlu':'Anthropic Messages compatible','Ollama / LM Studio gibi bu bilgisayardaki uyumlu sunucular için http://127.0.0.1:PORT/v1 kullanılabilir; anahtar zorunlu değildir. Sunucuyu ayrıca başlatmalısın.':'For compatible local servers such as Ollama or LM Studio, use http://127.0.0.1:PORT/v1; an API key is optional. Start the server separately.','Kendi API anahtarın':'Your API key','Anahtarını buraya gir':'Enter your API key','Bu Windows hesabında şifreli hatırla':'Remember encrypted for this Windows account','Varsayılan: yalnızca açık oturum. Şifreli kayıt başka bilgisayara/hesaba taşınmaz. Anahtar sohbetlere ve dağıtım paketine eklenmez.':'Default: current session only. Encrypted credentials cannot move to another computer or account. Keys are not added to conversations or release packages.','Bağlantıyı kaydet':'Save connection','Anahtarı unut':'Forget key','Anahtar oluştur ↗':'Get an API key ↗','Özel / OpenAI uyumlu':'Custom / OpenAI compatible','Yeni anahtar veya boş bırakarak mevcut anahtar':'Enter a new key or leave blank to keep the current key','API bağlantısı seçildi':'API connection selected','Windows hesabına bağlı şifreli kayıt.':'Encrypted for this Windows account.','Oturumluk bağlantı kaydedildi.':'Connection saved for this session.','Canlı erişim için bağlantıyı dene.':'Test the connection to check access.','Henüz bağlantı kaydedilmedi.':'No connection saved yet.','Servis yanıtı bekleniyor…':'Waiting for the service…',
  'WINDOWS X64 · RESMÎ KAYNAKLAR':'WINDOWS X64 · OFFICIAL SOURCES','Programları seçip topluca indirebilirsin. Taşınabilir olanlar otomatik hazırlanır.':'Select programs to download together. Portable apps are prepared automatically.','Paket merkezini kapat':'Close app catalog','Program kataloğunda ara':'Search app catalog','Program veya yapacağın işi ara…':'Search programs or tasks…','Katalog kategorisi':'Catalog category','Hızlı seçim:':'Quick selection:','Günlük araçlar':'Everyday tools','Kod yazıyorum':'Development','İçerik üretiyorum':'Creative tools','Görünenleri seç':'Select visible','Seçimi temizle':'Clear selection','Kurulum dosyaları yalnızca indirilir; otomatik çalıştırılmaz.':'Installers are downloaded only; they are not run automatically.','Güncellemeleri kontrol et':'Check for updates','Sürüm kontrolü sonucu':'Version check results','Henüz sürüm kontrolü yapılmadı.':'Versions have not been checked yet.','İndirme ve yönetim hakkında':'About downloads and management',
  'Kesilen indirmeyi yeniden seçerek sürdürebilirsin. Kaldırma yalnızca yönetilen paketlerde çalışır; dosyalar geri almak için saklanır, disk alanı boşaltılmaz. Profil verileri korunur. Sürüm kontrolü 24 pakette otomatik, 6 pakette yayıncı sayfası üzerinden yapılır; yeni sürüm kendiliğinden kurulmaz. İlk açılışta lisans, ağ veya ek çalışma zamanı gerekebilir. Kurulum dosyaları otomatik çalıştırılmaz.':'Reselect interrupted downloads to resume. Removal works only for managed packages; files are retained for undo, so disk space is not freed. Profile data is preserved. Version checks are automatic for 24 packages; 6 require the publisher page. New versions are not installed automatically. First launch may require a license, network access or additional runtime. Installers are not run automatically.',
  'Geri alınabilir kaldırılanlar':'Removed apps · undo available','İndirme boyutu: 0 MB':'Download size: 0 MB','İndirmeyi iptal et':'Cancel download','Seçilenleri indir ve hazırla ↓':'Download & prepare selected ↓','Kurulum dosyası':'Installer only','Otomatik hazırlanır':'Prepared automatically','İndirilebilir':'Available to download','Çantada mevcut · sürüm bilinmiyor':'Already on drive · version unknown','Kurulum dosyası hazır':'Installer ready','Sürüm ve ayrıntılar':'Version & details','Klasörü aç':'Open folder','Kaldır · geri alınabilir':'Remove · undo available','Devam et':'Resume','Yeniden dene':'Retry','Resmî kaynak ↗':'Official source ↗','Yayıncı ↗':'Publisher ↗','Katalog sürümü:':'Catalog version:','SHA-256:':'SHA-256:','katalogda sabitlenmiş özet':'hash pinned in catalog','yayıncı / release özeti':'publisher / release hash','Bu aramada program bulunamadı.':'No programs match your search.','Geri al':'Undo','Programlar yükleniyor…':'Loading programs…','Sırada':'Queued','İndiriliyor':'Downloading','Doğrulanıyor':'Verifying','Hazırlanıyor':'Preparing','İşlem tamamlanamadı':'Task failed','Yarım kalmış · devam edilebilir':'Partial download · resumable','Yeni sürüm var':'Update available',
  'Kod düzenleyici':'Code editor','PDF ve e-kitap okuyucu':'PDF and e-book reader','Dosya ve klasör karşılaştırma':'File and folder comparison','Parola kasası':'Password vault','Video ve ses oynatıcı':'Video and audio player','Ekran kaydı ve yayın':'Screen recording and streaming','Veritabanı düzenleyici':'Database editor','JavaScript çalışma ortamı':'JavaScript runtime','Python ortam ve paket yönetimi':'Python environment and package management','Dosyalarda hızlı metin arama':'Fast text search in files','JSON işleme':'JSON processing','SQLite araçları':'SQLite tools','SQLite komut satırı araçları':'SQLite command-line tools','Otomasyon ve komut satırı':'Automation and command line','C# ve .NET geliştirme':'C# and .NET development','Yerel model çalıştırıcı':'Local model runtime','Arşiv sıkıştırma ve açma':'Archive compression and extraction','Belge, hesap tablosu ve sunum':'Documents, spreadsheets and presentations','Python geliştirme kurulumu':'Python development installer','Sürüm kontrolü kurulumu':'Version control installer','Ekran görüntüsü ve kayıt':'Screenshots and recording','Yakındaki cihazlarla dosya paylaş':'Share files with nearby devices','Taşınabilir arşiv yöneticisi':'Portable archive manager','Video dönüştürme':'Video conversion','GIF ve ekran kaydı':'GIF and screen recording','Açık kaynak kod düzenleyici':'Open-source code editor','Ses kaydı ve düzenleme':'Audio recording and editing','Sistem bilgisi komut satırı aracı':'Command-line system information',
  '.NET Desktop Runtime ayrıca gerekebilir.':'.NET Desktop Runtime may be required separately.','Kurulum sihirbazını kullanıcı ayrıca çalıştırır.':'Run the installer separately.','Katalog sürümü yayıncıyla eşleşiyor.':'Catalog version matches the publisher.','Yeni sürüm otomatik indirilmez; katalog incelemesi gerekir.':'New versions are not downloaded automatically; the catalog must be reviewed.',
  'PDF İŞ AKIŞI':'PDF WORKFLOW','GÖRSEL İŞ AKIŞI':'IMAGE WORKFLOW','METİN OKUMA · OCR':'TEXT EXTRACTION · OCR','ÇALIŞMA ALANI':'WORKSPACE','Hazır ✓':'Ready ✓','Paket eksik':'Package missing','Motor eksik':'Engine missing','Yazılabilir ✓':'Writable ✓','Yazma izni yok':'Not writable','Taşınabilir araçlar':'Portable tools','Eklenmemiş':'Not added','Çanta klasörleri':'Workspace folders','Var ✓':'Exists ✓','Oluşturulacak +':'Will be created +','Kontrol tamamlandı.':'Check complete.',
  'Bu araçlar ilgili uygulama, proje veya asistan özelliği için kullanılır. PDF ve görsel işlemleri yukarıdaki paketlerle çalışır.':'These tools support app, project or assistant features. PDF and image workflows use the packages listed above.',
  'İşlem tamamlanamadı.':'The task could not be completed.','Durum yenilendi.':'Status refreshed.','Sohbet temizlendi.':'Conversation cleared.','Durduruldu':'Stopped','Yanıt hatası':'Response error','Yerel dosyalarda aranıyor…':'Searching local files…','Eşleşme bulunamadı. Daha belirgin bir kelimeyle tekrar ara.':'No matches. Try a more specific keyword.','Dosyayı aç ↗':'Open file ↗','Önce bir soru veya konu yaz.':'Enter a question or topic first.','Önce devam eden işlemin tamamlanmasını bekle.':'Wait for the current task to finish.','Önce devam eden işlemi bekle.':'Wait for the current task.','En fazla 30 dosya; dosya başına 50 MB, toplam 150 MB seç.':'Select up to 30 files, 50 MB per file and 150 MB total.','Dosyalar eklendi. Önizlemeye geçebilirsin.':'Files added. You can now preview the result.','Girdiler okunuyor ve kontrol ediliyor…':'Reading and checking inputs…','Önizleme hazır. Onayladığında işlem başlar.':'Preview ready. Confirm to start the task.',
  'Yerel bağlantı kesildi. FieldDesk’i yeniden açabilirsin.':'Local connection lost. Reopen FieldDesk.','Yerel bağlantı kesildi. İşlem durumunu yeniden açarak kontrol et.':'Local connection lost. Reopen the workspace to check the task status.','Yerel model yükleniyor. HDD’den ilk açılış birkaç dakika sürebilir.':'Loading local model. First launch from an HDD can take a few minutes.','Seçilen API servisine bağlanılıyor.':'Connecting to the selected API service.','Yanıt bu bilgisayarda üretiliyor.':'Generating a response on this computer.','Yanıt seçilen API servisinden bekleniyor.':'Waiting for a response from the API service.','Yanıt hazır.':'Response ready.','Yanıt hazır. Çıktı sınırına ulaşıldı; yanıt kesilmiş olabilir.':'Response ready. Output limit reached; the answer may be incomplete.','Model boş yanıt döndürdü. Yeniden dene veya başka bir model seç.':'The model returned an empty response. Retry or choose another model.','Model yükleme süresi aşıldı.':'Model loading timed out.','Model açılamadı. Yapay zekâ kaydını kontrol et.':'Could not start the model. Check the AI log.','Bu soruyla eşleşen yerel belge bulunamadı. Daha belirgin bir konu adıyla ara.':'No local documents match this question. Try a more specific topic.','Belge bulunamadı; model başlatılmadı.':'No matching documents; the model was not started.','Önce devam eden yanıtı tamamla veya durdur.':'Finish or stop the current response first.','1–2000 karakter uzunluğunda bir soru yaz.':'Enter a message between 1 and 2,000 characters.','Bilinmeyen model.':'Unknown model.','Bilinmeyen sağlayıcı.':'Unknown provider.','Hatalı sohbet geçmişi.':'Invalid conversation history.','Model indirmesi henüz tamamlanmadı.':'The model download has not finished.','Eşleşen belge bulunamadı; hiçbir belge gönderilmedi.':'No matching documents; nothing was sent.','Buluta belge göndermeden önce alıntıları önizleyip onayla.':'Review and approve excerpts before sending documents to a cloud provider.','API yanıtı işlenemedi. Bağlantı ve model uyumunu kontrol et.':'Could not process the API response. Check the connection and model compatibility.',
  'Soru ve aşağıdaki alıntılar gönderilecek. Dosya adları, yolları ve dosyanın tamamı gönderilmez. Beş dakika geçerli, tek kullanımlık onay.':'Your question and the excerpts below will be sent. File names, paths and full files are excluded. This one-time approval expires in five minutes.',
  'GETİRİLEN YEREL KAYNAKLAR · ALINTILARI KONTROL ET':'RETRIEVED LOCAL SOURCES · CHECK THE EXCERPTS','SEN':'YOU','YEREL ASİSTAN':'LOCAL ASSISTANT','FieldDesk kapatılıyor. Açık programlarını kapattıktan sonra diski güvenle çıkar.':'Closing FieldDesk. Close other running programs before safely ejecting the drive.'
};

Object.assign(EN, {
  "Kullanmaya hazır": "Ready to use",
  "Arşivde": "Archived",
  "Dosya bulunamadı": "File not found",
  "Proje": "Project",
  "Şablon": "Template",
  "SQLite araçları": "SQLite tools",
  "Çalışma alanın hazır. Mevcut dosyalar korundu.": "Your workspace is ready. Existing files were preserved.",
  "Desteklenmeyen arayüz dili.": "Unsupported interface language.",
  "API adresine bağlanılamadı.": "Could not connect to the API address.",
  "API bağlantısı tamamlanamadı. İnternet, TLS, adres ve zaman aşımını kontrol et.": "The API connection failed. Check your internet connection, TLS, address and timeout.",
  "API hedefi özel, bağlantı yerel veya ayrılmış ağ adresi olamaz.": "The API destination cannot be a private, link-local or reserved network address.",
  "API portu geçersiz.": "Invalid API port.",
  "API temel adresi geçersiz; kullanıcı adı, sorgu ve parça içeremez.": "Invalid API base address; usernames, queries and fragments are not allowed.",
  "API yanıt biçimi desteklenmiyor.": "Unsupported API response format.",
  "API yanıtı boyut sınırını aştı.": "The API response exceeded the size limit.",
  "Ad 1–60, açıklama en fazla 200, kategori en fazla 30 karakter olmalı.": "Use 1–60 characters for the name, up to 200 for the description and 30 for the category.",
  "Adres değişince anahtarı yeniden gir; önceki anahtar başka sunucuya taşınmaz.": "Enter the key again after changing the address; existing keys are not transferred to another server.",
  "Anahtar biçimi geçersiz.": "Invalid key format.",
  "Bu sağlayıcı için kendi API anahtarını gir.": "Enter your own API key for this provider.",
  "Bağlantı kaydedildi. Henüz sağlayıcıya istek gönderilmedi.": "Connection saved. No request has been sent to the provider yet.",
  "Bağlantı ve kayıtlı anahtar unutuldu.": "Connection and saved key removed.",
  "Hesabın bu kaynağa erişimi yok.": "Your account cannot access this resource.",
  "Hesabın döndürdüğü modeller listelendi; hepsi metin sohbetini desteklemeyebilir. Liste ilk sayfayla sınırlı olabilir.": "Models returned by your account are listed; some may not support text chat. The list may be limited to the first page.",
  "Kota veya hız sınırı aşıldı. Sağlayıcı hesabını kontrol et.": "Quota or rate limit exceeded. Check your provider account.",
  "Metin sohbeti için geçerli model kimliğini seç veya yaz.": "Choose or enter a valid text chat model ID.",
  "Metin yanıtı alındı; bağlantı çalışıyor.": "Text response received; the connection works.",
  "Model kimliği geçersiz.": "Invalid model ID.",
  "Model metin yanıtı vermedi. Modelin sohbet uyumunu ve çıktı sınırını kontrol et.": "The model returned no text. Check chat compatibility and the output limit.",
  "Model veya API uç noktası bulunamadı.": "Model or API endpoint not found.",
  "Önce sağlayıcı bağlantısını kaydet.": "Save the provider connection first.",
  "Yanıt durduruldu.": "Response stopped.",
  "Yanıt durduruldu; yerel model varsa kapatılıyor. Gönderilmiş API isteğinin sağlayıcıdaki işlemi ve ücreti geri alınamaz; bağlantı kapanana kadar beklemek gerekebilir.": "Response stopped; any local model is shutting down. Processing and charges for an API request already sent cannot be undone; you may need to wait for the connection to close.",
  "Şifreli bağlantılar açılamadı. Windows hesabı veya bilgisayar değişmiş olabilir; anahtarları yeniden gir.": "Encrypted connections could not be opened. Your Windows account or computer may have changed; enter the keys again.",
  "Şifreli kayıt fazla büyük.": "The encrypted record is too large.",
  "Şifreli kayıt için Windows gerekir. Oturumluk kullanabilirsin.": "Encrypted storage requires Windows. You can use a session-only connection.",
  "Windows şifreli kaydı açılamadı. Bu bilgisayardaki Windows hesabında anahtarı yeniden gir.": "The Windows encrypted record could not be opened. Enter the key again in this computer’s Windows account.",
  "[API anahtarı gizlendi]": "[API key hidden]",
  "Kaldığı yerden indiriliyor…": "Resuming download…",
  "Mevcut arşiv doğrulanıyor…": "Verifying existing archive…",
  "SHA-256 doğrulanıyor…": "Verifying SHA-256…",
  "Arşiv açılıyor ve menü hazırlanıyor…": "Extracting archive and preparing the menu…",
  "Doğrulandı, hazırlandı ve menüye eklendi.": "Verified, prepared and added to the menu.",
  "Kurulum dosyası indirildi; otomatik çalıştırılmadı.": "Installer downloaded; it was not run automatically.",
  "Seçilen paketler hazırlanıyor.": "Preparing selected packages.",
  "Seçilen paketler hazır. Mevcut olanlar korundu.": "Selected packages are ready. Existing copies were preserved.",
  "Kuyruk iptal edildi. Tamamlanmış paketler korundu.": "Queue cancelled. Completed packages were preserved.",
  "Yarım kaldı · devam edilebilir": "Incomplete · can resume",
  "İndirilmedi.": "Not downloaded.",
  "İndirme eksik; yeniden seçerek kaldığı yerden devam edebilirsin.": "Download incomplete; select it again to resume.",
  "İndirme kesildi. Yarım dosya korundu; yeniden seçerek devam edebilirsin.": "Download interrupted. The partial file was preserved; select it again to resume.",
  "İptal ediliyor. Bekleyen ağ okuması en fazla 30 saniye sürebilir.": "Cancelling. A pending network read may take up to 30 seconds.",
  "İndirme kuyruğu iptal ediliyor.": "Cancelling the download queue.",
  "Paket geri alındı ve menüye eklendi.": "Package restored and added to the menu.",
  "Paket menüden kaldırıldı. Dosyalar geri almak için saklandı; disk alanı henüz boşaltılmadı.": "Package removed from the menu. Files are kept for undo; disk space has not been freed.",
  "Önce bu uygulamanın açık penceresini kapat.": "Close the application’s open window first.",
  "Paket kaldırılamadı; açık programı kapatıp yeniden dene.": "Could not remove the package; close the program and retry.",
  "Yayıncı sürümleri kontrol ediliyor…": "Checking publisher versions…",
  "Yeni yayıncı sürümü var · katalog güncellemesi gerekiyor.": "New publisher version available · catalog update required.",
  "Yayıncı sayfasından kontrol et; otomatik sürüm kontrolü yok.": "Check the publisher’s page; automatic version checks are unavailable.",
  "Kontrol edilemedi · internet veya yayıncı API kotası. Güncel olduğu varsayılmadı.": "Could not check · internet connection or publisher API quota. This does not confirm the package is up to date.",
  "Yayıncının latest kanalı katalogdan daha eski; indirme değiştirilmedi.": "The publisher’s latest channel is older than the catalog; the download was not changed.",
  "İndirme için yeterli boş disk alanı yok.": "Not enough free disk space for the download.",
  "SHA-256 eşleşmedi; bozuk indirme silindi, paket hazırlanmadı.": "SHA-256 mismatch; the corrupt download was deleted and the package was not prepared.",
  "Yayıncı dosyasının boyutu katalogla eşleşmiyor.": "The publisher file size does not match the catalog.",
  "PDF birleştirme": "Merge PDFs",
  "Çevrimdışı metin okuma": "Offline text extraction",
  "1–30 dosya seç.": "Select 1–30 files.",
  "Aynı dosyayı iki kez ekleme.": "Do not add the same file twice.",
  "Dosya sınırı: dosya başına 50 MB, toplam 150 MB.": "File limit: 50 MB per file, 150 MB total.",
  "Listeden bir proje seç.": "Choose a project from the list.",
  "Bir iş akışı zaten çalışıyor.": "A workflow is already running.",
  "Bir kaynak dosya önizlemeden sonra değişti. Yeniden önizle.": "A source file changed after the preview. Preview again.",
  "Önizleme süresi doldu. Yeniden önizle.": "The preview expired. Preview again.",
  "İşlem tamamlandı. Kaynak dosyalar korundu.": "Task completed. Source files were preserved.",
  "Küçük görseller büyütülmez. EXIF/konum bilgileri çıktıya aktarılmaz.": "Small images are not enlarged. EXIF and location metadata are excluded from output.",
  "Şeffaf alanlar JPEG çıktısında beyaz olur.": "Transparent areas become white in JPEG output.",
  "Sıra aşağıdaki dosya sırasıdır. Yer işaretleri ve etkileşimli formlar korunmayabilir.": "Files are processed in the order below. Bookmarks and interactive forms may not be preserved.",
  "Çıktı PDF sayfaları yeniden görüntülenir; bağlantılar, formlar ve özgün PDF yapısı korunmaz.": "Output PDF pages are rendered again; links, forms and the original PDF structure are not preserved.",
  "OCR hata yapabilir; isimleri, rakamları ve kritik bilgileri kaynakla karşılaştır.": "OCR can make mistakes; compare names, numbers and important information with the source.",
  "El yazısı ve karmaşık tablolar için doğruluk güvencesi verilmez. Sonuçları Bilgi merkezine ekleyebilirsin.": "Handwriting and complex tables may be inaccurate. You can add results to the library.",
  "OCR için toplam en fazla 50 sayfa seç.": "Select up to 50 pages total for OCR.",
  "VS Code bulunamadı; yalnızca terminal seçeneğini kullanabilirsin.": "VS Code was not found; you can use the terminal option.",
  "Bağımlılık kurulumu ve proje kodu çalıştırılmaz. Terminal seçilen klasörde açılır.": "Dependencies and project code are not run. The terminal opens in the selected folder.",
  "İptal isteniyor; çalışan OCR sayfası durdurulacak.": "Cancellation requested; the current OCR page will be stopped.",
  "İptal edilebilecek bir OCR işlemi yok.": "There is no OCR task to cancel.",
  "Eksik klasörler oluşturulur; mevcut dosyalar korunur. Program veya model indirilmez.": "Missing folders will be created; existing files are preserved. No programs or models are downloaded.",
  "Bu bilgisayarda tam bir klasör yolu seç.": "Choose an absolute folder path on this computer.",
  "Sürücü kökü yerine var olan bir çanta klasörü seç.": "Choose an existing workspace folder instead of the drive root.",
  "Çantanın klasörünü belirt.": "Enter the workspace folder.",
  "Klasör penceresi açılamadı. Klasör yolunu alana yazabilirsin.": "The folder picker could not open. You can enter the folder path in the field.",
  "Klasör seçme penceresi zaten açık.": "The folder picker is already open.",
  "Uygulama menüye eklendi.": "Application added to the menu.",
  "Menü kaydı kaldırıldı. Uygulama dosyası korundu.": "Menu entry removed. The application file was preserved.",
  "Çanta içindeki bir .exe dosyasını seç.": "Choose an .exe file inside the workspace.",
  "Uygulama dosyası bulunamadı.": "Application file not found.",
  "Dosya dizini güncelleniyor.": "Updating the file index.",
  "Yedekleme penceresi açıldı. Tanımlı ikinci fiziksel disk gerekir; sonucu bu ekrandan yenileyebilirsin.": "Backup window opened. A configured second physical drive is required; refresh this screen to check the result."
});

Object.assign(EN, {
  "Arşiv": "Archive",
  "İşletim sistemi": "Operating system",
  "Git kurulum paketi": "Git installer",
  "uv — Python ortam yöneticisi": "uv — Python environment manager",
  "ripgrep — dosyalarda arama": "ripgrep — file search",
  "jq — JSON işleme": "jq — JSON processor",
  "WinMerge — dosya karşılaştırma": "WinMerge — file comparison",
  "KeePassXC — parola kasası aracı": "KeePassXC — password vault",
  "OBS Studio — ekran kaydı": "OBS Studio — screen recording",
  "Ventoy — USB hazırlama paketi": "Ventoy — USB preparation toolkit",
  "Node.js LTS kurulum paketi": "Node.js LTS installer",
  "7-Zip kurulum paketi": "7-Zip installer",
  "7-Zip taşınabilir konsol": "7-Zip portable console",
  "7-Zip açma yardımcısı": "7-Zip extraction helper",
  "SumatraPDF — PDF/EPUB okuyucu": "SumatraPDF — PDF/EPUB reader",
  "VLC — medya oynatıcı": "VLC — media player",
  "LibreOffice — ofis kurulum paketi": "LibreOffice — office installer",
  "Python 3.13 kurulum paketi": "Python 3.13 installer",
  "Python bağımsız çalıştırıcı": "Python standalone runtime",
  "Blender — 3B tasarım": "Blender — 3D design",
  "Krita — çizim ve görsel düzenleme": "Krita — drawing and image editing",
  "SystemRescue — kurtarma ISO": "SystemRescue — recovery ISO",
  "Qwen3 4B — çevrimdışı yapay zekâ": "Qwen3 4B — offline AI",
  "llama.cpp — yerel model çalıştırıcı": "llama.cpp — local model runtime",
  "Python — tam çevrimdışı belgeler": "Python — complete offline documentation",
  ".NET SDK — C# geliştirme": ".NET SDK — C# development",
  "SQLite — veritabanı araçları": "SQLite — database tools",
  "SQLite — çevrimdışı belgeler": "SQLite — offline documentation",
  "PowerShell — taşınabilir otomasyon": "PowerShell — portable automation",
  "Node.js — çevrimdışı API belgesi": "Node.js — offline API documentation",
  "Microsoft Visual C++ x64 çalışma zamanı": "Microsoft Visual C++ x64 runtime",
  "Resmi güncel x64": "Official current x64",
  "Acronis True Image — resmî deneme kurulum paketi": "Acronis True Image — official trial installer",
  "Resmî güncel deneme": "Official current trial",
  "Google Gemma 4 E2B — görsel/ses projektörü": "Google Gemma 4 E2B — vision/audio projector",
  "Windows 11 x64 — Türkçe Home/Pro çok sürümlü ISO": "Windows 11 x64 — Turkish Home/Pro multi-edition ISO",
  "Windows 10 — resmî medya oluşturma aracı": "Windows 10 — official Media Creation Tool",
  "7-Zip — tam kurulum ve taşınabilir RAR açma motoru": "7-Zip — full installer and portable RAR extraction engine",
  "Sergei Strelec WinPE 11/10 — doğrulanmış ISO": "Sergei Strelec WinPE 11/10 — verified ISO",
  "Tesseract OCR · Türkçe/İngilizce hazır": "Tesseract OCR · Turkish/English ready",
  "Dosyalar arşivdir; tek tıkla sistem kurulumu yapılmaz. Bir ISO’yu saklamak diski önyüklenebilir yapmaz.": "These files are an archive; operating systems are not installed with one click. Storing an ISO does not make the drive bootable.",
  "Windows 10 için medya oluşturma aracı var, ISO henüz yok.": "The Windows 10 Media Creation Tool is available; the ISO is not yet present.",
  "Acronis paketi denemedir.": "The Acronis package is a trial."
});

function translateUI(text,language='en') {
  if(language!=='en'||typeof text!=='string')return text;
  const trimmed=text.trim(), translated=EN[trimmed];
  if(translated!==undefined)return text.replace(trimmed,translated);
  // Composite UI messages contain numbers, dates, file names or vendor names.
  const rules=[
    [/^(Dosyalar arşivdir;.+?yapmaz\.)( Windows 10.+?yok\.)?( Acronis.+?denemedir\.)?$/,(_,a,b,c)=>[a,b,c].filter(Boolean).map(x=>translateUI(x.trim(),'en')).join(' ')],
    [/^Kuyruk tamamlandı\. (\d+) paket hazırlanamadı\.$/,(_,n)=>`Queue completed. ${n} packages could not be prepared.`],
    [/^(\d[\d.,]*) öğe( · filtrelenmiş)?$/,(_,n,f)=>`${n} ${n==='1'?'item':'items'}${f?' · filtered':''}`],
    [/^(\d[\d.,]*) GB paket ve model arşivi$/,(_,n)=>`${n} GB of packages and models`],
    [/^(\d[\d.,]*) dosya · (\d[\d.,]*) metin bölümü$/,(_,n,c)=>`${n} files · ${c} text sections`],
    [/^Dizin güncelleniyor · (.+) dosya tarandı$/,(_,n)=>`Updating index · ${n} files scanned`],
    [/^(\d+) belge okunamadı · Listeyi göster$/,(_,n)=>`${n} documents could not be read · Show list`],
    [/^(\d+) program seçildi(?: · Katalog: (\d+))?$/,(_,n,total)=>`${n} ${n==='1'?'program':'programs'} selected${total?' · Catalog: '+total:''}`],
    [/^Kalan indirme: (.+) · Açılmış dosyalar ayrıca yer kaplar$/,(_,n)=>`Remaining download: ${n} · Extracted files need additional space`],
    [/^(.+) indirildi · sunucu desteklerse devam edilir$/,(_,n)=>`${n} downloaded · resumes if supported by the server`],
    [/^Geri alınabilir kaldırılanlar \((\d+)\)$/,(_,n)=>`Removed apps · undo available (${n})`],
    [/^(\d+)\/(\d+) paket işlendi$/,(_,a,b)=>`${a}/${b} packages processed`],
    [/^(\d+)\/(\d+) dosya çantaya kopyalanıyor…$/,(_,a,b)=>`Copying file ${a}/${b} to the workspace…`],
    [/^(\d+) sayfa$/,(_,n)=>`${n} pages`],
    [/^(.+) GB kullanılabilir RAM$/,(_,n)=>`${n} GB available RAM`],
    [/^(.+) GB boş$/,(_,n)=>`${n} GB free`],
    [/^(Son kayıt: |Son başarılı kayıt: )(.+)$/,(_,label,date)=>`${label==='Son kayıt: '?'Last record: ':'Last successful record: '}${date}`],
    [/^(Favorilere ekle|Favorilerden çıkar|Yukarı taşı|Aşağı taşı|Kaldır): (.+)$/,(_,label,name)=>`${({'Favorilere ekle':'Add to favorites','Favorilerden çıkar':'Remove from favorites','Yukarı taşı':'Move up','Aşağı taşı':'Move down','Kaldır':'Remove'})[label]}: ${translateUI(name,'en')}`],
    [/^(.+): (aç|dosya eksik)$/,(_,name,action)=>`${translateUI(name,'en')}: ${action==='aç'?'open':'file missing'}`],
    [/^(.+) seç$/,(_,name)=>`Select ${name}`],
    [/^(.+) · (dosya eksik|başlatılmış|bağlanıyor)$/,(_,name,action)=>`${name} · ${({'dosya eksik':'file missing','başlatılmış':'running','bağlanıyor':'connecting'})[action]}`],
    [/^(.+) · Gönderdiğin mesaj ve bu sağlayıcıyla yakın sohbet geçmişi (.+) gönderilir\. Belge alıntıları ayrıca önizlenir\. Ücret ve kota hesabına aittir\.$/,(_,name,dest)=>`${name} · Your message and recent conversation with this provider are sent to ${dest}. Document excerpts are previewed separately. Charges and quotas apply to your account.`],
    [/^Hedef: (.+) · Model: (.+)$/,(_,dest,model)=>`Destination: ${dest} · Model: ${model}`],
    [/^(.+) \(ad ve yol gönderilmez\)$/,(_,label)=>`${label} (name and path are not sent)`],
    [/^(.+) açıldı\.$/,(_,name)=>`${name} opened.`],
    [/^Katalog sürümü: (.+)$/,(_,v)=>`Catalog version: ${v}`],
    [/^SHA-256: (.+)$/,(_,v)=>`SHA-256: ${EN[v]||v}`],
    [/^Yayıncı: (.+) · (.+)$/,(_,v,message)=>`Publisher: ${v} · ${translateUI(message,'en')}`],
    [/^(\d+) yeni sürüm · (\d+) yayıncı sayfasından kontrol · (\d+) kontrol hatası\. Karşılaştırma katalog sürümünedir; otomatik güncelleme yapılmaz\.(.*)$/,(_,a,b,c,tail)=>`${a} updates · ${b} publisher-page checks · ${c} check errors. Compared with the catalog; no automatic updates.${tail.replace('Son kontrol:','Last checked:')}`],
    [/^FieldDesk \/ (.+)$/,(_,label)=>`FieldDesk / ${translateUI(label,'en')}`],
    [/^(proje|şablon|Proje|Şablon) \/ (KOD ÇALIŞMA ALANI|KLASÖR)$/,(_,kind,type)=>`${EN[kind]} / ${EN[type]}`],
    [/^Çanta okunamadı: (.+)$/,(_,message)=>`Could not read workspace: ${translateUI(message,'en')}`],
    [/^(.+) Bilgi merkezinden arayabilirsin\.$/,(_,message)=>`${translateUI(message,'en')} Search for it in the library.`],
    [/^(.+) (· Klasörü aç)$/,(_,description)=>`${translateUI(description,'en')} · Open folder`]
  ];
  for(const [pattern,replace] of rules)if(pattern.test(trimmed))return text.replace(trimmed,trimmed.replace(pattern,replace));
  return text;
}

let uiLanguage='en';
let setUILanguage=()=>{};
function uiLocale(){return uiLanguage==='tr'?'tr-TR':'en-US';}
function t(text){return translateUI(text,uiLanguage);}
if(typeof module!=='undefined'&&module.exports)module.exports={translateUI,EN};
if(typeof document!=='undefined') {
  try{uiLanguage=localStorage.getItem('fielddesk-language')==='tr'?'tr':'en';}catch{}
  const textSources=new WeakMap(), attributeSources=new WeakMap();
  const excluded='script,style,pre,code,textarea,[data-user-content],[data-i18n-ignore],.message-body,.ocr-text,.result-path,.project-card h3,.project-card>p,.file-row strong,.picker-row strong,.plan-row>span';
  function localizeUI(){
    document.documentElement.lang=uiLanguage;
    document.title='FieldDesk — '+(uiLanguage==='tr'?'Taşınabilir çalışma alanı':'Portable workspace');
    const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
    for(let node;node=walker.nextNode();){
      const parent=node.parentElement;
      if(!parent||parent.closest(excluded)||!node.data.trim())continue;
      // Option values must never change when the visible label is translated.
      if(parent.tagName==='OPTION'&&!parent.hasAttribute('value'))parent.setAttribute('value',parent.textContent);
      let record=textSources.get(node);
      if(!record||node.data!==record.last)record={source:node.data,last:node.data};
      const result=t(record.source);
      if(node.data!==result)node.data=result;
      record.last=result;textSources.set(node,record);
    }
    for(const el of document.querySelectorAll('[aria-label],[placeholder],[title]')){
      if(el.closest('[data-user-content],[data-i18n-ignore]'))continue;
      let records=attributeSources.get(el)||{};
      for(const attr of ['aria-label','placeholder','title']){
        if(!el.hasAttribute(attr))continue;
        const value=el.getAttribute(attr);
        let record=records[attr];
        if(!record||record.last!==value)record={source:value,last:value};
        const result=t(record.source);
        if(result!==value)el.setAttribute(attr,result);
        record.last=result;records[attr]=record;
      }
      attributeSources.set(el,records);
    }
  }
  let queued=false;
  new MutationObserver(()=>{if(queued)return;queued=true;queueMicrotask(()=>{queued=false;localizeUI();});}).observe(document.body,{childList:true,subtree:true,characterData:true,attributes:true,attributeFilter:['aria-label','placeholder','title']});
  const select=document.getElementById('language-select');
  select.value=uiLanguage;
  setUILanguage=(value,persist=false)=>{
    uiLanguage=value==='tr'?'tr':'en';
    select.value=uiLanguage;
    try{localStorage.setItem('fielddesk-language',uiLanguage);}catch{}
    localizeUI();document.dispatchEvent(new CustomEvent('fielddesk-language',{detail:{persist,language:uiLanguage}}));
  };
  select.addEventListener('change',()=>setUILanguage(select.value,true));
  localizeUI();
}
