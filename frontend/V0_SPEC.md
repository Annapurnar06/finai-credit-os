# FINAI Credit OS — v0 Lender Portal Specification

## Design System Foundation

### Aesthetic Direction: "Institutional Warmth"

The credit officer stares at this screen for 8 hours. Every pixel must serve a decision. This is not a marketing dashboard — it is a judgment instrument where a single click approves ₹25 lakh that changes a family's trajectory. The design must convey: *we take this seriously, and so should you.*

**Tone**: Refined authority with warmth. Bloomberg Terminal's information density meets Linear's spatial clarity. Dense where data demands it, spacious where decisions need breathing room.

**What this is NOT**: Generic SaaS blue. Purple gradient hero sections. Rounded-everything with Inter font. Cookie-cutter shadcn defaults with no personality. Fintech "trust us" illustration pages.

### Design Tokens

```
Palette (Dark mode primary — credit officers work long hours):
  --bg-primary: #0C0E12          // Near-black with subtle warm undertone
  --bg-surface: #14161C          // Card/panel surface
  --bg-elevated: #1C1F28         // Hover, active states
  --bg-inset: #0A0B0F            // Sunken areas, input fields
  
  --text-primary: #E8E4DF        // Warm off-white, never pure white
  --text-secondary: #8B8680      // Muted warm gray
  --text-tertiary: #5C5752       // Labels, timestamps
  
  --accent-gold: #C8A862         // Primary accent — trust, authority, Indian context
  --accent-gold-muted: #8A7644   // Subtle gold for borders, dividers
  
  Risk signal colors (the ONLY place saturated color appears):
  --risk-green: #2D9D5E          // Approval, safe, AUTO-APPROVED
  --risk-amber: #D4912E          // Caution, review required
  --risk-red: #C94444            // Hard reject, critical flag
  --risk-red-bg: #1F1214         // Red flag card background
  --risk-amber-bg: #1C1610       // Amber flag card background
  --risk-green-bg: #0F1A14       // Green approval background

Typography:
  Display/Headings: "DM Serif Display" — editorial authority, financial gravitas
  Body/Data: "DM Sans" — clean, wide letterforms, excellent at small sizes
  Monospace/Numbers: "JetBrains Mono" — financial figures must be monospaced
  
  Scale: 11px (labels) / 13px (body) / 15px (emphasis) / 20px (section) / 28px (page)
  Numbers always rendered in JetBrains Mono, right-aligned in columns.
  INR amounts: ₹ symbol in text-secondary, figure in text-primary, always comma-formatted.

Spacing:
  Base unit: 4px. Cards: 16px padding. Sections: 32px gap. Page margin: 48px.
  
Motion:
  DESIGN_VARIANCE: 4 (professional, not experimental)
  MOTION_INTENSITY: 3 (subtle — fade-in on mount, smooth hover transitions)
  VISUAL_DENSITY: 8 (high density — this is a working tool, not a marketing page)
  
  Transitions: 150ms ease-out for hover, 200ms for panel open, 300ms for page transitions.
  No spring physics. No parallax. No scroll-triggered animations. This is a workplace.
```

### Component Conventions

- **Cards**: 1px border `rgba(200,168,98,0.08)`, no shadow. Hover: border brightens to `rgba(200,168,98,0.15)`.
- **Badges/Pills**: Risk badges are the ONLY saturated elements. Small, 10px font, uppercase, tight letter-spacing. `GREEN` / `AMBER` / `RED` on muted tinted backgrounds.
- **Tables**: Hairline borders `#1C1F28`. Row hover: `bg-elevated`. Fixed header. Monospaced numbers right-aligned.
- **Buttons**: Primary = gold outline, not filled. Secondary = ghost with border. Destructive = red outline. All 32px height, 13px font.
- **Empty states**: Single line of text in `text-tertiary`. No illustrations. No emojis.
- **Loading**: Subtle pulse on the data area only. Never a full-page spinner.

---

## Screen 1: LOS Pipeline Dashboard

### Job to Be Done
Credit officer opens the app in the morning. They need to answer in one glance: *How many applications need my attention today? What's stuck? What auto-approved overnight?*

### Surface Model
- **Primary surface**: Pipeline Kanban view (horizontal columns = stages)
- **Supporting surface**: Stats bar at top (counts per stage, total value)
- **Ambient signals**: Time-in-stage indicators on each card

### v0 Prompt

```
Build a loan origination pipeline dashboard for an Indian NBFC credit operations platform.

FRAMEWORK: Next.js 15 App Router + Tailwind CSS + shadcn/ui.

PAGE LAYOUT:
- Full viewport, no scrolling on the main frame. The Kanban columns scroll individually.
- Left sidebar (240px, collapsible): navigation with sections "Pipeline", "HITL Queue", "Borrowers", "Analytics", "Policies", "Settings". Active item has a gold left border accent. Logo at top: "FINAI" in DM Serif Display, gold color, with subtitle "Credit OS" in DM Sans small caps.
- Top bar: page title "Loan Pipeline", current date, and user avatar + role badge ("Credit Officer" / "RM" / "Ops Supervisor").

STATS BAR (below top bar, full width, 64px height):
Six metric cards in a horizontal row, each showing:
  - Label in small uppercase text-tertiary (11px, letter-spacing 0.05em)
  - Value in JetBrains Mono 20px text-primary
  - Delta badge (e.g., "+3 today" in green or "−2" in red, 10px)
Metrics: "Documents Submitted" | "Extracting" | "Proposal Generated" | "HITL Pending" | "Approved Today" | "Rejected Today"
Below the six cards: a thin progress bar showing total pipeline value (sum of all active loan amounts) with gold fill.

KANBAN VIEW (main area):
Six columns, each representing a pipeline stage:
1. "Documents Submitted" (icon: upload)
2. "Extracting" (icon: scan, animated subtle pulse)  
3. "Proposal Ready" (icon: file-check)
4. "HITL Pending" (icon: user-check, gold accent — this is the action column)
5. "Approved" (icon: check-circle, green)
6. "Rejected" (icon: x-circle, red)

Each column has:
- Header: stage name, count badge, total ₹ value
- Vertically scrollable card list

APPLICATION CARDS (inside columns):
Each card (full column width, ~120px height) contains:
- Row 1: Borrower name (DM Sans 13px semibold) + Segment badge ("Salaried" / "MSME" / "Gig" — small pill, ghost style)
- Row 2: Product type + Loan amount in JetBrains Mono (e.g., "Personal Loan · ₹5,00,000")
- Row 3: Risk level badge (GREEN/AMBER/RED) + Time in stage ("2h 15m" / "1d 4h") 
- Row 4 (only if HITL Pending): "Review →" button, gold outline, right-aligned
- Bottom: thin progress bar showing how far through the pipeline (gold fill proportional to stage)

Cards in "HITL Pending" column have a subtle left border in gold to draw the eye.
Cards in "Extracting" have a subtle animated shimmer effect on the progress bar.

INTERACTION:
- Click any card → navigates to /applications/[id] (the Decision Brief screen)
- Cards are NOT draggable (status driven by agent pipeline, not manual)
- Column counts update via polling (simulate with static data for now)

STATES TO HANDLE:
- Empty column: show "No applications" in text-tertiary, centered
- Loading: cards show skeleton with pulse animation
- Error: red banner at top of column "Pipeline sync error — retrying"

SAMPLE DATA (use realistic Indian names and amounts):
Column 1 (Documents Submitted): 
  - Arun Mehta, Salaried, Personal Loan ₹3,50,000, GREEN, 45m
  - Deepa Sharma, MSME, Business Loan ₹8,00,000, AMBER, 1h 20m

Column 2 (Extracting):
  - Vikram Reddy, Self-Employed, LAP ₹15,00,000, AMBER, 30m

Column 3 (Proposal Ready):
  - Sunita Devi, Agriculture, Agri Loan ₹2,00,000, GREEN, 2h

Column 4 (HITL Pending):
  - Savitri Bai Patil, MSME, Personal Loan ₹1,00,000, AMBER, 4h 30m
  - Meera Srinivasan, Gig Worker, Personal Loan ₹3,00,000, AMBER, 1h 15m
  - Prakash Kumar Yadav, MSME, Business Loan ₹2,00,000, RED, 6h

Column 5 (Approved):
  - Rajan Krishnamurthy, Salaried, Personal Loan ₹5,00,000, GREEN, auto-approved

Column 6 (Rejected):
  - Amit Shah, Self-Employed, Personal Loan ₹10,00,000, RED, bureau_score_below_threshold

DESIGN RULES:
- Dark theme only. Background #0C0E12. Cards #14161C with 1px border rgba(200,168,98,0.08).
- Typography: DM Serif Display for page title. DM Sans for everything else. JetBrains Mono for all numbers/amounts.
- Gold accent (#C8A862) used ONLY for: active nav item, HITL column highlight, primary buttons, progress bars.
- Risk colors (green/amber/red) used ONLY for risk badges. Never for decorative elements.
- No illustrations, no emojis, no decorative icons. Every element serves a decision.
- Amounts in Indian comma format: ₹15,00,000 (not ₹1,500,000).
```

---

## Screen 2: Credit Officer Decision Brief

### Job to Be Done
Credit officer clicked "Review" on an HITL-pending application. They need to make an approve/reject decision in under 3 minutes. They need to see: *who is this person, can they repay, what are the risks, and what did the agents find?*

### Surface Model
- **Primary surface**: Decision action panel (approve/reject with mandatory rationale)
- **Supporting surface**: 1-page financial summary compiled by agents
- **Ambient signals**: Risk flag badges, extraction confidence indicators, policy version tag

### Hierarchy
1. Borrower identity + loan ask (instant orientation — 2 seconds)
2. Risk assessment summary (RED/AMBER/GREEN flags — 5 seconds)
3. Financial evidence (income, DBR, triangulation — 30 seconds)
4. Agent extraction details (expandable, for deep-dive — optional)
5. Decision action (approve/reject — the climax)

### v0 Prompt

```
Build a credit officer decision brief page for an Indian NBFC loan origination system. This is the most critical screen — the officer reads this and approves or rejects a loan.

FRAMEWORK: Next.js 15 App Router + Tailwind CSS + shadcn/ui.

PAGE STRUCTURE (two-column, 65/35 split):

LEFT COLUMN (65%, scrollable) — "The Evidence":

SECTION 1: Borrower Header (sticky, 80px)
  - Row: Borrower name in DM Serif Display 24px + PAN in monospace text-secondary
  - Row: Segment badge ("MSME") + Product ("Personal Loan") + Amount in gold monospace ("₹1,00,000")
  - Row: Application ID (monospace, small) + Time in pipeline ("Submitted 4h 30m ago") + Policy version tag ("v1.0.0")

SECTION 2: Risk Assessment Panel (the most important visual on the page)
  A horizontal bar with three zones:
  - RED flags count (if any — displayed as a red-tinted card with count + descriptions)
  - AMBER flags count (amber-tinted card)  
  - GREEN (if clean — single green-tinted card saying "No risk flags")
  
  Each flag card contains:
  - Flag icon (shield-alert for RED, alert-triangle for AMBER)
  - Description text (e.g., "Borrower does not meet eligibility criteria")
  - Source agent name in monospace small text (e.g., "EligibilityEvaluator")
  
  If there are RED flags, the entire section has a subtle red left border.

SECTION 3: Financial Summary (4-column grid of metric cards)
  Card 1: "Monthly Income" — ₹ value in large monospace, source tag below ("bank_statement + salary_slip")
  Card 2: "Bureau Score" — score in large monospace, colored by tier (green >720, amber 650-720, red <650). "CIBIL" label.
  Card 3: "DBR Ratio" — percentage in large monospace with a half-circle gauge visual. Threshold line at 40% and 50%.
  Card 4: "Max Eligible Loan" — ₹ value in large monospace, if eligible. "INELIGIBLE" in red if not.

SECTION 4: Income Triangulation (critical for RBI compliance)
  Horizontal bar chart showing income from each source:
  - Bank Statement: ₹85,000/mo (bar width proportional)
  - Salary Slip: ₹72,900/mo
  - ITR: ₹45,000/mo (if applicable)
  - GST-derived: ₹23,125/mo (if applicable)
  
  Below the chart: "Verified Income: ₹XX,XXX" in gold + "Confidence: XX%" with a small confidence bar.
  If sources disagree by >20%: amber warning "Income mismatch detected — XX% deviation across sources"

SECTION 5: Document Extraction Results (expandable accordion)
  One row per document type extracted:
  - Doc type icon + name (e.g., "PAN Card")
  - Status badge: success (green checkmark) / low_confidence (amber ~) / failure (red x)
  - Confidence percentage in monospace
  - Expand arrow → shows extracted fields as a key-value table (key in text-secondary, value in text-primary monospace)
  
  Example expanded PAN row:
    pan_number: ABCPS1234A
    name: SAVITRI BAI PATIL
    dob: 20/08/1978
    fathers_name: RAMESH PATIL
    status: valid

SECTION 6: Agent Memory (if any prior interactions exist)
  Heading: "Borrower History" with memory count badge
  List of memory items, each showing:
  - Timestamp + channel badge ("voice" / "chat" / "los_pipeline")
  - Memory content text
  - Source agent in monospace small text
  If no memories: "First interaction — no prior history" in text-tertiary

RIGHT COLUMN (35%, sticky) — "The Decision":

TOP: Recommendation card
  - If auto-approve eligible: large green-tinted card "AUTO-APPROVE ELIGIBLE" with ratify button
  - If HITL required: neutral card "MANUAL REVIEW REQUIRED" with reason list

MIDDLE: Decision form
  - Two large buttons side by side:
    - "Approve" — gold outline, hover fills gold. Icon: check.
    - "Reject" — red outline, hover fills red. Icon: x.
  - Below buttons: mandatory textarea "Decision Rationale" (min 20 characters)
    - Placeholder: "State your reasoning for this decision (mandatory per RBI Fair Practices Code)"
  - Below textarea: dropdown "Deviation Type" (if approving despite flags): "None" / "Minor — within authority" / "Major — escalate to credit committee"
  - Submit button: "Submit Decision" — disabled until rationale is filled

BOTTOM: Audit Trail card
  - "This decision will be logged with your ID, timestamp, policy version, and full rationale."
  - "Decision cannot be reversed after 24 hours."
  - Small icon: lock

SAMPLE DATA (use Savitri Bai Patil scenario):
  Borrower: SAVITRI BAI PATIL, PAN: ABCPS1234A, MSME segment
  Product: Personal Loan ₹1,00,000
  Risk flags: 1 RED (ineligible), 3 AMBER (DBR >50%, high loan-to-income, missing documents)
  Monthly income: ₹0 (from passbook — no salary detected)
  Bureau score: N/A (no credit history)
  DBR: 100% (no income detected)
  Documents: PAN (success), Passbook (success), Utility Bill (success)
  Missing: bank_statement, salary_slip
  Memories: "PanDataAgent extracted pan: pan_number=ABCPS1234A, name=SAVITRI BAI PATIL"

DESIGN RULES:
- Same dark theme, typography, and color system as Screen 1.
- Numbers ALWAYS in JetBrains Mono. Labels ALWAYS in DM Sans uppercase 11px.
- Risk colors are signal, not decoration. A page with 0 flags should feel calm and spacious. A page with 3 RED flags should feel urgent through density and color weight, not through animation or size inflation.
- The right column (decision form) must be visible without scrolling. The officer should never have to scroll to find the approve/reject buttons.
- Every data point shows its provenance: which agent produced it, from which document, at what confidence.
```

---

## Screen 3: Borrower 360 Profile

### Job to Be Done
RM wants a complete picture of a borrower across all touchpoints — application history, documents, financial profile, interaction history, risk evolution. *"Tell me everything about Rajan before my call with him."*

### Surface Model
- **Primary surface**: Entity profile with tabbed sections
- **Supporting surface**: Interaction timeline (right rail)
- **Ambient signals**: Segment badge, risk tier, relationship tenure

### v0 Prompt

```
Build a borrower 360 profile page for an Indian lending platform. This gives the Relationship Manager a complete view of one borrower.

FRAMEWORK: Next.js 15 App Router + Tailwind CSS + shadcn/ui.

PAGE LAYOUT (full width, scrollable):

HEADER (sticky, 96px, bg-surface):
  Left: Borrower avatar placeholder (initials in circle, gold border) + Name in DM Serif Display 28px + PAN monospace
  Center: Three stat pills horizontally:
    - Segment: "Salaried" (ghost badge)
    - Relationship: "New Borrower" or "2 years" 
    - Risk tier: "LOW" (green) / "MEDIUM" (amber) / "HIGH" (red) badge
  Right: Action buttons — "Start Application", "Schedule Call", "View Documents"

TABS (below header): "Overview" | "Financial Profile" | "Documents" | "Applications" | "Interactions" | "Memory"

TAB: OVERVIEW (default)
  Two-column layout (60/40):
  
  Left column:
    CARD: Identity
      Key-value grid (2 columns):
      Name | PAN | DOB | Age | Mobile (masked) | Email (masked) | Address | Segment | Employer
      Each value in monospace. Sensitive fields show masked with "Reveal" link.
    
    CARD: Income Summary
      Horizontal bar chart (same style as Decision Brief triangulation):
      Sources with amounts and confidence indicators.
      Bottom line: "Verified Monthly Income: ₹XX,XXX (confidence: XX%)"
    
    CARD: Liability Summary  
      - Bureau Score gauge (half-circle, color-coded by tier)
      - Active Loans table: Lender | Type | Outstanding | EMI | DPD status
      - Total EMI | DBR ratio | Max eligible new EMI
    
  Right column:
    CARD: Recent Activity Timeline (vertical, chronological)
      Each entry: timestamp + icon + description + agent/channel badge
      Examples:
      - "Application submitted via API" (blue dot, 4h ago)
      - "PAN extracted — ABCPS1234A valid" (green dot, 4h ago)
      - "Sent to HITL review — 4 risk flags" (amber dot, 3h ago)
      - "Credit officer reviewed — approved with deviation" (gold dot, 1h ago)
    
    CARD: Entity Graph (simplified — shows linked identities)
      Visual: borrower node in center, connected to:
      - PAN node
      - Bank accounts (with bank names)
      - GSTIN (if any)
      - Mobile numbers
      Each connection shows source + last verified date.
      Render as a simple node diagram with lines, not a force-directed graph.

TAB: FINANCIAL PROFILE
  Full-width cards:
  
  CARD: Monthly Cash Flow Chart (12 months)
    Line chart: credits (green line) vs debits (red line) vs balance (gold line)
    X-axis: months. Y-axis: ₹ amounts.
    Below chart: table with the same data in monospace columns.
  
  CARD: Income Pattern Analysis
    Summary text generated by agent:
    "Regular salary credits of ₹85,000/month detected from TCS Ltd. 
     No irregular cash deposits. 1 EMI outflow of ₹12,000 to ICICI Bank.
     Income pattern: STABLE. Confidence: HIGH."
    
  CARD: GST/Business Performance (if MSME)
    Quarterly turnover bar chart + filing regularity score.

TAB: DOCUMENTS
  Grid of document cards (3 columns):
  Each card: doc type icon + filename + upload date + extraction status badge
  Click → expands to show extracted fields
  Missing documents highlighted with dashed border and "Request" button

TAB: APPLICATIONS
  Table of all loan applications:
  App ID | Date | Product | Amount | Status | Decision | Officer
  Click row → navigates to Decision Brief

TAB: INTERACTIONS
  Full timeline of all touchpoints:
  Each entry: date + time + channel icon (phone/chat/email/whatsapp/system) + summary + agent
  Filter bar: channel type, date range

TAB: MEMORY
  All Mem0 memories for this borrower:
  Each memory card: content + source agent + category badge + confidence score + timestamp
  Search bar at top for semantic memory search

SAMPLE DATA (use Rajan Krishnamurthy — the approved clean case):
  Name: RAJAN KRISHNAMURTHY, PAN: DEFPR5678B, DOB: 15/03/1985, Age: 41
  Segment: Salaried, Employer: TCS Limited
  Bureau Score: 765, Active Loans: 1 (Car loan ICICI ₹1,80,000 outstanding)
  Monthly Income: ₹85,000, DBR: 14.1%
  Application: Personal Loan ₹5,00,000 — AUTO-APPROVED
  Documents: PAN, Bank Statement, Salary Slip, CIBIL Report — all extracted successfully

DESIGN: Same system. DM Serif Display for borrower name and section titles. Dense data layout. Every number in JetBrains Mono. Gold accents only for primary actions and the entity graph connections.
```

---

## Screen 4: HITL Review Queue

### Job to Be Done
Credit officer checks the queue first thing each morning. They need to prioritize: *which application should I review first — the one that's been waiting longest, the one with the highest value, or the one with the most flags?*

### Surface Model
- **Primary surface**: Sortable, filterable table of pending reviews
- **Supporting surface**: Quick-view side panel (click row to preview without navigating)
- **Ambient signals**: Time-in-queue indicators with color escalation (>4h amber, >8h red)

### v0 Prompt

```
Build an HITL (Human-in-the-Loop) review queue for credit officers at an Indian NBFC. This is where they see all applications awaiting their decision.

FRAMEWORK: Next.js 15 App Router + Tailwind CSS + shadcn/ui.

PAGE LAYOUT:
- Same sidebar navigation as Screen 1 (HITL Queue item active, gold left border).
- Main area: full width table with quick-view side panel.

TOP BAR:
  Left: "HITL Review Queue" in DM Serif Display 24px
  Center: Three filter pills — "All (8)" | "Assigned to Me (3)" | "Unassigned (5)"
  Right: Sort dropdown — "Time in Queue (longest first)" / "Loan Amount (highest first)" / "Risk Level (highest first)"

TABLE (full width, scrollable):
  Columns:
  1. Priority indicator (vertical bar: red/amber/green based on wait time + risk combo)
  2. Borrower Name (DM Sans 13px semibold) + PAN (monospace small, text-secondary)
  3. Segment badge (pill)
  4. Product Type
  5. Loan Amount (JetBrains Mono, right-aligned, gold text for amounts >₹5,00,000)
  6. Risk Level — composite badge showing flag count by color: "2R 1A" meaning 2 red, 1 amber
  7. Time in Queue — color-coded: green <2h, amber 2-8h, red >8h. Shows exact duration.
  8. Assigned To — officer name or "Unassigned" in text-tertiary
  9. Action — "Review →" button (gold outline for unreviewed, ghost for already opened)

  Table features:
  - Fixed header on scroll
  - Row hover: bg-elevated
  - Click row: opens side panel (does not navigate away)
  - Selected row: subtle gold left border + bg-elevated persistent

SIDE PANEL (slides in from right, 480px wide, when a row is clicked):
  Panel header: Borrower name + "Quick Preview" label + "Open Full Brief →" link
  
  Panel content (condensed version of Decision Brief):
  - Risk flags summary (count badges: RED/AMBER/GREEN)
  - Top 3 flag descriptions (truncated to 1 line each)
  - Financial snapshot: Income | Bureau Score | DBR | Max Eligible (2x2 grid)
  - Extraction status: list of doc types with success/failure icons
  - "Review This Application →" button (gold, full width, navigates to Decision Brief page)
  
  Panel footer: 
  - Quick actions: "Assign to Me" / "Escalate to Committee" / "Request More Documents"

EMPTY STATE:
  If no pending reviews: centered text "No applications pending review" in DM Serif Display 20px, text-tertiary.
  Below: "Applications auto-approved by policy are not shown here."

SAMPLE DATA (8 rows):
1. Savitri Bai Patil | MSME | Personal Loan | ₹1,00,000 | 1R 3A | 4h 30m | Unassigned
2. Meera Srinivasan | Gig Worker | Personal Loan | ₹3,00,000 | 1R 1A | 1h 15m | Unassigned
3. Prakash Kumar Yadav | MSME | Business Loan | ₹2,00,000 | 1R 0A | 6h 00m | Priya Sharma
4. Anita Gupta | Salaried | Personal Loan | ₹7,50,000 | 0R 2A | 3h 45m | Unassigned
5. Rajesh Patel | Self-Employed | LAP | ₹25,00,000 | 0R 1A | 8h 20m | Vikram Singh
6. Farhan Khan | MSME | Business Loan | ₹4,00,000 | 2R 2A | 12h 05m | Unassigned
7. Lakshmi Nair | Agriculture | Agri Loan | ₹1,50,000 | 0R 1A | 2h 00m | Unassigned
8. Suresh Yadav | Salaried | Personal Loan | ₹2,25,000 | 0R 0A | 30m | Priya Sharma

DESIGN: Same system. The priority bar on the left of each row is the strongest visual signal — it tells the officer where to focus before they even read the data. Farhan Khan (12h, 2R 2A) should visually scream "handle me now" through the red priority bar and red time indicator, without any animation or size change. Just color weight and position.
```

---

## Screen 5: Agent Observability Panel

### Job to Be Done
Ops supervisor wants to understand: *are the agents performing well? Which documents are failing extraction? How much are we spending on LLM calls? Are there systemic issues?*

### v0 Prompt

```
Build an agent observability dashboard for an AI lending platform operations supervisor. This shows agent performance, extraction accuracy, pipeline health, and LLM costs.

FRAMEWORK: Next.js 15 App Router + Tailwind CSS + shadcn/ui.

PAGE LAYOUT:
- Same sidebar (Analytics active).
- Main area: stats row + two-column grid of panels.

STATS ROW (6 metrics, same style as Screen 1):
  "Applications Today: 47" | "Avg Pipeline Time: 2h 14m" | "Auto-Approve Rate: 34%" | "HITL Override Rate: 8%" | "Extraction Accuracy: 96.2%" | "LLM Cost Today: ₹847"

LEFT COLUMN:

  CARD: Extraction Agent Performance (table)
    Columns: Agent Name | Documents Processed | Success Rate | Avg Confidence | Avg Latency
    Rows for each agent: PanDataAgent, BankStatementAgent, SalarySlipAgent, ITReturnAgent, GSTReturnAgent, CreditBureauAgent, etc.
    Color-code success rate: >95% green, 85-95% amber, <85% red.
    Sort by success rate ascending (worst performers at top).

  CARD: Pipeline Throughput (line chart, last 7 days)
    Three lines: Submitted / Approved / Rejected per day.
    X-axis: dates. Y-axis: count.

RIGHT COLUMN:

  CARD: Risk Flag Distribution (horizontal stacked bar chart)
    Shows count of RED/AMBER/GREEN flags by category:
    eligibility | documentation | extraction | proposal

  CARD: LLM Usage Breakdown (table)
    Columns: Model | Calls Today | Tokens Used | Cost (₹) | Avg Latency
    Rows: claude-haiku-4.5 | claude-sonnet-4 | mock-llm-v1
    Total row at bottom in bold.

  CARD: Recent Incidents (if any)
    List of last 5 agent failures:
    Timestamp | Agent | Error | Application ID | Status (resolved/open)
    Each row clickable to expand error details.

DESIGN: Same system. This page is denser than others — VISUAL_DENSITY: 9. Small fonts, tight spacing. The supervisor is comfortable with data overload. Every chart should have a subtle gold accent line or fill. No chart libraries — use pure CSS/SVG bars. Keep it lean.
```

---

## Screen 6: Login / Auth Page

### v0 Prompt

```
Build a login page for FINAI Credit OS — an AI-native lending operations platform for Indian NBFCs.

FRAMEWORK: Next.js 15 App Router + Tailwind CSS.

LAYOUT: Full viewport, two columns (50/50).

LEFT COLUMN (brand panel):
  Background: #0C0E12 with a subtle gold geometric pattern (thin lines forming an abstract hexagonal grid — represents the agent network/decision graph).
  Centered content:
  - "FINAI" in DM Serif Display 48px, gold color (#C8A862)
  - "Credit OS" below in DM Sans 16px, small caps, text-secondary
  - Tagline below: "AI-native lending for India's 560M unserved" in DM Sans 13px, text-tertiary
  - Three small stat lines (fade-in staggered):
    "100 agents · Full loan lifecycle"
    "DPI-first · RBI compliant by design"
    "Voice-first for rural borrowers"

RIGHT COLUMN (form panel):
  Background: #14161C
  Centered vertically and horizontally, max-width 360px:
  - "Sign In" in DM Serif Display 28px
  - Email input (dark inset bg, 1px gold-muted border on focus)
  - Password input (same style, show/hide toggle)
  - "Sign In" button (full width, gold outline, hover fills gold)
  - Divider: "or continue with"
  - "Sign in with SSO" button (ghost style)
  - Footer: "FINAI Credit OS v0.1.0 · Contact admin for access"

NO: illustrations, stock photos, gradients, rounded pills with Inter font, "Welcome back!" copy. This is a serious financial tool login. Think Bloomberg Terminal login, not Notion.
```

---

## How to Use This Spec

1. Go to [v0.dev](https://v0.dev)
2. Paste one `v0 Prompt` section at a time (start with Screen 1 — Pipeline Dashboard)
3. After generation, iterate: "Make the numbers monospaced", "Darken the background", "Add Indian comma formatting to all amounts"
4. Export to your Next.js project, connect to your FastAPI backend at `http://localhost:8000/api/v1/`
5. Key API endpoints: `GET /applications`, `GET /hitl/queue`, `POST /hitl/{id}/resolve`, `GET /health`

### Iteration Prompts for Common Fixes

If the output looks too "AI generic":
- "Remove Inter font. Use DM Serif Display for headings, DM Sans for body, JetBrains Mono for all numbers."
- "Darken the background to near-black #0C0E12. Make cards #14161C with hairline gold borders."
- "Remove all purple/blue gradients. The only accent color is gold #C8A862."
- "Remove all decorative illustrations and emojis. This is a financial operations tool."
- "Format all INR amounts with Indian comma system: ₹15,00,000 not ₹1,500,000."

If the layout feels too sparse:
- "Increase visual density. This is a working tool, not a marketing page. Reduce padding, use 11px for labels, show more data per row."

If trust signals are missing:
- "Add provenance tags to every data point: which agent produced it, from which document, at what confidence."
- "Add policy version badge (e.g., v1.0.0) to every decision screen."
- "Add audit trail footer: 'This action will be logged with your ID, timestamp, and rationale.'"
