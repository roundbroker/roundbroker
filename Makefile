
build:
	docker build -t nginx-nchan:1.0 -f nchan/dockerfile .

deploy:
	docker deploy -c nchan/stack.yml turntable
