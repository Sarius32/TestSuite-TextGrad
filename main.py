import sys

import logging_

logging_.setup_logging(app_name="workflow", log_level_console="DEBUG")

import asyncio
import subprocess
import shutil
import os
from os.path import join as pjoin

from agent import Agent
from prompts import ARCH_NAME, ARCH_SYS_PROMPT, ARCH_PROMPT, GEN_NAME, GEN_SYS_PROMPT, GEN_INIT_PROMPT, \
    GEN_ERROR_PROMPT, GEN_REFINE_PROMPT, EVAL_NAME, EVAL_SYS_PROMPT, EVAL_PROMPT

LOGGER = logging_.get_logger(__name__)

CWD = sys.argv[1]
MODEL = sys.argv[2]
LOGGER.debug(f"Arguments: {CWD=}; {MODEL=}")


def archive_exec_eval(iteration):
    # remove cache
    shutil.rmtree(pjoin(CWD, ".pytest_cache")) if os.path.exists(pjoin(CWD, ".pytest_cache")) else None

    content = os.listdir(CWD)

    dst_dir = pjoin(CWD, "archive")
    os.mkdir(dst_dir)

    # files/folders to keep
    content.remove("simplejson")
    content.remove("tests")
    content.remove("evaluation_template.md")
    content.remove("pytest.ini")
    content.remove("test-requirements.md")
    content = [c for c in content if "zip" not in c]

    # move all created information
    for file_folder in content:
        shutil.move(pjoin(CWD, file_folder), pjoin(dst_dir, file_folder))

    shutil.make_archive(pjoin(CWD, f"archive_{iteration:02}"), 'zip', dst_dir)
    shutil.rmtree(dst_dir)
    LOGGER.debug(f"Created files for iteration {iteration} archived to archive_{iteration:02}.zip")


def archive_tests(iteration):
    # remove cache
    shutil.rmtree(pjoin(CWD, "tests", ".pytest_cache")) if os.path.exists(
        pjoin(CWD, "tests", ".pytest_cache")) else None
    shutil.make_archive(pjoin(CWD, f"tests_{iteration:02}"), 'zip', pjoin(CWD, "tests"))
    LOGGER.debug(f"Created tests for iteration {iteration} archived to tests_{iteration:02}.zip")


async def main(skip_architect=False):
    if not skip_architect:
        LOGGER.info("--- REQUIREMENTS DEFINITION ---")
        architect = Agent(ARCH_NAME, ARCH_SYS_PROMPT, CWD, MODEL)
        await architect.query(ARCH_PROMPT)

    gen_prompt = GEN_INIT_PROMPT
    for iteration in range(20):
        it = f" #{iteration}"
        LOGGER.info(f"--- TEST SUITE GENERATION{it} ---")
        generator = Agent(GEN_NAME + it, GEN_SYS_PROMPT, CWD, MODEL)
        await generator.query(gen_prompt)

        LOGGER.info(f"--- TEST SUITE ARCHIVING{it} ---")
        archive_exec_eval(iteration - 1) if iteration > 0 else None
        archive_tests(iteration)

        LOGGER.info(f"--- TEST SUITE EXECUTION{it} ---")
        exec_ = subprocess.run(["python", "-m", "pytest"], cwd=CWD, capture_output=True)
        if exec_.stderr or b"= ERRORS =" in exec_.stdout:
            LOGGER.info("Error(s) found during execution! Skipping evaluation!")
            gen_prompt = GEN_ERROR_PROMPT

            # save the error output of stderr (i.e. syntax error -> code can't be executed)
            if exec_.stderr:
                open(pjoin(CWD, "stderr.log"), "w").write(exec_.stderr.decode())

            # skip evaluation and instruct generator to fix errors directly
            continue

        LOGGER.info("Execution successful! Starting Evaluation!")
        gen_prompt = GEN_REFINE_PROMPT

        LOGGER.info(f"--- TEST SUITE EVALUATION{it} ---")
        evaluator = Agent(EVAL_NAME + it, EVAL_SYS_PROMPT, CWD, MODEL)
        final = "<FINAL>" in await evaluator.query(EVAL_PROMPT)

        if final:
            break


if __name__ == "__main__":
    asyncio.run(main(skip_architect=True))
