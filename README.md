# YÜKSEK LİSANS TEZ ÖNERİSİ

**Öğrenci Adı:** Yusuf Talha Arabacı
**Anabilim Dalı:** Yazılım Mühendisliği
**Proje Kod Adı:** Ubuntu Sovereign Stack
**Tez Başlığı (TR):** Ubuntu Tabanlı Açık Kaynak Kurumsal Mimari: Bulut Bağımlılığına Karşı Veri Egemenliği Odaklı Bir Alternatif Model
**Tez Başlığı (EN):** Ubuntu-Based Open Source Enterprise Architecture: An Alternative Model Focused on Data Sovereignty Against Cloud Dependency

---

## 1. ÖZET (ABSTRACT)

Bu tez çalışması, kurumların küresel bulut sağlayıcılarına (özellikle Microsoft Azure ve Office 365 ekosistemine) olan bağımlılığını azaltmak ve veri egemenliğini (*data sovereignty*) yasal ve teknik olarak güvence altına almak amacıyla, tamamen açık kaynak kodlu ve kurum içi (*on-premise*) çalışabilen bütünleşik bir BT mimarisi önermektedir.

Önerilen modelde; sunucu altyapısı **Rancher** ile yönetilen **Kubernetes** kümeleri üzerine kuruludur ve konteyner çalışma zamanı (CRI) olarak Docker yerine daha güvenli (daemonless/rootless) olan **Podman** teknolojisi esas alınmıştır. Kimlik yönetimi ve erişim güvenliği **Authentik** (SSO/MFA) ve **Samba 4 Active Directory** ile sağlanırken; tüm kurumsal iletişim (e-posta, takvim, rehber) **Zimbra Collaboration Suite**, **ClamAV** ve **SpamAssassin** entegrasyonu ile tek merkezden sunulmaktadır. Güvenlik ve gözlemlenebilirlik katmanında **Wazuh** (SIEM & Zafiyet Tespiti), **Prometheus** ve **Grafana** konumlandırılmıştır. İstemci tarafında ise tek tip dayatma yerine, **10 farklı Ubuntu LTS tabanlı** dağıtımın sunulduğu esnek bir model benimsenmiştir. Çalışma, bu mimariyi Toplam Sahip Olma Maliyeti (TCO), ABD CLOUD Act kaynaklı yasal risklerin eliminasyonu ve operasyonel sürdürülebilirlik açısından ticarî muadilleriyle karşılaştırmalı olarak analiz etmeyi hedefler.

---

## 2. GİRİŞ VE PROBLEM TANIMI

### 2.1. Bulut Bağımlılığı ve "Vendor Lock-in" Sorunu
Dijital dönüşüm süreçlerinde kurumlar, yönetim kolaylığı ve ölçeklenebilirlik vaadiyle Microsoft Azure, AWS ve Google Cloud gibi küresel sağlayıcılara yönelmektedir. Özellikle Microsoft'un "Cloud-First" stratejisi, müşteriyi sadece buluta çekmekle kalmayıp, oradan çıkışı teknik ve mali açıdan zorlaştıran bir "Vendor Lock-in" (Tedarikçi Kilidi) döngüsü yaratmaktadır:

* **Veri Yerçekimi (Data Gravity):** Veri bulut ortamına bir kez girdiğinde, "Egress Fees" (veri çıkış ücretleri) ve tescilli API bağımlılıkları nedeniyle taşınması fahiş maliyetlere yol açmaktadır.
* **Hibrit Tuzak:** Windows Server 2025 gibi yeni sürümlerde yerel yönetim araçlarının desteğinin azaltılması ve Azure Arc entegrasyonunun zorlanması, kurum içi (on-premise) sistemleri "ikinci sınıf" konuma düşürmektedir.
* **SaaS Bağımlılığı:** Office 365 ekosistemi (Teams, SharePoint, OneDrive), kurumları tek bir sağlayıcıya mekanik olarak bağlamaktadır.

### 2.2. Yasal Çatışma: Veri Egemenliği vs. ABD Yasaları
Sorunun temelinde teknik yetersizlikten ziyade, **yargı yetkisi (jurisdiction)** problemi yatmaktadır.

* **ABD CLOUD Act Riski:** Bu yasa, ABD menşeli şirketlerin verileri nerede saklanırsa saklansın (Data Residency Türkiye'de olsa dahi), ABD kolluk kuvvetleri talep ettiğinde bu veriyi teslim etmesini zorunlu kılar.
* **GDPR ve KVKK Uyumu:** Mart 2024'te Avrupa Veri Koruma Denetçisi (EDPS), Avrupa Komisyonu'nun Microsoft 365 kullanımının veri koruma kurallarını ihlal ettiğine hükmetmiştir. AB kurumları için dahi risk oluşturan bu durum, KVKK'nın "verinin yerli ve milli imkanlarla saklanması" ilkesiyle doğrudan çelişmektedir.

---

## 3. TEZİN AMACI VE HEDEFLERİ

Bu tez, söz konusu yasal ve teknik kuşatmaya karşı, verinin mülkiyetinin ve yönetiminin %100 kurumda kaldığı bağımsız bir "Egemen Bulut" (Sovereign Cloud) mimarisi geliştirmeyi amaçlar.

**Temel Hedefler:**
1.  **Hukuksal Güvenlik:** ABD CLOUD Act risklerini elimine eden, sadece Türk Hukukuna (KVKK) tabi bir altyapı sunmak.
2.  **Maliyet Etkinliği:** Lisans maliyeti olmayan bu yapının 5 yıllık projeksiyonda (TCO), bulut aboneliklerine (OpEx) göre tasarruf sağladığını kanıtlamak.
3.  **Teknik Sürdürülebilirlik:** Podman ve Kubernetes tabanlı modern mimarinin, kurumsal performans gereksinimlerini karşıladığını ampirik testlerle göstermek.

---

## 4. ÇÖZÜM MATRİSİ: MEVCUT DURUM vs. ÖNERİLEN MODEL

Aşağıdaki tablo, Microsoft ekosistemi ile tez kapsamında önerilen açık kaynak mimarinin stratejik karşılaştırmasını sunmaktadır:

| Risk Faktörü | Microsoft (Azure/O365) Durumu | Önerilen Mimari (On-Premise OSS) |
| :--- | :--- | :--- |
| **Yasal Erişim** | ABD CLOUD Act'e tabi. Veri ABD devletine verilebilir. | Sadece Türk Hukukuna (KVKK) tabi. Veri kurum dışına çıkmaz. |
| **Veri Konumu** | "Region" seçilse bile Kontrol Düzlemi (Control Plane) ABD'dedir. | %100 Kurum İçi (On-Prem). Fiziksel erişim kurumdadır. |
| **Bağımlılık** | Tescilli API'lar ve Egress ücretleri ile çıkış zordur. | Açık standartlar (IMAP, CalDAV, CardDAV). Göç etmek kolaydır. |
| **Lisanslama** | Sürekli artan döviz endeksli abonelik maliyeti. | Açık kaynak (GPL/Apache). Maliyet donanım ve insan gücüdür. |
| **Kimlik Yönetimi** | Azure AD (Entra ID) bağımlılığı. | Samba 4 AD + Authentik (Platform bağımsız SSO). |

---

## 5. MATERYAL VE YÖNTEM (SİSTEM MİMARİSİ)

Proje, "Cloud Native" prensiplerle tasarlanmış, birbiriyle entegre 5 ana katmandan oluşur.

### 5.1. Sunucu ve Altyapı Katmanı
* **İşletim Sistemi:** Kararlılık ve 5 yıllık kurumsal destek (LTS) nedeniyle **Ubuntu Server**.
* **Orkestrasyon:** Küme yönetimi, ölçekleme ve yaşam döngüsü için **Rancher** tarafından yönetilen **Kubernetes**.
* **Konteyner Runtime (CRI):** Docker yerine, **Podman** tercih edilmiştir. Podman'in *daemonless* (arka plan servisi olmadan çalışma) ve *rootless* (yetkisiz kullanıcı ile çalışma) yapısı, mimarinin güvenlik katsayısını artırmaktadır.

### 5.2. Kimlik ve Erişim Yönetimi (IAM)
* **Dizin Hizmeti:** Windows AD protokolleriyle tam uyumlu **Samba 4 Active Directory**.
* **Kimlik Sağlayıcı (IdP):** Tüm uygulamalar (Zimbra, Grafana vb.) için Merkezi Oturum Açma (SSO) ve Çok Faktörlü Kimlik Doğrulama (MFA) sağlayan **Authentik**.

### 5.3. İletişim ve İşbirliği
* **Grup Yazılımı:** Microsoft Exchange alternatifi olarak; E-posta, Takvim ve Dosya Paylaşımı için **Zimbra Collaboration Suite**.
* **İletişim Güvenliği:** E-posta ağ geçidinde **SpamAssassin** ve **ClamAV** entegrasyonu.

### 5.4. Güvenlik ve Gözlemlenebilirlik
* **SIEM & XDR:** Tüm uç noktalardan log toplayan, saldırı tespiti yapan ve CVE veritabanına göre zafiyet tarayan **Wazuh** platformu.
* **İzleme:** Sistem metrikleri için **Prometheus** ve görselleştirme için **Grafana**.

### 5.5. İstemci (Client) Katmanı: Esnek Dağıtım Modeli
Tek tip işletim sistemi dayatması yerine, kullanıcı profillerine göre özelleştirilmiş, merkezi yönetime (Wazuh Agent entegreli) dahil edilen 10 farklı dağıtım seçeneği:

| No | Dağıtım | Hedef Profil | Temel Avantaj |
|:---|:---|:---|:---|
| **1** | **Ubuntu Desktop** | Standart Kurumsal | Referans dağıtım, resmi destek. |
| 2 | Linux Mint | Ofis Çalışanı | Windows benzeri arayüz, kolay geçiş. |
| 3 | Zorin OS | Yönetici | Modern ve şık (Windows 11 benzeri). |
| 4 | Xubuntu | Eski Donanım | XFCE ile yüksek performans. |
| 5 | Lubuntu | İnce İstemci | Minimum kaynak tüketimi (LXQt). |
| 6 | Pop!_OS | Mühendis/Yazılımcı | Gelişmiş iş akışı ve GPU yönetimi. |
| 7 | Kubuntu | Power User | Tam özelleştirilebilirlik (KDE). |
| 8 | Ubuntu MATE | Gelenekselci | Klasik masaüstü deneyimi. |
| 9 | elementary OS | Kiosk/Danışma | Kararlı, macOS benzeri kısıtlı arayüz. |
| 10 | KDE Neon | Ar-Ge | En güncel arayüz teknolojileri. |

---

## 6. İŞ PAKETLERİ VE ZAMAN ÇİZELGESİ

* **Ay 1-2:** Altyapı kurulumu (Ubuntu, Kubernetes, Rancher, Podman yapılandırması).
* **Ay 3-4:** Kimlik (Samba AD, Authentik) ve İletişim (Zimbra, ClamAV) servislerinin entegrasyonu.
* **Ay 5:** Güvenlik katmanının (Wazuh, Prometheus) aktif edilmesi ve SIEM kurallarının yazılması.
* **Ay 6:** Pilot kullanıcı grubuyla 10 farklı istemci dağıtımının testi ve TCO analizi.
* **Ay 7-8:** Bulguların raporlanması ve tezin yazımı.

---

## 7. KAYNAKLAR (ÖN LİSTE)

1.  **Arabacı, Y. T.** (2024). *Microsoft’s Cloud-First Strategy and Data Privacy*. Medium.
2.  **Microsoft.** (2023). *Windows Server 2025 and Azure Arc Integration Overview*. Microsoft Learn.
3.  **US Congress.** (2018). *Clarifying Lawful Overseas Use of Data Act (CLOUD Act)*. H.R.4943.
4.  **Canonical.** (2024). *Ubuntu Server LTS: Security and Support Lifecycle*. Ubuntu.com.
5.  **The Wazuh Team.** (2024). *Wazuh: Open Source XDR and SIEM Documentation*. Wazuh.com.
