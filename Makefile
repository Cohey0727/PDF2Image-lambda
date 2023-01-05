image_deploy:
	aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin 303391106411.dkr.ecr.ap-northeast-1.amazonaws.com
	docker build -t pdf-to-image .
	docker tag pdf-to-image:latest 303391106411.dkr.ecr.ap-northeast-1.amazonaws.com/pdf-to-image:latest
	docker push 303391106411.dkr.ecr.ap-northeast-1.amazonaws.com/pdf-to-image:latest
