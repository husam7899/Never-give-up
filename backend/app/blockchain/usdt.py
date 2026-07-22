from web3 import Web3
from app.core.config import BSC_RPC_URL, BEP20_USDT_CONTRACT, HOT_WALLET_PRIVATE_KEY

USDT_ABI = [
    {
        "constant": False,
        "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function",
    },
]


class BEP20Service:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(BSC_RPC_URL))
        self.usdt = None
        if BEP20_USDT_CONTRACT:
            self.usdt = self.w3.eth.contract(
                address=Web3.to_checksum_address(BEP20_USDT_CONTRACT), abi=USDT_ABI
            )
        self.hot_wallet = None
        if HOT_WALLET_PRIVATE_KEY:
            self.hot_wallet = self.w3.eth.account.from_key(HOT_WALLET_PRIVATE_KEY)

    def is_connected(self) -> bool:
        return self.w3.is_connected()

    def get_balance(self, address: str) -> float:
        if not self.usdt:
            return 0.0
        decimals = self.usdt.functions.decimals().call()
        bal = self.usdt.functions.balanceOf(Web3.to_checksum_address(address)).call()
        return bal / (10 ** decimals)

    def transfer(self, to_address: str, amount: float) -> str:
        if not self.hot_wallet or not self.usdt:
            raise ValueError("Hot wallet or USDT contract not configured")
        decimals = self.usdt.functions.decimals().call()
        tx = self.usdt.functions.transfer(
            Web3.to_checksum_address(to_address), int(amount * (10 ** decimals))
        ).build_transaction({
            "from": self.hot_wallet.address,
            "nonce": self.w3.eth.get_transaction_count(self.hot_wallet.address),
            "gas": 100000,
            "gasPrice": self.w3.eth.gas_price,
        })
        signed = self.hot_wallet.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        return self.w3.to_hex(tx_hash)

    def get_hot_wallet_address(self) -> str:
        return self.hot_wallet.address if self.hot_wallet else ""


class TRC20Service:
    """Placeholder for TRC-20 USDT on Tron"""
    def is_connected(self) -> bool:
        return False