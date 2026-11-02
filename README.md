<!--
Dosya Yolu: REPO_ROOT/README.md
Amac: Ragnar Ragnarok Online istemci patch artifactlerini public olarak dagitmak
Modul - Markdown
Version: 1.0.3
Aciklama: Yeni organizasyonun kanonik URL'leri ve kilitli 2022 dagitim siniri
Bagimli Oldugu Katman: Documentation
-->

# Ragnar Ragnarok Online - Patch Distribution

Bu repo **kaynak kod reposu degildir**. Oyuncu istemcilerinin indirecegi public patch artifactlerini tutar.

Kaynak ve build pipeline:

`LevelUpRagnarok/RagnarokClient` (private)

Dagitim kanallari:

- Thor Legacy
- RPatchur
- Beam

**Bu ortak THOR akisi sadece 2015/legacy uyumluluk kanali icindir.** 20220406 profili farkli ve su an kilitlidir (`2022/channel.json`: `ready: false`). Yeni BEAM v1 adaylari, kaynagi `LevelUpRagnarok/RagnarokClient`, olusturucusu `LevelUpRagnarok/beam-patcher` olacak sekilde ayri bir 2022/beam dagitim kanali uzerinden, yalnizca onaydan sonra yayimlanabilir.

## Public yapi

```text
/
  plist.txt
  channel.json
  data/
    *.thor
  rpatchur/
  beam/
    patchlist.txt
```

`plist.txt` Thor Legacy ve RPatchur tarafindan kullanilir.

`beam/patchlist.txt` Beam tarafindan kullanilir ve ayni THOR paketlerinin SHA-256 degerlerini tasir.

Bu repoya patch artifactleri elle duzenlenmek yerine private kaynak repodaki GitHub Actions pipeline'i tarafindan yayinlanir.

## 20220406 icin ayrilmis BEAM dagitim kanali

- [2022/beam/README.md](2022/beam/README.md) — kaynak, sahiplik ve onay kapilari.
- [2022/beam/channel-policy.json](2022/beam/channel-policy.json) — yayina kapali kanal sozlesmesi.
- [2022/beam/patchlist.txt](2022/beam/patchlist.txt) — bilerek bos; oyunculara paket yonlendirmez.

**Dikkat:** `data/`, `beam/`, `plist.txt` kok aliaslari 2015'e aittir, yeni haritalar bu yollara eklenmez. `2022/data/` altinda su anda onaylanmis `.beam` paketi bulunmaz. Patch dosyalarini hazirlamak, yayin izni verildigi anlamina gelmez.

## Organizasyon transferi ve indirme URL'leri

Kanonik public patch root:
`https://raw.githubusercontent.com/LevelUpRagnarok/ragnarokclientpatch/main/`.

2026-10-30 itibariyla [salt-okunur HTTP smoke](https://github.com/LevelUpRagnarok/ragnarokclientpatch/actions/runs/41078436381),
eski `b1glord` ve yeni `LevelUpRagnarok` raw adreslerinden `plist.txt`,
`2015/plist.txt`, `data/custom-cursor.thor` ve
`2015/data/custom-cursor.thor` dosyalarini HTTP 200 ile indirdi.
Dort dosyanin SHA-256 degerleri her iki adreste de ayniydi.
2026-10-30 sonraki [alti dosyali GET+SHA testinde](https://github.com/LevelUpRagnarok/ragnarokclientpatch/actions/runs/41080318821),
ayrica `data/custom-maps01.thor` ile `2015/data/custom-maps01.thor`
(her biri 8.791.873 bayt) eski ve yeni URL'lerden ayni SHA-256 ile indirildi.
Tum 26 THOR'un online indirilmesi ve gerçek Windows oyun patcher smoke **NOT RUN**.

Kurulu istemcide onceden kayitli URL, burada bir template degisince otomatik
guncellenmez. Yeni konfigurasyonu oyuncuya dagitmadan once izole 2015 istemcide
indirme, GRF uygulama, yedekleme ve rollback testleri gereklidir.
Ayrica rPatchur `web.index_url` ile isaret edilen HTML dosyalarinin
repo agacinda bulunmamasi [issue #3](https://github.com/LevelUpRagnarok/ragnarokclientpatch/issues/3)
altinda takip edilmektedir.

`2022/channel.json.ready=false` ve
`2022/beam/channel-policy.json.publish_allowed=false` tutulur.
Bu sahiplik duzeltmesi bir release veya patch yayin izni degildir.

## Ragnar kurulum EXE - public QA

Turkuaz temali Ragnar kurulumunun **oyun client'i icermeyen, preview-only**
Windows test artifacti, pinlenmis `LevelUpRagnarok/beam-patcher`
kaynak commit'inden ve bu public depodaki
[Public Ragnar Installer QA](.github/workflows/public-ragnar-installer-qa.yml)
akisi ile uretilir. `installer/qa/README.md` ek teknik ayrintilari tutar.

Bu QA akisi private `LevelUpRagnarok/RagnarokClient` reposunu cekmez,
oyuncu client'i dagitmaz, `2022/beam` kanalini acmaz ve GitHub Release
olusturmaz. Test artifactlari gecicidir; gercek Windows oyun patcher
guncelleme/rollback ve oyuncu GUI kabulu **NOT RUN**.
