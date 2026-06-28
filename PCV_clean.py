import cv2          
import numpy as np  
import os           


def titik(pts):
    rect = np.zeros((4,2), dtype = "float32")
    s = pts.sum(axis = 1)  
    diff = np.diff(pts, axis = 1)  

    rect[0] = pts[np.argmin(s)]  
    rect[2] = pts[np.argmax(s)]  
    rect[1] = pts[np.argmin(diff)]  
    rect[3] = pts[np.argmax(diff)]  
    return rect


def klasifikasi_kartu(kartu_warped, all_templates):
    
    gray_warped = cv2.cvtColor(kartu_warped, cv2.COLOR_BGR2GRAY)
    _, threshold_warped = cv2.threshold(gray_warped, 150, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
  
    best_match = ("unknow", float('inf'))  # Simpan hasil terbaik (SAD terkecil)
    
    # Bandingkan dengan semua 52 template kartu
    for nama_kartu, gambar in all_templates.items():
        if threshold_warped.shape != gambar.shape:
            gambar = cv2.resize(gambar, (threshold_warped.shape[1], threshold_warped.shape[0]))
        
        # Hitung SAD: jumlah selisih absolut setiap piksel
        img1 = threshold_warped.astype(np.float32)
        img2 = gambar.astype(np.float32)
        
        diff = np.abs(img1 - img2)
        sad_value = np.sum(diff)
        
        
        # best_match[1] berisi nilai SAD dari template terbaik saat ini
        # Jika sad_value lebih kecil, berarti template ini lebih mirip
        if sad_value < best_match[1]:
            best_match = (nama_kartu, sad_value)
    
    kartu_terklasifikasi = best_match[0]  # Ambil nama kartu
    sad_value = best_match[1]  # Ambil nilai SAD terkecil (semakin kecil = semakin mirip)
    
    # Normalisasi SAD menjadi confidence (0-1)
    max_possible_sad = threshold_warped.shape[0] * threshold_warped.shape[1] * 255.0
    confidence = 1.0 - (sad_value / max_possible_sad)
    confidence = max(0.0, min(1.0, confidence))
    
    # Jika confidence terlalu rendah, kartu tidak diketahui
    if confidence < 0.6:
        kartu_terklasifikasi = "tidak tau"
    
    return kartu_terklasifikasi, confidence

# Inisialisasi: memuat 52 template kartu ke memori
Folder = r"C:\Users\aaron\Downloads\individual_cards_2"
RANKS = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
SUITS = ["Spade","Heart","Diamond","Club"]
kartu_template = {}
lebar, tinggi = 300, 420  # Ukuran standar kartu setelah di-warp

print(f"Nama folder: {Folder}")

# Loop untuk memuat semua template kartu
for suit in SUITS:
    for rank in RANKS:
        nama_kartu = f"{rank} {suit}"
        namafile = f"{rank}_{suit}.jpg"
        path = os.path.join(Folder, namafile)
        template = cv2.imread(path)
        
        if template is None:
            print(f"error {namafile} gaada di {Folder}")
            continue
        
        # Preprocessing template: resize, grayscale, threshold
        Resized = cv2.resize(template, (lebar, tinggi))
        template_gray = cv2.cvtColor(Resized, cv2.COLOR_BGR2GRAY)
        _, template_thresh = cv2.threshold(template_gray, 150, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        kartu_template[nama_kartu] = template_thresh

print(f"total: {len(kartu_template)}")



cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("kamera ga fungsi")
    
lebarkamerakartu = 300
tinggikamerakartu = 420

# Titik tujuan untuk perspective warp (4 pojok persegi panjang 300x420)
dst_pts = np.array([
    [0, 0],  # Kiri atas
    [lebarkamerakartu - 1, 0],  # Kanan atas
    [lebarkamerakartu - 1, tinggikamerakartu - 1],  # Kanan bawah
    [0, tinggikamerakartu - 1]  # Kiri bawah
], dtype="float32")

# Loop utama: deteksi kartu dari setiap frame kamera
while True:
    ret, frame = cap.read()
    
    if not ret:
        print('kamera errorr')
        break
    
    img_output = frame.copy()
    img_tinggi, img_lebar = frame.shape[:2]
    scale_down = 0.5  # Perkecil frame untuk mempercepat proses
    
    # Resize frame jika diperlukan
    if scale_down != 1.0:
        resized_frame = cv2.resize(
            frame, 
            (int(img_lebar * scale_down), int(img_tinggi * scale_down)), 
            interpolation=cv2.INTER_AREA
        )
    else:
        resized_frame = frame.copy()
    
    # Preprocessing: grayscale → blur → deteksi tepi (Canny)
    imgbaru_tinggi, imgbaru_lebar = resized_frame.shape[:2]
    gray = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    edges = cv2.Canny(blur, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Tampilkan kontur untuk debugging
    gambar_contour = resized_frame.copy()
    cv2.drawContours(gambar_contour, contours, -1, (0,255,0), 1)
    
    # Filter kontur berdasarkan area minimum
    area_kartumin = (imgbaru_lebar * imgbaru_tinggi) / 150
    
    cv2.imshow("Kontur", gambar_contour)
    cv2.imshow('edges', edges)
    #cv2.imshow('blur' , blur)
    
    kartu_terdeteksi = []
    
    # Deteksi kartu: cari kontur yang berbentuk segiempat (4 pojok)
    for c_resized in contours:
        area = cv2.contourArea(c_resized)
        
        # Filter kontur berdasarkan area minimum
        if area > area_kartumin:
            peri = cv2.arcLength(c_resized, True)
            approx_resized = cv2.approxPolyDP(c_resized, 0.02 * peri, True)  # Aproksimasi poligon
            
            # Cek apakah kontur punya 4 pojok (bentuk kartu)
            if len(approx_resized) == 4:
                # Kembalikan ke ukuran frame asli
                approx_original = (approx_resized / scale_down).astype(np.int32)
                src_pts = titik(approx_original.reshape(4,2))  # Urutkan 4 pojok
                
                # Perspective warp: luruskan kartu miring menjadi lurus
                # cv2.getPerspectiveTransform menghitung matriks transformasi 3x3
                # src_pts = 4 pojok kartu miring di frame kamera (input)
                # dst_pts = 4 pojok persegi panjang lurus 300x420 (output)
                # m = matriks transformasi yang akan mengubah src_pts menjadi dst_pts
                m = cv2.getPerspectiveTransform(src_pts, dst_pts)
                # Aplikasikan transformasi: ubah kartu miring jadi lurus dengan ukuran 300x420
                w_kartu = cv2.warpPerspective(frame, m, (lebar, tinggi))
                
                # Klasifikasi kartu menggunakan SAD
                klasifikasi_teks, confidence = klasifikasi_kartu(w_kartu, kartu_template)
                
                cv2.imshow("kartu ke warp", w_kartu)
                
                # Simpan info kartu yang terdeteksi
                kartu_terdeteksi.append({
                    'contour': approx_original,
                    'klasifikasi': klasifikasi_teks,
                    'confidence': confidence
                })
    
    # Tampilkan hasil: gambar kotak dan label di setiap kartu yang terdeteksi
    for info_kartu in kartu_terdeteksi:
        contour = info_kartu['contour']
        klasifikasi_teks = info_kartu['klasifikasi']
        confidence = info_kartu['confidence']
        
        # Gambar kotak hijau di sekitar kartu
        warna_contour = (0, 255, 0)
        cv2.drawContours(img_output, [contour], -1, warna_contour, 2)
        
        # Hitung pusat kartu untuk posisi teks
        m_cnt = cv2.moments(contour)
        
        if m_cnt['m00'] != 0:
            cX = int(m_cnt['m10'] / m_cnt['m00'])  # Centroid X
            cY = int(m_cnt['m01'] / m_cnt['m00'])  # Centroid Y
            
            # Tampilkan nama kartu dan confidence
            cv2.putText(img_output, klasifikasi_teks, (cX - 50, cY),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            cv2.putText(img_output, f'confidence: {confidence:.2f}', 
                       (cX - 50, cY + 20), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 255), 1)
    
    cv2.imshow('kartu', img_output)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()

