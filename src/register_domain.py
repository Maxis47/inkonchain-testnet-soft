import random
from typing import Optional

from loguru import logger

from src.client import Client
from src.vars import DOMAIN_ABI


class DomainManager:
    @staticmethod
    async def register_domain(client_ink: Client, domain_name: str, account_index: int) -> Optional[bool]:
        try:
            logger.info(f'Account {account_index+1} | {client_ink.wallet_address} | Attempting to register domain name "{domain_name}.ink"...')
            
            expiries = random.randint(1, 10)
            value = int((0.000005 * expiries) * 10 ** 18)
            
            if type(domain_name) != str:
                logger.error(f'Account {account_index+1} | {client_ink.wallet_address} | Domain name should be type(str): {e}.')
                return None
            
            return await client_ink._register_domain(
                domain_name=domain_name,
                expiries=expiries,
                contract_address='0xf180136DdC9e4F8c9b5A9FE59e2b1f07265C5D4D',
                abi_path=DOMAIN_ABI,
                value=value
            )
        
        except Exception as e:
            logger.error(f'Account {account_index+1} | {client_ink.wallet_address} | Error during registering domain: {e}.')
            return None
        