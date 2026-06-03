# E-Ticke CLI

这是一个为 AI Agent 设计的命令行工具，用于根据 JSON 数据生成批量开票的 Excel 文件。

## 使用方法

### 1. 准备输入数据 (JSON)

输入数据应为一个发票对象数组。每个对象包含发票基本信息和明细列表。

**示例 `input.json`:**

```json
[
  {
    "serialNo": "INV001",
    "invoiceType": "普通发票",
    "isTaxIncluded": "是",
    "buyerName": "示例公司",
    "buyerTaxId": "91310000XXXXXXXXXX",
    "items": [
      {
        "name": "技术服务",
        "code": "1060101010000000000",
        "qty": 1,
        "price": 100,
        "amount": 100,
        "taxRate": 0.01
      }
    ]
  }
]
```

### 2. 运行命令

```bash
# 使用文件输入
./e-ticke-cli -input input.json -output invoices.xlsx

# 使用标准输入
cat input.json | ./e-ticke-cli -output invoices.xlsx
```

## 参数说明

- `-input`: JSON 输入文件路径。如果不提供，则从标准输入读取。
- `-output`: 输出的 XLSX 文件路径。默认为 `output.xlsx`。
- `-template`: Base64 编码的模板文件路径。默认为 `../template_base64.txt`。
- `-tax-codes`: 税收分类编码 JSON 文件路径。默认为 `../tax_codes.json`。
- `-list-codes`: 列出前 100 条税收分类编码并退出。
- `-search-codes`: 搜索税收分类编码 (按名称) 并退出。

## 常用操作

### 查询税收编码
AI agent 可以通过以下命令搜索所需的税收编码：
```bash
./e-ticke-cli -search-codes "软件"
```

### 生成发票
```bash
./e-ticke-cli -input input.json -output invoices.xlsx
```

## 发票对象字段说明

| 字段 | 说明 | 示例 |
| :--- | :--- | :--- |
| `serialNo` | 发票流水号 (必填) | `INV20260603001` |
| `invoiceType` | 发票类型 | `普通发票` 或 `增值税专用发票` |
| `isTaxIncluded` | 是否含税 | `是` 或 `否` |
| `buyerName` | 购买方名称 | `上海某某科技有限公司` |
| `buyerTaxId` | 纳税人识别号 | `9131...` |
| `isNaturalPerson` | 自然人标识 | `是` 或 `否` |
| `buyerIdType` | 证件类型 | `居民身份证` 等 (仅自然人为定时有效) |
| `buyerIdNo` | 证件号码 | (仅自然人为定时有效) |
| `buyerNationality` | 国籍 | (仅自然人为定时有效) |
| `buyerAddress` | 购买方详细地址 | |
| `buyerPhone` | 购买方联系电话 | |
| `buyerBankName` | 购买方开户银行 | |
| `buyerBankAccount` | 购买方银行账号 | |
| `remark` | 备注 | |
| `buyerEmail` | 购买方邮箱 | |
| `items` | 明细列表 (数组) | 见下表 |

### 明细行 (Items) 字段

| 字段 | 说明 | 示例 |
| :--- | :--- | :--- |
| `name` | 项目名称 | `咨询费` |
| `code` | 税收分类编码 | `1060101010000000000` |
| `spec` | 规格型号 | |
| `unit` | 单位 | `次` |
| `qty` | 数量 | `1` |
| `price` | 单价 | `100.0` |
| `amount` | 金额 | `100.0` |
| `taxRate` | 税率 | `0.06` (代表 6%) |
