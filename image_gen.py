import time
from huggingface_hub import InferenceClient

MODEL_POOL = [
    "stabilityai/sd-turbo",
    "runwayml/stable-diffusion-v1-5",
    "prompthero/openjourney",
    "CompVis/stable-diffusion-v1-4",
    "stabilityai/stable-diffusion-xl-base-1.0"
]

def generate_sticker_image(prompt, hf_token, status_placeholder):
    """
    hf_token: app.py'den gelen şifre.
    """
    for model_id in MODEL_POOL:
        model_name = model_id.split('/')[-1]
        
        for attempt in range(1, 6):
            status_placeholder.info(f"🕵️ Human Mode: Trying `{model_name}` | Attempt {attempt}/5")
            
            try:
                # 3. ADIM: TOKEN'I BURADA KULLANIYORUZ
                client = InferenceClient(model=model_id, token=hf_token, timeout=60)
                image = client.text_to_image(prompt) # RAW Prompt
                
                if image:
                    return image
            
            except Exception as e:
                err = str(e)
                if "401" in err:
                    return "TOKEN_ERROR" # Token yanlışsa app.py'ye haber ver
                
                time.sleep(20) # İnsan gibi bekle
                continue
                
    return None