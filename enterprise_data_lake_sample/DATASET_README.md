# Enterprise Data Lake Sample Dataset

## Dataset Overview

This synthetic dataset represents the enterprise data of **Nexus Innovations Inc.**, a fictional enterprise software company founded in 2015. The company provides cloud-based platforms for data management, security, and business intelligence, serving over 500 enterprise clients across North America, Europe, and Asia Pacific.

The dataset is designed for testing the Data Quality Assessment system with realistic heterogeneous data assets that represent common enterprise data lake scenarios.

## Company Profile

**Company Name**: Nexus Innovations Inc.
**Industry**: Enterprise Software Solutions
**Founded**: 2015
**Headquarters**: San Francisco, California
**Employees**: 425 (as of 2024)
**Revenue**: $125 million (fiscal year 2024)
**Customers**: 512 enterprise clients
**Business Focus**: Cloud storage, analytics platforms, security suites, API gateways

## File Descriptions

### 1. customers.csv
**Purpose**: Customer relationship management data containing customer information and status.

**Schema**:
- Customer ID: Unique customer identifier (CUST#####)
- Name: Customer contact name
- Email: Customer email address
- Phone: Customer phone number
- City: Customer city location
- Registration Date: Date when customer registered
- Customer Status: Current status of customer relationship

**Records**: 41 customer records

**Intentional Quality Problems**:
- Row 6: Invalid email format ("invalid-email")
- Row 11: Missing email (empty string)
- Row 16: Inconsistent status value ("Premium" not in standard set)
- Row 21: Missing city (empty string)
- Row 26: Missing registration date (empty string)
- Row 31: Case inconsistency in status ("active" vs "Active")
- Row 41: Duplicate record (duplicate of Row 1)

**Expected Issues to be Detected**:
- Missing values (email, city, registration date)
- Duplicate rows
- Invalid email format
- Inconsistent categorical values (Customer Status)
- Case inconsistency in categorical values

**Relationships**: Customer IDs are referenced in sales.xlsx

---

### 2. sales.xlsx
**Purpose**: Sales transaction data recording sales activities across products and regions.

**Schema**:
- Sale ID: Unique sale identifier (SALE######)
- Customer ID: Reference to customers.csv
- Product ID: Product identifier (PROD###)
- Sale Date: Date of sale transaction
- Quantity: Number of units sold
- Unit Price: Price per unit
- Total Amount: Calculated total (Quantity × Unit Price)
- Region: Geographic region of sale

**Records**: 46 sales records

**Intentional Quality Problems**:
- Row 6: Invalid negative quantity (-5)
- Row 11: Missing unit price (empty string)
- Row 16: Invalid customer ID reference (CUST99999 not in customers.csv)
- Row 21: Invalid negative total amount (-1000)
- Row 26: Invalid date format (2024-13-45)
- Row 31: Outlier quantity (10000, far above normal range)
- Row 46: Duplicate record (duplicate of Row 1)

**Expected Issues to be Detected**:
- Missing values (unit price)
- Duplicate rows
- Invalid numeric values (negative quantity, negative total)
- Outliers (quantity = 10000)
- Invalid date format
- Referential integrity issue (invalid Customer ID)

**Relationships**: References Customer IDs from customers.csv

---

### 3. employee_records.json
**Purpose**: Human resources data containing employee information and employment details.

**Schema**:
- Employee ID: Unique employee identifier (EMP####)
- Name: Employee full name
- Department: Department within the company
- Age: Employee age
- Salary: Annual salary
- Hire Date: Date when employee was hired
- Employment Status: Current employment status

**Records**: 36 employee records

**Intentional Quality Problems**:
- Row 6: Invalid age (150, impossible value)
- Row 11: Missing salary (empty string)
- Row 16: Inconsistent department ("Management" not in standard set)
- Row 21: Missing hire date (empty string)
- Row 26: Inconsistent employment status ("permanent" vs "Full-time")
- Row 31: Edge case age (18, minimum working age)
- Row 36: Duplicate record (duplicate of Row 1)

**Expected Issues to be Detected**:
- Missing values (salary, hire date)
- Duplicate rows
- Invalid numeric values (age = 150)
- Outliers (age = 150)
- Inconsistent categorical values (Department, Employment Status)

**Relationships**: Employee IDs are referenced in application_logs.xml

---

### 4. application_logs.xml
**Purpose**: Application system logs recording service requests, response times, and status codes.

**Schema**:
- Log ID: Unique log identifier (LOG#######)
- Timestamp: Date and time of log entry
- Employee ID: Reference to employee_records.json
- Service: Name of service generating the log
- Log Level: Severity level of the log entry
- Response Time: Request processing time in milliseconds
- Status Code: HTTP status code
- Message: Log message description

**Records**: 41 log records

**Intentional Quality Problems**:
- Row 6: Invalid negative response time (-100)
- Row 11: Invalid status code ("999" not standard HTTP code)
- Row 16: Invalid employee ID reference (EMP9999 not in employee_records.json)
- Row 21: Missing timestamp (empty string)
- Row 26: Inconsistent log level ("CRITICAL" not in standard set)
- Row 31: Outlier response time (100000, far above normal range)
- Row 41: Duplicate record (duplicate of Row 1)

**Expected Issues to be Detected**:
- Missing values (timestamp)
- Duplicate rows
- Invalid numeric values (negative response time)
- Outliers (response time = 100000)
- Inconsistent categorical values (Log Level, Status Code)
- Referential integrity issue (invalid Employee ID)

**Relationships**: References Employee IDs from employee_records.json

---

### 5. company_policy.txt
**Purpose**: Corporate data handling and security policy document.

**Content**: Comprehensive data security policy covering:
- Data classification (Confidential, Internal, Public)
- Access control and authentication
- Encryption requirements
- Data retention and disposal
- Incident response procedures
- Compliance requirements
- Employee responsibilities
- Third-party risk management

**Length**: 1,687 words

**Quality Status**: CLEAN - No intentional quality problems

**Expected Issues to be Detected**: None (clean text)

**Purpose in Dataset**: Demonstrates clean unstructured text that should receive a high quality score

---

### 6. annual_report.pdf
**Purpose**: Annual business report summarizing company performance, operations, and future plans.

**Content**: Comprehensive annual report including:
- Company overview and leadership
- Business performance and financial highlights
- Sales summary by product and region
- Employee information and workforce growth
- Risk management
- Future plans and strategic initiatives
- Contact information

**Length**: 3 pages

**Quality Status**: CLEAN - No intentional quality problems

**Expected Issues to be Detected**: None (clean PDF)

**Purpose in Dataset**: Demonstrates clean unstructured PDF that should receive a high quality score

---

## Data Relationships

The dataset includes referential relationships between files:

1. **customers.csv → sales.xlsx**
   - sales.Customer ID references customers.Customer ID
   - Intentional invalid reference: sales Row 16 (CUST99999)

2. **employee_records.json → application_logs.xml**
   - application_logs.Employee ID references employee_records.Employee ID
   - Intentional invalid reference: logs Row 16 (EMP9999)

These relationships allow testing of:
- Referential integrity checks
- Cross-file data validation
- Orphaned record detection

## Quality Problem Distribution

Not all files have the same level of quality issues:

- **customers.csv**: Moderate issues (7 intentional problems)
- **sales.xlsx**: Moderate issues (7 intentional problems)
- **employee_records.json**: Moderate issues (7 intentional problems)
- **application_logs.xml**: Moderate issues (7 intentional problems)
- **company_policy.txt**: Clean (0 intentional problems)
- **annual_report.pdf**: Clean (0 intentional problems)

This distribution allows testing:
- Detection of various issue types
- Comparison between problematic and clean data
- Quality scoring differentiation

## Expected Detection by Current Quality Engine

The current Data Quality Assessment system should detect:

### Structured Data (CSV, Excel, JSON, XML)
- ✅ Missing values (empty strings, nulls)
- ✅ Duplicate rows
- ✅ Invalid numeric values (negative where inappropriate)
- ✅ Outliers (values far outside normal range)
- ✅ Invalid date formats
- ✅ Inconsistent categorical values
- ✅ Case inconsistencies
- ⚠️ Referential integrity (may require custom rules)

### Unstructured Data (TXT, PDF)
- ✅ Short text detection (if applicable)
- ✅ Repetitive content detection (if applicable)
- ✅ Special character detection (if applicable)
- ✅ Encoding issues (if present)

### Current Limitations
- Referential integrity checks between files (not implemented)
- Semantic validation (e.g., business rules)
- Cross-file relationship validation
- Data lineage tracking

## Usage Instructions

1. Upload each file individually to the Data Quality Assessment system
2. Review the quality report for each file
3. Compare detected issues with the intentional problems listed above
4. Verify that clean files (company_policy.txt, annual_report.pdf) receive high quality scores
5. Note any issues not detected by the current quality engine
6. Use results to identify areas for quality engine enhancement

## File Verification

All files have been verified to be readable:
- ✅ customers.csv: Valid CSV format, 41 records
- ✅ sales.xlsx: Valid Excel format, 46 records
- ✅ employee_records.json: Valid JSON format, 36 records
- ✅ application_logs.xml: Valid XML format, 41 records
- ✅ company_policy.txt: Valid text file, 1,687 words
- ✅ annual_report.pdf: Valid PDF format, 3 pages, text-based

## Disclaimer

This dataset contains entirely fictional and synthetic data. All names, addresses, phone numbers, email addresses, and other information are fictional. No real personal information is included. The company "Nexus Innovations Inc." is fictional and any resemblance to real companies is coincidental.

## Dataset Version

Version: 1.0
Created: January 2025
Purpose: Data Quality Assessment system testing
License: Internal use only for academic and testing purposes
