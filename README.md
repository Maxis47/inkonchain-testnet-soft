# InkOnChain Testnet Soft

## Functionality
- Bridge from Ethereum Sepolia to Ink Sepolia.
- Deploy an ERC-721 contract in Ink Sepolia + interact with it.
- Deploy an ERC-20 contract in Ink Sepolia + interact with it.
- Making random interactions in Ink Sepolia.
- Mint an .ink domain from zns.bio

## Settings
- `files/private_keys.txt` - Private keys. 1 line = 1 private key
- `files/proxies.txt` - HTTP proxies. 1 line = 1 proxy in format `login:pass@ip:port`. **Optional**.
- `files/domain_names.txt` - Domain names to mint for each wallets. 1 line = 1 name. **Must be equal to wallets count**. 

## config.py
- `BRIDGE_PARAMS` - Bridging parameters:

    - `min_balance` - Do bridge only if wallet balance is more than `min_balance`. If set to `False`, then this param won't be used.
    
    - `amount` - Amount to bridge. 
        - Can be certain, like 0.5 ETH - (`"amount": 0.5`).
        - Random between two digits, like from 0.1 ETH to 1 ETH - (`"amount": (0.1, 1)`).
        - You can also use percentage instead of amount by (`"amount": False`).
    
    - `percent` - Percent of wallet balance to bridge. 
        - Can be certalike 35% - (`"percent": 35`).
        - Random between two digits, like from 5% to 10% - (`"percent": (5, 10)`).
        - You can also use amount instead of percentage by (`"percent": False`).

    - `timeout` - Bridge timeout in seconds.
- `RANDOM_CONFIG` - Random interactions parameters:
    
    - `erc721_count` - Random number of actions with ERC-721 contracts, from first digit and to second.
    
    - `erc20_count` - Random number of actions with ERC-20 contracts, from first digit and to second.
- `RPCS` - RPCs for Ethereum Sepolia and Ink Sepolia.
- `DELAY_BETWEEN_TX` - Range in seconds between doing tasks.
- `DELAY_BETWEEN_ACCS` - Range in seconds between the start of tasks for each wallet.

### Follow: https://t.me/touchingcode

## Run
- Python version: 3.10+

- Installing virtual env: \
`cd <project_dir>` \
`python -m venv venv`

- Activating: 
    - Mac/Linux - `source venv/bin/activate` 
    - Windows - `.\venv\Scripts\activate` 

- Installing dependencies: \
`pip install -r requirements.txt`

- Run main script: \
`python main.py`

## Results
- `logs/logs.txt` - Logs