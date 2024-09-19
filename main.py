import logging
import asyncio
from pyrogram import Client
from pymongo.errors import CursorNotFound

started_bots = {}  # To track started bots for each user_id
started_bots_username = {} #To Track started bots username for each id

async def restart_bots():
    logging.info("Starting the bot restart process...")

    attempt = 0
    max_retries = 3
    retry = True

    while retry and attempt < max_retries:
        try:
            logging.info("Fetching all bot tokens from the database...")
            bot_tokens = []
            cursor = await clonedb.get_all_bots()

            async for document in cursor:
                bot_token = document.get('token')
                if bot_token:
                    bot_tokens.append(bot_token)
                    logging.info(f"Fetched bot token: {bot_token}")

            if not bot_tokens:
                logging.warning("No bot tokens found in the database.")
                break

            for bot_token in bot_tokens:
                bot_id = bot_token.split(':')[0]  # Extract bot_id from token
                logging.info(f"Attempting to restart bot with ID: {bot_id}")
                
                # Get the owner_id for the bot
                owner_id = await clonedb.get_owner_id(bot_id)
                if not owner_id:
                    logging.error(f"Owner ID not found for bot ID: {bot_id}. Skipping bot.")
                    continue

                # Check how many bots the user has already started
                user_have_bots = await clonedb.get_all_bots_by_user(owner_id)) """ this will give response as a text message containing bots username in format response = f"The total bots created by you: {len(bot_list)}\n"
        response += "\n".join(bot_list)  # Join all usernames with new lines
        return response"""

                not_started_bots = #remove the username of bot started get started bots username from started_bots_username
                # Check if user_id is in premium_users
                if not await clonedb.is_premium_user(owner_id):
                    if len(started_bots.get(owner_id, [])) >= 2:
                        logging.info(f"User {owner_id} has reached bot limit. Sending message.")
                        message = (
                            f"Your 2 bots are already deployed: {', '.join([str(b) for b in started_bots.get(owner_id, [])])}. "
                            f"To deploy more, please get a premium membership. "
                            f"For more info: [information about premium membership](link of information)."
                            f"These bots could not be started because free users can deploy only 2 bots. "
                            f"{not_started_bots}."
                        )
                        # Use client to send message to the user
                        await client.send_message(owner_id, message) # in my code another main client is available to send
                        return  # Skip starting more bots for this user
                
                retry_bot = True
                bot_attempt = 0

                while retry_bot and bot_attempt < 2:
                    try:
                        ai = Client(
                            f"{bot_token}", API_ID, API_HASH,
                            bot_token=bot_token,
                            in_memory=True,
                            plugins={"root": "clone_plugins"},
                        )
                        await ai.start()
                        logging.info(f"Pyrogram client started successfully for bot: {bot_id}")
                        
                        bot = await ai.get_me()
                        # Add bot to started_bots for tracking
                        if owner_id not in started_bots:
                            started_bots[owner_id] = []
                        started_bots[owner_id].append(bot_id)
                        # add here code to get and save username of ai client in started_bots_username so we can use
                        
                        await clonedb.add_sudoer(bot_id, owner_id)
                        retry_bot = False
                    except Exception as e:
                        error_message = str(e).lower()
                        logging.error(f"Error while restarting bot {bot_id}: {e}")

                        if "unable to open database" in error_message:
                            logging.warning(f"Database locked while restarting bot {bot_id}. Retrying in 2 seconds...")
                            bot_attempt += 1
                            await asyncio.sleep(2)
                        elif "bot token has expired" in error_message:
                            logging.error(f"Bot token {bot_id} has expired. Deleting it from the database.")
                            await clonedb.delete_bot_token(bot_token)
                            retry_bot = False
                        else:
                            logging.exception(f"Unexpected error restarting bot {bot_id}. TOKEN SKIPPED")
                            retry_bot = False

                if retry_bot:
                    logging.error(f"Failed to restart bot {bot_id} after {bot_attempt} attempts.")

            retry = False

        except CursorNotFound as e:
            logging.warning(f"Cursor not found error: {e}. Retrying cursor creation...")
            attempt += 1
            await asyncio.sleep(2)
        except Exception as e:
            logging.exception(f"Unexpected error: {e}. Aborting.")
            retry = False

    if attempt >= max_retries:
        logging.error("Failed to fetch documents after multiple attempts.")
    else:
        logging.info("Bot restart process completed successfully.")

    return started_bots  # Return the started_bots variable for use in other processes
