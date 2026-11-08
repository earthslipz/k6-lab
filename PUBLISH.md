# Uploading this lab to GitHub

This project is prepared for `https://github.com/earthslipz/k6-lab`.

1. Sign in to GitHub as **earthslipz**.
2. Open https://github.com/new.
3. Set repository name to `k6-lab`, visibility **Public**, and leave **Add a README** unchecked.
4. Create the empty repository.
5. In PowerShell, open the extracted `k6-lab` directory and run:

```powershell
git status
git remote -v
git remote add origin https://github.com/earthslipz/k6-lab.git
git push -u origin main
```

If a remote called `origin` already exists, run this instead of `git remote add`:

```powershell
git remote set-url origin https://github.com/earthslipz/k6-lab.git
git push -u origin main
```

After running the k6 experiments, update RESULTS.md using `python tools/build_results.py`, check the two notes that require reading HTML graphs, and commit the **real** new results:

```powershell
git add RESULTS.md reports
git commit -m "Record measured k6 performance results"
git push
```

To see the real history included with this ZIP:

```powershell
git log --oneline
```

Do not upload made-up HTML reports or label sample statistics as real measurements. The course requires output from actual runs on QuickPizza.
