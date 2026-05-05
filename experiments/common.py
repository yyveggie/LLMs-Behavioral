import json
import os
import re
import signal
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

import openai

try:
    from tqdm import tqdm
except ModuleNotFoundError:
    def tqdm(iterable=None, total=None, disable=False):
        return iterable if iterable is not None else range(total or 0)


class TimeoutException(Exception):
    pass


@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(int(seconds))
    try:
        yield
    finally:
        signal.alarm(0)


def strip_inline_comment(value):
    quote = None
    escaped = False
    for index, char in enumerate(value):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char in {"'", '"'}:
            if quote is None:
                quote = char
            elif quote == char:
                quote = None
            continue
        if char == "#" and quote is None:
            return value[:index].rstrip()
    return value.strip()


def parse_scalar(value):
    value = strip_inline_comment(value).strip()
    if value == "":
        return ""
    if value.startswith(("'", '"')) and value.endswith(("'", '"')):
        return value[1:-1]
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"null", "none"}:
        return None
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value


def simple_yaml_load(path):
    root = {}
    stack = [(-1, root)]
    with open(path, "r") as f:
        for raw_line in f:
            if not raw_line.strip() or raw_line.lstrip().startswith("#"):
                continue
            indent = len(raw_line) - len(raw_line.lstrip(" "))
            text = strip_inline_comment(raw_line.strip())
            if not text:
                continue
            while stack and indent <= stack[-1][0]:
                stack.pop()
            parent = stack[-1][1]
            if text.startswith("- "):
                item_text = text[2:].strip()
                item = {}
                parent.append(item)
                if item_text and ":" in item_text:
                    key, value = item_text.split(":", 1)
                    item[key.strip()] = parse_scalar(value)
                stack.append((indent, item))
                continue
            key, value = text.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value == "":
                child = [] if key == "llms" else {}
                parent[key] = child
                stack.append((indent, child))
            else:
                parent[key] = parse_scalar(value)
    return root


def load_yaml(path):
    try:
        import yaml
        with open(path, "r") as f:
            return yaml.safe_load(f)
    except ModuleNotFoundError:
        return simple_yaml_load(path)


def resolve_env(value):
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        return os.environ.get(value[2:-1])
    return value


def load_env_file(path=".env"):
    env_path = Path(path)
    if not env_path.exists():
        return
    with open(env_path, "r") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("'\"")
            os.environ.setdefault(key, value)


def merge_llm_configs(base_config, local_config):
    merged = dict(base_config or {})
    llms_by_name = {
        llm.get("name"): dict(llm)
        for llm in (merged.get("llms") or [])
        if llm.get("name")
    }
    for llm in (local_config or {}).get("llms", []) or []:
        name = llm.get("name")
        if name:
            llms_by_name[name] = dict(llm)
    merged["llms"] = list(llms_by_name.values())
    return merged


def load_llm_config(path, active_llm):
    config = load_yaml(path)
    local_path = Path(path).with_name(f"{Path(path).stem}.local{Path(path).suffix}")
    if local_path.exists():
        config = merge_llm_configs(config, load_yaml(local_path))
    llms = config.get("llms", [])
    for llm in llms:
        for key, value in list(llm.items()):
            llm[key] = resolve_env(value)
    matched = [llm for llm in llms if llm.get("name") == active_llm]
    if not matched:
        raise ValueError(f"LLM config not found: {active_llm}")
    llm = matched[0]
    if not llm.get("api_key"):
        raise ValueError(f"Missing API key for {active_llm}. Set the environment variable used in the LLM YAML.")
    return llm


def response_to_dict(response):
    if hasattr(response, "model_dump"):
        return response.model_dump()
    if hasattr(response, "to_dict_recursive"):
        return response.to_dict_recursive()
    if hasattr(response, "to_dict"):
        return response.to_dict()
    return response


def message_to_dict(message):
    if isinstance(message, dict):
        return dict(message)
    if hasattr(message, "model_dump"):
        return message.model_dump()
    if hasattr(message, "to_dict"):
        return message.to_dict()
    return {"role": getattr(message, "role", "assistant"), "content": getattr(message, "content", "")}


class ChatClient:
    def __init__(self, llm_config):
        self.name = llm_config["name"]
        self.model = llm_config["model"]
        self.base_url = llm_config.get("base_url")
        self.api_key = llm_config["api_key"]
        self.timeout = int(llm_config.get("timeout", 60))
        self.client = None
        if hasattr(openai, "OpenAI"):
            try:
                self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url, timeout=self.timeout)
            except TypeError:
                self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
        else:
            openai.api_key = self.api_key
            openai.api_base = self.base_url

    def complete(self, messages, **kwargs):
        with time_limit(self.timeout):
            if self.client is not None:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    **kwargs,
                )
            else:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=messages,
                    **kwargs,
                )
        return response_to_dict(response)


def assistant_message(response):
    message = response["choices"][0].get("message")
    if message is not None:
        return message_to_dict(message)
    return {"role": "assistant", "content": response["choices"][0].get("text", "")}


def update_messages(client, messages, responses, prompt, **kwargs):
    messages.append({"role": "user", "content": prompt})
    response = client.complete(messages, **kwargs)
    responses.append(response)
    messages.append(assistant_message(response))


def run_one_session(client, prompts, n_instances=30, orders=None, print_except=True, system_message="You are a helpful assistant.", max_retries=3):
    records = {"messages": [], "responses": []}
    if orders is None:
        orders = [list(range(len(prompts)))] * n_instances
    with tqdm(total=n_instances) as pbar:
        for i in range(n_instances):
            last_error = None
            for attempt in range(max_retries + 1):
                try:
                    messages = [{"role": "system", "content": system_message}]
                    responses = []
                    for prompt_id in orders[i]:
                        update_messages(client, messages, responses, prompts[prompt_id])
                    records["messages"].append(messages)
                    records["responses"].append(responses)
                    pbar.update(1)
                    break
                except Exception as e:
                    last_error = e
                    if print_except:
                        print(f"instance {i + 1}, attempt {attempt + 1} failed: {e}")
            else:
                raise RuntimeError(f"Failed instance {i + 1} after {max_retries + 1} attempts") from last_error
    return records


def extract_brackets(text, brackets="[]"):
    pattern = re.escape(brackets[0]) + r"(.*?)" + re.escape(brackets[1])
    return re.findall(pattern, text)


def extract_amount(message, prefix="", value_type=float, brackets="[]"):
    matches = extract_brackets(message, brackets=brackets)
    matches = [s.replace(" ", "") for s in matches]
    matches = [s[len(prefix):] if s.startswith(prefix) else s for s in matches]
    if not matches:
        return None
    if any(match != matches[0] for match in matches):
        return None
    try:
        return value_type(matches[0])
    except Exception:
        return None


def extract_card(message):
    matches = extract_brackets(message)
    for match in matches:
        normalized = match.strip().lower()
        if normalized == "push":
            return "Push"
        if normalized == "pull":
            return "Pull"
    match = re.search(r"\b(Push|Pull)\b", message, flags=re.IGNORECASE)
    if not match:
        return None
    return "Push" if match.group(1).lower() == "push" else "Pull"


def add_metadata(records, run_config, llm_config, experiment_name):
    records["metadata"] = {
        "experiment": experiment_name,
        "llm_name": llm_config["name"],
        "model": llm_config["model"],
        "base_url": llm_config.get("base_url"),
        "timestamp": datetime.now().isoformat(),
        "run_config": run_config,
    }
    return records


def save_records(records, results_dir, game_name):
    Path(results_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
    output_path = Path(results_dir) / f"{game_name}_{timestamp}.json"
    with open(output_path, "w") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print(f"saved: {output_path}")
    return output_path
