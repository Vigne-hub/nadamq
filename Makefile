.PHONY: build dist redist install clean uninstall

build:
	CYTHONIZE=1 ./setup.py build

dist:
	CYTHONIZE=1 ./setup.py sdist bdist_wheel

redist: clean dist

install:
	python ./file_handler.py . $(CONDA_PREFIX) nadamq nadamq NadaMQ
	CYTHONIZE=1 pip install .

clean:
	$(RM) -r build dist nadamq.egg-info
	$(RM) -r nadamq/src/{packet_actions.cpp,packet_socket_fsm_actions.cpp} nadamq/NadaMq.cpp
	$(RM) -r .pytest_cache
	find . -name __pycache__ -exec rm -r {} +
	#git clean -fdX

uninstall:
	pip uninstall nadamq
