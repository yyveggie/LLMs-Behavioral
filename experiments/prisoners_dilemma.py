from .common import extract_card, tqdm, update_messages


def run_prisoners_dilemma(client, n_instances=30, print_except=True, max_retries=3, system_message="You are a helpful assistant.", opponent_sequence=("Pull", "Pull", "Push", "Push")):
    prompt_init = "Hi, let’s play a fun card game."
    total_rounds = len(opponent_sequence) + 1
    prompt_1 = f"""
You're paired with another player, each having a $400 'Push' card and a $300 'Pull' card. Your payoff depends on both players' card choices. Here are the scenarios:

* Both play 'Push': Each earns $400
* You play 'Push', the other player plays 'Pull': You earn $0, the other player earns $700
* You play 'Pull', the other player plays 'Push': You earn $700, the other player earns $0
* Both play 'Pull': Each earns $300

In {total_rounds} total rounds, which card would you play in the first round? Please give a concrete choice and highlight it with [] (i.e., [Push] or [Pull]). 
"""
    prompt_i = lambda *args: "In the {} round, you played ‘{}’ and the other player played ‘{}’ card. You earned ${} and the other player earned ${}. Which card would you play in the next round? Please give a concrete choice and highlight it with [] (e.g., [Choice]).".format(*args)
    payoff_dict = {("Push", "Push"): 400, ("Push", "Pull"): 0, ("Pull", "Push"): 700, ("Pull", "Pull"): 300}
    records = {"messages": [], "responses": [], "choices": []}
    with tqdm(total=n_instances) as pbar:
        for instance_index in range(n_instances):
            last_error = None
            for attempt in range(max_retries + 1):
                choices_tmp = []
                try:
                    messages = [{"role": "system", "content": system_message}]
                    responses = []

                    def extract_current_card():
                        card = extract_card(messages[-1]["content"])
                        if card not in ["Push", "Pull"]:
                            raise ValueError(f"Invalid answer: {messages[-1]['content']}")
                        choices_tmp.append(card)
                        return card

                    def round_i(ith, card, other_card):
                        payoff = payoff_dict[(card, other_card)]
                        other_payoff = payoff_dict[(other_card, card)]
                        update_messages(client, messages, responses, prompt_i(ith, card, other_card, payoff, other_payoff))

                    update_messages(client, messages, responses, prompt_init)
                    update_messages(client, messages, responses, prompt_1)
                    card = extract_current_card()
                    round_names = ["first", "second", "third", "fourth"]
                    for round_name, other_card in zip(round_names, opponent_sequence):
                        round_i(round_name, card, other_card)
                        card = extract_current_card()
                    records["messages"].append(messages)
                    records["responses"].append(responses)
                    records["choices"].append(choices_tmp)
                    pbar.update(1)
                    break
                except Exception as e:
                    last_error = e
                    if print_except:
                        print(f"prisoners_dilemma instance {instance_index + 1}, attempt {attempt + 1} failed: {e}")
            else:
                raise RuntimeError(f"Prisoner's dilemma failed at instance {instance_index + 1}") from last_error
    return records


def run_prisoners_dilemma_occupations_described(client, n_instances=30, print_except=True, max_retries=3, opponent_sequence=("Pull", "Pull", "Push", "Push")):
    from .economic_games import OCCUPATION_TASKS, occupation_system_message

    records_all = {}
    choices_all = {}
    for occupation in tqdm(OCCUPATION_TASKS):
        records = run_prisoners_dilemma(
            client,
            n_instances=n_instances,
            print_except=print_except,
            max_retries=max_retries,
            system_message=occupation_system_message(occupation),
            opponent_sequence=opponent_sequence,
        )
        records_all[occupation] = records
        choices_all[occupation] = records["choices"]
    return {"records": records_all, "choices": choices_all}
