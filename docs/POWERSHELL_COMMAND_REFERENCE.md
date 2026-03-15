# Windows PowerShell Command Reference for Developers

## ⚠️ Important: Windows PowerShell vs Linux/Unix Commands

**THIS MACHINE RUNS WINDOWS WITH POWERSHELL 5.1**

This project runs on **Windows** with **PowerShell**. Many common developer commands are Unix/Linux-based and **will not work** in PowerShell.

**ALWAYS use PowerShell equivalents when working on this machine - Unix commands WILL FAIL!**

**Why?** PowerShell is a completely different shell with different commands, syntax, and redirection operators.

---

## Quick Reference: Common Commands

### File & Directory Operations

| Task | ❌ Unix/Bash | ✅ PowerShell |
|------|-----------|----------|
| List files | `ls -la` | `Get-ChildItem -Force` or `ls -Force` |
| List files long format | `ls -lh` | `Get-ChildItem \| Format-Table -AutoSize` |
| Show file size | `du -sh` | `(Get-ChildItem -Recurse \| Measure-Object -Sum Length).Sum / 1MB` |
| Change directory | `cd path` | `cd path` or `Set-Location path` |
| Print working directory | `pwd` | `pwd` (works in PowerShell) or `Get-Location` |
| Create directory | `mkdir name` | `mkdir name` or `New-Item -ItemType Directory -Name name` |
| Copy file | `cp src dest` | `Copy-Item src dest` |
| Copy directory | `cp -r src dest` | `Copy-Item -Recurse src dest` |
| Move file | `mv src dest` | `Move-Item src dest` |
| Remove file | `rm file` | `Remove-Item file` |
| Remove directory | `rm -rf dir` | `Remove-Item -Recurse -Force dir` |
| Touch/Create empty file | `touch file` | `New-Item -ItemType File file` |
| View file | `cat file` | `Get-Content file` or `cat file` (alias works) |
| View first N lines | `head -n 10 file` | `Get-Content file -Head 10` |
| View last N lines | `tail -n 10 file` | `Get-Content file -Tail 10` |
| Search in file | `grep "pattern" file` | `Select-String "pattern" file` |
| Find files | `find . -name "*.py"` | `Get-ChildItem -Recurse -Include "*.py"` |

### File Testing

| Task | ❌ Unix/Bash | ✅ PowerShell |
|------|-----------|----------|
| Check if file exists | `test -f file` or `[ -f file ]` | `Test-Path file` |
| Check if directory exists | `test -d dir` or `[ -d dir ]` | `Test-Path dir -PathType Container` |
| Check if readable | `test -r file` or `[ -r file ]` | `(Get-Item file).PSIsContainer -eq $false` |
| File exists (if statement) | `if [ -f file ]; then` | `if (Test-Path file) { }` |
| Directory exists (if statement) | `if [ -d dir ]; then` | `if (Test-Path dir) { }` |

### Text Processing

| Task | ❌ Unix/Bash | ✅ PowerShell |
|------|-----------|----------|
| Search text | `grep "text" file` | `Select-String "text" file` |
| Search with regex | `grep -E "regex" file` | `Select-String "regex" file` |
| Case insensitive | `grep -i "text" file` | `Select-String "text" file -CaseSensitive:$false` |
| Count occurrences | `grep -c "text" file` | `@(Select-String "text" file).Count` |
| Replace text | `sed 's/old/new/g' file` | `(Get-Content file) -replace 'old', 'new' \| Set-Content file` |
| Count lines | `wc -l file` | `@(Get-Content file).Count` or `(Get-Content file).Length` |
| Sort | `sort file` | `Get-Content file \| Sort-Object` |
| Unique lines | `sort \| uniq` | `Get-Content file \| Sort-Object -Unique` |

### Process Management

| Task | ❌ Unix/Bash | ✅ PowerShell |
|------|-----------|----------|
| List processes | `ps aux` | `Get-Process` |
| Find process | `ps aux \| grep name` | `Get-Process \| Where-Object {$_.Name -match "name"}` |
| Kill process | `kill -9 PID` | `Stop-Process -Id PID -Force` |
| Kill by name | `killall name` | `Stop-Process -Name name -Force` |
| Check if running | `pgrep name` | `Get-Process -Name name -ErrorAction SilentlyContinue` |

### Environment & Variables

| Task | ❌ Unix/Bash | ✅ PowerShell |
|------|-----------|----------|
| Set environment var | `export VAR=value` | `$env:VAR = "value"` |
| Get environment var | `echo $VAR` | `$env:VAR` |
| List all env vars | `env` | `Get-ChildItem Env:` or `dir env:` |
| Check if var set | `echo $VAR` | `if ($env:VAR) { }` |
| Append to PATH | `export PATH=$PATH:dir` | `$env:PATH += ";dir"` |

### Python/Virtual Environment

| Task | ❌ Bash | ✅ PowerShell |
|------|-------|----------|
| Activate venv | `source venv/bin/activate` | `.\venv\Scripts\Activate.ps1` |
| Run Python | `python script.py` | `python script.py` (same) |
| Run with module | `python -m module` | `python -m module` (same) |
| Check Python version | `python --version` | `python --version` (same) |
| List packages | `pip list` | `pip list` (same) |
| Install requirements | `pip install -r requirements.txt` | `pip install -r requirements.txt` (same) |

### Service Management

| Task | ❌ Bash | ✅ PowerShell |
|------|-------|----------|
| List services | `systemctl list-units --type service` | `Get-Service` |
| Start service | `sudo systemctl start name` | `Start-Service -Name name` (or `net start name`) |
| Stop service | `sudo systemctl stop name` | `Stop-Service -Name name` (or `net stop name`) |
| Check status | `systemctl status name` | `Get-Service -Name name` |
| Enable service | `sudo systemctl enable name` | `Set-Service -Name name -StartupType Automatic` |

### Network & Connectivity

| Task | ❌ Bash | ✅ PowerShell |
|------|-------|----------|
| Check port listening | `netstat -an \| grep 5432` | `netstat -an \| findstr ":5432"` or `Get-NetTCPConnection -LocalPort 5432` |
| Ping host | `ping host` | `Test-Connection host` |
| DNS lookup | `nslookup host` | `Resolve-DnsName host` |
| Check connectivity | `nc -zv host port` | `Test-NetConnection -ComputerName host -Port port` |

### Git Operations

| Task | ❌ Unix/Bash | ✅ PowerShell |
|------|-----------|----------|
| Clone repo | `git clone url` | `git clone url` (same) |
| Check status | `git status` | `git status` (same) |
| Add files | `git add .` | `git add .` (same) |
| Commit | `git commit -m "msg"` | `git commit -m "msg"` (same) |
| View log | `git log --oneline \| head` | `git log --oneline -n 10` (same) |
| Switch branch | `git checkout -b name` | `git checkout -b name` (same) |

### Piping & Redirection

| Task | ❌ Bash | ✅ PowerShell |
|------|-------|----------|
| Pipe output | `cmd1 \| cmd2` | `cmd1 \| cmd2` (same) |
| Redirect to file | `cmd > file` | `cmd > file` (same) |
| Append to file | `cmd >> file` | `cmd >> file` (same) |
| Redirect errors | `cmd 2>&1` | `cmd 2>&1` (same in PowerShell 7+) |
| Pipe to file | `cmd \| tee file` | `cmd \| Tee-Object -FilePath file` |

### Conditionals & Logic

| Task | ❌ Bash | ✅ PowerShell |
|------|-------|----------|
| If statement | `if [ -f file ]; then ... fi` | `if (Test-Path file) { ... }` |
| If-else | `if [ ]; then ... else ... fi` | `if (...) { ... } else { ... }` |
| And condition | `[ -f file ] && [ -d dir ]` | `(Test-Path file) -and (Test-Path dir)` |
| Or condition | `[ -f file ] \|\| [ -d dir ]` | `(Test-Path file) -or (Test-Path dir)` |
| Not condition | `! [ -f file ]` | `-not (Test-Path file)` |
| Case/switch | `case $var in` | `switch ($var) {` |

---

## PowerShell Specific Tips

### 1. Always Use Full Paths
```powershell
# ❌ Don't do this - may fail
Get-ChildItem c:\users\nick

# ✅ Do this - explicit and works
Get-ChildItem "C:\Users\Nick\PycharmProjects\nstv"
```

### 2. Use Quotes for Paths with Spaces
```powershell
# ❌ May fail
cd C:\Program Files\PostgreSQL

# ✅ Works reliably
cd "C:\Program Files\PostgreSQL"
```

### 3. PowerShell Objects vs Bash Text
```powershell
# ❌ Bash-style piping to grep won't work
Get-Process | grep python

# ✅ Use Where-Object instead
Get-Process | Where-Object {$_.Name -match "python"}

# ✅ Or use Select-String for text
dir | Select-String "pattern"
```

### 4. Use Backtick for Line Continuation
```powershell
# ❌ This will fail
Get-ChildItem -Path c:\dir `
  -Include "*.py"

# ✅ Backtick for line continuation
Get-ChildItem -Path "c:\dir" `
  -Include "*.py"
```

### 5. Variables Always Use $
```powershell
# ❌ Won't work
echo VAR

# ✅ Use $ prefix
echo $VAR
$var = "value"
Write-Host $var
```

### 6. Boolean Values
```powershell
# ❌ Wrong
$value = true  # This is a .NET boolean

# ✅ Better (but both work)
$value = $true
if ($value) { Write-Host "Yes" }
```

---

## Common Project Commands

### For This Project (nstv)

```powershell
# Navigate to project
cd C:\Users\Nick\PycharmProjects\nstv

# Activate Python virtual environment
.\venv\Scripts\Activate.ps1

# Run Django development server
python manage.py runserver

# Run migrations
python manage.py migrate

# Run tests
python -m pytest nstv/tests -q

# Check Django compatibility
python manage.py check

# Test database connection
python scripts/test_postgres_connection.py

# Create backup
python scripts/backup_database.py

# Verify upgrade
python scripts/verify_upgrade.py

# List running processes
Get-Process | Where-Object {$_.Name -match "python"}

# Kill Python process
Stop-Process -Name python -Force

# Check if port is in use
Get-NetTCPConnection -LocalPort 5432 -ErrorAction SilentlyContinue

# Start PostgreSQL service
net start postgresql-x64-14

# Stop PostgreSQL service
net stop postgresql-x64-14

# Check PostgreSQL service status
Get-Service -Name "postgresql-x64-14"
```

---

## SSH & Remote (if needed)

| Task | ❌ Bash | ✅ PowerShell |
|------|-------|----------|
| SSH connect | `ssh user@host` | `ssh user@host` (same) |
| Copy via SCP | `scp file user@host:path` | `pscp file user@host:path` (PuTTY) or `scp` (if installed) |
| SSH key gen | `ssh-keygen` | `ssh-keygen` (same if installed) |

---

## Batch/CMD vs PowerShell

If you see `.bat` or `.cmd` files, they're old Windows batch format:

| File Type | How to Run | Notes |
|-----------|-----------|-------|
| `.bat` or `.cmd` | Double-click OR `cmd /c file.bat` | Old batch language |
| `.ps1` | Right-click → "Run with PowerShell" OR `.\file.ps1` | PowerShell script |
| `.py` | `python file.py` | Python script |
| `.sh` | Won't work on Windows | Linux shell script |

---

## Creating Scripts for This Project

### Python Script Template
```python
#!/usr/bin/env python3
"""Description of script"""

if __name__ == '__main__':
    print("Hello from Python")
```

Run with:
```powershell
python scripts/my_script.py
```

### PowerShell Script Template
```powershell
# Description of script

Write-Host "Hello from PowerShell"
```

Run with:
```powershell
.\scripts\my_script.ps1
```

---

## Troubleshooting: Command Not Working?

1. **Check if it's a Bash command** - Try the PowerShell equivalent from the table above
2. **Use full path** - `C:\full\path\to\command` instead of just `command`
3. **Add quotes** - Especially for paths: `"C:\Path With Spaces\file.txt"`
4. **Check case sensitivity** - PowerShell is usually case-insensitive, but some commands aren't
5. **Use backticks for line breaks** - `command1 ` \` `command2` for multi-line commands
6. **Get help** - `Get-Help command-name` for PowerShell help
7. **Use -ErrorAction** - `command -ErrorAction SilentlyContinue` to suppress errors

---

## Resources

- **PowerShell Documentation**: https://learn.microsoft.com/en-us/powershell/
- **PowerShell Equivalents Chart**: https://learn.microsoft.com/en-us/powershell/scripting/samples/sample-scripts-for-administration
- **Windows Command Reference**: https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/windows-commands

---

## Summary: Key Rules for This Project

1. ✅ **Always use PowerShell**, not Command Prompt or Bash
2. ✅ **Quote file paths**, especially those with spaces
3. ✅ **Use `Get-` cmdlets** instead of Unix tools (Get-Process, Get-ChildItem, etc.)
4. ✅ **Use `$` prefix** for all variables
5. ✅ **Use `Test-Path`** instead of `test` or `[ ]`
6. ✅ **Use `Select-String`** instead of `grep`
7. ✅ **Use `Where-Object`** instead of piping to `grep`
8. ✅ **Check the table above** before running any command

**When in doubt, ask: "Is this a PowerShell equivalent?"**

---

**Last Updated**: March 15, 2026
**For Project**: nstv (C:\Users\Nick\PycharmProjects\nstv)
**OS**: Windows 11 (or Windows 10+)
**Shell**: PowerShell 5.1+ (or PowerShell 7+)

