import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# 1. SAYFA YAPILANDIRMASI
st.set_page_config(page_title="LGS Koçluk & Performans Portalı", layout="wide", page_icon="🎓")

# 2. LGS MÜFREDATI
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

# KOÇ VERİTABANI
if "koclar" not in st.session_state:
    st.session_state["koclar"] = {
        "koc1": {"ad": "Ahmet Hoca", "sifre": "koc123", "lisans": True},
        "koc2": {"ad": "Mehmet Hoca", "sifre": "koc123", "lisans": False}
    }

# ÖĞRENCİ VERİTABANI
if "ogrenciler" not in st.session_state:
    st.session_state["ogrenciler"] = {
        "ali": {
            "ad": "Ali Yılmaz", "sifre": "1234", "koc_id": "koc1",
            "calisma": [], "deneme": [],
            "hedef_netler": {"Türkçe": 18.0, "Matematik": 15.0, "Fen Bilimleri": 18.0, "T.C. İnkılap Tarihi": 9.0, "Din Kültürü ve A.B.": 10.0, "İngilizce": 9.0},
            "ozlu_soz": "Başarı, her gün tekrarlanan küçük çabaların toplamıdır!"
        },
        "zeynep": {
            "ad": "Zeynep Kaya", "sifre": "1234", "koc_id": "koc1",
            "calisma": [], "deneme": [],
            "hedef_netler": {"Türkçe": 19.0, "Matematik": 17.0, "Fen Bilimleri": 19.0, "T.C. İnkılap Tarihi": 10.0, "Din Kültürü ve A.B.": 10.0, "İngilizce": 10.0},
            "ozlu_soz": "İnanmak, başarmanın yarısıdır!"
        }
    }

# ----------------------------------------------------
# 4. GİRIS EKRANI (LOGIN SYSTEM)
# ----------------------------------------------------
if not st.session_state["logged_in"]:
    st.title("🎓 LGS Koçluk & Performans Portalı")
    st.caption("Lütfen Giriş Türünüzü Seçiniz")
    
    rol_secim = st.radio("Giriş Türü:", ["👨‍🎓 Öğrenci Girişi", "👨‍🏫 Koç Girişi", "👑 Ana Yönetici Girişi"], horizontal=True)
    
    st.divider()
    
    if rol_secim == "👨‍🎓 Öğrenci Girişi":
        st.subheader("Öğrenci Giriş Paneli")
        usr = st.text_input("Öğrenci Kullanıcı Adı (Örn: ali, zeynep):", key="in_stud_usr")
        pwd = st.text_input("Şifre:", type="password", key="in_stud_pwd")
        if st.button("Öğrenci Olarak Giriş Yap", type="primary"):
            usr_clean = usr.strip().lower()
            if usr_clean in st.session_state["ogrenciler"] and st.session_state["ogrenciler"][usr_clean]["sifre"] == pwd:
                st.session_state["logged_in"] = True
                st.session_state["user_role"] = "Öğrenci"
                st.session_state["current_user"] = usr_clean
                st.rerun()
            else:
                st.error("Hatalı Kullanıcı Adı veya Şifre!")
                
    elif rol_secim == "👨‍🏫 Koç Girişi":
        st.subheader("Koç Giriş Paneli")
        usr = st.text_input("Koç Kullanıcı Adı (Örn: koc1, koc2):", key="in_koc_usr")
        pwd = st.text_input("Şifre:", type="password", key="in_koc_pwd")
        if st.button("Koç Olarak Giriş Yap", type="primary"):
            usr_clean = usr.strip().lower()
            if usr_clean in st.session_state["koclar"] and st.session_state["koclar"][usr_clean]["sifre"] == pwd:
                st.session_state["logged_in"] = True
                st.session_state["user_role"] = "Koç"
                st.session_state["current_user"] = usr_clean
                st.rerun()
            else:
                st.error("Hatalı Koç Kullanıcı Adı veya Şifre!")

    elif rol_secim == "👑 Ana Yönetici Girişi":
        st.subheader("Ana Yönetici (Süper Admin) Girişi")
        pwd = st.text_input("Yönetici Şifreniz:", type="password", key="in_admin_pwd")
        if st.button("Yönetici Olarak Giriş Yap", type="primary"):
            if pwd == "admin123":
                st.session_state["logged_in"] = True
                st.session_state["user_role"] = "Ana Yönetici"
                st.session_state["current_user"] = "admin"
                st.rerun()
            else:
                st.error("Hatalı Yönetici Şifresi! (Varsayılan: admin123)")
    st.stop()

# ----------------------------------------------------
# 5. AKTİF KULLANICI VE ÖĞRENCİ BELİRLEME
# ----------------------------------------------------
role = st.session_state["user_role"]
curr_usr = st.session_state["current_user"]

# Yan menüde seçilen öğrenciyi takip etmek için
if "selected_student_id" not in st.session_state:
    st.session_state["selected_student_id"] = None

# Yetkiye göre öğrenci belirleme
if role == "Öğrenci":
    active_stud_id = curr_usr
elif role in ["Koç", "Ana Yönetici"]:
    # Koç ise sadece kendi öğrencileri, Admin ise tüm öğrenciler
    if role == "Koç":
        filtre_ogrenciler = {k: v for k, v in st.session_state["ogrenciler"].items() if v["koc_id"] == curr_usr}
    else:
        filtre_ogrenciler = st.session_state["ogrenciler"]
        
    if len(filtre_ogrenciler) > 0:
        if st.session_state["selected_student_id"] not in filtre_ogrenciler:
            st.session_state["selected_student_id"] = list(filtre_ogrenciler.keys())[0]
        active_stud_id = st.session_state["selected_student_id"]
    else:
        active_stud_id = None

# ----------------------------------------------------
# 6. YAN MENÜ (SIDEBAR)
# ----------------------------------------------------
with st.sidebar:
    st.title("🎓 LGS Koçluk Paneli")
    st.info(f"👤 **Oturum:** {role}")
    
    if role == "Ana Yönetici":
        st.success("👑 **Süper Admin Modu Aktif**")
        if len(st.session_state["ogrenciler"]) > 0:
            s_list = list(st.session_state["ogrenciler"].keys())
            st.session_state["selected_student_id"] = st.selectbox(
                "İncelenen Öğrenci:", s_list, 
                format_func=lambda x: f"{st.session_state['ogrenciler'][x]['ad']} ({x})"
            )
        else:
            st.warning("Sistemde kayıtlı öğrenci yok.")

    elif role == "Koç":
        koc_adi = st.session_state["koclar"][curr_usr]["ad"]
        st.markdown(f"**Koç:** {koc_adi}")
        if len(filtre_ogrenciler) > 0:
            s_list = list(filtre_ogrenciler.keys())
            st.session_state["selected_student_id"] = st.selectbox(
                "Öğrencinizi Seçiniz:", s_list, 
                format_func=lambda x: f"{filtre_ogrenciler[x]['ad']} ({x})"
            )
        else:
            st.warning("Size atanmış öğrenci bulunmuyor.")

    elif role == "Öğrenci":
        st.markdown(f"**Öğrenci:** {st.session_state['ogrenciler'][active_stud_id]['ad']}")

    st.divider()
    if active_stud_id and active_stud_id in st.session_state["ogrenciler"]:
        ogr_obj = st.session_state["ogrenciler"][active_stud_id]
        st.warning(f"💡 **Motivasyon Notu:**\n\n_{ogr_obj['ozlu_soz']}_")
        st.divider()
        st.markdown("### 🎯 Hedef Netler")
        for d, n in ogr_obj["hedef_netler"].items():
            st.text(f"• {d}: {n} Net")

    st.divider()
    if st.button("🚪 Çıkış Yap", type="secondary"):
        st.session_state["logged_in"] = False
        st.session_state["user_role"] = None
        st.session_state["current_user"] = None
        st.rerun()

# ----------------------------------------------------
# 7. ANA EKRAN SEKME YAPISI
# ----------------------------------------------------
tab_names = ["📝 Günlük Veri Girişi", "📊 Deneme & Netler", "📚 MEB & Çıkmışlar", "📖 Kitap & Öz Değerlendirme", "👨‍👩‍👧 Veli & Koç Analiz"]
if role in ["Koç", "Ana Yönetici"]:
    tab_names.append("⚙️ Yönetim Paneli")

tabs = st.tabs(tab_names)

# Eğer hiç öğrenci yoksa uyarı ver
if not active_stud_id and role != "Ana Yönetici":
    st.warning("İşlem yapmak için sisteme tanımlı bir öğrenci gereklidir.")
    st.stop()

# ----------------------------------------------------
# TAB 1: GÜNLÜK VERİ GİRİŞİ
# ----------------------------------------------------
with tabs[0]:
    if active_stud_id:
        ogr_obj = st.session_state["ogrenciler"][active_stud_id]
        st.header(f"📌 Günlük Çalışma ve Süre Girişi ({ogr_obj['ad']})")
        
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
            st.success("✅ Veri başarıyla kaydedildi!")

# ----------------------------------------------------
# TAB 2: DENEME SINAVLARI VE HEDEF NETLER
# ----------------------------------------------------
with tabs[1]:
    if active_stud_id:
        ogr_obj = st.session_state["ogrenciler"][active_stud_id]
        st.header(f"🎯 LGS Deneme Netleri ({ogr_obj['ad']})")
        
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
        st.subheader("📊 Hedef vs. Gerçekleşen Net Kıyaslaması")
        kiyas_data = []
        for d_ana, g_net in net_girisleri.items():
            h_net = ogr_obj["hedef_netler"].get(d_ana, 15.0)
            durum = "✅ Hedefe Ulaşıldı" if g_net >= h_net else f"⚠️ {h_net - g_net:.2f} Net Eksik"
            kiyas_data.append({"Ders": d_ana, "Hedef Net": h_net, "Gerçekleşen Net": g_net, "Durum": durum})
        
        st.dataframe(pd.DataFrame(kiyas_data), use_container_width=True)

        if st.button("📊 Deneme Sonucunu Kaydet", type="primary"):
            ogr_obj["deneme"].append({"Tarih": deneme_tarihi, "Deneme": deneme_adi, **net_girisleri})
            st.success("Deneme netleri kaydedildi!")

# ----------------------------------------------------
# TAB 3 & 4: MEB & KİTAP
# ----------------------------------------------------
with tabs[2]:
    st.header("📚 MEB Soruları ve Çıkmış Soru Kontrolü")
    for ders_adi in ANA_LGS_DERSLERI:
        with st.expander(f"📌 {ders_adi}"):
            st.checkbox(f"{ders_adi} - MEB Örnek Sorularını Çözdüm")
            st.checkbox(f"{ders_adi} - LGS Çıkmış Soruları Çözdüm")

with tabs[3]:
    st.header("📖 Kitap Okuma Takibi ve Öz Değerlendirme")
    col_k1, col_k2 = st.columns(2)
    with col_k1:
        st.text_input("Kitap Adı", "Şeker Portakalı")
    with col_k2:
        st.number_input("Haftalık Okunan Sayfa", min_value=0, value=75)
    st.text_area("Haftalık Öz Değerlendirme Notu:", "Bu hafta yeni nesil matematik sorularında gelişim sağladım...")

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
            st.info("İncelemek için lütfen 'Günlük Veri Girişi' sekmesinden veri kaydedin.")

# ----------------------------------------------------
# TAB 6: YÖNETİM PANELİ (SADECE KOÇ VE YÖNETİCİ)
# ----------------------------------------------------
if role in ["Koç", "Ana Yönetici"]:
    with tabs[5]:
        st.header("⚙️ Koç & Sistem Yönetim Merkezi")
        
        # 1. ÖĞRENCİ EKLEME VEYA SİLME ALANI
        st.subheader("👨‍🎓 Öğrenci Yönetimi (Ekle / Sil / Şifre Değiştir)")
        
        col_oe1, col_oe2 = st.columns(2)
        
        # Öğrenci Ekleme Formu
        with col_oe1:
            st.markdown("### ➕ Yeni Öğrenci Ekle")
            new_s_username = st.text_input("Öğrenci Kullanıcı Adı (Örn: ahmet):").strip().lower()
            new_s_fullname = st.text_input("Öğrenci Adı Soyadı (Örn: Ahmet Demir):")
            new_s_pass = st.text_input("Öğrenci Şifresi:", value="1234")
            
            # Eğer Admin ise hangi koça bağlayacağını seçsin
            if role == "Ana Yönetici":
                assigned_koc = st.selectbox("Atanacak Koç:", list(st.session_state["koclar"].keys()), format_func=lambda x: st.session_state["koclar"][x]["ad"])
            else:
                assigned_koc = curr_usr

            if st.button("➕ Öğrenciyi Kaydet", type="primary"):
                if new_s_username and new_s_fullname:
                    if new_s_username in st.session_state["ogrenciler"]:
                        st.error("Bu kullanıcı adı zaten mevcut!")
                    else:
                        st.session_state["ogrenciler"][new_s_username] = {
                            "ad": new_s_fullname, "sifre": new_s_pass, "koc_id": assigned_koc,
                            "calisma": [], "deneme": [],
                            "hedef_netler": {d: 15.0 for d in ANA_LGS_DERSLERI},
                            "ozlu_soz": "Başarı yolculuğun başladı!"
                        }
                        st.success(f"✅ {new_s_fullname} sisteme eklendi!")
                        st.rerun()

        # Öğrenci Silme Formu
        with col_oe2:
            st.markdown("### 🗑️ Öğrenci Sil")
            silinecek_ogrenciler = list(filtre_ogrenciler.keys()) if role == "Koç" else list(st.session_state["ogrenciler"].keys())
            
            if len(silinecek_ogrenciler) > 0:
                del_s_id = st.selectbox("Silinecek Öğrenciyi Seçin:", silinecek_ogrenciler, format_func=lambda x: f"{st.session_state['ogrenciler'][x]['ad']} ({x})")
                if st.button("❌ Seçili Öğrenciyi Sistemden Sil", type="secondary"):
                    del st.session_state["ogrenciler"][del_s_id]
                    st.success("Öğrenci başarıyla silindi!")
                    st.rerun()
            else:
                st.info("Silinecek öğrenci bulunmuyor.")

        st.divider()

        # 2. SADECE ANA YÖNETİCİ (SUPER ADMIN) KOÇ YÖNETİM ALANI
        if role == "Ana Yönetici":
            st.subheader("👑 Ana Yönetici Özel Paneli: Koç Yönetimi")
            
            col_ke1, col_ke2 = st.columns(2)
            
            # Koç Ekleme
            with col_ke1:
                st.markdown("### ➕ Yeni Koç Ekle")
                new_k_username = st.text_input("Koç Kullanıcı Adı (Örn: koc3):").strip().lower()
                new_k_fullname = st.text_input("Koç Adı Soyadı (Örn: Ayşe Hoca):")
                new_k_pass = st.text_input("Koç Şifresi:", value="koc123")
                new_k_lisans = st.checkbox("Lisans Ödemesi Yapıldı / Aktif", value=True)
                
                if st.button("➕ Yeni Koç Oluştur", type="primary"):
                    if new_k_username and new_k_fullname:
                        if new_k_username in st.session_state["koclar"]:
                            st.error("Bu koç kullanıcı adı zaten var!")
                        else:
                            st.session_state["koclar"][new_k_username] = {"ad": new_k_fullname, "sifre": new_k_pass, "lisans": new_k_lisans}
                            st.success(f"✅ Koç {new_k_fullname} başarıyla eklendi!")
                            st.rerun()

            # Koç Silme ve Lisans Durumu
            with col_ke2:
                st.markdown("### 🗑️ Koç Sil / Lisans Yönetimi")
                del_k_id = st.selectbox("İşlem Yapılacak Koç:", list(st.session_state["koclar"].keys()), format_func=lambda x: f"{st.session_state['koclar'][x]['ad']} ({x})")
                
                # Lisans durumu değiştirme
                cur_lic = st.session_state["koclar"][del_k_id]["lisans"]
                new_lic = st.checkbox("Lisans Aktif", value=cur_lic, key=f"lic_{del_k_id}")
                st.session_state["koclar"][del_k_id]["lisans"] = new_lic
                
                if st.button("❌ Seçili Koçu Sistemden Sil"):
                    del st.session_state["koclar"][del_k_id]
                    st.success("Koç sistemden silindi!")
                    st.rerun()
