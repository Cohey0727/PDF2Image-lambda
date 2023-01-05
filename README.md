＃ `PDF`を画像に変換する`Lambda`を構築する

## 概要

## `Docker Image`をビルドする

```sh
docker build ./ -t pdf-to-image
```

## `Docker`の中で動作確認

```sh
docker run -it pdf-to-image bash
$ python main.py
$ ls outputs
```

```sh
aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws/m1u1m5o0
```

## S3 からファイルをロード

```

```
