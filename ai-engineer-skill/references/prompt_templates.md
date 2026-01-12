# Prompt Templates

## Template Library

### Code Generation

**Basic Code:**
```python
template = "Write {language} code that {description}"
```

**With Constraints:**
```python
template = """
Write {language} code that {description}.

Requirements:
- Use {framework}
- Handle errors appropriately
- Include type hints
- Add documentation
"""
```

**Code Explanation:**
```python
template = """
Explain the following {language} code:

```
{code}
```

Focus on:
- Functionality
- Best practices
- Potential improvements
"""
```

### Text Generation

**Summarization:**
```python
template = """
Summarize the following text in {max_sentences} sentences:

{text}
"""
```

**Translation:**
```python
template = """
Translate the following text from {source_lang} to {target_lang}:

{text}
"""
```

**Rewriting:**
```python
template = """
Rewrite the following text in {tone} tone:

{text}
"""
```

### Question Answering

**RAG QA:**
```python
template = """
Based on the following context:

{context}

Answer the question: {question}

If the answer is not in the context, say "I don't know".
"""
```

**Multi-step QA:**
```python
template = """
Step 1: {question1}
Step 2: Based on your answer, {question2}
Step 3: Finally, {question3}
"""
```

### Data Processing

**Extraction:**
```python
template = """
Extract the following information from the text:

Text: {text}

Extract:
- Names: {names}
- Dates: {dates}
- Locations: {locations}

Format as JSON.
"""
```

**Classification:**
```python
template = """
Classify the following text into one of these categories:

Categories: {categories}

Text: {text}

Category:
"""
```

### Analysis

**Sentiment Analysis:**
```python
template = """
Analyze the sentiment of the following text:

{text}

Provide:
- Overall sentiment (positive/negative/neutral)
- Confidence score (0-1)
- Key phrases influencing sentiment
"""
```

**Topic Modeling:**
```python
template = """
Identify the main topics in the following text:

{text}

List topics with brief descriptions.
"""
```

## Prompt Engineering Techniques

### Chain-of-Thought
```python
template = """
{question}

Think step by step:
1.
2.
3.
4.

Final answer:
"""
```

### Few-Shot Learning
```python
template = """
Examples:
Input: "I love this!"
Output: positive

Input: "This is terrible"
Output: negative

Input: "It's okay"
Output: neutral

Input: {input_text}
Output:
"""
```

### Self-Consistency
```python
template = """
Solve this problem: {problem}

Provide your reasoning and final answer.
"""
# Generate multiple responses, take majority vote
```

### Tree-of-Thoughts
```python
template = """
Problem: {problem}

Branch 1: {approach1}
Branch 2: {approach2}
Branch 3: {approach3}

Evaluate each branch and select the best solution.
"""
```

## System Prompts

### Persona Definition
```python
system_prompt = """
You are an expert {domain} with {years} years of experience.
Your responses should be {tone} and include {level} of detail.
Always cite sources when applicable.
"""
```

### Task Specification
```python
system_prompt = """
Your task is to {task_description}.

Constraints:
- {constraint1}
- {constraint2}
- {constraint3}

Output format: {format_specification}
"""
```

## Prompt Optimization

### A/B Testing
```python
from prompt_engineer import PromptOptimizer

optimizer = PromptOptimizer()

template_a = "Summarize: {text}"
template_b = "Provide a concise summary of: {text}"

results = optimizer.compare_templates(
    [template_a, template_b],
    test_data=evaluation_set
)
```

### Iterative Improvement
```python
def improve_prompt(current_prompt, feedback):
    improved = llm.generate(f"""
    Improve this prompt based on feedback:

    Current prompt:
    {current_prompt}

    Feedback:
    {feedback}

    Improved prompt:
    """)

    return improved
```

## Best Practices

1. **Be specific**: Clearly define what you want
2. **Use examples**: Show desired input/output pairs
3. **Specify format**: Define output structure explicitly
4. **Add constraints**: Limit response length or format
5. **Test thoroughly**: Validate on diverse inputs
6. **Version control**: Track prompt changes over time
7. **Monitor performance**: Track quality metrics

## Common Pitfalls

1. **Ambiguous instructions**: Leads to inconsistent outputs
2. **Too complex**: Models may miss requirements
3. **Missing context**: Insufficient information for task
4. **No examples**: Models may misunderstand intent
5. **Poor formatting**: Hard to parse structured outputs
