# mirrorlist-injector.py #

__このスクリプトで実現しようとしていたことは，*.repoを下のように設定すると実現できるようです．．． (2013-01-03)__

    baseurl=http://unofficial.example.jp/.../
    mirrorlist=https://mirrors.fedoraproject.org/metalink?...

Yum(Yellowdog Updater Modified)において，公式ミラーリストに含まれていないミラーサーバを公式ミラーと同様に扱えるようにするものです．

## ユースケース ##

Fedoraの公式リポジトリ(fedora, update)からのダウンロードに，普段は`unofficial.example.jp`を使いたい．だが，`unofficial.example.jp`は公式ミラーリストに含まれていない．そのため，`/etc/yum.reposd/{fedora,fedora-update}.repo`に`unofficial.example.jp`に関する設定を行わなければならない．

`baseurl`に

    baseurl=http://unofficial.example.jp/.../
            http://official.example.com/.../

のように書けば解決するものの，リストアップした全てのサーバが利用できない場合を考える必要がある(上の例ならば，2つのサーバが同時に利用できなくなった場合，リポジトリへのアクセスができなくなる)．

・・・というような状況を想定しています．

## 使い方 ##

2点，準備を行う必要があります．

- `mirrorlist-injector.py`の設置&編集
- `/etc/yum.repos.d/*.repo`の編集

### mirrorlist-injector.pyの設置&編集 ###

+ `mirrorlist-injector.py`を，wsgiが使える環境に設置
    - お試しならば，`python mirrorlist-injector.py`を実行するとlocalhostで動きます
+ `mirrorlist-injector.py`内の`repos`を編集

### /etc/yum.repos.d/*.repoの編集 ###

+ ミラーサーバを利用したいホスト上の*.repoファイルを編集
    - `mirrorlist=`を，設置した`mirrorlist-injector.py`のURLに変更します
    - e.g. `mirrorlist=https://www.example.com/mirrorlist-injector/metalink?repo=fedora-17&arch=x86_64`
+ `yum clean metadata`を実行
