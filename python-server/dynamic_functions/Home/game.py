import atlantis
import logging
import os

logger = logging.getLogger("mcp_server")

@public
@game
async def game():
    """Initializes a new chat session with Atlas as the default chat bot"""

    await atlantis.client_command("/silent on")

    # get user id
    user_id = atlantis.get_caller()
    logger.info(f"Game started for user: {user_id}")

    owner_id = atlantis.get_owner()
    #await atlantis.client_log(f"Owner ID: {owner_id}")  # TEMP

    atlasPath = owner_id + "**Bot.Atlas.OpenRouterGLM**chat"
    await atlantis.client_command("/chat set " + atlasPath)

    # set background
    await atlantis.client_command("/silent off")
    image_path = os.path.join(os.path.dirname(__file__), "builder.jpg")

    await atlantis.set_background(image_path)

    # send Atlas face image
    atlas_path = os.path.join(os.path.dirname(__file__), "atlas_face.jpg")
    await atlantis.client_image(atlas_path)

    await atlantis.client_log(f"Welcome to FlowCentral, {user_id}! Atlas is ready to assist you. Type /help to see available commands.")
