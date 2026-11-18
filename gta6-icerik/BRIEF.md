# GTA 6 Çıkış İçerik Brifi (kalıcı hafıza)

> Yeni bir Claude oturumunda: "gta6-icerik/BRIEF.md dosyasını oku ve oradan devam et" demen yeterli.

## Kanal ve hesaplar
- YouTube: **@artozlab** (artoZLab) — vidIQ üzerinden bağlı, paylaşım yapabilir
- Instagram: **@artozlab** (artoZ.lab, profesyonel hesap) — vidIQ üzerinden bağlı, paylaşım yapabilir
- İçerik alanı: video oyunları, 3D modeller, lifestyle

## Kararlar (kullanıcı onaylı)
- **Format:** Şimdilik SADECE dikey (YouTube Shorts + Instagram Reels). Yatay video şimdilik YOK (ileride 5 dk olacak).
- **Dil:** Sadece Türkçe seslendirme.
- **Ses:** ElevenLabs **"Nil - Dynamic, Playful and Clear"** — voice_id `N0wraTTB0pquzsz3DLG8`, model `eleven_v4`, her zaman **tek take** (generations_count=1).
- **Senaryo yapısı:** 35-45 sn; ilk 1,5 sn kanca; her cümlede sahne değişimi; **son cümle "çünkü..." gibi yarıda kalmaz → izleyiciyi harekete geçiren bir SORU ile biter** ("... Yorumlara yaz!").
- **Akış:** Senaryo → (gerekirse ses örneği onayı) → seslendirme → montaj → paylaşım metni → **kullanıcının SON ONAYI** → paylaşım. Onaysız asla paylaşılmaz. Paylaşım saatini kullanıcı söyler.
- **Telif:** Kullanıcı başka hesapların kliplerini kullanmayı kabul ediyor; tercih edilen görüntü kaynağı Rockstar'ın resmi görselleri/klipleri (rockstargames.com/VI).
- **Yapılmayacak konular (kullanıcı zaten hazırladı):** "212 GB – hangi oyunu sileceksin?", "Kutudan disk değil kâğıt çıktı".
- **Kredi uyarısı:** ElevenLabs karakteri 2.000'in altına düşünce ve bittiğinde kullanıcıya AYRICA ve açıkça haber ver (başka hesaptan seslendirme alabilir).

## Önemli saatler (Türkiye saati)
- GTA 6 ilk açılış: Yeni Zelanda 19 Kas 00:00 NZDT = **18 Kasım 14:00 TR**
- Avustralya 16:00 · Güney Kore 18:00 · BAE 23:00 · **Türkiye 19 Kas 00:00 (beklenen, resmi değil)** · İngiltere 03:00 · ABD Doğu 08:00 · Meksika 09:00
- 14:00–00:00 arası: Türk izleyici oynayamıyor ama izliyor → en değerli pencere.

## Üretilen videolar
| # | Konu | Durum |
|---|---|---|
| 1 | Türkiye'den 10 saat önce GTA 6 oynayan ülke | Hazır ama kullanıcı RAFA KALDIRDI (18 Kas) — paylaşma, hatırlatma |
| 2 | Yeni Zelanda hilesi PS5'te işe yarıyor mu? | PLANLANDI: Instagram 18 Kas 13:00 (kapaklı, ilk kare), YouTube Shorts 18 Kas 14:00 (https://www.youtube.com/watch?v=t0sxlBv5HGY) |
| 3a | GTA 6'ya 99 puan! Tarihe geçti (Metacritic) | YAYINDA: YouTube Shorts 18 Kas ~14:40 (https://www.youtube.com/watch?v=Fdjnp0nqG3w). Instagram'a kullanıcı istemedi. |
| 4 | GTA 6'yı açar açmaz bu 5 şeyi yap | Hazır, YouTube taslağı var (postId 54ec4c63...), kullanıcı kararı bekleniyor (öneri 23:00) |
| 5 | GTA 6'nın ilk oynanış görüntüleri (kullanıcının verdiği X + YouTube klipleri) | YAYINDA: YouTube Shorts 18 Kas (https://www.youtube.com/watch?v=yt35uvE33xo) |
| 6 | Bedava GTA 6 kazanmanın 2 resmi yolu (Kick + Twitch, gerçek arayüz + kasa/drop animasyonları; ses: kullanıcının gönderdiği Nil kaydı) | YAYINDA: YouTube Shorts 18 Kas ~21:15 (https://www.youtube.com/watch?v=igoOsIpHxPM) + Instagram Reels (kapaklı) |
| 3 | GTA 6'da Türkçe yok – CİMER şikâyeti | Senaryo yazıldı, henüz üretilmedi |
| 4 | 4.811 gün – 13 yıllık bekleyiş | Senaryo yazıldı, henüz üretilmedi |

Paylaşım metinleri (onaylı):
- V1 başlık: `Türkiye'den 10 Saat Önce GTA 6 Oynayan Ülke 😳 #shorts`
- V2 başlık: `GTA 6 Yeni Zelanda Hilesi PS5'te Çalışıyor mu? 🤔 #shorts`
- Hashtagler: #GTA6 #GTAVI #GTA6Türkiye #GrandTheftAuto6 (+ konuya özel)

## Teknik kurulum (yeni bulut makinesinde)
```
pip3 install yt-dlp faster-whisper edge-tts
```
- `engine.py <spec.json>` → 1080x1920 MP4 (Inter Display Black font, kelime kelime altyazı, kanca yazısı, soru kartı, sahne geçiş efekti).
- Görseller: rockstargames.com/VI sayfasındaki `/VI/_next/static/media/*.jpg` dosyaları indirilir; `contact_index.txt` numaralarıyla spec'te kullanılır.
- Klip indirme: TikTok ve Instagram çalışıyor; YouTube bulut IP'sinde bot kontrolüne takılıyor.
- Altyazı zamanlaması: faster-whisper (small) ile ses ↔ senaryo hizalaması.

## Notlar
- ElevenLabs ücretsiz paketi bir kez "olağan dışı etkinlik" diye üretimi durdurdu, sonra tekrar çalıştı. Yedek: vidIQ seslendirmesi (~28 kredi / 1000 karakter) veya Microsoft Edge "tr-TR-AhmetNeural".
- vidIQ kredisi sınırlı (~100); araştırmada önce ücretsiz web aramasını kullan.
- Araştırma brifi: `arastirma/01_cikis_oncesi.md`
