＃ `PDF`を画像に変換する`Lambda`を構築する

## 概要

## `Docker Image`をビルドする

```sh
docker build ./ -t pdf-to-image
```

## `Docker`の中で動作確認

```sh
docker run -it pdf-to-image bash
$ python app.py
```

```sh
make image_deploy
```
