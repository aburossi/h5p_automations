# ✅ Setup Checklist

Use this checklist to ensure your H5P Generator V2 is properly configured and ready to use.

---

## 📦 Installation Checklist

### Prerequisites
- [ ] Python 3.8 or higher installed
  ```bash
  python3 --version  # Should show 3.8.x or higher
  ```

- [ ] pip package manager available
  ```bash
  pip3 --version
  ```

- [ ] Internet connection (for API calls and Wikimedia)

### Files Present
- [ ] `orchestrator_v2.py` - Main Streamlit application
- [ ] `booklet_generator_v2.py` - H5P structure generator
- [ ] `cli_generator.py` - Command-line interface
- [ ] `utils_booklet_iframe.py` - H5P utilities (from V1)
- [ ] `utils_image_gen.py` - Image generation (from V1)
- [ ] `requirements.txt` - Dependencies list
- [ ] `.env.example` - Environment config template
- [ ] `templates/template.zip` - Base H5P template

**Note**: `utils_booklet_iframe.py` and `utils_image_gen.py` should be copied from your original V1 codebase.

---

## 🔧 Configuration Checklist

### Dependencies Installation
- [ ] Run installation script:
  ```bash
  chmod +x install.sh
  ./install.sh
  ```

  **OR** install manually:
  ```bash
  pip install -r requirements.txt
  ```

- [ ] Verify all packages installed:
  ```bash
  pip list | grep -E "streamlit|google-generativeai|opencv-python|Pillow|pyphen|python-dotenv"
  ```

  Should show:
  - ✓ streamlit
  - ✓ google-generativeai
  - ✓ opencv-python
  - ✓ Pillow
  - ✓ pyphen
  - ✓ python-dotenv

### API Key Setup
- [ ] Get Gemini API key from: https://makersuite.google.com/app/apikey

- [ ] Create `.env` file:
  ```bash
  cp .env.example .env
  ```

- [ ] Edit `.env` and add your key:
  ```bash
  nano .env
  # or
  vi .env
  # or use any text editor
  ```

- [ ] Verify key is set:
  ```bash
  cat .env
  # Should show: GEMINI_API_KEY=your_actual_key
  ```

- [ ] Test API access:
  ```bash
  python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key loaded:', bool(os.getenv('GEMINI_API_KEY')))"
  ```
  Should output: `API Key loaded: True`

### Template Setup
- [ ] Ensure `templates/` directory exists:
  ```bash
  mkdir -p templates
  ```

- [ ] Copy or create `template.zip`:
  - Option A: Copy from V1 installation
  - Option B: Create from existing H5P package
  - Option C: Download from H5P.org

- [ ] Verify template exists:
  ```bash
  ls -lh templates/template.zip
  ```

---

## 🚀 First Run Checklist

### Streamlit UI Test
- [ ] Start the application:
  ```bash
  streamlit run orchestrator_v2.py
  ```

- [ ] Browser opens automatically (or go to http://localhost:8501)

- [ ] Interface loads without errors

- [ ] All input fields visible:
  - Video Title
  - Video URL
  - Transcript text area
  - Cover image uploader
  - Model selector

- [ ] Test with example transcript:
  ```bash
  cat example_transcript.txt  # Copy this content
  ```

- [ ] Click "Generate All Content" button

- [ ] Wait for progress bar (3-5 minutes)

- [ ] Content preview tabs appear:
  - Intro
  - Memory
  - Summary
  - Quiz
  - Cloze

- [ ] Click "Generate H5P Package"

- [ ] Download button appears

- [ ] Download and verify .h5p file created

### CLI Test
- [ ] Run CLI with example:
  ```bash
  python3 cli_generator.py \
    --transcript example_transcript.txt \
    --video-url "https://www.youtube.com/embed/dQw4w9WgXcQ" \
    --title "Test Video" \
    --output test_output.h5p
  ```

- [ ] Script runs without errors

- [ ] Progress messages appear

- [ ] Output file created:
  ```bash
  ls -lh test_output.h5p
  ```

---

## 🧪 Functional Tests

### Image Generation Test
- [ ] Memory game images downloaded from Wikimedia

- [ ] Text images created for matching pairs

- [ ] All image files in correct format (JPG/PNG)

- [ ] Image compression working (check file sizes < 1MB)

### Content Quality Test
- [ ] Introduction has meaningful content:
  - Title relevant to transcript
  - Welcome text makes sense
  - 3+ learning objectives
  - 3+ workflow steps

- [ ] Memory game has 6 pairs

- [ ] Summary accordion has 5-7 points

- [ ] Quiz has 10 questions (6 MC + 4 TF)

- [ ] Cloze has 2 exercises

### H5P Package Test
- [ ] Upload test .h5p to H5P.com or your LMS

- [ ] Package opens without errors

- [ ] All chapters visible in table of contents

- [ ] Memory game playable

- [ ] Video embeds correctly

- [ ] Quiz questions work

- [ ] Cloze exercises functional

---

## 🛠️ Troubleshooting Checklist

### If "API Key Not Found" Error:
- [ ] `.env` file exists in project root
- [ ] `.env` contains `GEMINI_API_KEY=...`
- [ ] No spaces around `=` in .env file
- [ ] API key is valid (test at https://makersuite.google.com)

### If "Template Not Found" Error:
- [ ] `templates/` directory exists
- [ ] `templates/template.zip` exists
- [ ] Template file is a valid ZIP
- [ ] Template contains H5P structure (content/ folder)

### If "Module Not Found" Error:
- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] Using correct Python version: `python3 --version`
- [ ] Virtual environment activated (if using one)

### If Images Don't Generate:
- [ ] Internet connection working
- [ ] Can access wikimedia.org
- [ ] OpenCV installed: `pip list | grep opencv`
- [ ] Pillow installed: `pip list | grep Pillow`

### If AI Content Is Poor Quality:
- [ ] Transcript is long enough (1000+ words)
- [ ] Transcript is in German (or adjust prompts)
- [ ] Try different Gemini model (gemini-1.5-pro)
- [ ] Edit prompts in orchestrator_v2.py

### If Video Doesn't Embed:
- [ ] Using iframe embed URL (not regular page URL)
- [ ] URL is publicly accessible
- [ ] Video allows embedding (check privacy settings)
- [ ] Test URL in simple HTML iframe first

---

## 📊 Performance Benchmarks

Expected timing on average hardware:

### Streamlit UI
- [ ] App startup: < 5 seconds
- [ ] Content generation: 2-4 minutes
- [ ] Image generation: 30-60 seconds
- [ ] Package creation: 5-10 seconds
- [ ] **Total time: 3-5 minutes**

### CLI
- [ ] Similar timing to UI
- [ ] Slightly faster (no UI overhead)
- [ ] **Total time: 2-4 minutes**

### Package Size
- [ ] Typical size: 2-5 MB
- [ ] With many images: 5-10 MB
- [ ] Should be < 20 MB for most uses

---

## 🎯 Ready to Use!

If all items checked above, your setup is complete! 

### Quick Start:
```bash
# Streamlit UI
streamlit run orchestrator_v2.py

# CLI
python3 cli_generator.py -t transcript.txt -u "video_url" -n "Title"
```

### Next Steps:
1. Process your first real transcript
2. Upload to your LMS
3. Share with learners
4. Gather feedback
5. Iterate and improve

---

## 📚 Additional Resources

- [ ] Read README.md for comprehensive guide
- [ ] Check QUICKSTART.md for detailed instructions
- [ ] Review MIGRATION.md if coming from V1
- [ ] See ARCHITECTURE.md for technical details
- [ ] Explore PROJECT_SUMMARY.md for overview

---

## 🆘 Still Having Issues?

1. **Re-run installation script**:
   ```bash
   ./install.sh
   ```

2. **Check all documentation files**

3. **Test with provided example transcript**

4. **Verify API key at Google AI Studio**

5. **Open GitHub issue with error details**

---

**Checklist Version**: 1.0  
**Last Updated**: December 2024  
**For**: H5P Generator V2
