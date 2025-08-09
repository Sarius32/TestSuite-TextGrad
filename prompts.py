def get_sys_prompt(name):
    return "'" + "".join(open(f"agents/{name}.md", "r").readlines()).strip().replace("\n", "\\n") + "'"


ARCH_NAME = "ARCHITECT"
ARCH_SYS_PROMPT = get_sys_prompt(ARCH_NAME.lower())
ARCH_PROMPT = "'For the `simplejson` project, generate the test requirements!'"

GEN_NAME = "GENERATOR"
GEN_SYS_PROMPT = get_sys_prompt(GEN_NAME.lower())
GEN_INIT_PROMPT = "'Generate an initial test suite for the `simplejson` project based on the given test requirements!'"
GEN_ERROR_PROMPT = "'Error(s) occurred during the collection of test suite for the `simplejson` project preventing it from being executed! Please correct the test suite accordingly!'"
GEN_REFINE_PROMPT = "'Refine the existing test suite for the `simplejson` project based on the latest evaluation!'"

EVAL_NAME = "EVALUATOR"
EVAL_SYS_PROMPT = get_sys_prompt(EVAL_NAME.lower())
EVAL_PROMPT = lambda \
        metrics: f"'Evaluate the given test suite for the `simplejson` project based on the latest execution reports! The execution yielded the following result: {metrics}'"
