BRIDGE_PARAMS = {
    "min_balance": False, 
    "amount": False, 
    "percent": (5, 10),
    "timeout": 120 
}

RANDOM_CONFIG = {
    'max_actions': {
        'erc721_count': (1, 3),
        'erc20_count': (1, 3),
    }
}

RPCS = {
    "ethereum_sepolia": 'https://ethereum-sepolia-rpc.publicnode.com',
    "ink_sepolia": 'https://rpc-gel-sepolia.inkonchain.com'
}

DELAY_BETWEEN_TX = (5, 12)
DELAY_BETWEEN_ACC = (10, 20)