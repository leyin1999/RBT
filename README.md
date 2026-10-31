# RBT Navigation — 项目结构升级说明

> **V2 目录调整提案**：在保留原有第一阶段可运行离线程序的基础上，新增医学导航软件、图谱、配准、机器人只读通信、相机、仿真与仿体传感研究的模块边界。以下原有第一阶段指南继续有效。

- [系统架构与模块边界](docs/architecture.md)
- [24 周开发路线](docs/roadmap-24-weeks.md)
- [坐标系和单位约定](docs/coordinate_frames.md)
- [安全与适用范围](docs/safety.md)
- [Slicer 软件模块入口](apps/slicer_extension/RBTNavigation/README.md)

**当前状态**：新增目录仍是占位骨架，不表示 Slicer UI、ANTs 配准或 Webots 模型已经实现。原来的 `python -m rbt.app` 和 `tests/test_offline.py` 不变。

---

# RBT：Mercury A1 + Gemini 215 第一阶段骨架

目标：在设备未完全接入时，先跑通“采集 → 视觉点 → 坐标变换 → 安全检查 → 记录 → 回放”。相机安装于机械臂末端，采用 Eye-in-Hand。

本包是可运行的离线最小实现与后续开发设计。Mock 只模拟接口数据，不是 Mercury A1 的运动学、动力学或精度仿真。已有 PyBullet 概念 demo 后续接入适配层，无须重做场景。本包未读取伙伴的源码，尚未完成代码合并。

第一阶段真实设备仅做连接、状态读取与采集；示例中没有硬件运动指令。真实钻孔、注射、自动工具切换执行不进入第一阶段。

## Windows 快速启动

建议 Windows 10/11 x64、Python 3.10 x64、Git。以下命令在 PowerShell 的项目根目录执行；直接使用虚拟环境解释器，无需更改系统执行策略。

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m rbt.app
.\.venv\Scripts\python.exe -m rbt.app --fault camera
.\.venv\Scripts\python.exe -m rbt.app --fault stale
.\.venv\Scripts\python.exe -m rbt.app --fault disconnect
.\.venv\Scripts\python.exe -m rbt.app --fault bounds
```

正常运行应打印 `decision=preview`、`point_B_m=[0.12, 0.2, 0.85]`（允许浮点尾差）、`motion_sent=false`，退出码 0。故障注入应打印 `blocked`，退出码 2，这是预期结果。每次运行生成独立的 `data/runs/<run_id>/`，含配置快照和 events.jsonl。

复制终端实际打印的日志路径进行回放：

```powershell
.\.venv\Scripts\python.exe -m rbt.app --replay data/runs/<run_id>/events.jsonl
```

回放仅展示保存的事件，不连接设备；完整 RGB-D 离线重算属于任务 P4。

## 当前目录与实现状态

```text
RBT/
  README.md
  pyproject.toml
  config/sim.json
  src/rbt/
    contracts.py           # Frame、RobotState、只读设备协议
    geometry.py            # SE(3) 检查与坐标变换
    devices/mock.py        # 虚拟相机、虚拟七关节状态
    vision.py              # 合成像素与深度反投影
    calibration.py         # 已知手眼变换夹具，尚非标定求解器
    safety.py              # 软件拦截、故障锁存与显式复位
    recording.py           # JSONL 记录、事件回放
    app.py                 # 串联流程、故障注入、命令行
  tests/test_offline.py
  docs/phase1-design.md
  .github/workflows/offline.yml
```

自动生成且不提交：`.venv/`、`data/runs/`、`data/raw/`、`config/local.json`。正式采集数据、MRI/NIfTI、完整视频和厂商 SDK 不直接提交公开仓库。开源许可证由仓库所有者选择后再加入。

## 依赖分层

| 层级 | 依赖 | 用途与安装时机 |
|---|---|---|
| 当前运行必需 | Python 3.10、NumPy | 无设备离线流程；NumPy 的宽范围是兼容声明，不是锁定文件 |
| 测试 | Python unittest | 已包含在标准库 |
| 视觉/手眼任务 | opencv-contrib-python | ChArUco 与 calibrateHandEye；只安装一种 OpenCV wheel，勿与 opencv-python 并装 |
| 机械臂只读接入 | pymycobot | 核对实际控制器、服务端与协议后安装；不预设 IP、COM 或端口 |
| 相机只读接入 | Orbbec SDK v2 对应的 Python Wrapper | 从官方发布选择适配 Windows x64、CPython 3.10 的 wheel，核对固件兼容性；不要猜包名 |
| 后续概念场景 | PyBullet | 复用已有 demo；离线主流程不依赖它 |

硬件依赖单独建立 `requirements-hardware.lock.txt`，在真实机器验证后固定准确版本、SDK/固件和 wheel 来源。当前未提供该锁文件，避免伪造已验证组合。正式离线环境首次验证后用 `python -m pip freeze` 保存环境快照；不要把 Linux 环境快照冒充 Windows 锁定结果。

## 设计与任务

模块边界、坐标与时间契约、手眼验证方案、首批任务和验收标准见 [docs/phase1-design.md](docs/phase1-design.md)。

## 官方资料（核对日期：2026-10-26）

- [Mercury A1 Socket 开发](https://docs.elephantrobotics.com/docs/Mercury_A1_en/6-SDKDevelopment/6.1-Python/6.1.3-TCPIP.html)：文档支持 MercurySocket；示例地址端口不是本项目实测参数。只读采集脚本不得照搬 power_on。
- [Orbbec SDK v2](https://github.com/orbbec/OrbbecSDK_v2)：Gemini 215 走 v2 路线。
- [Orbbec Python Wrapper](https://github.com/orbbec/pyorbbecsdk)：按对应 v2 文档/发布选择 wheel。
