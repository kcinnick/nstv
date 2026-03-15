# Documentation Index

## 🚀 Quick Start
1. **New users**: `../QUICK_START.md`
2. **Setup**: `DEPLOYMENT.md`
3. **Development**: `../instructions.md`

## 📖 Active Docs
| Document | Purpose |
|----------|---------|
| `README.md` (or `README_MINIFIED.md`) | Project overview |
| `DEPLOYMENT.md` | How to run/deploy |
| `FRONTEND_GUIDELINES.md` | Design system |
| `MANUAL_TASKS.md` (or `MANUAL_TASKS_MINIFIED.md`) | Maintenance tasks |
| `POWERSHELL_COMMAND_REFERENCE.md` | Windows PowerShell |
| `NZBGET_SETUP.md` | NZBGet config |

## 📦 Archived Docs (Local Only)
Located in `archive/` - not in version control:
- **postgresql-upgrade/**: Upgrade guides, procedures, logs
- **investigations/**: Environment & code audits, issue investigations
- **bugfixes/**: Bug documentation, historical fixes
- **automation/**: Automation research & runbooks
- **historical/**: Completed plans, security logs, checklists

## 🔍 Find What You Need
| Question | Answer |
|----------|--------|
| How do I start? | `../QUICK_START.md` |
| How do I deploy? | `DEPLOYMENT.md` |
| I need PowerShell help | `POWERSHELL_COMMAND_REFERENCE.md` |
| What are my tasks? | `MANUAL_TASKS.md` |
| Design guidelines? | `FRONTEND_GUIDELINES.md` |
| Old procedures? | `archive/` |

## 📝 Key Notes
- **PowerShell Only**: Always use PowerShell, never Unix/Bash commands
- **Minified Versions**: `README_MINIFIED.md`, `MANUAL_TASKS_MINIFIED.md` (same content, condensed)
- **Archive**: All reference docs stay locally, not in version control
- **Secrets**: Never commit `.env`, use `DJANGO_DB_PASSWORD` from environment


## 📝 Documentation Principles

✅ **Keep it current** - Update docs when procedures change  
✅ **Keep it real** - Document what actually happens, not what should happen  
✅ **Keep it local** - Archived docs don't clutter version control  
✅ **Keep it searchable** - Use clear headings and sections  

---

## 🔐 Important Security Notes

- **`.env` file**: Never commit! Use `.env.example` instead
- **Passwords**: Always use placeholders `[PASSWORD]` in examples
- **Secrets**: Keep in `.env`, never in documentation

See `archive/historical/SECURITY_UPDATE_PASSWORD_REMOVAL.md` for more details.

---

## 💡 Need Something?

1. **Can't find it?** → Search `POWERSHELL_COMMAND_REFERENCE.md`
2. **Need old docs?** → Check `archive/` folders
3. **Have a new procedure?** → Update `MANUAL_TASKS.md` or `DEPLOYMENT.md`
4. **Found outdated info?** → Update the relevant doc and commit

---

**Last Updated**: March 15, 2026  
**Structure**: Clean repo (active docs) + Local archive (reference docs)  
**Status**: 🟢 Organized and efficient

