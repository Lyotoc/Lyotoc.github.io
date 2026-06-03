package main

import (
	"bytes"
	"encoding/base64"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"log"
	"os"
	"strconv"
	"strings"

	"github.com/xuri/excelize/v2"
)

// TaxCode 代表税收分类编码项
type TaxCode struct {
	Name string `json:"n"`
	Code string `json:"c"`
}

// InvoiceItem 代表发票明细
type InvoiceItem struct {
	Name    string  `json:"name"`
	Code    string  `json:"code"`
	Spec    string  `json:"spec"`
	Unit    string  `json:"unit"`
	Qty     float64 `json:"qty"`
	Price   float64 `json:"price"`
	Amount  float64 `json:"amount"`
	TaxRate float64 `json:"taxRate"`
}

// Invoice 代表发票基本信息
type Invoice struct {
	SerialNo         string        `json:"serialNo"`
	InvoiceType      string        `json:"invoiceType"`
	SpecialBusiness  string        `json:"specialBusiness"`
	IsTaxIncluded    string        `json:"isTaxIncluded"`
	BuyerName        string        `json:"buyerName"`
	BuyerTaxId       string        `json:"buyerTaxId"`
	IsNaturalPerson  string        `json:"isNaturalPerson"`
	BuyerIdType      string        `json:"buyerIdType"`
	BuyerIdNo        string        `json:"buyerIdNo"`
	BuyerNationality string        `json:"buyerNationality"`
	BuyerAddress     string        `json:"buyerAddress"`
	BuyerPhone       string        `json:"buyerPhone"`
	BuyerBankName    string        `json:"buyerBankName"`
	BuyerBankAccount string        `json:"buyerBankAccount"`
	Remark           string        `json:"remark"`
	BuyerEmail       string        `json:"buyerEmail"`
	Items            []InvoiceItem `json:"items"`
}

func main() {
	inputPath := flag.String("input", "", "JSON 输入文件路径 (不填则从 stdin 读取)")
	outputPath := flag.String("output", "output.xlsx", "输出 XLSX 文件路径")
	templatePath := flag.String("template", "../template_base64.txt", "Base64 编码的模板文件路径")
	taxCodesPath := flag.String("tax-codes", "../tax_codes.json", "税收分类编码 JSON 文件路径")
	listCodes := flag.Bool("list-codes", false, "列出前 100 条税收分类编码并退出")
	searchCodes := flag.String("search-codes", "", "搜索税收分类编码 (按名称) 并退出")
	flag.Parse()

	// 加载税收编码
	taxCodes, err := loadTaxCodes(*taxCodesPath)
	if err != nil {
		log.Fatalf("加载税收编码失败: %v", err)
	}

	// 处理查询逻辑
	if *listCodes {
		printTaxCodes(taxCodes, "", 100)
		return
	}
	if *searchCodes != "" {
		printTaxCodes(taxCodes, *searchCodes, 0)
		return
	}

	var inputData []byte
	if *inputPath != "" {
		inputData, err = os.ReadFile(*inputPath)
	} else {
		inputData, err = io.ReadAll(os.Stdin)
	}

	if err != nil {
		log.Fatalf("读取输入失败: %v", err)
	}

	if len(inputData) == 0 {
		flag.Usage()
		return
	}

	var invoices []Invoice
	if err := json.Unmarshal(inputData, &invoices); err != nil {
		log.Fatalf("解析 JSON 失败: %v", err)
	}

	// 验证税收编码
	taxCodeMap := make(map[string]string)
	for _, tc := range taxCodes {
		taxCodeMap[tc.Code] = tc.Name
	}

	for i, inv := range invoices {
		for j, item := range inv.Items {
			if _, ok := taxCodeMap[item.Code]; !ok {
				log.Fatalf("发票 #%d 明细 #%d: 无效的税收编码 %s", i+1, j+1, item.Code)
			}
		}
	}

	templateBase64, err := os.ReadFile(*templatePath)
	if err != nil {
		log.Fatalf("读取模板文件失败: %v", err)
	}

	templateBytes, err := base64.StdEncoding.DecodeString(string(bytes.TrimSpace(templateBase64)))
	if err != nil {
		log.Fatalf("Base64 解码模板失败: %v", err)
	}

	f, err := excelize.OpenReader(bytes.NewReader(templateBytes))
	if err != nil {
		log.Fatalf("打开 Excel 模板失败: %v", err)
	}
	defer f.Close()

	wsBasic := "1-发票基本信息"
	wsDetail := "2-发票明细信息"

	detailRowIdx := 4
	for i, inv := range invoices {
		basicRowIdx := 4 + i
		
		// 填充基本信息
		setCell(f, wsBasic, 1, basicRowIdx, inv.SerialNo)
		setCell(f, wsBasic, 2, basicRowIdx, inv.InvoiceType)
		setCell(f, wsBasic, 3, basicRowIdx, inv.SpecialBusiness)
		setCell(f, wsBasic, 4, basicRowIdx, inv.IsTaxIncluded)
		setCell(f, wsBasic, 6, basicRowIdx, inv.BuyerName)
		setCell(f, wsBasic, 7, basicRowIdx, inv.BuyerTaxId)
		
		if inv.IsNaturalPerson == "是" {
			setCell(f, wsBasic, 8, basicRowIdx, inv.BuyerIdType)
			setCell(f, wsBasic, 9, basicRowIdx, inv.BuyerIdNo)
			setCell(f, wsBasic, 10, basicRowIdx, inv.BuyerNationality)
		} else {
			setCell(f, wsBasic, 8, basicRowIdx, "")
			setCell(f, wsBasic, 9, basicRowIdx, "")
			setCell(f, wsBasic, 10, basicRowIdx, "")
		}
		
		setCell(f, wsBasic, 11, basicRowIdx, inv.BuyerAddress)
		setCell(f, wsBasic, 17, basicRowIdx, inv.BuyerPhone)
		setCell(f, wsBasic, 18, basicRowIdx, inv.BuyerBankName)
		setCell(f, wsBasic, 19, basicRowIdx, inv.BuyerBankAccount)
		setCell(f, wsBasic, 23, basicRowIdx, inv.Remark)
		setCell(f, wsBasic, 31, basicRowIdx, inv.BuyerEmail)

		// 填充明细信息
		for _, item := range inv.Items {
			setCell(f, wsDetail, 1, detailRowIdx, inv.SerialNo)
			setCell(f, wsDetail, 2, detailRowIdx, item.Name)
			setCell(f, wsDetail, 3, detailRowIdx, item.Code)
			setCell(f, wsDetail, 4, detailRowIdx, item.Spec)
			setCell(f, wsDetail, 5, detailRowIdx, item.Unit)
			setCell(f, wsDetail, 6, detailRowIdx, item.Qty)
			setCell(f, wsDetail, 7, detailRowIdx, item.Price)
			setCell(f, wsDetail, 8, detailRowIdx, item.Amount)
			setCell(f, wsDetail, 9, detailRowIdx, item.TaxRate)
			detailRowIdx++
		}
	}

	if err := f.SaveAs(*outputPath); err != nil {
		log.Fatalf("保存 XLSX 失败: %v", err)
	}

	fmt.Printf("成功生成发票 XLSX: %s\n", *outputPath)
}

func setCell(f *excelize.File, sheet string, col, row int, value interface{}) {
	cell, _ := excelize.ColumnNumberToName(col)
	f.SetCellValue(sheet, cell+strconv.Itoa(row), value)
}

func loadTaxCodes(path string) ([]TaxCode, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	var codes []TaxCode
	err = json.Unmarshal(data, &codes)
	return codes, err
}

func printTaxCodes(codes []TaxCode, query string, limit int) {
	count := 0
	query = strings.ToLower(query)
	fmt.Printf("%-20s %-20s\n", "编码", "名称")
	fmt.Println(strings.Repeat("-", 45))
	for _, tc := range codes {
		if query != "" && !strings.Contains(strings.ToLower(tc.Name), query) {
			continue
		}
		fmt.Printf("%-20s %-20s\n", tc.Code, tc.Name)
		count++
		if limit > 0 && count >= limit {
			break
		}
	}
	if query != "" {
		fmt.Printf("\n找到 %d 条相关编码。\n", count)
	}
}
