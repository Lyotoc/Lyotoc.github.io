---
name: e-ticke-cli-helper
description: 用于生成批量开票 XLSX 的独立工具。集成自行车业务默认配置（1%税率、含税金额），内置命令行工具。
---

# E-Ticke CLI 助手 (独立版)

本技能提供了一套完整的、独立于 Web 界面的发票生成方案。它包含了核心业务规则、税收编码参考以及用于执行任务的命令行工具。

## 核心业务规则 (必须遵守)

在处理自行车及其零配件业务时，必须应用以下默认配置：
1. **税率**：统一使用 `0.01` (1%)。
2. **含税标识**：默认含税金额 (`isTaxIncluded: "是"`)。
3. **发票类型**：默认 `"普通发票"`。
4. **自然人标识**：默认非自然人 (`isNaturalPerson: ""`)。

## 资源说明

该技能目录包含执行任务所需的所有组件：
- **工具**：`scripts/e-ticke-cli` (Go 编写的二进制文件)。
- **素材**：
  - `assets/template_base64.txt`: Excel 导入模板。
  - `assets/tax_codes.json`: 官方税收分类编码表。
- **参考**：[references/json-format.md](references/json-format.md) 包含了详细的 JSON 格式示例。

## 操作指南

### 1. 查找或验证税收编码
使用内置工具搜索自行车相关编码：
```bash
./scripts/e-ticke-cli -tax-codes ./assets/tax_codes.json -search-codes "自行车"
```

### 2. 准备数据
按照 [references/json-format.md](references/json-format.md) 中的示例准备 JSON 文件（例如 `invoices.json`）。

### 3. 生成 Excel 文件
调用工具并指定本地素材路径：
```bash
./scripts/e-ticke-cli \
  -template ./assets/template_base64.txt \
  -tax-codes ./assets/tax_codes.json \
  -input invoices.json \
  -output 2026_自行车开票.xlsx
```

## 注意事项
- 工具运行在技能目录内或通过绝对路径调用。
- 请确保输入的商品金额与数量、单价的计算逻辑一致（含税）。
