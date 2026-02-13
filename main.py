from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="PROMPT GENK V4 - Veo 3 Professional")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=API_KEY)

def generate_veo3_prompt(data):
    """Membangun prompt Veo 3 dengan struktur profesional"""
    
    # Format shot type
    shot_map = {
        "Extreme Wide": "Extreme wide establishing shot",
        "Wide": "Wide shot",
        "Medium": "Medium shot",
        "Close Up": "Close-up shot",
        "Extreme Close Up": "Extreme close-up macro shot"
    }
    shot = shot_map.get(data['shot_type'], "Wide shot")
    
    # Format camera angle
    angle_map = {
        "Eye Level": "at eye level",
        "Low Angle": "from low angle looking up",
        "High Angle": "from high angle looking down",
        "Overhead": "directly overhead",
        "Dutch Angle": "with tilted Dutch angle"
    }
    angle = angle_map.get(data['camera_angle'], "at eye level")
    
    # Format camera movement
    movement_map = {
        "Static": "locked-off static camera",
        "Slow Dolly": "slow dolly-in",
        "Slow Push": "slow push-in",
        "Tracking": "tracking shot following the action",
        "Crane": "smooth crane up",
        "Handheld": "subtle handheld sway for documentary feel",
        "Rack Focus": "rack focus pulling from foreground to background"
    }
    movement = movement_map.get(data['camera_movement'], "locked-off static camera")
    
    # Format lens
    lens_map = {
        "35mm": "35mm anamorphic lens",
        "50mm": "50mm prime lens",
        "85mm": "85mm portrait lens with shallow depth of field",
        "100mm Macro": "100mm macro lens with extreme close-up capability",
        "24mm": "24mm wide-angle lens for environmental context"
    }
    lens = lens_map.get(data['lens'], "50mm prime lens")
    
    # Bangun prompt untuk Model 1
    model1_desc = f"{data['model1_name']}, {data['model1_desc']}, wearing {data['model1_clothing']}"
    
    # Bangun prompt untuk Model 2
    model2_desc = ""
    if data['model2_name'] and data['model2_desc']:
        model2_desc = f"alongside {data['model2_name']}, {data['model2_desc']}, wearing {data['model2_clothing']}"
    
    # Format dialog sesuai aturan Veo 3
    dialog_veo3 = ""
    if data['dialog1'] and data['dialog2']:
        # Multi-character dialogue dengan format titik dua
        dialog_veo3 = f'{data["model1_name"]} says: "{data["dialog1"]}" {data["model2_name"]} responds: "{data["dialog2"]}"'
    elif data['dialog1']:
        dialog_veo3 = f'{data["model1_name"]} says: "{data["dialog1"]}"'
    
    # Format environment
    environment = f"{data['tempat']}, {data['detail_tempat']}"
    
    # Format lighting
    lighting = f"{data['lighting']}, {data['suasana']}"
    
    # Format action
    action = data['adegan']
    
    # Bangun prompt lengkap
    prompt_parts = [
        f"{shot} {angle} using {lens},",
        f"the camera {movement}.",
        f"{model1_desc} {model2_desc}",
        f"in a {environment}.",
        f"They {action}.",
        f"Lighting: {lighting}.",
        f"Style: {data['gaya_visual']}, cinematic, 4k, photorealistic.",
        f"Audio: {data['audio_desc']}."
    ]
    
    # Gabungkan dengan koma dan spasi
    full_prompt = " ".join(prompt_parts)
    
    # Tambahkan dialog dengan format khusus
    if dialog_veo3:
        full_prompt += f" {dialog_veo3}"
    
    return full_prompt

@app.get("/")
def root():
    return {"message": "PROMPT GENK V4 - Veo 3 Professional siap!"}

@app.post("/generate-prompt")
async def generate_prompt(
    # Shot & Camera
    shot_type: str = Form(...),
    camera_angle: str = Form(...),
    camera_movement: str = Form(...),
    lens: str = Form(...),
    
    # Model 1
    model1_name: str = Form(...),
    model1_desc: str = Form(...),
    model1_clothing: str = Form(...),
    
    # Model 2 (opsional)
    model2_name: str = Form(""),
    model2_desc: str = Form(""),
    model2_clothing: str = Form(""),
    
    # Dialog
    dialog1: str = Form(""),
    dialog2: str = Form(""),
    
    # Scene
    tempat: str = Form(...),
    detail_tempat: str = Form(...),
    adegan: str = Form(...),
    
    # Visual
    lighting: str = Form(...),
    suasana: str = Form(...),
    gaya_visual: str = Form(...),
    
    # Audio
    audio_desc: str = Form(...)
):
    try:
        # Kumpulkan data
        form_data = {
            'shot_type': shot_type,
            'camera_angle': camera_angle,
            'camera_movement': camera_movement,
            'lens': lens,
            'model1_name': model1_name,
            'model1_desc': model1_desc,
            'model1_clothing': model1_clothing,
            'model2_name': model2_name,
            'model2_desc': model2_desc,
            'model2_clothing': model2_clothing,
            'dialog1': dialog1,
            'dialog2': dialog2,
            'tempat': tempat,
            'detail_tempat': detail_tempat,
            'adegan': adegan,
            'lighting': lighting,
            'suasana': suasana,
            'gaya_visual': gaya_visual,
            'audio_desc': audio_desc
        }
        
        # Generate prompt Veo 3
        veo3_prompt = generate_veo3_prompt(form_data)
        
        # Opsional: Minta Gemini menyempurnakan prompt
        perfection_prompt = f"""
Sempurnakan prompt Veo 3 berikut agar lebih profesional dan sesuai standar Google Veo 3.
Prompt saat ini:
{veo3_prompt}

Tingkatkan dengan:
1. Tambahkan detail visual yang lebih spesifik
2. Pastikan format dialog menggunakan titik dua (:) untuk menghindari subtitle
3. Optimalkan untuk video 8-10 detik
4. Gunakan bahasa sinematik

Berikan prompt final tanpa penjelasan tambahan.
"""
        
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=perfection_prompt
        )
        
        return JSONResponse(content={
            "success": True,
            "prompt": response.text.strip()
        })
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)