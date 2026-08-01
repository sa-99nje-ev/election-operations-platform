"""Simple script to test imports."""
import sys
sys.path.insert(0, '.')

try:
    from app.repositories.base import BaseRepository
    print("✓ BaseRepository import successful")
    print(f"✓ BaseRepository has methods: {[m for m in dir(BaseRepository) if not m.startswith('_')]}")
except Exception as e:
    print(f"✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
