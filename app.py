import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# 1. SAYFA YAPILANDIRMASI VE ŞIK STİL (CUSTOM CSS)
st.set_page_config(page_title="ŞAHİN MATH CHECK-UP KOÇLUK AKADEMİSİ", layout="wide", page_icon="🦅")

st.markdown("""
<style>
    .main-title {
        font-size: 2.3rem;
        color: #1E3A8A;
        text-align: center;
        font-weight: 800;
        margin-bottom: 5px;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #4B5563;
        text-align: center;
        margin-bottom: 25px;
    }
    .login-card {
        background-color: #F8FAFC;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# 2. LGS MÜFREDATI VE AKILLI AYRIMLAR
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

# 3. VERİTABANI İLKLEME (SESSION STATE)
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None

if "koclar" not in st.session_state:
    st.session_state["koclar"] = {
        "koc1": {"ad": "Ahmet Hoca", "sifre": "koc123", "lisans": True},
        "koc2": {"ad": "Mehmet Hoca", "sifre": "koc123", "lisans": False}
    }

if "ogrenciler" not in st.session_state:
    st.session_state["ogrenciler"] = {
        "ali": {
            "ad": "Ali Yılmaz", "sifre": "1234", "koc_id": "koc1",
            "calisma": [], "deneme": [], "kitap_ozdegerlendirme": [],
            "hedef_netler": {"Türkçe": 18.0, "Matematik": 15.0, "Fen Bilimleri": 18.0, "T.C. İnkılap Tarihi": 9.0, "Din Kültürü ve A.B.": 10.0, "İngilizce": 9.0},
            "ozlu_soz": "Başarı, her gün tekrarlanan küçük çabaların toplamıdır!"
        },
        "zeynep": {
            "ad": "Zeynep Kaya", "sifre": "1234", "koc_id": "koc1",
            "calisma": [], "deneme": [], "kitap_ozdegerlendirme": [],
            "hedef_netler": {"Türkçe": 19.0, "Matematik": 17.0, "Fen Bilimleri": 19.0, "T.C. İnkılap Tarihi": 10.0, "Din Kültürü ve A.B.": 10.0, "İngilizce": 10.0},
            "ozlu_soz": "İnanmak, başarmanın yarısıdır!"
        }
    }

# ----------------------------------------------------
# 4. ŞIK KARŞILAMA VE GİRİŞ EKRANI
# ----------------------------------------------------
if not st.session_state["logged_in"]:
    st.markdown('<div class="main-title">🦅 ŞAHİN MATH CHECK-UP KOÇLUK AKADEMİSİ</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">LGS Başarı & Performans Takip Sistemi</div>', unsafe_allow_html=True)
    
    col_cen, col_box, col_cen2 = st.columns([1, 2, 1])
    
    with col_box:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        rol_secim = st.radio("🔑 Giriş Türünü Seçiniz:", ["👨‍🎓 Öğrenci Girişi", "👨‍🏫 Koç Girişi", "👑 Ana Yönetici Girişi"], horizontal=True)
        st.divider()
        
        if rol_secim == "👨‍🎓 Öğrenci Girişi":
            usr = st.text_input("Kullanıcı Adı (Örn: ali, zeynep):", key="in_stud_usr").strip().lower()
            pwd = st.text_input("Şifre:", type="password", key="in_stud_pwd")
            if st.button("🚀 Öğrenci Olarak Giriş Yap", type="primary", use_container_width=True):
                if usr in st.session_state["ogrenciler"] and st.session_state["ogrenciler"][usr]["sifre"] == pwd:
                    st.session_state["logged_in"] = True
                    st.session_state["user_role"] = "Öğrenci"
                    st.session_state["current_user"] = usr
                    st.rerun()
                else:
                    st.error("Hatalı Kullanıcı Adı veya Şifre!")
                    
        elif rol_secim == "👨‍🏫 Koç Girişi":
            usr = st.text_input("Koç Kullanıcı Adı (Örn: koc1):", key="in_koc_usr").strip().lower()
            pwd = st.text_input("Şifre:", type="password", key="in_koc_pwd")
            if st.button("🚀 Koç Olarak Giriş Yap", type="primary", use_container_width=True):
                if usr in st.session_state["koclar"] and st.session_state["koclar"][usr]["sifre"] == pwd:
                    st.session_state["logged_in"] = True
                    st.session_state["user_role"] = "Koç"
                    st.session_state["current_user"] = usr
                    st.rerun()
                else:
                    st.error("Hatalı Koç Kullanıcı Adı veya Şifre!")

        elif rol_secim == "👑 Ana Yönetici Girişi":
            pwd = st.text_input("Yönetici Şifresi:", type="password", key="in_admin_pwd")
            if st.button("🚀 Yönetici Olarak Giriş Yap", type="primary", use_container_width=True):
                if pwd == "admin123":
                    st.session_state["logged_in"] = True
                    st.session_state["user_role"] = "Ana Yönetici"
                    st.session_state["current_user"] = "admin"
                    st.rerun()
                else:
                    st.error("Hatalı Yönetici Şifresi!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ----------------------------------------------------
# 5. OTURUM YÖNETİMİ & KULLANICI SEÇİMİ
# ----------------------------------------------------
role = st.session_state["user_role"]
curr_usr = st.session_state["current_user"]

if "selected_student_id" not in st.session_state:
    st.session_state["selected_student_id"] = None

if role == "Öğrenci":
    active_stud_id = curr_usr
elif role in ["Koç", "Ana Yönetici"]:
    filtre_ogrenciler = {k: v for k, v in st.session_state["ogrenciler"].items() if v["koc_id"] == curr_usr} if role == "Koç" else st.session_state["ogrenciler"]
    if len(filtre_ogrenciler) > 0:
        if st.session_state["selected_student_id"] not in filtre_ogrenciler:
            st.session_state["selected_student_id"] = list(filtre_ogrenciler.keys())[0]
        active_stud_id = st.session_state["selected_student_id"]
    else:
        active_stud_id = None

# ----------------------------------------------------
# 6. YAN MENÜ (SIDEBAR) & ŞİFRE DEĞİŞTİRME
# ----------------------------------------------------
with st.sidebar:
    st.markdown("### 🦅 ŞAHİN MATH CHECK-UP")
    st.caption("Koçluk Akademisi")
    st.info(f"👤 **Oturum:** {role}")
    
    if role == "Ana Yönetici":
        st.success("👑 **Süper Admin**")
        if len(st.session_state["ogrenciler"]) > 0:
            st.session_state["selected_student_id"] = st.selectbox(
                "İncelenen Öğrenci:", list(st.session_state["ogrenciler"].keys()),
                format_func=lambda x: f"{st.session_state['ogrenciler'][x]['ad']} ({x})"
            )
    elif role == "Koç":
        koc_adi = st.session_state["koclar"][curr_usr]["ad"]
        st.markdown(f"**Koç:** {koc_adi}")
        if len(filtre_ogrenciler) > 0:
            st.session_state["selected_student_id"] = st.selectbox(
                "Öğrenciniz:", list(filtre_ogrenciler.keys()),
                format_func=lambda x: f"{filtre_ogrenciler[x]['ad']} ({x})"
            )
    elif role == "Öğrenci":
        st.markdown(f"**Öğrenci:** {st.session_state['ogrenciler'][active_stud_id]['ad']}")

    st.divider()
    
    # ŞİFRE DEĞİŞTİRME EXPANDER
    with st.expander("🔑 Şifremi Değiştir"):
        yeni_pass = st.text_input("Yeni Şifreniz:", type="password", key="side_new_pass")
        if st.button("Şifreyi Güncelle"):
            if yeni_pass:
                if role == "Öğrenci":
                    st.session_state["ogrenciler"][curr_usr]["sifre"] = yeni_pass
                elif role == "Koç":
                    st.session_state["koclar"][curr_usr]["sifre"] = yeni_pass
                st.success("Şifreniz güncellendi!")

    if active_stud_id and active_stud_id in st.session_state["ogrenciler"]:
        ogr_obj = st.session_state["ogrenciler"][active_stud_id]
        st.divider()
        st.warning(f"💡 **Motivasyon Notu:**\n\n_{ogr_obj['ozlu_soz']}_")

    st.divider()
    if st.button("🚪 Çıkış Yap", type="secondary", use_container_width=True):
        st.session_state["logged_in"] = False
        st.session_state["user_role"] = None
        st.session_state["current_user"] = None
        st.rerun()

# ----------------------------------------------------
# 7. SEKMELER
# ----------------------------------------------------
tab_names = ["📝 Günlük Veri & Süre Girişi", "📊 Deneme & Konu Hataları", "📚 MEB & Çıkmışlar", "📖 Kitap & Öz Değerlendirme", "👨‍👩‍👧 Veli & Koç Analiz"]
if role in ["Koç", "Ana Yönetici"]:
    tab_names.append("⚙️ Yönetim Paneli")

tabs = st.tabs(tab_names)

if not active_stud_id and role != "Ana Yönetici":
    st.warning("İşlem yapmak için tanımlı bir öğrenci gereklidir.")
    st.stop()

# ----------------------------------------------------
# TAB 1: GÜNLÜK VERİ & DERS BAZLI SÜRE GİRİŞİ
# ----------------------------------------------------
with tabs[0]:
    if active_stud_id:
        ogr_obj = st.session_state["ogrenciler"][active_stud_id]
        st.header(f"Günlük Ders Çalışma ve Süre Girişi ({ogr_obj['ad']})")
        st.caption("Her ders ve konu için harcadığınız süreyi ve soru sayılarını ayrı ayrı kaydedebilirsiniz.")
        
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

        st.subheader("⏰ Çalışma Saat Aralığı")
        col_s1, col_s2, col_riayet = st.columns(3)
        with col_s1:
            baslangic = st.time_input("Başlangıç Saati", datetime.time(16, 0))
        with col_s2:
            bitis = st.time_input("Bitiş Saati", datetime.time(18, 0))
        with col_riayet:
            programa_riayet = st.selectbox("Program Uyum", ["Tam Uydum", "Kısmen Uydum", "Uymadım"])

        if bitis.hour >= 23 or bitis.hour < 5:
            st.warning("⚠️ **Geç Saat Uyarısı:** Gece geç saatlerde çalışmak verimi düşürebilir!")

        if st.button("💾 Günlük Dersi ve Süreyi Kaydet", type="primary"):
            ogr_obj["calisma"].append({
                "Tarih": tarih, "Ders": ders, "Konu": konu, "Süre (dk)": sure_dk,
                "Doğru": dogru, "Yanlış": yanlis, "Boş": bos, "Çözülen": dogru + yanlis + bos,
                "Hata Sebebi": hata_sebebi, "Çözüme Bakıldı": yapilamayana_bakildi, "Programa Uyum": programa_riayet
            })
            st.success(f"✅ {ders} - {konu} çalışması ({sure_dk} dk) başarıyla kaydedildi!")

# ----------------------------------------------------
# TAB 2: DENEME SINAVLARI VE KONU BAZLI HATA İŞARETLEME
# ----------------------------------------------------
with tabs[1]:
    if active_stud_id:
        ogr_obj = st.session_state["ogrenciler"][active_stud_id]
        st.header(f"🎯 LGS Deneme Netleri ve Konu Hataları ({ogr_obj['ad']})")
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            deneme_adi = st.text_input("Deneme Sınavı / Yayın Adı", "Kurumsal LGS Denemesi - 1")
        with col_d2:
            deneme_tarihi = st.date_input("Deneme Tarihi", datetime.date.today())
        
        st.subheader("📝 6 Ana Ders Netleri:")
        net_girisleri = {}
        cols = st.columns(3)
        idx = 0
        for d_ana in ANA_LGS_DERSLERI:
            with cols[idx % 3]:
                net_girisleri[d_ana] = st.number_input(f"{d_ana} Net", 0.0, 20.0, 15.0, step=0.33)
            idx += 1

        st.divider()
        st.subheader("📌 Denemedeki Yanlış / Boş Soruların Konu Dağılımı")
        st.caption("Hangi konudan kaç yanlış veya boş yaptığınızı seçiniz (Örn: 1 Yanlış Çarpanlar ve Katlar)")
        
        if "temp_deneme_hatalari" not in st.session_state:
            st.session_state["temp_deneme_hatalari"] = []

        col_h1, col_h2, col_h3, col_h4 = st.columns([2, 2, 1, 1])
        with col_h1:
            h_ders = st.selectbox("Ders Seç:", list(LGS_MUSERFAT.keys()), key="dh_ders")
        with col_h2:
            h_konu = st.selectbox("Konu Seç:", LGS_MUSERFAT[h_ders], key="dh_konu")
        with col_h3:
            h_yanlis = st.number_input("Yanlış", 0, 20, 1, key="dh_y")
        with col_h4:
            h_bos = st.number_input("Boş", 0, 20, 0, key="dh_b")

        if st.button("➕ Konu Hatasını Ekle"):
            st.session_state["temp_deneme_hatalari"].append({"Ders": h_ders, "Konu": h_konu, "Yanlış": h_yanlis, "Boş": h_bos})
            st.success("Konu hatası eklendi!")

        if len(st.session_state["temp_deneme_hatalari"]) > 0:
            st.table(pd.DataFrame(st.session_state["temp_deneme_hatalari"]))

        st.divider()
        if st.button("📊 Deneme Sınavını ve Konu Hatalarını Kaydet", type="primary"):
            ogr_obj["deneme"].append({
                "Tarih": deneme_tarihi, "Deneme": deneme_adi, 
                "Netler": net_girisleri, "KonuHatalari": st.session_state["temp_deneme_hatalari"]
            })
            st.session_state["temp_deneme_hatalari"] = []
            st.success("Deneme sınavı ve konu detayları başarıyla kaydedildi!")

# ----------------------------------------------------
# TAB 3: MEB & ÇIKMIŞLAR
# ----------------------------------------------------
with tabs[2]:
    st.header("📚 MEB Soruları ve Çıkmış Soru Kontrolü")
    for ders_adi in ANA_LGS_DERSLERI:
        with st.expander(f"📌 {ders_adi}"):
            st.checkbox(f"{ders_adi} - MEB Örnek Sorularını Çözdüm")
            st.checkbox(f"{ders_adi} - LGS Çıkmış Soruları Çözdüm")

# ----------------------------------------------------
# TAB 4: KİTAP OKUMA & HAFTALIK ÖZ DEĞERLENDİRME (KAYDET BUTONLU)
# ----------------------------------------------------
with tabs[3]:
    if active_stud_id:
        ogr_obj = st.session_state["ogrenciler"][active_stud_id]
        st.header(f"📖 Kitap Okuma Takibi ve Öz Değerlendirme ({ogr_obj['ad']})")
        
        col_k1, col_k2, col_k3 = st.columns(3)
        with col_k1:
            hafta_tarih = st.date_input("Hafta / Tarih Seçimi", datetime.date.today())
        with col_k2:
            kitap_adi = st.text_input("Okunan Kitap Adı", "Şeker Portakalı")
        with col_k3:
            okunan_sayfa = st.number_input("Haftalık Okunan Sayfa Sayısı", min_value=0, value=75)

        ogrenci_notu = st.text_area(
            "Haftalık Öz Değerlendirme Notunuz (Bu hafta ne durumdaydınız?):",
            "Bu hafta matematik yeni nesil sorularında gelişim sağladım, hedef okuma sayfamı tamamladım..."
        )

        if st.button("💾 Kitap & Öz Değerlendirmeyi Kaydet", type="primary"):
            ogr_obj["kitap_ozdegerlendirme"].append({
                "Tarih": hafta_tarih, "Kitap": kitap_adi, "Sayfa": okunan_sayfa, "Not": ogrenci_notu
            })
            st.success("✅ Haftalık kitap okuma ve öz değerlendirmeniz başarıyla kaydedildi!")

        if len(ogr_obj["kitap_ozdegerlendirme"]) > 0:
            st.divider()
            st.subheader("📜 Geçmiş Değerlendirme Kayıtları")
            st.dataframe(pd.DataFrame(ogr_obj["kitap_ozdegerlendirme"]), use_container_width=True)

# ----------------------------------------------------
# TAB 5: VELİ VE KOÇ ANALİZ PANELİ
# ----------------------------------------------------
with tabs[4]:
    if active_stud_id:
        ogr_obj = st.session_state["ogrenciler"][active_stud_id]
        st.header(f"👨‍👩‍👧 {ogr_obj['ad']} - İlerleme ve Süre Analiz Paneli")
        
        if len(ogr_obj["calisma"]) > 0:
            df_calisma = pd.DataFrame(ogr_obj["calisma"])
            st.subheader("⏱️ Çalışma Süresi Analizi")
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("Toplam Çalışma Süresi", f"{df_calisma['Süre (dk)'].sum() / 60:.1f} Saat")
            col_m2.metric("Toplam Çözülen Soru", f"{df_calisma['Çözülen'].sum()} Soru")
            
            fig_sure = px.pie(df_calisma, values="Süre (dk)", names="Ders", title="Derslere Göre Zaman Dağılımı")
            st.plotly_chart(fig_sure, use_container_width=True)
        else:
            st.info("İncelemek için lütfen 'Günlük Veri & Süre Girişi' sekmesinden veri kaydedin.")

# ----------------------------------------------------
# TAB 6: YÖNETİM PANELİ (KOÇ VE ADMİN)
# ----------------------------------------------------
if role in ["Koç", "Ana Yönetici"]:
    with tabs[5]:
        st.header("⚙️ Koç & Sistem Yönetim Merkezi")
        
        st.subheader("👨‍🎓 Öğrenci Yönetimi (Ekle / Sil / Şifre Değiştir)")
        col_oe1, col_oe2 = st.columns(2)
        
        with col_oe1:
            st.markdown("### ➕ Yeni Öğrenci Ekle")
            new_s_username = st.text_input("Kullanıcı Adı (Örn: ahmet):").strip().lower()
            new_s_fullname = st.text_input("Adı Soyadı (Örn: Ahmet Demir):")
            new_s_pass = st.text_input("Şifresi:", value="1234")
            assigned_koc = st.selectbox("Atanacak Koç:", list(st.session_state["koclar"].keys()), format_func=lambda x: st.session_state["koclar"][x]["ad"]) if role == "Ana Yönetici" else curr_usr

            if st.button("➕ Öğrenciyi Kaydet", type="primary"):
                if new_s_username and new_s_fullname:
                    if new_s_username in st.session_state["ogrenciler"]:
                        st.error("Bu kullanıcı adı zaten mevcut!")
                    else:
                        st.session_state["ogrenciler"][new_s_username] = {
                            "ad": new_s_fullname, "sifre": new_s_pass, "koc_id": assigned_koc,
                            "calisma": [], "deneme": [], "kitap_ozdegerlendirme": [],
                            "hedef_netler": {d: 15.0 for d in ANA_LGS_DERSLERI},
                            "ozlu_soz": "Başarı yolculuğun başladı!"
                        }
                        st.success(f"✅ {new_s_fullname} eklendi!")
                        st.rerun()

        with col_oe2:
            st.markdown("### 🗑️ Öğrenci Sil")
            silinecek_ogrenciler = list(filtre_ogrenciler.keys()) if role == "Koç" else list(st.session_state["ogrenciler"].keys())
            if len(silinecek_ogrenciler) > 0:
                del_s_id = st.selectbox("Silinecek Öğrenciyi Seçin:", silinecek_ogrenciler, format_func=lambda x: f"{st.session_state['ogrenciler'][x]['ad']} ({x})")
                if st.button("❌ Seçili Öğrenciyi Sil", type="secondary"):
                    del st.session_state["ogrenciler"][del_s_id]
                    st.success("Öğrenci silindi!")
                    st.rerun()

        st.divider()
        if role == "Ana Yönetici":
            st.subheader("👑 Ana Yönetici Özel Paneli: Koç Yönetimi")
            col_ke1, col_ke2 = st.columns(2)
            
            with col_ke1:
                st.markdown("### ➕ Yeni Koç Ekle")
                new_k_username = st.text_input("Koç Kullanıcı Adı (Örn: koc3):").strip().lower()
                new_k_fullname = st.text_input("Koç Adı Soyadı (Örn: Ayşe Hoca):")
                new_k_pass = st.text_input("Koç Şifresi:", value="koc123")
                
                if st.button("➕ Yeni Koç Oluştur", type="primary"):
                    if new_k_username and new_k_fullname:
                        st.session_state["koclar"][new_k_username] = {"ad": new_k_fullname, "sifre": new_k_pass, "lisans": True}
                        st.success(f"✅ Koç {new_k_fullname} eklendi!")
                        st.rerun()

            with col_ke2:
                st.markdown("### 🗑️ Koç Sil")
                del_k_id = st.selectbox("İşlem Yapılacak Koç:", list(st.session_state["koclar"].keys()), format_func=lambda x: f"{st.session_state['koclar'][x]['ad']} ({x})")
                if st.button("❌ Seçili Koçu Sil"):
                    del st.session_state["koclar"][del_k_id]
                    st.success("Koç silindi!")
                    st.rerun()
