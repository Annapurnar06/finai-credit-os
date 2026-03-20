"""Four demo borrower profiles — realistic Indian lending scenarios.

Each profile includes synthetic document content that the extraction agents
will process end-to-end. These are the personas from the FINAI spec:
Savitri, Rajan, Meera, Prakash.
"""
from __future__ import annotations

SALARIED_CLEAN = {
    "name": "Rajan Krishnamurthy",
    "pan": "DEFPR5678B",
    "scenario": "salaried_clean",
    "description": "Small manufacturer, Coimbatore. Salaried + business income. CIBIL 720. Clean case — should auto-approve.",
    "product_type": "personal_loan",
    "requested_amount": 500000,
    "documents": [
        {
            "filename": "rajan_pan_card.pdf",
            "doc_type": "pan",
            "content_text": (
                "INCOME TAX DEPARTMENT\n"
                "PERMANENT ACCOUNT NUMBER CARD\n"
                "Name: RAJAN KRISHNAMURTHY\n"
                "Father's Name: VENKATESH KRISHNAMURTHY\n"
                "Date of Birth: 15/03/1985\n"
                "PAN: DEFPR5678B\n"
                "Signature: [signed]\n"
            ),
        },
        {
            "filename": "rajan_bank_statement_hdfc.pdf",
            "doc_type": "bank_statement",
            "content_text": (
                "HDFC BANK — ACCOUNT STATEMENT\n"
                "Account Holder: RAJAN KRISHNAMURTHY\n"
                "Account Number: 50100248975631\n"
                "IFSC: HDFC0001234\n"
                "Period: March 2025 — February 2026\n\n"
                "MONTHLY SUMMARY:\n"
                "Mar-2025: Credits ₹92,000 | Debits ₹78,000 | Balance ₹1,45,000\n"
                "Apr-2025: Credits ₹88,000 | Debits ₹72,000 | Balance ₹1,61,000\n"
                "May-2025: Credits ₹90,000 | Debits ₹80,000 | Balance ₹1,71,000\n"
                "Jun-2025: Credits ₹85,000 | Debits ₹75,000 | Balance ₹1,81,000\n"
                "Jul-2025: Credits ₹91,000 | Debits ₹82,000 | Balance ₹1,90,000\n"
                "Aug-2025: Credits ₹87,000 | Debits ₹79,000 | Balance ₹1,98,000\n"
                "Sep-2025: Credits ₹93,000 | Debits ₹81,000 | Balance ₹2,10,000\n"
                "Oct-2025: Credits ₹86,000 | Debits ₹77,000 | Balance ₹2,19,000\n"
                "Nov-2025: Credits ₹89,000 | Debits ₹83,000 | Balance ₹2,25,000\n"
                "Dec-2025: Credits ₹95,000 | Debits ₹85,000 | Balance ₹2,35,000\n"
                "Jan-2026: Credits ₹88,000 | Debits ₹78,000 | Balance ₹2,45,000\n"
                "Feb-2026: Credits ₹92,000 | Debits ₹80,000 | Balance ₹2,57,000\n\n"
                "Average Monthly Balance: ₹2,03,000\n"
                "Salary Credits Detected: ₹85,000/month (Employer: TCS Ltd)\n"
                "EMI Outflows: ₹12,000/month (Car loan — ICICI Bank)\n"
                "Bounce Count: 0\n"
            ),
        },
        {
            "filename": "rajan_salary_slip_feb2026.pdf",
            "doc_type": "salary_slip",
            "content_text": (
                "TCS LIMITED - SALARY SLIP\n"
                "Employee: RAJAN KRISHNAMURTHY\n"
                "Employee ID: TCS-CBE-45678\n"
                "Month: February 2026\n\n"
                "EARNINGS:\n"
                "Basic Salary: ₹45,000\n"
                "HRA: ₹18,000\n"
                "Special Allowance: ₹15,000\n"
                "Performance Bonus: ₹7,000\n"
                "Gross Salary: ₹85,000\n\n"
                "DEDUCTIONS:\n"
                "EPF (Employee): ₹5,400\n"
                "Professional Tax: ₹200\n"
                "Income Tax: ₹6,500\n"
                "Total Deductions: ₹12,100\n\n"
                "Net Salary: ₹72,900\n"
            ),
        },
        {
            "filename": "rajan_cibil_report.pdf",
            "doc_type": "credit_bureau",
            "content_text": (
                "TRANSUNION CIBIL — CREDIT INFORMATION REPORT\n"
                "Consumer Name: RAJAN KRISHNAMURTHY\n"
                "PAN: DEFPR5678B\n"
                "CIBIL Score: 745\n\n"
                "ACCOUNT SUMMARY:\n"
                "Active Accounts: 1\n"
                "- Car Loan (ICICI Bank): Sanctioned ₹6,00,000 | Outstanding ₹1,80,000 | EMI ₹12,000 | DPD: NIL\n\n"
                "Enquiry Count (Last 6 months): 2\n"
                "Write-offs: NIL\n"
                "Settlements: NIL\n"
                "Oldest Tradeline: 48 months\n"
            ),
        },
    ],
}

MSME_SEASONAL = {
    "name": "Savitri Bai Patil",
    "pan": "ABCPS1234A",
    "scenario": "msme_seasonal",
    "description": "Vegetable cart owner, Nagpur. No credit history. Seasonal income. GrāmScore path.",
    "product_type": "personal_loan",
    "requested_amount": 100000,
    "documents": [
        {
            "filename": "savitri_pan_card.pdf",
            "doc_type": "pan",
            "content_text": (
                "INCOME TAX DEPARTMENT\n"
                "PERMANENT ACCOUNT NUMBER CARD\n"
                "Name: SAVITRI BAI PATIL\n"
                "Father's Name: RAMESH PATIL\n"
                "Date of Birth: 20/08/1978\n"
                "PAN: ABCPS1234A\n"
            ),
        },
        {
            "filename": "savitri_bank_passbook.pdf",
            "doc_type": "passbook",
            "content_text": (
                "BANK OF MAHARASHTRA — PASSBOOK\n"
                "Account Holder: SAVITRI BAI PATIL\n"
                "Account Number: 20198765432\n"
                "Branch: NAGPUR ITWARI, IFSC: MAHB0001456\n\n"
                "TRANSACTIONS (Last 6 months):\n"
                "01-Sep-2025: Cash Deposit ₹8,000 | Balance ₹12,500\n"
                "15-Sep-2025: UPI Credit ₹3,200 | Balance ₹15,700\n"
                "01-Oct-2025: Cash Deposit ₹12,000 | Balance ₹27,700\n"
                "15-Oct-2025: Cash Withdrawal ₹10,000 | Balance ₹17,700\n"
                "01-Nov-2025: Cash Deposit ₹15,000 | Balance ₹32,700\n"
                "15-Nov-2025: UPI Credit ₹5,500 | Balance ₹38,200\n"
                "01-Dec-2025: Cash Deposit ₹18,000 | Balance ₹56,200\n"
                "15-Dec-2025: Cash Withdrawal ₹12,000 | Balance ₹44,200\n"
                "01-Jan-2026: Cash Deposit ₹10,000 | Balance ₹54,200\n"
                "01-Feb-2026: Cash Deposit ₹8,000 | Balance ₹62,200\n\n"
                "Average Monthly Balance: ₹15,200\n"
                "Cash Deposit Pattern: Seasonal — higher in Oct-Dec (festive)\n"
                "UPI Transaction Count: 45/month avg\n"
            ),
        },
        {
            "filename": "savitri_utility_bill.pdf",
            "doc_type": "utility_bill",
            "content_text": (
                "MAHARASHTRA STATE ELECTRICITY DISTRIBUTION CO LTD\n"
                "Consumer Name: SAVITRI BAI PATIL\n"
                "Consumer No: NGP-789456123\n"
                "Address: Plot 45, Itwari Market, Nagpur — 440002\n"
                "Bill Amount: ₹1,850\n"
                "Units Consumed: 185 kWh\n"
                "Bill Period: January 2026\n"
                "Due Date: 15-Feb-2026\n"
                "Payment Status: PAID\n"
            ),
        },
    ],
}

GIG_WORKER = {
    "name": "Meera Srinivasan",
    "pan": "GHIMK9012C",
    "scenario": "gig_worker",
    "description": "Gig worker, Bengaluru. Multiple income sources. No Form 16. CIBIL 680.",
    "product_type": "personal_loan",
    "requested_amount": 300000,
    "documents": [
        {
            "filename": "meera_pan_card.pdf",
            "doc_type": "pan",
            "content_text": (
                "INCOME TAX DEPARTMENT\n"
                "PERMANENT ACCOUNT NUMBER CARD\n"
                "Name: MEERA SRINIVASAN\n"
                "Father's Name: KRISHNA SRINIVASAN\n"
                "Date of Birth: 12/06/1992\n"
                "PAN: GHIMK9012C\n"
            ),
        },
        {
            "filename": "meera_bank_statement_kotak.pdf",
            "doc_type": "bank_statement",
            "content_text": (
                "KOTAK MAHINDRA BANK — ACCOUNT STATEMENT\n"
                "Account Holder: MEERA SRINIVASAN\n"
                "Account Number: 98765432100\n"
                "IFSC: KKBK0005678\n"
                "Period: March 2025 — February 2026\n\n"
                "MONTHLY SUMMARY:\n"
                "Mar-2025: Credits ₹52,000 | Debits ₹48,000 | Balance ₹78,000\n"
                "Apr-2025: Credits ₹38,000 | Debits ₹35,000 | Balance ₹81,000\n"
                "May-2025: Credits ₹55,000 | Debits ₹50,000 | Balance ₹86,000\n"
                "Jun-2025: Credits ₹42,000 | Debits ₹40,000 | Balance ₹88,000\n"
                "Jul-2025: Credits ₹60,000 | Debits ₹52,000 | Balance ₹96,000\n"
                "Aug-2025: Credits ₹35,000 | Debits ₹33,000 | Balance ₹98,000\n"
                "Sep-2025: Credits ₹48,000 | Debits ₹44,000 | Balance ₹1,02,000\n"
                "Oct-2025: Credits ₹55,000 | Debits ₹50,000 | Balance ₹1,07,000\n"
                "Nov-2025: Credits ₹40,000 | Debits ₹38,000 | Balance ₹1,09,000\n"
                "Dec-2025: Credits ₹58,000 | Debits ₹53,000 | Balance ₹1,14,000\n"
                "Jan-2026: Credits ₹45,000 | Debits ₹42,000 | Balance ₹1,17,000\n"
                "Feb-2026: Credits ₹50,000 | Debits ₹46,000 | Balance ₹1,21,000\n\n"
                "Average Monthly Balance: ₹1,00,000\n"
                "Multiple credit sources: Swiggy, Urban Company, Freelance UPI\n"
                "No single salary credit detected — gig income pattern\n"
                "EMI Outflows: ₹5,000/month (BNPL — Simpl)\n"
                "Bounce Count: 1\n"
            ),
        },
        {
            "filename": "meera_itr_ay2025.pdf",
            "doc_type": "itr",
            "content_text": (
                "INCOME TAX RETURN — ITR-1 (SAHAJ)\n"
                "Assessment Year: 2025-26\n"
                "Name: MEERA SRINIVASAN\n"
                "PAN: GHIMK9012C\n\n"
                "INCOME DETAILS:\n"
                "Income from Salary: ₹0\n"
                "Income from Other Sources: ₹5,40,000\n"
                "Gross Total Income: ₹5,40,000\n"
                "Deductions (80C): ₹50,000\n"
                "Total Income: ₹4,90,000\n"
                "Tax Paid: ₹12,500\n"
                "ITR Filing Date: 28-Jul-2025\n"
            ),
        },
    ],
}

FIRST_TIME_BORROWER = {
    "name": "Prakash Kumar Yadav",
    "pan": "JKLPN3456D",
    "scenario": "first_time_borrower",
    "description": "Kirana store, rural UP. No credit history. First-time borrower. GrāmScore path.",
    "product_type": "business_loan",
    "requested_amount": 200000,
    "documents": [
        {
            "filename": "prakash_pan_card.pdf",
            "doc_type": "pan",
            "content_text": (
                "INCOME TAX DEPARTMENT\n"
                "PERMANENT ACCOUNT NUMBER CARD\n"
                "Name: PRAKASH KUMAR YADAV\n"
                "Father's Name: SURESH YADAV\n"
                "Date of Birth: 05/11/1988\n"
                "PAN: JKLPN3456D\n"
            ),
        },
        {
            "filename": "prakash_bank_statement_sbi.pdf",
            "doc_type": "bank_statement",
            "content_text": (
                "STATE BANK OF INDIA — ACCOUNT STATEMENT\n"
                "Account Holder: PRAKASH KUMAR YADAV\n"
                "Account Number: 38776543210\n"
                "IFSC: SBIN0009876\n"
                "Branch: SULTANPUR, UP\n"
                "Period: September 2025 — February 2026\n\n"
                "MONTHLY SUMMARY:\n"
                "Sep-2025: Credits ₹28,000 | Debits ₹25,000 | Balance ₹18,000\n"
                "Oct-2025: Credits ₹32,000 | Debits ₹28,000 | Balance ₹22,000\n"
                "Nov-2025: Credits ₹35,000 | Debits ₹30,000 | Balance ₹27,000\n"
                "Dec-2025: Credits ₹30,000 | Debits ₹27,000 | Balance ₹30,000\n"
                "Jan-2026: Credits ₹22,000 | Debits ₹20,000 | Balance ₹32,000\n"
                "Feb-2026: Credits ₹25,000 | Debits ₹22,000 | Balance ₹35,000\n\n"
                "Average Monthly Balance: ₹27,000\n"
                "UPI Merchant Credits (Google Pay): ₹18,000/month avg\n"
                "Cash Deposits: ₹10,000/month avg\n"
                "Mobile Recharge: Regular (₹299 plan, monthly)\n"
                "EMI Outflows: ₹0\n"
                "Bounce Count: 0\n"
            ),
        },
        {
            "filename": "prakash_gst_certificate.pdf",
            "doc_type": "gst_return",
            "content_text": (
                "GSTIN: 09JKLPN3456D1ZP\n"
                "Trade Name: YADAV KIRANA STORE\n"
                "Legal Name: PRAKASH KUMAR YADAV\n"
                "Registration Date: 01-Apr-2024\n"
                "Composition Scheme: Yes\n\n"
                "GSTR-4 (Annual Composition Return) — FY 2024-25:\n"
                "Total Turnover: ₹18,50,000\n"
                "Tax Payable: ₹18,500\n"
                "Tax Paid: ₹18,500\n"
                "Filing Status: Filed on time\n\n"
                "Quarterly Turnover Trend:\n"
                "Q1 (Apr-Jun 2024): ₹3,80,000\n"
                "Q2 (Jul-Sep 2024): ₹4,20,000\n"
                "Q3 (Oct-Dec 2024): ₹5,50,000\n"
                "Q4 (Jan-Mar 2025): ₹5,00,000\n"
            ),
        },
    ],
}

ALL_SCENARIOS = {
    "salaried_clean": SALARIED_CLEAN,
    "msme_seasonal": MSME_SEASONAL,
    "gig_worker": GIG_WORKER,
    "first_time_borrower": FIRST_TIME_BORROWER,
}
