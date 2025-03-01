import asyncio
import random
from typing import Optional, Union

from web3 import AsyncWeb3
from loguru import logger

from src.utils import Utils
from src.models import Network, TokenAmount


class Client:
    def __init__(self, private_key: str, network: Network, proxy: str = None):
        self.private_key = private_key
        self.network = network
        self.proxy = proxy
        if proxy:
            self.w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(endpoint_uri=self.network.rpc, request_kwargs={"proxy": f"http://{proxy}"}))
        else:
            self.w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(endpoint_uri=self.network.rpc))
        self.wallet_address = AsyncWeb3.to_checksum_address(self.w3.eth.account.from_key(private_key).address)
        self.nonce_lock = asyncio.Lock()

    async def get_balance(self) -> int:
        return await self.w3.eth.get_balance(self.wallet_address)

    async def get_transaction_count(self) -> int:
        async with self.nonce_lock:
            return await self.w3.eth.get_transaction_count(self.wallet_address)
        
    async def send_transaction(self, to_: str = None, data: str = None, value: int = None, tx_params: dict = None) -> Optional[str]:
        if not tx_params:
            tx_params = {
                'from': self.wallet_address,
                'gasPrice': await self.w3.eth.gas_price,
                'nonce': await self.get_transaction_count(),
                'chainId': await self.w3.eth.chain_id
            }

            if to_:
                tx_params['to'] = AsyncWeb3.to_checksum_address(to_)

            if data:
                tx_params['data'] = data

            if value:
                tx_params['value'] = value

            try:
                estimate_gas = await self.w3.eth.estimate_gas(tx_params)
                tx_params['gas'] = int(estimate_gas * 1.1)
            
            except Exception as e:
                logger.warning(f'{self.wallet_address} | Error estimating gas: {e}')
                return None
        
        else:
            tx_params = tx_params
        
        try:
            sign = self.w3.eth.account.sign_transaction(tx_params, self.private_key)
            return await self.w3.eth.send_raw_transaction(sign.rawTransaction)
        
        except Exception as e:
            if 'nonce too low' in str(e):
                tx_params['nonce'] += 1
                return await self.send_transaction(tx_params=tx_params)
            elif 'replacement transaction underpriced' in str(e):
                tx_params['nonce'] += 1
                return await self.send_transaction(tx_params=tx_params)
            
            logger.warning(f'{self.wallet_address} | Error sending transaction: {e}')
            return None

    async def send_transaction_with_abimethod(self, contract, method: str, *args, value: Optional[int] = None) -> Optional[str]:
        tx_params = {
            'to': contract.address,
            'from': self.wallet_address,
            'data': contract.encode_abi(method, args=args),
            'gasPrice': await self.w3.eth.gas_price,
            'nonce': await self.get_transaction_count(),
            'chainId': await self.w3.eth.chain_id
        }
        
        if value:
            tx_params['value'] = value
        
        try:
            estimate_gas = await self.w3.eth.estimate_gas(tx_params)
            tx_params['gas'] = int(estimate_gas * 1.1) 
        
        except Exception as e:
            logger.warning(f'{self.wallet_address} | Error estimating gas: {e}')
            return None
        
        return await self.send_transaction(tx_params=tx_params)

    async def _register_domain(self, domain_name: str, expiries: int, contract_address: str, abi_path: str, value: int) -> Optional[bool]:
        contract_abi = await Utils.read_json(abi_path)
        contract = self.w3.eth.contract(address=AsyncWeb3.to_checksum_address(contract_address), abi=contract_abi)

        args = [[self.wallet_address], [domain_name], [expiries], '0x0000000000000000000000000000000000000000', 0]
        
        tx = await self.send_transaction_with_abimethod(contract, 'registerDomains', *args, value=value)
        if tx:
            return await self.verif_tx(tx)
        return None
    
    async def bridge_eth(self, contract_address: str, value: Union[TokenAmount, int]) -> Optional[bool]:
        bal = await self.get_balance()
        if bal <= value:
            logger.warning(f'{self.wallet_address} | Bridge cancelled: balance is less than amount to bridge.')
            return None

        tx = await self.send_transaction(to_=contract_address, value=value)
        if tx:
            await self.verif_tx(tx)
            return True

    async def deploy_contract(self, name: str, symbol: str, abi_path: str, bytecode_path: str, increase_gas: float = 1.1) -> Optional[str]:
        contract_abi = await Utils.read_json(abi_path)
        contract_bytecode = await Utils.read_file(bytecode_path)
        contract = self.w3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)

        tx_params = {
            'chainId': await self.w3.eth.chain_id,
            'from': self.wallet_address,
            'nonce': await self.get_transaction_count(),
            'gasPrice': await self.w3.eth.gas_price
        }

        try:
            estimate_gas = await contract.constructor(name, symbol).estimate_gas({'from': self.wallet_address})
            tx_params['gas'] = int(estimate_gas * increase_gas)
        
        except Exception as e:
            logger.warning(f'{self.wallet_address} | Error estimating gas: {e}')
            return None

        construct_tx = await contract.constructor(name, symbol).build_transaction(tx_params)
        tx = await self.send_transaction(tx_params=construct_tx)

        if tx:
            if await self.verif_tx(tx):
                tx_receipt = await self.w3.eth.wait_for_transaction_receipt(tx, timeout=200)
                return tx_receipt.contractAddress
            
            logger.warning(f'{self.wallet_address} | Contract deployment failed.')
            return None

    async def mint_nft(self, contract_address: str, abi_path: str) -> Optional[bool]:
        contract_abi = await Utils.read_json(abi_path)
        contract = self.w3.eth.contract(address=AsyncWeb3.to_checksum_address(contract_address), abi=contract_abi)

        tx = await self.send_transaction_with_abimethod(contract, 'createCollectible')
        if tx:
            return await self.verif_tx(tx)
        return None

    async def random_interact_with_contract(self, contract_address: str, abi_path: str) -> Optional[bool]:
        contract_abi = await Utils.read_json(abi_path)
        contract = self.w3.eth.contract(address=AsyncWeb3.to_checksum_address(contract_address), abi=contract_abi)

        values = [10000, 50000, 100000, 250000, 500000, 1000000]
        available_methods = ['mint', 'burn', 'pause']
        args = []

        random_method = random.choice(available_methods)
        
        if random_method == 'mint':
            random_value = random.choice(values)
            args = [self.wallet_address, random_value * 10 ** 18]
        elif random_method == 'burn':
            random_value = random.choice(values)
            args = [random_value * 10 ** 18]
        
        tx = await self.send_transaction_with_abimethod(contract, random_method, *args)
        
        if tx:
            return await self.verif_tx(tx)
        return None
    
    async def verif_tx(self, tx_hash: str) -> bool:
        try:
            data = await self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=200)
            
            if data.get('status') == 1:
                logger.debug(f'{self.wallet_address} | Transaction was successful: {tx_hash.hex()}. Explorer: {self.network.explorer}')
                return True
            
            else:
                logger.warning(f'{self.wallet_address} | Transaction failed: {data["transactionHash"].hex()}. Explorer: {self.network.explorer}')
                return False
        
        except Exception as e:
            logger.warning(f'{self.wallet_address} | Unexpected error in <verif_tx> function: {e}')
            return False
