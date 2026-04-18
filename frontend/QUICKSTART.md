# Quick Start Guide - Chat with PDF Frontend

## Setup Instructions

### Step 1: Install Dependencies

```bash
cd c:\Users\suman\Code\Major Project II\frontend
npm install
```

### Step 2: Verify Environment Configuration

The `.env` file is already configured with:
```
REACT_APP_API_URL=http://localhost:8000
```

If your backend runs on a different port, update this value.

### Step 3: Start the Development Server

```bash
npm start
```

The application will automatically open at `http://localhost:3000`

### Step 4: Ensure Backend is Running

Make sure your FastAPI backend is running on port 8000:
```bash
# In another terminal, from the backend directory
python -m uvicorn main:app --reload
```

## Application Usage

### 1. **Upload PDF**
   - Click on the upload area or drag-and-drop a PDF file
   - Wait for the file to be processed
   - You'll see a success message when ready

### 2. **Ask Questions**
   - Type your question in the chat input
   - Press Enter to send (or click the send button)
   - Wait for the AI to generate an answer based on your PDF

### 3. **View Responses**
   - See chat history with timestamps
   - View source references (if available)
   - Ask follow-up questions

### 4. **Manage Chat**
   - Use the 🗑️ button to clear chat history
   - Use the ↻ button to upload a new PDF
   - Chat persists during your session

## Features

✨ **Beautiful UI**
- Modern gradient design
- Smooth animations
- Responsive layout

🚀 **Performance**
- Real-time chat interface
- Efficient file uploads
- Optimized rendering

📱 **Mobile Friendly**
- Works on all devices
- Touch-friendly interface
- Responsive design

🎯 **User Experience**
- Drag-and-drop uploads
- Loading indicators
- Error messages
- Typing animations

## Customization

### Change Colors
Edit `src/App.css` and update the gradient colors:
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Adjust Layout
- Modify max-width in `.container` class
- Adjust padding/margins in component CSS
- Change font sizes as needed

### API Configuration
Edit `src/services/api.js` to:
- Change timeout values
- Add request/response interceptors
- Handle authentication

## Build for Production

```bash
npm run build
```

This creates an optimized production build in the `build` folder that can be deployed.

## Troubleshooting

### Backend Connection Issues
```bash
# Test backend connectivity
curl http://localhost:8000/health
```

### Port Already in Use
```bash
# Change React port
PORT=3001 npm start
```

### Clear Cache
```bash
npm cache clean --force
rm -rf node_modules
npm install
```

## Project Structure

```
frontend/
├── public/
│   └── index.html              # HTML entry point
├── src/
│   ├── components/
│   │   ├── FileUpload.js       # PDF upload component
│   │   ├── FileUpload.css
│   │   ├── ChatInterface.js    # Chat component
│   │   └── ChatInterface.css
│   ├── services/
│   │   └── api.js              # API client
│   ├── App.js                  # Main component
│   ├── App.css
│   ├── index.js                # Entry point
│   └── index.css               # Global styles
├── package.json
├── .env                        # Environment variables
├── .gitignore
└── README.md
```

## Next Steps

1. Start your backend server
2. Run `npm install` to install dependencies
3. Run `npm start` to launch the application
4. Upload a PDF and start asking questions!

## Support

For issues:
- Check console errors (F12 → Console)
- Verify backend is running
- Check .env configuration
- Review API response in Network tab

Happy coding! 🚀
