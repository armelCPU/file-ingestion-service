import numpy as np

def mock_embedding(text: str) -> list:
    """
    Generates a simulated embedding vector for the given text.
    The size corresponds to that of the text-embedding-ada-002 (1536 dimensions).

    Args:
    - text (str): The input text to generate the mock embedding for.

    Returns:
    - list: A list representing the simulated embedding vector.
    """
    # Use a consistent hash function to generate the seed for reproducibility.
    np.random.seed(abs(hash(text)) % (2**32))
    return np.random.rand(1536).tolist()
