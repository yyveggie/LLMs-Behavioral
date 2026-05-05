# ChatGPT Behavioral Experiment Reproduction

Language: [English](#english) | [中文](#中文)

<a id="english"></a>

This repository is a modified and modularized reproduction project based on the original work by **Yutong Xie** and collaborators on behavioral experiments with AI chatbots.

The goal of this repository is to make the original notebook-based experiment workflow easier to run, configure, debug, and extend with different LLM providers and model variants.

## Running the Experiments

Detailed running instructions are available in:

```text
RUNNING_EXPERIMENTS.md
```

Please read that file first if you want to run the modular Python experiment scripts.

## LLM Provider Configuration

This project supports OpenAI-compatible LLM providers through `configs/llm_configs.yaml`.

Built-in example provider names include:

- **`moonshot`**
- **`openai`**
- **`deepseek`**
- **`qwen`**
- **`siliconflow`**

You can choose the default provider in `configs/run_config.yaml`:

```yaml
active_llm: deepseek
```

Or override it from the command line:

```bash
python scripts/run_configured_experiments.py --config configs/run_config.yaml --llm deepseek --experiment dictator
```

API keys should be provided through environment variables, not hardcoded in config files. You can copy `.env.example` to `.env` locally and fill in your keys:

```bash
cp .env.example .env
```

Do not commit your real `.env` file or real API keys.

## Attribution

This project is based on the original repository and research associated with:

**A Turing test of whether AI chatbots are behaviorally similar to humans**

The original code and materials were authored by **Yutong Xie** and are licensed under the MIT License.

This repository modifies and reorganizes the original project for reproduction and extension purposes. The original authors retain copyright over their original work.

## License

The original project is licensed under the **MIT License**.

The MIT License permits use, copy, modification, publication, distribution, sublicensing, and sale of the software, provided that the original copyright notice and license text are included in copies or substantial portions of the software.

The original license notice is preserved in:

```text
LICENSE
```

Original copyright notice:

```text
Copyright (c) 2023 Yutong Xie
```

Unless otherwise stated, modifications in this repository are also provided under the MIT License.

## Main Modifications in This Repository

Compared with the original notebook-oriented workflow, this repository includes the following modifications:

- **Modular experiment scripts**: Experiment logic has been split into Python modules under `experiments/`.
- **Unified configurable runner**: Experiments can be launched through `scripts/run_configured_experiments.py` and `configs/run_config.yaml`.
- **LLM provider configuration**: Model/provider settings are centralized in `configs/llm_configs.yaml`.
- **Finite retry logic**: API calls use limited retries to avoid experiments hanging indefinitely.
- **Expanded experiment variants**: Additional original notebook variants have been exposed as runnable Python experiment entries.
- **Running manual**: `RUNNING_EXPERIMENTS.md` documents commands and experiment meanings.

## Data and Materials

The `data/` directory contains human behavioral data and questionnaire-related files used for comparison with model behavior. These files are part of the original research materials unless otherwise noted.

The `records/` directory contains original or existing model output records from the project.

The `records_new/` directory is intended for newly generated model experiment outputs from this modified runner.

The `legacy_notebooks/` directory contains original or historical notebook workflows kept for reference. The recommended way to run new experiments is still the modular Python runner.

Please do not represent the original data, paper materials, or archived model outputs as newly collected data unless you have independently generated them.

## Citation

If you use this repository or its original materials in academic work, reports, or derivative projects, please cite the original paper and acknowledge the original authors.

Suggested acknowledgement:

```text
This project is based on the original work by Yutong Xie et al. on behavioral experiments with AI chatbots. The original project is licensed under the MIT License. This repository modifies and modularizes the experiment-running workflow for reproduction and extension purposes.
```

## Disclaimer

This repository is provided for research, reproduction, and educational purposes.

The modified code is provided "as is", without warranty of any kind. Users are responsible for verifying experiment settings, model configurations, data provenance, and any results generated from this repository.

## Notes for Future Users

Before running experiments, make sure to:

- **Activate the correct Python/conda environment**.
- **Set the required API key environment variables**.
- **Check `configs/run_config.yaml` for enabled experiments and output paths**.
- **Make sure the Python command you use has the required dependencies installed**.

For details, see:

```text
RUNNING_EXPERIMENTS.md
```

---

<a id="中文"></a>

# 中文说明

本仓库是在原作者 **Yutong Xie** 及其合作者相关研究项目基础上进行修改和整理的复现项目，研究主题为 AI 聊天机器人在行为实验中的表现。

本仓库的主要目标是将原本以 Jupyter Notebook 为主的实验流程，改造成更容易运行、配置、调试和扩展的 Python 脚本结构，方便使用不同服务商和不同模型进行复现实验。

## 实验运行说明

详细运行方式请查看：

```text
RUNNING_EXPERIMENTS.md
```

如果你想运行已经拆分好的 Python 实验脚本，请优先阅读该文件。

## LLM 服务商配置

只要服务商提供 OpenAI-compatible Chat Completions 接口，通常都可以通过 `configs/llm_configs.yaml` 接入。

当前内置示例配置包括：

- **`moonshot`**
- **`openai`**
- **`deepseek`**
- **`qwen`**
- **`siliconflow`**

你可以在 `configs/run_config.yaml` 中修改默认服务商：

```yaml
active_llm: deepseek
```

也可以在命令行临时切换：

```bash
python scripts/run_configured_experiments.py --config configs/run_config.yaml --llm deepseek --experiment dictator
```

API Key 应该通过环境变量提供，不要直接写进配置文件。你可以复制 `.env.example` 为本地 `.env`，然后填写自己的 Key：

```bash
cp .env.example .env
```

不要提交真实的 `.env` 文件或真实 API Key。

## 原作者与项目来源声明

本项目基于以下研究及其原始代码/材料修改而来：

**A Turing test of whether AI chatbots are behaviorally similar to humans**

原始代码和相关材料由 **Yutong Xie** 等作者完成，并采用 MIT License 授权。

本仓库仅在原项目基础上进行复现、模块化整理和扩展实验支持。原作者仍然保留其原始工作的版权。

## 许可证说明

原项目采用 **MIT License**。

MIT License 允许使用、复制、修改、发布、分发、再授权和销售该软件，但前提是必须在软件副本或实质性部分中保留原始版权声明和许可证文本。

原始许可证文件保留在：

```text
LICENSE
```

原始版权声明为：

```text
Copyright (c) 2023 Yutong Xie
```

除非另有说明，本仓库中的修改部分同样按照 MIT License 发布。

## 本仓库的主要修改

相比原始项目中以 Notebook 为主的运行方式，本仓库主要做了以下修改：

- **模块化实验脚本**：将不同实验逻辑拆分到 `experiments/` 目录下的多个 Python 模块中。
- **统一配置式运行入口**：通过 `scripts/run_configured_experiments.py` 和 `configs/run_config.yaml` 统一启动实验。
- **模型/服务商配置集中管理**：通过 `configs/llm_configs.yaml` 管理不同 LLM 服务商、模型名、API 地址和 Key。
- **有限重试机制**：API 请求失败时使用有限次数重试，避免实验长时间卡死。
- **补充实验变体**：将原始 Notebook 中的多个实验变体整理为可直接运行的 Python 实验入口。
- **运行说明书**：新增 `RUNNING_EXPERIMENTS.md`，说明每个实验命令对应的实验类别和含义。

## 数据和材料说明

`data/` 目录包含用于和模型行为进行对比的人类行为实验数据以及问卷相关文件。这些数据和材料除非特别说明，均来自原始研究项目。

`records/` 目录包含原项目中已有的模型输出记录或实验日志。

`records_new/` 目录用于保存通过本仓库修改后的实验 runner 新生成的模型实验结果。

`legacy_notebooks/` 目录用于保存原始或历史 Notebook 工作流，主要作为参考材料保留。新的实验运行仍然推荐使用模块化 Python runner。

请不要将原始数据、论文材料或已有模型输出记录表述为自己新采集的数据，除非你确实独立重新生成或采集了这些数据。

## 引用建议

如果你在论文、报告、课程项目或其他公开项目中使用本仓库或其中的原始材料，请引用原论文，并在项目中致谢原作者。

建议使用如下说明：

```text
本项目基于 Yutong Xie 等作者关于 AI 聊天机器人行为实验的原始研究项目修改而来。原项目采用 MIT License 授权。本仓库在其基础上对实验运行流程进行了模块化整理，并用于复现实验和扩展实验。
```

## 免责声明

本仓库仅用于研究、复现和教学目的。

本仓库中的修改代码按“现状”提供，不作任何形式的保证。使用者需要自行确认实验设置、模型配置、数据来源以及基于本仓库生成的实验结果是否正确。

## 使用前注意事项

运行实验前，请确认：

- **已经激活正确的 Python/conda 环境**。
- **已经设置所需的 API Key 环境变量**。
- **已经检查 `configs/run_config.yaml` 中启用的实验和输出路径**。
- **确认运行命令使用的 Python 环境已经安装所需依赖**。

更多细节请查看：

```text
RUNNING_EXPERIMENTS.md
```
