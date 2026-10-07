import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# 1. SAYFA YAPILANDIRMASI
st.set_page_config(page_title="LGS Koçluk & Performans Sistemi", layout="wide", page_icon="🎓")

# 2. LGS MÜFREDATI (DERSLER VE KONULAR)
LGS_MUSERFAT = {
    "Türkçe (Genel)": ["Fiilimsiler", "Sözcükte Anlam", "Cümlede Anlam", "Cümle Ögeleri", "Cümle Türleri", "Yazım Kuralları", "Noktalama İşaretleri", "Metin Türleri", "Söz Sanatları", "Anlatım Bozuklukları"],
    "Türkçe (Paragraf)": ["Paragrafta Ana Fikir ve Konu", "Paragrafta Yardımcı Fikir", "Paragraf Yapısı ve Akış", "Görsel Okuma ve Grafikler", "Sözel Mantık ve Muhakeme"],
    "Matematik (Kazanım)": ["Çarpanlar ve Katlar", "Üslü İfadeler", "Kareköklü İfadeler", "Veri Analizi", "Olasılık", "Cebirsel İfadeler ve Özdeşlikler", "Doğrusal Denklemler", "Eşitsizlikler", "Üçgenler", "Eşlik ve Benzerlik", "Dönüşüm Geometrisi", "Geometrik Cisimler"],
    "Matematik (Yeni Nesil)": ["Çarpanlar ve Katlar (Beceri Temelli)", "Üslü İfadeler (Beceri Temelli)", "Kareköklü İfadeler (Beceri Temelli)", "Veri Analizi (Grafik Yorumlama)", "Olasılık (Muhakeme)", "Cebirsel İfadeler (Model)", "Denklemler ve Eşitsizlikler (Yeni Nesil)", "Üçgenler ve Benzerlik (Yeni Nesil)", "Geometrik Cisimler (Yeni Nesil)"],
    "Fen Bilimleri": ["Mevsimler ve İklim", "DNA ve Genetik Kod", "Basınç", "Madde ve Endüstri", "Basit Makineler", "Enerji Dönüşümleri ve Çevre Bilimi", "Elektrik Yükleri ve Elektrik Enerjisi"],
    "T.C. İnkılap Tarihi": ["Bir Kahraman Doğuyor", "Milli Uyanış", "Ya İstiklal Ya Ölüm!", "Atatürkçülük ve Çağdaşlaşan Türkiye", "Demokratikleşme Çabaları", "Atatürk Dönemi Dış Politika", "Atatürk'ün Ölümü ve Sonrası"],
    "Din Kültürü ve A.B.": ["Kader İnancı", "Zekat ve Sadaka", "Din ve Hayat", "Hz. Muhammed'in Örnekliği", "Kur'an-ı Kerim ve Özellikleri"],
    "İngilizce": ["Unit 1: Friendship", "Unit 2: Teen Life", "Unit 3: In the Kitchen", "Unit 4: On the Phone", "Unit 5: The Internet", "Unit 6: Adventures", "Unit 7: Tourism", "Unit 8: Chores", "Unit 9: Science", "Unit 10: Natural Forces"]
}

ANA_LGS_DERSLERI = ["Türkçe", "Matematik", "Fen Bilimleri", "T.C. İnkılap Tarihi", "Din Kültürü ve A.B.", "İngilizce"]

SEBEP_LISTESI = [
    "Yok / Hepsi Doğru",
    "Dikkat / İşlem Hatası",
    "Konu Bilgisi Eksik",
    "Soru Tarzını / Öncülü Anlamadım",
    "Süre Yetmedi",
    "İki Şık Arasında Kaldım / Tahmin Ettim"
]

# 3. VERİ DEPOSU VE KULLANICI YÖNETİMİ
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None
if "active_student" not in st.session_state:
    st.session_state["active_student"] = "Ali Yılmaz"

# Varsayılan Öğrenci Listesi ve Veri Yapısı
if "ogrenci_verileri" not in st.session_state:
    st.session_state["ogrenci_verileri"] = {
        "Ali Yılmaz": {
            "calisma": [],
            "deneme": [],
            "hedef_netler": {"Türkçe": 18.0, "Matematik": 15.0, "Fen Bilimleri": 18.0, "T.C. İnkılap Tarihi": 9.0, "Din Kültürü ve A.B.": 10.0, "İngilizce": 9.0},
            "ozlu_soz": "Başarı, her gün tekrarlanan küçük çabaların toplamıdır!"
        },
        "Zeynep Kaya": {
            "calisma": [],
            "deneme": [],
            "hedef_netler": {"Türkçe": 19.0, "Matematik": 17.0, "Fen Bilimleri": 19.0, "T.C. İnkılap Tarihi": 10.0, "Din Kültürü ve A.B.": 10.0, "İngilizce": 10.0},
            "ozlu_soz": "İnanmak, başarmanın yarısıdır!"
        }
    }

if "koc_lisans_durumu" not in st.session_state:
    st.session_state["koc_lisans_durumu"] = {"Ana Koç (Siz)": True, "Ahmet Hoca (Diğer Koç)": False}

# ----------------------------------------------------
# GİRİŞ EKRANI (LOGIN SYSTEM)
# ----------------------------------------------------
if not st.session_state["logged_in"]:
    st.title("🎓 LGS Koçluk & Performans Portalı")
    st.subheader("Lütfen Giriş Türünü Seçiniz")
    
    col_l1, col_l2 = st.columns(2)
    
    with col_l1:
        st.markdown("### 👨‍🎓 Öğrenci Girişi")
        secilen_ogrenci = st.selectbox("İsminizi Seçiniz:", list(st.session_state["ogrenci_verileri"].keys()))
        ogrenci_sifre = st.text_input("Öğrenci Şifresi (Varsayılan: 1234)", type="password", key="ogrenci_pass")
        if st.button("Öğrenci Olarak Giriş Yap", type="primary"):
            if ogrenci_sifre == "1234" or ogrenci_sifre == "":
                st.session_state["logged_in"] = True
                st.session_state["user_role"] = "Öğrenci"
                st.session_state["active_student"] = secilen_ogrenci
                st.rerun()
            else:
                st.error("Hatalı şifre!")

    with col_l2:
        st.markdown("### 👨‍🏫 Koç / Öğretmen Girişi")
        secilen_koc = st.selectbox("Koç Profili Seçiniz:", list(st.session_state["koc_lisans_durumu"].keys()))
        koc_sifre = st.text_input("Koç Şifresi (Varsayılan: koc123)", type="password", key="koc_pass")
        if st.button("Koç Olarak Giriş Yap"):
            if koc_sifre == "koc123":
                st.session_state["logged_in"] = True
                st.session_state["user_role"] = "Koç"
                st.session_state["active_koc"] = secilen_koc
                st.rerun()
            else:
                st.error("Hatalı koç şifresi!")
    st.stop()

# ----------------------------------------------------
# YAN MENÜ (SIDEBAR) & OTURUM BİLGİSİ
# ----------------------------------------------------
aktif_ogr = st.session_state["active_student"]
ogr_data = st.session_state["ogrenci_verileri"][aktif_ogr]

with st.sidebar:
    st.title("🎓 LGS Koçluk Paneli")
    st.info(f"👤 **Giriş Yapan:** {st.session_state['user_role']}")
    
    # Koç Giriş Yaptıysa Öğrenci Değiştirebilir
    if st.session_state["user_role"] == "Koç":
        st.subheader("👨‍🏫 Koç Yönetim Alanı")
        secili_ogr = st.selectbox("İncelenen Öğrenci:", list(st.session_state["ogrenci_verileri"].keys()), index=list(st.session_state["ogrenci_verileri"].keys()).index(aktif_ogr))
        st.session_state["active_student"] = secili_ogr
        
        st.divider()
        st.markdown("**➕ Yeni Öğrenci Ekle:**")
        yeni_ogr_adi = st.text_input("Öğrenci Adı Soyadı:")
        if st.button("Öğrenciyi Kaydet"):
            if yeni_ogr_adi and yeni_ogr_adi not in st.session_state["ogrenci_verileri"]:
                st.session_state["ogrenci_verileri"][yeni_ogr_adi] = {
                    "calisma": [], "deneme": [],
                    "hedef_netler": {d: 15.0 for d in ANA_LGS_DERSLERI},
                    "ozlu_soz": "Yeni hedeflere doğru adım at!"
                }
                st.success(f"{yeni_ogr_adi} eklendi!")
                st.rerun()
    else:
        st.subheader(f"Öğrenci: {aktif_ogr}")

    st.divider()
    st.warning(f"💡 **Motivasyon Notu:**\n\n_{ogr_data['ozlu_soz']}_")
    
    st.divider()
    st.markdown("### 🎯 Ders Bazlı Hedef Netler")
    for d, n in ogr_data["hedef_netler"].items():
        st.text(f"• {d}: {n} Net")

    st.divider()
    if st.button("🚪 Çıkış Yap"):
        st.session_state["logged_in"] = False
        st.rerun()

# ----------------------------------------------------
# ANA EKRAN SEKME YAPISI
# ----------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📝 Günlük Veri Girişi", 
    "📊 Deneme Sınavları & Net Hedefleri", 
    "📚 MEB Soruları & Çıkmışlar", 
    "📖 Kitap Okuma & Öz Değerlendirme", 
    "👨‍👩‍👧 Veli & Koç Analiz Paneli",
    "⚙️ Program & Koç Yönetimi"
])

# ----------------------------------------------------
# TAB 1: GÜNLÜK VERİ GİRİŞİ
# ----------------------------------------------------
with tab1:
    st.header(f"📌 Günlük Ders Çalışma ve Süre Girişi ({aktif_ogr})")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        tarih = st.date_input("Çalışma Tarihi", datetime.date.today())
        ders = st.selectbox("Çalışılan Ders", list(LGS_MUSERFAT.keys()))
        konu = st.selectbox("Çalışılan Konu", LGS_MUSERFAT[ders])
        sure_dk = st.number_input("Harcanan Süre (Dakika)", min_value=5, max_value=300, value=45, step=5)
    
    with col_t2:
        dogru = st.number_input("Doğru Soru Sayısı", min_value=0, value=25)
        yanlis = st.number_input("Yanlış Soru Sayısı", min_value=0, value=3)
        bos = st.number_input("Boş Soru Sayısı", min_value=0, value=2)
        hata_sebebi = st.selectbox("Yanlış / Boş Soruların Ana Sebebi", SEBEP_LISTESI)
        yapilamayana_bakildi = st.radio("Yapamadığın Soruların Çözümüne Baktın mı?", ["Evet", "Hayır"], horizontal=True)

    st.subheader("⏰ Çalışma Saat Aralığı ve Program Uyuşması")
    col_s1, col_s2, col_riayet = st.columns(3)
    with col_s1:
        baslangic = st.time_input("Başlangıç Saati", datetime.time(16, 0))
    with col_s2:
        bitis = st.time_input("Bitiş Saati", datetime.time(18, 0))
    with col_riayet:
        programa_riayet = st.selectbox("Günlük Çalışma Programına Uyum", ["Tam Uydum", "Kısmen Uydum", "Uymadım"])

    if bitis.hour >= 23 or bitis.hour < 5:
        st.warning("⚠️ **Geç Saat Uyarısı:** Gece geç saatlerde çalışmak verimi düşürebilir!")

    if st.button("💾 Günlük Dersi ve Süreyi Kaydet", type="primary"):
        ogr_data["calisma"].append({
            "Tarih": tarih, "Ders": ders, "Konu": konu, "Süre (dk)": sure_dk,
            "Doğru": dogru, "Yanlış": yanlis, "Boş": bos, "Çözülen": dogru + yanlis + bos,
            "Hata Sebebi": hata_sebebi, "Çözüme Bakıldı": yapilamayana_bakildi, "Programa Uyum": programa_riayet
        })
        st.success("✅ Veri başarıyla kaydedildi!")

# ----------------------------------------------------
# TAB 2: DENEME SINAVLARI VE SADELEŞTİRİLMİŞ HEDEF NETLER (6 DERS)
# ----------------------------------------------------
with tab2:
    st.header("🎯 LGS Deneme Netleri ve 6 Ana Ders Hedef Kıyaslaması")
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        deneme_adi = st.text_input("Deneme Sınavı / Yayın Adı", "Kurumsal LGS Denemesi - 1")
    with col_d2:
        deneme_tarihi = st.date_input("Deneme Tarihi", datetime.date.today())
    
    st.subheader("📝 6 Ana Ders Netlerinizi Giriniz:")
    net_girisleri = {}
    cols = st.columns(3)
    idx = 0
    for d_ana in ANA_LGS_DERSLERI:
        with cols[idx % 3]:
            net_girisleri[d_ana] = st.number_input(f"{d_ana} Net", 0.0, 20.0, 15.0, step=0.33)
        idx += 1

    st.divider()
    st.subheader("📊 Hedef Net vs. Gerçekleşen Net Kıyaslaması")
    
    kiyas_data = []
    for d_ana, g_net in net_girisleri.items():
        h_net = ogr_data["hedef_netler"].get(d_ana, 15.0)
        durum = "✅ Hedefe Ulaşıldı" if g_net >= h_net else f"⚠️ {h_net - g_net:.2f} Net Eksik"
        kiyas_data.append({"Ders": d_ana, "Hedef Net": h_net, "Gerçekleşen Net": g_net, "Durum": durum})
    
    st.dataframe(pd.DataFrame(kiyas_data), use_container_width=True)

    if st.button("📊 Deneme Sonucunu Kaydet", type="primary"):
        ogr_data["deneme"].append({"Tarih": deneme_tarihi, "Deneme": deneme_adi, **net_girisleri})
        st.success("Deneme netleri kaydedildi!")

# ----------------------------------------------------
# TAB 3: MEB ÖRNEK SORULARI & ÇIKMIŞlar
# ----------------------------------------------------
with tab3:
    st.header("📚 MEB Soruları ve Çıkmış Soru Kontrol Listesi")
    for ders_adi in ANA_LGS_DERSLERI:
        with st.expander(f"📌 {ders_adi}"):
            st.checkbox(f"{ders_adi} - MEB Örnek Sorularını Çözdüm")
            st.checkbox(f"{ders_adi} - LGS Çıkmış Soruları Çözdüm")

# ----------------------------------------------------
# TAB 4: KİTAP OKUMA & ÖZ DEĞERLENDİRME
# ----------------------------------------------------
with tab4:
    st.header("📖 Kitap Okuma Takibi ve Öz Değerlendirme")
    col_k1, col_k2 = st.columns(2)
    with col_k1:
        kitap_adi = st.text_input("Kitap Adı", "Şeker Portakalı")
    with col_k2:
        okunan_sayfa = st.number_input("Haftalık Okunan Sayfa Sayısı", min_value=0, value=75)
    st.text_area("Haftalık Öz Değerlendirmeniz:", "Bu hafta matematik çalışmalarım verimli geçti...")

# ----------------------------------------------------
# TAB 5: VELİ VE KOÇ ANALİZ PANELİ
# ----------------------------------------------------
with tab5:
    st.header(f"👨‍👩‍👧 {aktif_ogr} - Veli ve Koç İlerleme Paneli")
    
    if len(ogr_data["calisma"]) > 0:
        df_calisma = pd.DataFrame(ogr_data["calisma"])
        
        st.subheader("⏱️ Çalışma Süresi Analizi")
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Toplam Çalışma Süresi", f"{df_calisma['Süre (dk)'].sum() / 60:.1f} Saat")
        col_m2.metric("Toplam Çözülen Soru", f"{df_calisma['Çözülen'].sum()} Soru")
        
        fig_sure = px.pie(df_calisma, values="Süre (dk)", names="Ders", title="Derslere Göre Zaman Dağılımı")
        st.plotly_chart(fig_sure, use_container_width=True)
    else:
        st.info("İncelemek için lütfen 'Günlük Veri Girişi' sekmesinden veri kaydedin.")

# ----------------------------------------------------
# TAB 6: PROGRAM & KOÇ LİSANS YÖNETİMİ
# ----------------------------------------------------
with tab6:
    st.header("⚙️ Program ve Koç Yönetim Paneli")
    
    st.subheader(f"🎯 6 Ana Ders İçin Hedef Netleri Düzenle ({aktif_ogr})")
    cols_h = st.columns(3)
    i = 0
    for d_ana in ANA_LGS_DERSLERI:
        with cols_h[i % 3]:
            ogr_data["hedef_netler"][d_ana] = st.number_input(
                f"{d_ana} Hedef Net", 0.0, 20.0, ogr_data["hedef_netler"].get(d_ana, 15.0)
            )
        i += 1

    st.divider()
    if st.session_state["user_role"] == "Koç":
        st.subheader("💬 Öğrenciye Özel Motivasyon Mesajı Güncelle")
        yeni_soz = st.text_input("Mesaj:", ogr_data["ozlu_soz"])
        if st.button("Mesajı Güncelle"):
            ogr_data["ozlu_soz"] = yeni_soz
            st.success("Güncellendi!")

        st.divider()
        with st.expander("🔒 Diğer Koçların Lisans / Ödeme Durumu (Sadece Ana Koç)"):
            for koc, durum in st.session_state["koc_lisans_durumu"].items():
                st.session_state["koc_lisans_durumu"][koc] = st.checkbox(f"{koc} - Ödeme Yapıldı / Aktif", value=durum)
