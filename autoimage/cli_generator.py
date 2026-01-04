#!/usr/bin/env python3
"""
CLI version of H5P Generator
Usage: python cli_generator.py --transcript transcript.txt --video-url "https://..." --title "My Video"
"""

import argparse
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

import booklet_generator_v2 as booklet_generator
import utils_booklet_iframe as utils_booklet
import utils_image_gen

# Load environment
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ Error: GEMINI_API_KEY not found in .env file")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)

PROJECT_ROOT = Path(__file__).parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
TEMPLATE_ZIP_PATH = TEMPLATES_DIR / "template.zip"

# --- Gemini Functions (same as orchestrator_v2.py) ---

def clean_json_response(text: str) -> str:
    """Remove markdown code blocks from Gemini response"""
    text = text.strip()
    if text.startswith("```json"):
        text = text.split("```json")[1].split("```")[0].strip()
    elif text.startswith("```"):
        text = text.split("```")[1].split("```")[0].strip()
    return text

def generate_intro_content(transcript: str, video_title: str, video_url: str, model_name: str = "gemini-flash-latest") -> dict:
    prompt = f"""Analyze this video transcript and create an engaging introduction for an H5P Interactive Book.

Video Title: {video_title}
Video URL: {video_url}

Transcript:
{transcript[:3000]}...

Generate a JSON object with:
{{
  "title": "Main title for the introduction (h2 heading)",
  "welcome_text": "2-3 sentences welcoming learners and introducing the topic",
  "learning_objectives": ["objective 1", "objective 2", "objective 3"],
  "workflow": ["step 1", "step 2", "step 3", "step 4"]
}}

Make it engaging and specific to the video content. Use German language."""

    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    return json.loads(clean_json_response(response.text))

def generate_memory_prompts(transcript: str, model_name: str = "gemini-flash-latest") -> list:
    prompt = f"""Analyze this transcript and identify 6 key concepts, people, or events that learners should remember BEFORE watching the video.

Transcript:
{transcript}

Generate a JSON array with 6 objects:
[
  {{
    "prompt": "Name or concept (for image search)",
    "match_text": "Short German description (max 7 words)"
  }}
]

Focus on visual, memorable elements. Return ONLY the JSON array."""

    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    return json.loads(clean_json_response(response.text))

def generate_video_summary(transcript: str, model_name: str = "gemini-flash-latest") -> list:
    prompt = f"""Analyze this transcript and create a structured summary as an accordion with 5-7 main points.

Transcript:
{transcript}

Generate a JSON array:
[
  {{
    "title": "Event/Topic headline",
    "text": "<p>Detailed explanation (2-3 sentences) with HTML formatting</p>"
  }}
]

Return ONLY the JSON array."""

    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    return json.loads(clean_json_response(response.text))

def generate_quiz_questions(transcript: str, model_name: str = "gemini-flash-latest") -> list:
    prompt = f"""Create 10 assessment questions based on this transcript: 6 Multiple Choice and 4 True/False.

Transcript:
{transcript}

Generate JSON:
[
  {{
    "type": "multichoice",
    "question": "Question text?",
    "answers": [
      {{"text": "Correct answer", "correct": true, "feedback": "✔️ Richtig. Explanation."}},
      {{"text": "Wrong answer", "correct": false, "feedback": "❌ Falsch. Explanation."}}
    ]
  }}
]

Return ONLY the JSON array with exactly 10 questions."""

    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    return json.loads(clean_json_response(response.text))

def generate_cloze_tasks(transcript: str, model_name: str = "gemini-flash-latest") -> list:
    prompt = f"""Create 2 cloze exercises (drag text) based on this transcript.

Transcript:
{transcript}

Generate JSON:
[
  {{
    "description": "Task instruction",
    "text_content": "Text with *Answer:Hint* gaps",
    "distractors": "*Distractor1* *Distractor2*"
  }}
]

Return ONLY the JSON array with exactly 2 tasks."""

    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    return json.loads(clean_json_response(response.text))

# --- Main Generation Pipeline ---

def generate_h5p_package(transcript: str, video_title: str, video_url: str, 
                         output_path: str, cover_image_path: str = None,
                         model_name: str = "gemini-flash-latest"):
    """
    Complete pipeline to generate H5P package from transcript
    """
    
    print("🚀 Starting H5P generation pipeline...")
    print(f"📝 Model: {model_name}")
    print()
    
    # Step 1: Introduction
    print("1/6 Generating introduction...")
    intro_data = generate_intro_content(transcript, video_title, video_url, model_name)
    print(f"   ✓ Title: {intro_data['title']}")
    
    # Step 2: Memory Game
    print("2/6 Generating memory game prompts...")
    memory_prompts = generate_memory_prompts(transcript, model_name)
    print(f"   ✓ Generated {len(memory_prompts)} pairs")
    
    print("   🎨 Downloading images from Wikimedia...")
    temp_dir = Path("./temp_generation")
    temp_dir.mkdir(exist_ok=True)
    
    h5p_memory_cards, image_files = utils_image_gen.generate_memory_assets(
        memory_prompts, temp_dir, use_collage=False, collage_count=4
    )
    print(f"   ✓ Generated {len(image_files)} image files")
    
    # Step 3: Video Summary
    print("3/6 Generating video summary...")
    summary_data = generate_video_summary(transcript, model_name)
    print(f"   ✓ Created {len(summary_data)} summary points")
    
    # Step 4: Quiz
    print("4/6 Generating quiz questions...")
    quiz_data = generate_quiz_questions(transcript, model_name)
    print(f"   ✓ Created {len(quiz_data)} questions")
    
    # Step 5: Cloze
    print("5/6 Generating cloze exercises...")
    cloze_data = generate_cloze_tasks(transcript, model_name)
    print(f"   ✓ Created {len(cloze_data)} cloze tasks")
    
    # Step 6: Package Creation
    print("6/6 Creating H5P package...")
    
    # Build chapters
    chapters_data = [
        {"type": "introduction", "data": intro_data},
        {"type": "memory_game", "title": "Memory-Spiel", 
         "instruction": "Ordnen Sie die Begriffe den passenden Beschreibungen zu.",
         "cards": h5p_memory_cards},
        {"type": "video_page", "title": "Video & Zusammenfassung",
         "video": {"url": video_url, "width": 800, "height": 400},
         "summary_accordion": summary_data},
        {"type": "question_set", "title": "Verständnisfragen",
         "intro_screen": {"title": "Verständnisfragen", 
                         "text": "Testen Sie Ihr Wissen zum Video.",
                         "background_image": "images/quiz_bg.png"},
         "questions": quiz_data},
        {"type": "cloze_set", "title": "Lückentexte",
         "intro_screen": {"title": "Lückentexte",
                         "text": "Ziehen Sie die passenden Wörter in die Lücken.",
                         "background_image": "images/cloze_bg.png"},
         "tasks": cloze_data}
    ]
    
    # Prepare files
    extra_files = []
    
    # Cover image
    cover_param = "images/default_cover.png"
    if cover_image_path and Path(cover_image_path).exists():
        with open(cover_image_path, "rb") as f:
            cover_data = f.read()
        processed = utils_booklet.compress_image_if_needed(cover_data, Path(cover_image_path).name)
        cover_param = f"images/{Path(cover_image_path).name}"
        extra_files.append({"filename": cover_param, "data": processed})
    
    # Memory images
    for img_path in image_files:
        with open(img_path, "rb") as f:
            extra_files.append({"filename": f"images/{img_path.name}", "data": f.read()})
    
    # Generate structure
    content_structure = booklet_generator.create_booklet_content_json_structure(
        chapters_data, video_title=video_title, cover_image_name=cover_param
    )
    
    content_json = json.dumps(content_structure, ensure_ascii=False)
    h5p_json = json.dumps(booklet_generator.generate_h5p_json_dict(video_title), ensure_ascii=False)
    
    # Create package
    pkg_bytes = utils_booklet.create_h5p_package(
        content_json, h5p_json, str(TEMPLATE_ZIP_PATH), extra_files
    )
    
    if pkg_bytes:
        with open(output_path, "wb") as f:
            f.write(pkg_bytes)
        print(f"   ✓ Package saved to: {output_path}")
        print()
        print(f"✅ Success! H5P package created: {output_path}")
        print(f"📦 Size: {len(pkg_bytes) / 1024 / 1024:.2f} MB")
        return True
    else:
        print("❌ Failed to create package")
        return False

# --- CLI Interface ---

def main():
    parser = argparse.ArgumentParser(
        description="Generate H5P Interactive Book from video transcript using AI"
    )
    
    parser.add_argument(
        "--transcript", "-t",
        required=True,
        help="Path to transcript text file"
    )
    
    parser.add_argument(
        "--video-url", "-u",
        required=True,
        help="Embeddable video URL (iframe)"
    )
    
    parser.add_argument(
        "--title", "-n",
        required=True,
        help="Video/Book title"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="output.h5p",
        help="Output H5P file path (default: output.h5p)"
    )
    
    parser.add_argument(
        "--cover", "-c",
        help="Path to cover image (optional)"
    )
    
    parser.add_argument(
        "--model", "-m",
        default="gemini-flash-latest",
        choices=["gemini-flash-latest", "gemini-1.5-pro", "gemini-1.5-flash"],
        help="Gemini model to use (default: gemini-flash-latest)"
    )
    
    args = parser.parse_args()
    
    # Read transcript
    if not Path(args.transcript).exists():
        print(f"❌ Error: Transcript file not found: {args.transcript}")
        sys.exit(1)
    
    with open(args.transcript, "r", encoding="utf-8") as f:
        transcript = f.read()
    
    if len(transcript) < 100:
        print("⚠️  Warning: Transcript seems very short. Better results with longer transcripts.")
    
    # Validate template
    if not TEMPLATE_ZIP_PATH.exists():
        print(f"❌ Error: Template not found: {TEMPLATE_ZIP_PATH}")
        sys.exit(1)
    
    # Generate
    success = generate_h5p_package(
        transcript=transcript,
        video_title=args.title,
        video_url=args.video_url,
        output_path=args.output,
        cover_image_path=args.cover,
        model_name=args.model
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()