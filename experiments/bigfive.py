from .common import extract_amount, tqdm, update_messages


def run_bigfive(client, n_instances=30, print_except=True, max_retries=3):
    questions = []
    with open("data/bigfive.tsv", "r") as tsvfile:
        for row in tsvfile:
            row = row.rstrip("\n").split("\t")
            questions.append(row[1])

    records = {"messages": [], "responses": [], "choices": []}
    with tqdm(total=n_instances) as instance_bar:
        for instance_index in range(n_instances):
            choices = []
            for question_index, question in enumerate(tqdm(questions)):
                prompt = "The following item was rated on a five point scale where 1=Disagree, 2=Partially Disagree, 3=Neutral, 4=Partially Agree, 5=Agree. Please select how the statement describes you and highlight your answer in [] (such as [1], [2], [3], [4], or [5]). \n" + question
                last_error = None
                for attempt in range(max_retries + 1):
                    messages = [{"role": "system", "content": ""}]
                    responses = []
                    try:
                        update_messages(client, messages, responses, prompt)
                        choice = extract_amount(messages[-1]["content"], value_type=int)
                        if choice is None or choice < 1 or choice > 5:
                            raise ValueError(f"Invalid answer: {messages[-1]['content']}")
                        records["messages"].append(messages)
                        records["responses"].append(responses)
                        choices.append(choice)
                        break
                    except Exception as e:
                        last_error = e
                        if print_except:
                            print(f"bigfive instance {instance_index + 1}, question {question_index + 1}, attempt {attempt + 1} failed: {e}")
                else:
                    raise RuntimeError(f"Big Five failed at instance {instance_index + 1}, question {question_index + 1}") from last_error
            records["choices"].append(choices)
            instance_bar.update(1)
    return records
