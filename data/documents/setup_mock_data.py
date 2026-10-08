
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "database.sqlite"
DOCUMENTS_DIR = BASE_DIR / "data" / "documents"
QUERIES_PATH = BASE_DIR / "query_examples.sql"

DOCUMENTS = {
    "security_policy.txt": """
Northstar Operations Group Security Policy

All users must have individual accounts. Shared accounts are prohibited unless approved by Information Security. Multi-factor authentication is required for remote access, privileged accounts, and critical applications.

Access must follow the principle of least privilege. Managers request access, system owners approve it, and access permissions are reviewed quarterly. Access must be removed within one business day when an employee leaves or changes roles.

Confidential information must be stored only in approved company systems. Sensitive data must be encrypted during storage and transmission. Employees may not copy company information to personal email, personal devices, or unauthorized cloud services.

Employees must report suspected phishing, malware, unauthorized access, lost devices, or accidental data disclosure to the Service Desk or Information Security team within one hour of discovery.

Security awareness training is required annually. Policy exceptions require documented business justification, a risk assessment, an expiration date, and Information Security Director approval.
""",
    "code_review_process.txt": """
Northstar Operations Group Code Review Process

All production code changes must be reviewed before being merged. The review process improves quality, security, maintainability, and knowledge sharing.

Developers must create a pull request describing the business purpose, technical approach, testing performed, deployment considerations, and rollback plan.

At least one qualified peer reviewer must approve a standard change. Unit tests, formatting checks, linting, dependency checks, and security scans must pass before approval.

Changes involving authentication, authorization, payment processing, confidential data, infrastructure, or major database changes require two reviewers. One reviewer must have relevant technical or security expertise.

Reviewers assess correctness, security, error handling, test coverage, maintainability, performance, and operational impact.

Only the pull request author or an authorized release manager may merge approved code. Emergency fixes may use an expedited review path, but a second review and retrospective review must be completed within two business days.
""",
    "customer_complaints.txt": """
Northstar Operations Group Customer Complaint Handling Procedure

Customers may submit complaints through the support portal, email, phone, account manager, or designated escalation channel. Every complaint receives a case number, customer identifier, date received, product or service involved, and issue description.

The support team must acknowledge a complaint within one business day. Standard complaints should receive an investigation update within three business days and a proposed resolution within five business days.

High-severity complaints include potential privacy or security incidents, safety concerns, repeated service failures, executive escalations, and issues affecting multiple customers. These complaints must be escalated to Customer Success leadership on the same business day.

The case owner reviews account history, service records, communications, and relevant product information. Possible resolutions include correcting the service issue, providing training, issuing an approved credit, replacing a deliverable, or changing a process.

Material or repeated complaints require a root-cause review and a corrective action with an accountable owner. Customer Success reviews complaint volume, response time, resolution time, repeat complaints, escalation rate, and satisfaction trends monthly.
""",
    "employee_experience_policy.txt": """
Northstar Operations Group Employee Experience Policy

Northstar conducts a quarterly employee pulse survey covering satisfaction, manager effectiveness, workload balance, learning access, and confidence in leadership.

People managers should hold a meaningful one-on-one conversation with each direct report at least monthly. Conversations should cover priorities, workload, professional development, recognition, and barriers to effective work.

Managers must review workload when an employee reports sustained over-capacity work, missed recovery time, or recurring priority conflicts. Teams should rebalance work, adjust deadlines, or request additional resources when appropriate.

Eligible teams may use a flexible work model based on role requirements, client commitments, collaboration needs, and security considerations.

Employees should receive access to at least four hours of structured learning time per month when business commitments permit. Leadership reviews satisfaction alongside manager effectiveness, workload balance, learning access, one-on-one completion, and learning-time completion.

These measures identify improvement opportunities but do not prove that a particular policy caused a satisfaction outcome.
""",
    "sales_customer_success_strategy.txt": """
Northstar Operations Group Sales and Customer Success Strategy

Sales teams qualify opportunities using customer need, business value, decision process, implementation readiness, budget confidence, and strategic fit. Opportunities without a documented business problem should not be forecast as committed revenue.

After contract signature, Sales must provide Customer Success with the signed scope, customer goals, implementation risks, key stakeholders, expected outcomes, and commercial commitments within two business days.

Customer Success creates a documented success plan within ten business days for strategic accounts. The plan includes measurable outcomes, milestones, customer responsibilities, adoption measures, and an executive sponsor.

Customer health is reviewed monthly using product adoption, open issues, support activity, payment status, stakeholder engagement, and progress against the success plan.

Accounts with declining health require a documented action plan within five business days. Renewal planning begins at least 90 days before the renewal date.

Leadership reviews revenue, win rate, renewal rate, customer satisfaction, implementation timeliness, handoff timeliness, success-plan completion, and at-risk action-plan completion together. Strong revenue performance is not sustainable if customer outcomes decline.
""",
    "analytics_data_dictionary.txt": """
Northstar Operations Group Analytics Data Dictionary

All records in this demonstration dataset are fictional and non-confidential.

Revenue is recorded by month and region. Monthly revenue trends are calculated by summing revenue across regions for each month. Q4 represents October through December 2025.

Gross customer churn rate is calculated as churned customers divided by beginning customers. A weighted period churn rate is calculated as total churned customers divided by total beginning customers.

Employee satisfaction is compared with a fictional industry benchmark. The benchmark gap equals satisfaction percentage minus benchmark percentage.

Employee policy indicators include manager effectiveness, workload balance, learning access, monthly one-on-one completion, and learning-time target completion.

Sales performance includes revenue, qualified opportunities, won deals, and win rate. Customer success outcomes include renewal rate, customer satisfaction, implementation timeliness, customer handoff timeliness, success-plan completion, and at-risk action-plan completion.

Aggregate data can identify relationships and policy areas for review, but it cannot prove that a policy caused a specific business outcome.
""",
}

def create_documents() -> None:
    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

    for filename, content in DOCUMENTS.items():
        (DOCUMENTS_DIR / filename).write_text(
            content.strip() + "\n",
            encoding="utf-8",
        )

def build_database() -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.executescript("""
        DROP TABLE IF EXISTS documents;
        DROP TABLE IF EXISTS regional_revenue;
        DROP TABLE IF EXISTS customer_churn;
        DROP TABLE IF EXISTS employee_satisfaction;
        DROP TABLE IF EXISTS sales_customer_success;

        CREATE TABLE documents (
            filename TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        );

        CREATE TABLE regional_revenue (
            month TEXT,
            quarter TEXT,
            region TEXT,
            revenue_usd REAL,
            orders INTEGER,
            gross_margin_pct REAL
        );

        CREATE TABLE customer_churn (
            month TEXT,
            beginning_customers INTEGER,
            churned_customers INTEGER,
            new_customers INTEGER,
            ending_customers INTEGER
        );

        CREATE TABLE employee_satisfaction (
            quarter TEXT,
            department TEXT,
            satisfaction_pct REAL,
            industry_benchmark_pct REAL,
            manager_effectiveness_pct REAL,
            workload_balance_pct REAL,
            learning_access_pct REAL,
            monthly_one_on_one_completion_pct REAL,
            learning_time_target_met_pct REAL
        );

        CREATE TABLE sales_customer_success (
            quarter TEXT,
            region TEXT,
            sales_revenue_usd REAL,
            qualified_opportunities INTEGER,
            won_deals INTEGER,
            renewal_rate_pct REAL,
            customer_satisfaction_pct REAL,
            implementation_on_time_pct REAL,
            handoff_within_2_business_days_pct REAL,
            success_plan_within_10_business_days_pct REAL,
            at_risk_action_plan_pct REAL
        );
        """)

        document_rows = [
            (
                filename,
                filename.replace(".txt", "").replace("_", " ").title(),
                content.strip(),
            )
            for filename, content in DOCUMENTS.items()
        ]
        connection.executemany(
            "INSERT INTO documents VALUES (?, ?, ?)",
            document_rows,
        )

        region_specs = {
            "North": (420000, 280, 41.0),
            "East": (380000, 250, 39.5),
            "South": (310000, 210, 37.8),
            "West": (350000, 230, 40.2),
        }

        revenue_rows = []
        for month_number in range(1, 13):
            month = f"2025-{month_number:02d}"
            quarter = f"Q{((month_number - 1) // 3) + 1}"
            growth = 1 + (0.03 * (month_number - 1))

            for region, values in region_specs.items():
                base_revenue, base_orders, base_margin = values
                revenue_rows.append((
                    month,
                    quarter,
                    region,
                    round(base_revenue * growth),
                    round(base_orders * growth),
                    round(base_margin + (0.15 * (month_number - 1)), 2),
                ))

        connection.executemany(
            "INSERT INTO regional_revenue VALUES (?, ?, ?, ?, ?, ?)",
            revenue_rows,
        )

        churned_values = [24, 22, 26, 25, 28, 30, 31, 29, 34, 35, 33, 38]
        new_values = [70, 65, 72, 80, 78, 85, 90, 88, 95, 100, 97, 105]
        churn_rows = []
        beginning_customers = 1200

        for month_number, (churned, new) in enumerate(
            zip(churned_values, new_values),
            start=1,
        ):
            ending_customers = beginning_customers - churned + new
            churn_rows.append((
                f"2025-{month_number:02d}",
                beginning_customers,
                churned,
                new,
                ending_customers,
            ))
            beginning_customers = ending_customers

        connection.executemany(
            "INSERT INTO customer_churn VALUES (?, ?, ?, ?, ?)",
            churn_rows,
        )

        employee_specs = {
            "Customer Success": (80, 78, 76, 72, 84, 74),
            "Consulting": (78, 77, 74, 70, 81, 71),
            "Operations": (74, 73, 79, 68, 78, 67),
            "Sales": (72, 70, 71, 65, 75, 63),
        }
        quarter_changes = [
            (0, 0, 0, 0, 0, 0),
            (2, 2, 3, 3, 4, 3),
            (1, 1, 2, 4, 6, 5),
            (3, 4, 5, 7, 8, 8),
        ]
        employee_rows = []

        for quarter_number in range(1, 5):
            quarter = f"Q{quarter_number}"
            changes = quarter_changes[quarter_number - 1]

            for department, base_values in employee_specs.items():
                values = [
                    base_value + change
                    for base_value, change in zip(base_values, changes)
                ]
                employee_rows.append((
                    quarter,
                    department,
                    values[0],
                    75,
                    values[1],
                    values[2],
                    values[3],
                    values[4],
                    values[5],
                ))

        connection.executemany(
            "INSERT INTO employee_satisfaction VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            employee_rows,
        )

        sales_specs = {
            "North": (950000, 110, 32, 88, 84, 89, 87, 85, 83),
            "East": (820000, 96, 28, 86, 82, 87, 82, 80, 78),
            "South": (700000, 88, 24, 84, 80, 85, 76, 74, 72),
            "West": (780000, 92, 26, 85, 81, 86, 80, 78, 76),
        }
        quarter_factors = [1.00, 1.10, 1.18, 1.32]
        sales_rows = []

        for quarter_number, factor in enumerate(quarter_factors, start=1):
            quarter = f"Q{quarter_number}"

            for region, values in sales_specs.items():
                revenue, opportunities, deals, renewal, satisfaction, on_time, handoff, plan, risk = values
                improvement = quarter_number - 1
                sales_rows.append((
                    quarter,
                    region,
                    round(revenue * factor),
                    round(opportunities * factor),
                    round(deals * factor),
                    renewal + improvement,
                    satisfaction + improvement,
                    on_time + improvement,
                    handoff + (2 * improvement),
                    plan + (2 * improvement),
                    risk + (2 * improvement),
                ))

        connection.executemany(
            "INSERT INTO sales_customer_success VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            sales_rows,
        )

def create_query_file() -> None:
    queries = """
-- Monthly revenue trends
SELECT month, ROUND(SUM(revenue_usd), 2) AS total_revenue_usd
FROM regional_revenue
GROUP BY month
ORDER BY month;

-- Weighted customer churn rate
SELECT ROUND(
    100.0 * SUM(churned_customers) / NULLIF(SUM(beginning_customers), 0),
    2
) AS churn_rate_pct
FROM customer_churn;

-- Q4 performance by region
SELECT
    region,
    SUM(revenue_usd) AS q4_revenue_usd,
    SUM(orders) AS q4_orders,
    ROUND(AVG(gross_margin_pct), 2) AS q4_average_margin_pct
FROM regional_revenue
WHERE quarter = 'Q4'
GROUP BY region
ORDER BY q4_revenue_usd DESC;

-- Employee satisfaction compared with industry standards
SELECT
    department,
    satisfaction_pct,
    industry_benchmark_pct,
    satisfaction_pct - industry_benchmark_pct AS benchmark_gap_pct,
    manager_effectiveness_pct,
    workload_balance_pct,
    learning_access_pct
FROM employee_satisfaction
WHERE quarter = 'Q4'
ORDER BY benchmark_gap_pct DESC;

-- Sales performance and customer-success policy indicators
SELECT
    region,
    SUM(sales_revenue_usd) AS annual_sales_revenue_usd,
    ROUND(
        100.0 * SUM(won_deals)
        / NULLIF(SUM(qualified_opportunities), 0),
        2
    ) AS win_rate_pct,
    ROUND(AVG(renewal_rate_pct), 2) AS renewal_rate_pct,
    ROUND(AVG(customer_satisfaction_pct), 2) AS customer_satisfaction_pct,
    ROUND(AVG(handoff_within_2_business_days_pct), 2) AS handoff_timeliness_pct,
    ROUND(AVG(success_plan_within_10_business_days_pct), 2) AS success_plan_timeliness_pct,
    ROUND(AVG(at_risk_action_plan_pct), 2) AS at_risk_action_plan_pct
FROM sales_customer_success
GROUP BY region
ORDER BY annual_sales_revenue_usd DESC;
"""
    QUERIES_PATH.write_text(queries.strip() + "\n", encoding="utf-8")

def main() -> None:
    create_documents()
    build_database()
    create_query_file()

    print(f"Created database: {DATABASE_PATH}")
    print(f"Created documents: {DOCUMENTS_DIR}")
    print(f"Created SQL queries: {QUERIES_PATH}")

if __name__ == "__main__":
    main()
