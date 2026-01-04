# 🚀 Quick Start Guide

## Option 1: Streamlit Web Interface (Recommended)

### Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file with your Gemini API key
cp .env.example .env
nano .env  # Add your API key

# 3. Run the app
streamlit run orchestrator_v2.py
```

### Usage
1. Open browser (usually http://localhost:8501)
2. Enter video title, URL, and paste transcript
3. Click "Generate All Content"
4. Review generated content in tabs
5. Click "Generate H5P Package"
6. Download your .h5p file

---

## Option 2: Command Line Interface

### Basic Usage
```bash
python cli_generator.py \
  --transcript example_transcript.txt \
  --video-url "https://www.youtube.com/embed/VIDEO_ID" \
  --title "Climate Change Explained"
```

### With Optional Parameters
```bash
python cli_generator.py \
  --transcript my_transcript.txt \
  --video-url "https://player.vimeo.com/video/123456" \
  --title "My Educational Video" \
  --output my_book.h5p \
  --cover cover_image.png \
  --model gemini-1.5-pro
```

### Available Options
- `--transcript, -t`: Path to transcript file (required)
- `--video-url, -u`: Embeddable video URL (required)
- `--title, -n`: Book/video title (required)
- `--output, -o`: Output filename (default: output.h5p)
- `--cover, -c`: Cover image path (optional)
- `--model, -m`: Gemini model choice (default: gemini-2.0-flash-exp)

---

## 📋 Preparing Your Transcript

### Best Practices
1. **Length**: At least 1000 words for good results
2. **Format**: Plain text, UTF-8 encoding
3. **Structure**: Include paragraph breaks for readability
4. **Language**: Currently optimized for German, but adaptable
5. **Content**: Clear, educational narrative works best

### Example Transcript Structure
```
Title of Topic - Transcript

Introduction paragraph explaining the topic...

Section 1 discussing key concept A...

Section 2 explaining B in detail...

Examples and case studies...

Conclusion with takeaways...
```

---

## 🎥 Video URL Requirements

### Supported Platforms

**YouTube**
- ❌ Regular: `https://www.youtube.com/watch?v=VIDEO_ID`
- ✅ Embed: `https://www.youtube.com/embed/VIDEO_ID`

**Vimeo**
- ❌ Regular: `https://vimeo.com/123456`
- ✅ Embed: `https://player.vimeo.com/video/123456`

**Other Platforms**
- Most platforms have an "embed" or "share" option
- Look for iframe embed codes
- Extract the `src` URL from the iframe

---

## 🎨 Customizing Output

### In Streamlit Interface
- Select different Gemini models for varied output
- Upload custom cover images
- Preview all content before packaging

### Via Code Modification

**Change memory game settings** (in `booklet_generator_v2.py`):
```python
"behaviour": {
    "useGrid": False,
    "allowRetry": False,
    "numCardsToUse": 6  # Adjust number of pairs
}
```

**Modify quiz pool size** (in `orchestrator_v2.py`):
```python
forced_pool_size=5  # Change from 5 to 10 for all questions
```

**Adjust Gemini prompts** (in `orchestrator_v2.py`):
- Edit prompt strings in generation functions
- Modify JSON structure requirements
- Change output length/detail

---

## ⚡ Performance Tips

### Speed Optimization
1. Use `gemini-2.0-flash-exp` for fastest results
2. Shorter transcripts (1000-3000 words) process faster
3. Disable image collages for quicker generation

### Quality Optimization
1. Use `gemini-1.5-pro` for most accurate content
2. Longer, detailed transcripts yield better results
3. Well-structured transcripts with clear sections

---

## 🐛 Troubleshooting

### "API Key Not Found"
```bash
# Check .env file exists
ls -la .env

# Verify content
cat .env

# Should show:
GEMINI_API_KEY=your_key_here
```

### "Template Not Found"
```bash
# Ensure template exists
ls templates/template.zip

# If missing, you need to provide the base H5P template
```

### "Images Not Generating"
- Check internet connection (needs Wikimedia access)
- Try different/simpler search terms
- Verify OpenCV is installed: `pip install opencv-python`

### "Video Not Embedding"
- Use iframe embed URLs, not regular page URLs
- Test the URL in an iframe on a simple HTML page first
- Some platforms restrict embedding

---

## 📦 Uploading to Your LMS

### Moodle
1. Go to course → "Add an activity or resource"
2. Select "H5P"
3. Upload your .h5p file
4. Configure display settings
5. Save and display

### H5P.com
1. Login to H5P.com
2. Click "Upload" or "Add new content"
3. Choose your .h5p file
4. Publish and share

### Other LMS
- Most modern LMS support H5P through plugins
- Check your LMS documentation for H5P integration

---

## 💡 Example Workflows

### Workflow 1: Quick Generation
```bash
# Generate everything with defaults
streamlit run orchestrator_v2.py
# Use GUI to paste transcript, generate, download
```

### Workflow 2: Batch Processing
```bash
# Process multiple videos via CLI
for transcript in transcripts/*.txt; do
    python cli_generator.py \
        -t "$transcript" \
        -u "$(cat urls.txt | head -n1)" \
        -n "$(basename $transcript .txt)" \
        -o "output/$(basename $transcript .txt).h5p"
done
```

### Workflow 3: Custom Iteration
```bash
# Generate with pro model for quality
python cli_generator.py \
    -t transcript.txt \
    -u "https://..." \
    -n "Title" \
    -m gemini-1.5-pro \
    -o v1.h5p

# Review, adjust transcript, regenerate with tweaks
# Edit orchestrator_v2.py prompts if needed
python cli_generator.py -t transcript_v2.txt ... -o v2.h5p
```

---

## 📚 Next Steps

1. **Test with example**: Use `example_transcript.txt` provided
2. **Customize prompts**: Edit generation functions for your needs
3. **Extend functionality**: Add more chapter types or assessment formats
4. **Share feedback**: Help improve the tool

---

**Need Help?** Check the main README.md or open an issue on GitHub!
