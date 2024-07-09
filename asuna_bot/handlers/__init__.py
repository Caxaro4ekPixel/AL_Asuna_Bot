from .dev_tools import dev_router
from .ass_to_srt import convert_router
from .registration import admin_router
from .start import start_router
from .supergroup import supergroup_router
from .time import time_router
from .settings import settings_router
from .report import report_router

__routers__ = (
    dev_router, 
    convert_router, 
    admin_router, 
    start_router, 
    supergroup_router,
    time_router,
    settings_router,
    report_router,
)