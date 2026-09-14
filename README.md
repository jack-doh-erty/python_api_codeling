# REST API Design with Python

This is my project for completing Codeling's REST API Design with Python
course, with help from Codex.

[Open this course workspace in Codeling](https://app.codeling.dev/workspace/863f2d9f-8af5-489a-be84-840a7d031aaf).

## How to use this repo

To use this repo you need to create a copy of it in your own GitHub account and then clone it to your local computer.

Follow these steps:

1. Create your own copy of this repo:
   - Follow this link: [Create repo from template](https://github.com/new?template_name=course_rest_api_design_python_init&template_owner=codelingdotdev)
   - Or click _Use this template_ > _Create new repository_ button on this screen
2. Give the repository a name (eg: codeling-rest-api)
3. Click the _Create Repository_ button
4. Clone your repo onto your local computer
5. Start the course in the [Codeling workspace](https://app.codeling.dev/workspace/863f2d9f-8af5-489a-be84-840a7d031aaf)

Your course progress will sync to your Codeling account seamlessly.

## More info

Detailed instructions are provided in the [course](https://app.codeling.dev) and you're always welcome to [contact us](https://codeling.dev/contact/) if you have any questions.

## Seed data for pagination testing

After applying migrations, create 20 test users and 10,000 barks with:

```shell
cd src
uv run python manage.py seed_db
```

The command accepts `--users`, `--barks`, `--batch-size`, and `--password` options.
Seed usernames start at `seed_dog_001`; their default password is
`seed-password`. Existing seed users are reused, while each run adds the
requested number of new barks.
