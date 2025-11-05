Technical Specifications: Underwriting Center (Interactive Demo)
================================================================

1\. Overview
------------

**Project Goal:** To create a high-fidelity, interactive frontend prototype of the Guidewire Underwriting Center application.

**Key Principle:** This is a *demo application*. Its purpose is to replicate the "story line" or "click path" shown in the video. All backend processes, AI analysis, and database interactions will be "faked" on the frontend to simulate the user experience.

**Core Functionality:**

-   **Screen 1:** A main dashboard with KPIs and a list of submissions.

-   **Screen 2:** A detailed submission view that dynamically updates based on user actions.

-   **Faked Logic:** Simulate AI summarization, proposal generation, and quote comparison through timed events and state changes.

-   **Data:** All data will be hard-coded (mocked).

2\. Core User Flow (Click Path)
-------------------------------

This is the primary "story" the demo must tell:

1.  **Start:** The user starts on the **Dashboard Screen**. They see KPIs (Quote Turnaround Time, etc.) and a table of "Active Submissions."

2.  **Navigate to Detail:** The user clicks on the "Floor & Decor Outlets of America, Inc" (SUB-2026-001) submission in the table.

3.  **Land on Submission Detail:** The user is navigated to the **Submission Detail Screen** for SUB-2026-001. They see KPIs for *this* submission (Status: "Triaged", Completeness: "74%").

4.  **Simulate AI Summarization:** The user clicks the "**Summarize**" button.

    -   A loading modal appears (e.g., "Analyzing Received Documentation...").

    -   After ~2 seconds, the modal disappears, and a new "Smart Summary" and "Impact on completeness" section appears.

5.  **Accept AI Summary:** The user clicks the "**Accept**" button on the summary.

    -   A loading modal appears (e.g., "Updating Completeness Score...").

    -   After ~2 seconds, the "Completeness" KPI updates from **74% -> 86%**.

    -   The "Status" KPI updates from **"Triaged" -> "In Review"**.

    -   A new button, "**+ Generate Proposal**", becomes visible.

6.  **Generate Proposal:** The user clicks "**+ Generate Proposal**".

    -   A loading modal appears (e.g., "Retrieving APD Product Details..." -> "Calculating Quote...").

    -   After ~3 seconds, the "Proposal Details" section appears, showing "Coverages," "Endorsements," and a "**Base Quote (Manual Premium)**" card for **$42,459**.

7.  **Simulate AI Proposal Analysis:** The user clicks the "**Analyze Proposal**" button.

    -   After ~2 seconds, a "Recommended Changes" section appears, suggesting to add "Voluntary Compensation."

8.  **Accept AI Recommendation:** The user clicks "**Accept Recommendation**".

    -   A loading modal appears (e.g., "Adding Endorsements...").

    -   After ~2 seconds, the "Endorsements" list updates (the "Voluntary Compensation" checkbox becomes checked).

9.  **Generate New Quote:** The user (optionally) un-checks "KOTECKI" and clicks "**Generate Quote**".

    -   A loading modal appears (e.g., "Analyzing Changes..." -> "Calculating Quote...").

    -   After ~3 seconds, a second quote card, "**Generated Quote**", appears with a price of **$75,334**.

10. **Compare Quotes:** The user clicks "**Compare Quotes**".

    -   A loading modal appears (e.g., "Retrieving Quotes...").

    -   After ~2 seconds, the view changes to a side-by-side comparison, showing both the "Base Quote" and "Generated Quote" in detail.

11. **Send Quote:** The user (implicitly) closes the comparison and clicks "**Send to Broker**" on the "Generated Quote" card.

    -   A loading modal appears (e.g., "Creating Broker Quote Page..." -> "Sending Email...").

    -   After ~3 seconds, the "Status" KPI on the Submission Detail page updates to **"Quoted"**.

12. **Return to Dashboard:** The user clicks the "**Return to Submission List**" breadcrumb link.

13. **View Updated Dashboard:** The user is back on the **Dashboard Screen**.

    -   The "Floor & Decor" submission in the "Active" list now shows the status "Quoted".

    -   *(Demo Step)* The user clicks the "**Bound**" tab, and "Floor & Decor" is now in this list (simulating the broker accepted).

14. **Complete the Loop:** The user clicks the "**Refresh**" icon on the dashboard.

    -   A loading modal appears (e.g., "Updating metrics...").

    -   After ~2 seconds, the main dashboard KPIs update: "Quote Turnaround Time" changes from **4.1 days -> 3.9 days**, and other charts update.

15. **End.**

3\. Screen & Component Breakdown
--------------------------------

### Screen 1: Dashboard (`/`)

-   **Layout:** Main app header, 4-column KPI row, main content area with tabs and table.

-   **Components:**

    -   `KpiCard`: Reusable card for KPIs.

        -   **Props:** `title` (string), `value` (string), `delta` (string, optional), `chartData` (array).

        -   **Note:** Renders a simple bar or line chart.

    -   `DashboardKpis`: Renders 4 `KpiCard` components with mock data for "Quote Turnaround Time", "Average Hit Ratio", "Cumulative Earned Premium", "In Force Loss Ratio".

    -   `SubmissionTable`:

        -   Manages tabs for "Active", "Bound", "Declined".

        -   Renders the main table.

        -   **Table Columns:** Account, Submission, Status, Broker, Broker Tier, Effective Date, Priority Score, Completeness, Appetite.

        -   **Interaction:** `onClick` on a row triggers navigation to `/submission/:id`.

### Screen 2: Submission Detail (`/submission/:id`)

-   **Layout:** Back-link, submission header, 4-column KPI row, main content area. This screen is stateful and reveals components based on the user flow.

-   **Components:**

    -   `SubmissionHeader`: Displays Account Name and Submission ID.

    -   `KpiCard`: Reused for "Status", "Risk Appetite", "Priority Score", "Completeness". These get their data from the global state.

    -   `RecentUpdates`: Shows mock PDF/Email attachments and the "**Summarize**" button.

    -   `SmartSummary`: (Conditionally rendered) Shows the hard-coded AI summary and "**Accept**" button.

    -   `ApplicantInfoTabs`: A tabbed view with hard-coded applicant info (HQ, Operations, etc.).

    -   `ProposalDetails`: (Conditionally rendered)

        -   Shows "Coverages" and "Endorsements" (list of checkboxes).

        -   Contains the `QuoteCard` components.

    -   `QuoteCard`: (Conditionally rendered)

        -   **Props:** `title` (e.g., "Base Quote"), `price` (string).

        -   Contains "Send to Broker" or "Compare Quotes" buttons.

    -   `QuoteComparison`: (Conditionally rendered) Shows a side-by-side view of the two mock quotes.

    -   `LoadingModal`: A generic modal that shows a loading spinner and a text message.

        -   **Props:** `text` (string).

4\. State Management (Demo Logic)
---------------------------------

A simple global state (e.g., React Context, Zustand) is required to manage the demo's flow.

```
// Example initial state
{
  // Controls main dashboard KPIs
  dashboardKpis: {
    turnaroundTime: 4.1,
    // ... other KPI data
  },

  // Controls the state of the specific submission
  submission: {
    id: 'SUB-2026-001',
    status: 'Triaged',
    riskAppetite: 'High',
    priorityScore: 4.8,
    completeness: 74,

    // Flow control flags
    isSummaryVisible: false,
    isProposalVisible: false,
    isRecsVisible: false,
    isComparisonVisible: false,

    // Controls which quotes are shown
    quotes: [] // e.g., ['base'], ['base', 'generated']
  },

  // Controls which modal is active
  modal: {
    isVisible: false,
    message: ''
  }
}

```

5\. Faked Interactions (Implementation)
---------------------------------------

This defines the logic for the click path.

-   **Click "Summarize":**

    1.  Set `modal = { isVisible: true, message: 'Analyzing...' }`.

    2.  `setTimeout(2000, () => {`

    3.  Set `submission.isSummaryVisible = true`.

    4.  Set `modal.isVisible = false`.

    5.  `})`

-   **Click "Accept" (Summary):**

    1.  Set `modal = { isVisible: true, message: 'Updating...' }`.

    2.  `setTimeout(2000, () => {`

    3.  Set `submission.completeness = 86`.

    4.  Set `submission.status = 'In Review'`.

    5.  Set `modal.isVisible = false`.

    6.  `})`

-   **Click "+ Generate Proposal":**

    1.  Set `modal = { isVisible: true, message: 'Calculating Quote...' }`.

    2.  `setTimeout(3000, () => {`

    3.  Set `submission.isProposalVisible = true`.

    4.  Set `submission.quotes = ['base']`.

    5.  Set `modal.isVisible = false`.

    6.  `})`

-   ...and so on for every interaction in the user flow (Analyze Proposal, Generate Quote, Send to Broker, Refresh Dashboard).

6\. Mock Data
-------------

All data will be hard-coded in files (e.g., `/data/mockData.js`).

-   **`submissions` Array:**

    ```
    [
      { id: 'SUB-2026-001', account: 'Floor & Decor Outlets of America, Inc', status: 'Triaged', broker: 'Marsh & McLennan', ... },
      { id: 'SUB-2026-003', account: 'Retail Chain Express', status: 'In Review', broker: 'Willis Towers Watson', ... },
      { id: 'SUB-2026-005', account: 'Norovia Metalworking', status: 'Cleared', broker: 'Brown & Brown', ... }
    ]

    ```

-   **`submissionDetails` Object:**

    ```
    {
      'SUB-2026-001': {
        applicantInfo: { hq: '...', operations: '...' },
        riskDescription: { ... },
        // ...
      }
    }

    ```

-   **`quotes` Object:**

    ```
    {
      'base': {
        price: 42459,
        coverages: [ ... ],
        endorsements: [ { name: 'KOTECKI', checked: true }, ... ]
      },
      'generated': {
        price: 75334,
        coverages: [ ... ],
        endorsements: [ { name: 'KOTECKI', checked: false }, { name: 'Voluntary Compensation', checked: true }, ... ]
      }
    }

    ```

7\. Styling (Visual Theme)
--------------------------

-   **Framework:** Use **Tailwind CSS** for all styling.

-   **Colors:**

    -   **Primary:** A corporate blue (e.g., `bg-blue-600`, `text-blue-600`).

    -   **Background:** Light gray (e.g., `bg-gray-100`).

    -   **Cards/Modals:** White (e.g., `bg-white`).

    -   **Text:** Dark gray/black (e.g., `text-gray-900`, `text-gray-600`).

    -   **Tags (Status):** Green (`bg-green-100`, `text-green-800`), Red, Yellow.

-   **Components:**

    -   **Cards:** `bg-white`, `rounded-lg`, `shadow-md`.

    -   **Buttons:** `bg-blue-600`, `text-white`, `rounded-lg`, `px-4`, `py-2`, `hover:bg-blue-700`.

    -   **Charts:** Use simple bar/line charts (e.g., from `recharts` or `chart.js`) styled to match.

8\. Recommended Stack
---------------------

-   **Frontend:** **React** (with Hooks)

-   **Styling:** **Tailwind CSS**

-   **State Management:** **Zustand** or **React Context** (for simplicity)

-   **Charts (Optional):** **Recharts**

-   **Icons:** **Lucide React**