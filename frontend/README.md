# Chat with PDF - React Frontend

A modern, responsive React frontend for the ChatWithPDF RAG system. This UI allows users to upload PDF documents and ask questions about their content using an AI-powered retrieval-augmented generation system.

## Features

- 📄 **PDF Upload**: Drag-and-drop or click to upload PDF files
- 💬 **Real-time Chat**: Interactive chat interface for asking questions
- 🎨 **Modern UI**: Beautiful gradient design with smooth animations
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile devices
- ⚡ **Fast & Efficient**: Optimized for performance
- 🎯 **User Feedback**: Real-time loading states and error handling

## Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- The backend API running at `http://localhost:8000`

## Installation

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Create a `.env` file (or update the existing one):

```env
REACT_APP_API_URL=http://localhost:8000
```

## Running the Application

### Development Mode

```bash
npm start
```

The application will open in your browser at `http://localhost:3000`

### Production Build

```bash
npm build
```

This creates an optimized production build in the `build` folder.

## Project Structure

```
src/
├── components/
│   ├── FileUpload.js       # PDF upload component
│   ├── FileUpload.css      # Upload styling
│   ├── ChatInterface.js    # Chat component
│   └── ChatInterface.css   # Chat styling
├── services/
│   └── api.js              # API communication
├── App.js                  # Main app component
├── App.css                 # App styling
├── index.js                # React entry point
└── index.css               # Global styles
```

## API Endpoints Used

The frontend communicates with the following backend endpoints:

- **POST /upload** - Upload and process a PDF file
- **POST /chat** - Send a question and get an answer
- **GET /health** - Health check

## Key Components

### FileUpload Component
- Handles PDF file uploads
- Supports drag-and-drop
- Shows upload progress
- Validates file size and type

### ChatInterface Component
- Displays conversation history
- Sends questions to the backend
- Shows typing indicators while waiting for responses
- Displays source references
- Real-time message updates

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REACT_APP_API_URL` | `http://localhost:8000` | Backend API URL |

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Styling

The application uses:
- Custom CSS with modern features (CSS Grid, Flexbox, animations)
- CSS gradients and transitions
- Mobile-first responsive design

## Future Enhancements

- [ ] Dark mode support
- [ ] Message export functionality
- [ ] Multiple file upload
- [ ] User authentication
- [ ] Chat history persistence
- [ ] Document preview
- [ ] Advanced search filters

## Troubleshooting

### "Cannot reach backend" error
- Ensure the backend server is running on `http://localhost:8000`
- Check the `REACT_APP_API_URL` in `.env`
- Verify CORS settings in the backend

### PDF upload fails
- Ensure the file is a valid PDF
- Check file size (max 50MB)
- Verify backend permissions

### Slow responses
- Check network connectivity
- Verify backend performance
- Consider optimizing PDF size

## License

This project is part of the Major Project II assignment.

## Support

For issues or questions, refer to the backend documentation or contact the development team.
