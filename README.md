# 盘中估值 + 本地自选板块工具

最小体量实现：3个核心脚本 + 文件持久化。

## 快速启动

```bash
# 安装依赖
pip install fastapi uvicorn pydantic

# 启动服务
cd intraday_valuation
python app.py
# 或
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

服务运行在 `http://localhost:8000`

## 文件结构

```
intraday_valuation/
├── app.py           # API入口
├── core.py          # 估值计算 + state管理
├── providers.py     # 持仓抓取 + 行情获取
├── data/
│   └── state.json   # 用户板块+基金持久化（自动生成）
├── cache/           # 持仓缓存（自动生成）
├── pyproject.toml
└── README.md
```

## API 接口

### 1. State 管理

#### GET /v1/state
读取全部状态（板块+基金列表）

**响应示例：**
```json
{
  "version": 1,
  "updated_at": "2026-01-31 12:57:00",
  "sectors": [
    {
      "name": "有色金属",
      "funds": [
        {"code": "017193", "alias": "天弘有色"},
        {"code": "000001", "alias": ""}
      ]
    },
    {
      "name": "半导体",
      "funds": [{"code": "012345", "alias": ""}]
    }
  ]
}
```

#### POST /v1/state
覆盖保存状态

**请求示例：**
```bash
curl -X POST http://localhost:8000/v1/state \
  -H "Content-Type: application/json" \
  -d '{
    "sectors": [
      {
        "name": "有色金属",
        "funds": [
          {"code": "017193", "alias": "天弘有色"}
        ]
      }
    ]
  }'
```

**响应：**
```json
{"success": true, "message": "保存成功"}
```

---

### 2. 估值接口

#### GET /v1/valuation/{fund_code}
单基金估值

**请求示例：**
```bash
curl http://localhost:8000/v1/valuation/017193
```

**响应示例：**
```json
{
  "fund_code": "017193",
  "asof_time": "2026-01-31 14:30:00",
  "holdings_asof_date": "2024-12-31",
  "estimation_change": -1.2345,
  "confidence": 0.85,
  "coverage": {
    "stock_total_weight": 94.52,
    "covered_weight": 90.12,
    "residual_weight": 4.40,
    "missing_tickers": ["688xxx"]
  },
  "notes": [
    "残差权重4.40%按0处理",
    "缺失1只股票行情",
    "持仓日期: 2024-12-31"
  ]
}
```

#### POST /v1/valuation/batch
批量估值

**请求示例：**
```bash
curl -X POST http://localhost:8000/v1/valuation/batch \
  -H "Content-Type: application/json" \
  -d '{"fund_codes": ["017193", "000001"]}'
```

**响应：**
```json
{
  "items": [
    {"fund_code": "017193", "estimation_change": -1.23, ...},
    {"fund_code": "000001", "estimation_change": 0.56, ...}
  ]
}
```

#### GET /v1/valuation/state
按当前state返回所有基金估值（板块分组）

**请求示例：**
```bash
curl http://localhost:8000/v1/valuation/state
```

**响应示例：**
```json
{
  "updated_at": "2026-01-31 14:30:00",
  "sectors": [
    {
      "name": "有色金属",
      "funds": [
        {
          "fund_code": "017193",
          "alias": "天弘有色",
          "estimation_change": -1.23,
          "confidence": 0.85,
          ...
        }
      ]
    }
  ]
}
```

---

## state.json 结构

```json
{
  "version": 1,
  "updated_at": "2026-01-31 12:57:00",
  "sectors": [
    {
      "name": "板块名称（用户自定义）",
      "funds": [
        {"code": "基金代码", "alias": "用户备注名（可选）"}
      ]
    }
  ]
}
```

---

## 估值说明

- **estimation_change**: 盘中估值涨跌幅（%），基于持仓权重加权计算
- **confidence**: 置信度（0~1），由覆盖率(70%)和持仓时效性(30%)决定
- **coverage**: 覆盖情况
  - stock_total_weight: 股票总仓位
  - covered_weight: 已获取行情的股票仓位
  - residual_weight: 残差仓位（按0处理）
  - missing_tickers: 缺失行情的股票代码

---

## 典型使用流程

1. **首次打开**：`GET /v1/state` → 返回空结构
2. **录入板块和基金**：前端编辑后 `POST /v1/state` 保存
3. **查看估值**：`GET /v1/valuation/state` 一次性获取所有基金估值
4. **二次打开**：直接 `GET /v1/valuation/state` 即可展示
