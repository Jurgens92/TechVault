# Security Features

This document covers the security features available in TechVault, including HTTPS setup and Two-Factor Authentication (2FA).

## Table of Contents

- [HTTPS Configuration](#https-configuration)
- [Two-Factor Authentication (2FA)](#two-factor-authentication-2fa)
- [Security Best Practices](#security-best-practices)

---

## HTTPS Configuration

TechVault supports automatic HTTPS setup using Let's Encrypt SSL certificates. HTTPS encrypts all communication between your browser and the server, protecting sensitive data.

### Prerequisites for HTTPS

1. **Valid Domain Name**: You must have a domain name (e.g., `techvault.yourdomain.com`) pointing to your server's public IP address
2. **Open Ports**: Port 80 (HTTP) and 443 (HTTPS) must be accessible from the internet
3. **Valid Email**: An email address for Let's Encrypt certificate notifications

**Note**: Let's Encrypt requires a valid domain name. You cannot use an IP address or localhost for SSL certificates.

### Installing with HTTPS

To install TechVault with HTTPS enabled, use the following command:

```bash
PUBLIC_DOMAIN=techvault.yourdomain.com \
ENABLE_HTTPS=true \
ADMIN_EMAIL=admin@yourdomain.com \
sudo -E bash install.sh
```

**Environment Variables:**

- `PUBLIC_DOMAIN` - Your domain name (required for HTTPS)
- `ENABLE_HTTPS` - Set to `true` to enable HTTPS
- `ADMIN_EMAIL` - Your email for Let's Encrypt notifications (optional, but recommended)

### What Happens During HTTPS Setup

1. The installation script installs `certbot` and `python3-certbot-nginx`
2. Nginx is configured with your domain name
3. Certbot obtains an SSL certificate from Let's Encrypt
4. Nginx is automatically configured to:
   - Serve HTTPS on port 443
   - Redirect HTTP to HTTPS
   - Use secure SSL settings
5. A cron job is created to automatically renew certificates before they expire

### Manual HTTPS Configuration

If you've already installed TechVault without HTTPS, you can enable it manually:

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Restart Nginx
sudo systemctl restart nginx
```

### Certificate Renewal

Certbot automatically renews certificates before they expire. You can test the renewal process with:

```bash
sudo certbot renew --dry-run
```

### Checking Certificate Status

To check your current certificate:

```bash
sudo certbot certificates
```

---

## Two-Factor Authentication (2FA)

Two-Factor Authentication (2FA) adds an extra layer of security to your account by requiring a second form of verification in addition to your password.

### What is 2FA?

2FA uses Time-based One-Time Passwords (TOTP) that change every 30 seconds. You'll need an authenticator app on your smartphone to generate these codes.

### Supported Authenticator Apps

- **Google Authenticator** (iOS, Android)
- **Authy** (iOS, Android, Desktop)
- **Microsoft Authenticator** (iOS, Android)
- **1Password** (iOS, Android, Desktop)
- **Bitwarden** (iOS, Android, Desktop)
- Any other TOTP-compatible authenticator

### Enabling 2FA

1. **Log in to TechVault** with your email and password
2. **Navigate to 2FA Security** from the sidebar menu
3. **Click "Enable 2FA"**
4. **Scan the QR Code** with your authenticator app
   - Open your authenticator app
   - Tap the "+" or "Add" button
   - Scan the QR code displayed on screen
   - The app will add "TechVault (your-email@example.com)"
5. **Enter the verification code** displayed in your authenticator app
6. **Save your backup codes** - These are shown only once!
   - Click "Copy All" to copy all codes
   - Store them in a secure location (password manager, safe, etc.)
   - Each backup code can only be used once

### Logging In with 2FA

Once 2FA is enabled, your login process changes:

1. Enter your **email** and **password** as usual
2. You'll be prompted for your **2FA code**
3. Open your authenticator app
4. Enter the **6-digit code** displayed for TechVault
5. Click **Verify** to complete login

### Using Backup Codes

If you lose access to your authenticator app:

1. At the 2FA verification screen, enter a **backup code** instead of the 6-digit code
2. Each backup code works **only once**
3. After using a backup code, you'll see how many codes remain
4. You can regenerate backup codes anytime from the 2FA Security page

### Managing Backup Codes

To regenerate your backup codes:

1. Go to **2FA Security** in the sidebar
2. Scroll to the **Backup Codes** section
3. Click **Regenerate Codes**
4. Enter your password when prompted
5. **Save the new codes** - old codes will no longer work

### Disabling 2FA

If you need to disable 2FA:

1. Go to **2FA Security** in the sidebar
2. Click **Disable 2FA**
3. Enter your **password** to confirm
4. 2FA will be disabled immediately

**Warning**: Disabling 2FA makes your account less secure. Only disable it if absolutely necessary.

### 2FA Status Indicators

On the 2FA Security page, you can see:
- Whether 2FA is enabled or disabled
- Number of remaining backup codes
- When you're running low on backup codes (< 3 remaining), you'll see a warning

---

## Security Best Practices

### General Security

1. **Always use HTTPS in production** - Never use HTTP for real deployments
2. **Use strong passwords** - At least 12 characters with mixed case, numbers, and symbols
3. **Enable 2FA** - Protects your account even if your password is compromised
4. **Keep backup codes secure** - Store them in a password manager or physical safe
5. **Regular updates** - Keep TechVault and the server operating system updated

### Password Security

- Never share your password with anyone
- Use a unique password for TechVault (don't reuse passwords)
- Use a password manager to generate and store strong passwords
- Change your password immediately if you suspect it's been compromised

### 2FA Security

- **Protect your authenticator device** - Use a screen lock on your phone
- **Store backup codes securely** - Treat them like passwords
- **Don't share codes** - Never give 2FA codes to anyone, even if they claim to be support
- **Multiple devices** - Consider setting up the same 2FA on multiple devices
- **Recovery plan** - Keep backup codes in a secure, accessible location

### Server Security

If you're self-hosting TechVault:

1. **Firewall**: Only open necessary ports (80, 443)
2. **SSH Security**: Use SSH keys instead of passwords
3. **Updates**: Enable automatic security updates
4. **Backups**: Regular database backups to a secure location
5. **Monitoring**: Monitor logs for suspicious activity

### Database Security

The installation script automatically:
- Generates a random strong database password
- Stores credentials in `/opt/techvault/installation_credentials.txt` (permissions: 600)
- Uses localhost-only database connections by default

**Recommendations:**
- Store the database credentials in a secure password manager
- Consider encrypting database backups
- Limit database access to the TechVault application only

---

## Troubleshooting

### HTTPS Issues

**Certificate not obtained:**
- Verify your domain DNS points to the server's public IP
- Check that ports 80 and 443 are open and accessible
- Ensure no other service is using port 80 or 443
- Check logs: `sudo journalctl -u nginx -n 100`

**Certificate expired:**
```bash
# Manually renew
sudo certbot renew
sudo systemctl reload nginx
```

### 2FA Issues

**Lost authenticator device:**
- Use a backup code to log in
- Once logged in, regenerate backup codes
- Disable and re-enable 2FA to set up a new device

**Backup codes not working:**
- Ensure you're entering the code exactly as shown (including dashes, or remove all dashes)
- Each code only works once
- If all codes are used, you may need administrator assistance

**Can't access account:**
- If you've lost both your authenticator and backup codes, contact your system administrator
- Administrators can disable 2FA for your account using Django admin panel

**Time sync issues:**
- TOTP codes are time-based and require accurate time
- Ensure your phone's time is set to automatic (synced with network time)
- Server time must also be accurate (use NTP)

---

## Support

For additional help:
- Check the main [README.md](README.md) for general installation and usage
- Check the [INSTALLATION.md](INSTALLATION.md) for detailed installation steps
- Report issues on GitHub: https://github.com/Jurgens92/TechVault/issues
