[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/KabiTaro/sample-product/blob/main/LICENSE.txt)
![CI-CD(https://github.com/KabiTaro/sample-product/actions?query=workflow%3ACI-CD)](https://github.com/KabiTaro/sample-product/workflows/CI-CD/badge.svg)
[![Maintainability](https://api.codeclimate.com/v1/badges/aed639878ec5c4ae4523/maintainability)](https://codeclimate.com/github/KabiTaro/sample-product/maintainability)

![image](https://user-images.githubusercontent.com/48993782/103092545-ea6d2100-463a-11eb-9178-3e7f94733030.png)

## 技術書典10発行:ConoHaで作る個人Webサービス-CI/CD完備の激安アーキを構築する-
![image](https://user-images.githubusercontent.com/48993782/103092627-31f3ad00-463b-11eb-983b-0ff72e624a2d.png)

 CI/CD完備のWebサービスの開発フローの雛形の構築を目指します。プロダクトコードのmainブランチへの変更をGitHubにpushする事で自動的にユニットテスト・カバレッジの計測(計測レポートは静的サイトとして出力され、閲覧する事ができます)・本番環境へのデプロイが実施されます。
 アプリケーションのDockerイメージはConoHaオブジェクトストレージを参照領域としたプライベートなレジストリでリポジトリ管理します。
 また、内部エラーがあった際はSentryにエラー追跡情報が送信され、解像度の高いトラブルシューティングが可能になります。