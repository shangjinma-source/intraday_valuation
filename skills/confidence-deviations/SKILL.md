---
name: confidence-deviations
description: |
  每日收盘后运行批处理任务，计算基金估值 vs 净值偏差，更新置信度。
  自动记录偏差历史到 confidence_deviations.json，用于后续置信度校准。
---

# Confidence Deviations - 置信度偏差计算

## 功能说明

每日收盘后（22:00）执行的批处理任务，主要功能：

1. **批量估值计算** - 加载 state.json 中所有基金代码，计算实时估值
2. **偏差记录** - 对比盘中估值与收盘净值，记录偏差到 `confidence_deviations.json`
3. **置信度校准** - 基于历史偏差中位数，校准每只基金的置信度

## 文件结构

```
skills/confidence-deviations/
├── SKILL.md                    # 技能文档
├── scripts/
│   ├── cron_job.py            # 主脚本（每日批处理入口）
│   ├── run_cron.bat           # Windows 批处理包装器
│   ├── create_schedule.py     # 创建 Windows 定时任务脚本
│   └── test_batch.py          # 测试脚本
└── docs/
    └── cron_log.txt           # 执行日志
```

## 使用方法

### 手动执行

```bash
cd E:\Git\valuation_grid\skills\confidence-deviations\scripts
python cron_job.py
```

### 通过批处理文件

```bash
run_cron.bat
```

### 输出说明

**成功输出：**
```
=== valuation_grid Daily Batch (22:00) ===
Found 368 funds, computing valuations...
Batch completed: 368 success, 0 errors
confidence_deviations.json updated: 363 funds with history
=== Done ===
```

**输出文件：**
- `E:\Git\valuation_grid\data\confidence_deviations.json` - 偏差历史数据
- `E:\Git\valuation_grid\skills\confidence-deviations\docs\cron_log.txt` - 执行日志

## 定时任务配置

### Cron Job (OpenClaw)

**Job ID:** `e8f3a9c2-7d41-4b5e-9f2a-1c8e6b3d5a7f`

**Schedule:** 每天 22:00 (`0 22 * * *`)

**Payload:**
```
派发给 urshifu：运行 valuation_grid 批处理脚本更新置信度：
1. 执行 python E:\Git\valuation_grid\skills\confidence-deviations\scripts\cron_job.py
2. 检查 E:\Git\valuation_grid\data\confidence_deviations.json 是否更新
3. 确认文件包含当天数据和多日统计置信度
4. 如果执行成功，返回：✅ 置信度已更新，处理了 X 只基金
5. 如果执行失败，返回：❌ 置信度更新失败，错误信息：{error}
```

**Timeout:** 600 秒

### Windows 任务计划程序（可选）

使用 `create_schedule.py` 创建 Windows 定时任务：

```bash
python create_schedule.py
```

## 数据格式

### confidence_deviations.json

```json
{
  "001234": [
    {
      "date": "2026-04-02",
      "est": 1.25,
      "nav": 1.23,
      "deviation": 0.02
    },
    ...
  ],
  ...
}
```

**字段说明：**
- `date`: 日期 (YYYY-MM-DD)
- `est`: 盘中估值涨幅 (%)
- `nav`: 实际净值涨幅 (%)
- `deviation`: 偏差绝对值 (|est - nav|)

**保留策略：** 每只基金最多保留 200 条历史记录

## 置信度校准逻辑

基于历史偏差中位数自动调整置信度下限：

| 偏差中位数 | 置信度下限 |
|-----------|-----------|
| < 0.3pp   | 0.85      |
| < 0.5pp   | 0.70      |
| < 1.0pp   | 0.60      |
| ≥ 1.0pp   | 保持原值  |

## 依赖

- Python 3.10+
- `valuation_grid` 项目环境（`.venv`）
- 已启动的 FastAPI 后端（用于获取估值数据）

## 故障排查

### 常见问题

1. **脚本执行失败**
   - 检查后端服务是否运行（端口 8000）
   - 检查 `state.json` 是否存在且格式正确
   - 查看 `cron_log.txt` 获取详细错误信息

2. **偏差数据未更新**
   - 确认执行时间在收盘后（15:05 之后）
   - 检查基金净值数据源是否可用

3. **置信度未校准**
   - 确认 `confidence_deviations.json` 中有足够的历史记录（≥5 条）
   - 检查校准逻辑是否被触发

## 测试

运行测试脚本：

```bash
python test_batch.py
```

## 相关技能

- [`export-valuation-images`](../export-valuation-images/) - 导出估值图片
- [`intraday-cache`](../intraday-cache/) - 盘中估值缓存更新

## 变更日志

- **2026-04-02**: 初始版本，从根目录迁移到 skills 目录
- **2026-04-02**: 添加超时保护（600 秒）
