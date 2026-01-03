import time
from huggingface_hub import InferenceClient

# En hızlı ve en çok kullanılan modelleri sıraladık
MODEL_POOL = [
    "stabilityai/sd-turbo",
    "runwayml/stable-diffusion-v1-5",
    "prompthero/openjourney",
    "CompVis/stable-diffusion-v1-4",
    "stabilityai/stable-diffusion-xl-base-1.0"
]

def generate_sticker_image(prompt, hf_token, status_placeholder):
    """
    Kullanıcının yazdığı promptu HİÇBİR DEĞİŞİKLİK YAPMADAN gönderir.
    """
    # Ustamın isteği üzerine: Prompt olduğu gibi gidiyor (RAW)
    raw_prompt = prompt 
    
    for model_id in MODEL_POOL:
        model_name = model_id.split('/')[-1]
        
        for attempt in range(1, 6):
            status_placeholder.info(f"🕵️ **Human Mode:** Trying `{model_name}` | Attempt {attempt}/5")
            
            try:
                client = InferenceClient(model=model_id, token=hf_token, timeout=60)
                image = client.text_to_image(raw_prompt)
                
                if image:
                    status_placeholder.success(f"✅ Success with `{model_name}`")
                    return image
            
            except Exception as e:
                err = str(e)
                # Token hatalıysa hemen durdur
                if "401" in err:
                    status_placeholder.error("❌ TOKEN HATALI! Lütfen Hugging Face Token'ınızı kontrol edin.")
                    return "TOKEN_ERROR"
                
                # Model yükleniyorsa (503) veya limit dolduysa (429)
                if attempt < 5:
                    status_placeholder.warning(f"⏳ `{model_name}` is loading or busy. (Error: {err[:40]}...) Waiting 20s.")
                    time.sleep(20)
                else:
                    status_placeholder.error(f"❌ `{model_name}` failed after 5 attempts.")
                    break # Diğer modele geç
                    
    return None