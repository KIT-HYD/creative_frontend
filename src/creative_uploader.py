from typing import Literal
from fastapi import Request, APIRouter, HTTPException
from starlette.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pathlib import Path

from metacatalog_api import core
from metacatalog_api.server import app, server
from metacatalog_api.router.api.read import read_router as api_read_router
from metacatalog_api.router.api.create import create_router as api_create_router
from metacatalog_api.apps.explorer.create import create_router as explorer_create
from metacatalog_api.apps.explorer.read import explorer_router, templates as explorer_templates
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

# create a router for extra CREATIVE pages
creative_pages = APIRouter()

# the main page is defined here
# this can easily be changed to a different entrypoint
@app.get('/')
def index(request: Request):
    """
    Main page for the HTML Creative Application.
    
    """
    return creative_templates.TemplateResponse(request=request, name="index.html", context={"path": server.app_prefix})


# we replace some of the default explorer pages with our own
@creative_pages.get('/creative/entries.html')
def entries_list(request: Request, limit: int = None, offset: int = None):
    entries = core.entries(limit=limit, offset=offset)
    return creative_templates.TemplateResponse(request=request, name="entries.html", context={"path": server.app_prefix, "entries": entries})

@creative_pages.get('/page/entries.html')
def get_entries_page(request: Request):
    return creative_templates.TemplateResponse(request=request, name="entries_page.html", context={"path": server.app_prefix, "root_path": server.uri_prefix})

@creative_pages.get('/page/entries/{entry_id}.html')
def get_entry_page(request: Request, entry_id: int):
    return creative_templates.TemplateResponse(request=request, name="entry_page.html", context={"path": server.app_prefix, "entry_id": entry_id})


@creative_pages.get('/creative/entries/{entry_id}.xml')
def get_entry_xml_metadata(request: Request, entry_id: int, template: Literal['default', 'zku', 'dublin'] = 'default'):
    entries = core.entries(ids=entry_id)
    if template == 'default':
        return explorer_templates.TemplateResponse(request=request, name="entry.xml", context={"entry": entries[0], "path": server.app_prefix}, media_type='application/xml')
    elif template == 'zku':
        return creative_templates.TemplateResponse(request=request, name="entry.radar.zku.xml", context={"entry": entries[0], "path": server.app_prefix})
    elif template == 'dublin':
        return creative_templates.TemplateResponse(request=request, name="entry.dublin.xml", context={"entry": entries[0], "path": server.app_prefix}, media_type='application/xml')
    else:
        raise HTTPException(status_code=404, detail=f"Template {template} not found")

# add the API
app.include_router(api_read_router)
app.include_router(api_create_router)

# add the default explorer application (the HTML)
app.mount(f"{server.app_prefix}static", static_files, name="static")
app.include_router(explorer_router, prefix=f"/{server.app_name}")
app.include_router(explorer_create, prefix=f"/{server.app_name}")
app.include_router(creative_pages, prefix=f"/{server.app_name}")

if __name__ == '__main__':
    # run the server
    server.cli_cmd('creative_uploader:app')
