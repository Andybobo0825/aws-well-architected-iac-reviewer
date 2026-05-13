# AWS Well-Architected IaC Reviewer

這是一個適合作品集展示的 Terraform 靜態架構審查工具。它會在基礎設施部署前掃描 Infrastructure as Code，並產出 AWS Well-Architected 風格的 Markdown 報告：`architecture-review.md`。

本專案刻意設計成可在本機安全執行的 demo：它**不會**呼叫 AWS API、不需要 AWS credentials、不會執行 `terraform apply`，也不會建立任何雲端資源。

## 專案目的

雲端架構審查常常發生在 Terraform 已經接近上線時，導致安全性、可靠性或成本風險太晚才被發現。本專案把一部分 AWS Well-Architected 的審查問題轉成自動化 Pull Request 回饋，讓常見風險能在更早的 IaC review 階段被看見。

這個專案展示：

- 以 AWS Well-Architected 五大支柱進行架構審查的思維。
- 不依賴雲端 API、無副作用的 Terraform 靜態分析能力。
- 可放進 GitHub Pull Request 討論的 Markdown 審查報告。
- 適合 Cloud Solution Architect / DevOps Engineer 作品集的 CI 自動化流程。

## 審查範圍

| Well-Architected 支柱 | 檢查類別 | 偵測訊號範例 |
| --- | --- | --- |
| Security | 公開暴露風險 | S3 公開存取、Security Group 開放 `0.0.0.0/0` 等過度寬鬆 ingress |
| Reliability | 資料韌性 | RDS 備份保留天數、Multi-AZ 設定訊號 |
| Operational Excellence | 可維運性 | CloudWatch Logs、Alarm、必要 Tags |
| Cost Optimization | 成本護欄 | 過大的運算資源、缺少 AWS Budget |
| Performance Efficiency | 擴展與快取設計 | Auto Scaling、Cache 設計訊號 |

規則刻意保持透明且保守。工具產生的 findings 應視為架構審查提示，不應取代完整的 AWS Well-Architected Review。

## 專案目錄結構

```text
.
├── src/iac_reviewer/             # Python CLI 與規則引擎
├── tests/                        # 單元測試與 fixture 測試
├── examples/terraform/           # 安全與不安全 Terraform 範例
├── docs/ARCHITECTURE.md          # 系統設計與資料流
├── docs/RULES.md                 # 規則目錄與 fixture 對應
├── docs/ROADMAP_ALIGNMENT.md     # 作品集 roadmap 對應說明
├── infra/terraform-intake.md     # Terraform 審查 intake 模板
└── .github/workflows/iac-review.yml
```

## 快速開始

本專案可直接用 Python module 執行。建議先跑語法與測試檢查：

```bash
python3 -m compileall src tests
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'
```

掃描範例 Terraform 並產生報告：

```bash
PYTHONPATH=src python3 -m iac_reviewer examples/terraform/insecure-sample --output architecture-review.md --fail-on none
```

如果已安裝 Terraform，可檢查範例與 intake 檔案格式：

```bash
terraform fmt -check -recursive examples infra
```

也可以執行整合驗證腳本：

```bash
./scripts/validate.sh
```

## GitHub Actions 流程

本專案包含 Pull Request 與 push 觸發的 GitHub Actions workflow，設計目標是讓 IaC review 能自動化執行：

1. 設定 Python 環境。
2. 在 dependency 檔案存在時安裝專案與測試依賴。
3. 編譯 Python source 與 tests。
4. 有測試時執行 pytest；本機腳本則提供 unittest fallback。
5. 在 Terraform CLI 與 `.tf` 檔案存在時執行格式檢查。
6. 使用 reviewer 掃描 Terraform 範例。
7. 產出並上傳 `architecture-review.md` 作為 workflow artifact。

## 安全邊界

- 只做靜態檔案掃描。
- 不需要、也不會要求 AWS credentials。
- Reviewer 流程不需要執行 `terraform init`、`terraform plan` 或 `terraform apply`。
- `examples/terraform/` 內的 Terraform 僅用於偵測規則覆蓋與作品集討論，不是 production deployment 範本。

## 報告內容範例

`architecture-review.md` 會包含：

- 審查摘要與掃描路徑。
- 每個 finding 的風險等級。
- 對應的 Well-Architected 支柱。
- 檔案與 Terraform resource evidence。
- 修正建議。
- 對假設與審查限制的簡短說明。

## Roadmap 對應

本 repo 對應作品集 roadmap 第二個專案：「AWS Well-Architected IaC Reviewer」。它展示如何把 AWS 架構最佳實踐轉成 Terraform 自動化審查規則，並在 PR 階段產生可討論的 Markdown 架構審查報告。
