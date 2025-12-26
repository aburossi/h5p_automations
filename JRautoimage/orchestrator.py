import streamlit as st
import json
import tempfile
import shutil
from pathlib import Path

import booklet_generator_iframe as booklet_generator
import utils_booklet_iframe as utils_booklet
# NEU: Importiere den Generator
import utils_image_gen 

# ... (Setup Code bleibt gleich) ...
PROJECT_ROOT = Path(__file__).parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
TEMPLATE_ZIP_PATH = TEMPLATES_DIR / "template.zip"

st.set_page_config(page_title="H5P Generator (Annual Review)", page_icon="📚", layout="wide")

def main():
    st.title("H5P Annual Review Generator")
    
    # --- NEW: Google Gem Link ---
    st.info("🤖 **Need help generating content?** Use this specialized Google Gem to create the JSONs: [**Click here to open Gem**](https://gemini.google.com/gem/f2f793ed47f4)")
    
    st.markdown("Generate an Interactive Book with automatic customization for 2025.")
    
    # Initialize Session State for generated files
    if 'generated_mem_files' not in st.session_state:
        st.session_state['generated_mem_files'] = []
    if 'generated_mem_json' not in st.session_state:
        st.session_state['generated_mem_json'] = ""
    if 'temp_dir' not in st.session_state:
        # Create a temp dir that persists for the session
        st.session_state['temp_dir'] = tempfile.mkdtemp()

    # ... (Google Gem Info & General Settings bleiben gleich) ...
    st.markdown("### ⚙️ General Settings")
    col_conf1, col_conf2 = st.columns(2)
    with col_conf1:
        roman_number = st.text_input("Roman Numeral (e.g. II, III)", value="II")
        cover_upload = st.file_uploader("Upload Title Image (Cover)", type=['png', 'jpg', 'jpeg'])
    with col_conf2:
        months_text = st.text_input("Months Text (e.g. März-April)", value="März-April")

    st.markdown("---")
    st.markdown("### 📝 Chapter Content")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Memory Game (Chap 2)")
        
        # --- TAB SWITCH: UPLOAD vs GENERATE ---
        tab_up, tab_gen = st.tabs(["📤 Upload Manually", "✨ Auto-Generate (Beta)"])
        
        # Var to hold the final JSON string to be used for generation
        final_memory_json_str = ""
        manual_files = None

        with tab_up:
            manual_files = st.file_uploader("Upload Images", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True, key="mem_upl")
            st.info("Ensure JSON paths match uploaded filenames.")
            final_memory_json_str = st.text_area(
                "Memory JSON (Manual)", 
                height=150, 
                placeholder='[{"image": {"path": "images/pic.jpg"...}, ...}]',
                key="input_memory_manual"
            )

        with tab_gen:
            st.markdown("Generate images from Wikimedia & Text.")
            input_prompts = st.text_area(
                "Prompts JSON",
                height=150,
                value='[\n  {"prompt": "Donald Trump", "match_text": "US-Präsident"},\n  {"prompt": "Eiffelturm", "match_text": "Paris"}\n]',
                help="List of dictionaries with 'prompt' and 'match_text'"
            )
            
            c_gen1, c_gen2 = st.columns(2)
            with c_gen1:
                use_collage = st.checkbox("Use Collage?", value=False)
            with c_gen2:
                collage_n = st.selectbox("Images per Collage", [4, 8, 16], disabled=not use_collage)

            if st.button("🚀 Generate Assets"):
                try:
                    prompts_data = json.loads(input_prompts)
                    temp_path = Path(st.session_state['temp_dir'])
                    
                    with st.spinner("Searching Wikimedia & Generating images..."):
                        # Call the generator logic
                        h5p_list, file_paths = utils_image_gen.generate_memory_assets(
                            prompts_data, 
                            temp_path, 
                            use_collage, 
                            collage_n
                        )
                        
                        # Store in session state
                        st.session_state['generated_mem_files'] = [str(p) for p in file_paths]
                        st.session_state['generated_mem_json'] = json.dumps(h5p_list, indent=2)
                        
                        st.success(f"Generated {len(file_paths)} files!")
                        
                except json.JSONDecodeError:
                    st.error("Invalid JSON in prompts.")
                except Exception as e:
                    st.error(f"Generation failed: {e}")

            # Show result if available
            if st.session_state['generated_mem_json']:
                st.text_area("Generated JSON (Read-only)", value=st.session_state['generated_mem_json'], height=150, disabled=True)
                st.caption(f"Files stored in temp: {len(st.session_state['generated_mem_files'])} assets ready.")
                final_memory_json_str = st.session_state['generated_mem_json']

        # Logic to decide which input to use
        # If the generated tab was last used or populated, usually we prioritize that if the user didn't type in manual.
        # Simple override logic: if tab_gen is active (conceptually), we use its JSON. 
        # Since Streamlit tabs don't easily give state, we rely on which text area has content.
        json_memory = final_memory_json_str

        # ... (Rest der Spalte 1: Video etc.) ...
        st.subheader("2. Video & Accordion (Chap 3)")
        json_video = st.text_area("Video JSON", height=150, key="input_video")
        
        st.subheader("3. Question Set (Chap 4)")
        json_questions = st.text_area("Quiz JSON", height=150, key="input_questions")

    with col2:
        # ... (Rest der Spalte 2: Cloze, Mentimeter etc. bleibt gleich) ...
        st.subheader("4. Cloze / Drag Text (Chap 5)")
        json_cloze = st.text_area("Cloze JSON", height=150, key="input_cloze")

        st.subheader("5. Survey & Results (Chap 6 & 7)")
        menti_url_6 = st.text_input("Reflexion URL (Step 6)", placeholder="https://www.menti.com/...")
        menti_url_7 = st.text_input("Results URL (Step 7)", placeholder="https://www.mentimeter.com/...")

    st.markdown("---")

    if st.button("Generate H5P Package", type="primary"):
        # Check Template
        if not TEMPLATE_ZIP_PATH.exists():
            st.error(f"❌ Template not found at {TEMPLATE_ZIP_PATH}")
            return
            
        # 1. Collect inputs
        raw_inputs = [json_memory, json_video, json_questions, json_cloze]
        parsed_data_list = []
        has_error = False
        
        # 2. Validate JSONs
        for idx, raw_text in enumerate(raw_inputs):
            if raw_text.strip():
                try:
                    data = json.loads(raw_text)
                    # FIX: Wrapper logic for Memory Game
                    if idx == 0 and isinstance(data, list):
                        data = {
                            "type": "memory_game",
                            "title": "Memory-Spiel",
                            "instruction": "Ordnen Sie die Gesichter den passenden Texten zu.",
                            "cards": data
                        }
                    parsed_data_list.append(data)
                except json.JSONDecodeError as e:
                    st.error(f"❌ JSON Error in Input #{idx+1}: {e}")
                    has_error = True
        
        if has_error: return

        try:
            with st.spinner("Compiling H5P package..."):
                extra_files_to_zip = []

                # A. Handle Cover Image
                cover_filename_param = "images/title_2025.png"
                if cover_upload:
                    processed = utils_booklet.compress_image_if_needed(cover_upload.getvalue(), cover_upload.name)
                    cover_filename_param = f"images/{cover_upload.name}"
                    extra_files_to_zip.append({"filename": cover_filename_param, "data": processed})

                # B. Handle Memory Images
                # CASE 1: Manual Upload
                if manual_files:
                    for f in manual_files:
                        processed = utils_booklet.compress_image_if_needed(f.getvalue(), f.name)
                        extra_files_to_zip.append({"filename": f"images/{f.name}", "data": processed})
                
                # CASE 2: Generated Files (from session state)
                # We check if json_memory matches the generated json to ensure we are using the generated assets
                elif st.session_state.get('generated_mem_files') and json_memory == st.session_state['generated_mem_json']:
                    for local_path_str in st.session_state['generated_mem_files']:
                        p = Path(local_path_str)
                        if p.exists():
                            with open(p, "rb") as f_local:
                                file_bytes = f_local.read()
                                # No need to compress again usually, as generator does resizing, but optional
                                extra_files_to_zip.append({
                                    "filename": f"images/{p.name}", 
                                    "data": file_bytes
                                })

                # C. Generate Content & Zip
                content_structure = booklet_generator.create_booklet_content_json_structure(
                    parsed_data_list, 
                    roman_number=roman_number, 
                    months_text=months_text,
                    cover_image_name=cover_filename_param,
                    mentimeter_urls=(menti_url_6, menti_url_7)
                )
                
                content_json = json.dumps(content_structure, ensure_ascii=False)
                h5p_json = json.dumps(booklet_generator.generate_h5p_json_dict(f"Jahresrückblick {roman_number}"), ensure_ascii=False)

                pkg_bytes = utils_booklet.create_h5p_package(
                    content_json, h5p_json, str(TEMPLATE_ZIP_PATH), extra_files_to_zip
                )

            if pkg_bytes:
                st.success("✅ Package created!")
                st.download_button("💾 Download .h5p", pkg_bytes, f"jahresrueckblick_{roman_number}.h5p", "application/zip")
            else:
                st.error("❌ Failed to create ZIP.")

        except Exception as e:
            st.error(f"Critical Error: {e}")
            import traceback
            st.text(traceback.format_exc())

if __name__ == "__main__":
    main()