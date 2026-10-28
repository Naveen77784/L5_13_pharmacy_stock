# Lab 5 Reflection

### 1. What did you learn about static code analysis?

I learned that static analysis tools can find problems by examining code without running it. Pylint helped identify code-quality concerns, Flake8 found style and formatting issues, and Bandit flagged a risky SQL query.

### 2. Which issue was most important, and why?

The SQL query was the most important issue to me because inserting user input directly into a query can create a SQL injection risk. I changed it to use a parameterized query, so the patient name is treated as data.

### 3. What was challenging about fixing the issues?

It was challenging to understand what each warning meant and how to fix it without changing the program’s behavior. For example, I had to replace broad exception handling with more specific handling and check the reports again after editing.

### 4. How will static analysis help you in future projects?

I can run these tools while developing, not just at the end of a project. Finding security, quality, and formatting problems early should make code easier to maintain and safer to use.