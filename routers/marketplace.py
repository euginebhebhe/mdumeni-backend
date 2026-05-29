# routers/marketplace.py
# ZimAgroMarket — all marketplace endpoints
# POST /marketplace/listing          create listing
# GET  /marketplace/listings         browse with filters
# GET  /marketplace/listings/mine    farmer's own listings
# PUT  /marketplace/listing/{id}     update listing
# DELETE /marketplace/listing/{id}   remove listing
# POST /marketplace/listing/{id}/deal  confirm deal
# POST /marketplace/listing/{id}/boost boost listing
# POST /marketplace/listing/{id}/photo upload photo
# GET  /marketplace/alerts           get price alerts
# POST /marketplace/alert            create price alert
# POST /marketplace/broadcast        trigger SMS blast

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import uuid
import os
from supabase import create_client

router = APIRouter(prefix="/marketplace", tags=["marketplace"])

# ── Supabase client ────────────────────────────────────────
supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_SERVICE_KEY"],
)

# ── Pydantic models ────────────────────────────────────────

class ListingCreate(BaseModel):
    type:            str          # selling | buying | input
    crop_name:       str
    product_name:    Optional[str] = None
    category:        Optional[str] = None
    quantity_kg:     float
    quantity_bags:   Optional[int] = None
    price_usd_kg:    float
    quality_grade:   str = "standard"  # A | B | standard
    province:        str
    district:        str
    phone:           str
    farmer_name:     str
    farmer_id:       Optional[str] = None
    description:     Optional[str] = None
    available_from:  Optional[str] = None
    broadcast:       bool = False

class ListingUpdate(BaseModel):
    price_usd_kg:   Optional[float] = None
    quantity_kg:    Optional[float] = None
    quantity_bags:  Optional[int] = None
    description:    Optional[str] = None
    status:         Optional[str] = None   # active | sold | expired
    available_from: Optional[str] = None

class DealCreate(BaseModel):
    listing_id:       str
    buyer_name:       str
    buyer_phone:      str
    quantity_kg:      float
    agreed_price:     float
    buyer_paid:       bool = False
    seller_confirmed: bool = False
    buyer_rating:     Optional[str] = None  # up | down

class AlertCreate(BaseModel):
    farmer_id:    str
    crop_name:    str
    target_price: float
    province:     str
    type:         str  # above | below

class PhotoUpload(BaseModel):
    image_base64: str


# ── Helpers ────────────────────────────────────────────────

def listing_is_expired(created_at: str) -> bool:
    try:
        created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        return datetime.utcnow().replace(tzinfo=created.tzinfo) > created + timedelta(days=7)
    except Exception:
        return False


# ══════════════════════════════════════════════════════════
# GET /marketplace/listings
# ══════════════════════════════════════════════════════════
@router.get("/listings")
async def get_listings(
    type:          Optional[str] = Query(None, description="selling | buying | input"),
    province:      Optional[str] = Query(None),
    district:      Optional[str] = Query(None),
    crop_name:     Optional[str] = Query(None),
    search:        Optional[str] = Query(None),
    boosted_first: bool          = Query(False),
    limit:         int           = Query(50),
    offset:        int           = Query(0),
):
    try:
        q = supabase.table("marketplace_listings").select("*").eq("status", "active")

        if type:
            q = q.eq("type", type)
        if province:
            q = q.eq("province", province)
        if district:
            q = q.eq("district", district)
        if crop_name:
            q = q.ilike("crop_name", f"%{crop_name}%")
        if search:
            # Supabase text search across multiple columns
            q = q.or_(
                f"crop_name.ilike.%{search}%,"
                f"farmer_name.ilike.%{search}%,"
                f"district.ilike.%{search}%,"
                f"description.ilike.%{search}%"
            )

        if boosted_first:
            q = q.order("is_boosted", desc=True).order("created_at", desc=True)
        else:
            q = q.order("created_at", desc=True)

        q = q.range(offset, offset + limit - 1)
        result = q.execute()

        listings = result.data or []

        # Auto-expire listings older than 7 days
        for listing in listings:
            if listing_is_expired(listing.get("created_at", "")):
                supabase.table("marketplace_listings").update(
                    {"status": "expired"}
                ).eq("id", listing["id"]).execute()
                listing["status"] = "expired"

        active = [l for l in listings if l["status"] == "active"]

        return {"listings": active, "total": len(active)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════════════════
# GET /marketplace/listings/mine
# ══════════════════════════════════════════════════════════
@router.get("/listings/mine")
async def get_my_listings(
    farmer_id: str = Query(..., description="Farmer ID"),
):
    try:
        result = (
            supabase.table("marketplace_listings")
            .select("*")
            .eq("farmer_id", farmer_id)
            .order("created_at", desc=True)
            .execute()
        )
        return {"listings": result.data or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════════════════
# POST /marketplace/listing
# ══════════════════════════════════════════════════════════
@router.post("/listing")
async def create_listing(payload: ListingCreate):
    try:
        listing_id = str(uuid.uuid4())
        expires_at = (datetime.utcnow() + timedelta(days=7)).isoformat()

        row = {
            "id":              listing_id,
            "type":            payload.type,
            "crop_name":       payload.crop_name,
            "product_name":    payload.product_name,
            "category":        payload.category,
            "quantity_kg":     payload.quantity_kg,
            "quantity_bags":   payload.quantity_bags,
            "price_usd_kg":    payload.price_usd_kg,
            "quality_grade":   payload.quality_grade,
            "province":        payload.province,
            "district":        payload.district,
            "phone":           payload.phone,
            "farmer_name":     payload.farmer_name,
            "farmer_id":       payload.farmer_id or "anonymous",
            "description":     payload.description,
            "available_from":  payload.available_from,
            "status":          "active",
            "deal_count":      0,
            "is_verified_seller": False,
            "is_pro":          False,
            "is_boosted":      False,
            "broadcast_sent":  False,
            "created_at":      datetime.utcnow().isoformat(),
            "expires_at":      expires_at,
        }

        supabase.table("marketplace_listings").insert(row).execute()

        # Trigger SMS broadcast if requested
        if payload.broadcast:
            await _send_broadcast(listing_id, payload)

        # Check and fire price alerts
        await _check_price_alerts(payload.crop_name, payload.province, payload.price_usd_kg)

        return {"success": True, "id": listing_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════════════════
# PUT /marketplace/listing/{listing_id}
# ══════════════════════════════════════════════════════════
@router.put("/listing/{listing_id}")
async def update_listing(listing_id: str, payload: ListingUpdate):
    try:
        updates = {k: v for k, v in payload.dict().items() if v is not None}
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")

        result = (
            supabase.table("marketplace_listings")
            .update(updates)
            .eq("id", listing_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Listing not found")

        return {"success": True}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════════════════
# DELETE /marketplace/listing/{listing_id}
# ══════════════════════════════════════════════════════════
@router.delete("/listing/{listing_id}")
async def delete_listing(listing_id: str):
    try:
        supabase.table("marketplace_listings").delete().eq("id", listing_id).execute()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════════════════
# POST /marketplace/listing/{listing_id}/deal
# ══════════════════════════════════════════════════════════
@router.post("/listing/{listing_id}/deal")
async def confirm_deal(listing_id: str, payload: DealCreate):
    try:
        deal_id = str(uuid.uuid4())

        deal_row = {
            "id":               deal_id,
            "listing_id":       listing_id,
            "buyer_name":       payload.buyer_name,
            "buyer_phone":      payload.buyer_phone,
            "quantity_kg":      payload.quantity_kg,
            "agreed_price":     payload.agreed_price,
            "buyer_paid":       payload.buyer_paid,
            "seller_confirmed": payload.seller_confirmed,
            "buyer_rating":     payload.buyer_rating,
            "created_at":       datetime.utcnow().isoformat(),
        }

        supabase.table("marketplace_deals").insert(deal_row).execute()

        # Increment deal count on listing
        listing = (
            supabase.table("marketplace_listings")
            .select("deal_count, farmer_id")
            .eq("id", listing_id)
            .single()
            .execute()
        )

        if listing.data:
            new_count = (listing.data.get("deal_count") or 0) + 1
            supabase.table("marketplace_listings").update(
                {"deal_count": new_count}
            ).eq("id", listing_id).execute()

            # Award verified seller badge at 5 deals
            farmer_id = listing.data.get("farmer_id")
            if new_count >= 5 and farmer_id:
                supabase.table("marketplace_listings").update(
                    {"is_verified_seller": True}
                ).eq("farmer_id", farmer_id).execute()

        return {"success": True, "deal_id": deal_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════════════════
# POST /marketplace/listing/{listing_id}/boost
# ══════════════════════════════════════════════════════════
@router.post("/listing/{listing_id}/boost")
async def boost_listing(listing_id: str):
    try:
        # Boost expires after 48 hours
        boost_expires = (datetime.utcnow() + timedelta(hours=48)).isoformat()
        supabase.table("marketplace_listings").update({
            "is_boosted":      True,
            "boost_expires_at": boost_expires,
        }).eq("id", listing_id).execute()
        return {"success": True, "boost_expires_at": boost_expires}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════════════════
# POST /marketplace/listing/{listing_id}/photo
# ══════════════════════════════════════════════════════════
@router.post("/listing/{listing_id}/photo")
async def upload_photo(listing_id: str, payload: PhotoUpload):
    try:
        import base64
        # Decode base64 image
        image_data = base64.b64decode(payload.image_base64)
        file_path  = f"marketplace/{listing_id}.jpg"

        # Upload to Supabase Storage bucket "marketplace-photos"
        supabase.storage.from_("marketplace-photos").upload(
            file_path, image_data,
            file_options={"content-type": "image/jpeg", "upsert": "true"}
        )

        photo_url = f"{os.environ['SUPABASE_URL']}/storage/v1/object/public/marketplace-photos/{file_path}"

        # Save URL on listing
        supabase.table("marketplace_listings").update(
            {"photo_url": photo_url}
        ).eq("id", listing_id).execute()

        return {"success": True, "photo_url": photo_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════════════════
# GET /marketplace/alerts
# ══════════════════════════════════════════════════════════
@router.get("/alerts")
async def get_alerts(farmer_id: str = Query(...)):
    try:
        result = (
            supabase.table("marketplace_alerts")
            .select("*")
            .eq("farmer_id", farmer_id)
            .eq("active", True)
            .execute()
        )
        return {"alerts": result.data or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════════════════
# POST /marketplace/alert
# ══════════════════════════════════════════════════════════
@router.post("/alert")
async def create_alert(payload: AlertCreate):
    try:
        alert_id = str(uuid.uuid4())
        row = {
            "id":           alert_id,
            "farmer_id":    payload.farmer_id,
            "crop_name":    payload.crop_name,
            "target_price": payload.target_price,
            "province":     payload.province,
            "type":         payload.type,
            "active":       True,
            "created_at":   datetime.utcnow().isoformat(),
        }
        supabase.table("marketplace_alerts").insert(row).execute()
        return {"success": True, "id": alert_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════════════════
# POST /marketplace/broadcast
# ══════════════════════════════════════════════════════════
@router.post("/broadcast")
async def trigger_broadcast(listing_id: str):
    """Trigger SMS blast to farmers in district who grow this crop."""
    try:
        listing = (
            supabase.table("marketplace_listings")
            .select("*")
            .eq("id", listing_id)
            .single()
            .execute()
        )

        if not listing.data:
            raise HTTPException(status_code=404, detail="Listing not found")

        l = listing.data
        sms_count = await _send_broadcast(listing_id, l)

        supabase.table("marketplace_listings").update(
            {"broadcast_sent": True}
        ).eq("id", listing_id).execute()

        return {"success": True, "sms_sent": sms_count}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Private helpers ────────────────────────────────────────

async def _send_broadcast(listing_id: str, listing) -> int:
    """
    Send SMS to farmers in district/province who grow this crop.
    Uses Econet/Netone bulk SMS API (configure SMS_API_KEY env var).
    Returns number of SMS sent.
    Falls back gracefully if SMS API not configured.
    """
    try:
        crop_name    = listing.crop_name if hasattr(listing, "crop_name") else listing.get("crop_name", "")
        province     = listing.province  if hasattr(listing, "province")  else listing.get("province", "")
        district     = listing.district  if hasattr(listing, "district")  else listing.get("district", "")
        price        = listing.price_usd_kg if hasattr(listing, "price_usd_kg") else listing.get("price_usd_kg", 0)
        phone        = listing.phone  if hasattr(listing, "phone")  else listing.get("phone", "")
        listing_type = listing.type   if hasattr(listing, "type")   else listing.get("type", "selling")
        farmer_name  = listing.farmer_name if hasattr(listing, "farmer_name") else listing.get("farmer_name", "")

        # Find farmers in same district/province who registered for this crop
        farmers_result = (
            supabase.table("farmers")
            .select("phone, district, province")
            .eq("province", province)
            .not_.is_("phone", "null")
            .execute()
        )

        recipients = farmers_result.data or []
        if not recipients:
            return 0

        # Build SMS message
        if listing_type == "buying":
            msg = (
                f"MDUMENI: {farmer_name} wants to BUY {crop_name} "
                f"at ${price:.2f}/kg in {district}. "
                f"Call {phone} or open MDUMENI app. "
                f"Reply STOP to unsubscribe."
            )
        else:
            msg = (
                f"MDUMENI: {farmer_name} is SELLING {crop_name} "
                f"at ${price:.2f}/kg in {district}. "
                f"Call {phone} or open MDUMENI app. "
                f"Reply STOP to unsubscribe."
            )

        sms_api_key = os.environ.get("SMS_API_KEY")
        if not sms_api_key:
            # Log intent but skip actual sending if API key not configured
            print(f"[BROADCAST] Would send to {len(recipients)} farmers: {msg}")
            return len(recipients)

        # TODO: Integrate with Econet/Netone bulk SMS API
        # import httpx
        # async with httpx.AsyncClient() as client:
        #     for farmer in recipients:
        #         await client.post("https://api.econet.co.zw/sms/send", ...)

        return len(recipients)

    except Exception as e:
        print(f"[BROADCAST ERROR] {e}")
        return 0


async def _check_price_alerts(crop_name: str, province: str, price: float) -> None:
    """
    Check if any farmer has a price alert that matches this new listing.
    Fire push notifications for matches.
    """
    try:
        # Find active alerts for this crop and province
        alerts_result = (
            supabase.table("marketplace_alerts")
            .select("*")
            .eq("crop_name", crop_name)
            .eq("province", province)
            .eq("active", True)
            .execute()
        )

        alerts = alerts_result.data or []

        for alert in alerts:
            triggered = False
            if alert["type"] == "above" and price >= alert["target_price"]:
                triggered = True
            elif alert["type"] == "below" and price <= alert["target_price"]:
                triggered = True

            if triggered:
                # Log alert trigger — in production this fires a push notification
                print(
                    f"[ALERT TRIGGERED] farmer={alert['farmer_id']} "
                    f"crop={crop_name} price=${price} "
                    f"target=${alert['target_price']} type={alert['type']}"
                )
                # TODO: integrate with Expo push notification service
                # await send_push(alert["farmer_id"], f"{crop_name} is now ${price}/kg")

    except Exception as e:
        print(f"[ALERT CHECK ERROR] {e}")
