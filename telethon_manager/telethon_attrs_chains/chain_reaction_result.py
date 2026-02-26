def get_reaction_result_attr_chains():
    attrs_chains = {
        # reaction_count (ReactionCount)
        "reaction_count": {
            "ev_reaction_result_reaction": "reaction",  # reaction_count_reaction >>> (Reaction)
            "ev_reaction_result_reaction_count": "count",
            "ev_reaction_result_reaction_chosen_order": "chosen_order",
            "separator": ""},
        # reaction_count_reaction >>> (Reaction)
        "reaction_count_reaction": {
            "ev_reaction_result_reaction_emoticon": "reaction.emoticon",  # (ReactionEmoji)
            "ev_reaction_result_reaction_document_id": "reaction.document_id",  # (ReactionCustomEmoji)
            "separator": ""},
    }
    return attrs_chains
