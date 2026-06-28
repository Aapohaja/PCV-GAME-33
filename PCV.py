# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 04:25:48 2025

@author: aaron
"""

import cv2          
import numpy as np  
import os           

def titik(pts):
    """
    Fungsi ini mengurutkan 4 titik pojok kartu menjadi:
    - pojok kiri atas
    - pojok kanan atas  
    - pojok kanan bawah
    - pojok kiri bawah
    """
    # Baris 12: Buat array kosong berukuran 4x2 (4 titik, masing-masing punya x dan y)
    rect = np.zeros((4,2), dtype = "float32")
    
    # Baris 13: Hitung x + y untuk setiap titik (sum axis 1 = jumlah per baris)
    # Contoh: titik (10, 20) → s = 30
    s = pts.sum(axis = 1)
    
    # Baris 14: Hitung selisih x - y untuk setiap titik (diff = difference)
    # Contoh: titik (10, 20) → diff = -10
    diff = np.diff(pts, axis = 1)
    
    # Baris 15: Pojok kiri atas = titik dengan x+y terkecil (paling kiri atas)
    rect[0] = pts[np.argmin(s)]
    
    # Baris 16: Pojok kanan bawah = titik dengan x+y terbesar (paling kanan bawah)
    rect[2] = pts[np.argmax(s)]
    
    # Baris 17: Pojok kanan atas = titik dengan x-y terkecil (biasanya paling kanan)
    rect[1] = pts[np.argmin(diff)]
    
    # Baris 18: Pojok kiri bawah = titik dengan x-y terbesar (biasanya paling kiri)
    rect[3] = pts[np.argmax(diff)]
    
    # Baris 19: Kembalikan array 4 pojok yang sudah terurut
    return rect

# Baris 25-59: Fungsi Klasifikasi Kartu Menggunakan SAD (Sum of Absolute Differences)
def klasifikasi_kartu(kartu_warped, all_templates):
    """
    Fungsi ini membandingkan kartu dari kamera dengan 52 template kartu
    menggunakan metode SUM OF ABSOLUTE DIFFERENCES (SAD)
    
    SAD = jumlah selisih absolut setiap piksel
    Semakin kecil SAD, semakin mirip kartunya!
    """
    
    # Baris 33: Ubah kartu dari warna (BGR) jadi abu-abu (grayscale)
    # Supaya lebih mudah diproses
    gray_warped = cv2.cvtColor(kartu_warped, cv2.COLOR_BGR2GRAY)
    
    # Baris 36: Ubah gambar abu-abu jadi hitam-putih saja (threshold)
    # > 150 = hitam (0), <= 150 = putih (255)
    # THRESH_OTSU = algoritma untuk otomatis cari nilai threshold terbaik
    # THRESH_BINARY_INV = invers (hitam jadi putih, putih jadi hitam)
    _, threshold_warped = cv2.threshold(gray_warped, 150, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Baris 41-42: Inisialisasi variabel untuk menyimpan hasil terbaik
    # float('inf') = infinity (nilai terbesar) karena kita cari SAD TERKECIL
    # Untuk SAD: semakin kecil = semakin mirip, jadi mulai dengan nilai terbesar
    best_match = ("unknow", float('inf'))
    
    # Baris 44: Loop melalui semua 52 template kartu yang sudah dihapal
    for nama_kartu, gambar in all_templates.items():
        
        # Baris 45-46: Cek apakah ukuran gambar sama dengan template
        # Kalau beda, resize template agar sama ukurannya
        if threshold_warped.shape != gambar.shape:
            gambar = cv2.resize(gambar, (threshold_warped.shape[1], threshold_warped.shape[0]))
        
        # ========================================
        # SUM OF ABSOLUTE DIFFERENCES (SAD)
        # ========================================
        
        # Baris 51: Ubah kedua gambar jadi float32 supaya bisa dikurangi
        # .astype(np.float32) = ubah tipe data jadi float (bisa desimal)
        img1 = threshold_warped.astype(np.float32)
        img2 = gambar.astype(np.float32)
        
        # Baris 54: Hitung selisih setiap piksel: |gambar_kamera - template|
        # np.abs() = absolut (selalu positif)
        # Contoh: piksel kamera = 255, template = 0 → diff = |255-0| = 255
        #         piksel kamera = 0, template = 0  → diff = |0-0| = 0
        diff = np.abs(img1 - img2)
        
        # Baris 57: Jumlahkan SEMUA selisih dari semua piksel
        # Ini adalah SUM OF ABSOLUTE DIFFERENCES (SAD)
        # Contoh: kalau semua piksel sama → SAD = 0 (sangat mirip!)
        #         kalau banyak beda → SAD besar (tidak mirip)
        sad_value = np.sum(diff)
        
        # Baris 60-61: Bandingkan dengan hasil sebelumnya
        # Untuk SAD: semakin kecil = semakin mirip
        # Jadi cari SAD TERKECIL
        if sad_value < best_match[1]:
            best_match = (nama_kartu, sad_value)
    
    # Baris 64: Ambil nama kartu yang paling mirip (SAD terkecil)
    kartu_terklasifikasi = best_match[0]
    
    # Baris 65: Ambil nilai SAD terkecil
    sad_value = best_match[1]
    
    # ========================================
    # NORMALISASI SAD MENJADI CONFIDENCE (0-1)
    # ========================================
    
    # Baris 71-72: Hitung SAD maksimum yang mungkin
    # Untuk gambar hitam-putih (0 atau 255), maksimum SAD adalah:
    # tinggi x lebar x 255 (semua piksel beda total)
    max_possible_sad = threshold_warped.shape[0] * threshold_warped.shape[1] * 255.0
    
    # Baris 75-76: Normalisasi SAD jadi confidence (0 sampai 1)
    # Formula: confidence = 1 - (SAD / max_SAD)
    # - SAD = 0 (sangat mirip) → confidence = 1 - 0 = 1.0 (100%)
    # - SAD = max_SAD (sangat beda) → confidence = 1 - 1 = 0.0 (0%)
    confidence = 1.0 - (sad_value / max_possible_sad)
    
    # Baris 79: Pastikan confidence antara 0 sampai 1
    # max(0.0, ...) = minimal 0, min(..., 1.0) = maksimal 1
    confidence = max(0.0, min(1.0, confidence))
    
    # Baris 82-83: Kalau confidence terlalu rendah (< 50%), kartu tidak diketahui
    if confidence < 0.5:
        kartu_terklasifikasi = "tidak diketahui"
    
    # Baris 85: Kembalikan nama kartu dan confidence
    return kartu_terklasifikasi, confidence

# ==========================================
# BAGIAN INISIALISASI - MEMUAT TEMPLATE KARTU
# ==========================================

# Baris 91: Path folder yang berisi 52 foto template kartu
Folder = r"C:\Users\aaron\Downloads\individual_cards_2"

# Baris 93: Daftar angka/rank kartu: A, 2, 3, 4, 5, 6, 7, 8, 9, 10, J, Q, K
RANKS = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]

# Baris 94: Daftar jenis/suit kartu: Spade (sekop), Heart (hati), Diamond (wajik), Club (keriting)
SUITS = ["Spade","Heart","Diamond","Club"]

# Baris 96: Dictionary kosong untuk menyimpan semua template kartu di memori
kartu_template = {}

# Baris 97: Ukuran standar kartu setelah di-warp (lebar x tinggi dalam piksel)
lebar, tinggi = 300, 420

# Baris 99: Print nama folder untuk debugging
print(f"Nama folder: {Folder}")

# Baris 101-119: Loop untuk memuat semua 52 template kartu
# Loop luar: untuk setiap jenis kartu (Spade, Heart, Diamond, Club)
for suit in SUITS:
    # Loop dalam: untuk setiap angka kartu (A, 2, 3, ..., K)
    for rank in RANKS:
        # Baris 106: Gabungkan angka dan jenis jadi nama kartu
        # Contoh: "A Spade", "K Diamond"
        nama_kartu = f"{rank} {suit}"
        
        # Baris 107: Nama file sesuai format: "A_Spade.jpg", "K_Diamond.jpg"
        namafile = f"{rank}_{suit}.jpg"
        
        # Baris 108: Gabungkan path folder + nama file
        # Contoh: "/folder/A_Spade.jpg"
        path = os.path.join(Folder, namafile)
        
        # Baris 110: Baca gambar dari file menggunakan OpenCV
        template = cv2.imread(path)
        
        # Baris 111-113: Cek apakah file ada
        # Kalau None = file tidak ditemukan
        if template is None:
            print(f"error {namafile} gaada di {Folder}")
            continue  # Skip ke kartu berikutnya
        
        # Baris 115: Resize template ke ukuran standar 300x420
        Resized = cv2.resize(template, (lebar, tinggi))
        
        # Baris 116: Ubah dari warna (BGR) jadi abu-abu (grayscale)
        template_gray = cv2.cvtColor(Resized, cv2.COLOR_BGR2GRAY)
        
        # Baris 118: Ubah jadi hitam-putih saja (threshold)
        # Sama seperti yang dilakukan pada kartu dari kamera
        _, template_thresh = cv2.threshold(template_gray, 150, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        
        # Baris 119: Simpan template yang sudah di-process ke dictionary
        # Key = nama kartu (contoh: "A Spade")
        # Value = gambar hitam-putih template
        kartu_template[nama_kartu] = template_thresh

# Baris 121: Print total template yang berhasil dimuat
print(f"total: {len(kartu_template)}")

# ==========================================
# BAGIAN KAMERA - DETEKSI REAL-TIME
# ==========================================

# Baris 127: Buka kamera default (0 = kamera pertama di laptop)
url = "http://192.168.111.199:4747/video"
cap = cv2.VideoCapture(url)

# Baris 128-129: Cek apakah kamera berhasil dibuka
if not cap.isOpened():
    print("kamera ga bisa")
    
# Baris 131-132: Ukuran kartu setelah di-warp (harus sama dengan template)
lebarkamerakartu = 300
tinggikamerakartu = 420

# Baris 134-138: Titik-titik tujuan untuk warp perspective
# Ini adalah 4 pojok dari kotak tujuan (sudut kiri atas, kanan atas, kanan bawah, kiri bawah)
dst_pts = np.array([
    [0, 0],                                    # Pojok kiri atas: (0, 0)
    [lebarkamerakartu - 1, 0],                 # Pojok kanan atas: (299, 0)
    [lebarkamerakartu - 1, tinggikamerakartu - 1],  # Pojok kanan bawah: (299, 419)
    [0, tinggikamerakartu - 1]                 # Pojok kiri bawah: (0, 419)
], dtype="float32")

# Baris 141: Loop utama - terus-terusan ambil frame dari kamera
while True:
    # Baris 142: Baca satu frame dari kamera
    # ret = return value (True/False) - apakah berhasil baca frame
    # frame = gambar yang diambil dari kamera
    ret, frame = cap.read()
    
    # Baris 143-145: Cek apakah berhasil membaca frame
    # Kalau tidak, keluar dari loop
    if not ret:
        print('kamera errorr')
        break
    
    # Baris 147: Copy frame untuk di-modify (supaya frame asli tetap utuh)
    img_output = frame.copy()
    
    # Baris 148: Ambil tinggi dan lebar frame
    # frame.shape = (tinggi, lebar, channel)
    # [:2] = ambil index 0 dan 1 saja (tinggi dan lebar)
    img_tinggi, img_lebar = frame.shape[:2]
    
    # Baris 150: Faktor perkecil gambar (0.5 = setengah ukuran)
    # Ini supaya proses lebih cepat (gambar kecil lebih cepat diproses)
    scale_down = 0.5
    
    # Baris 151-156: Perkecil frame kalau scale_down bukan 1.0
    if scale_down != 1.0:
        # Resize gambar jadi setengah ukuran
        # int(...) = ubah ke integer (pembulatan)
        resized_frame = cv2.resize(
            frame, 
            (int(img_lebar * scale_down), int(img_tinggi * scale_down)), 
            interpolation=cv2.INTER_AREA  # Metode resize (anti blur saat diperkecil)
        )
    else:
        # Kalau scale_down = 1.0, tidak perlu resize, copy saja
        resized_frame = frame.copy()
    
    # Baris 158: Ambil tinggi dan lebar frame yang sudah di-resize
    imgbaru_tinggi, imgbaru_lebar = resized_frame.shape[:2]
    
    # Baris 160: Ubah frame dari warna jadi abu-abu (grayscale)
    gray = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
    
    # Baris 161: Blur gambar untuk mengurangi noise (bintik-bintik kecil)
    # (5,5) = ukuran kernel blur
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    
    # Baris 162: Deteksi tepi menggunakan Canny edge detection
    # 50, 150 = threshold rendah dan tinggi untuk deteksi tepi
    edges = cv2.Canny(blur, 50, 150)
    
    # Baris 163: Cari kontur (garis-garis yang membentuk bentuk tertutup)
    # RETR_EXTERNAL = hanya ambil kontur luar (tidak ambil kontur di dalam)
    # CHAIN_APPROX_SIMPLE = simpan hanya titik-titik penting (hemat memori)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Baris 165: Copy frame untuk gambar kontur (untuk debugging)
    gambar_contour = resized_frame.copy()
    
    # Baris 166: Gambar semua kontur dengan warna hijau (0, 255, 0)
    # -1 = gambar semua kontur
    cv2.drawContours(gambar_contour, contours, -1, (0,255,0), 1)
    
    # Baris 168: Hitung area minimum untuk kartu
    # Hanya kontur yang lebih besar dari ini yang akan diproses
    # Membagi dengan 150 = filter benda kecil (noise)
    area_kartumin = (imgbaru_lebar * imgbaru_tinggi) / 150
    
    # Baris 170-171: Tampilkan window untuk debugging
    cv2.imshow("Kontur", gambar_contour)  # Window yang menampilkan kontur
    cv2.imshow('edges', edges)             # Window yang menampilkan tepi
    cv2.imshow('blur' , blur)
    
    # Baris 173: List kosong untuk menyimpan kartu yang terdeteksi
    kartu_terdeteksi = []
    
    # Baris 175: Loop melalui setiap kontur yang ditemukan
    for c_resized in contours:
        # Baris 176: Hitung luas area kontur
        area = cv2.contourArea(c_resized)
        
        # Baris 178: Cek apakah area cukup besar (bukan noise kecil)
        if area > area_kartumin:
            # Baris 179: Hitung keliling kontur
            peri = cv2.arcLength(c_resized, True)
            
            # Baris 180: Perkirakan kontur jadi bentuk poligon sederhana
            # 0.02 * peri = toleransi (2% dari keliling)
            # True = kontur tertutup
            approx_resized = cv2.approxPolyDP(c_resized, 0.02 * peri, True)
            
            # Baris 182: Cek apakah kontur punya 4 titik (bentuk kotak/segiempat)
            # Kartu remi bentuknya kotak, jadi harus 4 pojok!
            if len(approx_resized) == 4:
                # Baris 183: Kembalikan ukuran kontur ke ukuran frame asli
                # Karena sebelumnya frame diperkecil, sekarang dikembalikan
                approx_original = (approx_resized / scale_down).astype(np.int32)
                
                # Baris 184: Urutkan 4 pojok menggunakan fungsi titik()
                # reshape(4,2) = ubah jadi array 4x2 (4 titik, masing-masing x,y)
                src_pts = titik(approx_original.reshape(4,2))
                
                # Baris 186-187: Warp perspective untuk meluruskan kartu
                # Kartu mungkin miring di kamera, warp supaya jadi lurus
                # cv2.getPerspectiveTransform = hitung transformasi
                m = cv2.getPerspectiveTransform(src_pts, dst_pts)
                
                # cv2.warpPerspective = aplikasikan transformasi
                # Hasilnya: kartu lurus dengan ukuran 300x420
                w_kartu = cv2.warpPerspective(frame, m, (lebar, tinggi))
                
                # Baris 189-190: Klasifikasi kartu menggunakan SAD
                # Bandingkan kartu yang sudah di-warp dengan 52 template
                klasifikasi_teks, confidence = klasifikasi_kartu(w_kartu, kartu_template)
                
                # Baris 192: Tampilkan kartu yang sudah di-warp (untuk debugging)
                cv2.imshow("kartu ke warp", w_kartu)
                
                # Baris 195-199: Simpan info kartu yang terdeteksi ke list
                kartu_terdeteksi.append({
                    'contour': approx_original,      # Kontur (4 pojok) kartu
                    'klasifikasi': klasifikasi_teks,  # Nama kartu (contoh: "A Spade")
                    'confidence': confidence          # Tingkat kepercayaan (0-1)
                })
    
    # ==========================================
    # BAGIAN TAMPILAN HASIL
    # ==========================================
    
  
    # Baris 209: Loop untuk menampilkan info setiap kartu yang terdeteksi
    for info_kartu in kartu_terdeteksi:
        # Baris 210-212: Ambil data kartu
        contour = info_kartu['contour']          # 4 pojok kartu
        klasifikasi_teks = info_kartu['klasifikasi']  # Nama kartu
        confidence = info_kartu['confidence']    # Confidence
        
        # Baris 214: Warna kotak hijau (0, 255, 0) untuk semua kartu
        warna_contour = (0, 255, 0)  # Hijau
        
        # Baris 216: Gambar kotak di sekitar kartu dengan warna hijau
        cv2.drawContours(img_output, [contour], -1, warna_contour, 2)
        
        # Baris 218: Hitung pusat kartu (centroid) untuk posisi teks
        # Moments = sifat geometri kontur
        m_cnt = cv2.moments(contour)
        
        # Baris 219: Cek apakah kontur valid (m00 = area kontur)
        if m_cnt['m00'] != 0:
            # Baris 220-221: Hitung koordinat pusat (centroid)
            # cX = center X, cY = center Y
            cX = int(m_cnt['m10'] / m_cnt['m00'])  # m10/m00 = rata-rata x
            cY = int(m_cnt['m01'] / m_cnt['m00'])  # m01/m00 = rata-rata y
            
            # Baris 223-224: Tampilkan nama kartu di tengah kartu
            # (cX - 50, cY) = posisi teks (sedikit ke kiri dari pusat)
            # Warna kuning (0, 255, 255) untuk tulisan
            cv2.putText(img_output, klasifikasi_teks, (cX - 50, cY),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            # Baris 226-227: Tampilkan confidence di bawah nama kartu
            # :.2f = format 2 angka di belakang koma
            # Warna kuning (0, 255, 255) untuk tulisan
            cv2.putText(img_output, f'confidence: {confidence:.2f}', 
                       (cX - 50, cY + 20), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 255), 1)
    
    # Baris 229: Tampilkan frame final dengan semua info kartu
    cv2.imshow('kartu', img_output)
    
    # Baris 231-232: Cek apakah user menekan tombol 'q'
    # cv2.waitKey(1) = tunggu 1 milidetik untuk input keyboard
    # 0xFF == ord('q') = cek apakah yang ditekan adalah huruf 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break  # Keluar dari loop
    
# Baris 236: Tutup kamera
cap.release()

# Baris 237: Tutup semua window OpenCV
cv2.destroyAllWindows()

# ==========================================
# PENJELASAN SINGKAT ALGORITMA
# ==========================================
"""
CARA KERJA PROGRAM:
1. Load 52 template kartu (A-10, J, Q, K dari 4 jenis) ke memori
2. Buka kamera dan ambil frame terus-menerus
3. Untuk setiap frame:
   a. Perkecil gambar (supaya lebih cepat)
   b. Ubah jadi grayscale → blur → cari tepi (Canny)
   c. Cari kontur (bentuk tertutup)
   d. Filter kontur yang punya 4 pojok (bentuk kotak)
   e. Warp perspective untuk meluruskan kartu
   f. Bandingkan dengan 52 template menggunakan SAD:
      - Hitung selisih absolut setiap piksel
      - Jumlahkan semua selisih (SAD)
      - Kartu dengan SAD terkecil = yang paling mirip
   g. Normalisasi SAD jadi confidence (0-1)
   h. Tampilkan nama kartu dan confidence di layar
4. Tekan 'q' untuk keluar
"""