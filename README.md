# 🤖 Resume Screening AI Bot

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Built%20With-Streamlit-ff4b4b)

An intelligent AI-powered Resume Screening App built with **Streamlit**. It automatically extracts key information like **email**, **phone number**, and **location**, and matches resumes against a **Job Description (JD)**. You can also **download the results in Excel format**.

---

## 📸 Demo Screenshots

| Home Page | Prediction Page |
|-----------|-----------------|
| ![Home Page](images/1.png) | ![Prediction Page](images/2.png) |

| Uploaded Resume | Excel Download |
|------------------|----------------|
| ![Uploaded File](images/3.png) | ![Excel Output](images/4.png) |

---

## 🚀 Features

- Upload multiple PDF resumes 📂
- Paste job description (JD) text 📄
- Extract:
  - Name
  - Email
  - Phone Number
  - Location
  - Match Score 🔍
- View results in a table 📊
- Download as `.xlsx` Excel file 📥
- One-click refresh 🔄

---

## 🧠 Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **PDF Parsing**: PyMuPDF (`fitz`)
- **Excel Handling**: Pandas, Openpyxl

---

## 🛠️ Libraries Used

| Library | Purpose |
|--------|---------|
| `streamlit` | Web interface |
| `pandas` | Data handling and Excel export |
| `fitz` (PyMuPDF) | Extract text from PDFs |
| `re` | Extract emails, phone numbers, locations |
| `difflib` | Compute match scores |
| `base64` | Download button for Excel |
| `io` | In-memory file handling |
| `openpyxl` | Save Excel file properly |

---

## 🧪 How to Run Locally

1. **Clone the repository**
   ```bash
   git clone https://github.com/DevWaqarAhmad/Resume-Screening-Bot.git
   cd Resume-Screening-Bot
