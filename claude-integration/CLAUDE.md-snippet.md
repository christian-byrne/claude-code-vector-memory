# Memory Integration for CLAUDE.md

Add this section to your `~/.claude/CLAUDE.md` file to enable automatic memory integration:

```markdown
## Memory Integration (MANDATORY)

CRITICAL: Before starting ANY new task, you MUST search through your previous conversations with this user:

1. **Extract key terms** from the user's request (technologies, components, concepts)
2. **Run semantic search**: `~/agents/claude-code-vector-memory/search.sh "extracted key terms"`
3. **Review results** and identify relevant past work
4. **Present memory recap** to user showing what related work you've done before
5. **Ask user** if they want to build on previous approaches or start fresh

This is MANDATORY for all tasks, not optional. Users rely on this continuity.

When presenting found memories:
- Show a brief "memory recap" before beginning work:
  ```
  📚 I found relevant past work:
  1. [Title] - [Date]: We worked on [brief description]
     - Relevant because: [specific connection to current task]
  2. [Title] - [Date]: We implemented [solution]
     - Could apply here for: [specific aspect]
  ```
- Ask: "Would you like me to build on any of these previous approaches, or should we start fresh?"

## Memory Validation

When finding potentially related past sessions from conversation history:
- Read the full context of each memory match to verify genuine relevance
- Confirm tasks share actual similarity beyond surface-level keyword overlap
- Verify that past solutions/approaches actually apply to the current situation
- Only reference and build upon past work if it genuinely helps with the current task
- Present found memories with clear relevance indicators: "This is relevant because..."
- If uncertain about relevance, ask user: "I found this past work on [topic] - would it be helpful here?"
```

## Installation Instructions

1. **Copy the above section** to your `~/.claude/CLAUDE.md` file
2. **Copy command files** to your Claude Code commands directory:
   ```bash
   mkdir -p ~/.claude/commands/system/
   cp claude-integration/commands/*.md ~/.claude/commands/system/
   ```
3. **Verify integration** by starting a Claude Code session and trying:
   ```
   /system:semantic-memory-search test query
   ```

## Notes

- This enables automatic memory search before every task
- Claude Code will present relevant past work and ask for direction
- The system searches using semantic similarity, not just keywords
- Recent sessions are weighted higher in results
- Minimum 30% similarity threshold for results