#! /usr/bin/env make
APP_ROOT_PATH := ./app
TESTS_PATH := ./tests
TESTS_EVENTS_PATH := ${TESTS_PATH}/events
LOCALSTACK_IMAGE := "localstack/localstack:1.2.0"
LOCALSTACK_CONTAINER_NAME := "workshop-unit-testing"
DOCKER_API ?= "docker"
AWS_ACCESS_KEY_ID=foo
AWS_SECRET_ACCESS_KEY=bar

install:
	@pip install -r ${APP_ROOT_PATH}/requirements.txt
	@pip install -r ${TESTS_PATH}/requirements.txt

localstack-start: localstack-stop
	@echo ">>> Starting localstack in detached mode"
	@${DOCKER_API} run -d \
	-e DEBUG=1 \
	-e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
	-e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
	-e DEFAULT_REGION=eu-central-1 \
	-e HOSTNAME=localstack \
	-e HOSTNAME_EXTERNAL=localstack \
	-e LOCALSTACK_HOST=localstack \
	-e TEST_AWS_ACCOUNT_ID=000000000000 \
	--mount type=volume,target=/tmp/localstack \
	-p 4566:4566 \
	-p 4571:4571 \
	--name=${LOCALSTACK_CONTAINER_NAME} \
	${LOCALSTACK_IMAGE}

	@export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
	&& export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
	&& python ./build/localstack.py

localstack-stop:
	@echo ">>> Stopping container if it is running"
	@${DOCKER_API} stop ${LOCALSTACK_CONTAINER_NAME} || true && ${DOCKER_API} rm ${LOCALSTACK_CONTAINER_NAME} || true
	@echo ">>> Done"

run: localstack-start
	@export PYTHONPATH=${APP_ROOT_PATH} \
	&& export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
	&& export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
	&& python app/main.py

unit-tests:
	@export PYTHONPATH=${APP_ROOT_PATH} \
	&& export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
	&& export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
	&& pytest --cov-report term-missing --cov-config=.coveragerc --cov=${APP_ROOT_PATH}

default: install
