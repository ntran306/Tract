from fastapi import APIRouter

from app.api.v1 import analytics, auth, leases, properties, transactions

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(properties.router, prefix="/properties", tags=["properties"])
api_router.include_router(leases.router, prefix="/properties", tags=["leases"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])

# Added per milestone (see docs/ROADMAP.md):
# M2 (remaining): market
# M3: conversations, agent, notifications
# M4: premium, admin
