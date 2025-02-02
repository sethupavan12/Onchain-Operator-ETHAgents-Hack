from pydantic import BaseModel, Field
from cdp import Wallet

DEPLOY_MULTITOKEN_PROMPT = """
This tool deploys a new multi-token contract with a specified base URI for token metadata.
The base URI should be a template URL containing {id} which will be replaced with the token ID.
For example: 'https://example.com/metadata/{id}.json'
"""

class DeployMultiTokenInput(BaseModel):
    """Input argument schema for deploy multi-token contract action."""
    base_uri: str = Field(
        ...,
        description=
        "The base URI template for token metadata. Must contain {id} placeholder.",
        example="https://example.com/metadata/{id}.json")

def deploy_multi_token(wallet: Wallet, base_uri: str) -> str:
    """Deploy a new multi-token contract with the specified base URI.

    Args:
        wallet (Wallet): The wallet to deploy the contract from.
        base_uri (str): The base URI template for token metadata. Must contain {id} placeholder.

    Returns:
        str: A message confirming deployment with the contract address.
    """
    # Validate that the base_uri contains the {id} placeholder
    if "{id}" not in base_uri:
        raise ValueError("base_uri must contain {id} placeholder")

    # Deploy the contract
    deployed_contract = wallet.deploy_multi_token(base_uri)
    result = deployed_contract.wait()

    return f"Successfully deployed multi-token contract at address: {result.contract_address}"