
🔐 ZeroHate — Secure AI Content Moderation System

ZeroHate is an AI-powered content moderation system built with Zero Trust Security principles to ensure secure, reliable, and private text classification. It combines modern cybersecurity practices with a DistilBERT-based model to detect toxic content in real time.

🚀 Features
🔑 Secure Authentication
Email verification for account activation
Multi-Factor Authentication (MFA)
OTP-based login verification
🛡️ Zero Trust Security Implementation
Adaptive OTP triggering
Strict access control and verification at every step
🤖 AI-Powered Text Classification
Uses DistilBERT model
Classifies text into:
Toxic
Severely Toxic
Obscene
Threatening
Insulting
Identity Hate
Neutral
🔒 Data Protection
End-to-end encryption using Fernet
Secure storage of user inputs
Protection against unauthorized access
📁 File Upload Support
Supports PDF, DOCX, TXT
Extracts and classifies text securely
Temporary encrypted storage
⏱️ Rate Limiting
Max 5 requests per minute per user
Prevents abuse and brute-force attacks
📊 User Transparency
Users can view past classifications
🏗️ Tech Stack
Frontend: HTML, CSS, JavaScript
Backend: Python (Flask/Django)
AI Model: DistilBERT
Security: Zero Trust Architecture, MFA, OTP
Encryption: Fernet (Symmetric Encryption)
🔐 Zero Trust Implementation

This project follows the principle of "Never Trust, Always Verify" by:

Verifying user identity at every stage
Enforcing MFA and OTP validation
Encrypting sensitive data
Applying strict rate limits
Securing file uploads and processing
📦 Installation
# Clone repository
git clone https://github.com/your-username/zeroTrust-IS.git

# Navigate to project folder
cd zeroTrust-IS

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
📌 Usage
Sign up with your email
Verify account via activation link
Login using OTP verification
Enter or upload text for classification
View results and history
⚠️ Challenges Faced
Managing OTP triggering thresholds
Balancing rate limiting without affecting user experience
Ensing secure encryption and decryption workflow
🌟 Future Improvements
Real-time monitoring dashboard
Improved model accuracy
Advanced threat detection mechanisms
Scalability enhancements
📄 License

This project is for educational and research purposes.

👨‍💻 Author

Developed as part of a cybersecurity + AI integration project.
