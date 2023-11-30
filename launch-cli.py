#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys

sys.path.append(os.getcwd())

import yaml
import utils

from kubejobs.jobs import KubernetesJob


def argument_parser():
    parser = argparse.ArgumentParser(description="Backend Runner")
    parser.add_argument("config", type=str)
    args = parser.parse_args()
    return args




def main():
    args = argument_parser()
    configs = yaml.safe_load(open(args.config, "r"))

    job_name = 'hl-backend'
    is_completed = utils.check_if_completed(job_name)

    if is_completed is True:
        base_args = "apt -y update && apt -y upgrade && " \
                "apt-get -y install git-lfs unzip psmisc wget git python3 python-is-python3 pip bc htop nano && " \
                "git lfs install && " \
                "git clone https://huggingface.co/spaces/hallucinations-leaderboard/leaderboard && " \
                "cd leaderboard && pip install -U -r requirements.txt && pip install -U protobuf && " \
                "PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python HF_TOKEN=$HF_TOKEN H4_TOKEN=$HF_TOKEN "
        command = "python backend-cli.py"

        secret_env_vars = configs["env_vars"]

        # Create a Kubernetes Job with a name, container image, and command
        print(f"Creating job for: {command}")
        job = KubernetesJob(name="hl-backend",
                            image="nvcr.io/nvidia/cuda:12.0.0-cudnn8-devel-ubuntu22.04",
                            gpu_type="nvidia.com/gpu",
                            gpu_limit=configs["gpu_limit"],
                            gpu_product=configs["gpu_product"],
                            backoff_limit=1,
                            command=["/bin/bash", "-c", "--"],
                            args=[base_args + command],
                            secret_env_vars=secret_env_vars,
                            user_email="p.minervini@ed.ac.uk")

        # Run the Job on the Kubernetes cluster
        job.run()


if __name__ == "__main__":
    main()