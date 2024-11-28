import random
import asyncio
from typing import Optional, Union

from loguru import logger

from src.client import Client
from src.models import ethereum_sepolia, ink_sepolia
from src.utils import Utils
from src.vars import ERC721_ABI, ERC721_BYTECODE, ERC20_ABI, ERC20_BYTECODE, NAMES_PATH, SYMBOLS_PATH
from config import bridge_amount, delay


class Manager:
    @staticmethod
    async def bridge_eth(client_eth: Client, bridge_amount: Union[int, float] = None) -> Optional[bool]:
        if bridge_amount == None:
            eth_balance = await client_eth.w3.eth.get_balance(client_eth.wallet_address)
            max_bridge_amount = (eth_balance / 10 ** 18) * (random.randint(1, 50) / 100)
            formatted_amount = float(f"{max_bridge_amount:.5f}")
            bridge_amount = int(formatted_amount * 10 ** 18)
        else:
            bridge_amount = int(bridge_amount * 10 ** 18)

        try:
            logger.info(f'{client_eth.wallet_address} | Attempting to bridge {format(bridge_amount / 10 ** 18, ".18f").rstrip("0").rstrip(".")} ETH...')
            
            return await client_eth.bridge_eth(
                contract_address='0x33f60714BbD74d62b66D79213C348614DE51901C',
                value=bridge_amount,
            )
        
        except Exception as e:
            logger.error(f'{client_eth.wallet_address} | Error bridging ETH: {e}')
            return None
    
    @staticmethod
    async def deploy_erc721(client_ink: Client, name: str, symbol: str) -> Optional[bool]:
        try:
            logger.info(f'{client_ink.wallet_address} | Attempting to deploy ERC-721 contract in {client_ink.network.name}')
            
            return await client_ink.deploy_contract(
                name=name,
                symbol=symbol,
                abi_path=ERC721_ABI,
                bytecode_path=ERC721_BYTECODE
            )
        
        except Exception as e:
            logger.error(f'{client_ink.wallet_address} | Error deploying contract: {e}')
            return None
    
    @staticmethod
    async def mint_nft(client_ink: Client, contract_address: str) -> Optional[bool]:
        try:
            logger.info(f'{client_ink.wallet_address} | Attempting to mint NFT with contract {contract_address}')
        
            return await client_ink.mint_nft(
                contract_address=contract_address, 
                abi_path=ERC721_ABI
            )
        
        except Exception as e:
            logger.error(f'{client_ink.wallet_address} | Error interacting contract: {e}')
            return None
    
    @staticmethod
    async def deploy_erc20(client_ink: Client, name: str, symbol: str) -> Optional[bool]:
        try:
            logger.info(f'{client_ink.wallet_address} | Attempting to deploy ERC-20 contract in {client_ink.network.name}')
            
            return await client_ink.deploy_contract(
                name=name,
                symbol=symbol,
                abi_path=ERC20_ABI,
                bytecode_path=ERC20_BYTECODE
            )
        
        except Exception as e:
            logger.error(f'{client_ink.wallet_address} | Error deploying contract: {e}')
            return None
    
    @staticmethod
    async def interact_with_contract(client_ink: Client, contract_address: str) -> Optional[bool]:
        try:
            logger.info(f'{client_ink.wallet_address} | Attempting to interact with ERC-20 contract {contract_address}')
        
            return await client_ink.random_interact_with_contract(
                contract_address=contract_address,
                abi_path=ERC20_ABI
            )
        
        except Exception as e:
            logger.error(f'{client_ink.wallet_address} | Error interacting contract: {e}')
            return None
    
    @staticmethod
    async def random_interactions(client_ink: Client) -> Optional[bool]:
        deploy_erc721_calls = random.randint(0, 3)
        deploy_erc20_calls = random.randint(0, 3)

        tasks = []

        try:
            for _ in range(deploy_erc721_calls):
                name, symbol = await Utils.get_random_name_and_symbol(NAMES_PATH, SYMBOLS_PATH)
                deploy_task = asyncio.create_task(Manager.deploy_erc721(client_ink, name, symbol))
            
                tasks.append(deploy_task)
            
                tasks.append(asyncio.create_task(Manager.mint_nft(client_ink, await deploy_task)))

            for _ in range(deploy_erc20_calls):
                name, symbol = await Utils.get_random_name_and_symbol(NAMES_PATH, SYMBOLS_PATH)
                deploy_task = asyncio.create_task(Manager.deploy_erc20(client_ink, name, symbol))
            
                tasks.append(deploy_task)
            
                tasks.append(asyncio.create_task(Manager.interact_with_contract(client_ink, await deploy_task)))

            random.shuffle(tasks)

            await asyncio.gather(*tasks)
        
        except Exception as e:
            logger.error(f'{client_ink.wallet_address} | Error doing random interactions: {e}')
            return None
        
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
4. Random interaction
5. Quit\n''')
        
        choice = int(input('Choose an option (1-5): '))
        return choice
    
    @staticmethod
    async def handle_choice(choice: int, private_keys: list, proxies: list) -> Optional[bool]:
        tasks = []

        if choice == 1:
            print('''\n1. Bridge a certain amount (change in config.py).
2. Bridge a random amount.\n''')
            
            second_choice = int(input('Choose an option (1-2): '))
            
            if second_choice == 1:
                logger.info('Starting to bridge certain amount ETH...')
                    
                for private_key in private_keys:
                    if proxies:
                        proxy_index = private_keys.index(private_key) % len(proxies)
                        proxy = proxies[proxy_index]
                    else:
                        proxy = None
                    
                    client_eth = Client(private_key, ethereum_sepolia, proxy)

                    tasks.append(asyncio.create_task(Manager.bridge_eth(client_eth, bridge_amount)))

                    await asyncio.sleep(random.randint(delay[0], delay[1]))
            
            elif second_choice == 2:
                logger.info('Starting to bridge random amount ETH...')
                
                for private_key in private_keys:
                    if proxies:
                        proxy_index = private_keys.index(private_key) % len(proxies)
                        proxy = proxies[proxy_index]
                    else:
                        proxy = None
                    
                    client_eth = Client(private_key, ethereum_sepolia, proxy)
                    
                    tasks.append(asyncio.create_task(Manager.bridge_eth(client_eth)))
                    
                    await asyncio.sleep(random.randint(delay[0], delay[1]))
        
        elif choice == 2:
            second_choice = int(input('Enter an integer number of how many contracts you want to deploy: '))

            logger.info(f'Starting to deploy {second_choice} ERC-721 contracts...')
            
            deploy_tasks = []
            
            for _ in range(second_choice):
                for i, private_key in enumerate(private_keys):
                    if proxies:
                        proxy_index = i % len(proxies)
                        proxy = proxies[proxy_index]
                    else:
                        proxy = None
                    
                    client_ink = Client(private_keys[i % len(private_keys)], ink_sepolia, proxy)
                    
                    name, symbol = await Utils.get_random_name_and_symbol(NAMES_PATH, SYMBOLS_PATH)

                    deploy_tasks.append(asyncio.create_task(Manager.deploy_erc721(client_ink, name, symbol)))
                    
                    await asyncio.sleep(random.randint(delay[0], delay[1]))     
        
            results = await asyncio.gather(*deploy_tasks)

            for i, deploy_result in enumerate(results):
                if deploy_result is not None:
                    if proxies:
                        proxy_index = i % len(proxies)
                        proxy = proxies[proxy_index]
                    else:
                        proxy = None
                    
                    client_ink = Client(private_keys[i % len(private_keys)], ink_sepolia, proxy)
                    
                    tasks.append(asyncio.create_task(Manager.mint_nft(client_ink, deploy_result)))
                    
                    await asyncio.sleep(random.randint(delay[0], delay[1]))
        
        elif choice == 3:
            second_choice = int(input('Enter an integer number of how many contracts you want to deploy: '))

            logger.info(f'Starting to deploy {second_choice} ERC-20 contracts...')
            
            deploy_tasks = []
            
            for _ in range(second_choice):
                for i, private_key in enumerate(private_keys):
                    if proxies:
                        proxy_index = i % len(proxies)
                        proxy = proxies[proxy_index]
                    else:
                        proxy = None
                    
                    client_ink = Client(private_keys[i % len(private_keys)], ink_sepolia, proxy)
                    
                    name, symbol = await Utils.get_random_name_and_symbol(NAMES_PATH, SYMBOLS_PATH)
                    
                    deploy_tasks.append(asyncio.create_task(Manager.deploy_erc20(client_ink, name, symbol)))
                    
                    await asyncio.sleep(random.randint(delay[0], delay[1]))
        
            results = await asyncio.gather(*deploy_tasks)

            for i, deploy_result in enumerate(results):
                if deploy_result is not None:
                    if proxies:
                        proxy_index = i % len(proxies)
                        proxy = proxies[proxy_index]
                    else:
                        proxy = None
                    
                    client_ink = Client(private_keys[i % len(private_keys)], ink_sepolia, proxy)
                    
                    tasks.append(asyncio.create_task(Manager.interact_with_contract(client_ink, deploy_result)))
                    
                    await asyncio.sleep(random.randint(delay[0], delay[1]))
        
        elif choice == 4:
            logger.info('Starting random interactions...')
            
            for private_key in private_keys:
                if proxies:
                    proxy_index = private_keys.index(private_key) % len(proxies)
                    proxy = proxies[proxy_index]
                else:
                    proxy = None
                
                client_ink = Client(private_key, ink_sepolia, proxy)
                
                tasks.append(asyncio.create_task(Manager.random_interactions(client_ink)))
                
                await asyncio.sleep(random.randint(delay[0], delay[1]))
        
        elif choice == 5:
            pass
        
        else:
            logger.error('Print a number from 1 to 6.')
        
        await asyncio.gather(*tasks)

        logger.info('Finished.')
        