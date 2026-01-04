import streamlit as st
import json
import tempfile
import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

import booklet_generator_v2 as booklet_generator
import utils_booklet_iframe as utils_booklet
import utils_image_gen

# Load environment variables
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    st.error("⚠️ GEMINI_API_KEY not found in .env file!")

PROJECT_ROOT = Path(__file__).parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
TEMPLATE_ZIP_PATH = TEMPLATES_DIR / "template.zip"

st.set_page_config(page_title="H5P Transcript Generator", page_icon="📚", layout="wide")

# --- Gemini Prompts ---
SYSTEM_PROMPT = """You are an expert Instructional Designer and educational content creator. 
You analyze video transcripts and create engaging, pedagogically sound learning materials.
Always respond with valid JSON only, no additional text or markdown formatting."""

def clean_json_response(text: str) -> str:
    """Remove markdown code blocks and clean response"""
    if not text:
        return ""
    
    text = text.strip()
    
    # Remove markdown code blocks
    if text.startswith("```json"):
        text = text.split("```json")[1].split("```")[0].strip()
    elif text.startswith("```"):
        text = text.split("```")[1].split("```")[0].strip()
    
    return text

def generate_intro_content(transcript: str, video_title: str, video_url: str, model_name: str = "gemini-flash-latest") -> dict:
    """Generate customized introduction based on transcript"""
    prompt = f"""Analyze this video transcript and create an engaging introduction for an H5P Interactive Book.

Video Title: {video_title}
Video URL: {video_url}

Transcript:
{transcript[:3000]}...

You MUST respond with ONLY a valid JSON object (no markdown, no explanation):
{{
  "title": "Main title for the introduction (h2 heading)",
  "welcome_text": "2-3 sentences welcoming learners and introducing the topic",
  "learning_objectives": ["objective 1", "objective 2", "objective 3"],
  "workflow": ["step 1", "step 2", "step 3", "step 4"]
}}

Make it engaging and specific to the video content. Use German language.
Return ONLY the JSON, nothing else."""

    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        cleaned_text = clean_json_response(response.text)
        
        if not cleaned_text:
            raise ValueError("Empty response from API")
        
        return json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        st.error(f"Error parsing intro JSON: {e}")
        st.error(f"Response was: {response.text[:500]}")
        return None
    except Exception as e:
        st.error(f"Error generating intro: {e}")
        return None

def generate_memory_prompts(transcript: str, model_name: str = "gemini-flash-latest") -> list:
    """Generate 6 memory game pairs from transcript"""
    prompt = f"""Analyze this transcript and identify 6 key concepts, people, or events that learners should remember BEFORE watching the video.

Transcript:
{transcript}

You MUST respond with ONLY a valid JSON array (no markdown, no explanation):
[
  {{
    "prompt": "Name or concept (for image search)",
    "match_text": "Short German description (max 7 words)"
  }}
]

Focus on visual, memorable elements. The 'prompt' will be used to search for images on Wikimedia.
Return EXACTLY 6 objects in the array, nothing else."""

    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        cleaned_text = clean_json_response(response.text)
        
        if not cleaned_text:
            raise ValueError("Empty response from API")
        
        result = json.loads(cleaned_text)
        
        # Ensure we have exactly 6 items
        if len(result) < 6:
            st.warning(f"Only {len(result)} memory pairs generated, expected 6")
        
        return result[:6]  # Limit to 6
    except json.JSONDecodeError as e:
        st.error(f"Error parsing memory JSON: {e}")
        st.error(f"Response was: {response.text[:500]}")
        return None
    except Exception as e:
        st.error(f"Error generating memory prompts: {e}")
        return None

def generate_video_summary(transcript: str, model_name: str = "gemini-flash-latest") -> list:
    """Generate accordion summary for video content"""
    prompt = f"""Analyze this transcript and create a structured summary as an accordion with 5-7 main points.

Transcript:
{transcript}

You MUST respond with ONLY a valid JSON array (no markdown, no explanation):
[
  {{
    "title": "Event/Topic headline",
    "text": "<p>Detailed explanation (2-3 sentences) with HTML formatting</p>"
  }}
]

Follow the chronological order of the transcript. Return ONLY the JSON array, nothing else."""

    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        cleaned_text = clean_json_response(response.text)
        
        if not cleaned_text:
            raise ValueError("Empty response from API")
        
        return json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        st.error(f"Error parsing summary JSON: {e}")
        st.error(f"Response was: {response.text[:500]}")
        return None
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return None

def generate_quiz_questions(transcript: str, model_name: str = "gemini-flash-latest") -> list:
    """Generate 10 quiz questions (6 MC, 4 TF)"""
    prompt = f"""Create 10 assessment questions based on this transcript: 6 Multiple Choice and 4 True/False.

Transcript:
{transcript}

Rules:
- For Multiple Choice: at least one distractor must be longer than the correct answer
- Provide feedback for each answer
- Use German language
- Focus on key facts and comprehension

You MUST respond with ONLY a valid JSON array (no markdown, no explanation):
[
  {{
    "type": "multichoice",
    "question": "Question text?",
    "answers": [
      {{"text": "Correct answer", "correct": true, "feedback": "✔️ Richtig. Explanation."}},
      {{"text": "Wrong answer", "correct": false, "feedback": "❌ Falsch. Explanation."}},
      {{"text": "Longer wrong answer", "correct": false, "feedback": "❌ Falsch. Explanation."}}
    ]
  }},
  {{
    "type": "truefalse",
    "question": "Statement?",
    "correct": true,
    "feedback_correct": "✔️ Richtig. Explanation.",
    "feedback_wrong": "❌ Falsch. Explanation."
  }}
]

Return EXACTLY 10 questions (6 MC first, then 4 TF), nothing else."""

    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        cleaned_text = clean_json_response(response.text)
        
        if not cleaned_text:
            raise ValueError("Empty response from API")
        
        result = json.loads(cleaned_text)
        
        if len(result) != 10:
            st.warning(f"Generated {len(result)} questions, expected 10")
        
        return result
    except json.JSONDecodeError as e:
        st.error(f"Error parsing quiz JSON: {e}")
        st.error(f"Response was: {response.text[:500]}")
        return None
    except Exception as e:
        st.error(f"Error generating quiz: {e}")
        return None

def generate_cloze_tasks(transcript: str, model_name: str = "gemini-flash-latest") -> list:
    """Generate 2 cloze/drag text tasks"""
    prompt = f"""Create EXACTLY 2 cloze exercises (drag text) based on this transcript.

Transcript:
{transcript}

Task 1: Summary text with gaps (3-4 gaps)
Task 2: Glossary of key terms (3-4 gaps)

Rules:
- Use syntax: *Answer:Hint* for gaps
- Provide 2-3 distractors per task
- Use German language

You MUST respond with ONLY a valid JSON array (no markdown, no explanation):
[
  {{
    "description": "Vervollständigen Sie die Zusammenfassung.",
    "text_content": "Running text with *Answer:Hint* gaps showing the summary",
    "distractors": "*Distractor1* *Distractor2*"
  }},
  {{
    "description": "Ordnen Sie die Begriffe den Definitionen zu.",
    "text_content": "*Term1:Definition1* bedeutet explanation. *Term2:Definition2* bedeutet explanation.",
    "distractors": "*Distractor3* *Distractor4*"
  }}
]

Return EXACTLY 2 tasks in the array, nothing else."""

    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        cleaned_text = clean_json_response(response.text)
        
        if not cleaned_text:
            raise ValueError("Empty response from API")
        
        result = json.loads(cleaned_text)
        
        if len(result) != 2:
            st.warning(f"Generated {len(result)} cloze tasks, expected 2")
            # Ensure we return exactly 2 tasks
            if len(result) < 2:
                # Add a default second task if missing
                result.append({
                    "description": "Vervollständigen Sie den Text.",
                    "text_content": "Dies ist ein *Platzhalter:Begriff* für die fehlende Aufgabe.",
                    "distractors": "*Zusatz* *Extra*"
                })
        
        return result[:2]  # Always return exactly 2
    except json.JSONDecodeError as e:
        st.error(f"Error parsing cloze JSON: {e}")
        st.error(f"Response was: {response.text[:500]}")
        return None
    except Exception as e:
        st.error(f"Error generating cloze: {e}")
        return None

# --- Streamlit UI ---
def main():
    st.title("🎥 H5P Interactive Book Generator")
    st.markdown("Generate an interactive H5P learning module from any video transcript using AI.")
    
    # Initialize session state
    if 'generated_content' not in st.session_state:
        st.session_state['generated_content'] = {}
    if 'generated_mem_files' not in st.session_state:
        st.session_state['generated_mem_files'] = []
    if 'temp_dir' not in st.session_state:
        st.session_state['temp_dir'] = tempfile.mkdtemp()

    st.markdown("---")
    
    # Input Section
    st.markdown("### 📋 Input")
    
    col1, col2 = st.columns(2)
    
    with col1:
        video_title = st.text_input("Video Title", placeholder="e.g., Climate Change Explained")
        video_url = st.text_input("Video URL (iframe embeddable)", placeholder="https://...")
        
    with col2:
        cover_upload = st.file_uploader("Cover Image (optional)", type=['png', 'jpg', 'jpeg'])
        model_choice = st.selectbox("Gemini Model", 
                                     ["gemini-flash-latest", "gemini-1.5-pro", "gemini-1.5-flash"],
                                     index=0)
    
    transcript = st.text_area("Video Transcript", height=200, 
                              placeholder="Paste the full video transcript here...")
    
    st.markdown("---")
    
    # Generation Section
    col_gen1, col_gen2 = st.columns(2)
    
    with col_gen1:
        if st.button("🤖 Generate All Content", type="primary", disabled=not transcript):
            if not GEMINI_API_KEY:
                st.error("❌ Gemini API key not configured!")
                return
                
            progress_bar = st.progress(0)
            status = st.empty()
            
            # Step 1: Introduction
            status.text("📝 Generating introduction...")
            intro_data = generate_intro_content(transcript, video_title, video_url, model_choice)
            if intro_data:
                st.session_state['generated_content']['intro'] = intro_data
            progress_bar.progress(20)
            
            # Step 2: Memory Game
            status.text("🧠 Generating memory game prompts...")
            memory_prompts = generate_memory_prompts(transcript, model_choice)
            if memory_prompts:
                st.session_state['generated_content']['memory_prompts'] = memory_prompts
                
                # Generate images
                status.text("🎨 Generating memory game images...")
                temp_path = Path(st.session_state['temp_dir'])
                try:
                    h5p_list, file_paths = utils_image_gen.generate_memory_assets(
                        memory_prompts, temp_path, use_collage=False, collage_count=4
                    )
                    st.session_state['generated_mem_files'] = [str(p) for p in file_paths]
                    st.session_state['generated_content']['memory_cards'] = h5p_list
                    
                    # Debug info
                    st.write(f"✅ Generated {len(file_paths)} image files")
                    for fp in file_paths:
                        if Path(fp).exists():
                            st.write(f"  ✓ {Path(fp).name} ({Path(fp).stat().st_size / 1024:.1f} KB)")
                        else:
                            st.error(f"  ✗ Missing: {Path(fp).name}")
                            
                except Exception as e:
                    st.error(f"Error generating images: {e}")
                    import traceback
                    st.error(traceback.format_exc())
            progress_bar.progress(40)
            
            # Step 3: Video Summary
            status.text("📺 Generating video summary...")
            summary_data = generate_video_summary(transcript, model_choice)
            if summary_data:
                st.session_state['generated_content']['summary'] = summary_data
            progress_bar.progress(60)
            
            # Step 4: Quiz
            status.text("❓ Generating quiz questions...")
            quiz_data = generate_quiz_questions(transcript, model_choice)
            if quiz_data:
                st.session_state['generated_content']['quiz'] = quiz_data
            progress_bar.progress(80)
            
            # Step 5: Cloze
            status.text("📝 Generating cloze exercises...")
            cloze_data = generate_cloze_tasks(transcript, model_choice)
            if cloze_data:
                st.session_state['generated_content']['cloze'] = cloze_data
            progress_bar.progress(100)
            
            status.text("✅ All content generated!")
            st.success("🎉 Content generation complete!")
    
    with col_gen2:
        if st.button("🔄 Reset All", type="secondary"):
            st.session_state['generated_content'] = {}
            st.session_state['generated_mem_files'] = []
            st.rerun()
    
    # Preview Section
    if st.session_state['generated_content']:
        st.markdown("---")
        st.markdown("### 👀 Generated Content Preview")
        
        tabs = st.tabs(["Intro", "Memory", "Summary", "Quiz", "Cloze"])
        
        with tabs[0]:
            if 'intro' in st.session_state['generated_content']:
                st.json(st.session_state['generated_content']['intro'])
        
        with tabs[1]:
            if 'memory_prompts' in st.session_state['generated_content']:
                st.json(st.session_state['generated_content']['memory_prompts'])
                st.caption(f"Generated {len(st.session_state['generated_mem_files'])} image files")
        
        with tabs[2]:
            if 'summary' in st.session_state['generated_content']:
                st.json(st.session_state['generated_content']['summary'])
        
        with tabs[3]:
            if 'quiz' in st.session_state['generated_content']:
                st.json(st.session_state['generated_content']['quiz'])
        
        with tabs[4]:
            if 'cloze' in st.session_state['generated_content']:
                st.json(st.session_state['generated_content']['cloze'])
    
    st.markdown("---")
    
    # Package Generation
    if st.button("📦 Generate H5P Package", type="primary", 
                 disabled=not st.session_state['generated_content']):
        
        if not TEMPLATE_ZIP_PATH.exists():
            st.error(f"❌ Template not found at {TEMPLATE_ZIP_PATH}")
            return
        
        try:
            with st.spinner("📦 Creating H5P package..."):
                # Build chapter data
                chapters_data = []
                
                # Chapter 1: Introduction
                if 'intro' in st.session_state['generated_content']:
                    intro = st.session_state['generated_content']['intro']
                    chapters_data.append({
                        "type": "introduction",
                        "data": intro
                    })
                
                # Chapter 2: Memory Game
                if 'memory_cards' in st.session_state['generated_content']:
                    chapters_data.append({
                        "type": "memory_game",
                        "title": "Memory-Spiel",
                        "instruction": "Ordnen Sie die Begriffe den passenden Beschreibungen zu.",
                        "cards": st.session_state['generated_content']['memory_cards']
                    })
                
                # Chapter 3: Video + Summary
                if 'summary' in st.session_state['generated_content']:
                    chapters_data.append({
                        "type": "video_page",
                        "title": "Video & Zusammenfassung",
                        "video": {
                            "url": video_url,
                            "width": 800,
                            "height": 400
                        },
                        "summary_accordion": st.session_state['generated_content']['summary']
                    })
                
                # Chapter 4: Quiz
                if 'quiz' in st.session_state['generated_content']:
                    chapters_data.append({
                        "type": "question_set",
                        "title": "Verständnisfragen",
                        "intro_screen": {
                            "title": "Verständnisfragen",
                            "text": "Testen Sie Ihr Wissen zum Video.",
                            "background_image": "images/quiz_bg.png"
                        },
                        "questions": st.session_state['generated_content']['quiz']
                    })
                
                # Chapter 5: Cloze
                if 'cloze' in st.session_state['generated_content']:
                    chapters_data.append({
                        "type": "cloze_set",
                        "title": "Lückentexte",
                        "intro_screen": {
                            "title": "Lückentexte",
                            "text": "Ziehen Sie die passenden Wörter in die Lücken.",
                            "background_image": "images/cloze_bg.png"
                        },
                        "tasks": st.session_state['generated_content']['cloze']
                    })
                
                # Prepare extra files
                extra_files_to_zip = []
                
                # Cover image
                cover_filename_param = "images/default_cover.png"
                if cover_upload:
                    processed = utils_booklet.compress_image_if_needed(
                        cover_upload.getvalue(), cover_upload.name
                    )
                    cover_filename_param = f"images/{cover_upload.name}"
                    extra_files_to_zip.append({
                        "filename": cover_filename_param, 
                        "data": processed
                    })
                
                # Memory game images
                if st.session_state.get('generated_mem_files'):
                    for local_path_str in st.session_state['generated_mem_files']:
                        p = Path(local_path_str)
                        if p.exists():
                            with open(p, "rb") as f_local:
                                file_data = f_local.read()
                                # Compress if needed
                                compressed = utils_booklet.compress_image_if_needed(file_data, p.name)
                                extra_files_to_zip.append({
                                    "filename": f"images/{p.name}", 
                                    "data": compressed
                                })
                        else:
                            st.warning(f"Image file not found: {p}")
                            logger.warning(f"Missing image file: {p}")
                
                # Generate content structure
                content_structure = booklet_generator.create_booklet_content_json_structure(
                    chapters_data,
                    video_title=video_title,
                    cover_image_name=cover_filename_param
                )
                
                content_json = json.dumps(content_structure, ensure_ascii=False)
                h5p_json = json.dumps(
                    booklet_generator.generate_h5p_json_dict(video_title), 
                    ensure_ascii=False
                )
                
                # Create package
                pkg_bytes = utils_booklet.create_h5p_package(
                    content_json, h5p_json, str(TEMPLATE_ZIP_PATH), extra_files_to_zip
                )
                
                if pkg_bytes:
                    st.success("✅ Package created successfully!")
                    
                    # Safe filename
                    safe_title = "".join([c for c in video_title if c.isalnum() or c in (' ', '-', '_')]).strip()
                    filename = f"{safe_title or 'interactive_book'}.h5p"
                    
                    st.download_button(
                        "💾 Download H5P Package",
                        pkg_bytes,
                        filename,
                        "application/zip"
                    )
                else:
                    st.error("❌ Failed to create package")
                    
        except Exception as e:
            st.error(f"❌ Error creating package: {e}")
            import traceback
            st.text(traceback.format_exc())

if __name__ == "__main__":
    main()