# SUMO-CARLA-Autoware co-sim 起動手順

# 0. 前提条件
Autoware環境を構築済みであること。
環境構築については、「Autoware1.9.0環境構築ガイド_v1.0.md」を参照。


# 1. リポジトリ

以下のブランチを使用する。
このブランチはAutoware Universe(0.52.0)のautoware_carla_interfaceをベースに、CARLA公式のSUMO-CARLAブリッジを盛り込み、fullstack(SUMO-CARLA-Autoware)のco-simを実装したものである。

- ARC: 
https://github.com/NTT-DATA-ARC/autoware_universe/tree/feature/autoware-carla-interface
- 個人: 
https://github.com/hmuraki-dev/autoware_universe/tree/feature/autoware-carla-interface

本ブランチは、Autoware Universe ワークスペース内の次のディレクトリに配置される。

```text
~/autoware.1.9.0/
└── src/
    └── universe/
        └── autoware_universe/      ← GitHubからcloneするリポジトリ
            └── simulator/
                └── autoware_carla_interface/
```

`autoware_carla_interface` は独立したリポジトリではなく、`autoware_universe` リポジトリ配下のパッケージである。

# 2. 実行コマンド

## 2.1 CARLAサーバー起動(ターミナル1)

```bash
cd ~/CARLA
./CarlaUE4.sh
```
コマンドを実行すると、CARLAサーバーが起動し、CARLA(Unreal Engine)の画面が表示される。


## 2.2 マップのロード(ターミナル2)

```bash
cd ~/CARLA/PythonAPI/util
python3 config.py --map Town01
```
コマンドを実行すると、CARLAで読み込まれているマップが Town01 に切り替わる。CARLA画面が Town01 の地図に更新されたことを確認する。

Town05・Town10HDを使うときは、`--map`だけを変える。2.4.1の起動コマンドも、同じTownのものを使う。

```bash
# Town05
python3 config.py --map Town05
```

```bash
# Town10HD
python3 config.py --map Town10HD
```


### 2.3 ビルド(ターミナル3)

#### 通常のビルド(推奨)

```bash
source /opt/ros/humble/setup.bash
cd ~/autoware.1.9.0
colcon build --packages-select autoware_carla_interface --symlink-install
```

#### 初回ビルド・依存関係も含める場合

```bash
colcon build --packages-up-to autoware_carla_interface
```

#### ビルドオプション

| オプション | 内容 | 用途 |
|---|---|---|
| `--packages-select` | 指定パッケージのみビルド | 通常の開発 |
| `--packages-up-to` | 指定パッケージ＋依存パッケージをビルド | 初回・依存変更時 |
| `--symlink-install` | installへコピーせずシンボリックリンクを作成 | Python開発を効率化 |

#### Pythonファイル変更時

- `--symlink-install`あり：通常は**再ビルド不要**
- `--symlink-install`なし：**再ビルド必要**

#### 再ビルドが必要なケース

- setup.py
- setup.cfg
- package.xml
- CMakeLists.txt
- entry_points変更
- C++ソース（.cpp）

#### ビルド後

```bash
source ~/autoware.1.9.0/install/setup.bash
```

### 2.4 SUMO/CARLA/Autoware起動(ターミナル3)

#### 2.4.1 起動コマンド

```bash
source install/setup.bash
export ROS_DOMAIN_ID=33

ros2 launch autoware_launch e2e_simulator.launch.xml \
  simulator_type:=carla \
  map_path:=$HOME/autoware_map/Town01 \
  lanelet2_map_file:=lanelet2_map_with_tl.osm \
  vehicle_model:=sample_vehicle \
  sensor_model:=carla_sensor_kit \
  use_sumo:=true \
  sumo_gui:=true \
  sumo_cfg_file:=/home/divp/CARLA/Co-Simulation/Sumo/examples/Town01.sumocfg \
  tls_manager:=sumo \
  traffic_light.publish:=true \
  sync_vehicle_lights:=true \
  sync_vehicle_color:=true \
  sumo_warmup_time:=600 \
  spawn_point:="267.65,133.49,0.30,0.0,0.0,0.0" \
  spectator_follow:=true \
  2>&1 | tee -i /tmp/autoware_carla.log
```

Town05・Town10HDの起動コマンド(Town01との違いは`map_path`・`sumo_cfg_file`・`sumo_warmup_time`・`spawn_point`の4行):

```bash
# Town05(信号2408の手前にスポーン。2.7.1「Town05」)
ros2 launch autoware_launch e2e_simulator.launch.xml \
  simulator_type:=carla \
  map_path:=$HOME/autoware_map/Town05 \
  lanelet2_map_file:=lanelet2_map_with_tl.osm \
  vehicle_model:=sample_vehicle \
  sensor_model:=carla_sensor_kit \
  use_sumo:=true \
  sumo_gui:=true \
  sumo_cfg_file:=/home/divp/CARLA/Co-Simulation/Sumo/examples/Town05.sumocfg \
  tls_manager:=sumo \
  traffic_light.publish:=true \
  sync_vehicle_lights:=true \
  sync_vehicle_color:=true \
  sumo_warmup_time:=60 \
  spawn_point:="24.71,-51.03,0.30,0.0,0.0,91.5" \
  spectator_follow:=true \
  2>&1 | tee -i /tmp/autoware_carla.log
```

```bash
# Town10HD(信号954の手前にスポーン。2.7.1「Town10HD」)
ros2 launch autoware_launch e2e_simulator.launch.xml \
  simulator_type:=carla \
  map_path:=$HOME/autoware_map/Town10HD \
  lanelet2_map_file:=lanelet2_map_with_tl.osm \
  vehicle_model:=sample_vehicle \
  sensor_model:=carla_sensor_kit \
  use_sumo:=true \
  sumo_gui:=true \
  sumo_cfg_file:=/home/divp/CARLA/Co-Simulation/Sumo/examples/Town10HD.sumocfg \
  tls_manager:=sumo \
  traffic_light.publish:=true \
  sync_vehicle_lights:=true \
  sync_vehicle_color:=true \
  sumo_warmup_time:=60 \
  spawn_point:="30.02,133.95,0.30,0.0,0.0,-179.7" \
  spectator_follow:=true \
  2>&1 | tee -i /tmp/autoware_carla.log
```

- `source install/setup.bash`と`export ROS_DOMAIN_ID=33`はTown01と同じく先に実行しておく。
- `map_path`のフォルダ名(Town05・Town10HD)が、2.2でCARLAに読み込んだマップと同じであること。
- `sumo_warmup_time`は`60`にする。Town05・Town10HDのSUMOのルートは0〜199秒に計200台だけなので、
  Town01と同じ`600`にすると、EGOのスポーン時には車がいなくなっている。
- `lanelet2_map_with_tl.osm`は、2.7.1の「Town05」「Town10HD」の手順で作っておく(重複点を直した地図から作ること)。
- Town10HDは、この起動コマンドで実機確認済み(2026-10-21、2.7.1「Town10HD」)。Town05は地図・SUMOの信号とIDの照合までで、実機確認はまだ(2.7.4)。
- ゴールの置き方は2.7.1の各Townの項を参照(Town05は同じ道路を2回通る場所に置くと経路ができない。
  Town10HDはスポーン地点の先の交差点を抜けた道路5の上、map座標で(-104, -99)付近)。

| オプション | 説明 | 設定例 | デフォルト値(未指定時) |
|-----------|------|--------|--------------------------|
| `simulator_type` | 使用するシミュレータ | `carla` | なし(指定必須) |
| `map_path` | Lanelet2マップ | `$HOME/autoware_map/Town01` | なし(指定必須) |
| `vehicle_model` | 車両モデル | `sample_vehicle` | Launch既定値 |
| `sensor_model` | センサキット | `carla_sensor_kit` | Launch既定値 |
| `use_sumo` | SUMO連携 | `true` | `false` |
| `sumo_cfg_file` | SUMO設定 | `...Town01.sumocfg` | なし |
| `sumo_gui` | GUI表示 | `true` | `false(ヘッドレス)` |
| `sumo_host` | TraCIホスト | `localhost` | `localhost` |
| `sumo_port` | TraCIポート | `8813` | `8813` |
| `sumo_client_order` | クライアント順 | `1` | `1` |
| `tls_manager` | 信号管理 | `sumo` | `none` |
| `sync_vehicle_lights` | 灯火同期 | `true` | `false` |
| `sync_vehicle_color` | 車体色同期 | `true` | `false` |
| `spectator_follow` | EGO車両(role_name=`ego_vehicle_role_name`)にCARLAスペクテーターを自動追従させる | `true` | `false` |
| `spawn_point` | EGOのスポーン位置(CARLA座標、`x,y,z,roll,pitch,yaw`) | `"267.65,133.49,0.30,0.0,0.0,0.0"` | `None`(ランダム) |
| `vehicle_type` | EGOのCARLAブループリント | `vehicle.toyota.prius` | `vehicle.toyota.prius` |
| `sumo_warmup_time` | SUMOだけを先に進める秒数(整数)。0で無効。2.4.2参照 | `600` | `0`(無効) |
| `ego_spawn_front_margin` | EGOスポーン時に必要な前方車とのすき間 [m]。2.4.2参照 | `20.0` | `20.0` |
| `ego_spawn_rear_margin` | EGOスポーン時に必要な後方車とのすき間 [m]。2.4.2参照 | `20.0` | `20.0` |
| `ego_spawn_wait_timeout` | ウォームアップ後に空きを待つ上限秒数(整数)。2.4.2参照 | `60` | `60` |
| `traffic_light.publish` | CARLAの信号状態をAutowareへ直接通知する(カメラの信号認識は起動しない)。2.7参照 | `true` | `false` |
| `lanelet2_map_file` | Autowareが読み込むLanelet2地図のファイル名(`map_path`内)。信号を使うときは2.7.1で作った地図 | `lanelet2_map_with_tl.osm` | `lanelet2_map.osm` |
| `traffic_light.force_green` | 起動時に全信号を緑にして固定する。2.7参照 | `true` | `false` |

- `sumo_gui:=true`のsumo-guiは、起動後に自動でシミュレーションを開始する(`--start`)。Runボタンを押す必要はない。
  また、co-simの終了時にはダイアログを出さずに自動で閉じる(`--quit-on-end`)。
- `spectator_follow:=true`はCARLAスペクテーター(自由視点カメラ)をEGO車両に自動追従させる。
  カメラの距離・高さ・角度(`--distance`/`--height`/`--pitch`/`--rate`)はlaunch引数として
  公開されていないため、細かく調整したい場合はこの引数は使わず`ros2 run
  autoware_carla_interface spectator_follow --distance ... --height ...`のように別ターミナルで
  手動起動すること。
- `lanelet2_map_file`・`traffic_light.publish`の2行は、CARLAの信号状態をAutowareへ直接通知する設定(2.7参照)。
  2.7.1の信号入りの地図(`lanelet2_map_with_tl.osm`)を先に作っておくこと。使わない場合はこの2行を省く(カメラによる信号認識になる)。
- ウォームアップを使わない場合は、`sumo_warmup_time`と`spawn_point`の行を省く(EGOは起動直後にランダムな位置へスポーンされる)。
  `spawn_point`だけを指定すれば、ウォームアップなしで固定位置にスポーンする。
- `2>&1 | tee -i /tmp/autoware_carla.log`はログ保存用(2.4.4のgrepで使う)。不要なら省いてよい。
  `-i`を付けないと、Ctrl+Cで`tee`も終了し、それ以降(終了処理)のログが残らない。

#### 2.4.2 ウォームアップ・EGO安全スポーン

SUMOだけを先に所定時間進めて交通流を作ってから、EGOのスポーン位置の前後が空いたタイミングでEGOをスポーンする機能。
`sumo_warmup_time`に1以上を指定すると有効になり、指定しない(既定の0)場合は従来と同じ動作になる。
設計は`docs/SUMO_CARLA_Autoware_ウォームアップ_EGO安全スポーン_実装計画_v1.0.md`を参照。

- 起動の流れ: Autoware起動 → SUMOだけを`sumo_warmup_time`秒進める(CARLAは止まったまま) →
  その間にSUMOに現れた車両をCARLAへまとめてスポーン → EGOのスポーン位置の前後の空きを判定 →
  空いていなければSUMO・CARLAを1ステップずつ進めて再判定 → 空いたらEGOをスポーン → 通常のco-sim。
- 空きの判定: 同じ車線の前方車・後方車とのすき間(バンパー間の距離)が、それぞれ`ego_spawn_front_margin`・
  `ego_spawn_rear_margin`以上で、かつEGOの予定位置に重なる車両・歩行者がいなければスポーンする。
- EGOがスポーンされるまでは、CARLA上にEGOはおらず、RVizにもEGOは表示されない。
  ログに`[EGO SPAWN]`が出て、RVizにEGOが表示されてから、目的地を設定してAutoを押す(目的地の設定方法は従来と同じ)。
- ROSの時刻(`/clock`)はEGOのスポーン時点から0付近で始まる。ウォームアップ・空き待ちの時間は含まれない。

`sumo_warmup_time`に1以上を指定したときは、次を満たさないと起動時に
`Error: invalid parameters: ...`の1行を出して終了する。

- `use_sumo:=true`であること
- `spawn_point`を`x,y,z,roll,pitch,yaw`の6つの値で指定すること(ランダムスポーンでは判定する位置が決まらないため)
- `tls_manager`が`sumo`または`none`であること(`carla`ではウォームアップ中にSUMOの信号が消えたままになるため使えない)
- 必要距離が0以上、`ego_spawn_wait_timeout`が1以上であること

`ego_spawn_front_margin`・`ego_spawn_rear_margin`・`ego_spawn_wait_timeout`は、Vissim-CARLA-Autoware co-simの
ウォームアップ(`vissim_warmup_time`)と共通のパラメータである。
`autoware_launch`の`e2e_simulator.launch.xml`には、`sumo_warmup_time`を含む4つの引数の宣言・受け渡しを追加している
(`ros2 launch autoware_launch e2e_simulator.launch.xml --show-args`で確認できる)。
なお、宣言がなくてもコマンドラインで指定した値はノードまで届く。届いているかは2.4.4の`[EGO SPAWN CHECK] start:`の行の値で確認できる。

#### 2.4.3 スポーン地点の選び方

空きの判定は「スポーン地点が直線区間にある」ことを前提にしている(曲線では前後車の判定がずれる)。
また、SUMO車両が通る車線でないと、空き待ちの確認にならない。

1. 直線区間のスポーン地点の候補を一覧にする(CARLAサーバーを起動し、Town01を読み込んでおく)。
   前後50 mに交差点がなく、向きの変化が3°未満のCARLAのスポーン地点を表示する。

```bash
python3 - <<'EOF'
import carla
c = carla.Client('localhost', 2000); c.set_timeout(10)
m = c.get_world().get_map()
def yaw_diff(a, b): return abs((a - b + 180) % 360 - 180)
for i, sp in enumerate(m.get_spawn_points()):
    wp = m.get_waypoint(sp.location)
    if wp.is_junction:
        continue
    pts = []
    for d in range(5, 55, 5):
        pts += wp.next(float(d)) + wp.previous(float(d))
    if len(pts) < 20 or any(p.is_junction or yaw_diff(p.transform.rotation.yaw, wp.transform.rotation.yaw) > 3 for p in pts):
        continue
    l, r = sp.location, sp.rotation
    print(f"#{i:3d} road={wp.road_id:3d} lane={wp.lane_id:2d}  spawn_point:=\"{l.x:.2f},{l.y:.2f},{l.z:.2f},{r.roll:.1f},{r.pitch:.1f},{r.yaw:.1f}\"")
EOF
```

2. 候補の中から、SUMOのルートが通り、かつSUMO車両と同じ向きの車線のものを選ぶ。
   road番号が同じでも、対向車線(SUMO車両が通らない)のことがあるので、初回は`spectator_follow:=true`で
   スポーン後にSUMO車両と同じ向きに並んでいるかを目で確認する。
   SUMO車両が出発する道路(Town01では`-19.0.00`・`5.0.00`・`-9.0.00`・`19.0.00`・`2.0.00`・`10.0.00`・`-18.0.00`・`-8.0.00`・`-1.0.00`・`24.0.00`)の
   始点付近は、車両が突然現れるので避ける。

Town01(`rou/Town01.rou.xml`、2026-10-19以降: 入力1・2が各300台/h、多様な経路の入力3〜10が各40台/h、計920台/h)で確認済みの地点:

| 地点 | 用途 | SUMOの車線 | 交通量 | `spawn_point` |
|---|---|---|---|---|
| #37 | 交通量が多い(空き待ちが起きる) | `6.0.00` | 309台/h | `199.95,326.97,0.30,0.0,0.0,180.0` |
| #36 | SUMO車両が来ない(すぐスポーン) | `-6.0.00`(#37の対向車線) | 0台/h | `199.95,330.46,0.30,0.0,0.0,-0.0` |
| #144 | 別の道路で交通量が多い | `1.0.00` | 282台/h | `256.55,2.02,0.30,0.0,0.0,-0.0` |
| #249 | 交通量が少ない | `-4.0.00` | 101台/h | `220.14,133.24,0.30,0.0,0.0,-0.0` |
| — | 信号372の手前(信号状態の直接通知の確認用、2.7参照) | `-19.0.00` | 349台/h | `334.74,263.00,0.30,0.0,0.0,90.0` |

- `sumo_warmup_time:=600`・既定の必要距離での実績: #37は空き待ち13.75秒(シミュレーション時間)でスポーン、#36は待ちなし。
- 上の交通量と空き待ちの実績は、SUMOの信号が2交差点(CARLAの信号360〜362・372〜374)だけだったときの値。
  2026-10-16に全12交差点(CARLAの信号36個)へSUMOの信号を設置した後は信号待ちの渋滞が起きるため、値が変わる。
- 交通量の列は2026-10-19の`rou/Town01.rou.xml`の需要(flowの台数×経路の確率)。SUMO単体で1時間回した通過台数もほぼ同じ
  (`6.0.00`: 304台、`1.0.00`: 273台、`-4.0.00`: 99台)。変更前(入力2か所×600台/h、行き先はすべて`-18.0.00`)は
  1時間後に414台が出発待ちになるほど詰まっていたが、変更後は出発待ち10台・テレポート0回。
  #37は交通量が約半分になったので、空き待ちが起きるかは未確認。`-6.0.00`(#36)は変更後もSUMO車両が通らない。
- `spawn_point`のzにはCARLAの道路の高さ(Town01ではほぼ0〜0.3)を入れる。コード側で+2 mしてスポーンする。

#### 2.4.4 ログの見方

```bash
grep -nE "SUMO WARMUP|EGO SPAWN|EGO spawn gate" /tmp/autoware_carla.log
```

| ログ | 意味 |
|---|---|
| `EGO spawn gate: vehicle.toyota.prius footprint 4.51 x 2.01 m (...), lane width 4.00 m` | 判定に使うEGOの寸法とその出所、車線幅 |
| `[SUMO WARMUP] start: warmup_time=600 s (12000 steps)` | ウォームアップ開始 |
| `[SUMO WARMUP] t=10.0 s vehicles=1 persons=0 (wall 0.3 s)` | 10秒(シミュレーション時間)ごとの進捗。`wall`は実時間 |
| `[SUMO WARMUP] completed: t=600.0 s vehicles=40 ... (wall 19.3 s)` | ウォームアップ終了時の車両数 |
| `[SUMO WARMUP] caught up: carla_spawned=40 sumo_only=0 ...` | CARLAへまとめてスポーンした台数。`sumo_only`はCARLAに対応する車種がなくSUMOにだけいる台数 |
| `[EGO SPAWN CHECK] start: spawn_point=(...) ego=... lane_width=... front_margin=... rear_margin=... wait_timeout=...` | 空き判定の条件(launch引数が届いているかの確認にも使う) |
| `[EGO SPAWN CHECK] t=600.05 front=sumo:in1_A.52/carla:245 clearance=13.0 m rear=... clearance=-1.2 m overlap=... result=WAIT` | 判定結果。前方車・後方車とのすき間、EGOの位置に重なっている車両、`WAIT`/`SAFE`。結果や前後の車両が変わったときと、それ以外は1秒ごとに出る |
| `[EGO SPAWN] t=613.80 s waited=13.75 s spawn_point=(...) vehicles=42` | EGOをスポーンした時刻と空き待ちの時間 |

記録しておく項目(再現性のため): `.sumocfg`とルートファイル(SUMOの乱数シードを含む)、`sumo_warmup_time`・必要距離・
待ち時間上限、`spawn_point`、上の`[SUMO WARMUP] completed`・`[EGO SPAWN CHECK]`(最後のSAFE)・`[EGO SPAWN]`の行。
同じ`.sumocfg`・同じパラメータなら、SUMOの車両の動きは同じになる(開発用PCとLinux機で一致を確認済み)。

#### 2.4.5 試験開始失敗と終了

- `ego_spawn_wait_timeout`秒待っても空かない場合や、空いた後にEGOのスポーンに失敗した場合は、
  `Error: test start failed: ...`(最後の判定結果を含む)を出して後始末し、`autoware_carla_interface`が終了コード1で終了する。
  `autoware_carla_interface`ノードには`on_exit="shutdown"`が付いているので、launch全体(RViz・Autoware)も終了する。
  スポーン地点を変える、`sumo_warmup_time`を変える、`ego_spawn_wait_timeout`を延ばす、などで対処する。
- `sumo_gui:=true`のsumo-guiは、終了時にダイアログを出さずに自動で閉じる(`--quit-on-end`)。
- ウォームアップ中・空き待ち中にCtrl+Cを押すと、EGOをスポーンせずに後始末して終了する。
- Ctrl+Cで終了したときに、最後に`[ERROR] [launch]: Caught exception in launch ...: Cannot shutdown a ROS adapter that is not running`
  が1行出ることがあるが、launch側のメッセージで実害はない。

### 2.5 [appendix] 処理時間計測

```bash
ros2 launch autoware_launch e2e_simulator.launch.xml \
  simulator_type:=carla \
  map_path:=$HOME/autoware_map/Town01 \
  :
  :
  2>&1 | tee -i /tmp/autoware_carla.log
 ```
- `2>&1 | tee -i /tmp/autoware_carla.log` でターミナルログをautoware_carla.logに保存
- `-i`を付けること。付けないと、Ctrl+Cで`tee`も終了し、それ以降(終了処理)のログが残らない

```bash
grep "MAIN_LOOP_PERIOD" /tmp/autoware_carla.log
```
- 例えば、ログに[MAIN_LOOP_PERIOD]タグをつけている場合は、上記のコマンドで対象ログを抽出できます。

### 2.6 歩行者(Pedestrian)同期について

上記のco-sim起動(2.4)には、SUMO側の歩行者(`traci.person`)をCARLA側の`walker.pedestrian.*`
アクターとして反映する歩行者同期が組み込まれている。

- **常時有効(CLI引数・launch引数は無い)**: 車両同期(`sync_vehicle_lights`等)と異なり、
  歩行者同期のON/OFFを切り替える起動オプションは存在しない。SUMO設定(`sumo_cfg_file`)側に
  歩行者(`personFlow`/`person`)のルート・ネットワークが定義されていれば、追加設定なしに
  自動的に同期される。
- **sumo→carla の一方向のみ**: CARLA側でspawnした歩行者をSUMOへ送り返す機能(carla→sumo)は
  実装していない。あくまでSUMOが管理する歩行者をCARLA上に可視化・追従させるための機能である。
- **Z座標補正**: `carla.Walker`アクターのtransform原点はbounding boxの垂直中心にあり、
  SUMOが返す座標は地面(足元)基準のため、そのまま反映すると歩行者が地面に埋まって見える。
  この差分を吸収するため、SUMOの`VAR_HEIGHT`の半分(`sumo_person.extent.z`)をZ座標に
  加算する補正を行っている(`BridgeHelper.get_carla_pedestrian_transform()`)。
- **ログについて**: 歩行者のspawn/update/destroyは`logging.debug()`で出力しているが、本パッケージは
  Pythonの`logging`モジュールに対して`basicConfig`等でレベル設定を行っていないため、
  デフォルト状態では表示されない(ターミナルにはWARNING以上、例えば未対応vclassのため
  blueprintが見つからなかった場合の警告のみが表示される)。spawn/update/destroyの詳細を
  確認したい場合は、`autoware_carla_interface`起動前に`python3 -c "import logging;
  logging.basicConfig(level=logging.DEBUG)"`相当の設定を追加する、または該当箇所に
  一時的なデバッグ出力を追加すること。
- 歩行者用のCARLA walkerブレンプリントは`sumo_integration/data/vtypes.json`の
  `carla_blueprints`に`walker.pedestrian.0001`〜`0051`(`vClass: "pedestrian"`)として
  登録済みであり、追加設定は不要。

### 2.7 CARLAの信号状態をAutowareへ直接通知する

CARLAが管理している信号の状態(赤・黄・青)を、カメラ画像による信号認識を使わずに、
ブリッジ(`autoware_carla_interface`)から`/perception/traffic_light_recognition/traffic_signals`へ
毎tick publishする機能。設計と確認結果は`docs/CARLA_Autoware_信号状態publish_実装計画_v1.0.md`を参照。
`tls_manager:=sumo`のときは、SUMOが決めた信号状態がCARLA経由でそのままAutowareに届く。
Town01のSUMOのnet(`~/CARLA/Co-Simulation/Sumo/examples/net/Town01.net.xml`)には、CARLAの信号36個すべてに対応する信号がある
(設置方法と信号パターンは`~/CARLA/Co-Simulation/Sumo/docs/SUMO-CARLA_co-sim_起動手順.md`の「SUMOの信号(Town01)」を参照)。
Town05のnetにも、CARLAの信号54個すべてに対応する信号がある(同「SUMOの信号(Town05)」、地図は2.7.1の「Town05」)。
Town10HDは、netとルートを作り、CARLAの信号15個すべてに対応する信号を置いた(同「SUMOの信号(Town10HD)」、地図は2.7.1の「Town10HD」)。

#### 2.7.1 信号入りのLanelet2地図を作る(最初に1回)

標準のCARLA用Lanelet2地図(`~/autoware_map/Town01/lanelet2_map.osm`)には信号の情報がないため、
そのままではAutowareが信号で止まらない。CARLAから信号を読み取って地図に追加するツールで、
信号入りの地図を作る。

```bash
# CARLAサーバーを起動し、Town01を読み込んでおく(2.1・2.2)
cd ~/autoware.1.9.0/src/universe/autoware_universe/simulator/autoware_carla_interface
python3 tools/carla_tl_to_lanelet2.py ~/autoware_map/Town01/lanelet2_map.osm --stop-line-forward-offset 6
```

- `--stop-line-forward-offset 6`は、停止線をCARLAの停止位置から車線に沿って6 m前に出す。
  CARLAの停止位置は信号灯の約7 m手前(Town01では6.7〜8.9 m)にあり、そのままだとEGOが交差点のかなり手前で止まるため。
  Town01では、6 m前に出すと停止線から交差点の入口(laneletの終わり)までが0.96〜7.08 m(信号372では2.72 m)になる。
  前に出した停止線がlaneletの外(交差点の中)に出る信号は追加せず、`WARNING: ... not added`を出す。
  Town01でこうならないのは約6.9 mまで。
- 出力は`~/autoware_map/Town01/lanelet2_map_with_tl.osm`(元の地図は変更しない)。すでにある場合は`--force`で上書きする。
- 信号ごとに、信号灯・停止線・信号のregulatory element(IDはOpenDRIVEの信号ID)を追加し、
  交差点手前のlaneletに付ける。Town01では36信号すべてが追加される。
- 出力は元の地図と同じフォルダに置く(CARLAの地図名は`map_path`のフォルダ名から決まるため、
  別のフォルダにすると別の地図を読もうとする)。
- `WARNING: ... not added`が出た信号は、停止位置に合うlaneletが見つからなかったもの、または前に出した停止線がlaneletの外に出たもの。終了コードは2になる。

SUMOのnetと作った地図が、同じCARLAの信号(OpenDRIVEのlandmark ID)を指しているかを確かめる。
`--carla-json`は、`carla_tl_to_lanelet2.py`の`--dump-json`で保存したCARLAの信号(省略できる)。

```bash
python3 tools/check_sumo_lanelet2_tl_ids.py ~/CARLA/Co-Simulation/Sumo/examples/net/Town01.net.xml \
    ~/autoware_map/Town01/lanelet2_map_with_tl.osm --carla-json ~/autoware_map/Town01/carla_tl.json --report-mixed
```

- 最後に`OK`(終了コード0)が出れば、CARLAの全信号がSUMOと地図の両方にある。ずれがあると`NG ...`と、そのIDが出る。
- `--report-mixed`の`INFO ... -> CARLA shows red`は、SUMOの状態の違うリンクが対応していて、CARLAで赤に置き換えられる信号(2.7.4)。
  Town01では360と374。
- Town01以外のTownで、SUMOとLanelet2の両方に信号を置く手順(停止線をずらす量の決め方、交通量の見直し、記録まで)は、
  Claude Codeのスキル`/carla-town-signals`(`.claude/skills/carla-town-signals/SKILL.md`)にまとめてある。

**Town05**(2026-10-19に作成):

```bash
# 地図はTown01と同じ配布元(CARLA autoware-contents の vector_maps/lanelet2/Town05.osm)を
# ~/autoware_map/Town05/lanelet2_map.osm に置く。点群も同じ配布元の point_cloud_maps/Town05.pcd(y軸反転版)を
# pointcloud_map.pcd に置く。map_projector_info.yaml は「projector_type: Local」。
# 配布元の地図は境界線に同じ位置の点が続くので、先に直す(下の「重複点」。元の地図は .orig に残す)。
cp ~/autoware_map/Town05/lanelet2_map.osm ~/autoware_map/Town05/lanelet2_map.osm.orig
python3 tools/fix_lanelet2_duplicate_points.py ~/autoware_map/Town05/lanelet2_map.osm.orig \
    ~/autoware_map/Town05/lanelet2_map.osm
# CARLAサーバーでTown05を読み込んでおく(2.2の--mapをTown05にする)。2回目からは--dump-jsonの代わりに--from-json。
python3 tools/carla_tl_to_lanelet2.py ~/autoware_map/Town05/lanelet2_map.osm \
    --dump-json ~/autoware_map/Town05/carla_tl.json --stop-line-forward-offset 0 --group-id-offset 100000
python3 tools/check_sumo_lanelet2_tl_ids.py ~/CARLA/Co-Simulation/Sumo/examples/net/Town05.net.xml \
    ~/autoware_map/Town05/lanelet2_map_with_tl.osm --carla-json ~/autoware_map/Town05/carla_tl.json \
    --report-mixed --group-id-offset 100000
```

- 信号は54個(landmark 2376〜2434)。多車線のため、停止位置ごとに1つ、計111個のregulatory elementができる。
  OpenDRIVEのID(+100000)を持つのは各信号の最初の1つだけなので、2.7.2の位置の対応付け(既定)で使う。
  照合ツールは、同じ信号灯を共有するregulatory elementを1つの信号として数える
  (`Lanelet2: 54 traffic lights in 111 regulatory elements`)。結果は`OK`、`INFO`(赤に置き換えられる信号)はなし。
- `--group-id-offset 100000`: 付けないと、地図の既存のID(2376など)とぶつかって止まる。
- `--stop-line-forward-offset 0`: Town05では、CARLAの停止位置がもともと交差点の入口の1.3〜8.1 m手前(中央値6.8 m、
  CARLAの道路で測った値)にあり、Town01で6 m前に出した後と同じくらいなので、前に出さない。
  laneletがTown01より手前で終わるため、1 mでも`WARNING: ... not added`が出る(2395。3 mで4か所、6 mで45か所)。
- 点群に`~/CARLA/HDMaps/Town05.pcd`を使ってはいけない。CARLAの座標のまま(y軸が反転していない)なので、
  NDTの自己位置がずれ、RVizでEGOが車線をまたいで表示される(2026-10-19に発生)。Town01の`pointcloud_map.pcd`も配布元の版。
- 信号の手前に向かうスポーン地点: 信号2408の手前(SUMOの`-16.0.00`、ルートの17台が通る)
  `spawn_point:="24.71,-51.03,0.30,0.0,0.0,91.5"`。手前の交差点から26 m、CARLAの停止位置まで31 m。
  Town05は交差点の間隔が短く(約60 m)、前後とも30 m以上取れる直線のスポーン地点はない。
  `rou/Town05.rou.xml`は0〜199秒に計200台なので、`sumo_warmup_time`は`60`程度にする(600だと車がいなくなる)。
- **重複点**: 配布元のTown05の地図は、48本のlaneletで境界線の最初の2点が同じ位置にある(Town10HDは10本、Town01はなし)。
  そのままだと、map_loaderが作り直す中心線の先頭がNaNになり、そこを通る経路の長さもNaNになる。
  mission_plannerは空の経路を受け取り、`component_container_mt`(mission_planner_container)が終了コード-11で落ちる。
  RVizで2D Goal Poseを置いても経路ができず、以降のゴールも受け付けない(2026-10-21に発生。信号の有無に関係ない)。
  `tools/fix_lanelet2_duplicate_points.py`で直す。`--check`を付けると直さずに数だけ表示する(重複があれば終了コード1)。
  信号入りの地図を直す前の地図から作った場合は、`lanelet2_map_with_tl.osm`にも同じツールをかければよい。
- ゴールは、同じ道路を2回通らずに行ける場所に置く。スポーン地点(`24.71,-51.03`、南向き)から西側の
  (-153, -3)や(-129, 24)へは約1.6 kmの遠回りになり、途中で同じ道路の隣の車線を通るため、
  `Loop detected within route!`(`The planned route is empty.`)で経路ができない。
  (-44, 50)北向きや(0, 84)東向きは経路ができる(座標はmap座標。mission_plannerだけ起動して確認)。
- 実機(2.7.2)での確認はまだ。

**Town10HD**(2026-10-21に作成):

```bash
# 地図・点群は2026-07-16に置いたもの(Town05と同じ配布元。点群の座標が地図と合うことを確かめた)。
# 配布元の地図は10本のlaneletで境界線に同じ位置の点が続くので、先に直す(元の地図は .orig に残す)。
cp ~/autoware_map/Town10HD/lanelet2_map.osm ~/autoware_map/Town10HD/lanelet2_map.osm.orig
python3 tools/fix_lanelet2_duplicate_points.py ~/autoware_map/Town10HD/lanelet2_map.osm.orig \
    ~/autoware_map/Town10HD/lanelet2_map.osm
# CARLAサーバーでTown10HDを読み込んでおく(2.2の--mapをTown10HDにする)。2回目からは--dump-jsonの代わりに--from-json。
python3 tools/carla_tl_to_lanelet2.py ~/autoware_map/Town10HD/lanelet2_map.osm \
    --dump-json ~/autoware_map/Town10HD/carla_tl.json --stop-line-forward-offset 0 --group-id-offset 100000
python3 tools/check_sumo_lanelet2_tl_ids.py ~/CARLA/Co-Simulation/Sumo/examples/net/Town10HD.net.xml \
    ~/autoware_map/Town10HD/lanelet2_map_with_tl.osm --carla-json ~/autoware_map/Town10HD/carla_tl.json \
    --report-mixed --group-id-offset 100000
```

- 信号は15個(landmark 943〜945・949〜954・957〜962)。どれも2車線で、計30個のregulatory elementができる
  (`Lanelet2: 15 traffic lights in 30 regulatory elements`)。結果は`OK`、`INFO`(赤に置き換えられる信号)はなし。
- `--group-id-offset 100000`: 付けないと、地図の既存のID(943など。最大9690)とぶつかって止まる。
- `--stop-line-forward-offset 0`: CARLAの停止位置は、もともと交差点の入口の0.9〜6.9 m手前(中央値5.4 m、CARLAの道路で測った値)。
  Town05と同じく1 mでも`WARNING: ... not added`が出る(1 mで4か所、3 mで8か所、6 mで24か所)ので、前に出さない。
- SUMOは`examples/Town10HD.sumocfg`を使う(2.4.1の`map_path`・`sumo_cfg_file`のTown01をTown10HDに置き換える)。
  ルートは0〜199秒に計200台なので、Town05と同じく`sumo_warmup_time`は`60`程度にする。
- 信号の手前に向かうスポーン地点: 信号954の手前(CARLAのスポーン地点#80、SUMOの`1_4`、ルートの34台が通る)
  `spawn_point:="30.02,133.95,0.30,0.0,0.0,-179.7"`。CARLAの停止位置まで51 m、手前の交差点から110 m
  (後ろ36 mから先はカーブ)。SUMOの車両の19台がこのedge(`1`)の始点から出発するが、スポーン地点から約110 m後ろ。
  信号954(junction 468)はSUMOで0〜42秒が青、42〜45秒が黄、45〜90秒が赤の繰り返し。
  この車線は交差点を抜けると道路5へ曲がって続くだけなので、ゴールはその先(map座標で(-104, -99)付近、北北西向き)に置く。
- 実機(2.7.2)で確認済み(2026-10-21、利用者が確認。2.4.1のTown10HDの起動コマンド)。
  起動ログは`[EGO SPAWN] t=60.05 s waited=0.00 s`(ウォームアップ60秒、空き待ちなし、そのときのSUMOの車両48台)と
  `Traffic-light matching: 15 matched, 0 ambiguous, 0 too far, 0 overridden (map has 62 heads / 30 groups)`。
  `Different SUMO traffic-light states`は出なかった。

#### 2.7.2 起動

2.4.1の起動コマンド例の次の2行で有効になる。

```bash
  lanelet2_map_file:=lanelet2_map_with_tl.osm \
  traffic_light.publish:=true \
```

- `traffic_light.publish:=true`のときは、カメラによる信号認識(traffic_light_recognition)を起動しない。
  同じトピックに2つのノードがpublishしないようにするため。
- ブリッジは、Autowareが読み込む地図(`map_path`/`lanelet2_map_file`)を読み、CARLAの信号を
  地図の信号に位置で対応付ける。

起動ログで対応付けの結果を確認する。

```bash
grep -nE "Traffic-light matching|Traffic lights|traffic-light|force_green" /tmp/autoware_carla.log
```

| ログ                                                                                                      | 意味                                                                              |
| --------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| `Traffic-light matching: 36 matched, 0 ambiguous, 0 too far, 0 overridden (map has 36 heads / 36 groups)` | 正常。CARLAの36信号すべてが地図の信号に対応付いた                                 |
| `the map has no traffic-light heads; 36 CARLA lights not published`                                       | 地図に信号がない。`lanelet2_map_file:=lanelet2_map_with_tl.osm`を付け忘れている   |
| `ambiguous CARLA light (opendrive_id=...)` / `unmatched CARLA light (...)`                                | その信号は対応付けできず、publishされない。下の`traffic_light.id_map`で指定できる |

#### 2.7.3 オプション

| オプション                     | 説明                                                                                                                                  | デフォルト値                   |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------ |
| `traffic_light.publish`        | CARLAの信号状態をpublishする                                                                                                          | `false`                        |
| `traffic_light.force_green`    | 起動時に全信号を緑にして固定し、終了時に元に戻す。`use_sumo:=true`で`tls_manager`が`sumo`/`carla`のときは指定できない(起動時にエラー) | `false`                        |
| `traffic_light.map_path`       | 対応付けに使うLanelet2地図。空(`""`)にするとOpenDRIVEの信号IDをそのまま使う                                                           | `map_path`/`lanelet2_map_file` |
| `traffic_light.match_distance` | 対応付けを認める信号灯どうしの最大距離 [m]                                                                                            | `5.0`                          |
| `traffic_light.match_ratio`    | 曖昧と判定するしきい値(小さいほど厳しい)                                                                                              | `0.6`                          |
| `traffic_light.id_map`         | 手動の対応付け`opendrive_id:group_id[\|group_id...],...`。位置の対応付けより優先する。`\|`を含むので引用符で囲む                      | `""`                           |

- 状態の対応: CARLAのRed/Yellow/Green → RED/AMBER/GREEN(点灯)、Off → 消灯、それ以外 → UNKNOWN。
- 同じ信号IDに複数のCARLAの信号が対応して状態が違うときは、最も制限の強い状態(赤 > 黄 > 不明 > 消灯 > 青)を出す。

#### 2.7.4 注意点

- **SUMO連携(`tls_manager:=sumo`)では、黄信号もAutowareには赤として届くことがある。**
  1つのCARLAの信号に、状態の違うSUMOの複数のリンク(例: 直進は`G`、右左折は`y`)が対応している場合、
  CARLAの信号は赤になる(既存のSUMO連携の仕様。ログに`Different SUMO traffic-light states ... CARLA state is forced to red.`が出る)。
  Town01で起きるのは、信号パターンを手で設定した信号360と374だけ。後から設置した30個の信号は、対応するリンクが常に同じ色になる。
- RMWは`~/.bashrc`と同じ`RMW_IMPLEMENTATION=rmw_cyclonedds_cpp`で起動すること。Fast DDSで起動したときは
  ノードどうしの通信が一部できず、Autoを押せる状態にならなかった。
- 実機で確認済みの地図はTown01とTown10HD(Town05は地図と照合まで)。別の地図では、2.7.1のツールが既存のIDとぶつかって止まることがある。
  その場合は`--group-id-offset`(例: `--group-id-offset 100000`)を付け、2.7.2の位置の対応付け(既定)で使う。
