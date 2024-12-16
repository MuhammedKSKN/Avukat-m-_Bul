from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import psycopg2
from psycopg2 import sql
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import traceback
import pickle
import numpy as np
from sklearn.preprocessing import LabelEncoder
from flask_cors import CORS
import hashlib
from sklearn.base import BaseEstimator

lbe = LabelEncoder()
app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key'
from flask import jsonify

# Model dosyasını yükleme
with open("trained_model.sav", "rb") as file:
    model = pickle.load(file)
    
    from flask import jsonify
    
@app.route('/predict_case', methods=['POST'])
def predict_case():
    try:
        # Giriş verilerini al ve kontrol et
        dava_turu = int(request.form['dava_turu'])
        delil_durumu = int(request.form['delil_durumu'])
        tanik_sayisi = int(request.form['tanik_sayisi'])
        delil_sayisi = int(request.form['delil_sayisi'])
        hukuki_dayanak = int(request.form['hukuki_dayanak'])
        hukuki_temsil = int(request.form['hukuki_temsil'])
        onceki_davalar = int(request.form['onceki_davalar'])
        dava_suresi = int(request.form['dava_suresi'])
        hukuki_menfaat = int(request.form['hukuki_menfaat'])
        karmasiklik = int(request.form['karmasiklik'])

        yargi_durumu = int(request.form['yargi_durumu'])
        uzlasma = int(request.form['uzlasma'])
        uzman_gorus = int(request.form['uzman_gorus'])

        # Verileri modele uygun formata çevir
        input_data = np.array([[dava_turu, delil_durumu, tanik_sayisi, delil_sayisi, hukuki_dayanak, hukuki_temsil,
                                onceki_davalar, dava_suresi, hukuki_menfaat, karmasiklik, yargi_durumu, uzlasma, uzman_gorus]])

        # Model ile tahmin yap
        prediction = model.predict(input_data)
        result = {'prediction': 'Dava kazanılabilir' if prediction[0] == 1 else 'Dava kaybedilebilir'}

        return jsonify(result), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

    


def get_db_connection():
    try:
        connection = psycopg2.connect(
            host='localhost',
            port='5432',
            database='avukat-portali-db',
            user='postgres',
            password='123'
            # port='5432'
        )
        return connection
    except psycopg2.Error as e:
        print(f"PostgreSQL bağlantı hatası: {e}")
        return None


    

@app.route('/')
def index():
   
 return render_template('index.html')  # Tarayıcıya HTML şablonu döndür
import hashlib
# Giriş sayfası
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['userType']

        # Şifreyi MD5 ile hashle
        hashed_password = hashlib.md5(password.encode()).hexdigest()

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            if user_type == 'avukat':
                cursor.execute(
                    "SELECT * FROM lawyer WHERE username = %s AND password = %s",
                    (username, hashed_password))
            else:
                cursor.execute(
                    "SELECT * FROM kullanici WHERE username = %s AND password = %s",
                    (username, hashed_password))
                
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user:
                session['username'] = username
                flash('Giriş başarılı!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Kullanıcı adı veya şifre hatalı.', 'danger')
    return render_template('login.html')

# Kayıt sayfası
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        username = request.form['registerUsername']
        password = request.form['registerPassword']
        user_type = request.form['registerUserType']
        hashed_password = hashlib.md5(password.encode()).hexdigest()

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            if user_type == 'avukat':
                sicil_no = request.form['sicilNo']
                department = request.form['department']
                cursor.execute(
                    """INSERT INTO avukat (first_name, last_name, username, password, sicil_no, department) 
                    VALUES (%s, %s, %s, %s, %s, %s)""",
                    (first_name, last_name, username, hashed_password, sicil_no, department))
            else:
                cursor.execute(
                    """INSERT INTO kullanici (first_name, last_name, username, password) 
                    VALUES (%s, %s, %s, %s)""",
                    (first_name, last_name, username, hashed_password))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Kayıt başarılı! Giriş yapmayı deneyin.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Veritabanına bağlanılamadı.', 'danger')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)  # Oturumdan kullanıcı adını kaldır
    session.pop('sicil_no', None)  # Sicil numarasını session'dan kaldır
    flash('Çıkış başarılı!', 'success')  # Başarı mesajı
    return redirect(url_for('index'))  # Anasayfaya yönlendir
# Diğer sayfa rotaları
@app.route('/hakkımızda')
def hakkımızda():
    return render_template('hakkımızda.html')

@app.route('/sss')
def sss():
    return render_template('sss.html')

@app.route('/yapayzeka')
def yapayzeka():
    return render_template('yapayzeka.html')



# Avukat ilanlarını listeleme
@app.route('/avukat')
def avukat():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT isim_soyisim, uzmanlik, email, telefon_numarasi, deneyim_yil, buro_konum, puan, aciklama FROM ilan")
        ilanlar = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('avukat.html', ilanlar=ilanlar)
    else:
        flash('Veritabanına bağlanılamadı.', 'danger')
        return render_template('avukat.html', ilanlar=[])

# İlan ekleme
@app.route('/ilan', methods=['GET', 'POST'])
def ilan():
    mesaj = None
    if request.method == 'POST':
        isim_soyisim = request.form['isimSoyisim']
        uzmanlik = request.form['uzmanlik']
        email = request.form['email']
        telefon = request.form['telefon']
        deneyim = request.form['deneyim']
        konum = request.form['konum']
        aciklama = request.form['aciklama']
        puan = 0

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO ilan (isim_soyisim, uzmanlik, email, telefon_numarasi, deneyim_yil, buro_konum, puan, aciklama)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (isim_soyisim, uzmanlik, email, telefon, deneyim, konum, puan, aciklama))
            conn.commit()
            cursor.close()
            conn.close()
            mesaj = 'Tebrikler, ilanınız kaydedildi!'
        else:
            mesaj = 'Veritabanına bağlanılamadı.'
    return render_template('ilan.html', mesaj=mesaj)
#iletisime geç kısmı
def contact():
    if request.method == 'POST':
        email = request.form['email']
        # E-posta ile ilgili işlemleri burada yapın (örneğin, veritabanına kaydetme veya e-posta gönderme)
        return redirect(url_for('thank_you'))  # Teşekkür sayfasına yönlendirme
    return render_template('contact.html')
@app.route('/thank-you')
def thank_you():
    return "Teşekkürler! Mesajınız alınmıştır."
@app.route('/iletisim', methods=['GET', 'POST'])
def iletisim():
    eposta = request.args.get('email', '')  # URL'den e-posta değerini al
    ilan_id = request.args.get('ilan_id', '')
    if request.method == 'POST':
        # Burada e-posta gönderme işlemleri yapılabilir
        pass
    return render_template('iletisim.html', eposta=eposta, ilan_id=ilan_id)
#asistan
@app.route('/asistan')
def asistan():
    return render_template('asistan.html')
###E-Mail servisi
@app.route('/send_email', methods=['POST'])
def send_email():
    ad = request.form['ad']
    soyad = request.form['soyad']
    adres = request.form['adres']
    kullanici_email = request.form['kullanici_e-posta']
    avukat_email = request.form['email']
    randevu_tarihi = request.form['randevu_tarihi']
    mesaj = request.form['mesaj']

    # # Yandex SMTP ayarları
    # yandex_email = 'huaweiargekodlama@yandex.com'  # Yandex e-posta adresiniz
    # yandex_password = 'vxnzekvivqjrisne'  # Yandex uygulama şifreniz

#     # E-posta içeriği oluşturma
#     msg = MIMEMultipart()
#     msg['From'] = yandex_email
#     msg['To'] = avukat_email
#     msg['Subject'] = 'Avukatınız ile iletişime geçin'  # Dinamik başlık

#     body = f'''
#     <p><strong>Ad:</strong> {ad}</p>
#     <p><strong>Soyad:</strong> {soyad}</p>
#     <p><strong>Adres:</strong> {adres}</p>
#     <p><strong>Kullanıcı E-posta:</strong> {kullanici_email}</p>
#     <p><strong>Randevu Tarihi:</strong> {randevu_tarihi}</p>
#     <p><strong>Mesaj:</strong> {mesaj}</p>
#     '''
#     msg.attach(MIMEText(body, 'html'))

#     try:
#         # Yandex SMTP sunucusuna bağlan
#         server = smtplib.SMTP_SSL('smtp.yandex.com', 465)  # SSL kullanarak bağlantı
#         server.login(yandex_email, yandex_password)  # Giriş yap
#         server.send_message(msg)  # E-postayı gönder
#         server.quit()  # Bağlantıyı kapat
#         return 'E-posta başarıyla gönderildi!', 200
#     except Exception as e:
#         print(f"Hata: {e}")
#         return f"E-posta gönderilemedi! Hata: {e}", 500
# #avukat sorgu
@app.route('/avukat_sorgu', methods=['GET'])
def avukat_sorgu():
    avukat_turu = request.args.get('avukat')  # Kullanıcının girdiği avukat türünü al

    # PostgreSQL bağlantısı
    try:
        conn = psycopg2.connect(
            host='localhost',
            # port='5000'# EIP adresin
            user='postgres',  # Kullanıcı adın
            password='54155415',  # Şifren
            dbname='ankatech'  # Veritabanı adı
        )
        cursor = conn.cursor()
    except ZeroDivisionError:
        print("Bir hata yakalandı!")  # Hata burada yakalanır

    # SQL sorgusu
    query = "SELECT isim_soyisim, uzmanlik, email, telefon_numarasi, deneyim_yil, buro_konum, puan, aciklama FROM ilan WHERE uzmanlik LIKE %s"
    cursor.execute(query, ('%' + avukat_turu + '%',))  # Anahtar kelime ile filtreleme

    # Sonuçları al
    ilanlar = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('avukat_sorgu.html', ilanlar=ilanlar)  # Sonuçları HTML ş

if __name__ == '__main__':
    app.run(debug=True)





