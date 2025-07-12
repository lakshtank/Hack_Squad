# Testing the Forgot Password Feature

## 🧪 How to Test the Forgot Password Functionality

### Step 1: Start the Application
```bash
python3 app.py
```

### Step 2: Access the Login Page
1. Open your browser and go to: `http://localhost:8000/login`
2. You should see the login form with a "Forgot Password?" link below the password field

### Step 3: Test the Forgot Password Flow
1. **Click "Forgot Password?"** - This will take you to the forgot password page
2. **Enter a registered email address** - Use an email that exists in your database
3. **Click "Send Reset Link"** - You should see a success message with a clickable reset link
4. **Click the reset link** - This will take you to the reset password page
5. **Enter a new password** - Must be at least 6 characters
6. **Confirm the password** - Must match the first password
7. **Click "Reset Password"** - You should see a success message
8. **Try logging in** - Use your new password to log in

### Step 4: Test Error Cases
1. **Invalid email** - Enter an email that doesn't exist in the database
2. **Expired token** - Wait 24 hours or manually expire tokens in the database
3. **Used token** - Try using the same reset link twice
4. **Invalid password** - Try passwords less than 6 characters
5. **Mismatched passwords** - Enter different passwords in the confirmation field

## 🔧 Current Configuration

The app is currently configured to **show reset links directly** instead of sending emails. This is perfect for testing!

### To Enable Email Sending:
1. Edit `app.py`
2. Change this line:
   ```python
   app.config['SHOW_RESET_LINKS'] = True
   ```
   to:
   ```python
   app.config['SHOW_RESET_LINKS'] = False
   ```
3. Update the email configuration:
   ```python
   app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
   app.config['MAIL_PASSWORD'] = 'your-app-password'
   app.config['MAIL_DEFAULT_SENDER'] = 'your-email@gmail.com'
   ```

## 📝 Expected Behavior

### ✅ Success Cases:
- **Valid email**: Shows reset link with success message
- **Valid token**: Allows password reset
- **Valid password**: Successfully updates password

### ❌ Error Cases:
- **Invalid email**: Shows "Email not found" message
- **Invalid token**: Shows "Invalid or expired reset link"
- **Expired token**: Shows "Reset link has expired"
- **Used token**: Shows "Invalid or expired reset link"
- **Short password**: Shows "Password must be at least 6 characters"
- **Mismatched passwords**: Shows "Passwords do not match"

## 🎯 Test Data

If you don't have any users in your database, create one first:
1. Go to `http://localhost:8000/signup`
2. Create a new account
3. Use that email address to test the forgot password feature

## 🔍 Troubleshooting

### If you get "ModuleNotFoundError: No module named 'flask_mail'":
```bash
pip3 install Flask-Mail==0.9.1
```

### If the server won't start:
1. Check if port 8000 is already in use
2. Kill any existing processes: `lsof -ti:8000 | xargs kill -9`
3. Restart the server: `python3 app.py`

### If the database needs updating:
```bash
python3 update_database.py
```

## 🎉 Success!

Once you can successfully:
1. Request a password reset
2. See the reset link
3. Click the link
4. Set a new password
5. Log in with the new password

Then the forgot password feature is working perfectly! 🚀 