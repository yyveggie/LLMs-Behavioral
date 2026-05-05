import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.bigfive import run_bigfive
from experiments.common import ChatClient, add_metadata, load_env_file, load_llm_config, load_yaml, save_records
from experiments.economic_games import experiment_prompts, run_occupations_described, run_prompt_experiment
from experiments.prisoners_dilemma import run_prisoners_dilemma, run_prisoners_dilemma_occupations_described
from experiments.public_goods import run_public_goods, run_public_goods_occupations_described
from experiments.risk_games import run_beauty_contest, run_bomb_risk, run_holt_laury


def run_selected_experiment(client, name, exp_config, print_except, max_retries):
    n_instances = int(exp_config.get("n_instances", 30))
    if name == "bigfive":
        return run_bigfive(
            client,
            n_instances=n_instances,
            print_except=print_except,
            max_retries=max_retries,
        )
    if name in experiment_prompts():
        return run_prompt_experiment(
            client,
            name=name,
            n_instances=n_instances,
            print_except=print_except,
            max_retries=max_retries,
        )
    occupation_experiments = {
        "dictator_occupations_described": "dictator",
        "ultimatum_proposer_occupations_described": "ultimatum_proposer",
        "ultimatum_responder_occupations_described": "ultimatum_responder",
        "trust_investor_occupations_described": "trust_investor",
        "trust_banker_10_occupations_described": "trust_banker_10",
        "trust_banker_50_occupations_described": "trust_banker_50",
        "trust_banker_100_occupations_described": "trust_banker_100",
    }
    if name in occupation_experiments:
        return run_occupations_described(
            client,
            base_name=occupation_experiments[name],
            n_instances=n_instances,
            print_except=print_except,
            max_retries=max_retries,
        )
    if name == "bomb_risk":
        return run_bomb_risk(
            client,
            n_instances=n_instances,
            print_except=print_except,
            only_first=bool(exp_config.get("only_first", False)),
            max_retries=max_retries,
        )
    if name == "holt_laury":
        return run_holt_laury(
            client,
            n_instances=n_instances,
            print_except=print_except,
            max_retries=max_retries,
        )
    if name == "beauty_contest":
        return run_beauty_contest(
            client,
            n_instances=n_instances,
            print_except=print_except,
            max_retries=max_retries,
        )
    public_goods_names = {"public_goods", "public_goods_loss"}
    public_goods_occupation_names = {"public_goods_occupations_described", "public_goods_loss_occupations_described"}
    if name in public_goods_names:
        return run_public_goods(
            client,
            n_instances=n_instances,
            print_except=print_except,
            explicit=bool(exp_config.get("explicit", False)),
            accept_wrong_payoff=bool(exp_config.get("accept_wrong_payoff", True)),
            max_retries=max_retries,
            other_contributions=tuple(exp_config.get("other_contributions", [0, 0])),
        )
    if name in public_goods_occupation_names:
        return run_public_goods_occupations_described(
            client,
            n_instances=n_instances,
            print_except=print_except,
            explicit=bool(exp_config.get("explicit", False)),
            accept_wrong_payoff=bool(exp_config.get("accept_wrong_payoff", True)),
            max_retries=max_retries,
            other_contributions=tuple(exp_config.get("other_contributions", [0, 0])),
        )
    prisoner_sequences = {
        "prisoners_dilemma": ["Pull", "Pull", "Push", "Push"],
        "prisoners_dilemma_five_rounds_pull": ["Pull", "Pull", "Push", "Push"],
        "prisoners_dilemma_two_rounds_push": ["Push"],
        "prisoners_dilemma_two_rounds_pull": ["Pull"],
    }
    prisoner_occupation_sequences = {
        "prisoners_dilemma_occupations_described": ["Pull", "Pull", "Push", "Push"],
        "prisoners_dilemma_five_rounds_pull_occupations_described": ["Pull", "Pull", "Push", "Push"],
        "prisoners_dilemma_two_rounds_push_occupations_described": ["Push"],
        "prisoners_dilemma_two_rounds_pull_occupations_described": ["Pull"],
    }
    if name in prisoner_sequences:
        return run_prisoners_dilemma(
            client,
            n_instances=n_instances,
            print_except=print_except,
            max_retries=max_retries,
            opponent_sequence=prisoner_sequences[name],
        )
    if name in prisoner_occupation_sequences:
        return run_prisoners_dilemma_occupations_described(
            client,
            n_instances=n_instances,
            print_except=print_except,
            max_retries=max_retries,
            opponent_sequence=prisoner_occupation_sequences[name],
        )
    raise ValueError(f"Unknown experiment: {name}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/run_config.yaml")
    parser.add_argument("--experiment", default=None, help="Only run one experiment name from run_config.yaml")
    parser.add_argument("--llm", default=None, help="Override active_llm from run_config.yaml, e.g. moonshot/openai/deepseek/qwen")
    parser.add_argument("--results-dir", default=None, help="Override results_dir from run_config.yaml")
    args = parser.parse_args()

    load_env_file()
    run_config = load_yaml(args.config)
    active_llm = args.llm or run_config["active_llm"]
    llm_config = load_llm_config(run_config.get("llm_config_path", "configs/llm_configs.yaml"), active_llm)
    results_dir = args.results_dir or run_config.get("results_dir") or f"records_new/{active_llm}"
    run_options = run_config.get("run", {})
    print_except = bool(run_options.get("print_except", True))
    save_metadata = bool(run_options.get("save_metadata", True))
    max_retries = int(run_options.get("max_retries", 3))

    client = ChatClient(llm_config)
    print(f"active_llm: {active_llm}")
    print(f"model: {llm_config['model']}")
    print(f"results_dir: {results_dir}")
    print(f"max_retries: {max_retries}")

    ran_any = False
    for name, exp_config in run_config.get("experiments", {}).items():
        if args.experiment is not None and name != args.experiment:
            continue
        if args.experiment is None and not exp_config.get("enabled", False):
            print(f"skip disabled: {name}")
            continue
        ran_any = True
        print(f"running: {name}")
        records = run_selected_experiment(
            client,
            name=name,
            exp_config=exp_config,
            print_except=print_except,
            max_retries=max_retries,
        )
        if save_metadata:
            records = add_metadata(records, exp_config, llm_config, name)
        save_records(records, results_dir, f"{name}_{active_llm}")

    if not ran_any:
        if args.experiment is None:
            print("No enabled experiments found in config.")
        else:
            print(f"No enabled experiment matched: {args.experiment}")


if __name__ == "__main__":
    main()
