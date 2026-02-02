# How to set the GraphQL token for GitLab

From [docs.gitlab.com/api/oauth2/](https://docs.gitlab.com/api/oauth2/) and [docs.gitlab.com/api/graphql/](https://docs.gitlab.com/api/graphql/).

## 1. Obtain a token

GitLab GraphQL accepts the same tokens as the REST API. You can use:

- **OAuth 2.0 access token** (from the OAuth2 API)
- **Personal access token** (User → Settings → Access Tokens)
- **Project access token** (Project → Settings → Access Tokens)
- **Group access token** (Group → Settings → Access Tokens)

### OAuth 2.0 (docs.gitlab.com/api/oauth2/)

1. **Register an application** (if using OAuth2): User → **Settings → Applications** (`/user_settings/applications`). Create an application, set redirect URI and scopes. You get **Application ID** and **Client Secret**.

2. **Get an access token** using one of the supported flows:
   - **Authorization code (with PKCE)** – recommended for clients that cannot keep a secret.
   - **Authorization code** – for server-side apps (uses `client_id` + `client_secret`).
   - **Device authorization grant** (GitLab 17.1+) – for headless/CLI (user authorizes in browser on another device).
   - **Resource owner password** – only for trusted first-party services; GitLab recommends Personal Access Tokens instead.

3. **Token endpoint:** `POST https://gitlab.com/oauth/token` (or `https://gitlab.example.com/oauth/token` for self-managed).

   Example response:
   ```json
   {"access_token":"...", "token_type":"bearer", "expires_in":7200, "refresh_token":"...", "created_at":...}
   ```

   Use the **access_token** value as the GraphQL token.

### Personal / project / group access token

Create a token in the GitLab UI with the right scopes. For GraphQL:

- **read_api** – read-only (queries).
- **api** – read and write (queries and mutations).

Use that token as the GraphQL token (same as below).

## 2. Set the token for GraphQL

GraphQL endpoint: **`https://gitlab.com/api/graphql`** (or `https://<your-gitlab>/api/graphql`).

You can set the token in either of these ways:

### Header (recommended)

```bash
curl --request POST \
  --url "https://gitlab.com/api/graphql" \
  --header "Authorization: Bearer <YOUR_TOKEN>" \
  --header "Content-Type: application/json" \
  --data '{"query": "query { currentUser { name } }"}'
```

Replace `<YOUR_TOKEN>` with your OAuth2 access token, personal access token, or project/group access token.

### Query parameter

**OAuth2 token:**
```bash
curl --request POST \
  --url "https://gitlab.com/api/graphql?access_token=<OAUTH_TOKEN>" \
  --header "Content-Type: application/json" \
  --data '{"query": "query { currentUser { name } }"}'
```

**Personal / project / group access token:**
```bash
curl --request POST \
  --url "https://gitlab.com/api/graphql?private_token=<ACCESS_TOKEN>" \
  --header "Content-Type: application/json" \
  --data '{"query": "query { currentUser { name } }"}'
```

## 3. Token scopes for GraphQL

| Scope     | Use              |
|----------|-------------------|
| read_api | Queries only      |
| api      | Queries + mutations |

## 4. Summary

- **Get token:** OAuth2 flow (docs.gitlab.com/api/oauth2/) or create a Personal/Project/Group access token in GitLab.
- **Set for GraphQL:** Use `Authorization: Bearer <token>` header, or `access_token=<token>` (OAuth2) or `private_token=<token>` (PAT/project/group) on the GraphQL URL.
