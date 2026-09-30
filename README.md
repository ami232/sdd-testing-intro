# Premium Check: Testing Warm-Up (solutions)

> You are on the `solution` branch. Run `git switch main` for the version
> with the exercises left blank.

A 20-minute in-class warm-up on testing code that talks to the outside world.

`premium_check/users.py` decides whether a user is on a premium plan. To do
that it calls an HTTP API and reads an environment variable, so none of it can
be tested by just calling the function and hoping.

The test file gives you four **worked examples** to read first, then three
exercises to fill in.

## What you practice

| Tool | What it is for |
| --- | --- |
| `mocker` (pytest-mock) | Replace a collaborator for the duration of one test |
| `monkeypatch` | Change environment variables and attributes, undone automatically |
| `parametrize` | Run the same test body over a table of cases |
| Fixtures | Share setup between tests without repeating it |

The key idea in all four: a test that reaches the real network is slow,
flaky, and fails on a train. Replace the edges, keep the logic.

## Project layout

```dir_tree
root_dir
├─ premium_check/
│  ├─ __init__.py
│  └─ users.py
├─ tests/
│  └─ test_users.py
└─ README.md
```

## Get the code

This is a warm-up, so there is nothing to submit and no reason to fork.
Clone `ami232/sdd-testing-intro` directly:

```bash
git clone https://github.com/ami232/sdd-testing-intro.git
cd sdd-testing-intro
git switch solution
```

## Setup

Preferred: [uv](https://docs.astral.sh/uv/). Install uv once per machine (see
uv's docs), then from inside your local clone:

```bash
uv venv                              # create a local virtual environment (.venv)
uv pip install -r requirements.txt   # install pytest and pytest-mock into it
```

From then on, run any Python command through `uv run` so it uses that
environment automatically:

```bash
uv run pytest -v                          # run everything, one test per line
uv run pytest -k premium -v               # only tests matching "premium"
```

<details>
<summary>Alternative: plain venv + pip</summary>

```bash
# Unix
python -m venv .venv && source .venv/bin/activate

# Windows:
python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt

python -m pytest -v
```

</details>

## Exercises

Open `tests/test_users.py`. Read the four worked examples above the
`Exercises` divider and run them, then work through the three `TODO` blocks
below it.

### 1. monkeypatch

Write a test for `get_api_key` that sets `API_KEY` in the environment and
asserts that the value comes back. The worked example `test_env_default_key`
covers the opposite case, where the variable is absent.

Ask yourself why `monkeypatch` is the right tool rather than
`os.environ["API_KEY"] = ...`. Run the whole file afterwards and check that
`test_env_default_key` still passes.

### 2. parametrize

Fill in the case table for `is_premium_user`. Cover four scenarios: active
premium, expired premium, an active basic plan, and no subscription.

One of these is a trap. A real API can return `"plan": null`, and
`dict.get("plan", "")` does **not** protect you from that: the default only
applies when the key is missing, not when it is present and null. Look at
`users.py` to see how that case is handled, then write a case that would have
caught it.

### 3. Patching a failure

Test that `is_premium_user` returns `False` rather than crashing when the API
gives nothing back. Patch `get_user_data` to simulate the outage.

Mind the patch target: it is `premium_check.users.get_user_data`, the name as
`is_premium_user` looks it up, not the module where it happens to be defined.
Patch the wrong one and your test will pass while testing nothing.

## Going back

```bash
git switch main
```
