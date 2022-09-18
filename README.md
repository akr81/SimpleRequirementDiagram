# SimpleRequirementDiagram
JSON形式で記述された要求情報を、SysMLの要求図ライクなフォーマットで出力します。
![](./image/sample.png)

## 要求情報(JSONファイル)
要求情報は、以下の情報のリストとして構成されます。  
`sample/requirements.json`が記述のサンプルになっていますので、必要に応じて参照してください。

|キー|値フォーマット|可能な値|説明|
|:--:|:--:|--|--|
|type|string|usecase<br>requirement<br>block<br>rationale<br>problem|要求図のモデル要素を指定します。|
|id|string|Any|モデル要素のID|
|title|string|Any|モデル要素のタイトル(*1)|
|text|string|Any|モデル要素の説明(*1)|
|unique_id|string|Any|モデル要素を一意に表す文字列(*2)|
|relations|list|-|モデル要素間の接続関係を表す<br>下記kind, to, noteのみもつことが可能|
|kind|string|refine<br>deriveReqt<br>contains<br>satisfy<br>None|モデル要素間の接続関係を表す<br>Noneはrationale, problemのみ可能|
|to|string|Any|モデル要素の接続先を指定する<br>unique_idのみ指定可能|
|note|string|Any|モデル要素間の接続に対してrationaleまたはproblemのモデル要素を関連付ける<br>rationale, problemのunique_idのみ指定可能|
(*1) markdown形式のリンク文字列`[string](link)`が使用可能
(*2) 後述するVSCodeのスニペットで入力可能

### VSCodeスニペット
要求情報の入力を補助するためのスニペットを`json_snippet.json`に格納しています。  
jsonファイルへのユーザスニペットとしてコピー&ペーストしてください。  
以下の入力を行います。

|名称|ショートカット|説明|
|--|--|--|
|Add new requirement|a|relations以外の要求情報テンプレートを出力します<br>unique_idとして、現在日時が自動的に入力されます|
|Add datetime as unique id|u|現在日時を出力します<br>unique_idのみを更新する場合に利用します|
|Add new relation|r|relasionsのリストに格納する接続関係情報テンプレートを出力します|

## 要求図出力
