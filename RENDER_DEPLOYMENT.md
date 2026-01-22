# 🚀 Deploying to Render

This guide will walk you through deploying your Student Election System to Render.

## Prerequisites

- ✅ A [Render account](https://render.com) (free tier available)
- ✅ Your project in a Git repository (GitHub, GitLab, or Bitbucket)
- ✅ `firebase_credentials.json` file ready
- ✅ Ethereum wallet private key

---

## Step 1: Prepare Your Git Repository

### 1.1 Initialize Git (if not already done)

```bash
git init
git add .
git commit -m "Initial commit - Student Election System"
```

### 1.2 Create GitHub Repository

1. Go to [GitHub](https://github.com/new)
2. Create a new repository (e.g., `student-election-system`)
3. **DO NOT** initialize with README (you already have code)

### 1.3 Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/student-election-system.git
git branch -M main
git push -u origin main
```

> [!IMPORTANT]
> Verify that `.env` and `firebase_credentials.json` are **NOT** pushed to GitHub. Check your `.gitignore` is working correctly.

---

## Step 2: Deploy on Render

### 2.1 Create New Web Service

1. Log into [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select the `student-election-system` repository

### 2.2 Configure Service Settings

Fill in the following:

| Setting | Value |
|---------|-------|
| **Name** | `student-election-app` (or your choice) |
| **Region** | Select closest to you (e.g., Oregon) |
| **Branch** | `main` |
| **Root Directory** | (leave blank) |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |
| **Plan** | `Free` |

---

## Step 3: Set Environment Variables

In the Render dashboard, scroll to **"Environment Variables"** and add:

### Required Variables

| Key | Value | Notes |
|-----|-------|-------|
| `PYTHON_VERSION` | `3.11.0` | Python runtime version |
| `FLASK_SECRET_KEY` | `<generate-random-string>` | Use [RandomKeygen](https://randomkeygen.com/) |
| `ADMIN_PRIVATE_KEY` | `<your-wallet-private-key>` | From MetaMask/wallet |
| `CONTRACT_ADDRESS` | `0x585a1801372e73BabAf4144D306bAF80A7496ae9` | Your deployed contract |
| `RPC_URL` | `https://ethereum-sepolia.publicnode.com` | Sepolia RPC endpoint |
| `ALLOWED_ADMIN_EMAIL` | `your.admin@rvce.edu.in` | Admin email address |
| `FIREBASE_CREDENTIALS_PATH` | `firebase_credentials.json` | Path to Firebase file |
| `PYTHONUNBUFFERED` | `1` | Better logging |

> [!WARNING]
> **NEVER** commit private keys to Git! Always use environment variables on Render.

---

## Step 4: Upload Firebase Credentials

Since `firebase_credentials.json` is gitignored, you need to add it manually:

### Option A: Using Render Shell (Recommended)

1. After first deployment, go to your service dashboard
2. Click **"Shell"** tab
3. Run:
```bash
cat > firebase_credentials.json << 'EOF'
{paste your firebase credentials JSON here}
EOF
```

### Option B: Use Secret Files (Render Paid Plans)

1. In Render dashboard, go to **"Environment"** → **"Secret Files"**
2. Add new secret file:
   - **Filename**: `firebase_credentials.json`
   - **Contents**: Paste your Firebase JSON

---

## Step 5: Deploy!

1. Click **"Create Web Service"**
2. Render will automatically:
   - Pull your code from GitHub
   - Install dependencies
   - Start the application
3. Wait 2-5 minutes for deployment

---

## Step 6: Verify Deployment

### 6.1 Check Logs

1. Go to **"Logs"** tab in Render dashboard
2. Look for:
   ```
   ✅ Firebase initialized
   ✅ Admin Wallet Loaded: 0x...
   ```

### 6.2 Test the Application

1. Click on your service URL (e.g., `https://student-election-app.onrender.com`)
2. You should see the login page
3. Test login with your RVCE email
4. Test admin login at `/admin`

### 6.3 Test Blockchain Connection

1. Log in as a student
2. Go to `/vote`
3. Cast a test vote
4. Check `/results` to verify blockchain integration

---

## Step 7: Set Up Auto-Deploy (Optional)

Render automatically deploys on every push to `main` by default.

To disable:
1. Go to **"Settings"** → **"Build & Deploy"**
2. Toggle **"Auto-Deploy"** off

---

## Troubleshooting

### Issue: "ModuleNotFoundError"
**Solution**: Check that all dependencies are in `requirements.txt`

### Issue: "Firebase initialization failed"
**Solution**: Verify `firebase_credentials.json` was uploaded correctly via Shell

### Issue: "Admin Wallet Loaded" not appearing
**Solution**: Check that `ADMIN_PRIVATE_KEY` is set in environment variables

### Issue: Application keeps restarting
**Solution**: 
1. Check logs for errors
2. Verify all environment variables are set
3. Ensure `gunicorn` is in `requirements.txt`

### Issue: "Port already in use"
**Solution**: Render automatically handles ports. Use `app.run()` without specifying port in production.

---

## Important Notes

### Free Tier Limitations
- **Spin down after 15 minutes** of inactivity
- **Cold starts** may take 30-60 seconds
- Limited to 750 hours/month

### Data Persistence
> [!CAUTION]
> Render's free tier uses **ephemeral storage**. Your database files (`.db`, `.json`) will be reset on each deploy.

**Solutions**:
1. **Use PostgreSQL** (Render offers free PostgreSQL)
2. **Use external storage** (AWS S3, Firebase Storage)
3. **Upgrade to paid plan** with persistent disks

---

## Post-Deployment Configuration

### Update Firebase Authorized Domains

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Go to **Authentication** → **Settings** → **Authorized domains**
4. Add your Render URL: `student-election-app.onrender.com`

### Update Smart Contract (if needed)

If you deployed a new contract, update:
```bash
# In Render Environment Variables
CONTRACT_ADDRESS=<new-contract-address>
```

---

## Monitoring & Maintenance

### View Logs
```bash
# In Render dashboard
Go to "Logs" tab → Filter by severity
```

### Check Resource Usage
```bash
# In Render dashboard
Go to "Metrics" tab
```

### Manual Redeploy
```bash
# In Render dashboard
Click "Manual Deploy" → "Deploy latest commit"
```

---

## Security Checklist

- [ ] All secrets are in environment variables (not in code)
- [ ] `firebase_credentials.json` is not in Git
- [ ] `.env` is not in Git
- [ ] `ADMIN_PRIVATE_KEY` is set as environment variable
- [ ] Admin email is correctly configured
- [ ] Firebase authorized domains include Render URL
- [ ] Rate limiting is enabled (consider adding Flask-Limiter)

---

## Need Help?

- **Render Docs**: https://render.com/docs
- **Flask Deployment**: https://flask.palletsprojects.com/en/latest/deploying/
- **Render Community**: https://community.render.com/

---

**🎉 Your Student Election System is now live!**

Share your Render URL with students and start voting! 🗳️
