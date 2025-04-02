from typing import Literal
from fastapi import Request, APIRouter, HTTPException
from starlette.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pathlib import Path
from starlette.staticfiles import StaticFiles

from metacatalog_api import core
from metacatalog_api.server import app, server
from metacatalog_api.router.api.read import read_router as api_read_router
from metacatalog_api.router.api.create import create_router as api_create_router
from metacatalog_api.apps.explorer.create import create_router as explorer_create
from metacatalog_api.apps.explorer.read import explorer_router, templates as explorer_templates
from metacatalog_api.apps.explorer import static_files

from creative_tools import entryToBbox, get_static_metadata, get_mandatory_extra


# at first we add the cors middleware to allow everyone to reach the API
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# create a template engine for creative only
creative_templates = Jinja2Templates(directory=Path(__file__).parent / 'templates')

# serve static creative files
creative_assets = StaticFiles(directory=Path(__file__).parent / 'assets')

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
@creative_pages.get('/entries.html')
def entries_list(request: Request, limit: int = None, offset: int = None):
    entries = core.entries(limit=limit, offset=offset)
    return creative_templates.TemplateResponse(request=request, name="entries.html", context={"path": server.app_prefix, "entries": entries})

@creative_pages.get('/page/entries.html')
def get_entries_page(request: Request):
    return creative_templates.TemplateResponse(request=request, name="entries_page.html", context={"path": server.app_prefix, "root_path": server.uri_prefix})

@creative_pages.get('/page/entries/{entry_id}.html')
def get_entry_page(request: Request, entry_id: int):
    return creative_templates.TemplateResponse(request=request, name="entry_page.html", context={"path": server.app_prefix, "entry_id": entry_id})


@creative_pages.get('/entries/{entry_id}.xml')
def get_entry_xml_metadata(request: Request, entry_id: int, template: Literal['default', 'zku', 'dublin'] = 'default'):
    entries = core.entries(ids=entry_id)
    if len(entries) == 0:
        raise HTTPException(status_code=404, detail=f"Metadata <ID={entries[0].id}> was not found")

    entry = entries[0]

    if template == 'default':
        return explorer_templates.TemplateResponse(request=request, name="entry.xml", context={"entry": entry, "path": server.app_prefix}, media_type='application/xml')
    elif template == 'zku':
        if entry.datasource is None:
            raise HTTPException(status_code=404, detail=f"Metadata <ID={entry.id}> has no datasource associated. We need a datasource to export to RADAR.")
        
        bbox = entryToBbox(entry)
        meta = get_static_metadata()
        extra, errors = get_mandatory_extra(entry)
        if len(errors) > 0:
            print("There are errors")
        return creative_templates.TemplateResponse(request=request, name="entry.radar.zku.xml", context={"entry": entry,  "bbox": bbox,  "path": server.app_prefix, **meta, **extra}, media_type='application/xml')
    elif template == 'dublin':
        return creative_templates.TemplateResponse(request=request, name="entry.dublin.xml", context={"entry": entry, "path": server.app_prefix}, media_type='application/xml')
    else:
        raise HTTPException(status_code=404, detail=f"Template {template} not found")

# add the API
app.include_router(api_read_router)
app.include_router(api_create_router)

# add the default explorer application (the HTML)
app.mount(f"{server.app_prefix}static", static_files, name="static")
app.include_router(explorer_router, prefix=f"/{server.app_name}")
app.include_router(explorer_create, prefix=f"/{server.app_name}")
app.include_router(creative_pages, prefix=f"/{server.app_name}/creative")

# register file server for creative assets
app.mount(f"{server.app_prefix}assets", creative_assets, name="assets")

if __name__ == '__main__':
    # run the server
    server.cli_cmd('creative_uploader:app')
