from fastapi.templating import Jinja2Templates
from src.services.common_context import common_context
from src.configuration.config import SRC_DIR
from fastapi import Request

class CustomJinja2Templates(Jinja2Templates):
    def TemplateResponse(self, name, context: dict, **kwargs):
        request = context.get("request")
        if request:
            # inject common_context ke semua render
            context.update(common_context(request))
        return super().TemplateResponse(name, context, **kwargs)


# inisialisasi templates global
templates = CustomJinja2Templates(directory=SRC_DIR / "templates" / "pages")
