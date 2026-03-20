"""DPI (Digital Public Infrastructure) mock layer for FINAI Credit OS.

Provides realistic test implementations of India's DPI APIs:
Account Aggregator, Credit Bureau, PAN verification, Aadhaar eKYC, and GSTN.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Protocol, TypedDict, runtime_checkable

# ---------------------------------------------------------------------------
# Return-type TypedDicts
# ---------------------------------------------------------------------------

class ConsentResponse(TypedDict):
    consent_id: str
    status: str
    created_at: str
    expiry: str
    fi_types: list[str]


class TransactionSummary(TypedDict):
    month: str
    credit_total: float
    debit_total: float
    closing_balance: float


class FinancialData(TypedDict):
    account_holder: str
    bank_name: str
    account_type: str
    account_number: str
    ifsc: str
    avg_monthly_balance: float
    salary_credits_detected: bool
    avg_salary_credit: float
    transactions_24m: list[TransactionSummary]
    cash_deposit_ratio: float
    bounce_count: int
    emi_outflows: float


class Tradeline(TypedDict):
    account_type: str
    lender: str
    sanctioned_amount: float
    current_balance: float
    emi: float
    tenure_months: int
    dpd_history: list[int]
    status: str


class CreditReport(TypedDict):
    pan: str
    name: str
    score: int
    score_version: str
    active_tradelines: list[Tradeline]
    closed_tradelines_count: int
    total_enquiries_6m: int
    total_enquiries_12m: int
    dpd_max_12m: int
    overdue_amount: float
    report_date: str


class PANVerification(TypedDict):
    pan: str
    name: str
    father_name: str
    dob: str
    status: str
    aadhaar_seeding_status: str
    last_updated: str


class AadhaarDemographics(TypedDict):
    aadhaar_ref_id: str
    name: str
    dob: str
    gender: str
    address: str
    district: str
    state: str
    pincode: str
    mobile_hash: str
    verification_status: str


class GSTFilingRecord(TypedDict):
    return_type: str
    period: str
    date_of_filing: str
    status: str


class GSTDetails(TypedDict):
    gstin: str
    legal_name: str
    trade_name: str
    constitution: str
    date_of_registration: str
    status: str
    state: str
    annual_turnover_declared: float
    avg_monthly_turnover: float
    filing_regularity_pct: float
    recent_filings: list[GSTFilingRecord]
    itc_claimed_12m: float
    itc_as_pct_of_turnover: float


# ---------------------------------------------------------------------------
# Protocol (interface) definitions
# ---------------------------------------------------------------------------

@runtime_checkable
class AAClient(Protocol):
    """Account Aggregator client interface."""

    async def create_consent(
        self, mobile: str, fi_types: list[str] | None = None
    ) -> ConsentResponse: ...

    async def fetch_financial_data(self, consent_id: str) -> FinancialData: ...


@runtime_checkable
class BureauClient(Protocol):
    """Credit-bureau (CIBIL / Experian / CRIF) client interface."""

    async def pull_credit_report(self, pan: str) -> CreditReport: ...


@runtime_checkable
class PANVerificationClient(Protocol):
    """PAN verification (NSDL / UTIITSL) client interface."""

    async def verify_pan(self, pan: str) -> PANVerification: ...


@runtime_checkable
class AadhaarClient(Protocol):
    """Aadhaar eKYC (UIDAI) client interface."""

    async def verify_aadhaar_otp(
        self, aadhaar_number: str, otp: str
    ) -> AadhaarDemographics: ...


@runtime_checkable
class GSTNClient(Protocol):
    """GSTN lookup client interface."""

    async def get_gst_details(self, gstin: str) -> GSTDetails: ...


# ---------------------------------------------------------------------------
# Helper: generate 24-month transaction summaries
# ---------------------------------------------------------------------------

def _generate_transactions(
    avg_credit: float,
    avg_debit: float,
    starting_balance: float,
    *,
    salary_like: bool = False,
    volatility: float = 0.15,
) -> list[TransactionSummary]:
    """Create 24 months of plausible transaction summaries."""
    txns: list[TransactionSummary] = []
    balance = starting_balance
    # Walk backwards 24 months from a fixed reference date (Jan 2026)
    year, month = 2026, 1
    for i in range(24):
        m = month - i
        y = year
        while m <= 0:
            m += 12
            y -= 1
        # Add mild seasonality / jitter based on index
        factor = 1.0 + volatility * (0.5 - (i % 5) / 4)
        credit = round(avg_credit * factor, 2)
        debit = round(avg_debit * factor, 2)
        balance = round(balance + credit - debit, 2)
        if balance < 0:
            balance = round(abs(balance) * 0.3, 2)
        txns.append(
            TransactionSummary(
                month=f"{y}-{m:02d}",
                credit_total=credit,
                debit_total=debit,
                closing_balance=balance,
            )
        )
    txns.reverse()
    return txns


# ---------------------------------------------------------------------------
# Borrower profile data store
# ---------------------------------------------------------------------------

# Keyed by PAN for bureau / PAN-verification; secondary lookup by mobile
_PROFILES: dict[str, dict[str, Any]] = {
    # ---- Savitri — vegetable cart owner, Nagpur ----
    "ABCPS1234A": {
        "name": "Savitri Patel",
        "father_name": "Ramesh Patel",
        "dob": "1988-03-15",
        "gender": "F",
        "mobile": "9876543210",
        "aadhaar_ref": "XXXX-XXXX-1234",
        "address": "42, Gandhibagh Market, Nagpur, Maharashtra",
        "district": "Nagpur",
        "state": "Maharashtra",
        "pincode": "440002",
        "bank_name": "State Bank of India",
        "account_type": "savings",
        "account_number": "38291047562",
        "ifsc": "SBIN0001234",
        "avg_monthly_income": 15000.0,
        "avg_monthly_expense": 12500.0,
        "avg_balance": 8500.0,
        "salary_credits": False,
        "cash_deposit_ratio": 0.85,
        "bounce_count": 0,
        "emi_outflows": 0.0,
        "cibil_score": -1,  # no history
        "tradelines": [],
        "closed_tradelines": 0,
        "enquiries_6m": 0,
        "enquiries_12m": 0,
        "dpd_max_12m": 0,
        "overdue": 0.0,
        "gstin": None,
        "gst_turnover": 0.0,
        "segment": "self_employed",
    },
    # ---- Rajan — small manufacturer, Coimbatore ----
    "DEFPR5678B": {
        "name": "Rajan Krishnamurthy",
        "father_name": "Sundaram Krishnamurthy",
        "dob": "1979-07-22",
        "gender": "M",
        "mobile": "9845012345",
        "aadhaar_ref": "XXXX-XXXX-5678",
        "address": "12/A, SIDCO Industrial Estate, Coimbatore, Tamil Nadu",
        "district": "Coimbatore",
        "state": "Tamil Nadu",
        "pincode": "641021",
        "bank_name": "Indian Bank",
        "account_type": "current",
        "account_number": "6041027893",
        "ifsc": "IDIB000C042",
        "avg_monthly_income": 85000.0,
        "avg_monthly_expense": 62000.0,
        "avg_balance": 145000.0,
        "salary_credits": False,
        "cash_deposit_ratio": 0.30,
        "bounce_count": 1,
        "emi_outflows": 18500.0,
        "cibil_score": 720,
        "tradelines": [
            Tradeline(
                account_type="term_loan",
                lender="Indian Bank",
                sanctioned_amount=500000.0,
                current_balance=220000.0,
                emi=14500.0,
                tenure_months=48,
                dpd_history=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                status="active",
            ),
            Tradeline(
                account_type="credit_card",
                lender="HDFC Bank",
                sanctioned_amount=100000.0,
                current_balance=35000.0,
                emi=4000.0,
                tenure_months=0,
                dpd_history=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                status="active",
            ),
        ],
        "closed_tradelines": 1,
        "enquiries_6m": 1,
        "enquiries_12m": 2,
        "dpd_max_12m": 0,
        "overdue": 0.0,
        "gstin": "33DEFPR5678B1Z5",
        "gst_trade_name": "Rajan Auto Components",
        "gst_constitution": "Proprietorship",
        "gst_registration_date": "2018-07-01",
        "gst_annual_turnover": 1020000.0,
        "gst_filing_regularity": 95.0,
        "gst_itc_12m": 82000.0,
        "segment": "msme",
    },
    # ---- Meera — gig worker, Bengaluru ----
    "GHIMK9012C": {
        "name": "Meera Kulkarni",
        "father_name": "Vinayak Kulkarni",
        "dob": "1995-11-08",
        "gender": "F",
        "mobile": "9900112233",
        "aadhaar_ref": "XXXX-XXXX-9012",
        "address": "Flat 304, Whitefield Residency, Bengaluru, Karnataka",
        "district": "Bengaluru Urban",
        "state": "Karnataka",
        "pincode": "560066",
        "bank_name": "Kotak Mahindra Bank",
        "account_type": "savings",
        "account_number": "7712098345",
        "ifsc": "KKBK0000123",
        "avg_monthly_income": 45000.0,
        "avg_monthly_expense": 38000.0,
        "avg_balance": 22000.0,
        "salary_credits": False,
        "cash_deposit_ratio": 0.10,
        "bounce_count": 2,
        "emi_outflows": 6500.0,
        "cibil_score": 680,
        "tradelines": [
            Tradeline(
                account_type="personal_loan",
                lender="Bajaj Finance",
                sanctioned_amount=150000.0,
                current_balance=98000.0,
                emi=6500.0,
                tenure_months=36,
                dpd_history=[0, 0, 0, 30, 0, 0, 0, 0, 0, 0, 0, 0],
                status="active",
            ),
        ],
        "closed_tradelines": 0,
        "enquiries_6m": 3,
        "enquiries_12m": 5,
        "dpd_max_12m": 30,
        "overdue": 0.0,
        "gstin": None,
        "gst_turnover": 0.0,
        "segment": "gig_worker",
    },
    # ---- Prakash — kirana store, rural UP ----
    "JKLPN3456D": {
        "name": "Prakash Nishad",
        "father_name": "Harilal Nishad",
        "dob": "1984-01-25",
        "gender": "M",
        "mobile": "9451234567",
        "aadhaar_ref": "XXXX-XXXX-3456",
        "address": "Village Bhatpar Rani, Block Deoria, Deoria, Uttar Pradesh",
        "district": "Deoria",
        "state": "Uttar Pradesh",
        "pincode": "274701",
        "bank_name": "Bank of Baroda",
        "account_type": "savings",
        "account_number": "21340056789",
        "ifsc": "BARB0DEORIA",
        "avg_monthly_income": 25000.0,
        "avg_monthly_expense": 20000.0,
        "avg_balance": 12000.0,
        "salary_credits": False,
        "cash_deposit_ratio": 0.70,
        "bounce_count": 0,
        "emi_outflows": 0.0,
        "cibil_score": -1,  # first-time borrower
        "tradelines": [],
        "closed_tradelines": 0,
        "enquiries_6m": 0,
        "enquiries_12m": 0,
        "dpd_max_12m": 0,
        "overdue": 0.0,
        "gstin": "09JKLPN3456D1Z8",
        "gst_trade_name": "Prakash General Store",
        "gst_constitution": "Proprietorship",
        "gst_registration_date": "2021-04-01",
        "gst_annual_turnover": 300000.0,
        "gst_filing_regularity": 75.0,
        "gst_itc_12m": 18000.0,
        "segment": "msme",
    },
}

# Mobile → PAN lookup
_MOBILE_TO_PAN: dict[str, str] = {
    p["mobile"]: pan for pan, p in _PROFILES.items()
}


def _profile_for_pan(pan: str) -> dict[str, Any]:
    if pan in _PROFILES:
        return _PROFILES[pan]
    raise KeyError(f"No mock profile for PAN {pan}")


def _profile_for_mobile(mobile: str) -> dict[str, Any]:
    pan = _MOBILE_TO_PAN.get(mobile)
    if pan is None:
        raise KeyError(f"No mock profile for mobile {mobile}")
    return _PROFILES[pan]


def _pan_for_mobile(mobile: str) -> str:
    pan = _MOBILE_TO_PAN.get(mobile)
    if pan is None:
        raise KeyError(f"No mock profile for mobile {mobile}")
    return pan


# ---------------------------------------------------------------------------
# Mock implementations
# ---------------------------------------------------------------------------

class MockAAClient:
    """Mock Account Aggregator client returning preset financial data."""

    _consent_counter: int = 0
    _consent_store: dict[str, str] = {}  # consent_id → mobile

    async def create_consent(
        self, mobile: str, fi_types: list[str] | None = None
    ) -> ConsentResponse:
        MockAAClient._consent_counter += 1
        consent_id = f"MOCK-CONSENT-{MockAAClient._consent_counter:06d}"
        self._consent_store[consent_id] = mobile
        return ConsentResponse(
            consent_id=consent_id,
            status="ACTIVE",
            created_at=datetime.utcnow().isoformat(),
            expiry="2027-01-01T00:00:00",
            fi_types=fi_types or ["DEPOSIT", "RECURRING_DEPOSIT"],
        )

    async def fetch_financial_data(self, consent_id: str) -> FinancialData:
        mobile = self._consent_store.get(consent_id)
        if mobile is None:
            raise ValueError(f"Unknown consent_id: {consent_id}")
        p = _profile_for_mobile(mobile)
        txns = _generate_transactions(
            avg_credit=p["avg_monthly_income"],
            avg_debit=p["avg_monthly_expense"],
            starting_balance=p["avg_balance"],
            salary_like=p["salary_credits"],
            volatility=0.20 if p["cash_deposit_ratio"] > 0.5 else 0.10,
        )
        return FinancialData(
            account_holder=p["name"],
            bank_name=p["bank_name"],
            account_type=p["account_type"],
            account_number=p["account_number"],
            ifsc=p["ifsc"],
            avg_monthly_balance=p["avg_balance"],
            salary_credits_detected=p["salary_credits"],
            avg_salary_credit=p["avg_monthly_income"] if p["salary_credits"] else 0.0,
            transactions_24m=txns,
            cash_deposit_ratio=p["cash_deposit_ratio"],
            bounce_count=p["bounce_count"],
            emi_outflows=p["emi_outflows"],
        )


class MockBureauClient:
    """Mock credit-bureau client returning preset CIBIL reports."""

    async def pull_credit_report(self, pan: str) -> CreditReport:
        p = _profile_for_pan(pan)
        return CreditReport(
            pan=pan,
            name=p["name"],
            score=p["cibil_score"],
            score_version="CIBIL_V2",
            active_tradelines=p["tradelines"],
            closed_tradelines_count=p["closed_tradelines"],
            total_enquiries_6m=p["enquiries_6m"],
            total_enquiries_12m=p["enquiries_12m"],
            dpd_max_12m=p["dpd_max_12m"],
            overdue_amount=p["overdue"],
            report_date=date.today().isoformat(),
        )


class MockPANVerificationClient:
    """Mock PAN verification client."""

    async def verify_pan(self, pan: str) -> PANVerification:
        p = _profile_for_pan(pan)
        return PANVerification(
            pan=pan,
            name=p["name"],
            father_name=p["father_name"],
            dob=p["dob"],
            status="valid",
            aadhaar_seeding_status="linked",
            last_updated=date.today().isoformat(),
        )


class MockAadhaarClient:
    """Mock Aadhaar eKYC client."""

    async def verify_aadhaar_otp(
        self, aadhaar_number: str, otp: str
    ) -> AadhaarDemographics:
        # Map by last 4 digits of the aadhaar_ref
        suffix = aadhaar_number[-4:]
        matched: dict[str, Any] | None = None
        for p in _PROFILES.values():
            ref: str = p["aadhaar_ref"]
            if ref.endswith(suffix):
                matched = p
                break
        if matched is None:
            raise ValueError(f"No mock profile for Aadhaar ending {suffix}")
        return AadhaarDemographics(
            aadhaar_ref_id=matched["aadhaar_ref"],
            name=matched["name"],
            dob=matched["dob"],
            gender=matched["gender"],
            address=matched["address"],
            district=matched["district"],
            state=matched["state"],
            pincode=matched["pincode"],
            mobile_hash=f"sha256:{matched['mobile'][:4]}****",
            verification_status="success",
        )


class MockGSTNClient:
    """Mock GSTN lookup client."""

    async def get_gst_details(self, gstin: str) -> GSTDetails:
        # Find profile whose gstin matches
        matched: dict[str, Any] | None = None
        for p in _PROFILES.values():
            if p.get("gstin") == gstin:
                matched = p
                break
        if matched is None:
            raise ValueError(f"No mock profile for GSTIN {gstin}")

        annual = matched["gst_annual_turnover"]
        avg_monthly = round(annual / 12, 2)
        itc_pct = round(
            matched["gst_itc_12m"] / annual * 100, 2
        ) if annual > 0 else 0.0

        # Generate 12 months of filing records
        filings: list[GSTFilingRecord] = []
        year, month = 2026, 1
        regularity = matched["gst_filing_regularity"]
        for i in range(12):
            m = month - i
            y = year
            while m <= 0:
                m += 12
                y -= 1
            # Simulate occasional missed filings based on regularity
            filed = (i * 8.33) < regularity  # deterministic skip pattern
            filings.append(
                GSTFilingRecord(
                    return_type="GSTR-3B",
                    period=f"{y}-{m:02d}",
                    date_of_filing=f"{y}-{m:02d}-11" if filed else "",
                    status="Filed" if filed else "Not Filed",
                )
            )
        filings.reverse()

        return GSTDetails(
            gstin=gstin,
            legal_name=matched["name"],
            trade_name=matched.get("gst_trade_name", matched["name"]),
            constitution=matched.get("gst_constitution", "Proprietorship"),
            date_of_registration=matched.get("gst_registration_date", "2020-01-01"),
            status="Active",
            state=matched["state"],
            annual_turnover_declared=annual,
            avg_monthly_turnover=avg_monthly,
            filing_regularity_pct=regularity,
            recent_filings=filings,
            itc_claimed_12m=matched["gst_itc_12m"],
            itc_as_pct_of_turnover=itc_pct,
        )
