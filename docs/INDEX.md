# 📚 Documentation Index

Welcome! This folder contains all active project documentation. **Archived reference docs** are in `archive/` (local only, not in version control).

---

## 🚀 Quick Start

**New to the project?** Start here:
1. Read [`../QUICK_START.md`](../QUICK_START.md) - 5 min overview
2. Check [`../instructions.md`](../instructions.md) - Setup instructions
3. Review [`DEPLOYMENT.md`](./DEPLOYMENT.md) - How to run the project

---

## 📖 Active Documentation

### Essential Reading
- **[README.md](./README.md)** - Project overview and key information
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - How to deploy the application
- **[DEVELOPMENT.md](./DEVELOPMENT.md)** - Development guidelines and standards

### Reference Guides
- **[MANUAL_TASKS.md](./MANUAL_TASKS.md)** - Recurring maintenance tasks and procedures
- **[POWERSHELL_COMMAND_REFERENCE.md](./POWERSHELL_COMMAND_REFERENCE.md)** - PowerShell commands (this is a Windows machine!)
- **[NZBGET_SETUP.md](./NZBGET_SETUP.md)** - NZBGet configuration and setup

---

## 📦 Archived Documentation

These are **local reference documents** kept for historical purposes. They are **not in version control** to keep the repository clean.

### PostgreSQL Upgrade
Located in `archive/postgresql-upgrade/`
- Upgrade procedures and guides (one-time use ✓)
- Quick reference cards
- Completed upgrade logs

**Use when:** Planning future database upgrades

### Investigations & Research
Located in `archive/investigations/`
- Environment investigation snapshots
- Code audit results
- Issue investigation documents

**Use when:** Researching similar problems

### Bug Fixes & Historical
Located in `archive/bugfixes/`
- Bug reports and fix documentation
- Old issue tracking

**Use when:** Understanding historical bugs

### Automation Research
Located in `archive/automation/`
- Automation investigation notes
- Runbooks for specific procedures
- Automation research documents

**Use when:** Planning automation improvements

### Historical Records
Located in `archive/historical/`
- Completed cleanup plans
- Security update logs
- Upgrade checklists
- Documentation strategy notes

**Use when:** Need historical context

---

## 🔍 Finding What You Need

### For New Developers
1. Start with `../QUICK_START.md`
2. Read `DEPLOYMENT.md`
3. Check `FRONTEND_GUIDELINES.md` before writing code

### For Maintenance Tasks
- See `MANUAL_TASKS.md` for recurring procedures
- Use `POWERSHELL_COMMAND_REFERENCE.md` for command syntax (Windows!)

### For Troubleshooting
- Check `MANUAL_TASKS.md` troubleshooting section first
- Review archived investigations in `archive/investigations/`

### For NZBGet Issues
- Start with `NZBGET_SETUP.md`
- Check automation research in `archive/automation/`

### For PostgreSQL Issues
- Check `archive/postgresql-upgrade/` for reference
- See upgrade procedures for maintenance

---

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

