import numpy as np
import cv2
from PIL import Image
from rembg import remove
import io

def process_sticker(raw_img, outline_thickness=30, upscale_factor=4):
    """
    1. Arka planı siler.
    2. Gri pikselleri temizler.
    3. Görseli 4x büyütür.
    4. Pürüzsüz (Jilet) beyaz kontur ekler.
    """
    
    # --- ADIM 1: Arka Plan Silme ---
    # rembg kullanarak şeffaf hale getiriyoruz
    no_bg_img = remove(raw_img)
    
    # --- ADIM 2: Kenar Temizliği (Gri Çizgi Önleme) ---
    # rembg bazen kenarda yarı şeffaf pislik bırakır, onları threshold ile kesiyoruz
    img_array = np.array(no_bg_img)
    alpha = img_array[:, :, 3]
    _, alpha_clean = cv2.threshold(alpha, 127, 255, cv2.THRESH_BINARY)
    img_array[:, :, 3] = alpha_clean
    clean_img = Image.fromarray(img_array)

    # --- ADIM 3: Upscale (Önce Büyütme) ---
    # Konturu büyük resimde çizersek daha yuvarlak ve pürüzsüz olur
    w, h = clean_img.size
    upscaled_img = clean_img.resize((w * upscale_factor, h * upscale_factor), resample=Image.LANCZOS)
    
    # --- ADIM 4: Jilet Kontur (OpenCV) ---
    # Büyütülmüş resim üzerinde çalışıyoruz
    img_arr_big = np.array(upscaled_img)
    alpha_big = img_arr_big[:, :, 3]
    
    # Kalınlığı ölçeğe göre ayarla (4x büyüttüğümüz için 30 -> 120px olur)
    kernel_size = outline_thickness * upscale_factor // 4
    # Dairesel kernel ile yumuşak köşeler sağlıyoruz
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    
    # Maskeyi genişlet (Beyaz alan oluştur)
    dilated = cv2.dilate(alpha_big, kernel, iterations=1)
    
    # Kenar Yumuşatma (Anti-Aliasing Hilesi)
    # Önce bulandırıyoruz, sonra sert bir eşikleme ile pürüzsüzleştiriyoruz
    blur_amount = 11
    smoothed = cv2.GaussianBlur(dilated, (blur_amount, blur_amount), 0)
    _, final_mask = cv2.threshold(smoothed, 120, 255, cv2.THRESH_BINARY)
    
    # --- ADIM 5: Birleştirme ---
    # Beyaz katmanı oluştur
    outline_layer = np.zeros_like(img_arr_big)
    outline_layer[final_mask > 0] = [255, 255, 255, 255] # Beyaz renk
    
    # Orijinal (büyütülmüş) resmi beyaz katmanın üzerine yapıştır
    final_outline_img = Image.fromarray(outline_layer)
    final_outline_img.paste(upscaled_img, (0, 0), upscaled_img)
    
    return final_outline_img