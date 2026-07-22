import os
from dotenv import load_dotenv

load_dotenv()
raw_db_url = os.getenv("DATABASE_URL", "sqlite:///./p2p_market.db")
print(f"DEBUG: DATABASE_URL raw: {raw_db_url}")
# Fix Railway/Postgres URL if it starts with postgres:// instead of postgresql://
if raw_db_url and raw_db_url.startswith("postgres://"):
    raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)
# Handle edge case where it might just be the hostname or empty
if not raw_db_url or "://" not in raw_db_url:
     raw_db_url = "sqlite:///./p2p_market.db"

DATABASE_URL = raw_db_url
print(f"DEBUG: DATABASE_URL parsed: {DATABASE_URL}")
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production-please")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

# Demo Mode configuration
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"

# Blockchain
BEP20_USDT_CONTRACT = os.getenv("BEP20_USDT_CONTRACT", "0x55d398326f99059fF775485246999027B3197955")
TRC20_USDT_CONTRACT = os.getenv("TRC20_USDT_CONTRACT", "")
BSC_RPC_URL = os.getenv("BSC_RPC_URL", "https://bsc-dataseed.binance.org/")
TRON_RPC_URL = os.getenv("TRON_RPC_URL", "https://api.trongrid.io/")
HOT_WALLET_PRIVATE_KEY = os.getenv("HOT_WALLET_PRIVATE_KEY", "")

# Payment
TELEBIRR_API_KEY = os.getenv("TELEBIRR_API_KEY", "")
TELEBIRR_MERCHANT_ID = os.getenv("TELEBIRR_MERCHANT_ID", "")

PLATFORM_FEE_PERCENT = float(os.getenv("PLATFORM_FEE_PERCENT", "0.5"))