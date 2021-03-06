# -*- coding: utf-8 -*-
import logging
import requests

from acrobot.models import Acronym, find_acronyms
from acrobot.events import build_acronym_response

logger = logging.getLogger(__name__)


def respond_to_search_command(slack_event, app, slack_client):
    # Sends an ephemeral message back to the user
    with app.app_context():
        search_key = slack_event['text']
        found_acronyms = find_acronyms(search_key)
        message_text = build_acronym_response(found_acronyms)
        message = {
            "response_type": "ephemeral",
            "text": message_text
        }
        requests.post(slack_event['response_url'], json=message)
        report_usage(search_key, slack_client)


def report_usage(search_key, slack_client):
    # Implemented this so that 'admins' can know when slash commands are being used.
    # More could be done here, but this level of logging seemed sufficient.
    usage_report_recipients = {
        "James Fefes": "UKA5X94AZ",
    }
    for _, slack_user_id in usage_report_recipients.items():
        slack_client.chat_postMessage(channel=slack_user_id, text=f"someone just used Acrobot to search {search_key}")


def respond_to_add_command(slack_event, app, slack_client):
    with app.app_context():
        channel = "acrobot-support"
        message = "This is a mock response!"
        # Sloppy way to break out the two args passed in to slack. Sorry
        # Example: slack_event["text"] == '"gpc" "green button connect"'
        # Want to split on '" "', and replace the remaining quotes
        try:
            slack_message = slack_event["text"].replace('“', '"').replace('“','"').replace('”','"').replace(u'\u201c', '"').replace(u'\u201d', '"') # noqa
            acronym, definition = slack_message.replace('" "', '|||').strip('"').split("|||")
        # TODO: This should probably only need accept string formatting exceptions, but I was lazy. Still sorry.
        except:  # noqa: E722
            logger.warn(f"Failed to parse message: {slack_event['text']}")
            message = {
                # ephemeral messages are only seen by the user who sent the slash command
                # https://api.slack.com/methods/chat.postEphemeral
                "response_type": "ephemeral",
                "text": "It looks like your message was malformatted. :sadparrot:"
                        "\nUsage is `/acrobot-add \"acronym\" \"definition\"`. "
                        "\n Example: `/acrobot-add \"saas\" \"Software as a Service\"` :acrobot:"
            }
            requests.post(slack_event['response_url'], json=message)
        else:
            message = {
                "response_type": "ephemeral",
                "text": "Okay, i'll add it! :acrobot:"
            }
            Acronym.create(acronym, definition, created_by=slack_event["user_name"])
            mentioned_user = slack_event["user_id"]
            message = f"I have learned `{acronym}` means `{definition}`. Thank you <@{mentioned_user}>!"
            slack_client.chat_postMessage(channel=channel, text=message)
