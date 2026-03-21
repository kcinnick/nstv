# Documentation Index

## 🚀 Quick Start (Choose Your Path)

### I'm New to NSTV
1. **First read**: `DEVELOPER_GUIDE.md` (20 min overview)
2. **Quick commands**: `QUICK_TASK_CHECKLIST.md` (copy-paste reference)
3. **Architecture**: `ARCHITECTURE.md` (deep dive)

### I Need to Deploy
1. **Setup guide**: `DEPLOYMENT.md`
2. **Plex config**: `PLEX_CONNECTION_FIXED.md`
3. **Downloads**: `NZBGET_SETUP.md`

### I'm Developing Features
1. **Architecture**: `ARCHITECTURE.md` (complete module reference)
2. **Developer guide**: `DEVELOPER_GUIDE.md` (patterns & workflows)
3. **Frontend**: `FRONTEND_GUIDELINES.md` (UI conventions)

## 📖 Complete Documentation Map

| Document | Purpose | Audience |
|----------|---------|----------|
| **DEVELOPER_GUIDE.md** ⭐ | Complete developer handbook | All developers |
| **QUICK_TASK_CHECKLIST.md** ⭐ | One-liners & quick reference | Everyone |
| **ARCHITECTURE.md** ⭐ | Deep technical reference | Developers |
| `README.md` | Project overview | Everyone |
| `DEPLOYMENT.md` | Production setup | DevOps |
| `FRONTEND_GUIDELINES.md` | UI conventions | Frontend devs |
| `MANUAL_TASKS.md` | Maintenance procedures | Admin |
| `POWERSHELL_COMMAND_REFERENCE.md` | Windows commands | Windows users |
| `NZBGET_SETUP.md` | Download integration | Setup |
| `PLEX_CONNECTION_FIXED.md` | Plex configuration | Setup |
| `RECOVER_CONNECTION.md` | Troubleshooting | Everyone |
| `HARD_DRIVE_QUICK_REFERENCE.md` | Storage layout | Admin |

**⭐ = Start here for new developers**

## 🤖 Claude AI Skills & Instructions

**File**: `../.claude_instructions` - AI-optimized project knowledge

This file contains:
- Project architecture summary
- Core workflows (download processing, Plex sync, duplicates)
- Environment configuration
- Database models
- Code patterns
- Common issues & solutions
- Performance considerations

**How it helps Claude**:
- Faster understanding of project structure
- Consistent code patterns
- Accurate troubleshooting
- Better feature implementation

## 📚 Development Resources

### For Understanding the Codebase
1. **Start**: `ARCHITECTURE.md` → High-Level Architecture section
2. **Deep dive**: Read through complete Module Reference
3. **Code patterns**: See Common Code Patterns section
4. **Debugging**: Reference Debugging Tips section

### For Common Tasks
Use `QUICK_TASK_CHECKLIST.md` to find:
- ⚡ One-liners (copy & paste)
- 📺 Download processing workflow
- 🔄 Syncing Plex to database
- 🧹 Finding duplicates
- 👨‍💻 Creating management commands

### For Production/Deployment
1. `DEVELOPER_GUIDE.md` → Environment Setup
2. `DEPLOYMENT.md` → Full deployment guide
3. `PLEX_CONNECTION_FIXED.md` → Plex integration
4. `NZBGET_SETUP.md` → Download automation

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

