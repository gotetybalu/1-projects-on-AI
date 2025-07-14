import re
import json
from pypdf import PdfReader
from collections import defaultdct
data=defaultdict(dict)
def parse_payroll_text(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    section = 'header'
    earnings_start = re.compile(r'^(Basic Salar:)', re.I)
    deductions_start = re.compile(r'^(Provident Fund)', re.I)
    for line in lines:
        if earnings_start.match(line):
            section = 'earnings'
        elif deductions_start.match(line):
            section = 'deductions'
        m_money = re.match(r'(.+?)\s+([\d,]+\.\d{2})$', line)
        if m_money:
            label = m_money.group(1).strip()
            value = float(m_money.group(2).replace(',', ''))
            data[section][label] = value
            continue
        
        # Split other lines: multiple spaces separate key and value
        parts = re.split(r'\s{1,}', line, maxsplit=1)
        if len(parts) == 2:
            key, value = parts
            data['header'][key.strip()] = value.strip()
    
    return dict(data)
if __name__ == '__main__':
    print("pay slip \n")
    pdf_path =r"D:\s.pdf"
    reader = PdfReader(pdf_path)
    text=""
    for page_num, page in enumerate(reader.pages, start=1):
        text += page.extract_text()
    print("prepocessed text")
    print(text)
    

    """payroll = parse_payroll_text(text)
    t=json.dumps(payroll, indent=1)
    print(t)"""
    print("\n")
print("hash table")
def extract_name_value_pairs(text):
    pattern = r'([A-Za-z &]+?)\s(\d{1,3}(?:,\d{3})*(?:\.\d{2}|\.\d{1})|\d+\.?\d*)'
    matches = re.findall(pattern, text)
    output = {}
    for name, value in matches:
        name = name.strip()
        value = value.strip()
        output[name] = value
    return output
# Hash table
result = extract_name_value_pairs(text)
salary_data = result
for key, value in salary_data.items():
    print(f"{key}: {value}")

"""from tabulate import tabulate
data = salary_data
rows = list(data.items())
print(tabulate(rows, headers=["Earnings", "Value"], tablefmt="grid"))"""
def calculate_total_earnings(data):
    total = 0
    skip_keys = {"Total Deductions","Days Paid"}
    for key, value in data.items():
        if key in skip_keys:
            continue
        if isinstance(value, str):
            value = int(float(value.replace(",", "")))
        else:
            value = int(value)
        total += value
    return total

def calculate_net_salary(data):
    earnings = calculate_total_earnings(data)
    deductions = data.get("Total Deductions", 0)
    deductions=int(float(deductions.replace(",", "")))
    return earnings - deductions
def check_loan_eligibility(net_salary):
    if net_salary < 20000:
        return "Not Eligible due to Net Salary is too low"
    elif net_salary < 30000:
        return "Partially Eligible but Limited loan amount will be approved"
    elif net_salary < 50000:
        return "Eligible for Moderate loan"
    else:
        return "Eligible for loan"

total_earnings = calculate_total_earnings(salary_data)
net_salary = calculate_net_salary(salary_data)
eligibility_status = check_loan_eligibility(net_salary)

print(f"Total Earnings:{total_earnings:}")
print(f"Net Salary:{net_salary:}")
print(f"Loan Eligibility:{eligibility_status}")
