import random
import asyncio
from typing import Optional

from loguru import logger

from src.client import Client
from src.models import ethereum_sepolia, ink_sepolia
from src.utils import Utils
from src.vars import NAMES_PATH, SYMBOLS_PATH, DOMAIN_NAMES_PATH
from config import BRIDGE_PARAMS, DELAY_BETWEEN_ACC

from src.register_domain import DomainManager
from src.bridge import BridgeManager
from src.erc_721 import ERC721Manager
from src.erc_20 import ERC20Manager
from src.random_interactions import RandomManager


class Menu:
    def __init__(self):
        self.bridge_manager = BridgeManager()
        self.erc721_manager = ERC721Manager()
        self.erc20_manager = ERC20Manager()
        self.random_manager = RandomManager()
        self.domain_manager = DomainManager()

    @staticmethod
    def open_menu() -> int:
        print('''
█ █▄░█ █▄▀ █▀█ █▄░█ █▀▀ █░█ ▄▀█ █ █▄░█   ▀█▀ █▀▀ █▀ ▀█▀ █▄░█ █▀▀ ▀█▀   █▀ █▀█ █▀▀ ▀█▀
█ █░▀█ █░█ █▄█ █░▀█ █▄▄ █▀█ █▀█ █ █░▀█   ░█░ ██▄ ▄█ ░█░ █░▀█ ██▄ ░█░   ▄█ █▄█ █▀░ ░█░

█▄▄ █▄█   ▄▀█ █ █▀█ █▄░█ █▀█ ▀█▀ ▄▀█ █ █▀█
█▄█ ░█░   █▀█ █ █▄█ █░▀█ █▄█ ░█░ █▀█ █ █▄█\n''')
        
        print('''1. Bridge ETH from Ethereum Sepolia to Ink Sepolia.
2. Deploy an ERC-721 contract in Ink Sepolia + interact with it.
3. Deploy an ERC-20 contract in Ink Sepolia + interact with it.
4. Random interactions.
5. Register .ink testnet domain.
6. Quit.\n''')
        
        choice = int(input('Choose an option (1-6): '))
        return choice
    
    async def handle_choice(self, choice: int, private_keys: list, proxies: list) -> Optional[bool]:
        if choice == 1:
            async def process_account(private_key: str, account_index: int):
                try:
                    proxy = proxies[account_index % len(proxies)] if proxies else None
                    client_eth = Client(private_key, ethereum_sepolia, proxy)
                    client_ink = Client(private_key, ink_sepolia, proxy)
            
                    result = await self.bridge_manager.bridge_eth(client_eth, client_ink, BRIDGE_PARAMS, account_index)
            
                    if isinstance(result, Exception) or result is False:
                        logger.error(f'Account {account_index+1} | {client_eth.wallet_address} | Bridge failed with error: {result}.')
                    elif result is None:
                        logger.warning(f'Account {account_index+1} | {client_eth.wallet_address} | Bridge completed with no result.')
                    else:
                        logger.success(f'Account {account_index+1} | {client_eth.wallet_address} | Bridge completed successfully.')
                    
                    return result
            
                except Exception as e:
                    logger.error(f'Account {account_index+1} | {client_eth.wallet_address} | Error processing account: {e}.')
                    return False

            account_tasks = []
            for i, private_key in enumerate(private_keys):
                account_tasks.append(asyncio.create_task(
                    process_account(private_key, i)
                ))
        
                if i < len(private_keys) - 1:
                    delay = random.randint(DELAY_BETWEEN_ACC[0], DELAY_BETWEEN_ACC[1])
                    logger.info(f'Waiting {delay} seconds before starting next account...')
                    await asyncio.sleep(delay)

            if account_tasks:
                await asyncio.gather(*account_tasks, return_exceptions=True)

        elif choice == 2:
            second_choice = int(input('Enter an integer number of how many contracts you want to deploy: '))

            async def process_account(private_key: str, account_index: int):
                try:
                    proxy = proxies[account_index % len(proxies)] if proxies else None
                    client_ink = Client(private_key, ink_sepolia, proxy)
            
                    account_results = []

                    for contract_index in range(second_choice):
                        name, symbol = await Utils.get_random_name_and_symbol(NAMES_PATH, SYMBOLS_PATH)
                        contract_address = await self.erc721_manager.deploy_erc721(client_ink, name, symbol, account_index, is_first_tx=(contract_index==0))
                       
                        if isinstance(contract_address, Exception) or contract_address is False:
                            logger.error(f'Account {account_index+1} | {client_ink.wallet_address} | ERC-721 contract deployment {contract_index+1} failed with error: {contract_address}.')
                        elif contract_address is None:
                            logger.warning(f'Account {account_index+1} | {client_ink.wallet_address} | ERC-721 contract deployment {contract_index+1} completed with no result.')
                        else:
                            logger.success(f'Account {account_index+1} | {client_ink.wallet_address} | ERC-721 contract deployment {contract_index+1} completed successfully.')
                        
                        if contract_address:
                            account_results.append((contract_index, contract_address))
                            mint_result = await self.erc721_manager.mint_nft(client_ink, contract_address, account_index)
                    
                            if isinstance(mint_result, Exception) or mint_result is False:
                                logger.error(f'Account {account_index+1} | {client_ink.wallet_address} | Mint NFT with contract {contract_index+1} failed with error: {mint_result}.')
                            elif mint_result is None:
                                logger.warning(f'Account {account_index+1} | {client_ink.wallet_address} | Mint NFT with contract {contract_index+1} completed with no result.')
                            else:
                                logger.success(f'Account {account_index+1} | {client_ink.wallet_address} | Mint NFT with contract {contract_index+1} completed successfully.')
            
                    return account_results
            
                except Exception as e:
                    logger.error(f'Account {account_index+1} | {client_ink.wallet_address} | Error processing account: {e}.')
                    return []

            account_tasks = []
            for i, private_key in enumerate(private_keys):
                account_tasks.append(asyncio.create_task(
                    process_account(private_key, i))
                )
        
                if i < len(private_keys) - 1:
                    delay = random.randint(DELAY_BETWEEN_ACC[0], DELAY_BETWEEN_ACC[1])
                    logger.info(f'Waiting {delay} seconds before starting next account...')
                    await asyncio.sleep(delay)

            if account_tasks:
                await asyncio.gather(*account_tasks, return_exceptions=True)

        elif choice == 3:
            second_choice = int(input('Enter an integer number of how many contracts you want to deploy: '))

            async def process_account(private_key: str, account_index: int):
                try:
                    proxy = proxies[account_index % len(proxies)] if proxies else None
                    client_ink = Client(private_key, ink_sepolia, proxy)
            
                    account_results = []
            
                    for contract_index in range(second_choice):
                        name, symbol = await Utils.get_random_name_and_symbol(NAMES_PATH, SYMBOLS_PATH)
                        contract_address = await self.erc20_manager.deploy_erc20(client_ink, name, symbol, account_index, is_first_tx=(contract_index==0))
                
                        if isinstance(contract_address, Exception) or contract_address is False:
                            logger.error(f'Account {account_index+1} | {client_ink.wallet_address} | ERC-20 contract deployment {contract_index+1} failed with error: {contract_address}.')
                        elif contract_address is None:
                            logger.warning(f'Account {account_index+1} | {client_ink.wallet_address} | ERC-20 contract deployment {contract_index+1} completed with no result.')
                        else:
                            logger.success(f'Account {account_index+1} | {client_ink.wallet_address} | ERC-20 contract deployment {contract_index+1} completed successfully.')
                
                        if contract_address:
                            account_results.append((contract_index, contract_address))
                            interact_result = await self.erc20_manager.interact_with_contract(client_ink, contract_address, account_index)
                    
                            if isinstance(interact_result, Exception) or interact_result is False:
                                logger.error(f'Account {account_index+1} | {client_ink.wallet_address} | Interact with contract {contract_index+1} failed with error: {interact_result}.')
                            elif interact_result is None:
                                logger.warning(f'Account {account_index+1} | {client_ink.wallet_address} | Interact with contract {contract_index+1} completed with no result.')
                            else:
                                logger.success(f'Account {account_index+1} | {client_ink.wallet_address} | Interact with contract {contract_index+1} completed successfully.')
            
                    return account_results
            
                except Exception as e:
                    logger.error(f'Error processing account {account_index+1}: {e}.')
                    return []

            account_tasks = []
            for i, private_key in enumerate(private_keys):
                account_tasks.append(asyncio.create_task(
                    process_account(private_key, i)
                ))
        
                if i < len(private_keys) - 1:
                    delay = random.randint(DELAY_BETWEEN_ACC[0], DELAY_BETWEEN_ACC[1])
                    logger.info(f'Waiting {delay} seconds before starting next account...')
                    await asyncio.sleep(delay)

            if account_tasks:
                await asyncio.gather(*account_tasks, return_exceptions=True)
        
        elif choice == 4:
            async def process_account(private_key: str, account_index: int, total_accounts: int):
                try:
                    proxy = proxies[account_index % len(proxies)] if proxies else None
                    client_ink = Client(private_key, ink_sepolia, proxy)
            
                    result = await self.random_manager.random_interactions(client_ink, account_index, total_accounts)
            
                    if isinstance(result, Exception) or result is False:
                        logger.error(f'Account {account_index+1} | {client_ink.wallet_address} | Random interactions failed with error: {result}.')
                    elif result is None:
                        logger.warning(f'Account {account_index+1} | {client_ink.wallet_address} | Random interactions completed with no result.')
                    else:
                        logger.success(f'Account {account_index+1} | {client_ink.wallet_address} | Random interactions completed successfully.')
            
                    return result
            
                except Exception as e:
                    logger.error(f'Account {account_index+1} | {client_ink.wallet_address} | Error processing account: {e}.')
                    return False

            account_tasks = []
            for i, private_key in enumerate(private_keys):
                account_tasks.append(asyncio.create_task(
                    process_account(private_key, i, len(private_keys))
                ))
        
                if i < len(private_keys) - 1:
                    delay = random.randint(DELAY_BETWEEN_ACC[0], DELAY_BETWEEN_ACC[1])
                    logger.info(f'Waiting {delay} seconds before starting next account...')
                    await asyncio.sleep(delay)

            if account_tasks:
                await asyncio.gather(*account_tasks, return_exceptions=True)

        elif choice == 5:
            async def process_account(private_key: str, account_index: int, total_accounts: int):
                try:
                    proxy = proxies[account_index % len(proxies)] if proxies else None
                    client_ink = Client(private_key, ink_sepolia, proxy)
            
                    domain_name = await Utils.get_domain_name(DOMAIN_NAMES_PATH, account_index, total_accounts)
                    if not domain_name:
                        return False
                    
                    result = await self.domain_manager.register_domain(client_ink, domain_name, account_index)
            
                    if isinstance(result, Exception) or result is False:
                        logger.error(f'Account {account_index+1} | {client_ink.wallet_address} | Domain registration failed with error: {result}.')
                    elif result is None:
                        logger.warning(f'Account {account_index+1} | {client_ink.wallet_address} | Domain registration completed with no result.')
                    else:
                        logger.success(f'Account {account_index+1} | {client_ink.wallet_address} | Domain registration completed successfully.')
            
                    return result
            
                except Exception as e:
                    logger.error(f'Account {account_index+1} | {client_ink.wallet_address} | Error processing account: {e}.')
                    return False

            account_tasks = []
            for i, private_key in enumerate(private_keys):
                account_tasks.append(asyncio.create_task(
                    process_account(private_key, i, len(private_keys))
                ))
        
                if i < len(private_keys) - 1:
                    delay = random.randint(DELAY_BETWEEN_ACC[0], DELAY_BETWEEN_ACC[1])
                    logger.info(f'Waiting {delay} seconds before starting next account...')
                    await asyncio.sleep(delay)

            if account_tasks:
                await asyncio.gather(*account_tasks, return_exceptions=True)

        elif choice == 6:
            logger.info('Exiting...')
            return None
        
        else:
            logger.error('Please enter a number from 1 to 6.')

        logger.info('Finished.')
