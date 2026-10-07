import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# 1. SAYFA YAPILANDIRMASI
st.set_page_config(page_title="LGS Koçluk & Performans Sistemi", layout="wide", page_icon="🎓")

# 2. LGS MÜFREDATI VE HATA SEBEPLERİ
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

SEBEP_LISTESI = [
    "Yok / Hepsi Doğru",
    "Dikkat / İşlem Hatası",
    "Konu Bilgisi Eksik",
    "Soru Tarzını / Öncülü Anlamadım",
    "Süre Yetmedi",
    "İki Şık Arasında Kaldım / Tahmin Ettim"
]

# 3. VERİ DEPOSU (SESSION STATE)
if "calisma_verileri" not in st.session_state:
    st.session_state["calisma_verileri"] = []
if "deneme_verileri" not in st.session_state:
    st.session_state["deneme_verileri"] = []
if "meb_cikmis_durum" not in st.session_state:
    st.session_state["meb_cikmis_durum"] = {ders: {"meb": False, "cikmis": False} for ders in LGS_MUSERFAT.keys()}
if "ozlu_soz" not in st.session_state:
    st.session_state["ozlu_soz"] = "Başarı, her gün tekrarlanan küçük çabaların toplamıdır!"
if "hedef_netler" not in st.session_state:
    st.session_state["hedef_netler"] = {
        "Türkçe (Genel)": 9.0, "Türkçe (Paragraf)": 9.0,
        "Matematik (Kazanım)": 8.0, "Matematik (Yeni Nesil)": 6.0,
        "Fen Bilimleri": 17.0, "T.C. İnkılap Tarihi": 9.0,
        "Din Kültürü ve A.B.": 10.0, "İngilizce": 9.0
    }
if "koc_lisans_durumu" not in st.session_state:
    st.session_state["koc_lisans_durumu"] = {"Koç - Ahmet Hoca": True, "Koç - Mehmet Hoca": False}

# 4. YAN MENÜ (SIDEBAR)
with st.sidebar:
    st.title("🎓 LGS Koçluk Paneli")
    st.subheader("Öğrenci: Ali Yılmaz")
    st.divider()
    st.info(f"💡 **Koçtan Not:**\n\n_{st.session_state['ozlu_soz']}_")
    st.divider()
    st.markdown("### 🎯 Ders Bazlı Hedef Netler")
    for d, n in st.session_state["hedef_netler"].items():
        st.text(f"• {d}: {n} Net")

# 5. ANA EKRAN SEKME YAPISI
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📝 Günlük Veri Girişi", 
    "📊 Deneme Sınavları & Net Hedefleri", 
    "📚 MEB Soruları & Çıkmışlar", 
    "📖 Kitap Okuma & Öz Değerlendirme", 
    "👨‍👩‍👧 Veli & Koç Analiz Paneli",
    "⚙️ Program & Koç Yönetimi"
])

# ----------------------------------------------------
# TAB 1: GÜNLÜK VERİ GİRİŞİ (SÜRE VE KONU DETAYLI)
# ----------------------------------------------------
with tab1:
    st.header("📌 Günlük Ders Çalışma, Süre ve Yanlış/Boş Girişi")
    st.caption("Çalıştığınız her ders ve konu için sürenizi, doğru, yanlış ve boş sayılarınızı giriniz.")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        tarih = st.date_input("Çalışma Tarihi", datetime.date.today())
        ders = st.selectbox("Çalışılan Ders", list(LGS_MUSERFAT.keys()))
        konu = st.selectbox("Çalışılan Konu", LGS_MUSERFAT[ders])
        sure_dk = st.number_input("Bu Derse Harcanan Süre (Dakika)", min_value=5, max_value=300, value=45, step=5)
    
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

    # AKILLI UYARILAR
    if bitis.hour >= 23 or bitis.hour < 5:
        st.warning("⚠️ **Geç Saat Uyarısı:** Bitiş saatiniz gece geç saatlere denk geliyor! Zihinsel verim düşebilir, çalışma saatlerinizi öne çekiniz.")
    
    cozulen_toplam = dogru + yanlis + bos
    hedef_gunluk_soru = 120
    if cozulen_toplam < hedef_gunluk_soru:
        eksik = hedef_gunluk_soru - cozulen_toplam
        st.info(f"💡 **Otomatik Telafi:** Bugün hedeflenen soru sayısının {eksik} soru altında kaldın. Önümüzdeki 3 gün boyunca günlük fazladan +{int(eksik/3)+1} soru çözerek bu eksiği kapatabilirsin.")

    if st.button("💾 Günlük Dersi ve Süreyi Kaydet", type="primary"):
        st.session_state["calisma_verileri"].append({
            "Tarih": tarih, "Ders": ders, "Konu": konu, "Süre (dk)": sure_dk,
            "Doğru": dogru, "Yanlış": yanlis, "Boş": bos, "Çözülen": cozulen_toplam,
            "Hata Sebebi": hata_sebebi, "Çözüme Bakıldı": yapilamayana_bakildi, "Programa Uyum": programa_riayet
        })
        st.success(f"✅ {ders} - {konu} çalışması ({sure_dk} dk) başarıyla kaydedildi!")

# ----------------------------------------------------
# TAB 2: DENEME SINAVLARI VE DERS DERS NET HEDEFLERİ
# ----------------------------------------------------
with tab2:
    st.header("🎯 LGS Deneme Netleri ve Ders Hedef Kıyaslaması")
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        deneme_adi = st.text_input("Deneme Sınavı / Yayın Adı", "Kurumsal LGS Denemesi - 1")
    with col_d2:
        deneme_tarihi = st.date_input("Deneme Tarihi", datetime.date.today())
    
    st.subheader("📝 Ders Netlerinizi Giriniz:")
    net_girisleri = {}
    cols = st.columns(4)
    idx = 0
    for ders_adi in LGS_MUSERFAT.keys():
        with cols[idx % 4]:
            net_girisleri[ders_adi] = st.number_input(f"{ders_adi} Net", 0.0, 20.0, 8.0, step=0.33)
        idx += 1

    st.divider()
    st.subheader("📊 Hedef Net vs. Gerçekleşen Net Kıyaslaması")
    
    kiyas_data = []
    for d_adi, g_net in net_girisleri.items():
        h_net = st.session_state["hedef_netler"].get(d_adi, 0.0)
        durum = "✅ Hedefe Ulaşıldı" if g_net >= h_net else f"⚠️ {h_net - g_net:.2f} Net Eksik"
        kiyas_data.append({"Ders": d_adi, "Hedef Net": h_net, "Gerçekleşen Net": g_net, "Durum": durum})
    
    df_kiyas = pd.DataFrame(kiyas_data)
    st.dataframe(df_kiyas, use_container_width=True)

    if st.button("📊 Deneme Sonucunu Kaydet", type="primary"):
        st.session_state["deneme_verileri"].append({"Tarih": deneme_tarihi, "Deneme": deneme_adi, **net_girisleri})
        st.success("Deneme netleri başarıyla kaydedildi!")

# ----------------------------------------------------
# TAB 3: MEB ÖRNEK SORULARI & ÇIKMIŞ SORULAR
# ----------------------------------------------------
with tab3:
    st.header("📚 MEB Soruları ve Çıkmış Soru Kontrol Listesi")
    for ders_adi in LGS_MUSERFAT.keys():
        with st.expander(f"📌 {ders_adi}"):
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.session_state["meb_cikmis_durum"][ders_adi]["meb"] = st.checkbox(
                    f"{ders_adi} - MEB Örnek Sorularını Çözdüm", 
                    value=st.session_state["meb_cikmis_durum"][ders_adi]["meb"]
                )
            with col_m2:
                st.session_state["meb_cikmis_durum"][ders_adi]["cikmis"] = st.checkbox(
                    f"{ders_adi} - LGS Çıkmış Soruları Çözdüm", 
                    value=st.session_state["meb_cikmis_durum"][ders_adi]["cikmis"]
                )

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
        
    ogrenci_notu = st.text_area(
        "Haftalık Öz Değerlendirmeniz (Zorlandığınız noktalar, hissettikleriniz):",
        "Bu hafta matematik yeni nesil sorularında biraz zorlandım..."
    )
    if st.button("Öz Değerlendirmeyi Kaydet"):
        st.success("Haftalık değerlendirmeniz kaydedildi.")

# ----------------------------------------------------
# TAB 5: VELİ VE KOÇ ANALİZ PANELİ (SÜRE ANALİZLİ)
# ----------------------------------------------------
with tab5:
    st.header("👨‍👩‍👧 Veli ve Koç İlerleme ve Süre Analiz Paneli")
    
    if len(st.session_state["calisma_verileri"]) > 0:
        df_calisma = pd.DataFrame(st.session_state["calisma_verileri"])
        
        # 1. ÇALIŞMA SÜRELERİ ANALİZİ (YENİ EKLEME)
        st.subheader("⏱️ Ders Çalışma Süreleri Analizi")
        toplam_dakika = df_calisma["Süre (dk)"].sum()
        toplam_saat = toplam_dakika / 60
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Toplam Çalışma Süresi", f"{toplam_saat:.1f} Saat ({toplam_dakika} dk)")
        col_m2.metric("Toplam Çözülen Soru", f"{df_calisma['Çözülen'].sum()} Soru")
        col_m3.metric("Ortalama Soru Başına Süre", f"{(toplam_dakika / max(1, df_calisma['Çözülen'].sum())):.1f} dk/soru")
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            fig_sure_ders = px.pie(df_calisma, values="Süre (dk)", names="Ders", title="Derslere Göre Zaman Dağılımı (Dakika)")
            st.plotly_chart(fig_sure_ders, use_container_width=True)
        with col_g2:
            fig_sure_bar = px.bar(df_calisma, x="Ders", y="Süre (dk)", color="Ders", title="Ders Bazlı Toplam Çalışma Süresi")
            st.plotly_chart(fig_sure_bar, use_container_width=True)
            
        st.divider()

        # 2. HATA SEBEBİ VE KONU DETAYLARI
        st.subheader("🎯 Konu Bazlı Hata Sebepleri Dağılımı")
        df_hata = df_calisma[df_calisma["Hata Sebebi"] != "Yok / Hepsi Doğru"]
        if len(df_hata) > 0:
            fig_hata = px.pie(df_hata, names="Hata Sebebi", title="Yanlış ve Boş Bırakma Nedenleri")
            st.plotly_chart(fig_hata, use_container_width=True)
            st.dataframe(df_hata[["Tarih", "Ders", "Konu", "Yanlış", "Boş", "Hata Sebebi"]], use_container_width=True)
        else:
            st.info("Henüz kaydedilmiş hata sebebi bulunmuyor.")
            
    else:
        st.info("Grafiklerin ve süre analizlerinin oluşması için lütfen 'Günlük Veri Girişi' sekmesinden veri kaydedin.")

# ----------------------------------------------------
# TAB 6: PROGRAM & KOÇ YÖNETİMİ
# ----------------------------------------------------
with tab6:
    st.header("⚙️ Program ve Koç Yönetim Paneli")
    
    st.subheader("🎯 Ders Bazlı Hedef Netleri Düzenle")
    cols_h = st.columns(4)
    i = 0
    for d_adi in LGS_MUSERFAT.keys():
        with cols_h[i % 4]:
            st.session_state["hedef_netler"][d_adi] = st.number_input(
                f"{d_adi} Hedef", 0.0, 20.0, st.session_state["hedef_netler"].get(d_adi, 8.0)
            )
        i += 1
        
    st.divider()
    
    with st.expander("🔒 Sadece Ana Koç / Yönetici Paneli (Diğer Koçların Lisans Durumları)"):
        st.caption("Bu alanı sadece sistem sahibi koç diğer koçların ödeme durumunu kontrol etmek için kullanır.")
        for koc, durum in st.session_state["koc_lisans_durumu"].items():
            yeni_durum = st.checkbox(f"{koc} - Ücreti Ödendi / Lisans Aktif", value=durum)
            st.session_state["koc_lisans_durumu"][koc] = yeni_durum
