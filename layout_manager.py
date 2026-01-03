import io
import zipfile
import math
from PIL import Image

def get_grid_dims(layout_mode):
    """Layout moduna göre sütun ve satır sayısını jilet gibi belirler."""
    grid_map = {
        1: (1, 1),   # 1x1
        2: (1, 2),   # 1 sütun, 2 satır (Dikey)
        4: (2, 2),   # 2x2
        6: (2, 3),   # 2 sütun, 3 satır
        9: (3, 3),   # 3x3
        12: (3, 4)   # 3 sütun, 4 satır
    }
    return grid_map.get(layout_mode, (2, 3)) # Varsayılan 6'lı

def create_custom_sheets(processed_images, canvas_w, canvas_h, layout_mode):
    """
    Stickerları profesyonel ızgara düzenine göre sayfalara dizer.
    """
    sheets = []
    total_images = len(processed_images)
    num_sheets = math.ceil(total_images / layout_mode)
    
    cols, rows = get_grid_dims(layout_mode)
    
    # Hücre boyutlarını hesapla
    cell_w = canvas_w // cols
    cell_h = canvas_h // rows

    for s in range(num_sheets):
        # Şeffaf dev tuval
        canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        
        start_idx = s * layout_mode
        end_idx = min(start_idx + layout_mode, total_images)
        current_batch = processed_images[start_idx:end_idx]
        
        for idx, img in enumerate(current_batch):
            # Padding: Hücreden %15 küçük olsun (Kesim payı)
            max_w = int(cell_w * 0.85)
            max_h = int(cell_h * 0.85)
            
            # Kaliteyi bozmadan hücreye sığdır
            img_thumb = img.copy()
            img_thumb.thumbnail((max_w, max_h), Image.LANCZOS)
            
            # Izgara koordinatları
            c = idx % cols
            r = idx // cols
            
            # Merkezleme hesapla
            x_offset = c * cell_w + (cell_w - img_thumb.width) // 2
            y_offset = r * cell_h + (cell_h - img_thumb.height) // 2
            
            canvas.paste(img_thumb, (x_offset, y_offset), img_thumb)
        
        sheets.append(canvas)
    
    return sheets

def export_to_zip(individual_stickers, final_sheets):
    """
    İçeriği 'Klasör' yapısında tertemiz bir ZIP paketine dönüştürür.
    """
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        # 1. Klasör: Tekli jilet stickerlar
        for idx, img in enumerate(individual_stickers):
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            # ZIP içinde klasör yapısı oluşturuyoruz:
            zip_file.writestr(f"individual_stickers/sticker_{idx+1}.png", img_byte_arr.getvalue())
            
        # 2. Klasör: Baskıya hazır dizili sayfalar
        for idx, sheet in enumerate(final_sheets):
            sheet_byte_arr = io.BytesIO()
            sheet.save(sheet_byte_arr, format='PNG')
            zip_file.writestr(f"print_ready_sheets/full_sheet_{idx+1}.png", sheet_byte_arr.getvalue())
            
    return zip_buffer.getvalue()