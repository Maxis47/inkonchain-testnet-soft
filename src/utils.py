import asyncio
import random
from typing import Optional, Union

import aiofiles
import ujson
from loguru import logger

from config import DELAY_BETWEEN_TX


class Utils:
    @staticmethod
    async def read_json(path: str, encoding: Optional[str] = None) -> Union[list, dict]:
        async with aiofiles.open(path, 'r', encoding=encoding) as f:
            contents = await f.read()
            return ujson.loads(contents)

    @staticmethod
    async def read_file(path: str, encoding: Optional[str] = None) -> str:
        async with aiofiles.open(path, 'r', encoding=encoding) as f:
            return await f.read()
    
    @staticmethod
    async def read_strings_from_file(path: str) -> list:
        strings = []
        async with aiofiles.open(path, 'r') as f:
            async for line in f:
                line = line.strip()
                if line:
                    strings.append(line)
        return strings

    @staticmethod
    async def get_random_name_and_symbol(file1_path: str, file2_path: str) -> tuple:
        async with aiofiles.open(file1_path, 'r') as f1, aiofiles.open(file2_path, 'r') as f2:
            names = await f1.readlines()
            symbols = await f2.readlines()
        
        paired_list = list(zip(names, symbols))
        name, symbol = random.choice(paired_list)
    
        return name.strip(), symbol.strip()

    @staticmethod
    async def execute_with_delay(transaction, wallet_address: str, account_index: int):
        delay = random.randint(DELAY_BETWEEN_TX[0], DELAY_BETWEEN_TX[1])
        logger.info(f'Account {account_index+1} | {wallet_address} | Waiting {delay} seconds before transaction...')
        
        await asyncio.sleep(delay)
        
        logger.info(f'Account {account_index+1} | {wallet_address} | Delay completed. Starting next transaction...')
        return await transaction
    
    @staticmethod
    def round_to_significant_digits(num: Union[int, float], digits: int) -> str:
        if num == 0:
            return 0.0
        num_str = f"{num:.10f}"
        first_non_zero_index = None
        for i, char in enumerate(num_str):
            if char not in ('0', '.'):
                first_non_zero_index = i
                break
    
        if first_non_zero_index is None:
            return 0.0

        decimal_position = num_str.find('.')
        significant_position = first_non_zero_index - decimal_position - 1

        rounded_num = round(num, digits + significant_position)

        rounded_str = f"{rounded_num:.{digits + significant_position}f}"

        if '.' in rounded_str:
            rounded_str = rounded_str.rstrip('0').rstrip('.')
    
        return rounded_str
    
    @staticmethod
    async def get_domain_name(domain_names_path: str, wallet_index: int, total_wallets: int) -> str:
        try:
            with open(domain_names_path, 'r') as file:
                domain_names = [line.strip() for line in file if line.strip()]
            if len(domain_names) != total_wallets:
                logger.error(f"Number of domain names ({len(domain_names)}) doesn't match the number of wallets ({total_wallets}).")
                return False
            
            return domain_names[wallet_index]
    
        except Exception as e:
            logger.error(f'Error during reading domain names: {e}.')
            return False
        