"""
Generate synthetic Enterprise Data Lake dataset
"""

import pandas as pd
import random
from datetime import datetime, timedelta
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Fictional company info
COMPANY_NAME = "Nexus Innovations Inc."
INDUSTRY = "Enterprise Software Solutions"

# Helper functions
def random_date(start_date, end_date):
    return start_date + timedelta(days=random.randint(0, (end_date - start_date).days))

def generate_customer_id():
    return f"CUST{random.randint(10000, 99999)}"

def generate_sale_id():
    return f"SALE{random.randint(100000, 999999)}"

def generate_employee_id():
    return f"EMP{random.randint(1000, 9999)}"

def generate_log_id():
    return f"LOG{random.randint(1000000, 9999999)}"

# Cities
CITIES = ["San Francisco", "New York", "Austin", "Seattle", "Boston", "Denver", "Chicago", "Los Angeles"]
FIRST_NAMES = ["James", "Sarah", "Michael", "Emily", "David", "Jennifer", "Robert", "Amanda", "William", "Jessica", "John", "Ashley", "Richard", "Stephanie", "Joseph", "Nicole", "Thomas", "Melissa", "Charles", "Elizabeth"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
DEPARTMENTS = ["Engineering", "Sales", "Marketing", "HR", "Finance", "Operations", "Legal", "Support"]
SERVICES = ["auth_service", "payment_api", "user_dashboard", "data_sync", "email_service", "reporting", "analytics", "inventory"]
LOG_LEVELS = ["INFO", "WARNING", "ERROR", "DEBUG"]
STATUS_CODES = ["200", "201", "400", "401", "403", "404", "500", "503"]
REGIONS = ["North America", "Europe", "Asia Pacific", "Latin America"]
PRODUCTS = ["Enterprise License", "Cloud Storage", "Analytics Platform", "API Gateway", "Security Suite"]

# 1. Generate customers.csv
print("Generating customers.csv...")
customers = []
for i in range(40):
    customer = {
        "Customer ID": generate_customer_id(),
        "Name": f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
        "Email": f"{random.choice(FIRST_NAMES).lower()}.{random.choice(LAST_NAMES).lower()}@example.com",
        "Phone": f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
        "City": random.choice(CITIES),
        "Registration Date": random_date(datetime(2020, 1, 1), datetime(2024, 12, 31)).strftime("%Y-%m-%d"),
        "Customer Status": random.choice(["Active", "Inactive", "Pending", "Active", "Active"])
    }
    customers.append(customer)

# Intentional quality issues
customers[5]["Email"] = "invalid-email"  # Invalid email
customers[10]["Email"] = ""  # Missing email
customers[15]["Customer Status"] = "Premium"  # Inconsistent status
customers[20]["City"] = ""  # Missing city
customers[25]["Registration Date"] = ""  # Missing date
customers[30]["Customer Status"] = "active"  # Case inconsistency
# Duplicate
customers.append(customers[0].copy())

customers_df = pd.DataFrame(customers)
customers_df.to_csv("enterprise_data_lake_sample/customers.csv", index=False)
print(f"Generated {len(customers_df)} customer records")

# 2. Generate sales.xlsx
print("Generating sales.xlsx...")
sales = []
customer_ids = [c["Customer ID"] for c in customers[:35]]  # Use valid customer IDs
for i in range(45):
    sale = {
        "Sale ID": generate_sale_id(),
        "Customer ID": random.choice(customer_ids),
        "Product ID": f"PROD{random.randint(100, 999)}",
        "Sale Date": random_date(datetime(2023, 1, 1), datetime(2024, 12, 31)).strftime("%Y-%m-%d"),
        "Quantity": random.randint(1, 100),
        "Unit Price": round(random.uniform(100, 5000), 2),
        "Total Amount": 0,  # Will calculate
        "Region": random.choice(REGIONS)
    }
    sale["Total Amount"] = round(sale["Quantity"] * sale["Unit Price"], 2)
    sales.append(sale)

# Intentional quality issues
sales[5]["Quantity"] = -5  # Invalid negative quantity
sales[10]["Unit Price"] = ""  # Missing price
sales[15]["Customer ID"] = "CUST99999"  # Invalid customer ID
sales[20]["Total Amount"] = -1000  # Invalid negative total
sales[25]["Sale Date"] = "2024-13-45"  # Invalid date
sales[30]["Quantity"] = 10000  # Outlier quantity
# Duplicate
sales.append(sales[0].copy())

sales_df = pd.DataFrame(sales)
sales_df.to_excel("enterprise_data_lake_sample/sales.xlsx", index=False)
print(f"Generated {len(sales_df)} sales records")

# 3. Generate employee_records.json
print("Generating employee_records.json...")
employees = []
for i in range(35):
    employee = {
        "Employee ID": generate_employee_id(),
        "Name": f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
        "Department": random.choice(DEPARTMENTS),
        "Age": random.randint(22, 65),
        "Salary": random.randint(50000, 200000),
        "Hire Date": random_date(datetime(2015, 1, 1), datetime(2024, 12, 31)).strftime("%Y-%m-%d"),
        "Employment Status": random.choice(["Full-time", "Full-time", "Full-time", "Part-time", "Contract"])
    }
    employees.append(employee)

# Intentional quality issues
employees[5]["Age"] = 150  # Invalid age
employees[10]["Salary"] = ""  # Missing salary
employees[15]["Department"] = "Management"  # Inconsistent department
employees[20]["Hire Date"] = ""  # Missing hire date
employees[25]["Employment Status"] = "permanent"  # Inconsistent status
employees[30]["Age"] = 18  # Edge case
# Duplicate
employees.append(employees[0].copy())

with open("enterprise_data_lake_sample/employee_records.json", "w") as f:
    json.dump(employees, f, indent=2)
print(f"Generated {len(employees)} employee records")

# 4. Generate application_logs.xml
print("Generating application_logs.xml...")
logs = []
employee_ids = [e["Employee ID"] for e in employees[:30]]
for i in range(40):
    log = {
        "Log ID": generate_log_id(),
        "Timestamp": random_date(datetime(2024, 1, 1), datetime(2024, 12, 31)).strftime("%Y-%m-%d %H:%M:%S"),
        "Employee ID": random.choice(employee_ids),
        "Service": random.choice(SERVICES),
        "Log Level": random.choice(LOG_LEVELS),
        "Response Time": random.randint(10, 5000),
        "Status Code": random.choice(STATUS_CODES),
        "Message": f"Request processed successfully for {random.choice(SERVICES)}"
    }
    logs.append(log)

# Intentional quality issues
logs[5]["Response Time"] = -100  # Invalid response time
logs[10]["Status Code"] = "999"  # Invalid status code
logs[15]["Employee ID"] = "EMP9999"  # Invalid employee ID
logs[20]["Timestamp"] = ""  # Missing timestamp
logs[25]["Log Level"] = "CRITICAL"  # Inconsistent log level
logs[30]["Response Time"] = 100000  # Outlier response time
# Duplicate
logs.append(logs[0].copy())

# Create XML
root = ET.Element("ApplicationLogs")
for log in logs:
    log_elem = ET.SubElement(root, "Log")
    for key, value in log.items():
        field = ET.SubElement(log_elem, key.replace(" ", ""))
        field.text = str(value)

# Pretty print XML
xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
with open("enterprise_data_lake_sample/application_logs.xml", "w") as f:
    f.write(xml_str)
print(f"Generated {len(logs)} log records")

# 5. Generate company_policy.txt
print("Generating company_policy.txt...")
policy_text = """NEXUS INNOVATIONS INC. - DATA HANDLING AND SECURITY POLICY

DOCUMENT CONTROL
Document Owner: Chief Information Security Officer
Effective Date: January 1, 2024
Review Date: January 1, 2025
Classification: Internal

1. PURPOSE AND SCOPE

1.1 Purpose
This policy establishes the standards and procedures for the secure handling, storage, processing, and transmission of data within Nexus Innovations Inc. The policy ensures compliance with applicable regulations, protects sensitive information, and maintains trust with our customers and stakeholders.

1.2 Scope
This policy applies to all employees, contractors, consultants, temporary staff, and third-party partners who have access to company data systems or handle company data on behalf of Nexus Innovations Inc. This policy covers all data types including customer data, employee data, financial records, intellectual property, and business information.

1.3 Applicability
This policy applies to all data regardless of storage location, including on-premises systems, cloud services, mobile devices, and removable media. All business units and subsidiaries must adhere to this policy.

2. DATA CLASSIFICATION

2.1 Classification Framework
Data is classified based on its sensitivity and the impact of unauthorized disclosure. All data must be classified at the time of creation or receipt.

2.2 Confidential Data
Confidential data includes customer personal information (PII), financial records, employee data, proprietary business information, trade secrets, and any data that could cause significant harm if disclosed. This data must be encrypted at rest and in transit using AES-256 encryption or equivalent.

2.3 Internal Data
Internal data includes non-sensitive business information, operational metrics, internal communications, project documentation, and business plans. This data should be protected from external access but may be shared within the organization on a need-to-know basis.

2.4 Public Data
Public data includes information intended for external distribution, such as marketing materials, public reports, website content, and press releases. This data requires standard security measures but may be freely shared.

2.5 Classification Responsibilities
Data owners are responsible for classifying data under their control. Employees must follow classification markings and handle data according to its classification level. Unclassified data should be treated as Internal by default.

3. DATA ACCESS CONTROL

3.1 Authentication Requirements
All systems require strong authentication. Remote access requires multi-factor authentication (MFA). Passwords must be at least 12 characters with complexity requirements including uppercase, lowercase, numbers, and special characters. Passwords must be rotated every 90 days.

3.2 Authorization Principles
Access to data systems is granted based on the principle of least privilege. Employees receive only the minimum access necessary to perform their job functions. Access requests must be approved by both the data owner and the department manager. Access is reviewed quarterly.

3.3 Role-Based Access Control
Access is managed through role-based access control (RBAC). Roles are defined based on job functions and responsibilities. When employees change roles or leave the company, access rights must be updated or revoked within 24 hours.

3.4 Privileged Access
Privileged access accounts (administrative, root, system accounts) require additional approval, stronger authentication, and regular monitoring. Privileged access sessions must be logged and reviewed monthly.

3.5 Third-Party Access
Third-party access must be governed by contracts specifying security requirements. Access is temporary and granted only for the duration of the engagement. Third-party access must be monitored and reviewed weekly.

4. DATA ENCRYPTION

4.1 Encryption at Rest
All confidential data stored in databases, file systems, cloud storage, or backup systems must be encrypted using AES-256 encryption or equivalent industry standard. Encryption keys must be stored separately from the encrypted data in a secure key management system.

4.2 Encryption in Transit
All data transmitted over networks must be encrypted using TLS 1.3 or higher. Legacy protocols such as SSL 3.0 and TLS 1.0/1.1 are strictly prohibited. VPNs must be used for remote access to internal systems.

4.3 Key Management
Encryption keys must be generated using secure random number generators. Keys must be rotated annually or immediately upon compromise. Key access is restricted to authorized personnel with documented approval.

4.4 Mobile Device Encryption
All company-issued mobile devices must have full disk encryption enabled. Personal devices used for work must have encryption enabled through mobile device management (MDM) policies.

5. DATA RETENTION AND DISPOSAL

5.1 Retention Periods
Customer data must be retained for 7 years after the end of the customer relationship or as required by applicable law, whichever is longer. Employee records must be retained for 10 years after termination. Financial records must be retained for 7 years as required by law. Contracts and legal documents must be retained permanently.

5.2 Data Minimization
Only data necessary for business purposes should be collected and retained. Unnecessary data should be regularly purged. Data retention schedules must be documented and enforced.

5.3 Data Disposal Procedures
When data reaches the end of its retention period, it must be securely deleted using cryptographic erasure or physical destruction of storage media. Disposal must be documented and approved by the data owner. Disposal logs must be retained for audit purposes.

5.4 Backup Retention
Backups are retained according to the following schedule: daily backups for 30 days, weekly backups for 12 weeks, monthly backups for 12 months, and annual backups for 7 years. Backup media must be encrypted and stored securely.

6. INCIDENT RESPONSE

6.1 Incident Reporting
All data security incidents must be reported to the Security Operations Center (SOC) within 24 hours of discovery. Incidents include unauthorized access, data breaches, malware infections, policy violations, and suspected data exfiltration. Reporting can be done through security@nexusinnovations.com or the incident hotline.

6.2 Incident Classification
Incidents are classified based on severity: Critical (immediate threat to operations or data), High (significant impact but contained), Medium (limited impact), and Low (minimal impact). Classification determines response timeline and notification requirements.

6.3 Incident Response Process
The incident response team will assess the severity, contain the breach, eradicate the threat, recover affected systems, and implement remediation measures. The process follows industry-standard frameworks including NIST and SANS.

6.4 Incident Notification
Affected parties must be notified as required by law and contract. Notification timelines vary by jurisdiction but generally range from 72 hours to 30 days. Legal counsel must be consulted before external notification.

6.5 Post-Incident Review
All incidents are documented and reviewed for process improvement. Root cause analysis must be completed within 30 days. Lessons learned are incorporated into security policies and training.

7. COMPLIANCE AND AUDIT

7.1 Regulatory Compliance
Nexus Innovations Inc. complies with all applicable data protection regulations including GDPR, CCPA, HIPAA, and industry-specific requirements. Regular compliance assessments are conducted to ensure adherence.

7.2 Internal Audits
The Internal Audit department conducts annual security audits covering access controls, encryption, data handling procedures, and incident response. Audit findings must be addressed within defined timelines.

7.3 External Audits
Third-party security assessments are conducted biennially or as required by customers or regulators. Penetration testing is performed quarterly by qualified security firms.

7.4 Certification Maintenance
We maintain SOC 2 Type II certification, ISO 27001 certification, and industry-specific certifications as required. Certification audits are prepared for annually with full cooperation from all departments.

7.5 Non-Compliance Consequences
Non-compliance with this policy may result in disciplinary action including written warnings, suspension, termination of employment, or legal action. Intentional violations will be referred to law enforcement when appropriate.

8. EMPLOYEE RESPONSIBILITIES

8.1 Training Requirements
All employees must complete annual security training acknowledging their understanding of this policy. New employees must complete training within 30 days of hire. Specialized training is required for employees handling confidential data.

8.2 Acceptable Use
Company data and systems must be used only for legitimate business purposes. Personal use is permitted within reasonable limits but must not compromise security. Data must not be stored on personal devices without authorization.

8.3 Phishing Awareness
Employees must be vigilant against phishing attempts. Suspicious emails should be reported to the SOC. Security awareness training includes phishing simulations to improve detection skills.

8.4 Physical Security
Employees must protect physical access to data systems and storage media. Workstations must be locked when unattended. Documents containing confidential data must be stored securely and shredded when no longer needed.

8.5 Remote Work Security
Remote work must follow the same security standards as on-site work. Home networks must be secured with strong passwords and encryption. VPN must be used for all remote access to internal systems.

9. THIRD-PARTY RISK MANAGEMENT

9.1 Vendor Due Diligence
All third-party vendors handling company data must undergo security due diligence before engagement. Due diligence includes security questionnaires, assessment of certifications, and review of security practices.

9.2 Contractual Requirements
Vendor contracts must include security requirements specifying data protection measures, incident response obligations, breach notification requirements, and right-to-audit clauses.

9.3 Ongoing Monitoring
Vendor security performance is monitored quarterly. High-risk vendors are subject to annual on-site security assessments. Vendor security incidents must be reported immediately.

9.4 Data Processing Agreements
All data processing agreements must specify the scope of data processing, security measures, confidentiality obligations, and data return or destruction requirements.

10. POLICY GOVERNANCE

10.1 Policy Ownership
This policy is owned by the Chief Information Security Officer. Changes to this policy require approval from the CISO, Legal, and Executive Leadership.

10.2 Review Schedule
This policy is reviewed annually to address new threats, regulatory changes, and business requirements. Emergency updates may be made in response to significant security incidents or regulatory changes.

10.3 Exception Process
Exceptions to this policy may be granted in exceptional circumstances with documented business justification. Exceptions require approval from the CISO and relevant business leaders. Exceptions are temporary and must be reviewed quarterly.

10.4 Policy Distribution
This policy is distributed to all employees through the company intranet. Acknowledgment of understanding is required annually. The policy is available in multiple languages as needed.

11. CONTACT INFORMATION

For questions about this policy, to report security incidents, or to request policy exceptions, contact:

Security Operations Center: security@nexusinnovations.com
Chief Information Security Officer: ciso@nexusinnovations.com
Data Privacy Officer: privacy@nexusinnovations.com
Legal Department: legal@nexusinnovations.com
Human Resources: hr@nexusinnovations.com

Emergency Incident Hotline: 1-800-SECURE-NEXUS (available 24/7)

12. RELATED DOCUMENTS

This policy should be read in conjunction with:
- Acceptable Use Policy
- Incident Response Plan
- Business Continuity Plan
- Vendor Risk Management Policy
- Employee Handbook
- Privacy Policy

This policy is effective as of January 1, 2024, and supersedes all previous data handling policies. By accessing company data systems, individuals acknowledge their understanding and agreement to comply with this policy.
"""

with open("enterprise_data_lake_sample/company_policy.txt", "w") as f:
    f.write(policy_text)
print(f"Generated company policy ({len(policy_text.split())} words)")

# 6. Generate annual_report.pdf
print("Generating annual_report.pdf...")
report_text = """NEXUS INNOVATIONS INC.
ANNUAL REPORT 2024

COMPANY OVERVIEW

Nexus Innovations Inc. is a leading provider of enterprise software solutions, specializing in cloud-based platforms for data management, security, and business intelligence. Founded in 2015, the company has grown to serve over 500 enterprise clients across North America, Europe, and Asia Pacific.

Our mission is to empower organizations with secure, scalable, and intelligent software solutions that drive digital transformation. We are committed to innovation, customer success, and responsible data stewardship.

Leadership Team
Our executive leadership team brings together decades of experience in enterprise software, cybersecurity, and cloud computing. CEO Sarah Martinez joined Nexus in 2018 after a successful tenure at a Fortune 500 technology company. CTO David Chen leads our technology organization with a focus on innovation and engineering excellence. CFO Jennifer Williams oversees financial operations and strategic planning.

Corporate Values
Our core values guide everything we do: customer obsession, technical excellence, integrity, collaboration, and continuous improvement. These values are reflected in our product development, customer relationships, and internal culture.

BUSINESS PERFORMANCE

Revenue Growth
In fiscal year 2024, Nexus Innovations achieved total revenue of $125 million, representing a 28% increase over the previous year. This growth was driven by strong demand for our cloud storage and analytics platforms, particularly in the financial services and healthcare sectors. Our recurring revenue grew to 78% of total revenue, indicating strong customer adoption and retention.

Profitability
We achieved a gross margin of 72% and an operating margin of 18%, both improvements over the previous year. Net income reached $15.2 million, demonstrating our ability to scale profitably while investing in growth initiatives.

Customer Acquisition
We added 87 new enterprise customers in 2024, bringing our total customer base to 512. Our customer retention rate remained strong at 94%, reflecting high satisfaction with our products and services. The average contract value increased by 15%, driven by customers adopting more comprehensive solution bundles.

Market Expansion
We expanded our presence in the Asia Pacific market, opening new offices in Singapore and Tokyo. This strategic expansion contributed to 15% of our total revenue, up from 8% in the previous year. We also established partnerships with local system integrators to accelerate market penetration.

STRATEGIC INITIATIVES

Product Development
Our research and development investment increased to 22% of revenue, up from 18% in the previous year. We launched five major product updates and three new features across our platform portfolio. Our development team grew by 40% to support accelerated innovation.

Partnership Program
We expanded our partner ecosystem to include 150 technology partners and 45 system integrators. Our partner channel now contributes 35% of new business, up from 25% last year. We enhanced our partner program with better training, resources, and incentives.

Digital Transformation
We continued our own digital transformation initiatives, implementing advanced analytics for business intelligence, automating internal processes, and enhancing our customer service capabilities with AI-powered tools. These initiatives improved operational efficiency by 18%.

SALES SUMMARY

Product Performance
Our Analytics Platform was the top-performing product, generating $45 million in revenue. The Security Suite showed strong growth with $32 million in revenue, while our API Gateway reached $28 million. Cloud Storage contributed $20 million, and other products accounted for the remaining $30 million.

Regional Performance
North America remained our largest market with $70 million in revenue. Europe contributed $35 million, Asia Pacific $18 million, and Latin America $2 million. We see significant growth potential in emerging markets and plan to expand our presence accordingly.

Industry Verticals
Financial services accounted for 35% of revenue, healthcare at 25%, manufacturing at 20%, retail at 12%, and other industries at 8%. Our focus on regulated industries has proven successful due to our strong security and compliance capabilities.

Sales Channels
Direct sales contributed 65% of revenue, while partner channels contributed 35%. Our enterprise sales team grew from 40 to 65 representatives to support geographic expansion and increased customer demand.

EMPLOYEE INFORMATION

Workforce Growth
Our employee count grew from 350 to 425 during 2024. We hired 85 new employees across engineering, sales, and customer success teams. Our employee satisfaction score improved to 4.2 out of 5, based on annual surveys.

Diversity and Inclusion
We continue to prioritize diversity and inclusion. Women now represent 42% of our workforce and 35% of leadership positions. Underrepresented minorities make up 28% of our workforce. We implemented unconscious bias training and established employee resource groups.

Talent Development
We invested $2.5 million in employee training and development programs. These initiatives included technical certifications, leadership development, and diversity and inclusion training. Our promotion rate increased to 12% of eligible employees.

Remote Work
We adopted a hybrid work model with 60% of employees working remotely at least part-time. This flexibility has improved employee satisfaction and expanded our talent pool beyond our geographic hubs.

RISK MANAGEMENT

Cybersecurity Risks
We continue to invest in cybersecurity measures to protect our systems and customer data. Our security operations team responded to 45 potential incidents in 2024, none of which resulted in data breaches. We maintain SOC 2 Type II certification and ISO 27001 compliance.

Market Risks
The competitive landscape in enterprise software remains intense. We address this through continuous innovation, strategic partnerships, and focus on customer success. Economic uncertainty may impact customer IT spending, though our diversified product portfolio provides resilience.

Regulatory Risks
Evolving data protection regulations, including GDPR updates and emerging AI regulations, require ongoing compliance investments. We maintain a dedicated compliance team and engage with industry groups to stay ahead of regulatory changes.

Operational Risks
Our cloud infrastructure achieves 99.95% uptime. We have disaster recovery procedures in place and conduct quarterly penetration testing. Our business continuity plan was updated and tested in 2024.

FINANCIAL HIGHLIGHTS

Balance Sheet
Total assets increased to $85 million, driven by investments in technology infrastructure and working capital. Debt remains minimal at $5 million, providing financial flexibility. Cash and cash equivalents stand at $32 million.

Cash Flow
Operating cash flow was $18 million, demonstrating strong cash generation. Capital expenditures totaled $8 million, primarily for data center infrastructure and technology equipment. Free cash flow reached $10 million.

Investor Relations
We held our first earnings call in 2024, engaging with institutional investors and analysts. Our stock performance has been strong, reflecting market confidence in our growth trajectory and execution capabilities.

FUTURE PLANS

Product Innovation
In 2025, we plan to launch three new products: an AI-powered data quality analyzer, automated compliance monitoring tools, and enhanced integration platforms. These products will build on our existing technology stack and address emerging customer needs.

Market Expansion
We plan to enter three new markets: Brazil, India, and Australia. This expansion will require investment in local infrastructure, hiring, and regulatory compliance. We target $150 million in revenue for 2025.

Sustainability Initiatives
We are committed to reducing our environmental impact. Our data centers are powered by 60% renewable energy, and we plan to reach 80% by 2026. We are also implementing remote-first policies to reduce travel-related emissions.

Technology Investment
We will increase R&D investment to 25% of revenue to accelerate product innovation. We plan to expand our AI and machine learning capabilities, particularly in automated data quality assessment and predictive analytics.

Customer Success
We will expand our customer success organization to ensure high adoption and satisfaction. Our goal is to achieve 95% customer retention and increase our Net Promoter Score from 72 to 80.

CONCLUSION

2024 was a year of strong growth and execution for Nexus Innovations. We delivered on our financial targets, expanded our market presence, and strengthened our team. We are well-positioned for continued success in 2025 and beyond.

We remain grateful to our customers, employees, partners, and shareholders for their continued trust and support. Together, we are building the future of enterprise software.

Forward-Looking Statements
This report contains forward-looking statements about our future plans and expectations. Actual results may differ materially due to various risks and uncertainties. Readers should not place undue reliance on these statements.

Contact Information
For investor relations: investors@nexusinnovations.com
For media inquiries: media@nexusinnovations.com
For general information: info@nexusinnovations.com

Nexus Innovations Inc.
450 Technology Boulevard
San Francisco, CA 94107
www.nexusinnovations.com

This report is for informational purposes only and does not constitute an offer to sell securities. Past performance is not indicative of future results.
"""

# Create PDF using PyMuPDF
try:
    import pymupdf as fitz
    doc = fitz.open()
    
    # Create pages with the report text
    lines = report_text.split('\n')
    current_page = doc.new_page()
    y_position = 72  # Start from top margin
    
    font_size_title = 18
    font_size_header = 14
    font_size_body = 11
    
    for line in lines:
        if not line.strip():
            y_position += 10
            continue
        
        # Check if we need a new page
        if y_position > 720:
            current_page = doc.new_page()
            y_position = 72
        
        # Determine font size based on line content
        if line.isupper() and len(line) < 50:
            current_page.insert_text((72, y_position), line, fontsize=font_size_title, fontname="helvetica-bold")
            y_position += 30
        elif line.isupper():
            current_page.insert_text((72, y_position), line, fontsize=font_size_header, fontname="helvetica-bold")
            y_position += 24
        else:
            current_page.insert_text((72, y_position), line, fontsize=font_size_body, fontname="helvetica")
            y_position += 14
    
    page_count = doc.page_count
    doc.save("enterprise_data_lake_sample/annual_report.pdf")
    doc.close()
    print(f"Generated annual report PDF ({page_count} pages)")
except ImportError:
    print("PyMuPDF not available, creating text file instead")
    with open("enterprise_data_lake_sample/annual_report.txt", "w") as f:
        f.write(report_text)
    print(f"Generated annual report as text file")

print("\nAll files generated successfully!")
