# Hesap Makinesi

Türkçe yazım kurallarıyla çalışan (binlik ayracı nokta, ondalık ayracı virgül) basit bir hesap makinesi. Masaüstü (Windows) ve Android sürümü vardır.

## Özellikler

- Dört işlem ve yüzde işlemleri
- **%+ / %−**: `100 %+ 20 = 120`, `100 %− 20 = 80`
- **KDV−**: KDV dahil tutardan KDV hariç tutarı bulur (%20 oranıyla), örneğin `580 KDV− = 483,33`
- **AC+ / AC− / AC× / AC÷ / AC=**: ekrandaki sayıyı biriken toplama işler ve ekranı sıfırlar. `AC=` toplamı verir.
  Örnek: `100 AC+  25 AC+  10 AC=` → `135`

## Çalıştırma

**Windows:** `HesapMakinesi.exe` dosyasına çift tıklayın. Kurulum gerekmez (Windows 10/11, 64 bit).
Windows SmartScreen uyarı verirse "Ek bilgi" → "Yine de çalıştır" deyin; program dijital olarak imzalı değildir.

**Python ile:** Python 3 kuruluyken
```
python "Kaynak Kod/hesap_makinesi.pyw"
```

**Android:** `hesap-makinesi-android/android/BUILD.md` dosyasına bakın.

## Telif ve Lisans

© 2026 YGS. Tüm hakları saklıdır.

Bu yazılım izinsiz kopyalanamaz, değiştirilemez, dağıtılamaz veya kullanılamaz. Ayrıntılar için [LICENSE](LICENSE) dosyasına bakın.
