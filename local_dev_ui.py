import os
import random
import numpy as np
import torch
import gradio as gr
from chatterbox.tts import ChatterboxTTS

# Set environment variable for MPS fallback before importing torch
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

# Detect device - use CPU for better compatibility on Mac
if torch.cuda.is_available():
    DEVICE = "cuda"
elif torch.backends.mps.is_available():
    # For now, use CPU instead of MPS due to compatibility issues
    # DEVICE = "mps"
    DEVICE = "cpu"
    print("MPS is available but using CPU for better compatibility")
else:
    DEVICE = "cpu"

print(f"Using device: {DEVICE}")

def set_seed(seed: int):
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    random.seed(seed)
    np.random.seed(seed)

def load_model():
    try:
        print("Loading Chatterbox TTS model...")
        model = ChatterboxTTS.from_pretrained(device=DEVICE)
        print("Model loaded successfully!")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

def generate(model, text, audio_prompt_path, exaggeration, temperature, seed_num, cfgw):
    try:
        if model is None:
            print("Loading model...")
            model = ChatterboxTTS.from_pretrained(device=DEVICE)

        if not text or len(text.strip()) == 0:
            return None

        if len(text) > 300:
            text = text[:300]
            print("Text truncated to 300 characters")

        if seed_num != 0:
            set_seed(int(seed_num))

        print(f"Generating audio for: {text[:50]}...")
        wav = model.generate(
            text,
            audio_prompt_path=audio_prompt_path,
            exaggeration=exaggeration,
            temperature=temperature,
            cfg_weight=cfgw,
        )
        print("Audio generated successfully!")
        return (model.sr, wav.squeeze(0).numpy())
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None

# Create the Gradio interface
with gr.Blocks(title="Chatterbox TTS - Mac Version") as demo:
    model_state = gr.State(None)  # Loaded once per session/user

    gr.HTML("<h1 style='text-align: center; color: #2563eb;'>🎙️ Chatterbox TTS - Mac Version</h1>")
    gr.HTML("<p style='text-align: center;'>High-quality Text-to-Speech with emotion control</p>")
    gr.HTML(f"<p style='text-align: center;'><strong>Device:</strong> {DEVICE}</p>")

    with gr.Row():
        with gr.Column():
            text = gr.Textbox(
                value="Hello! This is Chatterbox TTS running on your Mac. I can generate natural-sounding speech with emotion control.",
                label="Text to synthesize (max 300 characters)",
                max_lines=5
            )
            
            with gr.Row():
                with gr.Column():
                    exaggeration = gr.Slider(
                        0.25, 2, 
                        step=0.05, 
                        label="Exaggeration", 
                        value=0.5,
                        info="Higher values = more expressive"
                    )
                with gr.Column():
                    cfg_weight = gr.Slider(
                        0.0, 1, 
                        step=0.05, 
                        label="CFG/Pace", 
                        value=0.5,
                        info="Lower values = slower speech"
                    )

            ref_wav = gr.Audio(
                sources=["upload", "microphone"], 
                type="filepath", 
                label="Reference Audio (optional)", 
                value=None
            )

            with gr.Accordion("Advanced Settings", open=False):
                temp = gr.Slider(0.05, 2, step=0.05, label="Temperature", value=0.8)
                seed_num = gr.Number(value=0, label="Random seed (0 for random)")

            run_btn = gr.Button("🎙️ Generate Audio", variant="primary", size="lg")

        with gr.Column():
            audio_output = gr.Audio(label="Generated Audio")
            
            with gr.Accordion("Tips", open=True):
                gr.HTML("""
                <ul>
                <li><strong>Default settings</strong> work well for most text</li>
                <li><strong>Lower CFG/Pace</strong> for slower, more deliberate speech</li>
                <li><strong>Higher Exaggeration</strong> for more dramatic speech</li>
                <li><strong>Reference Audio</strong> to clone a specific voice (optional)</li>
                </ul>
                """)

    # Load model when app starts
    demo.load(fn=load_model, inputs=[], outputs=model_state)

    # Connect the generate button
    run_btn.click(
        fn=generate,
        inputs=[
            model_state,
            text,
            ref_wav,
            exaggeration,
            temp,
            seed_num,
            cfg_weight,
        ],
        outputs=audio_output,
    )

if __name__ == "__main__":
    print("Starting Chatterbox TTS Gradio App...")
    demo.queue(max_size=10, default_concurrency_limit=1).launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True
    ) 