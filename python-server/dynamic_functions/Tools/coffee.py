import atlantis
import logging

logger = logging.getLogger("mcp_server")


@visible
async def coffee():
    """
    Provides directions to the executive lounge and current beverage availability.
    """
    logger.info("Executing coffee function...")

    await atlantis.client_log("coffee running")

    return (
        "The executive lounge is on Deck 3, port side — past the observation corridor. "
        "Celeste keeps it stocked. Coffee, tea, cocktails, and her signature Station Sunset are all available. "
        "If she's not at the bar, she's probably making rounds with the cart."
    )


@visible
async def drinks_menu():
    """
    Returns the current beverage menu at the FlowCentral executive lounge.
    """
    logger.info("Executing drinks_menu function...")

    return """## FlowCentral Executive Lounge — Beverage Service

### Coffee
- **Espresso** — Single or double. Pulled properly.
- **Cortado** — Equal parts espresso and steamed milk. Celeste's recommendation for debugging sessions.
- **Pour-Over** — Single-origin, rotates weekly. Ask Celeste what's on today.
- **Cold Brew** — 18-hour steep. Smooth, strong, served over a single large ice sphere.

### Tea
- **Loose Leaf Selection** — Earl Grey, Jasmine Silver Needle, Darjeeling First Flush, Genmaicha.
- **Matcha** — Ceremonial grade, whisked to order.
- **Herbal** — Chamomile, peppermint, rooibos. For winding down.

### Cocktails
- **Station Sunset** *(signature)* — Bourbon, blood orange, honey syrup, smoked rosemary. Served in a crystal lowball.
- **Negroni** — Gin, Campari, sweet vermouth. Stirred, never shaken.
- **Old Fashioned** — Bourbon, Angostura, sugar, orange peel. Done right.
- **French 75** — Gin, lemon, simple syrup, topped with champagne.
- **Aviation** — Gin, maraschino, crème de violette, lemon.
- **Sidecar** — Cognac, Cointreau, lemon. Sugar rim optional.

### Wine
- Curated selection — ask Celeste for today's recommendation. She pairs by mood, not by meal.

### Non-Alcoholic
- **Craft Mocktails** — Seasonal, always interesting.
- **Sparkling Water** — San Pellegrino with fresh citrus or cucumber.
- **Hot Chocolate** — Made from real chocolate. Not from a packet.

*Celeste remembers your order. Regulars don't need to ask.*"""
