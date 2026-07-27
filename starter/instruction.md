# GitHub Copilot Instructions

## Project Goal
Improve and maintain the Sudoku application while preserving all existing functionality.

## Coding Guidelines
- Keep the existing project structure.
- Write clean, modular, and readable code.
- Follow Python and JavaScript best practices.
- Do not remove existing features.
- Add comments where necessary.
- Ensure all existing tests continue to pass.

## UI Guidelines
- Maintain a responsive layout.
- Preserve dark mode functionality.
- Keep the interface accessible.
- Alternate colors for each 3×3 Sudoku block.
- Highlight invalid moves immediately after user input.

## How GitHub Copilot Was Used
GitHub Copilot was used to assist with:
- Implementing immediate invalid move highlighting.
- Improving the leaderboard and local storage functionality.
- Enhancing the difficulty selector and hint features.
- Suggesting UI improvements while preserving existing behavior.
- Generating boilerplate code and refactoring repetitive logic.

## Copilot Suggestion Review
One Copilot suggestion was modified before being accepted.

Copilot initially suggested validating Sudoku conflicts only after the user clicked **Check Puzzle**. This approach did not satisfy the project requirement for immediate visual feedback.

The implementation was revised so conflicts are detected and highlighted immediately whenever the user enters a value. This change improves the user experience while satisfying the project rubric.

## Testing
- Ran the complete test suite using `pytest`.
- All 17 tests passed successfully.
- Existing functionality was verified after each modification.