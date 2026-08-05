import importlib

modules = [
    'app.routers.auth',
    'app.routers.voters',
    'app.routers.candidates',
    'app.routers.constituencies',
    'app.routers.booths',
    'app.routers.vote',
]

print('\n=================== ROUTER INSPECTION ===================')
for mod_name in modules:
    try:
        mod = importlib.import_module(mod_name)
        router = getattr(mod, 'router', None)
        if router is None:
            print(f'? {mod_name:<25}: No router attribute found!')
        else:
            print(f'? {mod_name:<25}: {len(router.routes)} routes defined')
            for r in router.routes:
                methods = getattr(r, 'methods', None) or {'ALL'}
                print(f'   +- [{", ".join(sorted(methods))}] {r.path}')
    except Exception as e:
        print(f'? {mod_name:<25}: Import error -> {e}')
print('=========================================================\n')
