# Bluesky Policy Labeler: Panic-Language Detection

## Project Overview

This project is a **policy labeler** designed to detect **likely panic-inducing** in public social media posts on [Bluesky](https://bsky.app/). It implements a simple yet powerful rule-based detection system to identify language patterns that may cause undue fear or anxiety in public discourse. The goal is to support **trust and safety efforts** by applying a content policy related to likely panic-language detection. This is in line with efforts to label or moderate harmful or manipulative posts across decentralized platforms.

---

## Policy Summary: `likely-panic-language`

The label **`likely-panic-language`** is applied to posts that contain **emotionally manipulative or panic-inducing** content based on the following criteria:

- Use of language such as:  
  ``"breaking news"`, `"immediate threat"`, `"danger to life"`, `"EMERGENCY!!!"` etc.
- Usage of **urgency-related terms** in alarming contexts (e.g., natural disasters, mass alerts, evacuation, civil threat).
- Posts that mimic **emergency alert tone**, **mass fear tactics**, or **disaster warnings**.

Posts that **do not match these criteria** are left **unlabeled**.

---

## Project Structure

| File / Folder                            | Description |
|-----------------------------------------|-------------|
| `policy_proposal_labeler.py`            | Main labeling class containing `moderate_post()` for applying the panic-language policy. |
| `create_csv.py`                         | Collects posts using the Bluesky API and saves them to a CSV file (`input-posts-panic.csv`). |
| `test_policy_labeler.py`                | Loads posts from CSV, applies the labeler, and prints + saves labeled output. |
| `test-data/input-posts-panic.csv`       | The raw post data collected based on panic-related keywords. |
| `output-csv/labeled_output.csv`         | Final labeled results saved as a CSV with each post and its detected label (if any). |
| `README.md`                             | This file – describes the purpose, setup, and usage. |

---

## How It Works

1. **Collect Data**  
   Run `search_and_generate_data.py` to scrape Bluesky posts for relevant panic-related keywords. This generates `test-data/input-posts-panic.csv`.

2. **Label Posts**  
   Run `test_policy_labeler.py` to apply the panic-language labeler. This creates a new CSV file:  
   ➜ `output-csv/labeled_output.csv`

3. **Labeling Logic**  
   Implemented in `policy_proposal_labeler.py`, the labeler uses a regex-based rule system to detect and label posts.

---

## Example Labels

| Post Example | Label |
|--------------|-------|
| `DANGEROUS CONDITION-IMMEDIATE THREAT at RT 390...` | `likely-panic-language` |
| `My baby is only one week old… She was born under bombing...` | `likely-panic-language` |
| `Below is the decision that the Trump administration has just petitioned...` | *(no label)* |

---

## Future Improvements

- Switch to a hybrid model combining regex and ML.
- Introduce support for **soft warning labels** like `potential-panic-language`.
- Add visualization/dashboard.

---

# Bluesky labeler starter code
You'll find the starter code for Assignment 3 in this repository. More detailed
instructions can be found in the assignment spec.

## The Python ATProto SDK
To build your labeler, you'll be using the AT Protocol SDK, which is documented [here](https://atproto.blue/en/latest/).

## Automated labeler
The bulk of your Part I implementation will be in `automated_labeler.py`. You are
welcome to modify this implementation as you wish. However, you **must**
preserve the signatures of the `__init__` and `moderate_post` functions,
otherwise the testing/grading script will not work. You may also use the
functions defined in `label.py`. You can import them like so:
```
from .label import post_from_url
```

For Part II, you will create a file called `policy_proposal_labeler.py` for your
implementation. You are welcome to create additional files as you see fit.

## Input files
For Part I, your labeler will have as input lists of T&S words/domains, news
domains, and a list of dog pictures. These inputs can be found in the
`labeler-inputs` directory. For testing, we have CSV files where the rows
consist of URLs paired with the expected labeler output. These can be found
under the `test-data` directory.

## Testing
We provide a testing harness in `test-labeler.py`. To test your labeler on the
input posts for dog pictures, you can run the following command and expect to
see the following output:

```
% python test_labeler.py labeler-inputs test-data/input-posts-dogs.csv
The labeler produced 20 correct labels assignments out of 20
Overall ratio of correct label assignments 1.0
```

