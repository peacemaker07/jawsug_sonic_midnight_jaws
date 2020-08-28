# jawsug_sonic_midnight_jaws

[JAWS SONIC 2020 & MIDNIGHT JAWS 2020](https://jawssonic2020.jaws-ug.jp/) のセッション用のリポジトリ

## Description


## Requirement

- node 13 以上
- python3.8

## Install

### serverless framework のインストール

```
# Install the serverless cli
npm install -g serverless

# Or, update the serverless cli from a previous version
npm update -g serverless

# 参考
https://serverless.com/framework/docs/getting-started/
```

```
# プラグインをインストール
$ sls plugin install -n serverless-python-requirements
```

### clone

```
$ git clone git@github.com:peacemaker07/jawsug_sonic_midnight_jaws.git
```

※ 本リポジトリをcloneせずにいちから作成したい場合

```
$ serverless create --template aws-python3 --name jawsug-sonic-midnight-jaws --path jawsug_sonic_midnight_jaws
```

### deploy用のprofileを作成

```
$ aws configure --profile [任意のpfofile名(例:jaws_ug)]
AWS Access Key ID [None]: 任意のアクセスキー 
AWS Secret Access Key [None]: 任意のシークレットキー
Default region name [None]: ap-northeast-1
Default output format [None]: json
```

profile名をserverless.ymlの「profile」に設定

```yaml
...
provider:
  name: aws
  runtime: python3.8
...
  profile: jaws_ug
...
```

## Usage

### deploy

```
$ sls deploy -s dev -v
``

### test

ライブラリのインストール

```
$ pip install -r requirements-dev.txt
```

実行

```
$ pytest -v tests/
```
