import importlib
import pkgutil
import pathlib

# ambil path folder ini (models/)
package_dir = pathlib.Path(__file__).resolve().parent

# loop semua module .py di folder models
for module_info in pkgutil.iter_modules([str(package_dir)]):
    if module_info.name == "__init__":
        continue
    importlib.import_module(f"{__name__}.{module_info.name}")
