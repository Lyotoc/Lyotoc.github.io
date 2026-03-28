
import base64
import os
import json

# 1. 读取模板文件并编码
template_path = '(V251101版)批量开票-导入开票模板.xlsx'
with open(template_path, 'rb') as f:
    template_base64 = base64.b64encode(f.read()).decode()

# 2. 读取已过滤的税收编码 (3324条)
tax_codes = []
if os.path.exists('tax_codes.json'):
    with open('tax_codes.json', 'r', encoding='utf-8') as f:
        tax_codes = json.load(f)

# 3. 整合用户提供的最新 index.html 结构，并注入变量
# 注意：这里使用了双大括号 {{ }} 来转义 Python f-string
html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>批量发票填报系统</title>
    <script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>
    <script src="https://unpkg.com/exceljs/dist/exceljs.min.js"></script>
    <style>
        :root {{ --primary: #1890ff; --bg: #f5f7fa; --card: #ffffff; }}
        body {{ font-family: -apple-system, "SF Pro Text", sans-serif; background: var(--bg); margin: 0; padding: 20px; color: #262626; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        
        .card {{ background: var(--card); border-radius: 8px; padding: 24px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); position: relative; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #f0f0f0; padding-bottom: 16px; margin-bottom: 20px; }}
        .invoice-title {{ font-size: 18px; font-weight: 600; color: var(--primary); }}
        
        .section-header {{ font-size: 14px; font-weight: bold; color: #8c8c8c; margin-bottom: 16px; border-left: 3px solid var(--primary); padding-left: 8px; }}
        
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; margin-bottom: 16px; }}
        .field {{ display: flex; flex-direction: column; }}
        label {{ font-size: 13px; margin-bottom: 6px; color: #595959; }}
        .req::after {{ content: " *"; color: #f5222d; margin-left: 2px; }}
        input, select, textarea {{ padding: 8px 12px; border: 1px solid #d9d9d9; border-radius: 4px; font-size: 13px; transition: 0.2s; }}
        input:focus {{ border-color: var(--primary); outline: none; box-shadow: 0 0 0 2px rgba(24,144,255,0.1); }}
        input:disabled, select:disabled {{ background-color: #f5f5f5; color: #bfbfbf; cursor: not-allowed; }}
        
        /* 表格容器 */
        .table-container {{ border: 1px solid #f0f0f0; border-radius: 4px; overflow: visible !important; position: relative; }}
        table {{ width: 100%; border-collapse: collapse; table-layout: fixed; }}
        th {{ background: #fafafa; padding: 12px 8px; border-bottom: 2px solid #f0f0f0; font-size: 13px; position: relative; }}
        
        td {{ padding: 8px; border-bottom: 1px solid #f0f0f0; position: relative; background: #fff; }}
        .item-input {{ width: 100%; border: 1px solid transparent; padding: 6px; box-sizing: border-box; background: transparent; font-size: 13px; }}
        .item-input:hover {{ background: #f0f7ff; }}

        /* 合计预览条 */
        .total-summary {{ 
            margin-top: 0; padding: 12px 20px; background: #f0f7ff; 
            border: 1px solid #bae7ff; border-top: none; border-radius: 0 0 4px 4px;
            display: flex; justify-content: flex-end; align-items: center; gap: 10px;
        }}
        .total-label {{ font-size: 14px; color: #595959; }}
        .total-value {{ font-size: 18px; font-weight: bold; color: #1890ff; }}

        /* 搜索框 */
        .search-container {{ position: relative; width: 100%; }}
        .search-results {{ 
            position: absolute; top: 100%; left: 0; background: white; 
            box-shadow: 0 10px 32px rgba(0,0,0,0.18); border-radius: 6px; 
            z-index: 10000 !important; max-height: 250px; overflow-y: auto; 
            display: none; margin-top: 8px; width: 350px; border: 1px solid #e8e8e8;
        }}
        .search-results.active {{ display: block; }}
        .search-item {{ padding: 12px; cursor: pointer; border-bottom: 1px solid #f8f8f8; }}
        .search-item:hover {{ background: #e6f7ff; }}
        .search-item .name {{ font-weight: 500; color: #1890ff; display: block; }}
        .search-item .code {{ color: #8c8c8c; font-size: 11px; display: block; margin-top: 4px; }}

        .footer-actions {{ position: fixed; bottom: 0; left: 0; right: 0; background: white; padding: 16px 40px; border-top: 1px solid #f0f0f0; display: flex; justify-content: flex-end; gap: 16px; box-shadow: 0 -4px 12px rgba(0,0,0,0.05); z-index: 500; }}
        .btn {{ cursor: pointer; padding: 8px 16px; border-radius: 4px; border: 1px solid #d9d9d9; font-weight: 500; transition: 0.3s; font-size: 13px; }}
        .btn-primary {{ background: var(--primary); color: white; border-color: var(--primary); }}
        .btn-add {{ background: #52c41a; color: white; border-color: #52c41a; }}
        .btn-clone {{ background: #faad14; color: white; border-color: #faad14; }}
        .btn-json {{ background: #722ed1; color: white; border-color: #722ed1; }}
        .btn-danger {{ color: #ff4d4f; border-color: #ff4d4f; }}
    </style>
</head>
<body>
    <div id="app" class="container">
        <div class="card" style="text-align:center;">
            <h1 style="margin:0; font-size: 24px; color: #141414;">📄 批量发票填报系统 </h1>
        </div>

        <div v-for="(inv, invIdx) in invoices" :key="inv.id" class="card">
            <div class="header">
                <div class="invoice-title">发票 #{{{{ invIdx + 1 }}}}</div>
                <div style="display:flex; gap:10px;">
                    <button class="btn btn-clone" @click="cloneInvoice(inv)">克隆此票</button>
                    <button class="btn btn-danger" @click="removeInvoice(invIdx)" v-if="invoices.length > 1">删除</button>
                </div>
            </div>

            <!-- 基本信息 -->
            <div class="section-header">1. 购买方及发票基本信息</div>
            <div class="grid">
                <div class="field"><label class="req">发票流水号</label><input v-model="inv.serialNo" readonly style="background:#f5f5f5"></div>
                <div class="field"><label class="req">发票类型</label>
                    <select v-model="inv.invoiceType">
                        <option>普通发票</option>
                        <option>增值税专用发票</option>
                    </select>
                </div>
                <div class="field"><label>自然人标识</label>
                    <select v-model="inv.isNaturalPerson" @change="handleNaturalPersonChange(inv)">
                        <option value="">否</option>
                        <option value="是">是</option>
                    </select>
                </div>
                <div class="field"><label class="req">是否含税</label><select v-model="inv.isTaxIncluded"><option>是</option><option>否</option></select></div>
                <div class="field"><label class="req">购买方名称</label><input v-model="inv.buyerName" :title="inv.buyerName" placeholder="全称"></div>
                <div class="field"><label class="req">纳税人识别号</label><input v-model="inv.buyerTaxId" placeholder="税号"></div>
                
                <div class="field"><label>购买方证件类型</label>
                    <select v-model="inv.buyerIdType" :disabled="inv.isNaturalPerson !== '是'">
                        <option value="">(请选择)</option>
                        <option v-for="t in idTypes" :key="t">{{{{ t }}}}</option>
                    </select>
                </div>
                <div class="field"><label>购买方证件号码</label><input v-model="inv.buyerIdNo" :disabled="inv.isNaturalPerson !== '是'"></div>
                <div class="field"><label>购买方国籍（或地区）</label><input v-model="inv.buyerNationality" :disabled="inv.isNaturalPerson !== '是'"></div>
                
                <div class="field"><label>购买方详细地址</label><input v-model="inv.buyerAddress" :title="inv.buyerAddress"></div>
                <div class="field"><label>购买方联系电话</label><input v-model="inv.buyerPhone"></div>
                <div class="field"><label>购买方开户银行</label><input v-model="inv.buyerBankName" :title="inv.buyerBankName"></div>
                <div class="field"><label>购买方银行账号</label><input v-model="inv.buyerBankAccount"></div>
                <div class="field"><label>备注</label><input v-model="inv.remark" :title="inv.remark"></div>
            </div>

            <!-- 明细表 -->
            <div class="section-header">2. 明细列表 </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th style="width: 200px;" class="req">项目名称</th>
                            <th style="width: 250px;" class="req">税收分类</th>
                            <th style="width: 100px;">规格型号</th>
                            <th style="width: 60px;">单位</th>
                            <th style="width: 90px;" class="req">数量</th>
                            <th style="width: 100px;" class="req">单价</th>
                            <th style="width: 110px;" class="req">金额</th>
                            <th style="width: 80px;" class="req">税率</th>
                            <th style="width: 40px;"></th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(item, itemIdx) in inv.items" :key="itemIdx" :style="{{ zIndex: item._showResults ? 1000 : 1 }}">
                            <td><input v-model="item.name" class="item-input" :title="item.name" placeholder="名称"></td>
                            <td style="overflow: visible;">
                                <div class="search-container">
                                    <input v-model="item._search" class="item-input" :title="item._search" placeholder="搜索..." 
                                           @input="searchTaxCodes(item)" @focus="openSearch(item)" @blur="closeSearch(item)">
                                    <div class="search-results" :class="{{ active: item._showResults && item._filtered.length > 0 }}">
                                        <div v-for="res in item._filtered" :key="res.c" class="search-item" @mousedown="selectTaxCode(item, res)">
                                            <span class="name">{{{{ res.n }}}}</span>
                                            <span class="code">{{{{ res.c }}}}</span>
                                        </div>
                                    </div>
                                    <div style="font-size: 10px; color: #1890ff; padding-left: 6px;">{{{{ item.code || '未选' }}}}</div>
                                </div>
                            </td>
                            <td><input v-model="item.spec" class="item-input" :title="item.spec"></td>
                            <td><input v-model="item.unit" class="item-input" :title="item.unit"></td>
                            <td><input v-model.number="item.qty" type="number" class="item-input" @input="handleCalc(item, 'qty')"></td>
                            <td><input v-model.number="item.price" type="number" class="item-input" @input="handleCalc(item, 'price')"></td>
                            <td><input v-model.number="item.amount" type="number" class="item-input" style="font-weight:bold;" @input="handleCalc(item, 'amount')"></td>
                            <td>
                                <select v-model="item.taxRate" class="item-input">
                                    <option value="0.13">13%</option><option value="0.09">9%</option><option value="0.06">6%</option>
                                    <option value="0.03">3%</option><option value="0.01">1%</option><option value="0">0%</option>
                                </select>
                            </td>
                            <td><button @click="removeItem(invIdx, itemIdx)" style="color:#ff4d4f; border:none; background:none; cursor:pointer;">&times;</button></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <!-- 实时合计 -->
            <div class="total-summary">
                <span class="total-label">当前票据明细合计:</span>
                <span class="total-value">¥ {{{{ getInvTotal(inv) }}}}</span>
            </div>

            <button class="btn" style="margin-top:12px; border-style: dashed; width: 100%; color: #8c8c8c;" @click="addItem(invIdx)">+ 添加明细行</button>
        </div>

        <div style="height: 120px;"></div>
        <div class="footer-actions">
            <button class="btn btn-json" @click="exportJSON">💾 导出 JSON</button>
            <button class="btn btn-json" @click="triggerImport">📂 导入 JSON</button>
            <input type="file" id="jsonInput" style="display:none" accept=".json" @change="importJSON">
            <button class="btn btn-add" @click="addInvoice">➕ 添加空白发票</button>
            <button class="btn btn-primary" @click="exportAll" :disabled="isExporting">📥 导出批量开票 XLSX</button>
        </div>
    </div>

    <script>
        const {{ createApp, ref, reactive }} = Vue;
        const BASE64_TEMPLATE = "{template_base64}";
        const TAX_CODES = {json.dumps(tax_codes, ensure_ascii=False)};
        const ID_TYPES = ['居民身份证', '外国护照', '香港永久性居民身份证', '台湾身份证', '营业执照', '组织机构代码证', '税务登记证', '其他单位证件'];

        createApp({{
            setup() {{
                const isExporting = ref(false);
                const idTypes = ref(ID_TYPES);
                const generateSerial = () => 'INV' + Date.now().toString().slice(-6) + Math.random().toString(36).substr(2, 4).toUpperCase();
                const createEmptyItem = () => ({{ name: '', code: '', spec: '', unit: '', qty: null, price: null, amount: 0, taxRate: '0.01', _search: '', _filtered: [], _showResults: false }});
                const createEmptyInvoice = () => ({{
                    id: Date.now() + Math.random(), serialNo: generateSerial(), invoiceType: '普通发票', isNaturalPerson: '', isTaxIncluded: '是',
                    buyerName: '', buyerTaxId: '', buyerIdType: '', buyerIdNo: '', buyerNationality: '', buyerAddress: '', buyerPhone: '',
                    buyerBankName: '', buyerBankAccount: '', buyerEmail: '', remark: '', items: [createEmptyItem()]
                }});
                const invoices = reactive([createEmptyInvoice()]);

                const getInvTotal = (inv) => {{
                    const total = inv.items.reduce((sum, it) => sum + (parseFloat(it.amount) || 0), 0);
                    return total.toLocaleString('zh-CN', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
                }};

                const handleNaturalPersonChange = (inv) => {{
                    if (inv.isNaturalPerson !== '是') {{ inv.buyerIdType = ''; inv.buyerIdNo = ''; inv.buyerNationality = ''; }}
                }};

                const openSearch = (item) => {{ item._showResults = true; searchTaxCodes(item); }};
                const closeSearch = (item) => {{ setTimeout(() => {{ item._showResults = false; }}, 200); }};
                const searchTaxCodes = (item) => {{
                    const q = item._search ? item._search.toLowerCase() : '';
                    item._filtered = q ? TAX_CODES.filter(x => x.n.includes(q)).slice(0, 50) : TAX_CODES.slice(0, 20);
                }};
                const selectTaxCode = (item, res) => {{ item.code = res.c; item._search = res.n; item._showResults = false; if (!item.name) item.name = res.n; }};
                
                const handleCalc = (item, type) => {{
                    const qty = parseFloat(item.qty); const price = parseFloat(item.price); const amount = parseFloat(item.amount);
                    if (type === 'qty') {{ if (price) item.amount = (qty * price).toFixed(2); else if (amount) item.price = (amount / qty).toFixed(6); }}
                    else if (type === 'price') {{ if (qty) item.amount = (qty * price).toFixed(2); else if (amount) item.qty = (amount / price).toFixed(6); }}
                    else if (type === 'amount') {{ if (qty) item.price = (amount / qty).toFixed(6); else if (price) item.qty = (amount / price).toFixed(6); }}
                }};

                const addInvoice = () => invoices.push(createEmptyInvoice());
                const cloneInvoice = (inv) => {{ const newInv = JSON.parse(JSON.stringify(inv)); newInv.id = Date.now() + Math.random(); newInv.serialNo = generateSerial(); invoices.push(newInv); }};
                const removeInvoice = (idx) => invoices.splice(idx, 1);
                const addItem = (invIdx) => invoices[invIdx].items.push(createEmptyItem());
                const removeItem = (invIdx, itemIdx) => {{ if (invoices[invIdx].items.length > 1) invoices[invIdx].items.splice(itemIdx, 1); }};

                const exportJSON = () => {{
                    const blob = new Blob([JSON.stringify(invoices, null, 2)], {{ type: 'application/json' }});
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a'); a.href = url; a.download = `${{invoices[0].buyerName}}_发票草稿_${{new Date().getTime()}}.json`; a.click();
                }};
                const triggerImport = () => document.getElementById('jsonInput').click();
                const importJSON = (e) => {{
                    const file = e.target.files[0]; if (!file) return;
                    const reader = new FileReader();
                    reader.onload = (event) => {{
                        try {{
                            const data = JSON.parse(event.target.result);
                            invoices.splice(0, invoices.length, ...data);
                            alert('导入成功！');
                        }} catch (err) {{ alert('JSON 格式错误'); }}
                    }};
                    reader.readAsText(file);
                }};

                const exportAll = async () => {{
                    for (let i = 0; i < invoices.length; i++) {{
                        const inv = invoices[i]; if (!inv.buyerName) return alert(`发票 #${{i+1}}: 请输入购买方名称`);
                    }}
                    isExporting.value = true;
                    try {{
                        const workbook = new ExcelJS.Workbook();
                        const buffer = Uint8Array.from(atob(BASE64_TEMPLATE), c => c.charCodeAt(0));
                        await workbook.xlsx.load(buffer);
                        const ws1 = workbook.getWorksheet('1-发票基本信息');
                        const ws2 = workbook.getWorksheet('2-发票明细信息');
                        let detailRowIdx = 4;
                        invoices.forEach((inv, invIdx) => {{
                            const r1 = ws1.getRow(4 + invIdx);
                            r1.getCell(1).value = inv.serialNo; r1.getCell(2).value = inv.invoiceType;
                            r1.getCell(3).value = inv.specialBusiness; r1.getCell(4).value = inv.isTaxIncluded;
                            r1.getCell(6).value = inv.buyerName; r1.getCell(7).value = inv.buyerTaxId;
                            if (inv.isNaturalPerson === '是') {{
                                r1.getCell(8).value = inv.buyerIdType; r1.getCell(9).value = inv.buyerIdNo;
                                r1.getCell(10).value = inv.buyerNationality;
                            }} else {{
                                r1.getCell(8).value = ''; r1.getCell(9).value = ''; r1.getCell(10).value = '';
                            }}
                            r1.getCell(11).value = inv.buyerAddress; r1.getCell(17).value = inv.buyerPhone;
                            r1.getCell(18).value = inv.buyerBankName; r1.getCell(19).value = inv.buyerBankAccount;
                            r1.getCell(23).value = inv.remark; r1.getCell(31).value = inv.buyerEmail;
                            r1.commit();
                            inv.items.forEach(item => {{
                                const r2 = ws2.getRow(detailRowIdx++);
                                r2.getCell(1).value = inv.serialNo; r2.getCell(2).value = item.name;
                                r2.getCell(3).value = item.code; r2.getCell(4).value = item.spec;
                                r2.getCell(5).value = item.unit; r2.getCell(6).value = item.qty;
                                r2.getCell(7).value = item.price; r2.getCell(8).value = parseFloat(item.amount);
                                r2.getCell(9).value = parseFloat(item.taxRate); r2.commit();
                            }});
                        }});
                        const outBuffer = await workbook.xlsx.writeBuffer();
                        const blob = new Blob([outBuffer], {{ type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }});
                        const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = `${{invoices[0].buyerName}}_批量发票.xlsx`; a.click();
                    }} catch (e) {{ alert('导出错误: ' + e.message); }} finally {{ isExporting.value = false; }}
                }};
                return {{ invoices, idTypes, getInvTotal, addInvoice, cloneInvoice, removeInvoice, addItem, removeItem, handleNaturalPersonChange, exportJSON, triggerImport, importJSON, exportAll, isExporting, searchTaxCodes, selectTaxCode, handleCalc, openSearch, closeSearch }};
            }}
        }}).mount('#app');
    </script>
</body>
</html>
'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Updated build_app.py with filtered tax codes and synced UI.")
