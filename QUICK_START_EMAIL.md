# Quick Start: Email Feature

## 🚀 Quick Setup (5 minutes)

### 1. Configure Email Credentials

Edit your `.env` file and add:

```env
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

**For Gmail**: 
- Go to https://myaccount.google.com/apppasswords
- Create a new App Password
- Copy the 16-character password (no spaces)

### 2. Test Your Configuration

```bash
python test_email.py
```

This will send a test email to yourself. If successful, you're ready!

### 3. Use the Feature

1. Start the backend: `uvicorn main:app --reload`
2. Start the frontend: `streamlit run app.py`
3. Log in to the app (default: admin/admin or demo/demo)
4. Search for influencers
5. Click "📨 Send Emails to All Influencers"

## 📋 What Happens When You Send Emails?

The app will:
1. ✅ Use the personalized outreach message generated for each influencer
2. ✅ Send a professional HTML-formatted email
3. ✅ Track success/failure for each recipient
4. ✅ Show you detailed results

## 🎯 Example Workflow

```
1. Enter brief: "Looking for tech YouTubers to review our new gadget"
2. Set filters: Platform=YouTube, Category=Tech, Top K=5
3. Click "Find Influencers"
4. Review the 5 top matches with their personalized messages
5. Customize email subject if needed
6. Click "Send Emails to All Influencers"
7. Check results - emails sent to all 5 influencers!
```

## ⚡ Tips

- **Test first**: Always run `test_email.py` before using in production
- **Review messages**: Check the AI-generated messages before sending
- **Monitor limits**: Gmail allows ~500 emails/day
- **Stay compliant**: Follow anti-spam laws (include unsubscribe option for bulk sends)

## 🆘 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| "Email credentials not configured" | Add SMTP_EMAIL and SMTP_PASSWORD to .env |
| "Authentication failed" | Use App Password for Gmail, not regular password |
| "Connection timeout" | Check firewall, verify SMTP server/port |
| Emails not arriving | Check spam folder, verify recipient email addresses |

## 📚 More Help

- Full setup guide: [EMAIL_SETUP.md](EMAIL_SETUP.md)
- Test email: `python test_email.py`
- Backend logs: Check terminal running `uvicorn`
