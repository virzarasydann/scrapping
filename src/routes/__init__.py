
import importlib.util
from pathlib import Path

def load_module_from_path(module_path, module_name):
    """Load module dari path file"""
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def load_routers_from_folder(folder_name):
    """Load routers dengan file path langsung"""
    routers = []
    folder_path = Path(__file__).parent / folder_name
    
    if not folder_path.exists():
        return routers
    
    for file_path in folder_path.glob("*.py"):
        if file_path.name == "__init__.py":
            continue
            
        try:
            module = load_module_from_path(
                file_path, 
                f"routes_{folder_name}_{file_path.stem}"
            )
            
            if hasattr(module, 'router'):
                routers.append(module.router)
                print(f"✅ Loaded: {folder_name}/{file_path.stem}")
                
        except Exception as e:
            print(f"❌ Failed to load {file_path.stem}: {e}")
    
    return routers

api_routers = load_routers_from_folder("api")
page_routers = load_routers_from_folder("pages")