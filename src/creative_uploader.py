from fastapi import Request
from starlette.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pathlib import Path

from metacatalog_api.server import app, server
from metacatalog_api.router.api.read import read_router as api_read_router
from metacatalog_api.router.api.create import create_router as api_create_router
from metacatalog_api.apps.explorer.create import create_router as explorer_create
from metacatalog_api.apps.explorer.read import explorer_router
from metacatalog_api.apps.explorer import static_files


# at first we add the cors middleware to allow everyone to reach the API
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# create a template engine for creative only
creative_templates = Jinja2Templates(directory=Path(__file__).parent / 'templates')

# the main page is defined here
# this can easily be changed to a different entrypoint
@app.get('/')
def index(request: Request):
    """
    Main page for the HTML Creative Application.
    
    """
    return creative_templates.TemplateResponse(request=request, name="index.html", context={"path": server.app_prefix})


# add the API
app.include_router(api_read_router)
app.include_router(api_create_router)

# add the default explorer application (the HTML)
app.mount(f"{server.app_prefix}static", static_files, name="static")
app.include_router(explorer_router, prefix=f"/{server.app_name}")
app.include_router(explorer_create, prefix=f"/{server.app_name}")

if __name__ == '__main__':
    # run the server
    server.cli_cmd('creative_uploader:app')
