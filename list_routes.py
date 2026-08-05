"""
Deep Route Inspector for FastAPI Sub-Routers.
"""

from fastapi.routing import APIRoute
from app.main import app


def inspect_routes():
    print("\n================ Registered System Routes ================")
    
    routes_found = []

    def extract_routes(route_list):
        for route in route_list:
            if isinstance(route, APIRoute):
                methods = ",".join(sorted(route.methods))
                routes_found.append((methods, route.path))
            elif hasattr(route, "routes"):
                extract_routes(route.routes)

    extract_routes(app.routes)

    for method, path in sorted(set(routes_found), key=lambda x: x[1]):
        print(f"{method:<12} {path}")

    print("=========================================================\n")


if __name__ == "__main__":
    inspect_routes()