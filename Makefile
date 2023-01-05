deploy-image:
	aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws
	aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin 303391106411.dkr.ecr.ap-northeast-1.amazonaws.com
	docker build -t pdf-to-image .
	docker tag pdf-to-image:latest 303391106411.dkr.ecr.ap-northeast-1.amazonaws.com/pdf-to-image:latest
	docker push 303391106411.dkr.ecr.ap-northeast-1.amazonaws.com/pdf-to-image:latest
