import time
from huggingface_hub import InferenceClient

# Kullanacağımız Model Havuzu
MODEL_POOL = [
    "stabilityai/stable-diffusion-xl-base-1.0",
    "runwayml/stable-diffusion-v1-5",
    "prompthero/openjourney",
    "CompVis/stable-diffusion-v1-4",
    "stabilityai/sd-turbo"
]

def generate_sticker_image(prompt, hf_token, status_placeholder):
    """
    Hugging Face API üzerinden görsel üretir. 
    Hata durumunda havuzdaki diğer modelleri dener.
    """
    # Kullanıcı promptunu sticker için teknik olarak zenginleştiriyoruz
    refined_prompt = f"sticker design of {prompt}, isolated on white background, white border, vector art, high contrast, sharp edges, 300 dpi"
    
    # Bulldog Logic: 2 Tur, her turda tüm modelleri dene
    for round_num in range(2):
        for model_id in MODEL_POOL:
            status_placeholder.markdown(f"🔄 **[Round {round_num+1}]** Connecting to: `{model_id.split('/')[-1]}`")
            
            try:
                client = InferenceClient(model=model_id, token=hf_token)
                # Görsel üretim isteği
                image = client.text_to_image(refined_prompt)
                
                if image:
                    return image # Başarılıysa resmi döndür
                    
            except Exception as e:
                # Hata koduna göre analiz yapalım
                error_msg = str(e)
                if "401" in error_msg:
                    status_placeholder.error("❌ Invalid Token! Check your secrets.")
                    return "TOKEN_ERROR"
                
                # Diğer hatalarda (busy, 503 vb.) 20 saniye bekle ve devam et
                status_placeholder.warning(f"⚠️ Model busy. Cooldown 20s...")
                time.sleep(20)
                continue
                
    return None # Hiçbir modelden sonuç alınamazsa