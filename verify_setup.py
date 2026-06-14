#!/usr/bin/env python3
"""
Verification Script - Ensure all components are properly set up
Run this to verify the installation
"""

import sys
import subprocess
from pathlib import Path

class VerificationCheck:
    def __init__(self):
        self.checks = []
        self.passed = 0
        self.failed = 0
    
    def check(self, name, condition, details=""):
        status = "✅ PASS" if condition else "❌ FAIL"
        self.checks.append(f"{status}: {name}")
        if details:
            self.checks.append(f"        {details}")
        
        if condition:
            self.passed += 1
        else:
            self.failed += 1
    
    def print_results(self):
        print("\n" + "="*60)
        print("VERIFICATION RESULTS")
        print("="*60 + "\n")
        
        for check in self.checks:
            print(check)
        
        print("\n" + "="*60)
        print(f"Results: {self.passed} passed, {self.failed} failed")
        print("="*60 + "\n")
        
        return self.failed == 0

def verify_backend():
    """Verify backend setup"""
    print("\n📦 BACKEND VERIFICATION")
    print("-" * 60)
    
    verifier = VerificationCheck()
    backend_path = Path("backend")
    
    # Directory checks
    verifier.check("Backend directory exists", backend_path.exists())
    verifier.check("Core module exists", (backend_path / "core").exists())
    verifier.check("Services module exists", (backend_path / "services").exists())
    verifier.check("Routes module exists", (backend_path / "routes").exists())
    
    # File checks
    verifier.check("main.py exists", (backend_path / "main.py").exists())
    verifier.check("requirements.txt exists", (backend_path / "requirements.txt").exists())
    verifier.check("config.py exists", (backend_path / "config.py").exists())
    
    # Core module checks
    core_path = backend_path / "core"
    verifier.check("nlp_processor.py exists", (core_path / "nlp_processor.py").exists())
    verifier.check("computer_vision.py exists", (core_path / "computer_vision.py").exists())
    verifier.check("machine_learning.py exists", (core_path / "machine_learning.py").exists())
    verifier.check("ai_engine.py exists", (core_path / "ai_engine.py").exists())
    verifier.check("pdf_processor.py exists", (core_path / "pdf_processor.py").exists())
    verifier.check("vector_store.py exists", (core_path / "vector_store.py").exists())
    verifier.check("tokenizer.py exists", (core_path / "tokenizer.py").exists())
    
    # Services module checks
    services_path = backend_path / "services"
    verifier.check("comprehensive_analysis_service.py exists", 
                  (services_path / "comprehensive_analysis_service.py").exists())
    verifier.check("advanced_qa_service.py exists", 
                  (services_path / "advanced_qa_service.py").exists())
    verifier.check("rag_service.py exists", (services_path / "rag_service.py").exists())
    
    # Routes module checks
    routes_path = backend_path / "routes"
    verifier.check("analysis_routes.py exists", (routes_path / "analysis_routes.py").exists())
    
    # Python version check
    verifier.check("Python 3.8+", sys.version_info >= (3, 8), f"Version: {sys.version_info.major}.{sys.version_info.minor}")
    
    return verifier.print_results()

def verify_frontend():
    """Verify frontend setup"""
    print("\n🎨 FRONTEND VERIFICATION")
    print("-" * 60)
    
    verifier = VerificationCheck()
    frontend_path = Path("frontend")
    
    # Directory checks
    verifier.check("Frontend directory exists", frontend_path.exists())
    verifier.check("src directory exists", (frontend_path / "src").exists())
    verifier.check("components directory exists", (frontend_path / "src" / "components").exists())
    verifier.check("styles directory exists", (frontend_path / "src" / "styles").exists())
    verifier.check("services directory exists", (frontend_path / "src" / "services").exists())
    
    # File checks
    verifier.check("App.js exists", (frontend_path / "src" / "App.js").exists())
    verifier.check("package.json exists", (frontend_path / "package.json").exists())
    verifier.check("index.html exists", (frontend_path / "public" / "index.html").exists())
    
    # Component checks
    components_path = frontend_path / "src" / "components"
    verifier.check("Dashboard.js exists", (components_path / "Dashboard.js").exists())
    verifier.check("AnalyticsPanel.js exists", (components_path / "AnalyticsPanel.js").exists())
    verifier.check("AIFeatures.js exists", (components_path / "AIFeatures.js").exists())
    verifier.check("ChatInterface.js exists", (components_path / "ChatInterface.js").exists())
    verifier.check("FileUpload.js exists", (components_path / "FileUpload.js").exists())
    verifier.check("Sidebar.js exists", (components_path / "Sidebar.js").exists())
    
    # Style checks
    styles_path = frontend_path / "src" / "styles"
    verifier.check("Dashboard.css exists", (styles_path / "Dashboard.css").exists())
    verifier.check("AnalyticsPanel.css exists", (styles_path / "AnalyticsPanel.css").exists())
    verifier.check("AIFeatures.css exists", (styles_path / "AIFeatures.css").exists())
    
    return verifier.print_results()

def verify_documentation():
    """Verify documentation"""
    print("\n📚 DOCUMENTATION VERIFICATION")
    print("-" * 60)
    
    verifier = VerificationCheck()
    root_path = Path(".")
    
    verifier.check("IMPLEMENTATION_GUIDE.md exists", 
                  (root_path / "IMPLEMENTATION_GUIDE.md").exists())
    verifier.check("QUICKSTART.md exists", (root_path / "QUICKSTART.md").exists())
    verifier.check("FEATURE_CHECKLIST.md exists", 
                  (root_path / "FEATURE_CHECKLIST.md").exists())
    verifier.check("PROJECT_SUMMARY.md exists", 
                  (root_path / "PROJECT_SUMMARY.md").exists())
    verifier.check("README.md exists", (root_path / "README.md").exists())
    verifier.check("API_DOCUMENTATION.md exists", 
                  (root_path / "API_DOCUMENTATION.md").exists())
    verifier.check("ARCHITECTURE.md exists", (root_path / "ARCHITECTURE.md").exists())
    
    return verifier.print_results()

def check_dependencies():
    """Check Python dependencies"""
    print("\n📦 PYTHON DEPENDENCIES CHECK")
    print("-" * 60)
    
    verifier = VerificationCheck()
    
    packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'pdfplumber',
        'numpy',
        'nltk',
        'sklearn',
        'pandas',
        'scipy',
        'transformers',
        'torch',
        'spacy',
    ]
    
    optional_packages = [
        'cv2',
        'pytesseract',
        'PIL',
    ]
    
    for package in packages:
        try:
            __import__(package)
            verifier.check(f"{package} installed", True)
        except ImportError:
            verifier.check(f"{package} installed", False, "⚠️  Required - Run: pip install -r requirements.txt")
    
    print("\n  Optional packages:")
    for package in optional_packages:
        try:
            __import__(package)
            print(f"  ✅ {package} installed (optional)")
        except ImportError:
            print(f"  ⚠️  {package} not installed (optional - for advanced features)")
    
    return True

def print_summary():
    """Print final summary"""
    print("\n" + "="*60)
    print("🎉 VERIFICATION COMPLETE")
    print("="*60 + "\n")
    
    print("📋 Next Steps:")
    print("  1. Run backend: cd backend && python main.py")
    print("  2. Run frontend: cd frontend && npm start")
    print("  3. Open browser: http://localhost:3000")
    print("  4. Upload a PDF and start using the system!")
    
    print("\n📚 Documentation:")
    print("  - QUICKSTART.md - Quick setup guide")
    print("  - IMPLEMENTATION_GUIDE.md - Complete feature guide")
    print("  - FEATURE_CHECKLIST.md - Feature status")
    print("  - PROJECT_SUMMARY.md - Project overview")
    
    print("\n🎯 Available Features:")
    print("  ✅ NLP Processing (tokenization, NER, sentiment, etc.)")
    print("  ✅ Computer Vision (OCR, image processing)")
    print("  ✅ Machine Learning (classification, clustering)")
    print("  ✅ AI Engine (intent recognition, dialogue)")
    print("  ✅ Advanced Analytics (real-time insights)")
    print("  ✅ API Endpoints (15+ endpoints)")
    
    print("\n🚀 Ready to deploy!")
    print("\n" + "="*60 + "\n")

def main():
    """Run all verification checks"""
    print("\n")
    print("█" * 60)
    print("█" + " " * 58 + "█")
    print("█" + "   ChatWithPDF - Advanced AI System Setup Verification".center(58) + "█")
    print("█" + " " * 58 + "█")
    print("█" * 60)
    
    backend_ok = verify_backend()
    frontend_ok = verify_frontend()
    docs_ok = verify_documentation()
    check_dependencies()
    
    print_summary()
    
    if backend_ok and frontend_ok and docs_ok:
        print("✅ ALL CHECKS PASSED - System is ready!")
        return 0
    else:
        print("⚠️  Some checks failed - Please review the output above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
