# CARLA-Autoware: 信号状態の直接publish(Publishing CARLA Traffic-Light States) 実装計画 v1.0

対象ブランチ: `feature/carla_traffic_light_publish`(`feature/sumo_co-sim` から分岐)

参照仕様: Autoware公式ドキュメント
<https://autowarefoundation.github.io/autoware_universe/main/simulator/autoware_carla_interface/>
の「Publishing CARLA Traffic-Light States」

---

## 0. 目的・スコープ

CARLAが管理している信号機の状態(赤・黄・青)を、カメラ画像による認識処理を介さずに、
Autowareへ直接通知する。

- 出力トピック: `/perception/traffic_light_recognition/traffic_signals`
- 型: `autoware_perception_msgs/msg/TrafficLightGroupArray`
- 周期: 毎tick
- 信号の内容: 1つのCARLA信号を、形がCIRCLEの信号1つとして出す

| CARLAの状態            | color     | status    |
| ---------------------- | --------- | --------- |
| Red                    | RED       | SOLID_ON  |
| Yellow                 | AMBER     | SOLID_ON  |
| Green                  | GREEN     | SOLID_ON  |
| Off                    | (UNKNOWN) | SOLID_OFF |
| 上記以外(Unknown など) | UNKNOWN   | UNKNOWN   |

### 0.1 パラメータ(公式ドキュメントに合わせる)

| パラメータ                      | 既定値  | 内容                                                                            |
| ------------------------------- | ------- | ------------------------------------------------------------------------------- |
| `traffic_light.publish`         | `False` | CARLAの信号状態をpublishする                                                    |
| `traffic_light.force_green`     | `False` | 起動時に全信号を緑にしてfreezeする                                              |
| `traffic_light.map_path`        | `""`    | 位置マッチングに使うLanelet2の `.osm` のパス                                    |
| `traffic_light.match_distance`  | `5.0`   | マッチを認める信号灯どうしの最大距離 [m]                                        |
| `traffic_light.match_ratio`     | `0.6`   | 曖昧と判定するしきい値(小さいほど厳しい)                                        |
| `traffic_light.id_map`          | `""`    | 手動での対応付け `opendrive_id:group_id[\|group_id...]`。マッチングより優先する |
| `map_origin_x` / `map_origin_y` | `0.0`   | CARLAの原点からAutowareの地図原点までのずれ。位置マッチングでも使う             |

### 0.2 グループIDの決め方(優先順)

1. `traffic_light.id_map` に書かれていれば、それを使う。書式が不正なものは警告して読み飛ばす。
2. `traffic_light.map_path` があれば、位置マッチングを行う。CARLAの各信号灯を地図上で一番近い
   信号灯に対応付け、その信号灯を参照するすべてのregulatory elementのIDでpublishする。
   次の場合は対応付けずにログへ出し、publishしない。
   - 別の信号の信号灯がほぼ同じ距離にある(`match_ratio` で判定)
   - 2つの信号灯がまったく同じ距離にある
   - `match_distance` 以内に信号灯がない
3. 上のどちらもない場合は、OpenDRIVEの信号IDをそのままグループIDとして使う。

起動時のログに、マッチできた数・曖昧な数・遠すぎた数を出す。

---

## 1. 事前調査で分かったこと

1. **ローカルのLanelet2地図に信号の情報が入っていない。**
   `~/autoware_map/Town01`・`Town10HD` の `lanelet2_map.osm` には `lanelet`(subtype=road)
   しかなく、信号のregulatory element・信号灯のlinestring・停止線がいずれも0件。
   このままでは位置マッチングの照合先がなく、Autowareの計画側(traffic_lightモジュール)も
   反応しない。公式ドキュメントのKnown Issuesにも同じことが書かれている。
   → 地図に信号を追加するツール(T2)を作る。
2. CARLA 0.9.15 の `carla.TrafficLight` に、必要なAPIがそろっている:
   `get_opendrive_id()`、`get_light_boxes()`、`get_stop_waypoints()`、
   `get_affected_lane_waypoints()`、`freeze()`、`state`。
3. SUMO連携(`sumo_integration/carla_simulation.py`)に、landmark IDから信号actorを引く処理と、
   freeze/解除の処理がすでにある。`tls_manager=sumo` のときはCARLAの信号がSUMOに合わせて
   動くので、CARLAの状態をpublishすれば、SUMOが決めた信号状態もAutowareに届く。
4. `autoware_launch`(別リポジトリ)の `e2e_simulator.launch.xml` に、コミットされていない
   変更(Vissim用の引数など)がある。カメラ認識の停止は
   `tier4_perception_component.launch.xml` の `use_traffic_light_recognition` で行える。

---

## 2. タスク一覧

| #   | タスク                                                                            | 主な変更先                                                                                                               | 状態                                 |
| --- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | ------------------------------------ |
| T0  | ブランチ作成と計画書の保存                                                        | `docs/`                                                                                                                  | ✅ 完了                              |
| T1  | 座標系の確認(CARLAの座標、`pose()` の `map` 座標、osmの `local_x/local_y` の関係) | 調査のみ                                                                                                                 | ✅ 完了(Town01)                      |
| T2  | 地図に信号を追加するツール                                                        | `tools/carla_tl_to_lanelet2.py`、`test/test_carla_tl_to_lanelet2.py`(新規)                                               | ✅ 完了(Town01)                      |
| T3  | 信号publishのロジック(ROSに依存しない部分)                                        | `modules/traffic_light_matcher.py`(upstreamから移植)、`modules/traffic_light_publisher.py`(新規)                         | ✅ 完了                              |
| T4  | ROSパラメータとpublisherの追加                                                    | `carla_ros.py`、`carla_autoware.py`(起動時チェック)                                                                      | ✅ 完了                              |
| T5  | 毎tickのpublish                                                                   | `carla_ros.py`(`run_step()`)                                                                                             | ✅ 完了                              |
| T6  | `force_green` と排他チェック、終了時の解除                                        | `carla_autoware.py`                                                                                                      | ✅ 完了                              |
| T7  | launchの引数追加、カメラ認識の停止                                                | `autoware_carla_interface.launch.xml`、`e2e_simulator.launch.xml`(autoware_launch)                                       | ✅ 完了(autoware_launchは未コミット) |
| T8  | 単体テスト                                                                        | `test/test_traffic_light_matcher.py`(upstreamから移植)、`test/test_traffic_light_publisher.py`、`test/conftest.py`(新規) | ✅ 完了                              |
| T9  | 実機での確認                                                                      | –                                                                                                                        | 未着手                               |
| T10 | ドキュメント(起動手順書、README)                                                  | `docs/`、`README.md`                                                                                                     | 未着手                               |

進める順番: T0 → T1 → T3+T8 → T4/T5 → T6 → T2 → T7 → T9 → T10

T2が終わる前でも、`id_map` を使うか、IDが一致する仮の地図を使えば、トピックが出ることまでは
確かめられる。T2は座標の確認(T1)に左右され、作業量も読みにくいので、独立したStepとして扱う。

---

## 3. 各タスクの内容

### T1: 座標系の確認

- 地図上の数か所で、CARLAの座標、`pose()` がpublishする `map` 座標
  (`carla_location_to_ros_point`、y反転)、osmの `local_x/local_y` を比べる。
- y反転と原点のずれの有無を確定し、`map_origin_x/y` の既定値0.0がTown01・Town10HDで正しいか確かめる。

#### 結果(2026-10-16、CARLA 0.9.15、Town01)

- **`map_x = carla_x`、`map_y = -carla_y`(y反転のみ、原点のずれなし)。** `map_origin_x/y` の
  既定値0.0のままで正しい。`pose()`(`carla_location_to_ros_point`)の変換とも一致する。
  - 確かめ方: CARLAの車線中心のwaypoint(20 m間隔、370点)をy反転してosmに重ね、
    いずれかのlaneletの左右境界の間に入るかを調べた。全点で「左境界までの距離+右境界までの
    距離 = 車線幅(4.0 m)」となり、誤差は0.01 m未満だった。y反転しない場合は大きくずれる。
- osmのnodeは `ele` がすべて0.0。CARLAの道路の高さもほぼ0なので、信号灯の高さはCARLAの
  z座標をそのまま使ってよい。
- osmのIDの最大値: node 3522、way 3534、relation 3539。T2で追加する要素は、これと
  ぶつからないIDにする。
- Town01の信号: actorは36個で、OpenDRIVE IDはすべて異なる。どの信号も、信号灯
  (`get_light_boxes()`)が1つ、停止位置(`get_stop_waypoints()`)が1つ。
  `get_group_traffic_lights()` で、同じ交差点の信号のまとまりが取れる(例: 360・361・362)。
- 補足: CARLAが同期モードのまま一度もtickされていないと、`get_actors()` が空になる。
  T2のツールでは、最初に1回tickしてからactorを取得する。
- Town10HDは、CARLAの地図を切り替える必要があるため未確認。使うときに同じ方法で確かめる。

### T2: 地図に信号を追加するツール

CARLAに接続し、信号ごとに次を作ってosmに追記する。

- `get_light_boxes()` の各信号灯 → `traffic_light` linestring(高さは信号灯の箱から決める)
- `get_stop_waypoints()` → `stop_line` linestring(車線の幅で作る)
- `get_affected_lane_waypoints()` → 規制を受けるlaneletを特定し(位置と向きで照合)、
  `regulatory_element`(subtype=traffic_light、`refers`=信号灯、`ref_line`=停止線)を作る。
  laneletには `regulatory_element` の参照を追加する。
- regulatory elementのIDには、OpenDRIVEの信号IDを数値にして入れる。これで位置マッチングと
  OpenDRIVE IDの代替の両方が使え、確認もしやすくなる。既存の要素とIDがぶつかる場合は
  エラーにする。
- 出力は別ファイル(例: `lanelet2_map_with_tl.osm`)にし、元の地図は書き換えない。

#### 結果(T2)

- `tools/carla_tl_to_lanelet2.py` を追加した。CARLAに接続して信号を読み取り、Lanelet2地図に
  次を追加して別ファイルに書き出す(元の地図は変更しない)。
  - 信号灯: 信号灯の箱の下辺を `traffic_light` linestring(`subtype=red_yellow_green`、
    `height`=箱の高さ)にする。中点が信号灯の中心になるので、ブリッジの位置マッチングの
    照合点と一致する。
  - 停止線: 停止位置(`get_stop_waypoints()`)を通り、車線の幅で進行方向に直交する `stop_line`。
  - regulatory element: `type=regulatory_element`、`subtype=traffic_light`。
    メンバーは `refers`(信号灯)と `ref_line`(停止線)。IDはOpenDRIVEの信号ID
    (`--group-id-offset` を加える)。
  - 停止位置を含み、向きが同じ(45度以内)laneletに、regulatory elementへの参照を追加する。
    Autowareの traffic_light モジュールは、regulatory elementを持つlaneletごとにシーンを作り、
    信号状態をregulatory elementのIDで引く(`scene.cpp`)ので、手前の1つのlaneletで足りる。
  - `light_bulbs` は作らない。Autowareでは矢印信号の判定にしか使わない(`manager.cpp`)。
- 新しいnodeの `lat/lon` は、入力の地図の既存nodeから求めた比例係数で付ける
  (Town01・Town10HDとも、lon ≈ 8.974e-6 × local_x、lat ≈ 9.035e-6 × local_y)。
- 安全のためのチェック: OpenDRIVE IDが既存のIDとぶつかる場合、地図にすでに信号の
  regulatory elementがある場合は、エラーで止まる(Lanelet2のIDは種類をまたいで一意)。
  停止位置に合うlaneletがない場合は警告して、終了コード2を返す。
- 1つの信号に停止位置が複数ある場合は、停止位置ごとにregulatory elementを作る。OpenDRIVEの
  IDを持つのは最初の1つだけなので、この場合は `traffic_light.map_path`(位置マッチング)が必要。
- 単体テスト `test/test_carla_tl_to_lanelet2.py` を追加した(14件。全体でROSなし67件成功・
  1件スキップ)。`--from-json`(`--dump-json` で保存したデータ)を使えば、CARLAなしでも動く。

使い方:

```bash
# CARLAで地図(Town01)を読み込んだ状態で実行する
python3 tools/carla_tl_to_lanelet2.py ~/autoware_map/Town01/lanelet2_map.osm
# -> ~/autoware_map/Town01/lanelet2_map_with_tl.osm
```

出力は元の地図と同じフォルダに置く(CARLAの地図名はフォルダ名から決まるため)。Autowareには
`lanelet2_map_file:=lanelet2_map_with_tl.osm`、ブリッジには
`traffic_light.map_path:=<フォルダ>/lanelet2_map_with_tl.osm` で渡す(T7で起動引数に反映する)。

#### 実機での確認(2026-10-16、CARLA 0.9.15、Town01)

| 確認                       | 結果                                                                                                                           |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| ツールの実行               | 36信号すべてについてregulatory elementを追加。36個とも別々のlaneletに付いた                                                    |
| Lanelet2(Python)で読み込み | エラー0件。TrafficLightが36個、どれも停止線と信号灯1つを持つ                                                                   |
| 停止線の位置               | どれもlaneletの終わり(交差点の入口)から7〜13 m手前                                                                             |
| 位置マッチング(ブリッジ)   | 「36 matched、0 ambiguous、0 too far」。どの信号も自分のOpenDRIVE IDに対応し、ずれは1 µm未満。別の信号の信号灯までは最短18.6 m |
| トピック                   | 36グループがpublishされた                                                                                                      |

- 生成した地図は `~/autoware_map/Town01/lanelet2_map_with_tl.osm` に置いた(T9で使う)。
- Town10HDは未確認(CARLAの地図の切り替えが必要)。Town10HDの既存IDは1から始まるので、
  OpenDRIVE IDとぶつかる場合は `--group-id-offset` を使う。

### T3: 信号publishのロジック

ROSとCARLAに依存しない部分を、単体テストできるように分ける。

- CARLAの状態から `TrafficLightElement` 相当への変換(0章の表)
- `id_map` の解析
- osmを読み、信号灯(`traffic_light` linestring)とregulatory elementの対応表を作る
- 位置マッチング(`match_distance`・`match_ratio`、同じ距離の場合の扱い)
- グループIDの決め方(0.2の優先順)と、起動時のログ(マッチ・曖昧・遠すぎの件数)

#### 結果(T3)

- **upstreamに同じ機能がすでにあった。** autowarefoundation/autoware_universe の main
  (commit `8c41273b3`、#13327「publish CARLA traffic-light states, matched to the map by
  position」)。公式ドキュメントの説明はこの実装に対応する。
- 位置マッチングと `id_map` の解析は、upstreamの `modules/traffic_light_matcher.py` を
  **変更せずに移植**した(将来upstreamに追従しやすくするため)。テスト
  `test/test_traffic_light_matcher.py` も同様。
- upstreamでは `carla_ros.py` の中にある次の処理を、ROSにもCARLAにも依存しない
  `modules/traffic_light_publisher.py` に分け、単体テストできるようにした。
  - `carla_state_to_element()`: CARLAの状態(または状態名)→ `(color, status)`
  - `carla_head_map_point()`: 信号灯の箱の中心の平均 → 地図座標(`x + origin_x`、`-y + origin_y`)
  - `resolve_traffic_light_groups()`: グループIDの決め方(`id_map` → 位置マッチング → OpenDRIVE ID)
  - `resolution_report()`: 起動時ログの文面(マッチ・曖昧・遠すぎ・上書きの件数と警告)
  - `build_group_states()`: グループIDごとにまとめた状態(ID順)
- **upstreamとの違い**
  - 同じグループIDに複数のCARLA信号が対応し、状態が食い違う場合: upstreamは後から処理した
    信号の状態になる(actorの順番しだい)。本実装は**最も制限の強い状態**を出す
    (赤 > 黄 > 不明 > 消灯 > 青)。
  - 地図に信号灯が1つもない場合(標準のTown01など)、起動時ログで警告する。
  - `TrafficLightElement` の定数は、ROSなしでimportできるようにモジュール内に持つ。
    ROS環境ではテストでメッセージ定義と一致することを確かめる。
- 実データでの確認(T1で取得したTown01の36信号): 地図なしでは36信号すべてがOpenDRIVE IDで
  publish対象になる。現在のTown01の地図を指定すると、0件マッチと警告になる(想定どおり。T2が必要)。

#### 結果(T8)

- テストの実行方法(ROSなしでも、ROSをsourceした環境でも動く):
  `python3 -m pytest test/test_traffic_light_matcher.py test/test_traffic_light_publisher.py`
- `test/conftest.py`: `modules/__init__.py` がROSをimportするため、ROSがない環境では
  パッケージの `__init__.py` を実行せずに純粋なモジュールだけを読み込む。
- 結果: ROSなしで41件成功・1件スキップ(メッセージ定義との照合)。ROSをsourceした環境で
  42件すべて成功。

### T4: ROSパラメータとpublisher

- 0.1のパラメータを `carla_ros.py` の `_initialize_parameters()` に追加する。
- `traffic_light.publish=true` のときだけ、`TrafficLightGroupArray` のpublisherを作る。

### T5: 毎tickのpublish

- `world.tick()` とSUMO同期のあとに状態を集め、シミュレーション時刻をstampにしてpublishする。
- 信号の対応付けは起動時に1回だけ行い、毎tickは状態の読み出しだけにする。

#### 結果(T4/T5)

- `carla_ros.py`
  - パラメータ `traffic_light.publish`・`force_green`・`map_path`・`match_distance`・
    `match_ratio`・`id_map` を追加した(名前と既定値はupstreamと同じ)。
  - `traffic_light.publish=true` のときだけ、`TrafficLightGroupArray` のpublisher
    (`/perception/traffic_light_recognition/traffic_signals`、depth 1、reliable)を作る。
  - `run_step()` の最後(`ego_status()` の後)で `_publish_traffic_lights()` を呼ぶ。
    `run_step()` は直前にtickしたフレームを処理するので、状態はそのフレームのもの、
    stampはそのフレームのシミュレーション時刻になる。SUMO連携時は、SUMOが
    `sync_sumo_to_carla()` で設定した状態が、次のtickの後にpublishされる。
  - 信号の対応付けは、最初にpublishするtickで1回だけ行う。
  - `traffic_light.map_path` が読めない場合(壊れたosmなど)はエラーログを出し、何もpublishしない。
- `carla_autoware.py`: 起動時のパラメータチェック `_check_traffic_light_params()` を追加した
  (中身は `traffic_light_publisher.validate_traffic_light_params()`)。`map_path` が
  ファイルでない、`match_distance <= 0`、`match_ratio` が (0, 1] の外、のいずれかで起動を止める。
- T7の一部を前倒しした: `autoware_carla_interface.launch.xml` に引数を追加した(実機確認のため)。
  `match_distance`・`match_ratio` は、整数で指定してもDOUBLEになるよう `float()` を通す。
- **`map_origin_x/y` は追加しない。** ローカルの `pose()`・`initialpose` は原点のずれに
  対応しておらず、信号だけにずれを入れると座標がそろわなくなる。Town01では0で正しい(T1)。
  必要になったら、`pose()` などと合わせて別のタスクで対応する。
- 対応付けできた信号が1つもない場合は、メッセージをpublishしない(upstreamと同じ)。

#### 実機での確認(2026-10-16、CARLA 0.9.15、Town01、Autowareなしでブリッジ単体を起動)

| 条件                                                                    | 結果                                                                                                                                             |
| ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `traffic_light.publish:=true`、`"traffic_light.id_map:=360:9000\|9001"` | 起動ログ「35信号をOpenDRIVE IDで、1信号をid_mapで」。トピックに37グループ(9000・9001あり、360なし)。毎tickのpublish、stampはシミュレーション時刻 |
| 同上で、40秒間CARLAの状態と比較                                         | 315回中314回一致(1回はtickの最中に比べたため)。12グループで 青→黄→赤 の変化を確認                                                                |
| `traffic_light.map_path:=` Town01の `lanelet2_map.osm`                  | 「0 matched」と「地図に信号灯がない」警告。ブリッジは動き続け、トピックは出ない(T2が必要)                                                        |
| `traffic_light.map_path:=/no/such.osm`                                  | 起動時に「is not a file」のエラーで停止                                                                                                          |

- 実機確認で見つけた不具合を修正した: rclpyでは、同じ呼び出し箇所から重要度の違うログを
  出すと例外になる(`Logger severity cannot be changed between calls`)。起動時ログを
  infoとwarningで別の呼び出し箇所にした。
- `id_map` の値に `:` や `|` を含めても、launchから文字列のまま渡ることを確認した
  (`|` を含むので、コマンドラインでは引用符で囲む)。

### T6: force_green

- 起動時に全信号を緑にしてfreezeする。終了時の解除は、既存のSUMO用の解除処理と共通化する。
- `tls_manager=sumo/carla` との同時指定は、既存の排他チェック
  (`_check_sumo_traffic_manager_exclusivity()` など)と同じ形で、起動時にエラーにする。

#### 結果(T6)

- `carla_autoware.py`
  - `_force_green_traffic_lights()`: `traffic_light.force_green=true` のとき、ワールドの設定
    (同期モードなど)を反映した直後に、全信号を緑にしてfreezeする。SUMOとの接続やEGOの
    スポーンより前に行う。
  - `_cleanup_forced_green()`: 終了処理(`_cleanup()`)で、freezeした信号を解除する。解除の後、
    信号のまとまり(`get_group_traffic_lights()`)ごとに1回 `reset_group()` を呼び、交差点の
    周期を元に戻す。呼ばないと、まとまりの中の信号が全部緑のまま解除される。
  - SUMO用の解除処理(vendor版 `CarlaSimulation.close()`)とは共通化しなかった。vendorの
    コードには手を入れない方針で、`close()` はfreeze解除だけで `reset_group()` をしないため。
- 起動時のチェック: `use_sumo=true` かつ `tls_manager` が `sumo` または `carla` のときは、
  `force_green` を指定すると起動を止める。
  - `sumo`: SUMOが毎ステップCARLAの信号を上書きするので、緑に固定できない。
  - `carla`: 全部緑のCARLAの信号がSUMOに反映され、SUMOの車が交差点で衝突する。
  - `tls_manager=none`、またはSUMOを使わない場合は指定できる。
- 単体テストを7件追加した(合計54件成功・1件スキップ)。

#### 実機での確認(2026-10-16、CARLA 0.9.15、Town01、ブリッジ単体)

| 条件                                                               | 結果                                                                                                                                                          |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `traffic_light.publish:=true traffic_light.force_green:=true`      | 起動ログ「36信号を緑にしてfreeze」。25秒間で189メッセージ、すべてのグループがGREEN/SOLID_ON。CARLA側も36信号すべて緑・freeze中                                |
| 上記を停止した後                                                   | ログ「36信号のfreezeを解除、12グループをreset」。CARLAを20秒(400tick)進めて、freezeは0件、どのまとまりでも緑か黄の信号は常に1つ以下、状態が変化することを確認 |
| `use_sumo:=True tls_manager:=sumo traffic_light.force_green:=true` | 起動時にエラーで停止(SUMOに接続する前)                                                                                                                        |

### T7: launch

- `autoware_carla_interface.launch.xml` に0.1の引数を追加する。
  `traffic_light.map_path` が空のときは、既存の `map_path` から `lanelet2_map.osm` のパスを
  作る案を検討する。
- `e2e_simulator.launch.xml`(autoware_launch)から引数を渡す。`publish=true` のときは
  `use_traffic_light_recognition` を止め、同じトピックに2つのノードがpublishしないようにする。
- autoware_launchのコミットされていない変更と分けてコミットするかは、この時点で決める。

#### 結果(T7)

- `autoware_carla_interface.launch.xml`
  - `traffic_light.*` 引数はT4で追加済み。
  - `traffic_light.publish=true` のときは、カメラの信号認識向けのノード
    (`traffic_light_image_relay`・`traffic_light_camera_info_relay`・`traffic_light_republish`)を
    起動しない。CAM_FRONTの画像を毎フレーム変換・publishする負荷がなくなる。
- `e2e_simulator.launch.xml`(autoware_launch)
  - `traffic_light.*` の6つの引数を追加し、`autoware_carla_interface.launch.xml` に渡す。
  - `traffic_light.map_path` の既定値は `$(var map_path)/$(var lanelet2_map_file)`
    (Autowareが読み込むのと同じ地図)。Autowareが信号を引くregulatory elementと、ブリッジが
    対応付けるregulatory elementが必ず同じ地図のものになる。`""` を指定するとOpenDRIVE IDを
    そのまま使う。
  - `traffic_light.publish=true` のときは `<let name="use_traffic_light_recognition" value="false">`
    で、カメラによる信号認識(`perception.launch.xml` の traffic_light_recognition グループ)を
    起動しない。このグループだけが `/perception/traffic_light_recognition/traffic_signals` を
    publishするので、publisherがブリッジだけになる。`autoware.launch.xml` はこの引数を渡さないが、
    launchの設定値はincludeに引き継がれ、`<arg default=...>` より優先されることを小さなlaunchで
    確かめた。
- **autoware_launchへの変更はコミットしていない。** autoware_launchはブランチのないdetached
  HEADで、SUMO・Vissim用の変更もコミットせずに作業ツリーに置いている。それに合わせた。
  今回追加した差分は次のとおり(作業ツリー上の既存の変更に対する差分)。

```diff
--- a/e2e_simulator.launch.xml
+++ b/e2e_simulator.launch.xml
@@ -84,6 +84,26 @@
   <arg name="pointcloud_map_file" default="pointcloud_map.pcd" description="pointcloud map file name"/>
   <!-- Perception -->
   <arg name="traffic_light_namespace" default="[traffic_light]" description="traffic light recognition namespace"/>
+  <!-- CARLA traffic-light state publishing (only used when simulator_type is 'carla'; see
+       autoware_carla_interface/docs/CARLA_Autoware_信号状態publish_実装計画_v1.0.md).
+       With traffic_light.publish, autoware_carla_interface publishes the CARLA traffic-light states on
+       /perception/traffic_light_recognition/traffic_signals, so the camera-based traffic light
+       recognition is not launched (it would publish on the same topic).
+       For Autoware to stop at the lights, the lanelet2 map needs traffic-light regulatory elements:
+       generate them with autoware_carla_interface/tools/carla_tl_to_lanelet2.py and pass
+       lanelet2_map_file:=lanelet2_map_with_tl.osm. -->
+  <arg name="traffic_light.publish" default="false" description="Publish CARLA traffic-light states instead of running camera-based traffic light recognition (CARLA simulator_type only)"/>
+  <arg name="traffic_light.force_green" default="false" description="Set every CARLA traffic light to green and freeze it there at startup (CARLA simulator_type only)"/>
+  <arg
+    name="traffic_light.map_path"
+    default="$(var map_path)/$(var lanelet2_map_file)"
+    description="Lanelet2 map (.osm) the CARLA traffic lights are matched to by position; defaults to the map Autoware loads. Empty uses the OpenDRIVE signal id as the group id"
+  />
+  <arg name="traffic_light.match_distance" default="5.0" description="Max head-to-head distance (m) accepted when matching a CARLA traffic light to a lanelet2 head"/>
+  <arg name="traffic_light.match_ratio" default="0.6" description="Ambiguity threshold: reject a match when nearest &gt; ratio * second-nearest (different signal). Lower is stricter"/>
+  <arg name="traffic_light.id_map" default="" description="Optional override 'opendrive_id:group_id[|group_id...],...', taking precedence over position matching"/>
+  <!-- Picked up by tier4_perception_component.launch.xml (inherited through autoware.launch.xml). -->
+  <let name="use_traffic_light_recognition" value="false" if="$(var traffic_light.publish)"/>
   <!-- Control -->
   <!-- Vehicle -->
   <arg name="launch_vehicle_interface" default="false"/>
@@ -129,6 +149,12 @@
         <arg name="vehicle_type" value="$(var vehicle_type)"/>
         <arg name="spawn_point" value="$(var spawn_point)"/>
         <arg name="spectator_follow" value="$(var spectator_follow)"/>
+        <arg name="traffic_light.publish" value="$(var traffic_light.publish)"/>
+        <arg name="traffic_light.force_green" value="$(var traffic_light.force_green)"/>
+        <arg name="traffic_light.map_path" value="$(var traffic_light.map_path)"/>
+        <arg name="traffic_light.match_distance" value="$(var traffic_light.match_distance)"/>
+        <arg name="traffic_light.match_ratio" value="$(var traffic_light.match_ratio)"/>
+        <arg name="traffic_light.id_map" value="$(var traffic_light.id_map)"/>
       </include>
     </group>
   </group>
```

#### 確認(2026-10-16)

| 確認                                                               | 結果                                                                                                    |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| `ros2 launch autoware_launch e2e_simulator.launch.xml --show-args` | `traffic_light.*` の6つの引数が表示される。`map_path` の既定値は `map_path` + `/` + `lanelet2_map_file` |
| `<let ... if=...>` が入れ子のincludeに届くか(小さなlaunchで確認)   | `publish:=true` で `false`、`publish:=false` で既定値の `true` になる                                   |
| `autoware_carla_interface.launch.xml traffic_light.publish:=true`  | 信号認識用の3ノードが起動しない。36信号のpublishは動く                                                  |
| 同 `traffic_light.publish:=false`                                  | 3ノードが従来どおり起動する                                                                             |

Autoware全体を起動したときの確認(カメラの信号認識が起動しないこと、赤信号で止まること)はT9で行う。

### T8: 単体テスト

- 状態の変換、`id_map` の解析、マッチング(正常・曖昧・同じ距離・遠すぎ)、OpenDRIVE IDでの代替。
- 既存の `test/stand_ins.py` の方式に合わせ、CARLAなしでも動くようにする。

### T9: 実機での確認

1. `ros2 topic echo /perception/traffic_light_recognition/traffic_signals` で状態とIDを確認する
2. CARLAで信号を手動で変えたとき、トピックも変わる
3. Town01で、赤信号の停止線でEGOが止まり、青で発進する
4. `tls_manager=sumo` で、SUMOの信号とトピックが一致する
5. `force_green` で全信号が緑のまま変わらない

### T10: ドキュメント

- 起動手順書(2.4.1のオプション一覧)に新しい引数を追加する。
- READMEに、地図の作り方と使い方を追記する。
