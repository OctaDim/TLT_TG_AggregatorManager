from configs.settings import AGGREGATOR_API_SEVER_PORT

# ######################################################################
# ############# AGGREGATOR API end-points to send webhooks #############
# ######################################################################
AGGREGATOR_API_WEBHOOKS_URL = (
    f"http://{AGGREGATOR_API_SEVER_PORT}/global_msg_aggregator/global_api_webhooks/")
