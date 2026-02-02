# Plan: Collaborators – UNIX Accounts and GitHub/GitLab Invites

This document records: (1) groups created on GitHub and GitLab, (2) user lookup by name on GitHub/GitLab and Texas Tech directory/LDAP, (3) result of running `run_repo_sync_test_plan.sh`, and (4) a plan to add local UNIX accounts and invite all listed accounts to collaborate on the repository.

---

## 1. Groups Created

### GitHub

- **Team:** `canvas-lms-mcp-collaborators`
- **Organization:** `websharpstudios`
- **URL:** https://github.com/orgs/websharpstudios/teams/canvas-lms-mcp-collaborators
- **Created:** Via `gh api /orgs/websharpstudios/teams --method POST -f name="canvas-lms-mcp-collaborators" -f description="Collaborators for canvas-lms-mcp repository" -f privacy=closed`
- **Note:** The repository `canvas-lms-mcp` is under the **user** `sweeden-ttu`, not the org. Collaborators are added at the repo level (Settings → Collaborators). The team is available for grouping if the repo is later moved under `websharpstudios` or for adding org members to the team and then granting the team access to repos under the org.

### GitLab

- **Group:** Not created automatically (GitLab CLI `glab` was not authenticated; no `GITLAB_TOKEN` in env_save).
- **To create:** Either:
  1. Add `GITLAB_TOKEN` to `env_save` (GitLab Personal Access Token with `api` scope), then run:  
     `glab api /groups --method POST --field name="canvas-lms-mcp-collaborators" --field path="canvas-lms-mcp-collaborators" --field visibility=private`
  2. Or in GitLab: **Groups → New group** → name e.g. `canvas-lms-mcp-collaborators`, path `canvas-lms-mcp-collaborators`, visibility Private.

---

## 2. jck1278 (Casey) – Lookup and Invite

**GitHub username for jck1278:** **JCKING7878** (not jck1278).

**Lookup:**

- **GitHub:** No user with login `jck1278` exists. Casey’s GitHub account is **JCKING7878** (https://github.com/JCKING7878).
- **GitLab:** No user with username `jck1278` or `jcking7878` found. To invite on GitLab, Casey needs to create an account or share their GitLab username/email.

**Invite status (2026-02-02):**

- **GitHub repo (sweeden-ttu/canvas-lms-mcp):** **JCKING7878** was added as a collaborator with push permission (invitation created; they may need to accept in GitHub).
- **GitHub team (canvas-lms-mcp-collaborators):** **JCKING7878** was added to the team under org `websharpstudios` (membership state: pending until they accept if applicable).
- **GitLab (sweeden3/canvas-lms-mcp):** Not done—no GitLab user `jcking7878` found. Invite via **Members → Invite** once Casey has a GitLab account (username or email).

---

## 2b. Additional GitHub repo invites (confident name matches)

Invited to **sweeden-ttu/canvas-lms-mcp** with push permission (2026-02-02):

- **asiamina** (Akbar Siami Namin) – invitation sent; acceptance pending.
- **onyeka050** (Onyeka Onwubiko) – invitation sent; acceptance pending.

Adding them to the org team **canvas-lms-mcp-collaborators** (websharpstudios) requires inviting them to the organization first; the team is optional and documented in section 5.

---

## 3. User Lookup by Name (12 collaborators)

Target names:

- Akbar Siami Namin, Hasan Al-Qudah, Hanyao Zeng, Josiah Luke, Rocco Swaney, Hayden Hoppe, Kelly Nunez, Sonali Singh, Daniel Diaz Santiago, Onyeka Onwubiko, Judith Lopez, Chidera Agbogu

### 2.1 GitHub Search (by full name)

| Full Name              | GitHub Login (candidate) | Notes |
|------------------------|--------------------------|--------|
| Akbar Siami Namin      | **asiamina**             | 1 match; likely TTU faculty (Akbar Siami-Namin). |
| Hasan Al-Qudah         | —                        | 0 matches. |
| Hanyao Zeng            | —                        | 0 matches. |
| Josiah Luke            | Josiah-Watson, rukujosiah| 2 matches; verify which is TTU. |
| Rocco Swaney           | —                        | 0 matches. |
| Hayden Hoppe           | —                        | 0 matches. |
| Kelly Nunez            | knubez, Kellynunez, kellynnunez, kelnunez | 4+ matches; verify which is TTU. |
| Sonali Singh           | sonali-singh97, sonalisingh18, Sonali9737, … | Many matches; verify which is TTU. |
| Daniel Diaz Santiago   | diaz3618, danielpsantiago, danielsantiago, … | Many matches; “Daniel Diaz” + “Santiago” suggests **diaz3618** or confirm with email. |
| Onyeka Onwubiko         | **onyeka050**            | 1 match. |
| Judith Lopez           | JudSL, judithlr, Judithlf, … | 7 matches; verify which is TTU. |
| Chidera Agbogu         | —                        | 0 matches. |

Search used: `gh api "search/users?q=<First Last>+in:fullname"`. Ambiguous names require confirmation (e.g. by TTU email or direct ask).

### 2.2 GitLab Search

- GitLab user search was not run (API requires authentication; `glab` had no token).
- **To search:** After setting `GITLAB_TOKEN`, use GitLab API or web: **Search** → Users, or `glab api /users?search=<name>`.

### 2.3 Texas Tech Directory / LDAP

- **LDAP:** `ldapsearch` against `ldap://directory.ttu.edu` was tried from this environment; server was not reachable (e.g. network/firewall). Email lookup via LDAP could not be performed here.
- **TTU directory / web:**  
  - **Akbar Siami Namin:** Confirmed TTU CS faculty; email **akbar.namin@ttu.edu** (and/or akbar.siami-namin@ttu.edu from faculty page).  
  - Other names were not found in the limited public TTU pages checked; they may be students or use different listings.

**Suggested email pattern for TTU:** `firstname.lastname@ttu.edu` or `eid@ttu.edu` (EID from Registrar). To resolve emails for the rest:

1. Use TTU’s official directory or Registrar directory request (https://www.depts.ttu.edu/registrar/Directory_Information.php) if you have access.
2. If you have LDAP access from a TTU network, run for each name something like:  
   `ldapsearch -x -H ldap://directory.ttu.edu -b "dc=ttu,dc=edu" "(cn=*<Name>*)" mail`
3. Confirm with the course/instructor list or department (e.g. cs@ttu.edu) for current students/TAs.

**Placeholder table (fill once emails are known):**

| Full Name              | TTU / LDAP Email     | GitHub (verified) | GitLab (after lookup) |
|------------------------|----------------------|-------------------|------------------------|
| Akbar Siami Namin      | akbar.namin@ttu.edu  | asiamina          | —                      |
| Hasan Al-Qudah         | (lookup)             | —                 | —                      |
| Hanyao Zeng            | (lookup)             | —                 | —                      |
| Josiah Luke            | (lookup)             | (verify)          | —                      |
| Rocco Swaney           | (lookup)             | —                 | —                      |
| Hayden Hoppe           | (lookup)             | —                 | —                      |
| Kelly Nunez            | (lookup)             | (verify)          | —                      |
| Sonali Singh           | (lookup)             | (verify)          | —                      |
| Daniel Diaz Santiago   | (lookup)             | (verify)          | —                      |
| Onyeka Onwubiko        | (lookup)             | onyeka050         | —                      |
| Judith Lopez           | (lookup)             | (verify)          | —                      |
| Chidera Agbogu         | (lookup)             | —                 | —                      |

---

## 4. Run of `run_repo_sync_test_plan.sh`

- **Command:** `sudo bash /mnt/shared/Shared/scripts/run_repo_sync_test_plan.sh /mnt/shared/Shared/env_save`
- **Result:** Script completed; multiple steps failed.
- **Phase 1 (SSH keys):** SSH keys were ensured for local users `jck1278`, `cursor`, `sdw3098` (Ed25519, non-expiring).
- **Phase 2–4 (clone/push):** Failures due to:
  - User SSH public keys not registered with GitHub or GitLab (Permission denied (publickey)).
  - No `GITLAB_TOKEN` in env_save, so the script could not add keys to GitLab via `glab`.
  - `gh ssh-key add` not used (e.g. needs `gh auth refresh -s admin:public_key` and possibly user interaction).
- **Merge steps:** Some passed where repos exist; cursor repo had permission/safe.directory issues when run as different user.
- **Fix for future runs:** Add `GITLAB_TOKEN` to env_save; run `gh auth refresh -s admin:public_key` and complete device flow; then re-run the script so it can register keys and retry clone/push.

---

## 5. Plan: Add UNIX Accounts and Invite to GitHub/GitLab

### 5.1 Local UNIX Accounts

For each of the 12 people, create a local UNIX account on the machine(s) where repo sync and SSH are used (e.g. billnye / shared server):

1. **Choose username:** Prefer TTU EID if available (e.g. from LDAP or Registrar); otherwise a consistent scheme (e.g. `firstnamelastname` or `flastname`), avoiding clashes with existing users.
2. **Create account (example):**  
   `sudo useradd -m -c "Full Name" -s /bin/bash <username>`
3. **Set initial password or SSH-only:**  
   - Either: `sudo passwd <username>` and force change on first login.  
   - Or: no password, SSH key only (key added in step 4).
4. **Add SSH key for repo access:**  
   - Generate or install key: e.g. `sudo -u <username> ssh-keygen -t ed25519 -C "<username>@ttu" -f /home/<username>/.ssh/id_ed25519 -N ""`.  
   - Add the same public key to GitHub and GitLab (see below) so git over SSH works without passwords.
5. **Optional:** Add users to a shared group (e.g. `canvasdev`) and set repo/home permissions so cross-user merge tests (as in the test plan) can run.
6. **Safe directory (if needed):**  
   `sudo -u <username> git config --global --add safe.directory /path/to/canvas-lms-mcp` for each repo path that user will use.

**Order of operations:** Prefer creating accounts after you have a confirmed list of usernames (and optionally emails) so you don’t rename accounts later.

### 4.2 Invite to GitHub Repository

- **Repo:** `sweeden-ttu/canvas-lms-mcp` (user-owned).
- **How:** Repo → **Settings → Collaborators → Add people**. Enter GitHub username or email. Choose role (e.g. Write).
- **Candidates from section 2:**  
  - Confident: `asiamina`, `onyeka050`.  
  - Verify then add: Josiah Luke, Kelly Nunez, Sonali Singh, Daniel Diaz Santiago, Judith Lopez (use table in 2.1).
- **Team (if repo moves to org):** Add the same users to the team `websharpstudios/canvas-lms-mcp-collaborators` and give the team access to the repo.

**CLI (if you have admin on repo):**  
`gh api repos/sweeden-ttu/canvas-lms-mcp/collaborators/<username> --method PUT -f permission=push`

### 5.3 Invite to GitLab Project

- **Project:** `sweeden3/canvas-lms-mcp` on GitLab.com.
- **How:** Project → **Members → Invite members**. Enter GitLab username or email. Choose role (e.g. Developer).
- **Finding users:** After setting `GITLAB_TOKEN`, search users (web or API) and invite by username/email. If they don’t have GitLab accounts, invite by email; they will get an invite to sign up and join.

**CLI (with glab authenticated):**  
`glab api projects/sweeden3%2Fcanvas-lms-mcp/members --method POST --field user_id=<user_id> --field access_level=30`  
(User ID from `glab api /users?username=<username>`.)

### 5.4 Optional: GitLab Group

- Create group `canvas-lms-mcp-collaborators` (see section 1).
- Add each member to the group (Developer or appropriate role).
- Attach the group to the project `sweeden3/canvas-lms-mcp` with the desired access level so one place manages collaborators.

### 5.5 Checklist (per person)

- [ ] TTU/LDAP email resolved (if applicable).
- [ ] GitHub identity resolved (search + confirm); invite to `sweeden-ttu/canvas-lms-mcp`.
- [ ] GitLab identity resolved (search or invite by email); invite to `sweeden3/canvas-lms-mcp`.
- [ ] Local UNIX account created; SSH key generated/installed.
- [ ] Same SSH public key added to GitHub and GitLab (so clone/push work without passwords).
- [ ] Optional: Add to GitHub team `canvas-lms-mcp-collaborators` and/or GitLab group.

---

## 5.6 CI/CD strip-secrets (env_save / .env.save)

- **GitHub:** `.github/workflows/autogen-ci.yml` includes job `strip-env-save` (runs first). If `env_save` or `.env.save` are in the repo, they are removed, committed with `[skip ci]`, and pushed. Build/test then run on the cleaned tree.
- **GitLab:** `.gitlab-ci.yml` includes stage `strip-secrets` and job `strip-env-save`. Same logic; push uses `GITLAB_STRIP_TOKEN`.
- **GITLAB_STRIP_TOKEN:** Configured in project CI/CD variables at https://gitlab.com/sweeden3/canvas-lms-mcp/-/settings/ci_cd#js-cicd-variables-settings. Pipeline can now push removal commits when credentials are committed. `.gitignore` includes `env_save` and `.env.save`.

---

## 6. Summary

- **GitHub:** Team `canvas-lms-mcp-collaborators` created under `websharpstudios`. Repository is under user `sweeden-ttu`; add collaborators via repo Settings. GitHub user search results and suggested logins are in section 2.1.
- **GitLab:** Group creation and user search require `GITLAB_TOKEN`; steps are documented in sections 1 and 2.2. **GITLAB_STRIP_TOKEN** is set; strip-secrets pipeline is active (section 5.6).
- **TTU/LDAP:** LDAP was not reachable from this environment. Only Akbar Siami Namin’s email (akbar.namin@ttu.edu) was confirmed via TTU CS faculty page; others need directory/LDAP or department confirmation.
- **Test script:** `run_repo_sync_test_plan.sh` was run; failures are due to SSH keys not being on GitHub/GitLab and missing `GITLAB_TOKEN`; see section 3 and docs/TEST_PLAN_REPO_SYNC.md for fixing.
- **Next steps:** Resolve emails (TTU directory/LDAP or course list); confirm GitHub/GitLab identities; create UNIX accounts; invite to both repos and add SSH keys so passwordless sync works; optionally use the team/group for access control.
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   