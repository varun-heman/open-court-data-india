# Contributing

Thank you for your interest in contributing to the Open Court Data India project! This guide will help you get started with contributing to the project.

## Getting Started

1. **Fork the repository**: Click the "Fork" button at the top right of the [GitHub repository](https://github.com/varun-heman/open-court-data-india).

2. **Clone your fork**: Clone your fork to your local machine.

```bash
git clone https://github.com/your-username/open-court-data-india.git
cd open-court-data-india
```

3. **Set up the development environment**: Follow the [installation guide](../getting-started/installation.md) to set up your development environment.

4. **Create a branch**: Create a branch for your changes.

```bash
git checkout -b feature/your-feature-name
```

## Development Workflow

1. **Make your changes**: Make your changes to the codebase.

2. **Test your changes**: Make sure your changes work as expected.

3. **Update documentation**: Update the documentation if necessary.

4. **Commit your changes**: Commit your changes with a descriptive commit message.

```bash
git add .
git commit -m "Add feature: your feature description"
```

5. **Push your changes**: Push your changes to your fork.

```bash
git push origin feature/your-feature-name
```

6. **Create a pull request**: Create a pull request from your fork to the main repository.

## Code Style

Please follow the [code style guide](code-style.md) when making changes to the codebase.

## Adding a New Court Scraper

To add a new court scraper:

1. **Create a new directory**: Create a new directory for the court under the `scrapers` directory.

```
scrapers/
└── new_court/
    ├── __init__.py
    └── base_scraper.py
```

2. **Create a base scraper**: Create a base scraper for the court that inherits from the `BaseScraper` class.

```python
from scrapers.base_scraper import BaseScraper

class NewCourtScraper(BaseScraper):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.court_name = "New Court"
        self.court_code = "new_court"
        self.court_dir = f"data/{self.court_code}/"
        self.base_url = "https://newcourt.gov.in"
```

3. **Create specialized scrapers**: Create specialized scrapers for different types of documents (cause lists, judgments, etc.).

```
scrapers/
└── new_court/
    ├── __init__.py
    ├── base_scraper.py
    └── cause_lists/
        ├── __init__.py
        └── cause_list_scraper.py
```

4. **Implement the scraper**: Implement the scraper following the project's architecture and best practices.

5. **Add tests**: Add tests for the new scraper.

6. **Update documentation**: Update the documentation to include the new scraper.

## Adding a New Feature

To add a new feature:

1. **Discuss the feature**: Open an issue to discuss the feature before implementing it.

2. **Implement the feature**: Implement the feature following the project's architecture and best practices.

3. **Add tests**: Add tests for the new feature.

4. **Update documentation**: Update the documentation to include the new feature.

## Reporting Bugs

If you find a bug, please report it by opening an issue on the [GitHub repository](https://github.com/varun-heman/open-court-data-india/issues).

Please include:

- A clear and descriptive title
- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- Any error messages or logs
- Your environment (OS, Python version, etc.)

## Feature Requests

If you have an idea for a new feature, please open an issue on the [GitHub repository](https://github.com/varun-heman/open-court-data-india/issues).

Please include:

- A clear and descriptive title
- A detailed description of the feature
- Why the feature would be useful
- Any relevant examples or mockups

## Code of Conduct

Please follow the [code of conduct](code-of-conduct.md) when contributing to the project.

## License

By contributing to the Open Court Data India project, you agree that your contributions will be licensed under the [MIT License](../about/license.md).
