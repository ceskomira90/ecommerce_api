
APPLICATION_PATH=app.py
TESTS_PATH=tests/
COVERAGE_PATH=views/
IMAGES_PATH=static/images/
DATABASE=database.db
EDITOR=subl

##########
# DEPLOY #
##########

########
# OPEN #
########

.PHONY: open
open:
	$(EDITOR) .

#######
# RUN #
#######

.PHONY: run
run:
	FLASK_APP=$(APPLICATION_PATH) flask run

.PHONY: debug
debug:
	FLASK_APP=$(APPLICATION_PATH) FLASK_DEBUG=1 flask run

########
# TEST #
########

.PHONY: test
test:
	pytest $(TESTS_PATH) --cov=$(COVERAGE_PATH) --cov-report html -v -s

#########
# CLEAN #
#########

.PHONY: clean
clean: clean_pyc clean_coverage clean_database clean_images

.PHONY: clean_coverage
clean_coverage:
	rm -rf htmlcov/

.PHONY: clean_database
clean_database:
	rm $(DATABASE)

.PHONY: clean_images
clean_images:
	rm -rf $(IMAGES_PATH)

.PHONY: clean_pyc
clean_pyc:
	find . -name '*.pyc' -delete
	find . -name __pycache__ -delete
