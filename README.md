# المساعد الذكي لمركز تجديد الطبي (Arabic AI Assistant)

A powerful Arabic chatbot application that answers questions based on text content loaded from files using Google's Gemini 1.5 Pro AI model.

## 🌟 Features

- **Natural Arabic Conversation**: Interactive chatbot with support for Egyptian Arabic dialect
- **Context-Aware Responses**: AI answers based solely on the loaded text content
- **Beautiful UI/UX**: Rich, responsive user interface with modern design elements
- **Real-time Interaction**: Dynamic conversation interface with typing indicators
- **Conversation History**: Save and load conversation sessions
- **Optimized for Arabic**: Full RTL (Right-to-Left) support and Arabic-optimized design

## 🚀 Live Demo

Check out the live demo: [المساعد الذكي](https://answerfrompdf.vercel.app/)

## 💻 Tech Stack

### Backend
- Python 3.9+
- Flask for API endpoints
- LangChain & LangGraph for AI conversation management
- Google Gemini 1.5 Pro AI model
- Python-dotenv for environment variable management

### Frontend
- Pure HTML, CSS, and JavaScript
- Interactive particle system for dynamic background
- Responsive design for all device sizes
- Modern animations and UI effects

## 🔧 Setup

### Prerequisites
- Python 3.9 or higher
- A Google API key for Gemini 1.5 Pro access

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/A11Veles/answerfrompdf.git
   cd answerfrompdf
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with your Google API key:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```

5. Create a directory for your Arabic text content:
   ```bash
   mkdir content_arabic
   ```

6. Add your text files (in UTF-8 encoding) to the `content_arabic` directory.

## 🎮 Usage

1. Start the Flask server:
   ```bash
   python api.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

3. Start chatting with the AI assistant in Arabic!

## 📁 Project Structure

```
answerfrompdf/
├── api.py              # Flask API for serving the frontend and handling requests
├── main.py             # Core chatbot logic with Gemini AI integration
├── index.html          # Frontend user interface
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (not in repo)
└── content_arabic/     # Directory for text files to be processed
```

## 🔑 Environment Variables

- `GOOGLE_API_KEY`: Your Google API key for accessing Gemini 1.5 Pro

## 🛠️ Deployment

### Deploying to Vercel

1. Fork this repository
2. Create a new project in Vercel
3. Link your GitHub repository
4. Set the following:
   - Build Command: `pip install -r requirements.txt`
   - Output Directory: `./`
   - Install Command: `pip install -r requirements.txt`
5. Add your environment variables in the Vercel dashboard
6. Deploy!

## 📝 License

This project is provided as-is. Feel free to use and modify as needed.

## 👥 Contact

For any questions or feedback, please [open an issue](https://github.com/A11Veles/answerfrompdf/issues) on GitHub.

---

Built with ❤️ using Google Gemini 1.5 Pro
