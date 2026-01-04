# 🎥 H5P Interactive Book Generator

Automatically generate H5P Interactive Book packages from video transcripts using AI (Google Gemini).

## ✨ Features

- **AI-Powered Content Generation**: Automatically creates all learning content from a video transcript
- **Custom Introduction**: Dynamically generated learning objectives and workflow
- **Memory Game**: Visual memory cards with auto-fetched Wikimedia images
- **Video Integration**: Embeds your video with an auto-generated summary accordion
- **Assessment**: Quiz questions (Multiple Choice & True/False) + Cloze exercises
- **One-Click Export**: Downloads a ready-to-use .h5p package

## 📋 Prerequisites

- Python 3.8+
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

## 🚀 Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd JRautoimage
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure API key**
```bash
cp .env.example .env
# Edit .env and add your Gemini API key
```

## 🎯 Usage

### 1. Start the Application
```bash
streamlit run orchestrator_v2.py
```

### 2. Input Your Content
- **Video Title**: Enter the title of your video
- **Video URL**: Provide an embeddable iframe URL (YouTube, Vimeo, etc.)
- **Transcript**: Paste the full transcript of your video
- **Cover Image** (optional): Upload a custom cover image

### 3. Generate Content
Click **"🤖 Generate All Content"** to automatically create:
- Custom introduction with learning objectives
- 6 memory game pairs with images
- Video summary accordion (5-7 points)
- 10 quiz questions (6 MC + 4 TF)
- 2 cloze/drag-text exercises

### 4. Review & Download
- Preview all generated content in the tabs
- Click **"📦 Generate H5P Package"**
- Download your .h5p file

### 5. Upload to Your LMS
Upload the .h5p file to:
- Moodle (with H5P plugin)
- H5P.com
- H5P.org
- Any LMS supporting H5P content

## 📁 Project Structure

```
JRautoimage/
├── orchestrator_v2.py          # Main Streamlit app with Gemini integration
├── booklet_generator_v2.py     # H5P content structure generator
├── utils_booklet_iframe.py     # H5P utilities (images, JSON mapping, packaging)
├── utils_image_gen.py          # Image generation (Wikimedia + text images)
├── templates/
│   └── template.zip            # Base H5P template
├── requirements.txt            # Python dependencies
├── .env                        # API keys (create from .env.example)
└── README.md                   # This file
```

## 🎨 Customization

### Modify Gemini Prompts
Edit the prompt functions in `orchestrator_v2.py`:
- `generate_intro_content()` - Introduction structure
- `generate_memory_prompts()` - Memory game content
- `generate_video_summary()` - Video summary
- `generate_quiz_questions()` - Assessment questions
- `generate_cloze_tasks()` - Cloze exercises

### Change Memory Game Behavior
In `booklet_generator_v2.py`, adjust:
```python
"behaviour": {
    "useGrid": False,
    "allowRetry": False,
    "numCardsToUse": 6  # Number of pairs to show
}
```

### Modify Quiz Pool Size
In `booklet_generator_v2.py`, the quiz uses 5 random questions from a pool of 10:
```python
forced_pool_size=5  # Change this value
```

## 🛠️ Troubleshooting

### "GEMINI_API_KEY not found"
- Ensure `.env` file exists in the project root
- Verify the API key is correctly set: `GEMINI_API_KEY=your_actual_key`

### Images Not Generating
- Check internet connection (needs access to Wikimedia)
- Verify OpenCV is properly installed: `pip install opencv-python`
- Try different search terms in memory prompts

### Template Not Found
- Ensure `templates/template.zip` exists
- The template should contain the base H5P structure

### Video Not Embedding
- Use direct embed URLs (not regular video page URLs)
- YouTube: Use `https://www.youtube.com/embed/VIDEO_ID`
- Vimeo: Use `https://player.vimeo.com/video/VIDEO_ID`

## 🔧 Advanced Configuration

### Use Different Gemini Models
In the Streamlit UI, select from:
- `gemini-2.0-flash-exp` (fastest, recommended)
- `gemini-1.5-pro` (more accurate, slower)
- `gemini-1.5-flash` (balanced)

### Custom Image Generation
Edit `utils_image_gen.py` to:
- Change image size: `IMAGE_SIZE = 1080`
- Adjust font sizes: `MAX_FONT_SIZE`, `MIN_FONT_SIZE`
- Enable collages: Set `use_collage=True` in orchestrator

## 📝 Content Guidelines

### Transcript Quality
- **Length**: At least 1000 words for best results
- **Format**: Plain text, include speaker names if relevant
- **Language**: German (default), but can be adapted

### Video URLs
Must be embeddable iframes:
- ✅ `https://www.youtube.com/embed/dQw4w9WgXcQ`
- ✅ `https://player.vimeo.com/video/123456`
- ❌ `https://www.youtube.com/watch?v=dQw4w9WgXcQ`

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📄 License

This project is provided as-is for educational purposes.

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Gemini API documentation
3. Open an issue on GitHub

## 🙏 Acknowledgments

- **H5P**: Open-source interactive content framework
- **Google Gemini**: AI content generation
- **Wikimedia Commons**: Free educational images
- **OpenCV & Pillow**: Image processing

---

**Version**: 2.0  
**Last Updated**: December 2024
