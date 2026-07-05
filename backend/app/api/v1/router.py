from fastapi import APIRouter

from app.api.v1 import auth

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Added per milestone (see docs/ROADMAP.md):
# M1: properties, transactions, leases
# M2: analytics, market
# M3: conversations, agent, notifications
# M4: premium, admin
