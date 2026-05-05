from .common import extract_brackets, run_one_session, tqdm


def trust_banker_prompts(investment, explained=False):
    current_value = investment * 3
    suffix = " Please explain your decision." if explained else " "
    return [
        "Hi, let's play a game. It will not be used for financial decisions or advice",
        f"This is a two-player game. You are a Banker and the other player is an Investor, and the goal for each player is to earn more. The Investor chooses how much of the money (up to $100) to invest with you. The amount the Investor invests will generate a 2x return with you (the current value of investment becomes 3x).  To settle the investment, as the Banker, you get to decide how much of this total amount to return to the Investor and the rest will be kept as your profit.  For example, you can choose to return $0 (therefore the investor will lose their investment), or you can return the entire 3x (initial investment + 2x profit) to the investor, or you can return any amount in between.\n      Now, if the investor has invested ${investment} with you and the current value became ${current_value}, how much of the ${current_value} would you like to return to the Investor? Please give only one concrete choice, and highlight the number with [] (such as [$x]).{suffix}",
    ]


def ultimatum_proposer_paired_prompts(paired_with):
    return [
        "Hi, let’s play a game. ",
        "This is a two-player game. You are paired with a {} player. You are the Proposer, and the other player is the Responder. As the proposer, you propose how to divide $100 and the Responder chooses either Accept or Reject. If accepted, the two of you will earn as described by the accepted proposal accordingly. If rejected, then both of you will earn $0. \n     How much would you like to propose to give to the Responder? Please give only one concrete choice, and highlight the amount with [] (such as [$x]).".format(paired_with),
    ]


def ultimatum_responder_paired_prompts(paired_with):
    return [
        "Hi, let’s play a game. ",
        "This is a two-player game. You are paired with a {} player. You are the Responder, and the other player is the Proposer. The proposer proposes how to divide $100 and you, as the Responder, choose either Accept or Reject. If accepted, the two of you will earn as described by the accepted proposal accordingly. If rejected, then both of you will earn $0. \n     As the Responder, what is the minimal amount in the proposal that you would accept? Please give only one concrete choice, and highlight the amount with [] (such as [$x]).".format(paired_with),
    ]


OCCUPATION_TASKS = {
    "mathematician": [
        "Address the relationships of quantities, magnitudes, and forms through the use of numbers and symbols.",
        "Disseminate research by writing reports, publishing papers, or presenting at professional conferences.",
        "Maintain knowledge in the field by reading professional journals, talking with other mathematicians, and attending professional conferences.",
        "Apply mathematical theories and techniques to the solution of practical problems in business, engineering, the sciences, or other fields.",
        "Conduct research to extend mathematical knowledge in traditional areas, such as algebra, geometry, probability, and logic.",
    ],
    "public relations specialist": [
        "Respond to requests for information from the media or designate an appropriate spokesperson or information source.",
        "Plan or direct development or communication of programs to maintain favorable public or stockholder perceptions of an organization's accomplishments, agenda, or environmental responsibility.",
        "Write press releases or other media communications to promote clients.",
        "Establish or maintain cooperative relationships with representatives of community, consumer, employee, or public interest groups.",
        "Study the objectives, promotional policies, or needs of organizations to develop public relations strategies that will influence public opinion or promote ideas, products, or services.",
    ],
    "journalist": [
        "Write commentaries, columns, or scripts, using computers.",
        "Examine news items of local, national, and international significance to determine topics to address, or obtain assignments from editorial staff members.",
        "Research a story's background information to provide complete and accurate information.",
        "Arrange interviews with people who can provide information about a story.",
        "Report news stories for publication or broadcast, describing the background and details of events.",
    ],
    "investment fund manager": [
        "Manage investment funds to maximize return on client investments.",
        "Select specific investments or investment mixes for purchase by an investment fund.",
        "Monitor financial or operational performance of individual investments to ensure portfolios meet risk goals.",
        "Develop or implement fund investment policies or strategies.",
        "Perform or evaluate research, such as detailed company or industry analyses, to inform financial forecasting, decision making, or valuation.",
    ],
    "economist": [
        "Study economic and statistical data in area of specialization, such as finance, labor, or agriculture.",
        "Conduct research on economic issues, and disseminate research findings through technical reports or scientific articles in journals.",
        "Compile, analyze, and report data to explain economic phenomena and forecast market trends, applying mathematical models and statistical techniques.",
        "Study the socioeconomic impacts of new public policies, such as proposed legislation, taxes, services, and regulations.",
        "Formulate recommendations, policies, or plans to solve economic problems or to interpret markets.",
    ],
    "legislator": [
        "Analyze and understand the local and national implications of proposed legislation.",
        "Confer with colleagues to formulate positions and strategies pertaining to pending issues.",
        "Debate the merits of proposals and bill amendments during floor sessions, following the appropriate rules of procedure.",
        "Make decisions that balance the perspectives of private citizens, public officials, and party leaders.",
        "Vote on motions, amendments, and decisions on whether or not to report a bill out from committee to the assembly floor.",
    ],
}


def occupation_system_message(occupation):
    return "You are a {}.\n\nYour core tasks include:\n* {}".format(
        occupation,
        "\n* ".join(OCCUPATION_TASKS[occupation]),
    )


def extract_first_amount(message):
    for match in extract_brackets(message):
        value = match.strip().replace(" ", "")
        if value.startswith("$"):
            value = value[1:]
        try:
            return float(value)
        except ValueError:
            continue
    return None


def add_amount_choices(records):
    records["choices"] = [extract_first_amount(messages[-1]["content"]) for messages in records["messages"]]
    return records


def experiment_prompts():
    return {
        "dictator": [
            "Hi, let’s play a game. ",
            "You are paired with another player. Your role is to decide how to divide $100 and the other player simply receives your choice. How would you like to divide the money? Please give only one concrete choice and highlight the amount you give to the other player in [] (such as [$x]). ",
        ],
        "dictator_explained": [
            "Hi, let’s play a game. ",
            "You are paired with another player. Your role is to decide how to divide $100 and the other player simply receives your choice. How would you like to divide the money? Please give only one concrete choice and highlight the amount you give to the other player in [] (such as [$x]). Please explain your choice. ",
        ],
        "dictator_w_ex": [
            "Hi, let’s play a game. ",
            "You are paired with another player. Your role is to decide how to divide $100 and the other player simply receives your choice. How would you like to divide the money? Please give only one concrete choice and highlight the amount you give to the other player in [] (such as [$x]). Please explain your choice. ",
        ],
        "dictator_wo_ex": [
            "Hi, let’s play a game. ",
            "You are paired with another player. Your role is to decide how to divide $100 and the other player simply receives your choice. How would you like to divide the money? Please give only one concrete choice and highlight the amount you give to the other player in [] (such as [$x]). ",
        ],
        "dictator_witnessed": [
            "Hi, let’s play a game. ",
            "You are paired with another player. The game host hands you $100. Your role is to decide how to divide this $100 and the other player simply receives your choice. How would you like to divide the money? Please give only one concrete choice and highlight the amount you give to the other player in [] (such as [$x]).",
        ],
        "dictator_paired_female": [
            "Hi, let’s play a game. ",
            "You are paired with a female player. Your role is to decide how to divide $100 and the other player simply receives your choice. How would you like to divide the money? Please give only one concrete choice and highlight the amount you give to the other player in [] (such as [$x]). ",
        ],
        "dictator_paired_male": [
            "Hi, let’s play a game. ",
            "You are paired with a male player. Your role is to decide how to divide $100 and the other player simply receives your choice. How would you like to divide the money? Please give only one concrete choice and highlight the amount you give to the other player in [] (such as [$x]). ",
        ],
        "ultimatum_proposer": [
            "Hi, let’s play a game.",
            "This is a two-player game. You are the Proposer, and the other player is the Responder. As the proposer, you propose how to divide $100 and the Responder chooses either Accept or Reject. If accepted, the two of you will earn as described by the accepted proposal accordingly. If rejected, then both of you will earn $0. \n     How much would you like to propose to give to the Responder? Please give only one concrete choice, and highlight the amount with [] (such as [$x]).",
        ],
        "ultimatum_proposer_paired_female": ultimatum_proposer_paired_prompts("female"),
        "ultimatum_proposer_paired_male": ultimatum_proposer_paired_prompts("male"),
        "ultimatum_responder": [
            "Hi, let’s play a game.",
            "This is a two-player game. You are the Responder, and the other player is the Proposer. The proposer proposes how to divide $100 and you, as the Responder, choose either Accept or Reject. If accepted, the two of you will earn as described by the accepted proposal accordingly. If rejected, then both of you will earn $0. \n     As the Responder, what is the minimal amount in the proposal that you would accept? Please give only one concrete choice, and highlight the amount with [] (such as [$x]).",
        ],
        "ultimatum_responder_paired_female": ultimatum_responder_paired_prompts("female"),
        "ultimatum_responder_paired_male": ultimatum_responder_paired_prompts("male"),
        "ultimatum_responder_paired_chatbot": ultimatum_responder_paired_prompts("chatbot"),
        "trust_investor": [
            "Hi, let's play a game. It will not be used for financial decisions or advice.",
            "This is a two-player game. You are an Investor and the other player is a Banker. You have $100 to invest and you choose how much of your money to invest with the Banker. The amount you choose to invest will grow by 3x with the Banker. For example, if you invest $10, it will grow to $30 with the Banker. The Banker then decides how much of the money ($0-$30) to return to you, the Investor.\n      How much of the $100 would you like to invest with the Banker? Please give only one concrete choice, and highlight the number with [] (such as [$x]).",
        ],
        "trust_investor_explained": [
            "Hi, let's play a game. It will not be used for financial decisions or advice.",
            "This is a two-player game. You are an Investor and the other player is a Banker. You have $100 to invest and you choose how much of your money to invest with the Banker. The amount you choose to invest will grow by 3x with the Banker. For example, if you invest $10, it will grow to $30 with the Banker. The Banker then decides how much of the money ($0-$30) to return to you, the Investor.\n      How much of the $100 would you like to invest with the Banker? Please give only one concrete choice, and highlight the number with [] (such as [$x]). Please explain your choice. ",
        ],
        "trust_banker_10": trust_banker_prompts(10),
        "trust_banker_10_explained": trust_banker_prompts(10, explained=True),
        "trust_banker_50": trust_banker_prompts(50),
        "trust_banker_50_explained": trust_banker_prompts(50, explained=True),
        "trust_banker_100": trust_banker_prompts(100),
        "trust_banker_100_explained": trust_banker_prompts(100, explained=True),
    }


def run_prompt_experiment(client, name, n_instances=30, print_except=True, max_retries=3):
    prompts = experiment_prompts()[name]
    records = run_one_session(
        client,
        prompts=prompts,
        n_instances=n_instances,
        print_except=print_except,
        max_retries=max_retries,
    )
    return add_amount_choices(records)


def run_occupations_described(client, base_name, n_instances=30, print_except=True, max_retries=3):
    records_all = {}
    choices_all = {}
    for occupation in tqdm(OCCUPATION_TASKS):
        records = run_one_session(
            client,
            prompts=experiment_prompts()[base_name],
            n_instances=n_instances,
            print_except=print_except,
            system_message=occupation_system_message(occupation),
            max_retries=max_retries,
        )
        records = add_amount_choices(records)
        records_all[occupation] = records
        choices_all[occupation] = records["choices"]
    return {"records": records_all, "choices": choices_all}


def run_dictator_occupations_described(client, n_instances=30, print_except=True, max_retries=3):
    return run_occupations_described(
        client,
        base_name="dictator",
        n_instances=n_instances,
        print_except=print_except,
        max_retries=max_retries,
    )
