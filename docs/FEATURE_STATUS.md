# GUARD AI ekran durumları

Bu tablo, canlı API davranışını etkileşimli demo davranışından ayırır.

| Ekran | Ne işe yarar? | Mevcut davranış |
| --- | --- | --- |
| AI Ajanları | Gateway tarafından korunan ajanları ve ayrıntılarını gösterir. | Canlı API verisi; demo modu açıksa API kesintisinde örnek veriye düşebilir. |
| Politikalar | Deterministik Policy Engine kurallarını gösterir. | Canlı ve salt okunur API listesi; oluşturma/düzenleme henüz demo davranışıdır. |
| Güvenlik Olayları | Gateway kararlarını arar, filtreler, inceler ve JSON olarak dışa aktarır. | Canlı API verisi; demo fallback desteklenir. |
| Gölge Modu | Trafiği engellemeden olası policy etkilerini gösterir. | Tarayıcı oturumuyla sınırlı etkileşimli demo. |
| İncelemeler | Bir kararın kullanıcı niyetinden enforcement sonucuna kadar izini gösterir. | Örnek olay ve yerel eşik simülasyonu. |
| Acil Kontroller | Enforcement modu, ajan izolasyonu ve lockdown davranışını gösterir. | Güvenli demo; canlı ajan veya backend durumu değişmez. |
| Hızlı Kurulum | İlk ajan entegrasyonunun örnek adımlarını gösterir. | Yönlendirmeli demo; gerçek workspace veya bağlantı oluşturmaz. |
| Entegrasyonlar | Ajan, onay kanalı, SIEM ve gözlemleme bağlantılarını listeler. | Aranabilir demo katalog; bağlantı durumu kalıcı değildir. |
| Ajan Keşfi | Ajanların araçlar ve korunan sistemlerle ilişkisini görselleştirir. | Örnek erişim haritası; canlı keşif etkin değildir. |
| Politika Asistanı | Doğal dildeki kuraldan açıklanabilir policy taslağı üretir. | Deterministik demo; taslak canlı Policy API'ye yazılmaz. |
| AI Güvenlik Analisti | Olay kayıtlarını özetler ve ilgili kanıtlara bağlar. | API olayları üzerinde çalışan kural tabanlı analiz; LLM değildir. |
| Saldırı Laboratuvarı | Prompt injection, veri sızdırma ve yetki yükseltme savunmalarını gösterir. | İzole simülasyon; production sistemine istek göndermez. |
| Uyumluluk | Kanıt türlerini mevzuat ve güvenlik kontrolleriyle eşler. | Örnek skorlar; sertifikasyon veya canlı compliance sonucu değildir. |

## Yayın doğrulaması

Frontend için `npm run check`, backend için `pytest` çalıştırılmalıdır. Canlı deployment doğrulamasında demo fallback kapatılmalıdır; aksi hâlde API kesintisi örnek veriyle maskelenebilir.
