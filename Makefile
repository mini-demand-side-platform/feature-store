package_name = feature-store
tag = 0.1.0

help:  
	@sed -ne '/@sed/!s/## //p' $(MAKEFILE_LIST)

server-dev: ## start local dev server
	uvicorn feature_store.main:app --reload 

build-dev: ## build image
	docker build -t mini-demand-side-platform/feature-store:dev -f ./docker/Dockerfile .

run-dev: ## run image locally
	docker run -it --rm --network databases_default -p 8000:8000 \
	-e olap_host='postgresql' \
	-e cache_host='redis' \
	mini-demand-side-platform/feature-store:dev