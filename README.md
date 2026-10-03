# NEXUS for Octopus Energy Flexibility

An independent data engineering portfolio presentation by Firman Insan Muhammad (VIM), prepared for Octopus Energy's Senior Data Engineer role on the Flexibility team.

Live site: https://rfim.github.io/nexus-octopus-flexibility/

The Lifepal results on the site are career outcomes reported in VIM's CV. The energy flexibility architecture and formulas are proposed designs for the role, not claims about Octopus production systems. The Python/Delta Lake code is a separate, runnable portfolio reference with synthetic events.

Run the reference with Python 3.12:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r examples/requirements.txt
.venv/bin/python -m unittest discover -s examples -p 'test_*.py' -v
```

The architecture uses locally vendored technology SVGs from [Devicon](https://github.com/devicons/devicon), [Simple Icons](https://github.com/simple-icons/simple-icons), and the [official Delta Lake website](https://github.com/delta-io/website). Their license texts and Delta Lake notice are included in `assets/stack/`. Brand marks identify technologies; they do not imply endorsement.

The Octopus Energy logo was supplied by the portfolio owner. This site is not affiliated with or endorsed by Octopus Energy.
