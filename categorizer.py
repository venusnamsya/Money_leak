# Known merchants and their categories

MERCHANT_CATEGORIES = {
    "uber": "Transport",
    "bolt": "Transport",
    "shell": "Fuel",
    "total": "Fuel",

    "naivas": "Groceries",
    "carrefour": "Groceries",
    "quickmart": "Groceries",

    "java": "Food",
    "kfc": "Food",
    "pizza": "Food",

    "netflix": "Entertainment",
    "spotify": "Entertainment",

    "hospital": "Healthcare",
    "pharmacy": "Healthcare",
}


def categorize_transaction(description):
    """
    Try to identify the category of a transaction
    based on its description.
    """

    description = description.lower()

    for merchant, category in MERCHANT_CATEGORIES.items():

        if merchant in description:
            return category

    return "Unknown"