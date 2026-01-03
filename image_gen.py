import time
from huggingface_hub import InferenceClient

# Model Havuzu (En stabil olanlar üstte)
MODEL_POOL = [
    "runwayml/stable-diffusion-v1-5",
    "prompthero/openjourney",
    "CompVis/stable-diffusion-v1-4",
    "stabilityai/stable-diffusion-xl-base-1.0",
    "stabilityai/sd-turbo"
]

def generate_sticker_image(prompt, hf_token, status_placeholder):
    """
    HUMAN MODE: Bir insan gibi sabırla bekler ve modelleri zorlar.
    """
    refined_prompt = f"sticker design of {prompt}, isolated on white background, white border, vector art, high contrast, sharp edges, 4k"
    
    # Her bir model için döngü
    for model_id in MODEL_POOL:
        model_name = model_id.split('/')[-1]
        
        # AYNI MODELDE 5 KEZ DENEME (Ustamın İsteği)
        for attempt in range(1, 6):
            status_placeholder.info(f"🕵️ **Human Mode:** Trying `{model_name}` | Attempt {attempt}/5 for: '{prompt}'")
            
            try:
                client = InferenceClient(model=model_id, token=hf_token)
                image = client.text_to_image(refined_prompt)
                
                if image:
                    status_placeholder.success(f"✅ Success! Image fetched from `{model_name}`")
                    return image # Görseli bulduğumuz an fonksiyondan çıkarız
            
            except Exception as e:
                err = str(e)
                
                # Eğer Token hatalıysa hiç bekleme (401)
                if "401" in err:
                    status_placeholder.error("❌ Critical: Token Invalid. Check Secrets.")
                    return "TOKEN_ERROR"
                
                # Model meşgulse veya yükleniyorsa (503 / 429 vb.)
                # Ustamın istediği 20 saniyelik "İnsan Sabrı" molası
                if attempt < 5:
                    status_placeholder.warning(f"⏳ `{model_name}` is busy or sleeping. Mimicking human wait (20s)...")
                    time.sleep(20)
                else:
                    # 5 deneme de bittiyse bir sonraki modele geçeceğiz
                    status_placeholder.error(f"❌ `{model_name}` failed after 5 attempts. Switching to next model...")
                    time.sleep(5) 
                    break # İçteki deneme döngüsünden çıkar, bir sonraki modele geçer

    # Tüm modeller ve tüm denemeler bittiyse
    status_placeholder.error(f"💀 All nodes exhausted. Could not generate: '{prompt}'")
    return None