MERCHANT_CATEGORIES = {
    "uber": "Transport",
    "bolt": "Transport",
    "little cab": "Transport",
    "shell": "Fuel",
    "total": "Fuel",
    "rubis": "Fuel",

    "naivas": "Groceries",
    "carrefour": "Groceries",
    "quickmart": "Groceries",
    "chandarana": "Groceries",

    "java": "Food",
    "kfc": "Food",
    "pizza": "Food",
    "subway": "Food",
    "glovo": "Food",
    "jambojet": "Travel",

    "netflix": "Entertainment",
    "spotify": "Entertainment",
    "showmax": "Entertainment",

    "hospital": "Healthcare",
    "pharmacy": "Healthcare",
    "chemist": "Healthcare",

    "safaricom": "Utilities",
    "airtel": "Utilities",
    "kenya power": "Utilities",

    "school": "Education",
    "university": "Education",
}


CATEGORIES = [
    "Food",
    "Transport",
    "Groceries",
    "Entertainment",
    "Healthcare",
    "Utilities",
    "Education",
    "Fuel",
    "Shopping",
    "Bills",
    "Travel",
    "Other",
    "Unknown",
]


def categorize_transaction(description):
    description = str(description).lower()

    for merchant, category in MERCHANT_CATEGORIES.items():
        if merchant in description:
            return category

    return "Unknown"