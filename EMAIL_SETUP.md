# Email Integration Setup Guide

This guide will help you configure email sending functionality to reach out to top influencers.

## 📧 Email Feature Overview

Once you've found your top influencers using the search feature, you can:
- Send personalized outreach emails to all matched influencers
- Customize the email subject
- Use AI-generated outreach messages (if Gemini is configured)
- Track which emails were sent successfully

## ⚙️ Configuration Steps

### Option 1: Gmail (Recommended)

1. **Enable 2-Factor Authentication**
   - Go to your Google Account: https://myaccount.google.com/security
   - Enable 2-Step Verification if not already enabled

2. **Create an App Password**
   - Visit: https://myaccount.google.com/apppasswords
   - Select "Mail" as the app and your device
   - Click "Generate"
   - Copy the 16-character password (no spaces)

3. **Update .env file**
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_EMAIL=your_email@gmail.com
   SMTP_PASSWORD=your_16_char_app_password
   ```

### Option 2: Outlook/Hotmail

```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_EMAIL=your_email@outlook.com
SMTP_PASSWORD=your_password
```

### Option 3: Yahoo Mail

```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_EMAIL=your_email@yahoo.com
SMTP_PASSWORD=your_app_password
```

### Option 4: Custom SMTP Server

```env
SMTP_SERVER=your.smtp.server.com
SMTP_PORT=587
SMTP_EMAIL=your_email@domain.com
SMTP_PASSWORD=your_password
```

## 🚀 How to Use

1. **Start the Backend**
   ```bash
   uvicorn main:app --reload
   ```

2. **Start the Frontend**
   ```bash
   streamlit run app.py
   ```

3. **Find Influencers**
   - Log in to the app
   - Enter your campaign brief
   - Set filters (platform, category, continent, follower count)
   - Click "🔍 Find Influencers"

4. **Send Emails**
   - Review the matched influencers and their personalized messages
   - Customize the email subject if needed
   - Click "📨 Send Emails to All Influencers"
   - Monitor the sending status and results

## 📝 Email Template

Emails are sent with:
- **Subject**: Customizable (default based on campaign brief)
- **Body**: Personalized outreach message (AI-generated or template)
- **Format**: HTML and plain text versions
- **From**: Your configured SMTP email

## 🔍 Troubleshooting

### "Email credentials not configured"
- Make sure `.env` file exists (copy from `.env.example`)
- Verify `SMTP_EMAIL` and `SMTP_PASSWORD` are set

### "Authentication failed"
- For Gmail: Use App Password, not regular password
- For other providers: Check if "Less secure app access" needs to be enabled
- Verify email and password are correct

### "Connection timeout"
- Check your firewall/antivirus settings
- Verify SMTP server and port are correct
- Try port 465 with SSL instead of 587 with TLS

### "Failed to send email"
- Check recipient email addresses are valid
- Verify your email provider's sending limits
- Check spam/rate limiting policies

## 🔒 Security Best Practices

1. **Never commit `.env` file** to version control
2. **Use App Passwords** instead of regular passwords
3. **Rotate credentials** regularly
4. **Monitor sending activity** for unusual patterns
5. **Respect rate limits** of your email provider

## 📊 Sending Limits

Common provider limits:
- **Gmail**: 500 emails/day (with App Password)
- **Outlook**: 300 emails/day
- **Yahoo**: 500 emails/day
- **Custom SMTP**: Check with your provider

## 🎯 Features

- ✅ Bulk email sending to multiple influencers
- ✅ Personalized messages for each influencer
- ✅ HTML formatted emails
- ✅ Success/failure tracking
- ✅ Detailed error reporting
- ✅ Customizable subject lines

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the FastAPI logs in the terminal
3. Verify your email provider's documentation
4. Check the email sending results in the Streamlit interface
