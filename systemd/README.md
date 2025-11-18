mjpeg_server systemd unit

このディレクトリには `mjpeg_server.py` を systemd サービスとして動かすためのテンプレートユニットファイルが含まれます。

インストール手順（例）

1. ユニットファイルを `/etc/systemd/system/` にコピー（root 権限が必要）:

```bash
sudo cp systemd/mjpeg_server.service /etc/systemd/system/mjpeg_server.service
```

2. systemd をリロードしてサービスを有効化・起動:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now mjpeg_server.service
```

3. 動作確認とログ確認:

```bash
sudo systemctl status mjpeg_server.service
sudo journalctl -u mjpeg_server.service -f
```

カスタマイズ

- `User=` をサービスを動かしたいユーザ名に変更してください（デフォルトは `hdtk7897`）。
- 仮想環境を使っている場合は `ExecStart` を仮想環境の python に書き換えてください。例:
  `/home/hdtk7897/venv/bin/python /home/hdtk7897/manage_aquarium/python/mjpeg_server.py`
- ポートを変更した場合は `aquarium_api/main.py` 側の `CAMERA_URL` も合わせて更新してください。

注意点

- サービスは Picamera2 とカメラドライバ（Raspberry Pi のカメラ機能）が有効な環境でのみ正常に動作します。
- 開発中で物理カメラがないマシンでは起動に失敗します。開発用にモックサーバを用意するか unit を無効化してください。
