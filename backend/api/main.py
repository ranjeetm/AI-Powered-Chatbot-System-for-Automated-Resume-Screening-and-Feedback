from fastapi import FastAPI

from fastapi.middleware.cors import (
    CORSMiddleware
)

from backend.api.routes.upload import (
    router as upload_router
)

from backend.api.routes.ranking import (
    router as ranking_router
)

from backend.api.routes.candidates import (
    router as candidate_router
)
from backend.api.routes.jobs import (
    router as jobs_router
)
from backend.api.routes.chatbot import (
    router as chatbot_router
)
from backend.api.routes.jd_matching import (
    router as jd_matching_router
)
from backend.api.routes.shortlist import (
    router as shortlist_router
)
from backend.api.auth import (
    router as auth_router
)

# -----------------------------
# DATABASE
# -----------------------------

from backend.db.initializer import initialize_database


initialize_database()

# -----------------------------
# FASTAPI APP
# -----------------------------

app = FastAPI(
    title="AI Resume Screening API"
)

import os

# --------------------------------
# CORS CONFIGURATION
# --------------------------------

allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = [origin.strip() for origin in allowed_origins_raw.split(",") if origin.strip()]

if not allowed_origins:
    allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ]

# If '*' (all origins) is explicitly requested, we can use it
# Note: allow_credentials=True cannot be used with '*' in some configurations,
# but we support it in case wildcard is requested.
is_wildcard = "*" in allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=None if is_wildcard else r"http://(localhost|127\.0\.0\.1):[0-9]+",
    allow_credentials=not is_wildcard,
    allow_methods=["*"],
    allow_headers=["*"]
)

# --------------------------------
# ROUTES
# --------------------------------

app.include_router(
    upload_router
)

app.include_router(
    ranking_router
)

app.include_router(
    candidate_router
)
app.include_router(
    jobs_router
)
app.include_router(
    chatbot_router
)
app.include_router(
    jd_matching_router
)
app.include_router(
    shortlist_router
)
app.include_router(auth_router)
