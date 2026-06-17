# coding: utf-8
# Copyright (c) Huawei Technologies Co., Ltd. 2026. All rights reserved.
"""Entry point for `python -m agent_evolving`.

Invokes the offline GEPA skill evolver CLI.

Examples:
    python -m agent_evolving.offline --skill git-review
    python -m agent_evolving.offline --skill git-review --dry-run
    python -m agent_evolving.offline --skill git-review --iterations 5 --reuse-dataset
    python -m agent_evolving.offline --help
"""
from agent_evolving.offline.cli import main

if __name__ == "__main__":
    main()
