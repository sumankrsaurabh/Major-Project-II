"""
Backend Initialization Module
Sets up all dependencies and models
"""

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def initialize_backend():
    """Initialize all backend components"""
    logger.info("=" * 50)
    logger.info("🚀 INITIALIZING ADVANCED AI BACKEND")
    logger.info("=" * 50)
    
    # Create necessary directories
    logger.info("📁 Creating directories...")
    directories = [
        Path("backend/models/checkpoints"),
        Path("backend/data"),
        Path("backend/scratch"),
        Path("backend/temp_uploads"),
        Path("faiss_index"),
        Path("conversations")
    ]
    
    for dir_path in directories:
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ Created: {dir_path}")
    
    # Check dependencies
    logger.info("\n📦 Checking dependencies...")
    dependencies = {
        'nltk': 'Natural Language Toolkit',
        'spacy': 'NLP library',
        'sklearn': 'Machine Learning',
        'numpy': 'Numerical computing',
        'pandas': 'Data analysis',
        'fastapi': 'Web framework',
        'PIL': 'Image processing',
        'cv2': 'Computer Vision (optional)',
        'pytesseract': 'OCR (optional)'
    }
    
    missing_deps = []
    for module, description in dependencies.items():
        try:
            __import__(module)
            logger.info(f"✓ {module}: OK ({description})")
        except ImportError:
            if module in ['cv2', 'pytesseract']:
                logger.warning(f"⚠ {module}: NOT FOUND ({description}) - Optional")
            else:
                logger.error(f"✗ {module}: NOT FOUND ({description})")
                missing_deps.append(module)
    
    if missing_deps:
        logger.error(f"\n❌ Missing required dependencies: {', '.join(missing_deps)}")
        logger.error("Install with: pip install -r requirements.txt")
        return False
    
    # Download NLTK data
    logger.info("\n📚 Downloading NLTK data...")
    try:
        import nltk
        nltk_resources = ['punkt', 'averaged_perceptron_tagger', 'maxent_ne_chunker', 'wordnet', 'words']
        for resource in nltk_resources:
            try:
                nltk.data.find(f'{resource}')
                logger.info(f"✓ NLTK/{resource}: OK")
            except LookupError:
                logger.info(f"⚠ Downloading NLTK/{resource}...")
                nltk.download(resource, quiet=True)
                logger.info(f"✓ Downloaded: {resource}")
    except Exception as e:
        logger.warning(f"⚠ NLTK setup issue: {e}")
    
    logger.info("\n" + "=" * 50)
    logger.info("✅ BACKEND INITIALIZATION COMPLETE")
    logger.info("=" * 50)
    
    # Print available features
    logger.info("\n🎯 Available Features:")
    logger.info("  📝 NLP Processing (tokenization, lemmatization, NER, sentiment)")
    logger.info("  🖼️  Computer Vision (OCR, image processing, document analysis)")
    logger.info("  🤖 Machine Learning (classification, clustering, anomaly detection)")
    logger.info("  🧠 AI Engine (intent recognition, dialogue management, reasoning)")
    logger.info("  📊 Analytics (comprehensive text analysis, insights extraction)")
    
    logger.info("\n🌐 API Endpoints:")
    logger.info("  POST /api/analysis/document     - Full document analysis")
    logger.info("  POST /api/analysis/query        - Query understanding")
    logger.info("  POST /api/analysis/insights     - Extract key insights")
    logger.info("  POST /api/analysis/answer       - Generate answers")
    logger.info("  POST /api/analysis/compare      - Compare texts")
    
    return True


def check_nlp_setup():
    """Verify NLP components are ready"""
    try:
        from core.nlp_processor import NLPPipeline
        pipeline = NLPPipeline()
        logger.info("✓ NLP Pipeline initialized successfully")
        return True
    except Exception as e:
        logger.error(f"✗ NLP Pipeline initialization failed: {e}")
        return False


def check_ml_setup():
    """Verify ML components are ready"""
    try:
        from core.machine_learning import (
            TextClassifier, DocumentClustering, AnomalyDetector
        )
        logger.info("✓ ML Models initialized successfully")
        return True
    except Exception as e:
        logger.error(f"✗ ML Models initialization failed: {e}")
        return False


def check_ai_setup():
    """Verify AI components are ready"""
    try:
        from core.ai_engine import (
            IntentRecognizer, DialogueManager, KnowledgeGraph
        )
        logger.info("✓ AI Engine initialized successfully")
        return True
    except Exception as e:
        logger.error(f"✗ AI Engine initialization failed: {e}")
        return False


if __name__ == "__main__":
    # Run initialization
    success = initialize_backend()
    
    if success:
        logger.info("\n🔍 Verifying components...")
        nlp_ok = check_nlp_setup()
        ml_ok = check_ml_setup()
        ai_ok = check_ai_setup()
        
        if nlp_ok and ml_ok and ai_ok:
            logger.info("\n🎉 All systems operational!")
        else:
            logger.warning("\n⚠️ Some components need attention")
    else:
        logger.error("\n❌ Backend initialization failed!")
        exit(1)
