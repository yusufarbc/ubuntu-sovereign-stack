# ubuntu-sovereign-stack
An open-source, on-premise enterprise architecture based on Ubuntu LTS, Kubernetes/Podman, and Wazuh to ensure data sovereignty and eliminate cloud dependency

**Tez Önerisi Özeti:**

Bu tez, kurumların Microsoft Azure ve Office 365 gibi küresel bulut sağlayıcılarına bağımlılığını azaltmayı ve veri egemenliğini (data sovereignty) hem yasal hem de teknik olarak güvence altına almayı amaçlayan, tamamen açık kaynaklı ve kurum içi (on-premise) bir BT mimarisi önermektedir. Microsoft'un "Cloud-First" stratejisi ve CLOUD Act gibi yasaların yarattığı risklere karşı, kurumların verilerini kendi kontrolünde tutabileceği bir "Egemen Bulut" (Sovereign Cloud) modeli sunulmaktadır.

**Önerilen Mimarinin Temel Bileşenleri:**

* **Sunucu Altyapısı:** Ubuntu Server LTS üzerinde Rancher tarafından yönetilen Kubernetes kümeleri ve Docker yerine daha güvenli olan **Podman** konteyner teknolojisi kullanılacaktır.
* **Kimlik ve Erişim Yönetimi:** Windows AD ile tam uyumlu **Samba 4 Active Directory** ve tüm uygulamalar için SSO/MFA sağlayan **Authentik** kullanılacaktır.
* **İletişim ve İşbirliği:** Microsoft Exchange alternatifi olarak e-posta, takvim ve dosya paylaşımı için **Zimbra Collaboration Suite**; güvenlik için ise **SpamAssassin** ve **ClamAV** entegrasyonu sağlanacaktır.
* **Güvenlik ve Gözlemlenebilirlik:** Merkezi log yönetimi, saldırı tespiti ve zafiyet taraması için **Wazuh**; sistem izleme için **Prometheus** ve **Grafana** kullanılacaktır.
* **İstemci Katmanı:** Tek tip sistem yerine, kullanıcı profillerine göre (ofis çalışanı, yönetici, mühendis vb.) özelleştirilmiş **10 farklı Ubuntu LTS tabanlı dağıtım** (Linux Mint, Zorin OS, Pop!_OS vb.) sunulacaktır.

**Araştırmanın Hedefleri:**

Çalışma, bu mimariyi maliyet (TCO), yasal güvenlik (CLOUD Act risklerinin eliminasyonu) ve teknik yönetilebilirlik açısından ticari muadilleriyle karşılaştırmalı olarak analiz etmeyi ve uygulanabilir bir alternatif model ortaya koymayı hedeflemektedir.

---

# YÜKSEK LİSANS TEZ ÖNERİSİ (NİHAİ SÜRÜM)

**Öğrenci Adı:** Yusuf Talha Arabacı
**Anabilim Dalı:** Yazılım Mühendisliği
**Tez Başlığı (TR):** Ubuntu Tabanlı Açık Kaynak Kurumsal Mimari: Bulut Bağımlılığına Karşı Veri Egemenliği Odaklı Bir Alternatif Model
**Tez Başlığı (EN):** Ubuntu-Based Open Source Enterprise Architecture: An Alternative Model Focused on Data Sovereignty Against Cloud Dependency

---

### 1. ÖZET (ABSTRACT)
Bu tez çalışması, kurumların küresel bulut sağlayıcılarına (özellikle Microsoft Azure ve Office 365 ekosistemine) olan bağımlılığını azaltmak ve veri egemenliğini (data sovereignty) yasal ve teknik olarak güvence altına almak amacıyla, tamamen açık kaynak kodlu ve kurum içi (on-premise) çalışabilen bütünleşik bir BT mimarisi önermektedir. Önerilen modelde; sunucu altyapısı **Rancher** ile yönetilen **Kubernetes** kümeleri üzerine kuruludur ve konteyner çalışma zamanı (CRI) olarak Docker yerine **Podman** teknolojisi esas alınmıştır. Kimlik yönetimi ve erişim güvenliği **Authentik** (SSO/MFA) ve **Samba 4 Active Directory** ile sağlanırken; tüm kurumsal iletişim (e-posta, takvim, rehber) **Zimbra Collaboration Suite**, **ClamAV** ve **SpamAssassin** entegrasyonu ile tek merkezden sunulmaktadır. Güvenlik ve gözlemlenebilirlik katmanında **Wazuh** (SIEM & Zafiyet Tespiti), **Prometheus** ve **Grafana** konumlandırılmıştır. İstemci tarafında ise tek tip dayatma yerine, **10 farklı Ubuntu LTS tabanlı** dağıtımın sunulduğu esnek bir model benimsenmiştir. Çalışma, bu mimariyi Toplam Sahip Olma Maliyeti (TCO), ABD CLOUD Act kaynaklı yasal risklerin eliminasyonu ve operasyonel sürdürülebilirlik açısından ticarî muadilleriyle karşılaştırmalı olarak analiz etmeyi hedefler.

---

### 2. GİRİŞ VE PROBLEM TANIMI
Dijital dönüşümle birlikte kurumlar, yönetim kolaylığı nedeniyle bulut hizmetlerine yönelmektedir. Ancak kritik verilerin küresel sağlayıcılarda (Amazon, Microsoft, Google) barındırılması, "Veri Egemenliği" sorununu doğurmaktadır. [cite_start]Veriler fiziksel olarak ülke içinde tutulsa bile (Data Residency), hizmet sağlayıcı ABD menşeli olduğu sürece **CLOUD Act** yasası gereği yabancı yargı makamlarının veriye erişim riski devam etmektedir[cite: 4, 1].

[cite_start]Özellikle Microsoft'un "Cloud-First" stratejisiyle Windows Server 2025 ve sonraki sürümlerde Azure entegrasyonunu zorunlu kılması, yerel yönetim araçlarını (örn: WSUS) desteğini çekerek (deprecation) kurumları hibrit yapıya zorlaması, hem lisans maliyetlerini artırmakta hem de tam veri kontrolünü imkansız hale getirmektedir[cite: 3, 2]. Bu tez, söz konusu yasal ve teknik kuşatmaya karşı, verinin mülkiyetinin ve yönetiminin %100 kurumda kaldığı bağımsız bir mimari modeli sunarak literatürdeki boşluğu doldurmayı amaçlamaktadır.

---

### 3. TEZİN AMACI VE KAPSAMI
**Amaç:**
Projenin amacı; ABD CLOUD Act gibi sınır ötesi veri erişim yasalarından bağımsız, Microsoft ekosistemine (Exchange, Active Directory, Azure) alternatif, Ubuntu tabanlı ve açık kaynak kodlu bir "Egemen Bulut" (Sovereign Cloud) mimarisi geliştirmektir.

**Araştırma Soruları:**
1.  **Hukuksal Güvenlik:** Önerilen yerel mimari, CLOUD Act kaynaklı sınır ötesi veri erişim risklerini Microsoft Azure/365 çözümlerine kıyasla nasıl elimine etmektedir?
2.  **Maliyet Etkinliği:** Lisans maliyeti olmayan bu yapının 5 yıllık Toplam Sahip Olma Maliyeti (TCO), bulut abonelik modellerine göre ne düzeyde tasarruf sağlamaktadır?
3.  **Teknik ve İdari Yönetilebilirlik:** 10 farklı istemci dağıtımı ve Podman tabanlı Kubernetes altyapısı, kurumsal yönetim standartlarını (SSO, Yama Yönetimi, Loglama) karşılayabilmekte midir?

---

### 4. MATERYAL VE YÖNTEM (SİSTEM MİMARİSİ)
Proje, "Cloud Native" prensiplerle tasarlanmış 5 ana katmandan oluşur.



[Image of Kubernetes architecture diagram]


#### 4.1. Sunucu ve Altyapı Katmanı
* **İşletim Sistemi:** 5 yıllık kurumsal destek süresi ve kararlılık nedeniyle **Ubuntu Server LTS**.
* **Orkestrasyon:** Küme yönetimi ve yaşam döngüsü için **Rancher** tarafından yönetilen **Kubernetes**.
* **Konteyner Runtime:** Docker yerine, güvenlik (daemonless yapı) ve lisans avantajları nedeniyle **Podman** teknolojisi kullanılacaktır.

#### 4.2. Kimlik ve Erişim Yönetimi (IAM)
* **Dizin Hizmeti (Source of Truth):** Windows AD protokolleriyle tam uyumlu, kullanıcı ve grup politikalarının merkezi **Samba 4 Active Directory**.
* **Kimlik Sağlayıcı (IdP):** Tüm uygulamalar (Zimbra, Grafana vb.) için Merkezi Oturum Açma (SSO) ve Çok Faktörlü Kimlik Doğrulama (MFA) sağlayan **Authentik**.

#### 4.3. İletişim ve İşbirliği (Zimbra Collaboration Suite)
* **E-Posta ve İşbirliği:** Microsoft Exchange alternatifi olarak; E-posta, Takvim, Kişiler ve Dosya Paylaşımı hizmetlerini bütünleşik sunan **Zimbra Collaboration Suite (Open Source Edition)** kullanılacaktır.
* **İletişim Güvenliği:** E-posta trafiği, **SpamAssassin** (istenmeyen posta filtresi) ve **ClamAV** (antivirüs) ağ geçitleri ile korunarak güvenli iletişim sağlanacaktır.

#### 4.4. Güvenlik ve Gözlemlenebilirlik
* **SIEM & Zafiyet Tespiti:** Tüm sunucu ve istemcilerden log toplayan, saldırı tespiti yapan ve "Vulnerability Detector" modülü ile sistemdeki paket zafiyetlerini tarayan **Wazuh** platformu. (OpenVAS yerine Wazuh'un yerleşik yetenekleri kullanılacaktır).
* **İzleme:** Sistem kaynak kullanımı (CPU/RAM/Disk) için **Prometheus** ve görselleştirme için **Grafana**.



[Image of Wazuh architecture diagram]


#### 4.5. İstemci (Client) Katmanı: Esnek Dağıtım Modeli
Tümü Ubuntu LTS tabanlı, merkezi yönetime (Wazuh Agent/ClamAV) entegre 10 dağıtım seçeneği:

| No | Dağıtım | Hedef Profil | Temel Avantaj |
|:---|:---|:---|:---|
| **1** | **Ubuntu Desktop** | Standart Kurumsal | Referans dağıtım, resmi destek. |
| 2 | Linux Mint | Ofis Çalışanı | Windows benzeri en kolay geçiş. |
| 3 | Zorin OS | Yönetici | Modern/Şık Windows 11 görünümü. |
| 4 | Xubuntu | Eski Donanım | Dengeli performans (XFCE). |
| 5 | Lubuntu | İnce İstemci | Minimum kaynak tüketimi (LXQt). |
| 6 | Pop!_OS | Mühendis/Yazılımcı | İş akışı ve GPU optimizasyonu. |
| 7 | Kubuntu | Power User | Tam özelleştirme (KDE). |
| 8 | Ubuntu MATE | Gelenekselci | Klasik ve hızlı yapı. |
| 9 | elementary OS | Kiosk/Danışma | Bozulması zor, macOS benzeri. |
| 10 | KDE Neon | Ar-Ge | En yeni arayüz teknolojileri. |

---

### 5. NEDEN UBUNTU LTS TABANI?
1.  [cite_start]**Sürdürülebilirlik:** 5 yıl resmi güvenlik güncellemesi garantisi ve kurumsal kararlılık[cite: 5].
2.  **Bütünlük:** Sunucudan istemciye tüm katmanlarda `.deb` paket yönetimi ve ortak sürücü havuzu kullanımı sayesinde yönetim kolaylığı.
3.  **Uyumluluk:** Podman, Zimbra ve Kubernetes gibi kritik bileşenlerin referans platformu olması.

---

### 6. İŞ PAKETLERİ VE ZAMAN ÇİZELGESİ (Özet)
* **Ay 1-2:** Altyapı kurulumu (Ubuntu, Kubernetes, Rancher, Podman yapılandırması).
* **Ay 3-4:** Kimlik (Samba AD, Authentik) ve İletişim (Zimbra, ClamAV) servislerinin devreye alınması ve entegrasyonu.
* **Ay 5:** Güvenlik katmanının (Wazuh, Prometheus, Grafana) aktif edilmesi ve SIEM kurallarının yazılması.
* **Ay 6:** Pilot kullanıcı grubuyla 10 farklı istemci dağıtımının testi, TCO analizi ve stres testleri.
* **Ay 7-8:** Bulguların raporlanması, karşılaştırmalı analizlerin yapılması ve tezin yazımı.

---

### 7. KAYNAKLAR (ÖN LİSTE)

1.  **Arabacı, Y. T.** (2024). *Microsoft’s Cloud-First Strategy and Data Privacy*. Medium.
2.  **Arabacı, Y. T.** (2024). *Microsoft’un Bulut Odaklı Stratejisi*. Medium.
3.  **Microsoft.** (2023). *Windows Server 2025 and Azure Arc Integration Overview*. Microsoft Learn.
4.  **US Congress.** (2018). *Clarifying Lawful Overseas Use of Data Act (CLOUD Act)*. H.R.4943.
5.  **Canonical.** (2024). *Ubuntu Server LTS: Security and Support Lifecycle*. Ubuntu.com.
6.  **The Wazuh Team.** (2024). *Wazuh: Open Source XDR and SIEM Documentation*. Wazuh.com.
