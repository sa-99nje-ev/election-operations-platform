import sys, pathlib, importlib

print('\n=================== COMPLETE PROJECT DIAGNOSTIC ===================')

# 1. Config
try:
    from app.core.config import settings
    print(f'1. [CONFIG] ✅ ENV: {settings.ENVIRONMENT}')
except Exception as e:
    print(f'1. [CONFIG] ❌ {e}')

# 2. Database
try:
    from app.database import engine
    print(f'2. [DATABASE] ✅ {getattr(engine, "driver", "N/A")}')
except Exception as e:
    print(f'2. [DATABASE] ❌ {e}')

# 3. Models
try:
    from app.models.user import User
    print('3. [MODELS] ✅ User model loaded')
except Exception as e:
    print(f'3. [MODELS] ❌ {e}')

# 4. Routes
try:
    from app.main import app
    print('\n4. [LIVE FASTAPI ROUTES]')
    for r in app.routes:
        if hasattr(r, 'path'):
            methods = list(getattr(r, 'methods', ['GET']))
            print(f'   {methods[0]:<6} {r.path}')
except Exception as e:
    print(f'4. [ROUTES] ❌ {e}')

# 5. Routers
try:
    print('\n5. [APP.ROUTERS MODULE SCAN]')
    for f in pathlib.Path('app/routers').glob('*.py'):
        if f.name != '__init__.py':
            try:
                m = importlib.import_module(f'app.routers.{f.stem}')
                exports = [k for k in dir(m) if not k.startswith('_')]
                print(f'   - {f.name}: {exports}')
            except Exception as e:
                print(f'   - {f.name}: ERROR - {e}')
except Exception as e:
    print(f'5. [ROUTERS] ❌ {e}')

print('\n===================================================================')
