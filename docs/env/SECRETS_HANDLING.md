# Secrets Handling

## Never Store Env Values in Repo

**Critical Rule**: Never commit environment variable values (secrets, tokens, passwords) to the repository.

## What to Do

1. **Use environment variable managers**:
   - Vercel Dashboard → Settings → Environment Variables
   - Local: `.env` file (gitignored)
   - CI/CD: Use your platform's secret management

2. **Template files only**:
   - `config/env.example` — contains keys only, no real values
   - Use placeholders like `CHANGE_ME` or `your-secret-here`

3. **Recovery**:
   - If env values are lost, see `docs/env/env_recovery_guide_v1.md`
   - Never store recovered values in the repo

## What NOT to Do

❌ Never commit `.env` files  
❌ Never store secrets in documentation  
❌ Never include real tokens in example files  
❌ Never commit `config/env.local` (gitignored for a reason)

## If You Find Secrets in the Repo

1. **Immediately rotate the secret** (generate new token/password)
2. **Remove from git history** (if possible) or mark as compromised
3. **Update `.gitignore`** to prevent future commits
4. **Document the incident** in `docs/security/incidents.md` (if exists)
