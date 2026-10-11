import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import requests
import json

# ==============================================================================
# GOOGLE SHEETS BAGLANTI URL'SI
# ==============================================================================
GSHEETS_URL = "https://script.google.com/macros/s/AKfycbzJ1udjB5PymW1Msl7Zk51t7uwATJzVYds9F98iq7kalanTvtQUvOfmG87Y6HaER2BS/exec"

def load_db():
    if GSHEETS_URL and GSHEETS_URL.startswith("http"):
        try:
            res = requests.get(GSHEETS_URL, timeout=8)
            if res.status_code == 200:
                val = res.json()
                if isinstance(val, dict) and "koclar" in val and "ogrenciler" in val:
                    return val
        except Exception:
            pass
    return None

def save_db(data):
    if GSHEETS_URL and GSHEETS_URL.startswith("http"):
        try:
            headers = {'Content-Type': 'application/json'}
            res = requests.post(GSHEETS_URL, data=json.dumps(data), headers=headers, timeout=10)
            return res.status_code == 200
        except Exception:
            return False
    return False

# 1. SAYFA YAPILANDIRMASI VE ŞIK STİL
st.set_page_config(page_title="ŞAHİN MATH CHECK-UP KOÇLUK AKADEMİSİ", layout="wide", page_icon="🦅")

st.markdown("""
<style>
    .main-title { font-size: 2.2rem; color: #1E3A8A; text-align: center; font-weight: 800; margin-bottom: 5px; }
    .sub-title { font-size: 1.1rem; color: #4B5563; text-align: center; margin-bottom: 20px; }
    .login-card { background-color: #F8FAFC; padding: 25px; border-radius: 15px; border: 1px solid #E2E8F0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# 2. VERİTABANI YÜKLEME
db_remote = load_db()

if "db" not in st.session_state:
    if db_remote:
        st.session_state["db"] = db_remote
    else:
        st.session_state["db"] = {
            "koclar": {
                "koc1": {"ad": "Ahmet Hoca", "sifre": "koc123", "lisans": True},
                "koc2": {"ad": "Mehmet Hoca", "sifre": "koc123", "lisans": False}
            },
            "ogrenciler": {
                "ali": {
                    "ad": "Ali Yılmaz", "sifre": "1234", "koc_id": "koc1",
                    "calisma": [], "deneme": [], "meb_cikmis_konu": {}, "haftalik_program": [],
                    "hedef_netler": {"Türkçe": 18.0, "Matematik": 15.0, "Fen Bilimleri": 18.0, "T.C. İnkılap Tarihi": 9.0, "Din Kültürü ve A.B.": 10.0, "İngilizce": 9.0},
                    "ozlu_soz": "Başarı, her gün tekrarlanan küçük çabaların toplamıdır!"
                }
            }
        }

db = st.session_state["db"]

# LGS MÜFREDATI
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
SEBEP_LISTESI = ["Yok / Hepsi Doğru", "Dikkat / İşlem Hatası", "Konu Bilgisi Eksik", "Soru Tarzını / Öncülü Anlamadım", "Süre Yetmedi", "İki Şık Arasında Kaldım / Tahmin Ettim"]
GUNLER = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None

# GİRİŞ EKRANI
if not st.session_state["logged_in"]:
    st.markdown('<div class="main-title">🦅 ŞAHİN MATH CHECK-UP KOÇLUK AKADEMİSİ</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">LGS Başarı & Performans Takip Sistemi</div>', unsafe_allow_html=True)
    
    col_c1, col_box, col_c2 = st.columns([1, 2, 1])
    with col_box:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        rol_secim = st.radio("🔑 Giriş Türünü Seçiniz:", ["👨‍🎓 Öğrenci Girişi", "👨‍🏫 Koç Girişi", "👑 Ana Yönetici Girişi"], horizontal=True)
        st.divider()
        
        if rol_secim == "👨‍🎓 Öğrenci Girişi":
            usr = st.text_input("Kullanıcı Adı (Örn: ali):", key="in_stud_usr").strip().lower()
            pwd = st.text_input("Şifre:", type="password", key="in_stud_pwd")
            if st.button("🚀 Öğrenci Olarak Giriş Yap", type="primary", use_container_width=True):
                if usr in db["ogrenciler"] and db["ogrenciler"][usr]["sifre"] == pwd:
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
                if usr in db["koclar"] and db["koclar"][usr]["sifre"] == pwd:
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

role = st.session_state["user_role"]
curr_usr = st.session_state["current_user"]

if "selected_student_id" not in st.session_state:
    st.session_state["selected_student_id"] = None

if role == "Öğrenci":
    active_stud_id = curr_usr
elif role in ["Koç", "Ana Yönetici"]:
    filtre_ogrenciler = {k: v for k, v in db["ogrenciler"].items() if v["koc_id"] == curr_usr} if role == "Koç" else db["ogrenciler"]
    if len(filtre_ogrenciler) > 0:
        if st.session_state["selected_student_id"] not in filtre_ogrenciler:
            st.session_state["selected_student_id"] = list(filtre_ogrenciler.keys())[0]
        active_stud_id = st.session_state["selected_student_id"]
    else:
        active_stud_id = None

# ==============================================================================
# DİKEY YAN MENÜ (ALT ALTA NAVİGASYON)
# ==============================================================================
with st.sidebar:
    st.markdown("### 🦅 ŞAHİN MATH CHECK-UP")
    st.caption("Koçluk Akademisi")
    st.info(f"👤 **Oturum:** {role}")
    
    if role == "Ana Yönetici":
        st.success("👑 **Süper Admin**")
        if len(db["ogrenciler"]) > 0:
            st.session_state["selected_student_id"] = st.selectbox(
                "İncelenen Öğrenci:", list(db["ogrenciler"].keys()),
                format_func=lambda x: f"{db['ogrenciler'][x]['ad']} ({x})"
            )
    elif role == "Koç":
        st.markdown(f"**Koç:** {db['koclar'][curr_usr]['ad']}")
        if len(filtre_ogrenciler) > 0:
            st.session_state["selected_student_id"] = st.selectbox(
                "Öğrenciniz:", list(filtre_ogrenciler.keys()),
                format_func=lambda x: f"{filtre_ogrenciler[x]['ad']} ({x})"
            )
    elif role == "Öğrenci":
        st.markdown(f"**Öğrenci:** {db['ogrenciler'][active_stud_id]['ad']}")

    st.divider()

    # DİKEY MENÜ SEÇİMİ (ALT ALTA SEÇENEKLER)
    menu_options = [
        "📝 Günlük Çalışma & Kitap Okuma",
        "📅 Haftalık Ders Çalışma Programı",
        "📊 Deneme Sınavları & Konu Hataları",
        "📚 MEB & Çıkmış Sorular (Konu Konu)",
        "👨‍👩‍👧 Veli & Koç Analiz Paneli"
    ]
    if role in ["Koç", "Ana Yönetici"]:
        menu_options.append("⚙️ Yönetim Paneli")

    secili_menu = st.radio("📌 **AKADEMİ MENÜSÜ**", menu_options)

    st.divider()
    with st.expander("🔑 Şifremi Değiştir"):
        yeni_pass = st.text_input("Yeni Şifreniz:", type="password", key="side_new_pass")
        if st.button("Şifreyi Güncelle"):
            if yeni_pass:
                if role == "Öğrenci":
                    db["ogrenciler"][curr_usr]["sifre"] = yeni_pass
                elif role == "Koç":
                    db["koclar"][curr_usr]["sifre"] = yeni_pass
                save_db(db)
                st.success("Şifreniz Google Sheets'e kaydedildi!")

    if active_stud_id and active_stud_id in db["ogrenciler"]:
        st.divider()
        st.warning(f"💡 **Motivasyon Notu:**\n\n_{db['ogrenciler'][active_stud_id]['ozlu_soz']}_")

    st.divider()
    if st.button("🚪 Çıkış Yap", type="secondary", use_container_width=True):
        st.session_state["logged_in"] = False
        st.session_state["user_role"] = None
        st.session_state["current_user"] = None
        st.rerun()

if not active_stud_id and role != "Ana Yönetici":
    st.warning("İşlem yapmak için tanımlı bir öğrenci gereklidir.")
    st.stop()

# ==============================================================================
# 1. GÜNLÜK ÇALIŞMA, SÜRE, KİTAP OKUMA VE ÖZ DEĞERLENDİRME
# ==============================================================================
if secili_menu == "📝 Günlük Çalışma & Kitap Okuma":
    if active_stud_id:
        ogr_obj = db["ogrenciler"][active_stud_id]
        st.header(f"📌 Günlük Ders Çalışma, Süre ve Kitap Okuma Girişi ({ogr_obj['ad']})")
        
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

        st.divider()
        st.subheader("📖 Kitap Okuma ve Günlük Öz Değerlendirme")
        col_k1, col_k2 = st.columns(2)
        with col_k1:
            kitap_adi = st.text_input("Bugün Okunan Kitap Adı", "Şeker Portakalı")
        with col_k2:
            okunan_sayfa = st.number_input("Bugün Okunan Sayfa Sayısı", min_value=0, value=20)

        gunluk_not = st.text_area("Günün Öz Değerlendirmesi / Çalışma Notun:", "Bugün yeni nesil sorularda iyi ilerledim, eksiklerimi tamamladım...")

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

        if st.button("💾 Günlük Tüm Verileri Kaydet", type="primary", use_container_width=True):
            ogr_obj["calisma"].append({
                "Tarih": str(tarih), "Ders": ders, "Konu": konu, "Süre (dk)": sure_dk,
                "Doğru": dogru, "Yanlış": yanlis, "Boş": bos, "Çözülen": dogru + yanlis + bos,
                "Hata Sebebi": hata_sebebi, "Çözüme Bakıldı": yapilamayana_bakildi, "Programa Uyum": programa_riayet,
                "Kitap": kitap_adi, "Sayfa": okunan_sayfa, "Not": gunluk_not
            })
            save_db(db)
            st.success("✅ Günlük ders, süre, kitap okuma ve öz değerlendirme kaydınız kalıcı olarak Google Sheets'e eklendi!")

# ==============================================================================
# 2. HAFTALIK DERS ÇALIŞMA PROGRAMI TABLOSU
# ==============================================================================
elif secili_menu == "📅 Haftalık Ders Çalışma Programı":
    if active_stud_id:
        ogr_obj = db["ogrenciler"][active_stud_id]
        if "haftalik_program" not in ogr_obj:
            ogr_obj["haftalik_program"] = []

        st.header(f"📅 Haftalık Ders Çalışma Programı ({ogr_obj['ad']})")
        st.caption("Haftalık ders programınızı gün ve saat aralıklarıyla belirleyebilirsiniz.")

        with st.expander("➕ Programa Yeni Ders / Saat Ekle"):
            col_p1, col_p2, col_p3, col_p4 = st.columns(4)
            with col_p1:
                prog_gun = st.selectbox("Gün Seç:", GUNLER)
            with col_p2:
                prog_saat = st.text_input("Saat Aralığı (Örn: 16:30 - 18:00):", "16:30 - 18:00")
            with col_p3:
                prog_ders = st.selectbox("Ders / Konu:", list(LGS_MUSERFAT.keys()))
            with col_p4:
                prog_hedef = st.number_input("Hedef Soru Sayısı:", min_value=0, value=40)

            if st.button("➕ Ders Programına Ekle"):
                ogr_obj["haftalik_program"].append({
                    "Gün": prog_gun, "Saat Aralığı": prog_saat, "Ders": prog_ders, "Hedef Soru": prog_hedef
                })
                save_db(db)
                st.success("Program güncellendi!")

        st.divider()
        st.subheader("📋 Mevcut Haftalık Çalışma Programınız")
        if len(ogr_obj["haftalik_program"]) > 0:
            df_prog = pd.DataFrame(ogr_obj["haftalik_program"])
            st.dataframe(df_prog, use_container_width=True)
            if st.button("🗑️ Programı Temizle / Sıfırla"):
                ogr_obj["haftalik_program"] = []
                save_db(db)
                st.warning("Haftalık program sıfırlandı!")
                st.rerun()
        else:
            st.info("Henüz oluşturulmuş bir haftalık çalışma programı bulunmuyor.")

# ==============================================================================
# 3. DENEME SINAVLARI VE KONU BAZLI HATA İŞARETLEME
# ==============================================================================
elif secili_menu == "📊 Deneme Sınavları & Konu Hataları":
    if active_stud_id:
        ogr_obj = db["ogrenciler"][active_stud_id]
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
        
        if "temp_deneme_hatalari" not in st.session_state:
            st.session_state["temp_deneme_hatalari"] = []

        col_h1, col_h2, col_h3, col_h4 = st.columns(4)
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
                "Tarih": str(deneme_tarihi), "Deneme": deneme_adi, 
                "Netler": net_girisleri, "KonuHatalari": st.session_state["temp_deneme_hatalari"]
            })
            st.session_state["temp_deneme_hatalari"] = []
            save_db(db)
            st.success("✅ Deneme sınavı kalıcı olarak Google Sheets'e kaydedildi!")

# ==============================================================================
# 4. MEB ÖRNEK VE ÇIKMIŞ SORULAR (KONU KONU İŞARETLEME)
# ==============================================================================
elif secili_menu == "📚 MEB & Çıkmış Sorular (Konu Konu)":
    if active_stud_id:
        ogr_obj = db["ogrenciler"][active_stud_id]
        if "meb_cikmis_konu" not in ogr_obj:
            ogr_obj["meb_cikmis_konu"] = {}

        st.header(f"📚 MEB Soruları ve Çıkmış Sorular (Konu Bazlı Takip)")
        st.caption("Her konunun MEB örnek sorularını ve LGS çıkmış sorularını tamamladıkça durumunu güncelleyebilirsiniz.")

        for ders_kategori, konular in LGS_MUSERFAT.items():
            with st.expander(f"📌 {ders_kategori}"):
                for kn in konular:
                    key_base = f"{ders_kategori}_{kn}"
                    if key_base not in ogr_obj["meb_cikmis_konu"]:
                        ogr_obj["meb_cikmis_konu"][key_base] = {"meb": False, "cikmis": False}

                    col_m1, col_m2, col_m3 = st.columns([2, 1, 1])
                    with col_m1:
                        st.markdown(f"**{kn}**")
                    with col_m2:
                        chk_meb = st.checkbox("MEB Soruları", value=ogr_obj["meb_cikmis_konu"][key_base]["meb"], key=f"meb_{key_base}")
                        ogr_obj["meb_cikmis_konu"][key_base]["meb"] = chk_meb
                    with col_m3:
                        chk_cikmis = st.checkbox("Çıkmış Sorular", value=ogr_obj["meb_cikmis_konu"][key_base]["cikmis"], key=f"cikmis_{key_base}")
                        ogr_obj["meb_cikmis_konu"][key_base]["cikmis"] = chk_cikmis

        st.divider()
        if st.button("💾 Konu Durumlarını Kalıcı Kaydet", type="primary", use_container_width=True):
            save_db(db)
            st.success("✅ Tüm konu bazlı MEB ve çıkmış soru durumları Google Sheets'e kaydedildi!")

# ==============================================================================
# 5. VELİ VE KOÇ ANALİZ PANELİ
# ==============================================================================
elif secili_menu == "👨‍👩‍👧 Veli & Koç Analiz Paneli":
    if active_stud_id:
        ogr_obj = db["ogrenciler"][active_stud_id]
        st.header(f"👨‍👩‍👧 {ogr_obj['ad']} - İlerleme ve Süre Analiz Paneli")
        
        if len(ogr_obj["calisma"]) > 0:
            df_calisma = pd.DataFrame(ogr_obj["calisma"])
            st.subheader("⏱️ Çalışma Süresi Analizi")
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("Toplam Çalışma Süresi", f"{df_calisma['Süre (dk)'].sum() / 60:.1f} Saat")
            col_m2.metric("Toplam Çözülen Soru", f"{df_calisma['Çözülen'].sum()} Soru")
            
            fig_sure = px.pie(df_calisma, values="Süre (dk)", names="Ders", title="Derslere Göre Zaman Dağılımı")
            st.plotly_chart(fig_sure, use_container_width=True)

            st.divider()
            st.subheader("📖 Günlük Kitap Okuma ve Öz Değerlendirme Geçmişi")
            st.dataframe(df_calisma[["Tarih", "Ders", "Süre (dk)", "Kitap", "Sayfa", "Not"]], use_container_width=True)
        else:
            st.info("Kayıtlı çalışma verisi bulunmuyor.")

# ==============================================================================
# 6. YÖNETİM PANELİ (KOÇ VE ADMİN)
# ==============================================================================
elif secili_menu == "⚙️ Yönetim Paneli" and role in ["Koç", "Ana Yönetici"]:
    st.header("⚙️ Koç & Sistem Yönetim Merkezi")
    
    st.subheader("👨‍🎓 Öğrenci Yönetimi (Ekle / Sil)")
    col_oe1, col_oe2 = st.columns(2)
    
    with col_oe1:
        st.markdown("### ➕ Yeni Öğrenci Ekle")
        new_s_username = st.text_input("Kullanıcı Adı (Örn: ahmet):").strip().lower()
        new_s_fullname = st.text_input("Adı Soyadı (Örn: Ahmet Demir):")
        new_s_pass = st.text_input("Şifresi:", value="1234")
        assigned_koc = st.selectbox("Atanacak Koç:", list(db["koclar"].keys()), format_func=lambda x: db["koclar"][x]["ad"]) if role == "Ana Yönetici" else curr_usr

        if st.button("➕ Öğrenciyi Kaydet", type="primary"):
            if new_s_username and new_s_fullname:
                if new_s_username in db["ogrenciler"]:
                    st.error("Bu kullanıcı adı zaten mevcut!")
                else:
                    db["ogrenciler"][new_s_username] = {
                        "ad": new_s_fullname, "sifre": new_s_pass, "koc_id": assigned_koc,
                        "calisma": [], "deneme": [], "meb_cikmis_konu": {}, "haftalik_program": [],
                        "hedef_netler": {d: 15.0 for d in ANA_LGS_DERSLERI},
                        "ozlu_soz": "Başarı yolculuğun başladı!"
                    }
                    save_db(db)
                    st.success(f"✅ {new_s_fullname} Google Sheets'e eklendi!")
                    st.rerun()

    with col_oe2:
        st.markdown("### 🗑️ Öğrenci Sil")
        silinecek_ogrenciler = list(filtre_ogrenciler.keys()) if role == "Koç" else list(db["ogrenciler"].keys())
        if len(silinecek_ogrenciler) > 0:
            del_s_id = st.selectbox("Silinecek Öğrenciyi Seçin:", silinecek_ogrenciler, format_func=lambda x: f"{db['ogrenciler'][x]['ad']} ({x})")
            if st.button("❌ Seçili Öğrenciyi Sil", type="secondary"):
                del db["ogrenciler"][del_s_id]
                save_db(db)
                st.success("Öğrenci silindi ve veritabanı güncellendi!")
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
                    db["koclar"][new_k_username] = {"ad": new_k_fullname, "sifre": new_k_pass, "lisans": True}
                    save_db(db)
                    st.success(f"✅ Koç {new_k_fullname} eklendi!")
                    st.rerun()

        with col_ke2:
            st.markdown("### 🗑️ Koç Sil")
            del_k_id = st.selectbox("İşlem Yapılacak Koç:", list(db["koclar"].keys()), format_func=lambda x: f"{db['koclar'][x]['ad']} ({x})")
            if st.button("❌ Seçili Koçu Sil"):
                del db["koclar"][del_k_id]
                save_db(db)
                st.success("Koç silindi!")
                st.rerun()
