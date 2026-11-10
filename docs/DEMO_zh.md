# 安装、运行及导师演示手册

## 1. 第一次安装

打开 PowerShell 或 VS Code 的 Terminal。将项目放在 D 盘。下面路径是示例；实际克隆路径不同就修改 `Set-Location`。

```powershell
Set-Location D:\CodexWork
git clone https://github.com/fkgm12138/label-efficient-support-ticket-classification.git
Set-Location .\label-efficient-support-ticket-classification
& D:\anaconda\python.exe bootstrap.py
& .\.venv\Scripts\python.exe -m pip check
& .\.venv\Scripts\python.exe verify_results.py
```

需要 **Python 3.12 64 位**，不需要 GPU。`D:\anaconda\python.exe` 是本机现有解释器；其他电脑可用 `py -3.12 bootstrap.py`。安装会创建项目自己的 `.venv`，把缓存和临时目录放在项目内。在线安装需要访问 PyPI；仓库不附带 Python、虚拟环境或离线 wheel 包。依赖已经锁定版本。

若保留了之前下载的离线包，可运行：

```powershell
& D:\anaconda\python.exe bootstrap.py --wheelhouse 'D:\你的离线包目录\wheelhouse'
```

离线 wheel 要与 Windows x64、Python 3.12 匹配。不要把整套虚拟环境从别的电脑直接复制过来。

## 2. 会前准备（一次训练，反复演示）

```powershell
& .\.venv\Scripts\python.exe run.py --mode baseline --output outputs/demo-01
& .\.venv\Scripts\python.exe demo.py --models outputs/demo-01 --text "I lost my bank card. How can I freeze it?"
& .\.venv\Scripts\python.exe demo.py --models outputs/demo-01 --web
```

浏览器打开 **http://127.0.0.1:8765**。最后一条命令会持续运行，这是正常状态；服务运行时不要关闭该终端。结束时按 `Ctrl+C`。如果提示端口占用，加 `--port 8766`，并打开对应地址。

`baseline` 会训练全训练池模型并完成校准，不会重跑主动学习40次训练和 Cleanlab 的交叉验证。这个界面是新整理的展示入口，不代表已经建立真实客服业务系统，也不代表低预算主动学习与复核策略已完成整合。

再次训练须更换目录，例如 `outputs/demo-02`。程序拒绝覆盖已有非空目录。

## 3. 现场演示顺序（建议约 6–8 分钟）

| 顺序 | 打开什么 / 做什么 | 可以怎样解释 |
|---|---|---|
| 1 | README 与 `docs/METHODS.md` | “研究目标是固定标注数量下如何学习分类，以及怎样识别需要复核的预测。当前数据是77类英文银行意图。” |
| 2 | 本地网页，点击“丢失银行卡”后分析 | “文本先转换成 TF-IDF 特征，再由逻辑回归预测意图。概率最高的类别是模型建议。” |
| 3 | 查看候选集合与概率列表 | “MAPIE 结合独立校准集生成候选集合；集合只有一个标签时保留单个建议，否则建议复核。单标签也可能错。” |
| 4 | 点击“含糊问题”，再分析 | “观察当前模型的实际输出。不要预先承诺这个句子一定触发复核；如果只返回单标签，也应如实展示。” |
| 5 | 打开 `reference_results/learning-curve.png` 和 `active-learning-runs.csv` | “随机抽样和 margin 抽样共享每个种子的起点，比较308、616、1232、2464条训练标签下的验证效果。均值提升并不代表每次都赢。” |
| 6 | 打开 `reference_results/label-review-queue.csv` | “Cleanlab 用训练池内五折的样本外预测找出可疑标签。队列全是 pending，不能说已证实错标。” |
| 7 | `docs/RESULTS.md` 与本次 `run-status.json` | “这里区分现有证据、运行检查和下一步实验；官方测试分数尚未计算。” |

如果老师问“输入一句话怎么知道对不对”：示例没有新人工真值，只展示行为；正式效果来自带真值的验证集。概率、候选集合与验证准确率是不同概念。英文模型不能保证中文输入的分类效果。

## 4. 完整复现实验

```powershell
& .\.venv\Scripts\python.exe run.py --mode full --output outputs/full-01
& .\.venv\Scripts\python.exe verify_results.py --results outputs/full-01
& .\.venv\Scripts\python.exe -m unittest discover -s tests -v
& .\.venv\Scripts\python.exe tests/smoke_demo.py --models outputs/full-01
```

完整流程：数据审查 → 固定划分 → 全训练池基线 → 独立校准 → 五个种子×两种策略×四个预算，共40次训练 → Cleanlab五折审查 → 绘图及结果核对。运行时间取决于电脑；现场优先用会前训练好的模型。

输出在 `outputs/full-01`：

- `baseline.json` / `validation-predictions.csv`：准确率、F1及逐条验证预测。
- `active-learning-runs.csv` / `paired-differences.csv` / `learning-curve.png`：学习曲线与配对差值。
- `selection-种子-策略.json`：每轮已选样本ID，可以追溯抽样过程；并未保存每个主动学习模型权重。
- `conformal.json` / `conformal-per-class.csv`：覆盖、复核、单标签错误率及每类情况。
- `cleanlab-audit.json` / `label-review-queue.csv`：可疑标签统计与待人工审查队列。
- `split/split-manifest.csv`：本次实际划分。
- `run-status.json` / `independent-verification.json` / 两个 `.log`：步骤退出码和检查记录。
- `baseline-model.joblib` / `conformal-model.joblib`：本机训练得到的演示模型。

`reference_results` 是保留的历史参考结果；`outputs` 才是你刚跑出来的结果。不要把参考结果误称为本次新实验。

## 5. VS Code 操作

打开仓库文件夹，按 `Ctrl+Shift+P` → `Python: Select Interpreter` → 选择本项目 `.venv\Scripts\python.exe`。`Ctrl+Shift+B` 执行默认的“Train demo baseline”，也可在 Terminal → Run Task 中选完整实验、结果检查或演示。任务直接调用项目 `.venv`，不需要激活脚本，不会误用 WindowsApps Python。

## 6. 常见问题

| 现象 | 原因及处理 |
|---|---|
| `No module named cleanlab/mapie/skactiveml` | 当前解释器不是项目 `.venv`，或安装未完成。用完整 `.venv\Scripts\python.exe` 命令，并运行 `bootstrap.py`、`pip check`。 |
| `Output directory is not empty` | 为保护已有结果而停止。换 `outputs/full-02` 等新目录。 |
| `Train first` / 没有 `outputs/latest.json` | 先执行 baseline 或 full 训练，再指定 `--models`。仓库不提交已训练的 joblib。 |
| 安装找不到某个锁定版本 / 网络失败 | 核对 Python3.12、平台、PyPI连通性，或使用之前的匹配 wheelhouse；保留错误信息，不要随意升级依赖后声称精确复现。 |
| 页面访问不了 | 保持服务终端开启；使用命令打印的 localhost 地址；端口冲突时改端口。 |
| 服务终端没有退出 | 正常，网页服务正在等待请求。按 `Ctrl+C` 停止。 |

## 7. 汇报时保留的事实边界

1,232只是训练标签；加上1,499验证和1,499校准标签，共4,230开发标签。尚未证明总标注成本减少。单一划分的五个种子不是外部验证。界面展示77类意图，不含真实部门映射、SLA或客服处理时间。322个是候选，不是已确认错误。导师认可、创新性和成绩均不能由代码运行成功推导。
