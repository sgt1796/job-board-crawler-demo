# Job Spy & Auto Apply Assistant

This project is a **proof‑of‑concept** implementation of the job monitoring and semi‑automatic application pipeline described in earlier design discussions.  The goal is to provide a reproducible reference implementation that is easy to audit, extend and adapt to different job sources or applicant profiles.  It is not intended to be a drop‑in solution for production use; instead it shows how one can structure a complex workflow around crawlers, lightweight agents, an FSM (finite state machine), and storage.

## Features

* **Crawler layer** – pluggable crawlers fetch raw job posts from various sources.  A simple in‑memory dummy crawler is provided for demonstration.
* **Agent layer** – small, single‑responsibility classes normalise jobs, evaluate their fit against a candidate profile, plan an application and prepare materials.  These agents show how to use the [`PromptFunction`](../POP/POP.py) class from the [POP](https://github.com/sgt1796/POP) library and the `Embedder` class for semantic similarity calculations.  In this demo the embedder is instantiated but not used to avoid network calls.
* **Finite state machine** – the core pipeline is driven by a finite state machine which ensures that each job proceeds through the same sequence of states (normalise → evaluate → plan → generate materials → submit) and can be safely resumed after interruption.
* **SQLite storage** – a simple SQLite database records the current state of each job, decisions and results.  The schema lives in `data/schema.sql` and is initialised automatically when the pipeline first runs.
* **Profiles and materials** – a candidate profile (`profiles/candidate_profile.json`) describes target titles and skills, a core résumé (`profiles/resume_core.md`) represents fixed content, and a directory of résumé modules (`profiles/resume_modules/`) contains optional highlights.  The agents read these files to tailor applications.
* **Tests** – unit tests built with `unittest` exercise the evaluator logic and state machine transitions.  They do not depend on network access and are safe to run in isolated environments.

## Quick Start

To run the demonstration pipeline you need Python 3.11+.  No external packages are required beyond the standard library.  The pipeline uses the POP library’s `PromptFunction` and `Embedder` classes but avoids calling any remote LLM or embedding service.

1. **Clone or download** this repository alongside the [`POP` library](https://github.com/sgt1796/POP) so that Python can import `POP`.  In this challenge environment the `POP` code is already available.

2. From the project root run the test suite:

```bash
python -m unittest discover -s job_spy/tests
```

3. To execute the pipeline on sample data, run:

```bash
python job_spy/scheduler/run_pipeline.py
```

You should see the pipeline fetch a dummy job, normalise it, evaluate fit, plan the application and generate a cover letter.  Since this is a demonstration the final submission step only logs output to the console.

## Directory Structure

```
job_spy/
├── README.md               # this file
├── agents/                 # LLM/logic agents
│   ├── __init__.py
│   ├── job_normalizer.py   # normalise raw jobs into structured objects
│   ├── job_evaluator.py    # compute match scores and decisions
│   ├── application_planner.py # plan how to apply
│   ├── resume_modifier.py  # tweak résumé modules
│   └── cover_letter_writer.py # generate a simple cover letter
├── apply/                  # submission helpers
│   ├── __init__.py
│   ├── form_filler.py
│   ├── upload.py
│   ├── screenshot.py
│   └── confirm.py
├── crawlers/               # job fetchers
│   ├── __init__.py
│   ├── base.py
│   └── dummy_crawler.py
├── pipeline/               # finite state machine and execution
│   ├── __init__.py
│   ├── states.py
│   ├── fsm.py
│   └── runner.py
├── scheduler/              # entry points for cron/APS
│   ├── __init__.py
│   ├── crawl_jobs.py
│   ├── run_pipeline.py
│   └── notify.py
├── data/
│   ├── schema.sql          # database schema
│   └── jobs.db             # created on first run
├── profiles/
│   ├── candidate_profile.json
│   ├── resume_core.md
│   └── resume_modules/
│       └── research_highlight.md
├── config/
│   ├── crawl.yaml
│   ├── limits.yaml
│   └── secrets.env.example
└── tests/
    ├── __init__.py
    ├── test_evaluator.py
    └── test_fsm.py
```

## Extending This Project

* **Add real crawlers** – create a new class inheriting from `BaseCrawler` in `crawlers/` that scrapes a real job board.  Return a list of dictionaries with at least `title`, `company`, `location`, `description` and `source_url` fields.
* **Integrate an embedder** – the `agents/job_evaluator.py` file instantiates the `Embedder` class from POP.  To use it in practice you must supply an API key (e.g., OpenAI or Jina AI) via environment variables or a local model name.  See the POP documentation for details.
* **Use a real LLM** – to generate better cover letters you can create a `PromptFunction` with an appropriate system prompt and call its `execute` method.  This demonstration simply concatenates text, but the hook is there for future upgrades.

Please consult the inline docstrings in each file for further details.

## Using the JobSpy crawler

An optional crawler backed by the [`jobspy`](https://pypi.org/project/jobspy/) library lives in `crawlers/jobspy_crawler.py`.  Install `jobspy` (and its dependencies) and instantiate the crawler with your search parameters and optional rotating proxies:

```python
from job_spy.crawlers.jobspy_crawler import JobSpyCrawler
from job_spy.pipeline.runner import load_profile, load_resume_inventory
from job_spy.pipeline.fsm import JobStateMachine

profile = load_profile("profiles/candidate_profile.json")
inventory = load_resume_inventory("profiles/resume_core.md", "profiles/resume_modules")

crawler = JobSpyCrawler(
    search_term="UI UX -PhD -Master -Head",
    location="MA, USA",
    platforms=["indeed", "linkedin"],
    hours_old=144,
    results_wanted=50,
    proxies=["username:password@gw.dataimpulse.com:823"],  # optional
)

fsm = JobStateMachine(profile, inventory)
fsm.add_jobs(crawler.fetch())
fsm.run()
fsm.close()
```

If `jobspy` is not installed the crawler raises a clear `ImportError` and the rest of the pipeline can still be used with the bundled dummy crawler.
