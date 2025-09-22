IMAGE_NAME := st-grabriel-workshop
IMAGE_TAG := latest
REGISTRY ?= ameengwxo
PROJECT_NAME := st-grabriel-workshop
SECRET_NAME := st-grabriel-secret

.PHONY: build push

build_tag_push:
	podman buildx build --platform linux/amd64 -t $(IMAGE_NAME):$(IMAGE_TAG) .
	podman push $(IMAGE_NAME):$(IMAGE_TAG) $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)

login:
	ibmcloud login --apikey F66P5rljWFnkvqsbeSYkh1kRnUj3unn1sqp8iolGPGGQ -r us-south
	ibmcloud target -g itz-wxo-68977ca7fbf8f4f78fdf00
	ibmcloud ce project select --id 7000decf-aa43-4301-9e54-2501324f24cb

create_secret:
	ibmcloud ce secret create --name $(SECRET_NAME) --from-env-file .env
	
get_secret:
	ibmcloud ce secret get --name $(SECRET_NAME)

create:
	ibmcloud ce application create --name st-grabriel-workshop --cpu 2 --memory 4G --es 4G --min-scale 1 --env-from-secret $(SECRET_NAME) -v public \
		--image docker.io/$(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG) \
		--port 8000 \
		--registry-secret $(SECRET_NAME)

update:
	ibmcloud ce application update --name st-grabriel-workshop --cpu 2 --memory 4G --es 4G --min-scale 1 --env-from-secret $(SECRET_NAME) -v public \
		--image docker.io/$(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG) \
		--port 8000 \
		--registry-secret $(SECRET_NAME)
