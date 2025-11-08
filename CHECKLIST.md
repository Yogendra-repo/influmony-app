# ✅ Email Feature Setup Checklist

Use this checklist to set up and test the email feature.

## 📋 Pre-Flight Checklist

### 1. Environment Setup
- [ ] Python virtual environment activated
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] `.env` file created (copied from `.env.example`)

### 2. Email Configuration
- [ ] Email provider chosen (Gmail recommended)
- [ ] For Gmail: 2-Factor Authentication enabled
- [ ] For Gmail: App Password created at https://myaccount.google.com/apppasswords
- [ ] `SMTP_EMAIL` added to `.env`
- [ ] `SMTP_PASSWORD` added to `.env`
- [ ] `SMTP_SERVER` configured (default: smtp.gmail.com)
- [ ] `SMTP_PORT` configured (default: 587)

### 3. Test Email Configuration
- [ ] Run: `python test_email.py`
- [ ] Test email received successfully
- [ ] No authentication errors
- [ ] No connection errors

### 4. Start Application
- [ ] Backend started: `uvicorn main:app --reload`
- [ ] Backend health check: http://localhost:8000/health
- [ ] Frontend started: `streamlit run app.py`
- [ ] Frontend accessible in browser

### 5. Test Email Feature
- [ ] Logged into Streamlit app
- [ ] Entered campaign brief
- [ ] Set search filters
- [ ] Clicked "Find Influencers"
- [ ] Results displayed with personalized messages
- [ ] Email section visible below results
- [ ] Email subject customizable
- [ ] Clicked "Send Emails to All Influencers"
- [ ] Emails sent successfully
- [ ] Results displayed (success/failure)

## 🔍 Verification Steps

### Email Configuration Verification
```bash
# Run test script
python test_email.py

# Expected output:
# ✅ SUCCESS! Email sent successfully!
# 📬 Check your inbox at: your_email@gmail.com
```

### Backend Verification
```bash
# Start backend
uvicorn main:app --reload

# Test health endpoint
# Visit: http://localhost:8000/health
# Expected: {"status":"ok", "rows":1000, ...}
```

### Frontend Verification
```bash
# Start frontend
streamlit run app.py

# Expected: Browser opens to http://localhost:8501
# Login page visible
```

## 🎯 Quick Test Scenario

1. **Login**
   - Username: `admin`
   - Password: `admin`

2. **Search**
   - Brief: "Looking for tech YouTubers"
   - Platform: YouTube
   - Category: Tech
   - Top K: 3

3. **Send Email**
   - Review the 3 results
   - Check personalized messages
   - Click "Send Emails to All Influencers"
   - Verify 3 emails sent

## ⚠️ Common Issues Checklist

If emails aren't sending, check:

- [ ] `.env` file is in the correct directory (project root)
- [ ] Environment variables loaded (restart backend after changing .env)
- [ ] For Gmail: Using App Password, not regular password
- [ ] No typos in SMTP_EMAIL and SMTP_PASSWORD
- [ ] SMTP_SERVER and SMTP_PORT match your provider
- [ ] Firewall not blocking SMTP port (587 or 465)
- [ ] Email provider allows SMTP access
- [ ] Not exceeding rate limits (Gmail: 500/day)

## 📊 Feature Checklist

### Core Features Working
- [ ] Find influencers by campaign brief
- [ ] Filter by platform, category, continent
- [ ] AI-generated personalized messages
- [ ] Email section appears after search
- [ ] Customizable email subject
- [ ] Bulk send to all matched influencers
- [ ] Success/failure tracking
- [ ] Detailed results display

### Advanced Features
- [ ] HTML formatted emails
- [ ] Plain text fallback
- [ ] Error handling with helpful messages
- [ ] Session state persists results
- [ ] Can send multiple campaigns in one session

## 🎓 Learning Resources

- [ ] Read: `EMAIL_SETUP.md` - Full setup guide
- [ ] Read: `QUICK_START_EMAIL.md` - Quick reference
- [ ] Read: `VISUAL_GUIDE.md` - Visual diagrams
- [ ] Read: `IMPLEMENTATION_SUMMARY.md` - Technical details

## 🚀 Production Readiness

Before using in production:

- [ ] Tested with real email addresses
- [ ] Verified emails not going to spam
- [ ] Checked anti-spam compliance
- [ ] Added unsubscribe mechanism (if required)
- [ ] Reviewed email content for professionalism
- [ ] Set up monitoring for failed sends
- [ ] Documented email sending limits
- [ ] Prepared support documentation

## 📝 Notes

**Date**: _______________
**Email Provider**: _______________
**Test Results**: _______________

**Issues Encountered**:
- 
- 
- 

**Solutions Applied**:
- 
- 
- 

---

## ✨ All Done?

If all checkboxes are checked, you're ready to send emails to influencers! 🎉

**Next Steps**:
1. Start finding influencers
2. Send personalized outreach emails
3. Track your campaign success

**Need Help?**
- Check troubleshooting sections in documentation
- Review backend logs for errors
- Test email configuration again with `test_email.py`
