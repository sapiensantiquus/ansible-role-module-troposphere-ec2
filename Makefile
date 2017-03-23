GIT_COMMIT=$(shell git rev-parse HEAD)
MY_DIR=$(shell basename $(CURDIR))
TEST_LABEL_KEY=ansible-role-testing
PLATFORM=ubuntu
define DOCKER_BODY
RUN apt-get update && apt-get install -y \\
      gcc \\
      git \\
      python-dev \\
      python-pip \\
      libffi-dev \\
      libssl-dev \\
			zip && \\
    pip install -U distribute boto ansible==2.2.1 virtualenv awscli psycopg2
    # ansible 2.1.0 fail: https://github.com/ansible/ansible/issues/16015
ARG ANSIBLE_OPTIONS
ARG TEST_LABEL
ARG TEST_LABEL_KEY
ARG TEST_TAG
ARG GIT_COMMIT=unknown
LABEL $$TEST_LABEL_KEY=$$TEST_LABEL
LABEL git-commit=$$GIT_COMMIT
LABEL TEST_TAG=$$TEST_TAG
ADD tests /tmp/playbook
ADD . /tmp/playbook/roles/$$TEST_LABEL
WORKDIR /tmp/playbook
RUN pip install -r test_requirements.pip && \\
    ansible-playbook $$ANSIBLE_OPTIONS -i inventory test.yml -e ec2_subnet_id=${SUBNET_ID} -e ec2_ami=${EC2_AMI} -e ec2_key_name=${EC2_KEY} -e ec2_sgs=${EC2_SGS}
endef
export DOCKER_BODY

%4: TEST_TAG = 14.04
%6: TEST_TAG = 16.04

.PHONY: default
default: test16

testv%: ANSIBLE_OPTIONS = -vvvv
test%:
	( echo 'FROM ${PLATFORM}:${TEST_TAG}' ) > tests/Dockerfile.${PLATFORM}.${TEST_TAG}
	echo "$$DOCKER_BODY" >> tests/Dockerfile.${PLATFORM}.${TEST_TAG}
	docker build --build-arg TEST_LABEL=${MY_DIR} \
	  --build-arg TEST_LABEL_KEY=${TEST_LABEL_KEY} \
	  --build-arg GIT_COMMIT=${GIT_COMMIT} \
	  --build-arg TEST_TAG=${TEST_TAG} \
          --build-arg ANSIBLE_OPTIONS=${ANSIBLE_OPTIONS} \
	  --force-rm -t ${MY_DIR}:${TEST_TAG} -f tests/Dockerfile.${PLATFORM}.${TEST_TAG} .
remove%:
	docker rmi $(shell docker images -q --filter label=TEST_TAG=${TEST_TAG} --filter label=${TEST_LABEL_KEY}=${MY_DIR})
	rm tests/Dockerfile.${PLATFORM}.${TEST_TAG}
clean .IGNORE: remove14 remove16
all: test14 test16
