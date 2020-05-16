DOCKER_TAG=${shell git rev-parse HEAD}
DOCKER_IMAGE="butecoopensource/postman:${DOCKER_TAG}"

docker: docker-build docker-push

docker-build:
	docker build -t "${DOCKER_IMAGE}" .

docker-push:
	docker push "${DOCKER_IMAGE}"

docker-tag:
	echo "${DOCKER_TAG}"

test: docker-build 
	docker run -it --rm --env-file .env "${DOCKER_IMAGE}"
