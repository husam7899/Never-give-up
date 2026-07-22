from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserWallet

router = APIRouter(prefix="/api/wallets", tags=["wallets"])


@router.post("")
def create_wallet(data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    wallet = UserWallet(
        user_id=current_user.id,
        chain=data["chain"].upper(),
        address=data["address"],
        label=data.get("label"),
        is_default=data.get("is_default", False),
    )
    if data.get("is_default"):
        db.query(UserWallet).filter(
            UserWallet.user_id == current_user.id,
            UserWallet.chain == data["chain"].upper(),
        ).update({"is_default": False})
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return {"id": wallet.id, "chain": wallet.chain, "address": wallet.address,
            "label": wallet.label, "is_default": wallet.is_default}


@router.get("")
def list_wallets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    wallets = db.query(UserWallet).filter(UserWallet.user_id == current_user.id).all()
    return {"wallets": [
        {"id": w.id, "chain": w.chain, "address": w.address,
         "label": w.label, "is_default": w.is_default}
        for w in wallets
    ]}


@router.delete("/{wallet_id}")
def delete_wallet(wallet_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    wallet = db.query(UserWallet).filter(
        UserWallet.id == wallet_id, UserWallet.user_id == current_user.id
    ).first()
    if not wallet:
        raise HTTPException(404, "Wallet not found")
    db.delete(wallet)
    db.commit()
    return {"message": "Wallet deleted"}