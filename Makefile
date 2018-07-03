all:

flake8:
	venv/bin/flake8 server/ client/

pipcheck:
	venv/bin/pip check

# The ResourceWarning's come from ImageField's, but we weren't able to
# fix them. When we update Django we should check if they are fixed.
PYTHON := venv/bin/python -Werror

init:
	test -d venv/ || python3.5 -m venv venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install -r requirements-dev.txt
	venv/bin/pip install --require-hashes -r requirements.txt

check: pipcheck flake8
