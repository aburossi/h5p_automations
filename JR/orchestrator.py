import streamlit as st
import json
from pathlib import Path
import booklet_generator_iframe as booklet_generator
import utils_booklet_iframe as utils_booklet

# Setup
PROJECT_ROOT = Path(__file__).parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
TEMPLATE_ZIP_PATH = TEMPLATES_DIR / "template.zip"

st.set_page_config(page_title="H5P Generator (Annual Review)", page_icon="📚", layout="wide")

def main():
    st.title("H5P Annual Review Generator")
    st.markdown("Generate an Interactive Book with automatic customization for 2025.")

    # --- TOP CONFIG ---
    st.markdown("### ⚙️ General Settings")
    col_conf1, col_conf2 = st.columns(2)
    with col_conf1:
        roman_number = st.text_input("Roman Numeral (e.g. II, III)", value="II")
    with col_conf2:
        months_text = st.text_input("Months Text (e.g. März-April)", value="März-April")

    st.markdown("---")
    st.markdown("### 📝 Chapter Content (JSON)")

    # --- INPUTS ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Memory Game (Chap 2)")
        st.info("You can paste the full JSON object OR just the list of cards `[...]`.")
        json_memory = st.text_area(
            "Memory JSON", 
            height=150, 
            placeholder='[{"image": ...}, {"image": ...}]',
            key="input_memory"
        )

        st.subheader("2. Video & Accordion (Chap 3)")
        json_video = st.text_area(
            "Video JSON", 
            height=150, 
            placeholder='{"chapter_id": 3, "type": "video_page", ...}',
            key="input_video"
        )

        st.subheader("3. Question Set (Chap 4)")
        json_questions = st.text_area(
            "Quiz JSON", 
            height=150, 
            placeholder='{"chapter_id": 4, "type": "question_set", ...}',
            key="input_questions"
        )

    with col2:
        st.subheader("4. Cloze / Drag Text (Chap 5)")
        json_cloze = st.text_area(
            "Cloze JSON", 
            height=150, 
            placeholder='{"chapter_id": 5, "type": "cloze_set", ...}',
            key="input_cloze"
        )

        st.subheader("5. Survey / IFrame Pages (Chap 6 & 7)")
        json_steps = st.text_area(
            "Steps JSON", 
            height=150, 
            placeholder='{"steps_6_and_7": [...]}',
            key="input_steps"
        )

    st.markdown("---")

    # --- GENERATION LOGIC ---

    if st.button("Generate H5P Package", type="primary"):
        if not TEMPLATE_ZIP_PATH.exists():
            st.error(f"❌ Template not found at {TEMPLATE_ZIP_PATH}")
            return

        if not roman_number or not months_text:
            st.warning("⚠️ Please fill in the Roman Numeral and Months Text.")
            return

        # 1. Collect inputs
        raw_inputs = [json_memory, json_video, json_questions, json_cloze, json_steps]
        parsed_data_list = []
        has_error = False

        # 2. Validate and Parse JSONs
        for idx, raw_text in enumerate(raw_inputs):
            if raw_text.strip():
                try:
                    data = json.loads(raw_text)
                    
                    # --- FIX: Auto-wrap Memory Game if it is just a list ---
                    if idx == 0 and isinstance(data, list):
                        data = {
                            "type": "memory_game",
                            "title": "Memory-Spiel",
                            "instruction": "Ordnen Sie die Gesichter den passenden Texten zu.",
                            "themeColor": "#002f6c",
                            "card_back_image": "images/card_back.png",
                            "cards": data
                        }
                    # -------------------------------------------------------

                    parsed_data_list.append(data)
                except json.JSONDecodeError as e:
                    st.error(f"❌ JSON Error in Input Box #{idx+1}: {e}")
                    has_error = True
        
        if has_error:
            return

        if not parsed_data_list:
            st.warning("⚠️ All JSON input boxes are empty.")
            return

        try:
            with st.spinner("Compiling H5P package..."):
                # 3. Generate Content Structure (content.json) with dynamic values
                content_structure = booklet_generator.create_booklet_content_json_structure(
                    parsed_data_list, 
                    roman_number=roman_number, 
                    months_text=months_text
                )
                content_json_str = json.dumps(content_structure, ensure_ascii=False, indent=None)
                
                # 4. Generate H5P Definition (h5p.json) with dynamic title
                full_book_title = f"Jahresrückblick SRF 2025 Teil {roman_number}"
                h5p_json_dict = booklet_generator.generate_h5p_json_dict(full_book_title)
                h5p_json_str = json.dumps(h5p_json_dict, ensure_ascii=False, indent=2)

                # 5. Create ZIP Package
                pkg_bytes = utils_booklet.create_h5p_package(
                    content_json_str, h5p_json_str, str(TEMPLATE_ZIP_PATH), []
                )

            if pkg_bytes:
                st.success(f"✅ H5P Booklet '{full_book_title}' generated successfully!")
                
                clean_filename = f"jahresrueckblick_2025_teil_{roman_number}.h5p".lower()
                
                st.download_button(
                    label="💾 Download .h5p File",
                    data=pkg_bytes,
                    file_name=clean_filename,
                    mime="application/zip"
                )
            else:
                st.error("❌ Failed to create ZIP package. Check logs.")

        except Exception as e:
            st.error(f"❌ Critical Error: {e}")
            import traceback
            st.text(traceback.format_exc())

if __name__ == "__main__":
    main()