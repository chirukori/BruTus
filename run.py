"""
Axiom Health • Enterprise AI Clinical Suite
Production & Development Server Launcher
Run: python run.py
Access at: http://localhost:5000
"""
import sys
import os

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import app

if __name__ == '__main__':
    print("=" * 65)
    print("  AXIOM HEALTH • AI CLINICAL INTELLIGENCE PLATFORM")
    print("  Server running at: http://localhost:5000")
    print("=" * 65)
    app.run(host='0.0.0.0', port=5000, debug=True)

