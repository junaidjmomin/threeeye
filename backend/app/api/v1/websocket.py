import asyncio

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from app.core.database import async_session_factory
from app.core.security import decode_access_token
from app.models.vendor import Vendor

router = APIRouter()

# Track connected clients
connected_clients: set[WebSocket] = set()


async def broadcast(message: dict):
    """Send a message to all connected WebSocket clients."""
    dead = set()
    for ws in connected_clients:
        try:
            await ws.send_json(message)
        except Exception:
            dead.add(ws)
    connected_clients.difference_update(dead)


@router.websocket("/ws/live")
async def websocket_live(
    websocket: WebSocket,
    token: str = Query(default=""),
):
    # Validate token
    payload = decode_access_token(token) if token else None
    if payload is None:
        await websocket.close(code=4001, reason="Unauthorized")
        return

    await websocket.accept()
    connected_clients.add(websocket)

    try:
        # Send CERT-In clock ticks every second
        while True:
            async with async_session_factory() as db:
                result = await db.execute(
                    select(Vendor).where(Vendor.cert_in_clock_active == True)  # noqa: E712
                )
                active_clocks = result.scalars().all()

                for v in active_clocks:
                    clock = v.cert_in_clock_dict()
                    if clock:
                        await websocket.send_json({
                            "type": "cert_in_clock_tick",
                            "vendorId": v.id,
                            "remaining": clock["remaining"],
                        })

            # Also listen for client messages (keepalive pings)
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
            except asyncio.TimeoutError:
                pass

    except WebSocketDisconnect:
        pass
    finally:
        connected_clients.discard(websocket)
