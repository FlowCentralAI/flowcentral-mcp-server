import atlantis
import logging
import os

logger = logging.getLogger("mcp_server")

@public
@game
async def game():
    """
    Main game function - initializes FlowCentral session
    """

    await atlantis.client_command("/silent on")

    # get user id
    user_id = atlantis.get_caller()
    logger.info(f"Game started for user: {user_id}")

    owner_id = atlantis.get_owner()
    await atlantis.client_log(f"Owner ID: {owner_id}")

    await atlantis.client_command("/chat set " + owner_id + "*atlas")

    # set background
    await atlantis.client_command("/silent off")
    image_path = os.path.join(os.path.dirname(__file__), "builder.jpg")

    await atlantis.set_background(image_path)

    # send Atlas face image
    atlas_path = os.path.join(os.path.dirname(__file__), "atlas_face.jpg")
    await atlantis.client_image(atlas_path)

    await atlantis.client_log(f"Welcome to FlowCentral, {user_id}! Atlas is ready to assist you.")
