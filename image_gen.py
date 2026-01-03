import time
import requests
import random
from huggingface_hub import InferenceClient

# --- DEV MODEL HAVUZU (Hugging Face) ---
HF_MODELS = [
    "black-forest-labs/FLUX.1-schnell",          # En yeni ve hızlı
    "stabilityai/stable-diffusion-xl-base-1.0",  # Klasik kalite
    "stabilityai/sd-turbo",                      # Çok hızlı
    "runwayml/stable-diffusion-v1-5",            # Çok stabil
    "prompthero/openjourney",                    # Artistik
    "Lykon/DreamShaper-v8",                      # Popüler
    "SG161222/RealVisXL_V4.0",                   # Foto-gerçekçi
    "digiplay/AbsoluteReality_v1.8.1",           # Keskin detaylar
    "CompVis/stable-diffusion-v1-4",             # Eski ama sağlam
    "stabilityai/stable-diffusion-3-medium-diffusers", # SD3 denemesi
    "dataautogpt3/OpenDalleV1.1",                # Dalle tarzı
    "XpucT/Realistic_Vision_V5.1"                # Sticker için yüksek kontrast
]

def generate_sticker_image(prompt, hf_token, status_placeholder):
    """
    Sırasıyla Hugging Face modellerini ve en son Pollinations motorunu dener.
    """
    
    # --- 1. AŞAMA: HUGGING FACE MODELLERİNİ TARA ---
    for model_id in HF_MODELS:
        model_name = model_id.split('/')[-1]
        
        # Her model için 2 kez "Human Mode" denemesi (Bekleyerek)
        for attempt in range(1, 3):
            status_placeholder.info(f"🕵️ HF Mode: `{model_name}` | Attempt {attempt}/2")
            
            try:
                client = InferenceClient(model=model_id, token=hf_token, timeout=45)
                image = client.text_to_image(prompt)
                
                if image:
                    status_placeholder.success(f"✅ Success with HF Model: `{model_name}`")
                    return image
            except Exception as e:
                err = str(e)
                if "401" in err: return "TOKEN_ERROR"
                
                # Eğer model meşgulse biraz bekle, değilse diğer modele geçmek için kısa mola
                if "503" in err or "429" in err:
                    status_placeholder.warning(f"⏳ `{model_name}` busy, waiting 15s...")
                    time.sleep(15)
                else:
                    time.sleep(2)
                continue

    # --- 2. AŞAMA: POLLINATIONS.AI (Yıkılmaz Yedek) ---
    status_placeholder.warning("⚠️ HF Models exhausted. Switching to Pollinations.ai...")
    
    for attempt in range(1, 6):
        status_placeholder.info(f"🚀 Pollinations Mode | Attempt {attempt}/5")
        try:
            seed = random.randint(1, 999999)
            # Pollinations için URL yapılandırması
            encoded_prompt = requests.utils.quote(prompt)
            # Sticker için gizli takviye (Sadece burada, işi garantiye almak için)
            poll_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}%20sticker%20white%20background?width=1024&height=1024&seed={seed}&nologo=true"
            
            response = requests.get(poll_url, timeout=60)
            if response.status_code == 200 and len(response.content) > 10000:
                from PIL import Image
                import io
                image = Image.open(io.BytesIO(response.content))
                status_placeholder.success(f"✅ Success with Pollinations!")
                return image
            else:
                time.sleep(10)
        except Exception as e:
            status_placeholder.error(f"Pollinations Error: {str(e)[:50]}")
            time.sleep(10)

    status_placeholder.error(f"💀 All 20+ attempts failed for: '{prompt}'")
    return None