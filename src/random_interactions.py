import random
from typing import Optional

from loguru import logger

from src.client import Client
from src.erc_20 import ERC20Manager
from src.erc_721 import ERC721Manager
from src.register_domain import DomainManager
from src.utils import Utils
from src.vars import NAMES_PATH, SYMBOLS_PATH, DOMAIN_NAMES_PATH
from config import RANDOM_CONFIG


class RandomManager:
    def __init__(self) -> None:
        self.erc20_manager = ERC20Manager()
        self.erc721_manager = ERC721Manager()
        self.domain_manager = DomainManager()
        
    @staticmethod
    async def random_interactions(client_ink: Client, account_index: int, total_accounts: int) -> Optional[bool]:
        try:
            erc721_manager = ERC721Manager()
            erc20_manager = ERC20Manager()
            domain_manager = DomainManager()

            erc721_count = random.randint(RANDOM_CONFIG['max_actions']['erc721_count'][0], RANDOM_CONFIG['max_actions']['erc721_count'][1])
            erc20_count = random.randint(RANDOM_CONFIG['max_actions']['erc20_count'][0], RANDOM_CONFIG['max_actions']['erc20_count'][1])
            domain_count = 1

            logger.info(f'Account {account_index+1} | {client_ink.wallet_address} | Planning to deploy {erc721_count} ERC-721 contracts...')
            logger.info(f'Account {account_index+1} | {client_ink.wallet_address} | Planning to deploy {erc20_count} ERC-20 contracts...')
            logger.info(f'Account {account_index+1} | {client_ink.wallet_address} | Planning to register {domain_count} domains...')
        
            for i in range(erc721_count):
                name, symbol = await Utils.get_random_name_and_symbol(NAMES_PATH, SYMBOLS_PATH)
                logger.info(f'Account {account_index+1} | {client_ink.wallet_address} | Deploying ERC-721 contract {i+1}/{erc721_count}...')
            
                contract_address = await erc721_manager.deploy_erc721(client_ink, name, symbol, account_index, is_first_tx=(i==0 and erc721_count > 0))
            
                if isinstance(contract_address, Exception):
                    logger.error(f'Account {account_index+1} | {client_ink.wallet_address} | ERC-721 Deploy {i+1} failed with error: {contract_address}.')
                elif contract_address:
                    logger.success(f'Account {account_index+1} | {client_ink.wallet_address} | ERC-721 Deploy {i+1} completed successfully.')

                    logger.info(f'Account {account_index+1} | {client_ink.wallet_address} | Starting mint for ERC-721 contract {i+1}.')
                    mint_result = await erc721_manager.mint_nft(client_ink, contract_address, account_index)
                
                    if isinstance(mint_result, Exception):
                        logger.error(f'Account {account_index+1} | {client_ink.wallet_address} | ERC-721 Mint {i+1} failed with error: {mint_result}.')
                    else:
                        logger.success(f'Account {account_index+1} | {client_ink.wallet_address} | ERC-721 Mint {i+1} completed successfully.')
        
            for i in range(erc20_count):
                name, symbol = await Utils.get_random_name_and_symbol(NAMES_PATH, SYMBOLS_PATH)
                logger.info(f'Account {account_index+1} | {client_ink.wallet_address} | Deploying ERC-20 contract {i+1}/{erc20_count}...')
            
                contract_address = await erc20_manager.deploy_erc20(client_ink, name, symbol, account_index, is_first_tx=(i==0 and erc721_count == 0))
            
                if isinstance(contract_address, Exception):
                    logger.error(f'Account {account_index+1} | {client_ink.wallet_address} | ERC-20 Deploy {i+1} failed with error: {contract_address}.')
                elif contract_address:
                    logger.success(f'Account {account_index+1} | {client_ink.wallet_address} | ERC-20 Deploy {i+1} completed successfully.')

                    logger.info(f'Account {account_index+1} | {client_ink.wallet_address} | Starting interaction with ERC-20 contract {i+1}...')
                    interact_result = await erc20_manager.interact_with_contract(client_ink, contract_address, account_index)
                
                    if isinstance(interact_result, Exception):
                        logger.error(f'Account {account_index+1} | {client_ink.wallet_address} | ERC-20 Interaction {i+1} failed with error: {interact_result}.')
                    else:
                        logger.success(f'Account {account_index+1} | {client_ink.wallet_address} | ERC-20 Interaction {i+1} completed successfully.')

            for i in range(domain_count):
                domain_name = await Utils.get_domain_name(DOMAIN_NAMES_PATH, account_index, total_accounts)
                logger.info(f'Account {account_index+1} | {client_ink.wallet_address} | Registering domain {i+1}/{domain_count}: {domain_name}...')
            
                result = await domain_manager.register_domain(client_ink, domain_name, account_index)
            
                if isinstance(result, Exception):
                    logger.error(f'Account {account_index+1} | {client_ink.wallet_address} | Domain Registration {i+1} failed with error: {result}.')
                else:
                    logger.success(f'Account {account_index+1} | {client_ink.wallet_address} | Domain Registration {i+1} completed successfully.')

            return True

        except Exception as e:
            logger.error(f'Account {account_index+1} | Error during random interactions: {e}')
            return None
        