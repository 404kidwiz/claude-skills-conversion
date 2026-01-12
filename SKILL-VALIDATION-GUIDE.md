---
name: skill-validation-guide
description: Validation and testing guide for Agent Skills to ensure quality, functionality, and compliance with best practices. Use when creating, reviewing, or validating skills to verify they meet standards and work correctly.
---

# Skill Validation and Testing Guide

This guide provides comprehensive validation criteria and testing procedures for Agent Skills to ensure quality, functionality, and compliance with Anthropic best practices.

## Validation Checklist

### Frontmatter Validation

**Required Fields:**
- [ ] `name` is present and follows naming conventions:
  - Lowercase letters, numbers, and hyphens only
  - 3-64 characters maximum
  - No spaces, underscores, or special characters
  - Matches directory name
- [ ] `description` is present and effective:
  - Third-person perspective
  - Clearly states what the skill does
  - Includes when to use the skill
  - Contains trigger keywords for auto-discovery
  - 10-1024 characters in length

**Optional Fields Validation:**
- [ ] `allowed-tools` is scoped to minimum necessary tools only
- [ ] `license` points to actual LICENSE.txt file if used
- [ ] `model` specifies appropriate model for skill requirements
- [ ] `user-invocable` is set correctly (true/false) based on intended use
- [ ] `disable-model-invocation` is used appropriately

### Content Validation

**Structure:**
- [ ] SKILL.md starts immediately after frontmatter (no blank lines)
- [ ] Markdown is well-formatted with proper headers
- [ ] Line count is under 500 lines (optimal for performance)
- [ ] Content is concise and focused on AI guidance, not human documentation

**Content Quality:**
- [ ] Instructions are clear, actionable, and specific
- [ ] Skill has a clear purpose and philosophy
- [ ] Capabilities are well-defined and scoped
- [ ] Behavioral traits are described
- [ ] When-to-use criteria are specific
- [ ] Example interactions are provided
- [ ] References to supporting files use forward slashes

**Progressive Disclosure:**
- [ ] Main SKILL.md provides essential guidance only
- [ ] Detailed reference materials are in separate files
- [ ] Supporting files are linked with `[filename](path)`
- [ ] Scripts directory contains executable code (not documentation)
- [ ] Reference files contain detailed information loaded as needed

### Functionality Validation

**Testing Steps:**

1. **Basic Loading Test:**
   ```bash
   # Test that skill is discovered
   claude
   # Ask: "What skills are available?"
   # Verify your skill appears in the list
   ```

2. **Trigger Test:**
   - Describe a task matching your skill's description
   - Verify Claude offers to use the skill
   - Accept the offer and confirm it loads correctly

3. **Execution Test:**
   - Provide a real task the skill should handle
   - Verify skill follows its instructions correctly
   - Check that output matches expected behavior

4. **Reference Loading Test** (if applicable):
   - Trigger a scenario that requires reference files
   - Verify skill loads references as needed
   - Confirm references are accessible and complete

5. **Multi-File Test** (if applicable):
   - Test with scenarios requiring multiple files
   - Verify skill references files correctly
   - Check that all links work

6. **Error Handling Test:**
   - Test with invalid inputs or edge cases
   - Verify skill provides helpful error messages
   - Confirm skill doesn't break unexpectedly

7. **Tool Restrictions Test** (if using `allowed-tools`):
   - Attempt to use tools outside allowed set
   - Verify tool is blocked or permission is requested
   - Confirm allowed tools work without prompts

### Best Practices Compliance

**Content Guidelines:**
- [ ] No auxiliary documentation files (README.md, INSTALLATION_GUIDE.md, etc.)
- [ ] Skill focuses on AI guidance, not human-to-human documentation
- [ ] Description avoids vague terms ("helper", "utilities", "tools")
- [ ] Skill name is descriptive (not generic like "helper", "utils")
- [ ] No reserved words in name (e.g., "anthropic-helper")

**Progressive Disclosure:**
- [ ] SKILL.md is concise (< 500 lines, < 5,000 words recommended)
- [ ] Reference materials are organized by domain or topic
- [ ] Scripts are executable and tested independently
- [ ] No circular references in reference files

**Tool Usage:**
- [ ] `allowed-tools` is minimized to essential tools only
- [ ] Wildcard patterns are scoped appropriately (e.g., `Bash(git:*)`)
- [ ] Tool descriptions are clear and specific
- [ ] Scripts use `{baseDir}` for skill directory references

## Testing Scenarios

### Scenario 1: Auto-Discovery
**Purpose:** Verify skill triggers automatically on relevant queries.

**Steps:**
1. Ask Claude a question that matches your skill's description
2. Wait for Claude to offer the skill
3. Accept the offer
4. Verify skill loads and provides correct guidance

**Success Criteria:**
- Claude offers the skill without manual invocation
- Skill description appears correctly in offer
- Skill activates and provides expected output

### Scenario 2: Manual Invocation
**Purpose:** Verify skill can be invoked via `/skill-name` command.

**Steps:**
1. Type `/skill-name` (replace with actual skill name)
2. Provide a task for the skill
3. Verify skill activates and executes correctly

**Success Criteria:**
- Skill is accessible via slash command (if `user-invocable: true`)
- Skill executes as expected
- Output follows skill instructions

### Scenario 3: Multi-File Coordination
**Purpose:** Verify skill correctly coordinates with reference files.

**Steps:**
1. Choose a task requiring detailed reference material
2. Execute task using the skill
3. Observe if skill loads reference files appropriately

**Success Criteria:**
- Reference files are loaded when needed
- Information from references is correctly applied
- No unnecessary reference loading (efficient context use)

### Scenario 4: Error Recovery
**Purpose:** Verify skill handles errors gracefully.

**Steps:**
1. Provide invalid or problematic input
2. Observe skill's behavior

**Success Criteria:**
- Skill provides helpful error message
- Skill doesn't crash or break context
- Error message guides toward correct usage

### Scenario 5: Tool Restrictions
**Purpose:** Verify `allowed-tools` restrictions work correctly.

**Steps:**
1. Use a skill with `allowed-tools` configured
2. Attempt to use a restricted tool
3. Verify behavior

**Success Criteria:**
- Restricted tools are blocked or require permission
- Allowed tools work without prompting
- Skill functionality isn't significantly impaired

## Common Issues and Fixes

### Issue: Skill Not Triggering Automatically

**Symptoms:**
- Claude never offers the skill
- Description matches query but skill doesn't appear

**Solutions:**
1. **Improve Description:** Add more specific keywords and trigger terms
2. **Check Frontmatter:** Ensure YAML is valid and required fields are present
3. **Verify Location:** Ensure skill is in correct directory (`~/.claude/skills/` or `.claude/skills/`)
4. **Restart Claude:** Exit and restart Claude Code

### Issue: Skill Doesn't Load

**Symptoms:**
- Skill appears in list but fails when activated
- Claude reports errors when using skill

**Solutions:**
1. **Validate YAML:** Check frontmatter starts with `---` and ends with `---`
2. **Check Syntax:** Run `claude --debug` to see loading errors
3. **Verify Paths:** Ensure all file references use forward slashes
4. **Check File Permissions:** Verify SKILL.md is readable

### Issue: Context Too Large

**Symptoms:**
- Skill causes context limit errors
- Performance is slow with skill active

**Solutions:**
1. **Reduce Content:** Simplify SKILL.md to essential guidance only
2. **Use Progressive Disclosure:** Move detailed info to reference files
3. **Check Line Count:** Ensure SKILL.md is under 500 lines
4. **Review Reference Loading:** Minimize unnecessary reference file loads

### Issue: Tool Restrictions Too Strict

**Symptoms:**
- Skill can't complete tasks due to tool limitations
- Claude asks for permissions repeatedly

**Solutions:**
1. **Review `allowed-tools`:** Add missing essential tools
2. **Use Wildcards:** Consider scoped wildcards (e.g., `Bash(python scripts/*:*)`)
3. **Document Limitations:** Clearly state in description what tools are available

## Final Validation

Before publishing or using a skill, ensure:

**Essential:**
- [ ] Frontmatter is valid YAML with required fields
- [ ] Description is effective for auto-discovery
- [ ] SKILL.md is under 500 lines
- [ ] Skill passes basic trigger test
- [ ] Skill passes execution test
- [ ] No auxiliary documentation files (README.md, etc.)

**Recommended:**
- [ ] Progressive disclosure implemented
- [ ] Supporting reference files organized
- [ ] Tool restrictions tested and validated
- [ ] Multiple scenarios tested successfully
- [ ] Error handling verified
- [ ] Documentation is clear and actionable

**For Complex Skills:**
- [ ] Reference files have table of contents (if > 100 lines)
- [ ] Scripts are tested and executable
- [ ] Multi-file coordination tested
- [ ] Performance tested with realistic workloads

## Continuous Improvement

**After Using Skills:**
1. Observe how Claude invokes and uses the skill
2. Identify areas where Claude struggles or deviates from instructions
3. Iterate on skill content based on real usage patterns
4. Test changes with multiple Claude instances or models
5. Gather feedback from teammates if sharing skill

**Testing Frequency:**
- Test skills whenever Claude updates (new model versions)
- Revalidate after significant content changes
- Test across different projects and contexts
- Verify with different user intents and query types
