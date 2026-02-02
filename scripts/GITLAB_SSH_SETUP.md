# GitLab SSH Key Setup for Doug (sdw3098)

## SSH Key Generated

An SSH key has been generated for Doug at:
- **Private key**: `/home/sdw3098/.ssh/id_ed25519_gitlab`
- **Public key**: `/home/sdw3098/.ssh/id_ed25519_gitlab.pub`

## Public Key (to add to GitLab)

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIEK5hqhZiy4Rav9lkTSXLyMe6UOUn+jmgHz6IMgaH5rx sdw3098@ttu.edu
```

## Steps to Complete GitLab Setup

1. **Copy the public key above** (or retrieve it):
   ```bash
   sudo -u sdw3098 cat /home/sdw3098/.ssh/id_ed25519_gitlab.pub
   ```

2. **Add to GitLab**:
   - Go to: https://gitlab.com/-/profile/keys
   - Or: https://gitlab.com/profile/keys
   - Click "Add new key"
   - Paste the public key
   - Give it a title (e.g., "sdw3098-server")
   - Click "Add key"

3. **Test connection**:
   ```bash
   sudo -u sdw3098 ssh -T git@gitlab.com
   ```
   Should show: "Welcome to GitLab, @username!"

4. **Push to GitLab**:
   ```bash
   sudo -u sdw3098 bash -c 'cd /home/sdw3098/canvas-lms-mcp && git push -uf origin main'
   ```

## Current Status

- ✅ SSH key generated
- ✅ SSH config configured
- ✅ GitLab added to known_hosts
- ✅ Repository remote configured
- ⏳ Waiting for SSH key to be added to GitLab account
- ⏳ Push pending until SSH key is added