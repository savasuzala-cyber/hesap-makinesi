# Hesap Makinesi — Android (APK)

Arayüz ve hesap mantığı: `assets/index.html` (masaüstü hesap_makinesi.pyw ile birebir aynı mantık).
`src/.../MainActivity.java` yalnızca bu sayfayı tam ekran WebView'de açar.

## Derleme (Ubuntu/WSL)
    sudo apt install aapt apksigner android-sdk-platform-23 dalvik-exchange zipalign default-jdk
    SDK=/usr/lib/android-sdk/platforms/android-23/android.jar
    mkdir -p build/gen build/classes build/dex
    aapt package -f -m -J build/gen -M AndroidManifest.xml -S res -I $SDK
    javac -source 8 -target 8 -bootclasspath $SDK -d build/classes build/gen/com/serhad/hesapmakinesi/R.java src/com/serhad/hesapmakinesi/MainActivity.java
    dalvik-exchange --dex --output=build/dex/classes.dex build/classes
    aapt package -f -M AndroidManifest.xml -S res -A assets -I $SDK -F build/unsigned.apk
    (cd build/dex && aapt add ../unsigned.apk classes.dex)
    zipalign -f -p 4 build/unsigned.apk build/aligned.apk
    apksigner sign --ks hesap-imza.keystore --ks-key-alias hesap --out HesapMakinesi.apk build/aligned.apk

Her sürümde AndroidManifest.xml içindeki versionCode'u 1 artır (şu an 3 / v1.2).

## İmza anahtarı
`hesap-imza.keystore` bu repoda YOKTUR (ayrı saklanır). Telefondaki uygulamayı silmeden
güncellemek için aynı anahtarla imzalamak gerekir. Şifre: ayrı not edildi.
