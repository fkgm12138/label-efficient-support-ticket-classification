# 代码和数据逐项说明

| 文件 | 作用 | 如何使用 |
|---|---|---|
| `bootstrap.py` | 检查Python版本，建立本地虚拟环境，安装锁定依赖 | 首次运行或修复依赖；支持`--wheelhouse` |
| `run.py` | 安排实验、设置D盘本地缓存、拒绝覆盖已有结果、记录状态 | `--mode baseline/full --output outputs/新目录` |
| `src/run_pilot.py` | 固定种子数据清理与划分、TF-IDF逻辑回归、MAPIE、主动学习 | 由`run.py`调用；通过环境变量接收输出目录 |
| `src/analyze_pilot.py` | 仅在训练池内做Cleanlab五折OOF、生成曲线、Gantt及协议检查 | full模式第二步；不属于在线预测 |
| `verify_results.py` | 从实际CSV重算指标、核对数据哈希、划分和抽样ID；有模型时重算候选集合 | 默认检查参考结果，也可`--results outputs/本次目录` |
| `demo.py` | 读取本机模型，对一条文本做预测；启动本地HTTP服务 | `--text`或`--web`，可指定`--models` |
| `demo/index.html` | 网页布局、样例按钮、结果展示 | 通过demo.py提供服务；不能双击HTML代替服务 |
| `tests/test_contracts.py` | 数据哈希与已保存结果检查的自动化入口 | `python -m unittest discover -s tests -v` |
| `tests/smoke_demo.py` | 真实启动本地服务，测试网页、预测API、空输入和未知路径 | 指定本次训练的模型目录 |
| `requirements-lock.txt` | 经既有实验使用的锁定依赖及传递依赖 | 由bootstrap安装；不是任意最新版本 |
| `.vscode/settings.json` | 选定项目虚拟环境 | 文件夹打开VS Code后使用 |
| `.vscode/tasks.json` | 训练/演示/检查任务 | Terminal → Run Task |
| `data/raw/*` | 原始公开数据、来源说明、许可 | 不改原文件；使用哈希核对 |
| `data/processed/split-manifest.csv` | 既有参考划分 | 新运行的划分另存在该次输出目录 |
| `data/source-manifest.json` | 来源固定commit、URL、SHA-256 | verify_results.py自动核对 |
| `reference_results/*` | 历史实验记录及图表 | 没有重跑时也能了解结果；不冒充新结果 |
| `evidence/release-validation.json` | 本次发布版本的运行检查记录 | 阅读验证范围、日期和限制 |
| `evidence/file-manifest.json` | 上传文件的SHA-256清单 | 可核对下载后文件，清单不包含自身 |

生成Word/PDF的旧排版脚本属于个人论文制作流程，依赖私人模板和本机路径，不是本仓库的实验模块。公开仓库只收录复现实验、结果分析、校验和演示所需的完整代码；不上传私人导师录音、对话或论文材料。未完成的Transformer、低预算校准整合、真实客服派单不会作为已完成代码写入。
