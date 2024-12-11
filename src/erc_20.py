from typing import Union

from loguru import logger

from src.client import Client
from src.utils import Utils
from src.vars import ERC20_ABI, ERC20_BYTECODE


class ERC20Manager():
    async def deploy_erc20(self, client_ink: Client, name: str, symbol: str, account_index: int, is_first_tx: bool = False) -> Union[bool, str]:
        balance = await client_ink.w3.eth.get_balance(client_ink.wallet_address)
    
        if balance <= 0:
            logger.error(f'Account {account_index+1} | {client_ink.wallet_address} | Deploy cancelled: zero balance.')
            return False
    
        try:
            logger.info(f'Account {account_index+1} | {client_ink.wallet_address} | Attempting to deploy ERC-20 contract in {client_ink.network.name}...')
            if is_first_tx:
                result = await client_ink.deploy_contract(
                    name=name,
                    symbol=symbol,
                    abi_path=ERC20_ABI,
                    bytecode_path=ERC20_BYTECODE
                )
            else:
                result = await Utils.execute_with_delay(client_ink.deploy_contract(
                    name=name,
                    symbol=symbol,
                    abi_path=ERC20_ABI,
                    bytecode_path=ERC20_BYTECODE
                ), client_ink.wallet_address, account_index)
            
            return result
        except Exception as e:
            logger.error(f'Account {account_index+1} | {client_ink.wallet_address} | Error during deploying ERC-20 contract: {e}.')
            return False

    async def interact_with_contract(self, client_ink: Client, contract_address: str, account_index: int) -> bool:
        balance = await client_ink.w3.eth.get_balance(client_ink.wallet_address)
        
        if balance <= 0:
            logger.error(f'Account {account_index+1} | {client_ink.wallet_address} | Interact cancelled: zero balance.')
            return False
        
        try:
            logger.info(f'Account {account_index+1} | {client_ink.wallet_address} | Attempting to interact with ERC-20 contract {contract_address}...')
            result = await Utils.execute_with_delay(client_ink.random_interact_with_contract(
                contract_address=contract_address,
                abi_path=ERC20_ABI
            ), client_ink.wallet_address, account_index)
            
            return result
        except Exception as e:
            logger.error(f'Account {account_index+1} | {client_ink.wallet_address} | Error during interacting with contract: {e}.')
            return False
