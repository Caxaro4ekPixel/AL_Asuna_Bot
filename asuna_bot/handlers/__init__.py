from .dev_tools import dev_router
from .ass_to_srt import convert_router
from .registration import admin_router
from .start import start_router
from .supergroup import supergroup_router
from .submitters import submitter_router

__routers__ = (
    dev_router, 
    convert_router, 
    admin_router, 
    start_router, 
    supergroup_router,
    submitter_router,
)