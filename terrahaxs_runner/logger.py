import logging

# TODO: fix logger based on where running
# TODO: add attributes to logger if hosted: org, repo, project, etc
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)